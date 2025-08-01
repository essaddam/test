# Guide Rapide - Claude Desktop + Odoo MCP Server

Guide de démarrage rapide pour utiliser le serveur MCP Odoo avec Claude Desktop.

## 🚀 Installation en 5 Minutes

### 1. Préparer le serveur MCP

```bash
# Cloner et installer
git clone <votre-repo>
cd odoo-mcp-server
pip install -r requirements.txt

# Configurer
cp .env.example .env
# Éditer .env avec vos paramètres Odoo

# Tester la connexion
python examples/test_connection.py

# Démarrer le serveur
python start.py
```

### 2. Configurer Claude Desktop

```bash
# Génération automatique de la configuration
make claude-config

# Ou voir des exemples
make claude-examples
```

### 3. Vérification complète

```bash
# Vérifier tout le setup
make check-setup
```

## 📝 Configuration Manuelle Claude Desktop

### Localisation du fichier de configuration

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Configuration de base

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

## 🔒 Modes de Fonctionnement

### Mode Lecture Seule
```env
MCP_MODE=readonly
```
- ✅ Recherche, lecture, rapports
- ❌ Création, modification, suppression

### Mode Lecture/Écriture
```env
MCP_MODE=readwrite
```
- ✅ Toutes les opérations

## 🧪 Test de la Configuration

### 1. Redémarrer Claude Desktop
Fermez complètement et relancez Claude Desktop.

### 2. Tester dans Claude Desktop

```
Peux-tu lister les outils MCP Odoo disponibles ?
```

```
Recherche les 5 premiers partenaires dans Odoo
```

```
Quel est le mode de fonctionnement du serveur MCP ?
```

## 🛠️ Commandes Utiles

```bash
# Vérifier le serveur
curl http://localhost:8000/health
curl http://localhost:8000/mcp/mode

# Tester les modes
python examples/mode_demo.py

# Génération config Claude
python tools/generate-claude-config.py --interactive

# Vérification complète
python tools/check-setup.py
```

## 💡 Exemples d'Usage dans Claude Desktop

### Analyse de Données
```
"Analyse les tendances de vente des 6 derniers mois"
"Quels sont les clients qui n'ont pas commandé depuis 3 mois ?"
"Montre-moi les produits les plus vendus par catégorie"
```

### Gestion des Données
```
"Crée un nouveau client pour TechCorp avec l'email contact@techcorp.com"
"Met à jour le prix du produit 'Laptop Pro' à 1299€"
"Génère un rapport de facture pour la commande SO001"
```

### Exploration du Système
```
"Quels sont les modèles Odoo disponibles ?"
"Montre-moi la structure du modèle res.partner"
"Liste les entreprises configurées dans le système"
```

## 🚨 Dépannage Rapide

### Claude Desktop ne voit pas le serveur MCP
1. Vérifier que le serveur MCP fonctionne: `curl http://localhost:8000/health`
2. Vérifier la syntaxe JSON du fichier de configuration
3. Redémarrer Claude Desktop complètement
4. Vérifier les logs Claude Desktop

### Erreurs de permissions
1. Vérifier le mode: `curl http://localhost:8000/mcp/mode`
2. Ajuster `MCP_MODE` dans `.env` si nécessaire
3. Redémarrer le serveur MCP

### Erreur de connexion Odoo
1. Tester la connexion: `python examples/test_connection.py`
2. Vérifier les paramètres dans `.env`
3. Contrôler les droits utilisateur Odoo

## 📚 Documentation Complète

- [Configuration détaillée Claude Desktop](docs/claude-desktop-setup.md)
- [Guide des outils et ressources](docs/claude-desktop-tools.md)
- [Modes de fonctionnement](docs/modes.md)
- [Configuration serveur](config_guide.md)

## 🎯 Workflow Recommandé

1. **Développement** : Mode `readonly` pour explorer et tester
2. **Production** : Mode `readwrite` avec utilisateur dédié
3. **Démonstration** : Mode `readonly` avec données de démo
4. **Intégration** : Mode `readwrite` avec authentification forte

---

**🚀 Prêt à utiliser Odoo avec Claude Desktop !**

Pour toute question, consultez les guides détaillés dans le dossier `docs/`.