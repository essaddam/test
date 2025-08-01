import os
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    """Configuration management for Odoo MCP Server"""
    
    def __init__(self, env_file: Optional[str] = None):
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Odoo connection settings
        self.odoo_url = os.getenv("ODOO_URL", "http://localhost:8069")
        self.odoo_database = os.getenv("ODOO_DATABASE", "odoo")
        self.odoo_username = os.getenv("ODOO_USERNAME", "admin")
        self.odoo_password = os.getenv("ODOO_PASSWORD", "admin")
        
        # Server settings
        self.server_host = os.getenv("SERVER_HOST", "0.0.0.0")
        self.server_port = int(os.getenv("SERVER_PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # MCP settings
        self.mcp_server_name = os.getenv("MCP_SERVER_NAME", "odoo-mcp-server")
        self.mcp_server_version = os.getenv("MCP_SERVER_VERSION", "1.0.0")
        
        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # CORS settings
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # Rate limiting
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # Streaming settings
        self.stream_chunk_size = int(os.getenv("STREAM_CHUNK_SIZE", "10"))
        self.stream_delay = float(os.getenv("STREAM_DELAY", "0.1"))
        
        # Security settings
        self.api_key = os.getenv("API_KEY")
        self.allowed_ips = os.getenv("ALLOWED_IPS", "").split(",") if os.getenv("ALLOWED_IPS") else []
        
        # Validate required settings
        self._validate_config()
        
        # Configure logging
        self._configure_logging()
    
    def _validate_config(self):
        """Validate required configuration settings"""
        required_settings = {
            "ODOO_URL": self.odoo_url,
            "ODOO_DATABASE": self.odoo_database,
            "ODOO_USERNAME": self.odoo_username,
            "ODOO_PASSWORD": self.odoo_password
        }
        
        missing_settings = [key for key, value in required_settings.items() if not value]
        
        if missing_settings:
            raise ValueError(f"Missing required configuration: {', '.join(missing_settings)}")
        
        # Validate URL format
        if not self.odoo_url.startswith(("http://", "https://")):
            raise ValueError("ODOO_URL must start with http:// or https://")
        
        logger.info("Configuration validation passed")
    
    def _configure_logging(self):
        """Configure logging based on settings"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=self.log_format
        )
        
        if self.debug:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def get_odoo_config(self) -> dict:
        """Get Odoo connection configuration"""
        return {
            "url": self.odoo_url,
            "database": self.odoo_database,
            "username": self.odoo_username,
            "password": self.odoo_password
        }
    
    def get_server_config(self) -> dict:
        """Get server configuration"""
        return {
            "host": self.server_host,
            "port": self.server_port,
            "debug": self.debug
        }
    
    def get_mcp_config(self) -> dict:
        """Get MCP server configuration"""
        return {
            "name": self.mcp_server_name,
            "version": self.mcp_server_version
        }
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            "odoo_url": self.odoo_url,
            "odoo_database": self.odoo_database,
            "odoo_username": self.odoo_username,
            "server_host": self.server_host,
            "server_port": self.server_port,
            "debug": self.debug,
            "mcp_server_name": self.mcp_server_name,
            "mcp_server_version": self.mcp_server_version,
            "log_level": self.log_level,
            "cors_origins": self.cors_origins,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window": self.rate_limit_window,
            "stream_chunk_size": self.stream_chunk_size,
            "stream_delay": self.stream_delay
        }