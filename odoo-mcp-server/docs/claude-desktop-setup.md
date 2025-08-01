# Configuration Claude Desktop avec Odoo MCP Server

Ce guide explique comment configurer Claude Desktop pour utiliser le serveur MCP Odoo via HTTP.

## Prérequis

- Claude Desktop installé sur votre machine
- Serveur MCP Odoo démarré et accessible
- Accès aux fichiers de configuration de Claude Desktop

## 🔧 Configuration Claude Desktop

### 1. Localisation du fichier de configuration

Le fichier de configuration Claude Desktop se trouve à :

#### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Linux
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Structure de base du fichier de configuration

Si le fichier n'existe pas, créez-le avec cette structure :

```json
{
  "mcpServers": {},
  "globalShortcut": null
}
```

## 🚀 Configuration HTTP du serveur MCP Odoo

### Configuration de base (Mode lecture/écriture)

Ajoutez cette configuration dans la section `mcpServers` :

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": [
        "-e",
        "const { MCPHTTPClient } = require('@modelcontextprotocol/sdk/client/http'); const client = new MCPHTTPClient('http://localhost:8000'); client.connect().then(() => { client.request({ method: 'initialize', params: {} }).then(() => { process.stdin.pipe(client.transport.writer); client.transport.reader.pipe(process.stdout); }); });"
      ],
      "env": {
        "ODOO_MCP_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Configuration simplifiée avec npx

```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "http://localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Configuration avec Python (Alternative)

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": [
        "-c",
        "import requests; import json; import sys; url='http://localhost:8000'; response=requests.post(f'{url}/mcp/initialize'); capabilities=response.json(); print(json.dumps({'jsonrpc': '2.0', 'id': 1, 'result': capabilities})); sys.stdout.flush(); [print(json.dumps(requests.post(f'{url}/mcp/tools/call', json=json.loads(line)).json())) for line in sys.stdin]"
      ],
      "env": {
        "PYTHONPATH": ".",
        "ODOO_MCP_URL": "http://localhost:8000"
      }
    }
  }
}
```

## 📝 Configurations par Environnement

### Développement Local

```json
{
  "mcpServers": {
    "odoo-dev": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-http-client",
        "http://localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000",
        "NODE_ENV": "development"
      }
    }
  }
}
```

### Production/Serveur Distant

```json
{
  "mcpServers": {
    "odoo-prod": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client", 
        "https://votre-serveur-odoo-mcp.com/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "https://votre-serveur-odoo-mcp.com",
        "NODE_ENV": "production"
      }
    }
  }
}
```

### Mode Lecture Seule

```json
{
  "mcpServers": {
    "odoo-readonly": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "http://localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000",
        "MCP_MODE": "readonly"
      }
    }
  }
}
```

## 🔐 Configuration avec Authentification

### Avec clé API

```json
{
  "mcpServers": {
    "odoo-secure": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "http://localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000",
        "API_KEY": "votre-cle-api-secrete",
        "AUTHORIZATION": "Bearer votre-cle-api-secrete"
      }
    }
  }
}
```

### Avec authentification basique

```json
{
  "mcpServers": {
    "odoo-auth": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "http://username:password@localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000"
      }
    }
  }
}
```

## 🌐 Configuration Multi-Serveurs

Vous pouvez configurer plusieurs instances Odoo :

```json
{
  "mcpServers": {
    "odoo-production": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "https://prod-odoo-mcp.monentreprise.com/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "https://prod-odoo-mcp.monentreprise.com"
      }
    },
    "odoo-staging": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "https://staging-odoo-mcp.monentreprise.com/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "https://staging-odoo-mcp.monentreprise.com"
      }
    },
    "odoo-demo": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "http://localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000",
        "MCP_MODE": "readonly"
      }
    }
  }
}
```

## 🛠️ Configuration du Serveur MCP Odoo

### Paramètres serveur pour Claude Desktop

Dans votre fichier `.env` du serveur MCP :

```env
# Configuration pour Claude Desktop
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
CORS_ORIGINS=*

# Mode de fonctionnement
MCP_MODE=readwrite  # ou readonly

# Authentification (optionnel)
API_KEY=votre-cle-pour-claude

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DATABASE=votre_base
ODOO_USERNAME=votre_utilisateur
ODOO_PASSWORD=votre_motdepasse
```

### Démarrage du serveur

```bash
# Démarrer le serveur MCP
cd odoo-mcp-server
python start.py

# Vérifier que le serveur répond
curl http://localhost:8000/health
curl http://localhost:8000/mcp/mode
```

## ✅ Test de la Configuration

### 1. Vérifier la configuration Claude Desktop

Après avoir modifié le fichier de configuration :

1. Fermez complètement Claude Desktop
2. Redémarrez Claude Desktop
3. Ouvrez une nouvelle conversation

### 2. Tester la connexion MCP

Dans Claude Desktop, essayez ces commandes :

```
Peux-tu lister les outils MCP Odoo disponibles ?
```

```
Recherche les 5 premiers partenaires dans Odoo
```

```
Quels sont les modèles Odoo disponibles ?
```

### 3. Vérifier les logs

#### Logs du serveur MCP
```bash
# Regarder les logs du serveur
tail -f logs/mcp-server.log
```

#### Logs Claude Desktop
- **Windows** : `%APPDATA%\Claude\logs\`
- **macOS** : `~/Library/Logs/Claude/`
- **Linux** : `~/.config/Claude/logs/`

## 🚨 Dépannage

### Problème : Claude Desktop ne voit pas le serveur MCP

**Solutions :**
1. Vérifiez que le serveur MCP est démarré : `curl http://localhost:8000/health`
2. Vérifiez la syntaxe JSON du fichier de configuration
3. Redémarrez Claude Desktop complètement
4. Vérifiez les logs Claude Desktop

### Problème : Erreur de connexion HTTP

**Solutions :**
1. Vérifiez l'URL dans la configuration
2. Testez manuellement : `curl http://localhost:8000/mcp/initialize`
3. Vérifiez les paramètres CORS du serveur
4. Contrôlez les pare-feu/proxy

### Problème : Permissions refusées

**Solutions :**
1. Vérifiez le mode du serveur : `curl http://localhost:8000/mcp/mode`
2. Ajustez `MCP_MODE` dans `.env`
3. Vérifiez les credentials Odoo
4. Contrôlez les droits utilisateur Odoo

### Problème : Outils MCP non disponibles

**Solutions :**
1. Vérifiez la liste des outils : `curl http://localhost:8000/mcp/tools/list`
2. Redémarrez le serveur MCP
3. Vérifiez la configuration Odoo
4. Consultez les logs du serveur

## 📋 Configuration Complète Exemple

Fichier `claude_desktop_config.json` complet :

```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http-client",
        "http://localhost:8000/mcp"
      ],
      "env": {
        "MCP_HTTP_URL": "http://localhost:8000",
        "NODE_ENV": "development"
      }
    }
  },
  "globalShortcut": "CommandOrControl+Shift+C"
}
```

## 🔗 Liens Utiles

- [Documentation officielle Claude Desktop](https://docs.anthropic.com/claude/desktop)
- [MCP SDK Documentation](https://docs.anthropic.com/mcp)
- [Configuration du serveur MCP Odoo](../README.md)
- [Guide des modes de fonctionnement](modes.md)

## 💡 Conseils d'Usage

1. **Testez d'abord en local** avant de déployer en production
2. **Utilisez le mode readonly** pour les démonstrations et analyses
3. **Configurez l'authentification** pour les environnements de production
4. **Surveillez les logs** pour diagnostiquer les problèmes
5. **Sauvegardez** vos configurations avant modification