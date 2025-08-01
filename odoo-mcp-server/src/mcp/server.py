import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPServer:
    """Model Context Protocol server for Odoo integration"""
    
    def __init__(self, odoo_client):
        self.odoo_client = odoo_client
        self.tools = {}
        self.resources = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize the MCP server and register tools/resources"""
        await self._register_tools()
        await self._register_resources()
        self.initialized = True
        logger.info("MCP Server initialized with tools and resources")
    
    async def _register_tools(self):
        """Register available MCP tools"""
        self.tools = {
            "odoo_search": {
                "name": "odoo_search",
                "description": "Search for records in Odoo models",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "description": "Odoo model name (e.g., 'res.partner')"},
                        "domain": {"type": "array", "description": "Search domain filters"},
                        "fields": {"type": "array", "description": "Fields to retrieve"},
                        "limit": {"type": "integer", "description": "Maximum number of records"}
                    },
                    "required": ["model"]
                }
            },
            "odoo_create": {
                "name": "odoo_create",
                "description": "Create a new record in Odoo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "description": "Odoo model name"},
                        "values": {"type": "object", "description": "Field values for the new record"}
                    },
                    "required": ["model", "values"]
                }
            },
            "odoo_write": {
                "name": "odoo_write",
                "description": "Update existing records in Odoo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "description": "Odoo model name"},
                        "ids": {"type": "array", "description": "Record IDs to update"},
                        "values": {"type": "object", "description": "Field values to update"}
                    },
                    "required": ["model", "ids", "values"]
                }
            },
            "odoo_unlink": {
                "name": "odoo_unlink",
                "description": "Delete records from Odoo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "description": "Odoo model name"},
                        "ids": {"type": "array", "description": "Record IDs to delete"}
                    },
                    "required": ["model", "ids"]
                }
            },
            "odoo_call": {
                "name": "odoo_call",
                "description": "Call a method on Odoo model",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "description": "Odoo model name"},
                        "method": {"type": "string", "description": "Method name to call"},
                        "args": {"type": "array", "description": "Method arguments"},
                        "kwargs": {"type": "object", "description": "Method keyword arguments"}
                    },
                    "required": ["model", "method"]
                }
            },
            "odoo_fields_get": {
                "name": "odoo_fields_get",
                "description": "Get field definitions for an Odoo model",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string", "description": "Odoo model name"},
                        "fields": {"type": "array", "description": "Specific fields to get (optional)"}
                    },
                    "required": ["model"]
                }
            },
            "odoo_report": {
                "name": "odoo_report",
                "description": "Generate reports from Odoo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "report_name": {"type": "string", "description": "Report template name"},
                        "record_ids": {"type": "array", "description": "Record IDs for the report"},
                        "format": {"type": "string", "description": "Output format (pdf, html, etc.)"}
                    },
                    "required": ["report_name", "record_ids"]
                }
            }
        }
    
    async def _register_resources(self):
        """Register available MCP resources"""
        self.resources = {
            "odoo://models": {
                "uri": "odoo://models",
                "name": "Odoo Models",
                "description": "List of all available Odoo models",
                "mimeType": "application/json"
            },
            "odoo://users": {
                "uri": "odoo://users",
                "name": "Odoo Users",
                "description": "List of Odoo users",
                "mimeType": "application/json"
            },
            "odoo://companies": {
                "uri": "odoo://companies",
                "name": "Odoo Companies",
                "description": "List of companies in Odoo",
                "mimeType": "application/json"
            },
            "odoo://config": {
                "uri": "odoo://config",
                "name": "Odoo Configuration",
                "description": "Odoo server configuration and settings",
                "mimeType": "application/json"
            }
        }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get MCP server capabilities"""
        return {
            "tools": True,
            "resources": True,
            "prompts": False,
            "sampling": False,
            "experimental": {
                "streaming": True
            }
        }
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return list(self.tools.values())
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        try:
            if name == "odoo_search":
                return await self._handle_search(arguments)
            elif name == "odoo_create":
                return await self._handle_create(arguments)
            elif name == "odoo_write":
                return await self._handle_write(arguments)
            elif name == "odoo_unlink":
                return await self._handle_unlink(arguments)
            elif name == "odoo_call":
                return await self._handle_call(arguments)
            elif name == "odoo_fields_get":
                return await self._handle_fields_get(arguments)
            elif name == "odoo_report":
                return await self._handle_report(arguments)
            else:
                raise ValueError(f"Tool {name} not implemented")
                
        except Exception as e:
            logger.error(f"Tool execution error for {name}: {e}")
            raise
    
    async def stream_tool_call(self, name: str, arguments: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream tool call results"""
        yield {"type": "start", "tool": name, "timestamp": datetime.now().isoformat()}
        
        try:
            result = await self.call_tool(name, arguments)
            
            # For large results, stream in chunks
            if isinstance(result, dict) and "records" in result:
                records = result["records"]
                chunk_size = 10
                
                for i in range(0, len(records), chunk_size):
                    chunk = records[i:i + chunk_size]
                    yield {
                        "type": "chunk",
                        "data": chunk,
                        "progress": {"current": i + len(chunk), "total": len(records)}
                    }
                    await asyncio.sleep(0.1)  # Allow other tasks to run
            else:
                yield {"type": "chunk", "data": result}
            
            yield {"type": "end", "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            yield {"type": "error", "message": str(e), "timestamp": datetime.now().isoformat()}
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        return list(self.resources.values())
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource"""
        if uri not in self.resources:
            raise ValueError(f"Unknown resource: {uri}")
        
        try:
            if uri == "odoo://models":
                models = await self.odoo_client.list_models()
                return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(models)}]}
            elif uri == "odoo://users":
                users = await self.odoo_client.call("res.users", "search_read", [[]], {"fields": ["name", "login", "email"]})
                return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(users)}]}
            elif uri == "odoo://companies":
                companies = await self.odoo_client.call("res.company", "search_read", [[]], {"fields": ["name", "email", "website"]})
                return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(companies)}]}
            elif uri == "odoo://config":
                config = await self.odoo_client.get_server_info()
                return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(config)}]}
            else:
                raise ValueError(f"Resource {uri} not implemented")
                
        except Exception as e:
            logger.error(f"Resource read error for {uri}: {e}")
            raise
    
    # Tool handlers
    async def _handle_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odoo_search tool"""
        model = args["model"]
        domain = args.get("domain", [])
        fields = args.get("fields", [])
        limit = args.get("limit", 100)
        
        records = await self.odoo_client.call(
            model, "search_read", [domain], 
            {"fields": fields, "limit": limit}
        )
        
        return {
            "model": model,
            "count": len(records),
            "records": records
        }
    
    async def _handle_create(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odoo_create tool"""
        model = args["model"]
        values = args["values"]
        
        record_id = await self.odoo_client.call(model, "create", [values])
        
        return {
            "model": model,
            "created_id": record_id,
            "success": True
        }
    
    async def _handle_write(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odoo_write tool"""
        model = args["model"]
        ids = args["ids"]
        values = args["values"]
        
        result = await self.odoo_client.call(model, "write", [ids, values])
        
        return {
            "model": model,
            "updated_ids": ids,
            "success": result
        }
    
    async def _handle_unlink(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odoo_unlink tool"""
        model = args["model"]
        ids = args["ids"]
        
        result = await self.odoo_client.call(model, "unlink", [ids])
        
        return {
            "model": model,
            "deleted_ids": ids,
            "success": result
        }
    
    async def _handle_call(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odoo_call tool"""
        model = args["model"]
        method = args["method"]
        call_args = args.get("args", [])
        kwargs = args.get("kwargs", {})
        
        result = await self.odoo_client.call(model, method, call_args, kwargs)
        
        return {
            "model": model,
            "method": method,
            "result": result
        }
    
    async def _handle_fields_get(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odoo_fields_get tool"""
        model = args["model"]
        fields = args.get("fields", [])
        
        field_info = await self.odoo_client.call(
            model, "fields_get", 
            [fields] if fields else []
        )
        
        return {
            "model": model,
            "fields": field_info
        }
    
    async def _handle_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle odoo_report tool"""
        report_name = args["report_name"]
        record_ids = args["record_ids"]
        format_type = args.get("format", "pdf")
        
        # Generate report using Odoo's report service
        report_data = await self.odoo_client.call(
            "ir.actions.report", "_render", 
            [report_name, record_ids],
            {"data": {"form": {}}}
        )
        
        return {
            "report_name": report_name,
            "record_ids": record_ids,
            "format": format_type,
            "data": report_data
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        self.initialized = False
        logger.info("MCP Server cleanup completed")