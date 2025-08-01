"""
Système de gestion des permissions pour le serveur MCP Odoo
"""

import logging
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class MCPMode(Enum):
    """Modes de fonctionnement MCP"""
    READONLY = "readonly"
    READWRITE = "readwrite"

class PermissionLevel(Enum):
    """Niveaux de permission"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"

class PermissionManager:
    """Gestionnaire des permissions selon le mode MCP"""
    
    def __init__(self, mode: str):
        self.mode = MCPMode(mode.lower())
        self._setup_permissions()
    
    def _setup_permissions(self):
        """Configure les permissions selon le mode"""
        if self.mode == MCPMode.READONLY:
            self.allowed_permissions = {PermissionLevel.READ, PermissionLevel.EXECUTE}
            self.forbidden_permissions = {PermissionLevel.WRITE, PermissionLevel.DELETE}
        else:  # READWRITE
            self.allowed_permissions = {
                PermissionLevel.READ, 
                PermissionLevel.WRITE, 
                PermissionLevel.DELETE, 
                PermissionLevel.EXECUTE
            }
            self.forbidden_permissions = set()
        
        logger.info(f"Permissions configurées pour le mode {self.mode.value}")
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """Vérifie si un outil est autorisé selon le mode"""
        tool_permissions = self._get_tool_permissions(tool_name)
        return not any(perm in self.forbidden_permissions for perm in tool_permissions)
    
    def _get_tool_permissions(self, tool_name: str) -> List[PermissionLevel]:
        """Retourne les permissions requises pour un outil"""
        tool_permission_map = {
            # Outils en lecture seule
            "odoo_search": [PermissionLevel.READ],
            "odoo_fields_get": [PermissionLevel.READ],
            "odoo_call_readonly": [PermissionLevel.READ, PermissionLevel.EXECUTE],
            
            # Outils d'écriture
            "odoo_create": [PermissionLevel.WRITE],
            "odoo_write": [PermissionLevel.WRITE],
            "odoo_unlink": [PermissionLevel.DELETE],
            
            # Outils mixtes (lecture + exécution)
            "odoo_call": [PermissionLevel.READ, PermissionLevel.EXECUTE],
            "odoo_report": [PermissionLevel.READ, PermissionLevel.EXECUTE],
        }
        
        return tool_permission_map.get(tool_name, [PermissionLevel.READ])
    
    def validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Valide un appel d'outil selon les permissions"""
        if not self.is_tool_allowed(tool_name):
            logger.warning(f"Outil {tool_name} non autorisé en mode {self.mode.value}")
            return False
        
        # Validation spécifique pour odoo_call
        if tool_name == "odoo_call":
            return self._validate_odoo_call(arguments)
        
        return True
    
    def _validate_odoo_call(self, arguments: Dict[str, Any]) -> bool:
        """Valide un appel odoo_call selon le mode"""
        method = arguments.get("method", "").lower()
        
        # Méthodes d'écriture interdites en mode readonly
        write_methods = {
            "create", "write", "unlink", "copy", "toggle_active",
            "action_confirm", "action_cancel", "action_done",
            "button_confirm", "button_cancel", "post", "reconcile"
        }
        
        if self.mode == MCPMode.READONLY:
            if any(write_method in method for write_method in write_methods):
                logger.warning(f"Méthode {method} interdite en mode readonly")
                return False
        
        return True
    
    def get_allowed_tools(self) -> List[str]:
        """Retourne la liste des outils autorisés"""
        all_tools = [
            "odoo_search", "odoo_create", "odoo_write", "odoo_unlink",
            "odoo_call", "odoo_fields_get", "odoo_report"
        ]
        
        return [tool for tool in all_tools if self.is_tool_allowed(tool)]
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le mode actuel"""
        return {
            "mode": self.mode.value,
            "allowed_permissions": [p.value for p in self.allowed_permissions],
            "forbidden_permissions": [p.value for p in self.forbidden_permissions],
            "allowed_tools": self.get_allowed_tools(),
            "description": self._get_mode_description()
        }
    
    def _get_mode_description(self) -> str:
        """Retourne la description du mode"""
        if self.mode == MCPMode.READONLY:
            return "Mode lecture seule - Seules les opérations de lecture et consultation sont autorisées"
        else:
            return "Mode lecture/écriture - Toutes les opérations sont autorisées"

class PermissionError(Exception):
    """Exception levée lors d'une violation de permission"""
    pass