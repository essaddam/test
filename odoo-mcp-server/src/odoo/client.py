import asyncio
import logging
import xmlrpc.client
from typing import Dict, List, Any, Optional
import httpx
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class OdooClient:
    """Async Odoo client for XML-RPC communication"""
    
    def __init__(self, config):
        self.config = config
        self.url = config.odoo_url
        self.database = config.odoo_database
        self.username = config.odoo_username
        self.password = config.odoo_password
        self.uid = None
        self.authenticated = False
        self.session = None
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self):
        """Establish connection to Odoo server"""
        try:
            # Create HTTP session
            self.session = httpx.AsyncClient(timeout=30.0)
            
            # Authenticate
            await self.authenticate()
            logger.info(f"Connected to Odoo at {self.url} as user {self.username}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            raise
    
    async def authenticate(self):
        """Authenticate with Odoo server"""
        try:
            # Use XML-RPC for authentication
            common_url = urljoin(self.url, '/xmlrpc/2/common')
            
            # Create a synchronous XML-RPC proxy for authentication
            # We'll wrap this in asyncio.to_thread for async compatibility
            common = xmlrpc.client.ServerProxy(common_url)
            
            # Get version info
            version = await asyncio.to_thread(common.version)
            logger.info(f"Odoo version: {version}")
            
            # Authenticate user
            self.uid = await asyncio.to_thread(
                common.authenticate,
                self.database,
                self.username,
                self.password,
                {}
            )
            
            if not self.uid:
                raise Exception("Authentication failed - invalid credentials")
            
            self.authenticated = True
            logger.info(f"Authenticated as user ID: {self.uid}")
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def call(self, model: str, method: str, args: List[Any] = None, kwargs: Dict[str, Any] = None) -> Any:
        """Execute a call to Odoo model method"""
        if not self.authenticated:
            await self.authenticate()
        
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        try:
            # Use XML-RPC object proxy
            object_url = urljoin(self.url, '/xmlrpc/2/object')
            models = xmlrpc.client.ServerProxy(object_url)
            
            # Execute the method call
            result = await asyncio.to_thread(
                models.execute_kw,
                self.database,
                self.uid,
                self.password,
                model,
                method,
                args,
                kwargs
            )
            
            logger.debug(f"Called {model}.{method} with args={args}, kwargs={kwargs}")
            return result
            
        except Exception as e:
            logger.error(f"Call failed for {model}.{method}: {e}")
            raise
    
    async def search(self, model: str, domain: List[Any] = None, offset: int = 0, limit: int = None, order: str = None) -> List[int]:
        """Search for record IDs"""
        if domain is None:
            domain = []
        
        kwargs = {"offset": offset}
        if limit is not None:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order
        
        return await self.call(model, "search", [domain], kwargs)
    
    async def read(self, model: str, ids: List[int], fields: List[str] = None) -> List[Dict[str, Any]]:
        """Read record data"""
        kwargs = {}
        if fields:
            kwargs["fields"] = fields
        
        return await self.call(model, "read", [ids], kwargs)
    
    async def search_read(self, model: str, domain: List[Any] = None, fields: List[str] = None, 
                         offset: int = 0, limit: int = None, order: str = None) -> List[Dict[str, Any]]:
        """Search and read records in one call"""
        if domain is None:
            domain = []
        
        kwargs = {"offset": offset}
        if fields:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order
        
        return await self.call(model, "search_read", [domain], kwargs)
    
    async def create(self, model: str, values: Dict[str, Any]) -> int:
        """Create a new record"""
        return await self.call(model, "create", [values])
    
    async def write(self, model: str, ids: List[int], values: Dict[str, Any]) -> bool:
        """Update existing records"""
        return await self.call(model, "write", [ids, values])
    
    async def unlink(self, model: str, ids: List[int]) -> bool:
        """Delete records"""
        return await self.call(model, "unlink", [ids])
    
    async def fields_get(self, model: str, fields: List[str] = None) -> Dict[str, Any]:
        """Get field definitions for a model"""
        args = [fields] if fields else []
        return await self.call(model, "fields_get", args)
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Get list of all available models"""
        try:
            # Get all installed models
            models = await self.search_read(
                "ir.model",
                [["transient", "=", False]],
                ["model", "name", "info"]
            )
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise
    
    async def get_model_fields(self, model_name: str) -> Dict[str, Any]:
        """Get detailed field information for a model"""
        try:
            fields = await self.fields_get(model_name)
            return fields
        except Exception as e:
            logger.error(f"Failed to get fields for model {model_name}: {e}")
            raise
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get Odoo server information"""
        try:
            # Get database info
            db_info = await self.call("ir.config_parameter", "search_read", 
                                    [["key", "in", ["database.expiration_date", "database.enterprise_code"]]],
                                    {"fields": ["key", "value"]})
            
            # Get installed modules
            modules = await self.search_read(
                "ir.module.module",
                [["state", "=", "installed"]],
                ["name", "shortdesc", "author", "version"],
                limit=50
            )
            
            return {
                "database": self.database,
                "url": self.url,
                "user_id": self.uid,
                "database_info": db_info,
                "installed_modules": modules
            }
        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            raise
    
    async def execute_workflow(self, model: str, signal: str, record_id: int):
        """Execute workflow signal on a record"""
        return await self.call("workflow", "trg_validate", [self.uid, model, record_id, signal])
    
    async def get_reports(self) -> List[Dict[str, Any]]:
        """Get available reports"""
        try:
            reports = await self.search_read(
                "ir.actions.report",
                [],
                ["name", "report_name", "model", "report_type"]
            )
            return reports
        except Exception as e:
            logger.error(f"Failed to get reports: {e}")
            raise
    
    async def render_report(self, report_name: str, record_ids: List[int], data: Dict[str, Any] = None) -> bytes:
        """Render a report"""
        if data is None:
            data = {}
        
        try:
            # Use the report service
            result = await self.call(
                "ir.actions.report",
                "_render",
                [report_name, record_ids],
                {"data": data}
            )
            return result
        except Exception as e:
            logger.error(f"Failed to render report {report_name}: {e}")
            raise
    
    async def close(self):
        """Close the connection"""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.authenticated = False
        logger.info("Odoo client connection closed")