import google.generativeai as genai
from pypdf import PdfReader
import os
import json
import csv
import random
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Configurez votre clé API ici
genai.configure(api_key="VOTRE_CLE_API_GEMINI_ICI")
app.secret_key = 'CLE_SECRETE_A_CHANGER'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# On définit le dossier où chercher les CSV (theoj.csv, etc.)
FLASHCARDS_DIR = os.path.join(BASE_DIR, 'flashcards_data')
os.makedirs(FLASHCARDS_DIR, exist_ok=True)

# --- SECURITE ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- GESTION UTILISATEURS ---
def charger_users():
    path = os.path.join(BASE_DIR, 'users.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def sauver_users(users):
    path = os.path.join(BASE_DIR, 'users.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

# --- GESTION FLASHCARDS (MULTI-FICHIERS) ---
def lister_decks():
    if not os.path.exists(FLASHCARDS_DIR):
        return []
    files = [f for f in os.listdir(FLASHCARDS_DIR) if f.lower().endswith('.csv')]
    return files

def charger_deck_csv(deck_filename):
    path = os.path.join(FLASHCARDS_DIR, deck_filename)
    cartes = []
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8', newline='') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = csv.reader(csvfile, dialect)
                for row in reader:
                    if len(row) >= 2:
                        cartes.append({'question': row[0], 'reponse': row[1]})
        except Exception as e:
            print(f"Erreur de lecture {deck_filename}: {e}")
    return cartes

def charger_progression(deck_name):
    user = session['user']
    path_progress = os.path.join(BASE_DIR, 'user_progress.json')
    global_progress = {}
    if os.path.exists(path_progress):
        with open(path_progress, 'r', encoding='utf-8') as f:
            global_progress = json.load(f)
    
    user_data = global_progress.get(user, {})
    deck_progress = user_data.get(deck_name, {})
    return deck_progress, global_progress

def sauvegarder_score_csv(deck_name, question, est_connu):
    user = session['user']
    deck_progress, global_progress = charger_progression(deck_name)
    score_actuel = deck_progress.get(question, 0)
    
    if est_connu:
        nouveau_score = min(score_actuel + 1, 5)
    else:
        nouveau_score = 0
        
    deck_progress[question] = nouveau_score
    if user not in global_progress:
        global_progress[user] = {}
    global_progress[user][deck_name] = deck_progress
    
    path_progress = os.path.join(BASE_DIR, 'user_progress.json')
    with open(path_progress, 'w', encoding='utf-8') as f:
        json.dump(global_progress, f, ensure_ascii=False, indent=4)

def piocher_carte_csv(deck_name):
    cartes = charger_deck_csv(deck_name)
    if not cartes: return None
    deck_progress, _ = charger_progression(deck_name)
    poids = []
    for c in cartes:
        score = deck_progress.get(c['question'], 0)
        poids.append(10 / (score + 1))
    return random.choices(cartes, weights=poids, k=1)[0]

# --- GÉNÉRATION IA (GEMINI) ---
def generer_flashcards_gemini(pdf_path, nom_deck):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Erreur lecture PDF: {e}")
        return False

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyse le texte de cours ci-dessous et génère les flashcards pertinentes (Question;Réponse).
    Format: CSV avec point-virgule (;). Pas d'entêtes.
    Texte : {text[:10000]} 
    """

    try:
        response = model.generate_content(prompt)
        contenu_csv = response.text.replace("```csv", "").replace("```", "").strip()
        
        path = os.path.join(FLASHCARDS_DIR, f"{nom_deck}.csv")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(contenu_csv)
        return True
    except Exception as e:
        print(f"Erreur API Gemini: {e}")
        return False

# --- ROUTES ---

@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('login' if 'user' not in session else 'cours'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Gestion UNIFIÉE Login + Register pour correspondre à votre HTML
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        action = request.form.get('action') # 'login' ou 'register'
        
        users = charger_users()

        # CAS 1 : Inscription
        if action == 'register':
            if username in users:
                flash("Utilisateur déjà existant !")
            elif len(password) < 4:
                flash("Mot de passe trop court !")
            else:
                users[username] = generate_password_hash(password)
                sauver_users(users)
                session['user'] = username
                return redirect(url_for('cours'))

        # CAS 2 : Connexion
        elif action == 'login':
            if username in users and check_password_hash(users[username], password):
                session['user'] = username
                return redirect(url_for('cours'))
            else:
                flash("Identifiants incorrects")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        users = charger_users()
        
        if username in users:
            flash("Utilisateur déjà existant !")
        elif len(password) < 4:
            flash("Mot de passe trop court (minimum 4 caractères) !")
        elif password != password_confirm:
            flash("Les mots de passe ne correspondent pas !")
        else:
            users[username] = generate_password_hash(password)
            sauver_users(users)
            session['user'] = username
            return redirect(url_for('cours'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# --- ROUTES PDFS ---
def gestion_dossier(categorie):
    dossier_org = os.path.join(BASE_DIR, 'static/pdfs', categorie, 'originaux')
    dossier_upl = os.path.join(BASE_DIR, 'static/pdfs', categorie, 'uploads')
    os.makedirs(dossier_org, exist_ok=True)
    os.makedirs(dossier_upl, exist_ok=True)
    if request.method == 'POST' and 'fichier_pdf' in request.files:
        f = request.files['fichier_pdf']
        if f.filename.endswith('.pdf'): f.save(os.path.join(dossier_upl, f.filename))
        return True
    return [f for f in os.listdir(dossier_org) if f.endswith('.pdf')], [f for f in os.listdir(dossier_upl) if f.endswith('.pdf')]

@app.route('/cours', methods=['GET', 'POST'])
@login_required
def cours():
    res = gestion_dossier('cours')
    if res == True: return redirect(url_for('cours'))
    return render_template('cours.html', originaux=res[0], uploads=res[1], page='cours')

@app.route('/fiches', methods=['GET', 'POST'])
@login_required
def fiches():
    res = gestion_dossier('fiches')
    if res == True: return redirect(url_for('fiches'))
    return render_template('fiches.html', originaux=res[0], uploads=res[1], page='fiches')

# --- ROUTES FLASHCARDS ---

@app.route('/generer_deck', methods=['POST'])
@login_required
def generer_deck():
    # Cette route gère uniquement la génération
    if 'pdf_file' not in request.files:
        flash("Aucun fichier sélectionné")
        return redirect(url_for('flashcards_menu'))
        
    file = request.files['pdf_file']
    if file.filename == '':
        flash("Nom invalide")
        return redirect(url_for('flashcards_menu'))

    if file and file.filename.endswith('.pdf'):
        nom_deck = os.path.splitext(file.filename)[0]
        temp_path = os.path.join(BASE_DIR, "temp_cours.pdf")
        file.save(temp_path)
        
        succes = generer_flashcards_gemini(temp_path, nom_deck)
        if os.path.exists(temp_path): os.remove(temp_path)
            
        if succes: flash(f"Deck '{nom_deck}' créé !")
        else: flash("Erreur IA")
    return redirect(url_for('flashcards_menu'))

@app.route('/flashcards')
@login_required
def flashcards_menu():
    # Cette route affiche le menu
    decks = lister_decks()
    return render_template('flashcards_menu.html', decks=decks, page='flashcards')

@app.route('/flashcards/play')
@login_required
def flashcards_play():
    deck_name = request.args.get('deck')
    if not deck_name: return redirect(url_for('flashcards_menu'))
    carte = piocher_carte_csv(deck_name)
    return render_template('flashcards.html', page='flashcards', carte=carte, current_deck=deck_name)

@app.route('/flashcards/vote')
@login_required
def vote_card():
    deck_name = request.args.get('deck')
    question = request.args.get('question')
    resultat = request.args.get('result')
    sauvegarder_score_csv(deck_name, question, (resultat == 'ok'))
    nouvelle_carte = piocher_carte_csv(deck_name)
    return render_template('card_fragment.html', carte=nouvelle_carte, current_deck=deck_name)

@app.route('/flashcards/delete/<deck_name>', methods=['POST'])
@login_required
def delete_deck(deck_name):
    try:
        # Validate deck_name to prevent path traversal attacks
        if not deck_name or '/' in deck_name or '\\' in deck_name or '..' in deck_name:
            flash("Nom de deck invalide")
            return redirect(url_for('flashcards_menu'))
        
        # Ensure deck_name ends with .csv
        if not deck_name.endswith('.csv'):
            flash("Nom de deck invalide")
            return redirect(url_for('flashcards_menu'))
        
        deck_path = os.path.join(FLASHCARDS_DIR, deck_name)
        
        # Verify the path is within FLASHCARDS_DIR (additional safety check)
        if not os.path.abspath(deck_path).startswith(os.path.abspath(FLASHCARDS_DIR)):
            flash("Accès non autorisé")
            return redirect(url_for('flashcards_menu'))
        
        if os.path.exists(deck_path):
            os.remove(deck_path)
            flash(f"Le deck '{deck_name}' a été supprimé avec succès!")
        else:
            flash("Deck introuvable")
    except Exception as e:
        flash(f"Erreur lors de la suppression: {e}")
    return redirect(url_for('flashcards_menu'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)