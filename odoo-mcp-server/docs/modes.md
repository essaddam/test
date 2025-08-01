# Modes de Fonctionnement MCP Odoo

Le serveur MCP Odoo propose deux modes de fonctionnement pour contrôler les permissions d'accès aux données Odoo.

## 🔒 Mode Lecture Seule (readonly)

### Description
En mode lecture seule, seules les opérations de consultation des données sont autorisées. Aucune modification, création ou suppression n'est possible.

### Configuration
```env
MCP_MODE=readonly
```

### Outils Autorisés
- ✅ `odoo_search` - Recherche d'enregistrements
- ✅ `odoo_fields_get` - Récupération des définitions de champs
- ✅ `odoo_report` - Génération de rapports
- ✅ `odoo_call` (méthodes de lecture uniquement)

### Outils Interdits
- ❌ `odoo_create` - Création d'enregistrements
- ❌ `odoo_write` - Modification d'enregistrements
- ❌ `odoo_unlink` - Suppression d'enregistrements
- ❌ `odoo_call` avec méthodes d'écriture

### Cas d'Usage
- **Tableaux de bord** en lecture seule
- **Intégrations de reporting**
- **Applications d'analyse** de données
- **API publiques** sans modification
- **Environnements de démonstration**

### Exemple de Configuration
```env
# Mode lecture seule pour un dashboard
ODOO_URL=https://demo.odoo.com
ODOO_DATABASE=demo
ODOO_USERNAME=dashboard_user
ODOO_PASSWORD=secure_password
MCP_MODE=readonly
```

## 🔓 Mode Lecture/Écriture (readwrite)

### Description
En mode lecture/écriture, toutes les opérations sont autorisées, incluant la création, modification et suppression des données.

### Configuration
```env
MCP_MODE=readwrite
```

### Outils Autorisés
- ✅ `odoo_search` - Recherche d'enregistrements
- ✅ `odoo_create` - Création d'enregistrements
- ✅ `odoo_write` - Modification d'enregistrements
- ✅ `odoo_unlink` - Suppression d'enregistrements
- ✅ `odoo_call` - Appel de toutes méthodes
- ✅ `odoo_fields_get` - Définitions de champs
- ✅ `odoo_report` - Génération de rapports

### Cas d'Usage
- **Intégrations complètes** avec systèmes tiers
- **Applications de gestion**
- **Synchronisation de données**
- **Workflows automatisés**
- **Environnements de développement**

### Exemple de Configuration
```env
# Mode complet pour intégration
ODOO_URL=https://production.odoo.com
ODOO_DATABASE=production
ODOO_USERNAME=integration_user
ODOO_PASSWORD=very_secure_password
MCP_MODE=readwrite
```

## Vérification des Permissions

### Validation des Outils
Le serveur vérifie automatiquement les permissions avant l'exécution de chaque outil :

```python
# Exemple de validation en mode readonly
if mode == 'readonly' and tool_name == 'odoo_create':
    raise PermissionError("Tool odoo_create not allowed in readonly mode")
```

### Validation des Méthodes
Pour `odoo_call`, les méthodes d'écriture sont filtrées en mode readonly :

```python
# Méthodes interdites en readonly
write_methods = {
    "create", "write", "unlink", "copy", "toggle_active",
    "action_confirm", "action_cancel", "action_done",
    "button_confirm", "button_cancel", "post", "reconcile"
}
```

## API de Vérification

### Endpoint Mode Info
```bash
GET /mcp/mode
```

Retourne :
```json
{
  "mode": "readonly",
  "allowed_permissions": ["read", "execute"],
  "forbidden_permissions": ["write", "delete"],
  "allowed_tools": ["odoo_search", "odoo_fields_get", "odoo_report"],
  "description": "Mode lecture seule - Seules les opérations de lecture et consultation sont autorisées"
}
```

### Endpoint Capabilities
```bash
POST /mcp/initialize
```

Inclut les informations de mode dans les capacités :
```json
{
  "tools": true,
  "resources": true,
  "mode": {
    "mode": "readonly",
    "allowed_tools": [...],
    "description": "..."
  }
}
```

## Exemples d'Usage

### Mode Lecture Seule - Dashboard Analytics
```python
# Configuration pour un dashboard en lecture seule
client = MCPClient("http://localhost:8000")

# Recherche de données (autorisé)
partners = await client.call_tool("odoo_search", {
    "model": "res.partner",
    "domain": [["is_company", "=", True]],
    "fields": ["name", "sales_count"],
    "limit": 100
})

# Création interdite - lèvera une PermissionError
try:
    await client.call_tool("odoo_create", {
        "model": "res.partner",
        "values": {"name": "New Partner"}
    })
except PermissionError:
    print("Création interdite en mode readonly")
```

### Mode Lecture/Écriture - Synchronisation
```python
# Configuration pour synchronisation complète
client = MCPClient("http://localhost:8000")

# Recherche (autorisé)
existing = await client.call_tool("odoo_search", {
    "model": "product.product",
    "domain": [["default_code", "=", "PROD001"]]
})

if not existing["result"]["records"]:
    # Création (autorisé en readwrite)
    new_product = await client.call_tool("odoo_create", {
        "model": "product.product",
        "values": {
            "name": "Nouveau Produit",
            "default_code": "PROD001"
        }
    })
else:
    # Mise à jour (autorisé en readwrite)
    await client.call_tool("odoo_write", {
        "model": "product.product",
        "ids": [existing["result"]["records"][0]["id"]],
        "values": {"name": "Produit Mis à Jour"}
    })
```

## Démonstration

Utilisez le script de démonstration pour tester les modes :

```bash
# Démarrer le serveur en mode readonly
MCP_MODE=readonly python start.py

# Dans un autre terminal, lancer la démo
python examples/mode_demo.py

# Changer pour le mode readwrite
MCP_MODE=readwrite python start.py

# Relancer la démonstration
python examples/mode_demo.py
```

## Sécurité et Bonnes Pratiques

### Mode Lecture Seule
- ✅ Utiliser pour les API publiques
- ✅ Idéal pour les environnements de démonstration
- ✅ Recommandé pour les tableaux de bord
- ✅ Parfait pour l'analyse de données

### Mode Lecture/Écriture
- ⚠️ Réserver aux intégrations de confiance
- ⚠️ Utiliser des comptes avec droits limités
- ⚠️ Implémenter une authentification forte
- ⚠️ Surveiller les logs d'accès

### Recommandations
1. **Principe du moindre privilège** : Commencer en readonly
2. **Utilisateurs dédiés** : Créer des comptes spécifiques par usage
3. **Surveillance** : Logger toutes les opérations d'écriture
4. **Tests** : Valider les permissions avec le script de démonstration