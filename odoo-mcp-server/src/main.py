#!/usr/bin/env python3

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from mcp.server import MCPServer
from odoo.client import OdooClient
from utils.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
mcp_server: Optional[MCPServer] = None
odoo_client: Optional[OdooClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_server, odoo_client
    
    # Initialize components
    config = Config()
    odoo_client = OdooClient(config)
    mcp_server = MCPServer(odoo_client, config)
    
    # Start MCP server
    await mcp_server.initialize()
    logger.info("MCP Server initialized successfully")
    
    yield
    
    # Cleanup
    if mcp_server:
        await mcp_server.cleanup()
    if odoo_client:
        await odoo_client.close()
    logger.info("Server shutdown completed")

# FastAPI app
app = FastAPI(
    title="Odoo MCP Server",
    description="Model Context Protocol server for Odoo integration with HTTP streaming support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any] = {}
    id: Optional[str] = None

class MCPResponse(BaseModel):
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class OdooQuery(BaseModel):
    model: str
    method: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "odoo-mcp-server"}

# Mode and permissions endpoint
@app.get("/mcp/mode")
async def get_mcp_mode():
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP server not initialized")
    
    return mcp_server.permission_manager.get_mode_info()

# MCP protocol endpoints
@app.post("/mcp/initialize")
async def initialize_mcp():
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP server not initialized")
    
    capabilities = await mcp_server.get_capabilities()
    return {"capabilities": capabilities}

@app.post("/mcp/tools/list")
async def list_tools():
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP server not initialized")
    
    tools = await mcp_server.list_tools()
    return {"tools": tools}

@app.post("/mcp/tools/call", response_model=MCPResponse)
async def call_tool(request: MCPRequest):
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP server not initialized")
    
    try:
        result = await mcp_server.call_tool(
            request.method,
            request.params
        )
        return MCPResponse(result=result, id=request.id)
    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return MCPResponse(
            error={"code": -1, "message": str(e)},
            id=request.id
        )

@app.post("/mcp/resources/list")
async def list_resources():
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP server not initialized")
    
    resources = await mcp_server.list_resources()
    return {"resources": resources}

@app.post("/mcp/resources/read")
async def read_resource(request: MCPRequest):
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP server not initialized")
    
    try:
        content = await mcp_server.read_resource(
            request.params.get("uri", "")
        )
        return MCPResponse(result=content, id=request.id)
    except Exception as e:
        logger.error(f"Resource read error: {e}")
        return MCPResponse(
            error={"code": -1, "message": str(e)},
            id=request.id
        )

# Streaming endpoints
@app.post("/mcp/stream/tools/call")
async def stream_tool_call(request: MCPRequest):
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP server not initialized")
    
    async def generate_response():
        try:
            async for chunk in mcp_server.stream_tool_call(
                request.method,
                request.params
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            error_chunk = {
                "error": {"code": -1, "message": str(e)},
                "id": request.id
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Direct Odoo integration endpoints
@app.post("/odoo/query")
async def odoo_query(query: OdooQuery):
    if not odoo_client:
        raise HTTPException(status_code=500, detail="Odoo client not initialized")
    
    try:
        result = await odoo_client.call(
            query.model,
            query.method,
            query.args,
            query.kwargs
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"Odoo query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/odoo/models")
async def list_odoo_models():
    if not odoo_client:
        raise HTTPException(status_code=500, detail="Odoo client not initialized")
    
    try:
        models = await odoo_client.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/odoo/models/{model_name}/fields")
async def get_model_fields(model_name: str):
    if not odoo_client:
        raise HTTPException(status_code=500, detail="Odoo client not initialized")
    
    try:
        fields = await odoo_client.get_model_fields(model_name)
        return {"fields": fields}
    except Exception as e:
        logger.error(f"Error getting model fields: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time MCP communication
@app.websocket("/mcp/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process MCP request
            if not mcp_server:
                await websocket.send_text(json.dumps({
                    "error": {"code": -1, "message": "MCP server not initialized"},
                    "id": message.get("id")
                }))
                continue
            
            try:
                if message.get("method") == "tools/call":
                    result = await mcp_server.call_tool(
                        message["params"]["name"],
                        message["params"].get("arguments", {})
                    )
                    response = {"result": result, "id": message.get("id")}
                elif message.get("method") == "tools/list":
                    tools = await mcp_server.list_tools()
                    response = {"result": {"tools": tools}, "id": message.get("id")}
                elif message.get("method") == "resources/list":
                    resources = await mcp_server.list_resources()
                    response = {"result": {"resources": resources}, "id": message.get("id")}
                else:
                    response = {
                        "error": {"code": -1, "message": f"Unknown method: {message.get('method')}"},
                        "id": message.get("id")
                    }
                
                await websocket.send_text(json.dumps(response))
                
            except Exception as e:
                logger.error(f"WebSocket processing error: {e}")
                await websocket.send_text(json.dumps({
                    "error": {"code": -1, "message": str(e)},
                    "id": message.get("id")
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )