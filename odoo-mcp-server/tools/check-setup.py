#!/usr/bin/env python3

"""
Script de vérification complète du setup Odoo MCP Server
"""

import sys
import subprocess
import json
import platform
from pathlib import Path
import httpx
import asyncio

class SetupChecker:
    """Vérificateur de configuration complète"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
    
    def check_python_version(self):
        """Vérifier la version Python"""
        print("🐍 Vérification de Python...")
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.success.append(f"Python {version.major}.{version.minor}.{version.micro} ✅")
        else:
            self.errors.append(f"Python 3.8+ requis, trouvé {version.major}.{version.minor}")
    
    def check_dependencies(self):
        """Vérifier les dépendances Python"""
        print("📦 Vérification des dépendances...")
        
        required_packages = [
            "fastapi", "uvicorn", "httpx", "pydantic", 
            "python-dotenv", "websockets"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.success.append(f"Package {package} installé ✅")
            except ImportError:
                self.errors.append(f"Package {package} manquant")
    
    def check_env_file(self):
        """Vérifier le fichier .env"""
        print("⚙️  Vérification du fichier .env...")
        
        env_path = Path(".env")
        if not env_path.exists():
            self.warnings.append("Fichier .env manquant (utilisez: cp .env.example .env)")
            return
        
        required_vars = ["ODOO_URL", "ODOO_DATABASE", "ODOO_USERNAME", "ODOO_PASSWORD"]
        
        try:
            with open(env_path) as f:
                content = f.read()
            
            for var in required_vars:
                if f"{var}=" in content:
                    self.success.append(f"Variable {var} définie ✅")
                else:
                    self.errors.append(f"Variable {var} manquante dans .env")
                    
        except IOError as e:
            self.errors.append(f"Erreur lecture .env: {e}")
    
    async def check_mcp_server(self):
        """Vérifier que le serveur MCP répond"""
        print("🚀 Vérification du serveur MCP...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test de santé
                response = await client.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    self.success.append("Serveur MCP accessible ✅")
                    
                    # Test mode
                    mode_response = await client.get("http://localhost:8000/mcp/mode")
                    if mode_response.status_code == 200:
                        mode_info = mode_response.json()
                        self.success.append(f"Mode MCP: {mode_info['mode']} ✅")
                    
                    # Test outils
                    tools_response = await client.post("http://localhost:8000/mcp/tools/list")
                    if tools_response.status_code == 200:
                        tools = tools_response.json()
                        tool_count = len(tools.get('tools', []))
                        self.success.append(f"{tool_count} outils MCP disponibles ✅")
                    
                else:
                    self.errors.append(f"Serveur MCP inaccessible (status: {response.status_code})")
                    
        except Exception as e:
            self.warnings.append(f"Serveur MCP non démarré: {e}")
    
    def check_claude_config(self):
        """Vérifier la configuration Claude Desktop"""
        print("🤖 Vérification configuration Claude Desktop...")
        
        system = platform.system().lower()
        
        if system == "windows":
            config_path = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
        elif system == "darwin":
            config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        else:
            config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        
        if not config_path.exists():
            self.warnings.append(f"Configuration Claude Desktop non trouvée: {config_path}")
            return
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            if "mcpServers" in config:
                odoo_servers = [name for name in config["mcpServers"].keys() if "odoo" in name.lower()]
                if odoo_servers:
                    self.success.append(f"Serveurs Odoo MCP configurés: {', '.join(odoo_servers)} ✅")
                else:
                    self.warnings.append("Aucun serveur Odoo MCP configuré dans Claude Desktop")
            else:
                self.warnings.append("Section mcpServers manquante dans configuration Claude")
                
        except (json.JSONDecodeError, IOError) as e:
            self.errors.append(f"Erreur lecture config Claude Desktop: {e}")
    
    def check_odoo_connection(self):
        """Vérifier la connexion Odoo"""
        print("🏢 Vérification connexion Odoo...")
        
        try:
            # Utiliser le script de test existant
            result = subprocess.run([
                sys.executable, "examples/test_connection.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.success.append("Connexion Odoo fonctionnelle ✅")
            else:
                error_output = result.stderr or result.stdout
                self.errors.append(f"Erreur connexion Odoo: {error_output[:200]}...")
                
        except subprocess.TimeoutExpired:
            self.errors.append("Timeout connexion Odoo")
        except FileNotFoundError:
            self.warnings.append("Script test_connection.py non trouvé")
        except Exception as e:
            self.errors.append(f"Erreur test Odoo: {e}")
    
    def check_nodejs_npm(self):
        """Vérifier Node.js et npm pour Claude Desktop"""
        print("🟢 Vérification Node.js/npm...")
        
        try:
            # Vérifier Node.js
            node_result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if node_result.returncode == 0:
                version = node_result.stdout.strip()
                self.success.append(f"Node.js {version} installé ✅")
            else:
                self.warnings.append("Node.js non installé (requis pour Claude Desktop)")
            
            # Vérifier npm
            npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if npm_result.returncode == 0:
                version = npm_result.stdout.strip()
                self.success.append(f"npm {version} installé ✅")
            else:
                self.warnings.append("npm non installé")
                
        except subprocess.CalledProcessError:
            self.warnings.append("Erreur vérification Node.js/npm")
        except FileNotFoundError:
            self.warnings.append("Node.js/npm non trouvés dans PATH")
    
    def print_results(self):
        """Afficher les résultats de vérification"""
        print("\n" + "="*60)
        print("📋 RÉSULTATS DE VÉRIFICATION")
        print("="*60)
        
        if self.success:
            print(f"\n✅ Succès ({len(self.success)}):")
            for item in self.success:
                print(f"   {item}")
        
        if self.warnings:
            print(f"\n⚠️  Avertissements ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"   {item}")
        
        if self.errors:
            print(f"\n❌ Erreurs ({len(self.errors)}):")
            for item in self.errors:
                print(f"   {item}")
        
        print(f"\n📊 Score: {len(self.success)} succès, {len(self.warnings)} avertissements, {len(self.errors)} erreurs")
        
        if self.errors:
            print("\n🔧 Actions recommandées:")
            if any("package" in error.lower() for error in self.errors):
                print("   - Installer les dépendances: pip install -r requirements.txt")
            if any(".env" in error for error in self.errors):
                print("   - Configurer .env: cp .env.example .env && nano .env")
            if any("odoo" in error.lower() for error in self.errors):
                print("   - Vérifier paramètres Odoo dans .env")
            if any("python" in error.lower() for error in self.errors):
                print("   - Mettre à jour Python vers 3.8+")
        
        if self.warnings:
            print("\n💡 Suggestions:")
            if any("claude" in warning.lower() for warning in self.warnings):
                print("   - Configurer Claude Desktop: make claude-config")
            if any("serveur" in warning.lower() for warning in self.warnings):
                print("   - Démarrer le serveur MCP: python start.py")
            if any("node" in warning.lower() for warning in self.warnings):
                print("   - Installer Node.js: https://nodejs.org/")
        
        return len(self.errors) == 0

async def main():
    """Fonction principale de vérification"""
    print("🔍 VÉRIFICATION COMPLÈTE ODOO MCP SERVER")
    print("="*60)
    
    checker = SetupChecker()
    
    # Vérifications synchrones
    checker.check_python_version()
    checker.check_dependencies()
    checker.check_env_file()
    checker.check_claude_config()
    checker.check_nodejs_npm()
    
    # Vérifications asynchrones
    await checker.check_mcp_server()
    
    # Vérification Odoo (peut être lente)
    checker.check_odoo_connection()
    
    # Afficher résultats
    success = checker.print_results()
    
    if success:
        print("\n🎉 Tout semble en ordre ! Votre serveur MCP Odoo est prêt.")
        print("\n🚀 Prochaines étapes:")
        print("   1. Démarrer le serveur: python start.py")
        print("   2. Tester avec Claude Desktop")
        print("   3. Ou utiliser l'exemple: python examples/client_example.py")
    else:
        print("\n⚠️  Des problèmes ont été détectés. Consultez les recommandations ci-dessus.")
        return False
    
    return True

if __name__ == "__main__":
    import os
    # Changer vers le répertoire du script pour les chemins relatifs
    os.chdir(Path(__file__).parent.parent)
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)