# Générateur de Flashcards par IA

Une application web open-source permettant de transformer automatiquement des cours PDF en flashcards interactives grâce à l'intelligence artificielle, utilisant un algorithme de répétition espacée pour optimiser la mémorisation à long terme.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)

## À propos

Cette application révolutionnaire résout le problème de la création manuelle et fastidieuse de fiches de révision. L'application extrait le texte de vos documents PDF et utilise des modèles de langage (LLM) pour générer des questions pertinentes et pédagogiques. Elle intègre ensuite ces cartes dans un système de révision intelligent basé sur l'algorithme **SM-2** (similaire à Anki).

## Fonctionnalités Clés

* **Génération IA Multi-Moteurs :** Support complet et configurable pour **OpenAI** (GPT-4o), **Google** (Gemini) et **Anthropic** (Claude). Vous choisissez votre fournisseur.
* **Parsing PDF Avancé :** Extraction automatique de texte depuis des fichiers PDF uploadés (cours complets ou fiches).
* **Répétition Espacée (SRS) :** Implémentation fidèle de l'algorithme Anki pour gérer les intervalles de révision selon votre mémoire (Recommencer, Difficile, Bon, Facile).
* **Statistiques et Gamification :** Suivi de l'activité quotidienne (heatmap type GitHub), calcul des séries (streaks) et classement des utilisateurs (Leaderboard).
* **Interface Réactive :** Navigation fluide sans rechargement de page grâce à **HTMX** et **Alpine.js**.
* **Support Mathématique :** Rendu parfait des formules LaTeX via **MathJax**.
* **Confidentialité & Sécurité :** Base de données **SQLite** locale ; vos fichiers et vos clés API restent sous votre contrôle. Mots de passe hashés.

## Stack Technique

* **Backend :** Python, Flask, Werkzeug.
* **Base de Données :** SQLite (aucune installation serveur requise).
* **Frontend :** Bootstrap 5 (UI), HTMX (Interactivité), Alpine.js (État), MathJax (Maths).
* **IA & Traitement :** PyPDF2, SDKs officiels (OpenAI, Anthropic, Google Generative AI).

## Installation et Démarrage

Suivez ces étapes pour installer le projet localement en moins de 3 minutes.

### 1. Prérequis
* Python 3.8 ou supérieur.
* Git.

### 2. Clonage et Environnement
Clonez le dépôt et créez un environnement virtuel isolé :

```bash
git clone [https://github.com/yacineklikel/TDLOG_project.git](https://github.com/yacineklikel/TDLOG_project.git)
cd TDLOG_project

# Création de l'environnement virtuel
python3 -m venv venv

# Activation (Mac/Linux)
source venv/bin/activate

# Activation (Windows)
# venv\Scripts\activate
```

### 3. Dépendances
Installez les bibliothèques requises :

```bash
pip install -r requirements.txt
```

### 4. Configuration
Créez votre fichier de configuration personnel à partir du modèle :

```bash
cp config.example.py config.py
```

Ouvrez le fichier `config.py` créé et renseignez au moins une clé API (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY` ou `GOOGLE_API_KEY`) et définissez la variable `API_PROVIDER` correspondante.

### 5. Base de Données
Initialisez la base de données locale (cette étape crée le fichier `flashcards.db` et les tables nécessaires) :

```bash
python setup_complete_database.py
```

### 6. Lancement
Lancez le serveur de développement :

```bash
python app.py
```

L'application est maintenant accessible à l'adresse : **http://127.0.0.1:5001**


## ⚙️ Configuration Avancée

Le fichier `config.py` permet de contrôler le comportement de l'application :

* **`API_PROVIDER`** : Définit quel moteur IA utiliser. Valeurs possibles : `'openai'`, `'claude'`, `'gemini'`.
* **`SECRET_KEY`** : Clé utilisée pour sécuriser les sessions Flask (à changer impérativement en production).
* **`MODELS`** : Vous permet de changer les versions spécifiques des modèles (ex: passer de `gpt-4o` à `gpt-3.5-turbo`).

## Guide d'Utilisation

1.  **Inscription :** Créez un compte local via la page "S'inscrire". Une question de sécurité est requise pour la récupération de mot de passe.
2.  **Import de Cours :** Allez dans l'onglet **Cours** et uploadez vos fichiers PDF (cours magistraux, TD, résumés).
3.  **Génération :** Cliquez sur le bouton **"⚡ Générer Flashcards"** à côté d'un PDF. Choisissez le nom du deck et le nombre de cartes souhaitées (ex: 10 ou 20).
4.  **Révision :** Allez dans le menu **Flashcards**, sélectionnez un deck et lancez la session.
    * Cliquez sur la carte pour voir la réponse.
    * Votez selon votre facilité (Recommencer, Difficile, Bon, Facile) pour ajuster le prochain intervalle.
5.  **Suivi :** Consultez vos progrès (nombre de cartes apprises, heatmap) et votre position dans le classement via le menu **Statistiques**.

## Structure du Projet

Vue d'ensemble des fichiers principaux pour vous aider à vous y repérer :

```text
TDLOG_project/
├── app.py                       # Point d'entrée de l'application (Routes Flask & Contrôleurs)
├── database.py                  # Gestion de la base de données SQLite (CRUD)
├── anki_algorithm.py            # Algorithme de répétition espacée (Logique SM-2)
├── config.example.py            # Modèle de configuration (Clés API, Secret Key)
├── requirements.txt             # Liste des dépendances Python
├── setup_complete_database.py   # Script d'initialisation des tables de la BDD
├── create_test_account.py       # Utilitaire pour créer un utilisateur de test
├── run_tests.py                 # Script pour lancer la suite de tests
├── templates/                   # Fichiers HTML (Templates Jinja2)
│   ├── base.html                # Layout principal (Navbar, imports JS/CSS)
│   ├── cours.html               # Page d'upload et gestion des PDF
│   ├── flashcards.html          # Interface de jeu (Révision)
│   ├── flashcards_menu.html     # Sélection des decks et arborescence
│   ├── card_fragment.html       # Composant carte pour le remplacement dynamique (HTMX)
│   ├── fiches.html              # Page de consultation des fiches résumé
│   ├── statistiques.html        # Dashboard, Heatmap et graphiques
│   ├── leaderboard.html         # Classement des utilisateurs
│   ├── parametres.html          # Réglages (Prompt IA, Thème)
│   └── auth/                    # Pages d'authentification (login, register, etc.)
└── static/                      # Fichiers statiques
    ├── pdfs/                    # Dossier de stockage des cours PDF uploadés
    └── fiches/                  # Dossier de stockage des fiches Markdown générées
```