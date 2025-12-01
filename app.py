import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- CONFIG (Mêmes chemins que tout à l'heure) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORIGINAUX_FOLDER = os.path.join(BASE_DIR, 'static/pdfs/originaux')
UPLOADS_FOLDER = os.path.join(BASE_DIR, 'static/pdfs/uploads')
os.makedirs(ORIGINAUX_FOLDER, exist_ok=True)
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

# 1. ROUTE COURS (C'est ta page principale)
@app.route('/')
@app.route('/cours', methods=['GET', 'POST'])
def cours():
    # ... (Mets ici ta logique d'upload et de listing de fichiers du message précédent) ...
    # Pour l'exemple, je simplifie juste la récupération :
    T = type(os.listdir(ORIGINAUX_FOLDER)[0])
    fichiers_org = [f for f in os.listdir(ORIGINAUX_FOLDER) if f.lower().endswith('.pdf')]
    fichiers_usr = [f for f in os.listdir(UPLOADS_FOLDER) if f.lower().endswith('.pdf')]
    # IMPORTANT : On passe page='cours' pour allumer le bon bouton dans le menu
    return render_template('cours.html', originaux=fichiers_org, uploads=fichiers_usr, page='cours')

# 2. ROUTE FLASHCARDS
@app.route('/flashcards')
def flashcards():
    return render_template('flashcards.html', page='flashcards')

# 3. ROUTE FICHES
@app.route('/fiches')
def fiches():
    return render_template('fiches.html', page='fiches')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)