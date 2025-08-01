# Outils et Ressources MCP Odoo dans Claude Desktop

Ce guide détaille l'utilisation des outils et ressources MCP Odoo dans Claude Desktop.

## 🛠️ Outils MCP Disponibles

### 1. `odoo_search` - Recherche d'enregistrements

**Description** : Recherche des enregistrements dans les modèles Odoo

**Exemples d'usage dans Claude Desktop :**

```
Recherche tous les clients entreprises avec leur email
```

```
Trouve les 10 dernières commandes confirmées
```

```
Liste les produits avec un stock inférieur à 10
```

**Paramètres supportés :**
- `model` : Nom du modèle Odoo (requis)
- `domain` : Filtres de recherche
- `fields` : Champs à récupérer
- `limit` : Nombre maximum d'enregistrements

### 2. `odoo_create` - Création d'enregistrements

**Description** : Crée de nouveaux enregistrements dans Odoo

**Exemples d'usage :**

```
Crée un nouveau client avec les informations suivantes :
- Nom: Tech Solutions SARL
- Email: contact@techsolutions.fr
- Téléphone: 01 23 45 67 89
```

```
Ajoute un nouveau produit "Ordinateur portable HP" avec un prix de 899€
```

**Paramètres :**
- `model` : Modèle Odoo cible
- `values` : Valeurs des champs à créer

### 3. `odoo_write` - Modification d'enregistrements

**Description** : Met à jour des enregistrements existants

**Exemples d'usage :**

```
Met à jour l'email du client "Tech Solutions" vers "nouveau@techsolutions.fr"
```

```
Change le prix du produit "Ordinateur portable HP" à 799€
```

**Paramètres :**
- `model` : Modèle Odoo
- `ids` : IDs des enregistrements à modifier
- `values` : Nouvelles valeurs

### 4. `odoo_unlink` - Suppression d'enregistrements

**Description** : Supprime des enregistrements d'Odoo

**Exemples d'usage :**

```
Supprime le client "Test Client" de la base
```

**Paramètres :**
- `model` : Modèle Odoo
- `ids` : IDs des enregistrements à supprimer

### 5. `odoo_call` - Appel de méthodes

**Description** : Exécute des méthodes spécifiques sur les modèles Odoo

**Exemples d'usage :**

```
Confirme la commande de vente numéro SO001
```

```
Valide la facture FACT/2024/001
```

**Paramètres :**
- `model` : Modèle Odoo
- `method` : Nom de la méthode
- `args` : Arguments de la méthode
- `kwargs` : Arguments nommés

### 6. `odoo_fields_get` - Définitions des champs

**Description** : Récupère les définitions des champs d'un modèle

**Exemples d'usage :**

```
Montre-moi la structure du modèle res.partner
```

```
Quels sont les champs disponibles pour les commandes de vente ?
```

### 7. `odoo_report` - Génération de rapports

**Description** : Génère des rapports depuis Odoo

**Exemples d'usage :**

```
Génère le rapport de facture pour FACT/2024/001
```

```
Crée un rapport des ventes du mois
```

## 📚 Ressources MCP Disponibles

### 1. `odoo://models` - Liste des modèles

**Description** : Liste tous les modèles Odoo disponibles

**Usage :**
```
Quels sont tous les modèles disponibles dans Odoo ?
```

### 2. `odoo://users` - Utilisateurs Odoo

**Description** : Liste des utilisateurs du système

**Usage :**
```
Montre-moi tous les utilisateurs Odoo
```

### 3. `odoo://companies` - Entreprises

**Description** : Liste des entreprises configurées

**Usage :**
```
Quelles sont les entreprises configurées dans le système ?
```

### 4. `odoo://config` - Configuration serveur

**Description** : Informations de configuration du serveur Odoo

**Usage :**
```
Montre-moi la configuration du serveur Odoo
```

## 💡 Exemples Pratiques d'Usage

### Gestion des Clients

```
"Peux-tu me chercher tous les clients qui ont une adresse email Gmail ?"

"Crée un nouveau client pour l'entreprise 'Innovation Corp' avec l'email contact@innovation-corp.com"

"Met à jour le téléphone du client 'Innovation Corp' avec le numéro 01 98 76 54 32"
```

### Gestion des Produits

```
"Liste tous les produits de la catégorie 'Informatique' avec leur prix"

"Crée un nouveau produit 'Clavier sans fil' à 45€ dans la catégorie 'Accessoires'"

"Quels sont les produits avec un stock critique (moins de 5 unités) ?"
```

### Gestion des Ventes

```
"Montre-moi les 5 dernières commandes de vente avec leur statut"

"Crée une nouvelle commande pour le client 'Tech Solutions' avec 2 ordinateurs portables"

"Confirme toutes les commandes en brouillon d'aujourd'hui"
```

### Reporting et Analyse

```
"Génère un rapport des ventes par client pour ce mois"

"Montre-moi les statistiques des ventes par produit"

"Quels sont les clients qui n'ont pas passé de commande depuis 6 mois ?"
```

## 🔒 Outils selon les Modes

### Mode Lecture Seule (`MCP_MODE=readonly`)

**Outils disponibles :**
- ✅ `odoo_search`
- ✅ `odoo_fields_get`  
- ✅ `odoo_report`
- ✅ `odoo_call` (méthodes lecture uniquement)

**Exemples autorisés :**
```
"Recherche les clients de Paris"
"Génère un rapport de facture"
"Montre la structure du modèle product.product"
```

**Exemples interdits :**
```
"Crée un nouveau client" ❌
"Met à jour ce produit" ❌
"Supprime cette commande" ❌
```

### Mode Lecture/Écriture (`MCP_MODE=readwrite`)

**Outils disponibles :**
- ✅ Tous les outils MCP

**Exemples autorisés :**
```
"Recherche et modifie les clients sans email"
"Crée 10 nouveaux produits depuis cette liste"
"Confirme et facture cette commande"
```

## 🎯 Cas d'Usage Spécialisés

### Analyse de Données

```
"Analyse les tendances de vente des 6 derniers mois et identifie les produits les plus performants"

"Compare les performances commerciales par équipe de vente"

"Identifie les clients à risque basé sur leur historique de paiement"
```

### Automatisation de Tâches

```
"Traite toutes les commandes en attente de validation"

"Met à jour les prix de tous les produits de la catégorie X avec une augmentation de 5%"

"Génère et envoie les factures pour toutes les livraisons de cette semaine"
```

### Maintenance et Administration

```
"Vérifie la cohérence des données entre les stocks et les commandes"

"Liste tous les utilisateurs inactifs depuis plus de 30 jours"

"Nettoie les données doublons dans la base clients"
```

## 🔍 Conseils d'Optimisation

### Performance

1. **Limiter les résultats** : Utilisez des filtres et limites appropriés
```
"Trouve les 50 derniers clients créés" au lieu de "Trouve tous les clients"
```

2. **Champs spécifiques** : Demandez uniquement les champs nécessaires
```
"Liste les clients avec seulement nom et email"
```

### Sécurité

1. **Vérification avant modification** : Toujours vérifier avant modifier
```
"Montre-moi d'abord les commandes que tu vas confirmer"
```

2. **Sauvegarde** : Faire des recherches avant suppression
```
"Liste les enregistrements à supprimer avant de les effacer"
```

### Efficacité

1. **Combiner les opérations** : Grouper les actions similaires
```
"Recherche tous les clients sans email et ajoute un email par défaut"
```

2. **Utiliser les ressources** : Explorer les modèles disponibles
```
"Montre-moi d'abord tous les modèles puis explique celui qui m'intéresse"
```

## 🚨 Limitations et Considérations

### Limitations Techniques

- **Timeout** : Les requêtes complexes peuvent prendre du temps
- **Mémoire** : Les grandes extractions de données peuvent être limitées
- **Connexion** : Nécessite une connexion stable au serveur Odoo

### Bonnes Pratiques

1. **Tester d'abord** : Utiliser le mode readonly pour explorer
2. **Sauvegarder** : Faire des backups avant modifications importantes
3. **Monitorer** : Surveiller les logs pour détecter les erreurs
4. **Authentifier** : Utiliser des comptes avec droits appropriés

### Sécurité

- **Pas de mots de passe** : Ne jamais partager de credentials dans Claude
- **Droits limités** : Utiliser des comptes avec permissions minimales
- **Audit** : Tracer les modifications importantes
- **Test** : Valider sur environnement de test d'abord