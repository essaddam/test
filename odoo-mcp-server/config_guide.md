# Guide de Configuration Odoo MCP Server

## Configuration des paramètres Odoo

### 1. URL du serveur Odoo
```env
ODOO_URL=http://localhost:8069        # Serveur local
ODOO_URL=https://monodoo.com          # Serveur distant avec SSL
ODOO_URL=http://192.168.1.100:8069    # Serveur réseau local
```

### 2. Base de données
```env
ODOO_DATABASE=production    # Base de production
ODOO_DATABASE=test         # Base de test
ODOO_DATABASE=demo         # Base de démonstration
```

### 3. Authentification utilisateur

#### Option 1: Utilisateur admin (recommandé pour les tests)
```env
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password
```

#### Option 2: Utilisateur technique (recommandé pour la production)
```env
ODOO_USERNAME=api_user
ODOO_PASSWORD=secure_api_password
```

#### Option 3: Utilisateur avec droits limités
```env
ODOO_USERNAME=mcp_integration
ODOO_PASSWORD=integration_password
```

## Création d'un utilisateur API dans Odoo

### 1. Via l'interface Odoo
1. Aller dans **Paramètres > Utilisateurs et Sociétés > Utilisateurs**
2. Cliquer sur **Créer**
3. Remplir les informations :
   - **Nom** : API MCP User
   - **Identifiant** : api_mcp_user
   - **Mot de passe** : [mot de passe sécurisé]
   - **Email** : api@monentreprise.com

### 2. Droits d'accès recommandés
```
Groupe d'accès : Utilisateur interne
Applications :
  - Ventes : Utilisateur
  - CRM : Utilisateur  
  - Comptabilité : Utilisateur de facturation
  - Achats : Utilisateur
  - Inventaire : Utilisateur
  - Paramètres : Accès aux paramètres (si nécessaire)
```

### 3. Via XML-RPC (programmation)
```python
import xmlrpc.client

# Connexion admin pour créer l'utilisateur
url = 'http://localhost:8069'
db = 'votre_base'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Créer l'utilisateur API
user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [{
    'name': 'API MCP User',
    'login': 'api_mcp_user',
    'password': 'votre_mot_de_passe_securise',
    'email': 'api@votre-entreprise.com',
    'groups_id': [(6, 0, [1])]  # Groupe utilisateur interne
}])
```

## Configuration de sécurité

### 1. Paramètres de sécurité dans .env
```env
# Clé API pour authentification (optionnel)
API_KEY=votre-cle-api-secrete

# Limitation d'accès par IP
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8

# Limitation de taux
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 2. Configuration HTTPS pour production
```env
ODOO_URL=https://votre-odoo-securise.com
```

## Exemples de configuration par environnement

### Développement local
```env
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
DEBUG=true
LOG_LEVEL=DEBUG
```

### Test/Staging
```env
ODOO_URL=https://test-odoo.monentreprise.com
ODOO_DATABASE=test_db
ODOO_USERNAME=test_api_user
ODOO_PASSWORD=${TEST_API_PASSWORD}
DEBUG=false
LOG_LEVEL=INFO
```

### Production
```env
ODOO_URL=https://odoo.monentreprise.com
ODOO_DATABASE=production
ODOO_USERNAME=${PROD_API_USER}
ODOO_PASSWORD=${PROD_API_PASSWORD}
DEBUG=false
LOG_LEVEL=WARNING
API_KEY=${PROD_API_KEY}
ALLOWED_IPS=10.0.0.0/8
```

## Vérification de la configuration

### 1. Test de connexion
```bash
# Utiliser le script de test
python examples/test_connection.py
```

### 2. Via l'API de santé
```bash
curl http://localhost:8000/health
```

### 3. Test des modèles Odoo
```bash
curl -X GET http://localhost:8000/odoo/models
```

## Dépannage des problèmes de connexion

### Erreur d'authentification
- Vérifier les identifiants dans `.env`
- S'assurer que l'utilisateur existe dans Odoo
- Vérifier que la base de données est correcte

### Erreur de réseau
- Vérifier l'URL du serveur Odoo
- Tester la connectivité réseau
- Vérifier les pare-feu

### Erreur de droits
- S'assurer que l'utilisateur a les droits nécessaires
- Vérifier les groupes d'accès dans Odoo

## Variables d'environnement complètes

```env
# === ODOO CONFIGURATION ===
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# === SERVER CONFIGURATION ===
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# === MCP CONFIGURATION ===
MCP_SERVER_NAME=odoo-mcp-server
MCP_SERVER_VERSION=1.0.0

# === LOGGING ===
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# === SECURITY ===
API_KEY=
ALLOWED_IPS=
CORS_ORIGINS=*

# === PERFORMANCE ===
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
STREAM_CHUNK_SIZE=10
STREAM_DELAY=0.1
```