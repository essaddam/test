#!/bin/bash

# Script de configuration rapide du serveur MCP Odoo
echo "🚀 Configuration du serveur MCP Odoo"
echo "======================================"

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Créer l'environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt
pip install -r tests/requirements.txt

# Copier le fichier de configuration
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier de configuration..."
    cp .env.example .env
    echo "✅ Fichier .env créé - veuillez le modifier avec vos paramètres Odoo"
else
    echo "📝 Fichier .env existant trouvé"
fi

# Proposer de tester la connexion
echo ""
echo "🔍 Voulez-vous tester la connexion Odoo maintenant? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "🧪 Test de la connexion..."
    python examples/test_connection.py
fi

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "Prochaines étapes:"
echo "1. Éditez le fichier .env avec vos paramètres Odoo"
echo "2. Testez la connexion: python examples/test_connection.py"
echo "3. Démarrez le serveur: python start.py"
echo "4. Testez l'API: curl http://localhost:8000/health"
echo ""
echo "Documentation complète: cat config_guide.md"