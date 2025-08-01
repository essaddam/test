#!/usr/bin/env python3

"""
Démonstration des modes lecture seule et lecture/écriture du serveur MCP Odoo
"""

import asyncio
import json
import httpx
from typing import Dict, Any

class MCPModeDemo:
    """Démonstrateur des modes MCP"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.http_client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def get_mode_info(self) -> Dict[str, Any]:
        """Récupère les informations sur le mode actuel"""
        response = await self.http_client.get(f"{self.base_url}/mcp/mode")
        return response.json()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Récupère les capacités du serveur"""
        response = await self.http_client.post(f"{self.base_url}/mcp/initialize")
        return response.json()
    
    async def list_tools(self) -> Dict[str, Any]:
        """Liste les outils disponibles"""
        response = await self.http_client.post(f"{self.base_url}/mcp/tools/list")
        return response.json()
    
    async def test_read_operation(self) -> Dict[str, Any]:
        """Test d'une opération de lecture (toujours autorisée)"""
        payload = {
            "method": "odoo_search",
            "params": {
                "model": "res.partner",
                "domain": [],
                "fields": ["name", "email"],
                "limit": 5
            }
        }
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/mcp/tools/call",
                json=payload
            )
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_write_operation(self) -> Dict[str, Any]:
        """Test d'une opération d'écriture (interdite en mode readonly)"""
        payload = {
            "method": "odoo_create",
            "params": {
                "model": "res.partner",
                "values": {
                    "name": "Test Partner MCP",
                    "email": "test@mcp.example.com",
                    "is_company": False
                }
            }
        }
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/mcp/tools/call",
                json=payload
            )
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_delete_operation(self) -> Dict[str, Any]:
        """Test d'une opération de suppression (interdite en mode readonly)"""
        # D'abord chercher un enregistrement test
        search_payload = {
            "method": "odoo_search",
            "params": {
                "model": "res.partner",
                "domain": [["name", "=", "Test Partner MCP"]],
                "fields": ["id"],
                "limit": 1
            }
        }
        
        try:
            search_response = await self.http_client.post(
                f"{self.base_url}/mcp/tools/call",
                json=search_payload
            )
            search_result = search_response.json()
            
            if search_result.get("result", {}).get("records"):
                record_id = search_result["result"]["records"][0]["id"]
                
                delete_payload = {
                    "method": "odoo_unlink",
                    "params": {
                        "model": "res.partner",
                        "ids": [record_id]
                    }
                }
                
                response = await self.http_client.post(
                    f"{self.base_url}/mcp/tools/call",
                    json=delete_payload
                )
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": "Aucun enregistrement test trouvé à supprimer"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_restricted_call(self) -> Dict[str, Any]:
        """Test d'un appel avec méthode d'écriture (restrictive en mode readonly)"""
        payload = {
            "method": "odoo_call",
            "params": {
                "model": "res.partner",
                "method": "write",
                "args": [[1], {"name": "Modified by MCP"}]
            }
        }
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/mcp/tools/call",
                json=payload
            )
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def demo_readonly_mode():
    """Démonstration du mode lecture seule"""
    print("🔒 Démonstration du mode LECTURE SEULE")
    print("=" * 50)
    
    async with MCPModeDemo() as demo:
        # Informations sur le mode
        mode_info = await demo.get_mode_info()
        print(f"Mode actuel: {mode_info['mode']}")
        print(f"Description: {mode_info['description']}")
        print(f"Outils autorisés: {len(mode_info['allowed_tools'])}")
        print(f"Permissions interdites: {mode_info['forbidden_permissions']}")
        print()
        
        # Liste des outils disponibles
        tools = await demo.list_tools()
        print(f"Outils disponibles ({len(tools['tools'])}):")
        for tool in tools['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
        print()
        
        # Test de lecture (autorisé)
        print("✅ Test de lecture (odoo_search):")
        read_result = await demo.test_read_operation()
        if read_result['success']:
            count = read_result['data'].get('result', {}).get('count', 0)
            print(f"   Succès - {count} enregistrements trouvés")
        else:
            print(f"   Erreur: {read_result['error']}")
        print()
        
        # Test d'écriture (interdit)
        print("❌ Test d'écriture (odoo_create):")
        write_result = await demo.test_write_operation()
        if write_result['success']:
            print("   Succès - Enregistrement créé")
        else:
            print(f"   Erreur attendue: {write_result['error']}")
        print()
        
        # Test d'appel restreint (interdit)
        print("❌ Test d'appel restreint (odoo_call avec write):")
        call_result = await demo.test_restricted_call()
        if call_result['success']:
            print("   Succès - Méthode exécutée")
        else:
            print(f"   Erreur attendue: {call_result['error']}")

async def demo_readwrite_mode():
    """Démonstration du mode lecture/écriture"""
    print("\n🔓 Démonstration du mode LECTURE/ÉCRITURE")
    print("=" * 50)
    
    async with MCPModeDemo() as demo:
        # Informations sur le mode
        mode_info = await demo.get_mode_info()
        print(f"Mode actuel: {mode_info['mode']}")
        print(f"Description: {mode_info['description']}")
        print(f"Outils autorisés: {len(mode_info['allowed_tools'])}")
        print(f"Permissions interdites: {mode_info['forbidden_permissions']}")
        print()
        
        # Test de lecture (autorisé)
        print("✅ Test de lecture (odoo_search):")
        read_result = await demo.test_read_operation()
        if read_result['success']:
            count = read_result['data'].get('result', {}).get('count', 0)
            print(f"   Succès - {count} enregistrements trouvés")
        else:
            print(f"   Erreur: {read_result['error']}")
        print()
        
        # Test d'écriture (autorisé)
        print("✅ Test d'écriture (odoo_create):")
        write_result = await demo.test_write_operation()
        if write_result['success']:
            record_id = write_result['data'].get('result', {}).get('created_id')
            print(f"   Succès - Enregistrement créé avec ID: {record_id}")
        else:
            print(f"   Erreur: {write_result['error']}")
        print()
        
        # Test de suppression (autorisé)
        print("✅ Test de suppression (odoo_unlink):")
        delete_result = await demo.test_delete_operation()
        if delete_result['success']:
            print("   Succès - Enregistrement supprimé")
        else:
            print(f"   Erreur: {delete_result['error']}")
        print()
        
        # Test d'appel libre (autorisé)
        print("✅ Test d'appel libre (odoo_call):")
        call_result = await demo.test_restricted_call()
        if call_result['success']:
            print("   Succès - Méthode exécutée")
        else:
            print(f"   Erreur: {call_result['error']}")

async def main():
    """Fonction principale de démonstration"""
    print("🚀 Démonstration des modes MCP Odoo")
    print("=" * 60)
    
    try:
        # Vérifier le mode actuel
        async with MCPModeDemo() as demo:
            mode_info = await demo.get_mode_info()
            current_mode = mode_info['mode']
            
            if current_mode == 'readonly':
                await demo_readonly_mode()
                print("\n💡 Pour tester le mode lecture/écriture:")
                print("   1. Changez MCP_MODE=readwrite dans le fichier .env")
                print("   2. Redémarrez le serveur: python start.py")
                print("   3. Relancez cette démonstration")
                
            elif current_mode == 'readwrite':
                await demo_readwrite_mode()
                print("\n💡 Pour tester le mode lecture seule:")
                print("   1. Changez MCP_MODE=readonly dans le fichier .env")
                print("   2. Redémarrez le serveur: python start.py")
                print("   3. Relancez cette démonstration")
                
    except Exception as e:
        print(f"❌ Erreur de connexion au serveur: {e}")
        print("💡 Assurez-vous que le serveur MCP est démarré: python start.py")

if __name__ == "__main__":
    asyncio.run(main())