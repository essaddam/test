import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mcp.server import MCPServer

class TestMCPServer:
    
    @pytest.fixture
    def mock_odoo_client(self):
        """Create a mock Odoo client"""
        client = AsyncMock()
        client.call = AsyncMock()
        client.list_models = AsyncMock(return_value=[
            {"model": "res.partner", "name": "Contact"}
        ])
        return client
    
    @pytest.fixture
    def mcp_server(self, mock_odoo_client):
        """Create MCP server instance"""
        return MCPServer(mock_odoo_client)
    
    @pytest.mark.asyncio
    async def test_initialization(self, mcp_server):
        """Test MCP server initialization"""
        await mcp_server.initialize()
        assert mcp_server.initialized == True
        assert len(mcp_server.tools) > 0
        assert len(mcp_server.resources) > 0
    
    @pytest.mark.asyncio
    async def test_get_capabilities(self, mcp_server):
        """Test getting server capabilities"""
        await mcp_server.initialize()
        capabilities = await mcp_server.get_capabilities()
        
        assert capabilities["tools"] == True
        assert capabilities["resources"] == True
        assert "experimental" in capabilities
    
    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_server):
        """Test listing available tools"""
        await mcp_server.initialize()
        tools = await mcp_server.list_tools()
        
        assert len(tools) > 0
        tool_names = [tool["name"] for tool in tools]
        assert "odoo_search" in tool_names
        assert "odoo_create" in tool_names
        assert "odoo_write" in tool_names
    
    @pytest.mark.asyncio
    async def test_odoo_search_tool(self, mcp_server, mock_odoo_client):
        """Test odoo_search tool"""
        await mcp_server.initialize()
        
        # Mock search_read response
        mock_records = [{"id": 1, "name": "Test Partner"}]
        mock_odoo_client.call.return_value = mock_records
        
        result = await mcp_server.call_tool("odoo_search", {
            "model": "res.partner",
            "domain": [],
            "fields": ["name"],
            "limit": 10
        })
        
        assert result["model"] == "res.partner"
        assert result["count"] == 1
        assert result["records"] == mock_records
        
        # Verify the call was made correctly
        mock_odoo_client.call.assert_called_once_with(
            "res.partner", "search_read", [[]], 
            {"fields": ["name"], "limit": 10}
        )
    
    @pytest.mark.asyncio
    async def test_odoo_create_tool(self, mcp_server, mock_odoo_client):
        """Test odoo_create tool"""
        await mcp_server.initialize()
        
        # Mock create response
        mock_odoo_client.call.return_value = 123
        
        result = await mcp_server.call_tool("odoo_create", {
            "model": "res.partner",
            "values": {"name": "New Partner"}
        })
        
        assert result["model"] == "res.partner"
        assert result["created_id"] == 123
        assert result["success"] == True
        
        # Verify the call was made correctly
        mock_odoo_client.call.assert_called_once_with(
            "res.partner", "create", [{"name": "New Partner"}]
        )
    
    @pytest.mark.asyncio
    async def test_unknown_tool(self, mcp_server):
        """Test calling unknown tool"""
        await mcp_server.initialize()
        
        with pytest.raises(ValueError, match="Unknown tool"):
            await mcp_server.call_tool("unknown_tool", {})
    
    @pytest.mark.asyncio
    async def test_list_resources(self, mcp_server):
        """Test listing available resources"""
        await mcp_server.initialize()
        resources = await mcp_server.list_resources()
        
        assert len(resources) > 0
        resource_uris = [resource["uri"] for resource in resources]
        assert "odoo://models" in resource_uris
        assert "odoo://users" in resource_uris
    
    @pytest.mark.asyncio
    async def test_read_models_resource(self, mcp_server, mock_odoo_client):
        """Test reading models resource"""
        await mcp_server.initialize()
        
        mock_models = [{"model": "res.partner", "name": "Contact"}]
        mock_odoo_client.list_models.return_value = mock_models
        
        result = await mcp_server.read_resource("odoo://models")
        
        assert "contents" in result
        assert len(result["contents"]) == 1
        content = result["contents"][0]
        assert content["uri"] == "odoo://models"
        assert content["mimeType"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_stream_tool_call(self, mcp_server, mock_odoo_client):
        """Test streaming tool call"""
        await mcp_server.initialize()
        
        # Mock large dataset
        mock_records = [{"id": i, "name": f"Partner {i}"} for i in range(25)]
        mock_odoo_client.call.return_value = {
            "model": "res.partner",
            "count": 25,
            "records": mock_records
        }
        
        chunks = []
        async for chunk in mcp_server.stream_tool_call("odoo_search", {
            "model": "res.partner",
            "limit": 25
        }):
            chunks.append(chunk)
        
        # Check we got start, chunks, and end
        assert chunks[0]["type"] == "start"
        assert chunks[-1]["type"] == "end"
        
        # Check we got data chunks
        data_chunks = [c for c in chunks if c["type"] == "chunk"]
        assert len(data_chunks) > 1  # Should be split into multiple chunks