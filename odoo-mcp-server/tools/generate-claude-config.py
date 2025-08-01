#!/usr/bin/env python3

"""
Générateur de configuration Claude Desktop pour le serveur MCP Odoo
"""

import json
import os
import platform
import argparse
from pathlib import Path
from typing import Dict, Any

class ClaudeConfigGenerator:
    """Générateur de configuration Claude Desktop"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.config_path = self._get_config_path()
    
    def _get_config_path(self) -> Path:
        """Détermine le chemin du fichier de configuration selon l'OS"""
        if self.system == "windows":
            return Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
        elif self.system == "darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        else:  # Linux
            return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    
    def load_existing_config(self) -> Dict[str, Any]:
        """Charge la configuration existante ou crée une nouvelle"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Erreur lecture config existante: {e}")
                return self._default_config()
        else:
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            "mcpServers": {},
            "globalShortcut": None
        }
    
    def generate_odoo_config(self, 
                           name: str = "odoo",
                           url: str = "http://localhost:8000",
                           mode: str = "readwrite",
                           auth_method: str = "none",
                           api_key: str = "",
                           username: str = "",
                           password: str = "") -> Dict[str, Any]:
        """Génère la configuration pour le serveur MCP Odoo"""
        
        base_config = {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-http-client",
                f"{url}/mcp"
            ],
            "env": {
                "MCP_HTTP_URL": url,
                "NODE_ENV": "production" if "localhost" not in url else "development"
            }
        }
        
        # Ajouter le mode si spécifié
        if mode != "readwrite":
            base_config["env"]["MCP_MODE"] = mode
        
        # Ajouter l'authentification selon la méthode
        if auth_method == "api_key" and api_key:
            base_config["env"]["API_KEY"] = api_key
            base_config["env"]["AUTHORIZATION"] = f"Bearer {api_key}"
        elif auth_method == "basic" and username and password:
            # Modifier l'URL pour inclure l'auth basique
            auth_url = url.replace("://", f"://{username}:{password}@")
            base_config["args"][-1] = f"{auth_url}/mcp"
        
        return base_config
    
    def add_server_config(self, config: Dict[str, Any], server_config: Dict[str, Any], name: str):
        """Ajoute une configuration serveur à la config Claude"""
        config["mcpServers"][name] = server_config
    
    def save_config(self, config: Dict[str, Any], backup: bool = True):
        """Sauvegarde la configuration"""
        # Créer le répertoire si nécessaire
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Faire une sauvegarde si demandé
        if backup and self.config_path.exists():
            backup_path = self.config_path.with_suffix('.json.backup')
            self.config_path.replace(backup_path)
            print(f"📋 Sauvegarde créée: {backup_path}")
        
        # Sauvegarder la nouvelle configuration
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuration sauvée: {self.config_path}")
    
    def generate_examples(self) -> Dict[str, Dict[str, Any]]:
        """Génère des exemples de configuration"""
        examples = {}
        
        # Configuration locale basique
        examples["local_basic"] = self.generate_odoo_config(
            name="odoo-local",
            url="http://localhost:8000",
            mode="readwrite"
        )
        
        # Configuration locale lecture seule
        examples["local_readonly"] = self.generate_odoo_config(
            name="odoo-readonly",
            url="http://localhost:8000", 
            mode="readonly"
        )
        
        # Configuration production avec API key
        examples["prod_secure"] = self.generate_odoo_config(
            name="odoo-prod",
            url="https://your-odoo-mcp.example.com",
            mode="readwrite",
            auth_method="api_key",
            api_key="your-secret-api-key"
        )
        
        # Configuration avec auth basique
        examples["staging_auth"] = self.generate_odoo_config(
            name="odoo-staging",
            url="https://staging-odoo-mcp.example.com",
            mode="readwrite",
            auth_method="basic",
            username="api_user",
            password="secure_password"
        )
        
        return examples
    
    def interactive_setup(self):
        """Configuration interactive"""
        print("🚀 Configuration Interactive Claude Desktop MCP Odoo")
        print("=" * 60)
        
        # Charger config existante
        config = self.load_existing_config()
        
        # Informations de base
        name = input("Nom du serveur MCP (odoo): ").strip() or "odoo"
        url = input("URL du serveur MCP (http://localhost:8000): ").strip() or "http://localhost:8000"
        
        # Mode
        print("\nModes disponibles:")
        print("1. readwrite - Toutes les opérations (défaut)")
        print("2. readonly - Lecture seule")
        mode_choice = input("Choisir le mode (1-2): ").strip() or "1"
        mode = "readwrite" if mode_choice == "1" else "readonly"
        
        # Authentification
        print("\nMéthodes d'authentification:")
        print("1. none - Aucune (défaut)")
        print("2. api_key - Clé API")
        print("3. basic - Authentification basique")
        auth_choice = input("Choisir l'authentification (1-3): ").strip() or "1"
        
        auth_method = "none"
        api_key = ""
        username = ""
        password = ""
        
        if auth_choice == "2":
            auth_method = "api_key"
            api_key = input("Clé API: ").strip()
        elif auth_choice == "3":
            auth_method = "basic"
            username = input("Nom d'utilisateur: ").strip()
            password = input("Mot de passe: ").strip()
        
        # Générer la configuration
        server_config = self.generate_odoo_config(
            name=name,
            url=url,
            mode=mode,
            auth_method=auth_method,
            api_key=api_key,
            username=username,
            password=password
        )
        
        # Ajouter à la config
        self.add_server_config(config, server_config, name)
        
        # Afficher la configuration
        print(f"\n📋 Configuration générée pour '{name}':")
        print(json.dumps({name: server_config}, indent=2))
        
        # Confirmer la sauvegarde
        save = input("\nSauvegarder cette configuration ? (Y/n): ").strip().lower()
        if save != 'n':
            self.save_config(config)
            print(f"\n✅ Configuration ajoutée pour le serveur '{name}'")
            print("\n📝 Prochaines étapes:")
            print("1. Redémarrez Claude Desktop")
            print("2. Testez la connexion avec: 'Peux-tu lister les outils MCP Odoo ?'")
        else:
            print("❌ Configuration non sauvegardée")

def main():
    parser = argparse.ArgumentParser(description="Générateur de configuration Claude Desktop MCP Odoo")
    parser.add_argument("--interactive", "-i", action="store_true", help="Mode interactif")
    parser.add_argument("--examples", "-e", action="store_true", help="Générer des exemples")
    parser.add_argument("--name", default="odoo", help="Nom du serveur MCP")
    parser.add_argument("--url", default="http://localhost:8000", help="URL du serveur MCP")
    parser.add_argument("--mode", choices=["readonly", "readwrite"], default="readwrite", help="Mode de fonctionnement")
    parser.add_argument("--auth-method", choices=["none", "api_key", "basic"], default="none", help="Méthode d'authentification")
    parser.add_argument("--api-key", help="Clé API")
    parser.add_argument("--username", help="Nom d'utilisateur (auth basique)")
    parser.add_argument("--password", help="Mot de passe (auth basique)")
    parser.add_argument("--no-backup", action="store_true", help="Ne pas créer de sauvegarde")
    
    args = parser.parse_args()
    
    generator = ClaudeConfigGenerator()
    
    if args.interactive:
        generator.interactive_setup()
    elif args.examples:
        examples = generator.generate_examples()
        print("📋 Exemples de Configuration Claude Desktop MCP Odoo")
        print("=" * 60)
        for name, config in examples.items():
            print(f"\n## {name.replace('_', ' ').title()}")
            print(f"```json")
            print(json.dumps({"mcpServers": {name: config}}, indent=2))
            print("```")
    else:
        # Mode ligne de commande
        config = generator.load_existing_config()
        server_config = generator.generate_odoo_config(
            name=args.name,
            url=args.url,
            mode=args.mode,
            auth_method=args.auth_method,
            api_key=args.api_key or "",
            username=args.username or "",
            password=args.password or ""
        )
        
        generator.add_server_config(config, server_config, args.name)
        generator.save_config(config, backup=not args.no_backup)
        
        print(f"✅ Configuration '{args.name}' ajoutée avec succès")

if __name__ == "__main__":
    main()