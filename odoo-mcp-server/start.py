#!/usr/bin/env python3

import sys
import os
import uvicorn
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils.config import Config

def main():
    """Start the Odoo MCP server"""
    try:
        # Load configuration
        config = Config()
        server_config = config.get_server_config()
        
        print(f"Starting Odoo MCP Server on {server_config['host']}:{server_config['port']}")
        print(f"Odoo URL: {config.odoo_url}")
        print(f"Database: {config.odoo_database}")
        print(f"Debug mode: {server_config['debug']}")
        
        # Start the server
        uvicorn.run(
            "main:app",
            host=server_config["host"],
            port=server_config["port"],
            reload=server_config["debug"],
            log_level=config.log_level.lower(),
            access_log=True
        )
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()