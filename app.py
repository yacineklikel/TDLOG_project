import os
from flask import Flask, render_template, request, redirect, url_for
import json
import random

app = Flask(__name__)

# On garde juste le dossier de base, le reste sera calculé plus tard
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- FONCTION INTELLIGENTE (Remplace tes variables globales) ---
def gestion_dossier(categorie):
    """
    categorie : peut être 'cours' ou 'fiches'
    """
    # 1. On construit les chemins SPÉCIFIQUES à la catégorie
    # Exemple : .../static/pdfs/cours/originaux
    dossier_org = os.path.join(BASE_DIR, 'static/pdfs', categorie, 'originaux')
    dossier_upl = os.path.join(BASE_DIR, 'static/pdfs', categorie, 'uploads')

    # 2. On crée les dossiers s'ils n'existent pas (Sécurité)
    os.makedirs(dossier_org, exist_ok=True)
    os.makedirs(dossier_upl, exist_ok=True)

    # 3. Gestion de l'UPLOAD (Si un fichier est envoyé)
    if request.method == 'POST':
        if 'fichier_pdf' in request.files:
            file = request.files['fichier_pdf']
            # On vérifie que c'est un PDF
            if file and file.filename.lower().endswith('.pdf'):
                # On sauvegarde dans le dossier 'uploads' de CETTE catégorie
                file.save(os.path.join(dossier_upl, file.filename))
                return True # On signale que l'upload a réussi

    # 4. Lecture des fichiers pour l'affichage
    liste_org = [f for f in os.listdir(dossier_org) if f.lower().endswith('.pdf')]
    liste_upl = [f for f in os.listdir(dossier_upl) if f.lower().endswith('.pdf')]
    
    return liste_org, liste_upl

def piocher_carte_aleatoire():
    chemin_json = os.path.join(BASE_DIR, 'flashcards.json')
    if os.path.exists(chemin_json):
        with open(chemin_json, 'r', encoding='utf-8') as f:
            cartes = json.load(f)
            if cartes:
                return random.choice(cartes)
    return None

# --- ROUTE 1 : La page complète (chargement initial) ---
@app.route('/flashcards')
def flashcards():
    carte = piocher_carte_aleatoire()
    # On rend la page entière (qui inclut le fragment)
    return render_template('flashcards.html', page='flashcards', carte=carte)

# --- ROUTE 2 : Juste la prochaine carte (appelée par HTMX) ---
@app.route('/flashcards/next')
def next_card():
    carte = piocher_carte_aleatoire()
    # ATTENTION : Ici on ne renvoie QUE le fragment, pas toute la page !
    return render_template('card_fragment.html', carte=carte)

# --- ROUTES ---

@app.route('/')
@app.route('/cours', methods=['GET', 'POST'])
def cours():
    # On appelle la fonction pour le dossier 'cours'
    resultat = gestion_dossier('cours')
    
    if resultat == True: # Si un upload a eu lieu
        return redirect(url_for('cours'))
        
    org, upl = resultat
    return render_template('cours.html', originaux=org, uploads=upl, page='cours')

@app.route('/fiches', methods=['GET', 'POST'])
def fiches():
    # On appelle la fonction pour le dossier 'fiches'
    resultat = gestion_dossier('fiches')
    
    if resultat == True:
        return redirect(url_for('fiches'))
        
    org, upl = resultat
    return render_template('fiches.html', originaux=org, uploads=upl, page='fiches')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)