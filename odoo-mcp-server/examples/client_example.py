#!/usr/bin/env python3

import asyncio
import json
import websockets
import httpx
from typing import Dict, Any

class OdooMCPClient:
    """Example client for Odoo MCP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.http_client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        response = await self.http_client.get(f"{self.base_url}/health")
        return response.json()
    
    async def initialize_mcp(self) -> Dict[str, Any]:
        """Initialize MCP connection"""
        response = await self.http_client.post(f"{self.base_url}/mcp/initialize")
        return response.json()
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools"""
        response = await self.http_client.post(f"{self.base_url}/mcp/tools/list")
        return response.json()
    
    async def call_tool(self, method: str, params: Dict[str, Any], tool_id: str = None) -> Dict[str, Any]:
        """Call an MCP tool"""
        payload = {
            "method": method,
            "params": params
        }
        if tool_id:
            payload["id"] = tool_id
        
        response = await self.http_client.post(
            f"{self.base_url}/mcp/tools/call",
            json=payload
        )
        return response.json()
    
    async def stream_tool_call(self, method: str, params: Dict[str, Any]):
        """Stream tool call results"""
        payload = {
            "method": method,
            "params": params
        }
        
        async with self.http_client.stream(
            "POST",
            f"{self.base_url}/mcp/stream/tools/call",
            json=payload
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available MCP resources"""
        response = await self.http_client.post(f"{self.base_url}/mcp/resources/list")
        return response.json()
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read an MCP resource"""
        payload = {
            "params": {"uri": uri}
        }
        response = await self.http_client.post(
            f"{self.base_url}/mcp/resources/read",
            json=payload
        )
        return response.json()
    
    async def websocket_example(self):
        """Example WebSocket communication"""
        uri = f"ws://localhost:8000/mcp/ws"
        
        async with websockets.connect(uri) as websocket:
            # Send a tool list request
            request = {
                "method": "tools/list",
                "id": "1"
            }
            await websocket.send(json.dumps(request))
            
            # Receive response
            response = await websocket.recv()
            return json.loads(response)

async def main():
    """Example usage of the MCP client"""
    async with OdooMCPClient() as client:
        print("=== Odoo MCP Server Client Example ===\n")
        
        # Health check
        print("1. Health Check:")
        health = await client.health_check()
        print(f"   Status: {health}\n")
        
        # Initialize MCP
        print("2. Initialize MCP:")
        init_result = await client.initialize_mcp()
        print(f"   Capabilities: {init_result}\n")
        
        # List tools
        print("3. List Tools:")
        tools = await client.list_tools()
        print(f"   Available tools: {len(tools['tools'])}")
        for tool in tools['tools'][:3]:  # Show first 3 tools
            print(f"   - {tool['name']}: {tool['description']}")
        print()
        
        # List resources
        print("4. List Resources:")
        resources = await client.list_resources()
        print(f"   Available resources: {len(resources['resources'])}")
        for resource in resources['resources']:
            print(f"   - {resource['uri']}: {resource['name']}")
        print()
        
        # Example tool call - search partners
        print("5. Example Tool Call (Search Partners):")
        try:
            result = await client.call_tool("odoo_search", {
                "model": "res.partner",
                "domain": [["is_company", "=", True]],
                "fields": ["name", "email"],
                "limit": 5
            })
            print(f"   Found {result.get('result', {}).get('count', 0)} company partners")
            if 'result' in result and 'records' in result['result']:
                for record in result['result']['records'][:2]:
                    print(f"   - {record.get('name', 'N/A')}: {record.get('email', 'N/A')}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # Example streaming call
        print("6. Example Streaming Call:")
        try:
            chunk_count = 0
            async for chunk in client.stream_tool_call("odoo_search", {
                "model": "res.partner",
                "limit": 20
            }):
                if chunk['type'] == 'start':
                    print(f"   Stream started for tool: {chunk['tool']}")
                elif chunk['type'] == 'chunk':
                    chunk_count += 1
                    if 'progress' in chunk:
                        progress = chunk['progress']
                        print(f"   Chunk {chunk_count}: {progress['current']}/{progress['total']} records")
                elif chunk['type'] == 'end':
                    print(f"   Stream completed")
                elif chunk['type'] == 'error':
                    print(f"   Stream error: {chunk['message']}")
        except Exception as e:
            print(f"   Streaming error: {e}")
        print()
        
        # Read a resource
        print("7. Read Resource (Odoo Models):")
        try:
            models_resource = await client.read_resource("odoo://models")
            if 'result' in models_resource and 'contents' in models_resource['result']:
                content = models_resource['result']['contents'][0]
                models_data = json.loads(content['text'])
                print(f"   Found {len(models_data)} models")
                for model in models_data[:3]:
                    print(f"   - {model.get('model', 'N/A')}: {model.get('name', 'N/A')}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # WebSocket example
        print("8. WebSocket Example:")
        try:
            ws_result = await client.websocket_example()
            print(f"   WebSocket response: {ws_result.get('result', {}).get('tools', [])[:2]}")
        except Exception as e:
            print(f"   WebSocket error: {e}")

if __name__ == "__main__":
    asyncio.run(main())