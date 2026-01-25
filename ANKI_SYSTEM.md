# Système de Répétition Espacée Anki (SM-2)

## Vue d'ensemble

L'application utilise maintenant l'algorithme **SM-2 (SuperMemo 2)**, le même algorithme utilisé par Anki, pour optimiser la mémorisation à long terme des flashcards.

## Qu'est-ce que SM-2 ?

SM-2 est un algorithme de répétition espacée qui :
- Adapte automatiquement les intervalles de révision selon votre performance
- Optimise le temps d'étude en espaçant les révisions
- Améliore la rétention à long terme

### Principe

Au lieu d'un simple score de 0 à 5, Anki utilise :
- **Ease Factor** : Facteur de facilité (commence à 2.5)
- **Interval** : Intervalle jusqu'à la prochaine révision (en jours)
- **Steps** : Étapes d'apprentissage (1min, 10min pour les nouvelles cartes)
- **Due Date** : Date de la prochaine révision

## Les 4 boutons de réponse

### **Recommencer** (Again - Rating 0)
- **Nouvelle carte** : Redémarre à l'étape 1 (1 minute)
- **Carte en révision** : Retour en apprentissage, réduction du ease factor
- **Utiliser quand** : Vous ne vous souvenez pas du tout

### **Difficile** (Hard - Rating 1)
- **Nouvelle carte** : Répète l'étape actuelle
- **Carte en révision** : Intervalle légèrement réduit (×1.2), ease -0.15
- **Utiliser quand** : Vous vous souvenez mais avec difficulté

### **Bon** (Good - Rating 2)
- **Nouvelle carte** : Passe à l'étape suivante
- **Carte en révision** : Intervalle normal selon l'algorithme SM-2
- **Utiliser quand** : Vous vous souvenez correctement
- **C'est le bouton par défaut** pour une bonne maîtrise

### **Facile** (Easy - Rating 3)
- **Nouvelle carte** : Graduation immédiate (4 jours)
- **Carte en révision** : Intervalle augmenté (×ease×1.3), ease +0.15
- **Utiliser quand** : Vous trouvez la carte très facile

## Phases d'apprentissage

### 1. Phase d'apprentissage (Learning)

**Nouvelles cartes ou cartes oubliées**

Étapes par défaut : **1 minute** → **10 minutes** → **1 jour**

- Première fois : carte présentée
- **Again** (0) : Retour à 1 min
- **Hard** (1) : Reste à l'étape actuelle
- **Good** (2) : Passe à l'étape suivante
- **Easy** (3) : Graduation immédiate à 4 jours

### 2. Phase de révision (Review)

**Cartes maîtrisées**

Intervalles suivent l'algorithme SM-2 :

| Répétition | Intervalle (Good) |
|------------|-------------------|
| 1ère       | 1 jour            |
| 2ème       | 6 jours           |
| 3ème       | 15 jours          |
| 4ème       | 37 jours          |
| 5ème       | 93 jours          |
| 6ème       | 232 jours         |
| ...        | ...               |

La formule : `nouveau_intervalle = intervalle_actuel × ease_factor`

## Paramètres de configuration

```python
DEFAULT_CONFIG = {
    'learning_steps': [1, 10],  # Minutes: 1min, 10min
    'graduating_interval': 1,    # 1 jour pour passer en révision
    'easy_interval': 4,          # 4 jours si "Facile" dès le début
    'starting_ease': 2.5,        # Facteur de facilité initial
    'easy_bonus': 1.3,           # Bonus pour réponse "Facile"
    'interval_modifier': 1.0,    # Modificateur d'intervalle global
    'max_interval': 36500,       # Intervalle max (100 ans)
    'min_ease': 1.3,             # Ease minimum
}
```

## Exemples de parcours

### Carte facile (maîtrise rapide)

1. Nouvelle carte → **Good** (2) → Due: 10 min
2. 10 min plus tard → **Good** (2) → Due: 1 jour
3. 1 jour plus tard → **Good** (2) → Due: 6 jours
4. 6 jours plus tard → **Good** (2) → Due: 15 jours
5. 15 jours plus tard → **Easy** (3) → Due: 49 jours

Résultat : Ease = 2.65, intervalle long

### Carte difficile (apprentissage lent)

1. Nouvelle carte → **Hard** (1) → Due: 1 min
2. 1 min plus tard → **Good** (2) → Due: 10 min
3. 10 min plus tard → **Good** (2) → Due: 1 jour
4. 1 jour plus tard → **Again** (0) → Retour en apprentissage
5. 1 min plus tard → **Good** (2) → Due: 10 min
6. 10 min plus tard → **Good** (2) → Due: 1 jour
7. 1 jour plus tard → **Hard** (1) → Due: 1 jour
8. 1 jour plus tard → **Good** (2) → Due: 6 jours

Résultat : Ease réduit, apprentissage renforcé

## Migration depuis l'ancien système

Les anciens scores (0-5) ont été convertis :

| Ancien score | Nouveau statut             | Intervalle initial |
|--------------|----------------------------|--------------------|
| 0-1          | En apprentissage           | 1 minute           |
| 2            | Révision débutante         | 1 jour             |
| 3            | Révision intermédiaire     | 3 jours            |
| 4            | Révision avancée           | 7 jours            |
| 5            | Révision maîtrisée         | 30 jours           |

## Architecture

### Fichiers créés/modifiés

1. **`anki_algorithm.py`** (nouveau)
   - Implémentation de l'algorithme SM-2
   - Classe `AnkiCard` pour représenter l'état d'une carte
   - Fonction `calculate_next_review()` pour calculer le prochain intervalle
   - Fonctions utilitaires (statistiques, filtrage)

2. **`migrate_to_anki.py`** (nouveau)
   - Script de migration de l'ancien système vers Anki
   - Sauvegarde automatique de la base avant migration
   - Conversion des scores en paramètres Anki

3. **`database.py`** (modifié)
   - `update_progress()` : Nouveaux paramètres Anki
   - `get_all_user_progress()` : Tri par due_date

4. **`app.py`** (modifié)
   - `piocher_carte()` : Sélection basée sur due_date
   - `vote_card()` : Utilise l'algorithme SM-2

5. **`templates/card_fragment.html`** (modifié)
   - 4 boutons au lieu de 2
   - Design adaptatif mobile/desktop

### Schéma de base de données

Table `user_progress` (nouveaux champs) :

```sql
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    flashcard_id INTEGER NOT NULL,
    ease_factor REAL DEFAULT 2.5,
    interval INTEGER DEFAULT 0,
    due_date TEXT,
    step INTEGER DEFAULT 0,
    is_learning INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    last_reviewed TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (flashcard_id) REFERENCES flashcards(id),
    UNIQUE(user_id, flashcard_id)
)
```

## Conseils d'utilisation

### Pour les utilisateurs

1. **Soyez honnête** avec vos réponses
   - Utilisez "Again" si vous ne vous souvenez vraiment pas
   - "Good" est le choix par défaut pour une bonne réponse
   - "Easy" seulement si c'est vraiment très facile

2. **Faites confiance à l'algorithme**
   - Les intervalles peuvent sembler longs, c'est normal
   - L'algorithme optimise votre temps d'étude
   - La répétition espacée est prouvée scientifiquement

3. **Révisez régulièrement**
   - Vérifiez les cartes "dues" chaque jour
   - Les nouvelles cartes apparaissent en premier
   - Les cartes en retard sont prioritaires

### Pour les développeurs

1. **Tester l'algorithme**
   ```bash
   python anki_algorithm.py
   ```

2. **Migrer une base existante**
   ```bash
   python migrate_to_anki.py
   ```

3. **Personnaliser la configuration**
   - Modifier `DEFAULT_CONFIG` dans `anki_algorithm.py`
   - Adapter les `learning_steps` selon vos besoins
   - Ajuster le `starting_ease` pour difficulté globale

## Références

- [Supermemo Algorithm SM-2](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)
- [Anki Manual - Spaced Repetition](https://docs.ankiweb.net/studying.html)
- [The Science of Spaced Repetition](https://www.gwern.net/Spaced-repetition)

## Statistiques et métriques

L'algorithme permet de calculer :
- Nombre de cartes nouvelles
- Nombre de cartes en apprentissage
- Nombre de cartes en révision
- Nombre de cartes dues aujourd'hui

Exemple :
```python
from anki_algorithm import get_statistics

stats = get_statistics(cards_with_progress)
print(f"Nouvelles: {stats['new']}")
print(f"En apprentissage: {stats['learning']}")
print(f"En révision: {stats['review']}")
print(f"À réviser aujourd'hui: {stats['due_today']}")
```

## Limites et améliorations futures

### Limites actuelles

- Pas de limite sur le nombre de nouvelles cartes par jour
- Pas de limite sur le nombre de révisions par jour
- Pas de prise en compte des "lapses" (nombre de fois où la carte est oubliée)
- Pas de statistiques détaillées visibles par l'utilisateur

### Améliorations possibles

1. **Paramètres utilisateur** : Permettre à chaque utilisateur de configurer ses paramètres
2. **Statistiques** : Afficher des graphiques de progression
3. **Limites quotidiennes** : Limiter nouvelles cartes et révisions par jour
4. **Tags et filtres** : Permettre de filtrer les cartes par tags
5. **Mode étude** : Différents modes (nouveau, révision, tout)
6. **Prédictions** : Estimer le temps nécessaire pour maîtriser un deck

## Notes techniques

### Performance

L'algorithme est très efficace :
- O(1) pour calculer le prochain intervalle
- O(n) pour filtrer les cartes dues (n = nombre de cartes)
- Utilise des index sur `due_date` pour requêtes rapides

### Thread-safety

L'implémentation actuelle n'est pas thread-safe. Pour une utilisation multi-utilisateurs simultanés :
- Utiliser des transactions SQL
- Ajouter des locks sur les updates
- Considérer Redis pour le cache

### Tests

Les tests unitaires doivent être adaptés pour le nouveau système.
Voir `test_database.py` - section à mettre à jour avec les nouveaux paramètres.
