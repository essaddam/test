#!/usr/bin/env python3

"""
Script de test de connexion Odoo
Vérifie la configuration et la connexion à Odoo
"""

import sys
import os
from pathlib import Path
import asyncio
import xmlrpc.client

# Ajouter le répertoire src au chemin Python
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.config import Config
from odoo.client import OdooClient

def test_xmlrpc_connection(config):
    """Test de connexion XML-RPC direct"""
    print("🔌 Test de connexion XML-RPC direct...")
    
    try:
        # Test de connexion au service common
        common_url = f"{config.odoo_url}/xmlrpc/2/common"
        common = xmlrpc.client.ServerProxy(common_url)
        
        # Obtenir les informations de version
        version_info = common.version()
        print(f"✅ Connexion réussie au serveur Odoo")
        print(f"   Version: {version_info.get('server_version', 'N/A')}")
        print(f"   Série: {version_info.get('server_serie', 'N/A')}")
        
        # Test d'authentification
        uid = common.authenticate(
            config.odoo_database,
            config.odoo_username, 
            config.odoo_password,
            {}
        )
        
        if uid:
            print(f"✅ Authentification réussie - ID utilisateur: {uid}")
            return True
        else:
            print("❌ Échec de l'authentification")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion XML-RPC: {e}")
        return False

async def test_odoo_client(config):
    """Test du client Odoo asynchrone"""
    print("\n🔌 Test du client Odoo asynchrone...")
    
    try:
        async with OdooClient(config) as client:
            await client.connect()
            print("✅ Connexion client Odoo réussie")
            
            # Test de liste des modèles
            models = await client.list_models()
            print(f"✅ Récupération de {len(models)} modèles")
            
            # Test de recherche d'utilisateurs
            users = await client.search_read(
                "res.users", 
                [], 
                ["name", "login"], 
                limit=5
            )
            print(f"✅ Récupération de {len(users)} utilisateurs")
            
            # Test de récupération des informations serveur
            server_info = await client.get_server_info()
            print("✅ Informations serveur récupérées")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur client Odoo: {e}")
        return False

def print_config_info(config):
    """Affiche les informations de configuration"""
    print("📋 Configuration détectée:")
    print(f"   URL Odoo: {config.odoo_url}")
    print(f"   Base de données: {config.odoo_database}")
    print(f"   Nom d'utilisateur: {config.odoo_username}")
    print(f"   Mot de passe: {'*' * len(config.odoo_password) if config.odoo_password else 'NON DÉFINI'}")
    print()

def check_requirements():
    """Vérifie les prérequis"""
    print("🔍 Vérification des prérequis...")
    
    required_vars = ["ODOO_URL", "ODOO_DATABASE", "ODOO_USERNAME", "ODOO_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("💡 Créez un fichier .env basé sur .env.example")
        return False
    else:
        print("✅ Toutes les variables d'environnement requises sont définies")
        return True

async def main():
    """Fonction principale de test"""
    print("🚀 Test de connexion Odoo MCP Server")
    print("=" * 50)
    
    # Vérifier les prérequis
    if not check_requirements():
        sys.exit(1)
    
    try:
        # Charger la configuration
        config = Config()
        print_config_info(config)
        
        # Test de connexion XML-RPC
        xmlrpc_success = test_xmlrpc_connection(config)
        
        if xmlrpc_success:
            # Test du client Odoo asynchrone
            client_success = await test_odoo_client(config)
            
            if client_success:
                print("\n🎉 Tous les tests de connexion ont réussi!")
                print("✅ Le serveur MCP peut se connecter à Odoo")
                return True
            else:
                print("\n❌ Échec du test du client Odoo")
                return False
        else:
            print("\n❌ Échec du test de connexion XML-RPC")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur lors du test de configuration: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)