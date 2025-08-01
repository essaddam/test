import pytest
import os
from unittest.mock import patch
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.config import Config

class TestConfig:
    
    def test_default_config(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.odoo_url == "http://localhost:8069"
            assert config.odoo_database == "odoo"
            assert config.odoo_username == "admin"
            assert config.server_host == "0.0.0.0"
            assert config.server_port == 8000
    
    def test_environment_variables(self):
        """Test configuration from environment variables"""
        env_vars = {
            "ODOO_URL": "http://test.odoo.com",
            "ODOO_DATABASE": "test_db",
            "ODOO_USERNAME": "test_user",
            "ODOO_PASSWORD": "test_pass",
            "SERVER_PORT": "9000",
            "DEBUG": "true"
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.odoo_url == "http://test.odoo.com"
            assert config.odoo_database == "test_db"
            assert config.odoo_username == "test_user"
            assert config.odoo_password == "test_pass"
            assert config.server_port == 9000
            assert config.debug == True
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test invalid URL
        with patch.dict(os.environ, {"ODOO_URL": "invalid-url"}):
            with pytest.raises(ValueError, match="ODOO_URL must start with"):
                Config()
    
    def test_get_odoo_config(self):
        """Test getting Odoo configuration"""
        env_vars = {
            "ODOO_URL": "http://test.odoo.com",
            "ODOO_DATABASE": "test_db",
            "ODOO_USERNAME": "test_user",
            "ODOO_PASSWORD": "test_pass"
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            odoo_config = config.get_odoo_config()
            
            assert odoo_config["url"] == "http://test.odoo.com"
            assert odoo_config["database"] == "test_db"
            assert odoo_config["username"] == "test_user"
            assert odoo_config["password"] == "test_pass"