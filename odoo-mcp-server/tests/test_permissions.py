import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.permissions import PermissionManager, PermissionError, MCPMode, PermissionLevel

class TestPermissionManager:
    
    def test_readonly_mode_initialization(self):
        """Test initialization in readonly mode"""
        pm = PermissionManager("readonly")
        assert pm.mode == MCPMode.READONLY
        assert PermissionLevel.READ in pm.allowed_permissions
        assert PermissionLevel.EXECUTE in pm.allowed_permissions
        assert PermissionLevel.WRITE in pm.forbidden_permissions
        assert PermissionLevel.DELETE in pm.forbidden_permissions
    
    def test_readwrite_mode_initialization(self):
        """Test initialization in readwrite mode"""
        pm = PermissionManager("readwrite")
        assert pm.mode == MCPMode.READWRITE
        assert len(pm.forbidden_permissions) == 0
        assert len(pm.allowed_permissions) == 4
    
    def test_invalid_mode(self):
        """Test invalid mode raises error"""
        with pytest.raises(ValueError):
            PermissionManager("invalid_mode")
    
    def test_readonly_tool_permissions(self):
        """Test tool permissions in readonly mode"""
        pm = PermissionManager("readonly")
        
        # Allowed tools
        assert pm.is_tool_allowed("odoo_search") == True
        assert pm.is_tool_allowed("odoo_fields_get") == True
        assert pm.is_tool_allowed("odoo_report") == True
        
        # Forbidden tools
        assert pm.is_tool_allowed("odoo_create") == False
        assert pm.is_tool_allowed("odoo_write") == False
        assert pm.is_tool_allowed("odoo_unlink") == False
    
    def test_readwrite_tool_permissions(self):
        """Test tool permissions in readwrite mode"""
        pm = PermissionManager("readwrite")
        
        # All tools should be allowed
        assert pm.is_tool_allowed("odoo_search") == True
        assert pm.is_tool_allowed("odoo_create") == True
        assert pm.is_tool_allowed("odoo_write") == True
        assert pm.is_tool_allowed("odoo_unlink") == True
        assert pm.is_tool_allowed("odoo_call") == True
    
    def test_readonly_odoo_call_validation(self):
        """Test odoo_call validation in readonly mode"""
        pm = PermissionManager("readonly")
        
        # Read methods should be allowed
        assert pm.validate_tool_call("odoo_call", {"method": "search"}) == True
        assert pm.validate_tool_call("odoo_call", {"method": "read"}) == True
        assert pm.validate_tool_call("odoo_call", {"method": "fields_get"}) == True
        
        # Write methods should be forbidden
        assert pm.validate_tool_call("odoo_call", {"method": "create"}) == False
        assert pm.validate_tool_call("odoo_call", {"method": "write"}) == False
        assert pm.validate_tool_call("odoo_call", {"method": "unlink"}) == False
        assert pm.validate_tool_call("odoo_call", {"method": "action_confirm"}) == False
    
    def test_readwrite_odoo_call_validation(self):
        """Test odoo_call validation in readwrite mode"""
        pm = PermissionManager("readwrite")
        
        # All methods should be allowed
        assert pm.validate_tool_call("odoo_call", {"method": "search"}) == True
        assert pm.validate_tool_call("odoo_call", {"method": "create"}) == True
        assert pm.validate_tool_call("odoo_call", {"method": "write"}) == True
        assert pm.validate_tool_call("odoo_call", {"method": "unlink"}) == True
    
    def test_get_allowed_tools_readonly(self):
        """Test getting allowed tools in readonly mode"""
        pm = PermissionManager("readonly")
        allowed_tools = pm.get_allowed_tools()
        
        assert "odoo_search" in allowed_tools
        assert "odoo_fields_get" in allowed_tools
        assert "odoo_report" in allowed_tools
        assert "odoo_create" not in allowed_tools
        assert "odoo_write" not in allowed_tools
        assert "odoo_unlink" not in allowed_tools
    
    def test_get_allowed_tools_readwrite(self):
        """Test getting allowed tools in readwrite mode"""
        pm = PermissionManager("readwrite")
        allowed_tools = pm.get_allowed_tools()
        
        expected_tools = [
            "odoo_search", "odoo_create", "odoo_write", 
            "odoo_unlink", "odoo_call", "odoo_fields_get", "odoo_report"
        ]
        
        for tool in expected_tools:
            assert tool in allowed_tools
    
    def test_get_mode_info_readonly(self):
        """Test getting mode info for readonly"""
        pm = PermissionManager("readonly")
        info = pm.get_mode_info()
        
        assert info["mode"] == "readonly"
        assert "read" in info["allowed_permissions"]
        assert "execute" in info["allowed_permissions"]
        assert "write" in info["forbidden_permissions"]
        assert "delete" in info["forbidden_permissions"]
        assert "lecture seule" in info["description"].lower()
    
    def test_get_mode_info_readwrite(self):
        """Test getting mode info for readwrite"""
        pm = PermissionManager("readwrite")
        info = pm.get_mode_info()
        
        assert info["mode"] == "readwrite"
        assert len(info["forbidden_permissions"]) == 0
        assert len(info["allowed_permissions"]) == 4
        assert "lecture/écriture" in info["description"].lower()
    
    def test_tool_validation_flow(self):
        """Test complete tool validation flow"""
        pm_readonly = PermissionManager("readonly")
        pm_readwrite = PermissionManager("readwrite")
        
        # Test readonly validation
        assert pm_readonly.validate_tool_call("odoo_search", {}) == True
        assert pm_readonly.validate_tool_call("odoo_create", {}) == False
        
        # Test readwrite validation
        assert pm_readwrite.validate_tool_call("odoo_search", {}) == True
        assert pm_readwrite.validate_tool_call("odoo_create", {}) == True