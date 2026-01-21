#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes Anki à la table user_progress
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'flashcards.db'

def migrate():
    """Ajoute les colonnes du système Anki à user_progress"""

    # Backup de la base de données
    backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(DB_PATH):
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup créé: {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Vérifier quelles colonnes existent
        cursor.execute("PRAGMA table_info(user_progress)")
        columns = {col[1] for col in cursor.fetchall()}
        print(f"Colonnes existantes: {columns}")

        # Colonnes Anki à ajouter
        anki_columns = {
            'ease_factor': 'REAL DEFAULT 2.5',
            'interval': 'INTEGER DEFAULT 0',
            'due_date': 'TIMESTAMP',
            'step': 'INTEGER DEFAULT 0',
            'is_learning': 'INTEGER DEFAULT 1',
            'repetitions': 'INTEGER DEFAULT 0'
        }

        # Ajouter les colonnes manquantes
        added = 0
        for col_name, col_type in anki_columns.items():
            if col_name not in columns:
                print(f"Ajout de la colonne {col_name}...")
                cursor.execute(f'ALTER TABLE user_progress ADD COLUMN {col_name} {col_type}')
                added += 1
                print(f"✅ Colonne {col_name} ajoutée")
            else:
                print(f"⚠️  Colonne {col_name} existe déjà")

        if added > 0:
            # Initialiser les valeurs pour les enregistrements existants
            cursor.execute('''
                UPDATE user_progress
                SET ease_factor = 2.5,
                    interval = 0,
                    due_date = datetime('now'),
                    step = 0,
                    is_learning = 1,
                    repetitions = 0
                WHERE ease_factor IS NULL
            ''')
            updated = cursor.rowcount
            print(f"✅ {updated} enregistrements existants mis à jour")

        conn.commit()
        print(f"\n✅ Migration réussie! {added} colonnes ajoutées.")

        # Afficher les statistiques
        cursor.execute('SELECT COUNT(*) FROM user_progress')
        nb_progress = cursor.fetchone()[0]
        print(f"📊 Nombre total d'enregistrements de progression: {nb_progress}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
