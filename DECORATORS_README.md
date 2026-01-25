# Décorateurs Context Manager

Ce module fournit plusieurs décorateurs pour transformer des fonctions ordinaires en **context managers** (utilisables avec l'instruction `with`).

## Table des matières

1. [Installation](#installation)
2. [Décorateurs disponibles](#décorateurs-disponibles)
3. [Exemples pratiques](#exemples-pratiques)
4. [Bonnes pratiques](#bonnes-pratiques)

## Installation

Aucune dépendance externe nécessaire. Le module utilise uniquement la bibliothèque standard Python.

```python
from decorators import as_context_manager, context_manager, simple_context, with_setup_teardown
```

## Décorateurs disponibles

### 1. `@as_context_manager` (Recommandé)

Transforme une fonction génératrice en context manager. Utilise `contextlib.contextmanager` en interne.

**Utilisation:**

```python
from decorators import as_context_manager

@as_context_manager
def database_connection(db_url):
    conn = connect(db_url)
    print("Connexion établie")
    try:
        yield conn  # La valeur yielded est disponible avec 'as'
    finally:
        print("Fermeture de la connexion")
        conn.close()

# Utilisation
with database_connection("sqlite:///test.db") as conn:
    conn.execute("SELECT * FROM users")
```

**Avantages:**
- Simple et idiomatique
- Basé sur la bibliothèque standard
- Supporte la gestion des exceptions avec try/finally

### 2. `@context_manager`

Version personnalisée qui ne dépend pas de `contextlib`. Fonctionne de manière similaire à `@as_context_manager`.

**Utilisation:**

```python
from decorators import context_manager
import time

@context_manager
def timer(name):
    start = time.time()
    print(f"Début de {name}")
    yield
    elapsed = time.time() - start
    print(f"{name} terminé en {elapsed:.2f}s")

# Utilisation
with timer("opération complexe"):
    # Code à chronométrer
    time.sleep(1)
```

### 3. `@simple_context`

Pour des fonctions simples qui ne nécessitent pas de code de nettoyage (teardown). La fonction s'exécute à l'entrée du contexte.

**Utilisation:**

```python
from decorators import simple_context
import json

@simple_context
def load_config(filename):
    with open(filename) as f:
        return json.load(f)

# Utilisation
with load_config("config.json") as config:
    print(config["database"])
```

**Cas d'usage:**
- Chargement de configuration
- Préparation de données
- Initialisation sans besoin de nettoyage

### 4. `@with_setup_teardown`

Permet de spécifier explicitement une fonction de nettoyage (teardown).

**Utilisation:**

```python
from decorators import with_setup_teardown

class Resource:
    def __init__(self, name):
        self.name = name
        print(f"Ouverture de {name}")

    def close(self):
        print(f"Fermeture de {self.name}")

def cleanup(resource, exc_type, exc_val, exc_tb):
    if resource:
        resource.close()

@with_setup_teardown(teardown_func=cleanup)
def get_resource(name):
    return Resource(name)

# Utilisation
with get_resource("database") as res:
    print(f"Utilisation de {res.name}")
```

## Exemples pratiques

### Exemple 1: Gestion de fichiers avec traçage

```python
from decorators import as_context_manager

@as_context_manager
def tracked_file(filename, mode='r'):
    print(f"📂 Ouverture de {filename}")
    file_obj = open(filename, mode)
    try:
        yield file_obj
    finally:
        print(f"🔒 Fermeture de {filename}")
        file_obj.close()

with tracked_file("data.txt", "r") as f:
    content = f.read()
```

### Exemple 2: Chronomètre de performance

```python
from decorators import as_context_manager
import time

@as_context_manager
def performance_timer(operation_name):
    start = time.time()
    print(f"⏱️  Début: {operation_name}")
    try:
        yield operation_name
    finally:
        elapsed = time.time() - start
        print(f"✅ {operation_name} terminé en {elapsed:.3f}s")

with performance_timer("Calcul complexe"):
    # Code à chronométrer
    result = sum(i**2 for i in range(1000000))
```

### Exemple 3: Gestion de transactions de base de données

```python
from decorators import as_context_manager

@as_context_manager
def database_transaction(conn):
    """Context manager pour gérer les transactions de base de données."""
    print("🔄 Début de la transaction")
    try:
        yield conn
        conn.commit()
        print("✅ Transaction validée (commit)")
    except Exception as e:
        conn.rollback()
        print(f"❌ Transaction annulée (rollback): {e}")
        raise

with database_transaction(my_connection) as conn:
    conn.execute("INSERT INTO users (name) VALUES ('Alice')")
    conn.execute("UPDATE accounts SET balance = balance - 100")
```

### Exemple 4: Changement temporaire de répertoire

```python
from decorators import as_context_manager
import os

@as_context_manager
def temporary_directory(path):
    """Change temporairement de répertoire."""
    original_dir = os.getcwd()
    os.chdir(path)
    print(f"📁 Changement vers: {path}")
    try:
        yield path
    finally:
        os.chdir(original_dir)
        print(f"📁 Retour vers: {original_dir}")

with temporary_directory("/tmp"):
    # Le répertoire courant est /tmp
    print(os.getcwd())
# Le répertoire est restauré automatiquement
```

### Exemple 5: Suppression de sortie temporaire

```python
from decorators import as_context_manager
import sys
from io import StringIO

@as_context_manager
def suppress_output():
    """Supprime temporairement stdout et stderr."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

with suppress_output():
    print("Ce message ne sera pas affiché")
    # Utile pour supprimer les logs de bibliothèques tierces
```

### Exemple 6: Context manager réutilisable avec état

```python
from decorators import as_context_manager

class Counter:
    def __init__(self):
        self.count = 0

counter = Counter()

@as_context_manager
def increment_counter():
    """Incrémente un compteur à chaque utilisation."""
    counter.count += 1
    print(f"Entrée #{counter.count}")
    try:
        yield counter.count
    finally:
        print(f"Sortie #{counter.count}")

with increment_counter() as n:
    print(f"Exécution {n}")

with increment_counter() as n:
    print(f"Exécution {n}")
# Output:
# Entrée #1
# Exécution 1
# Sortie #1
# Entrée #2
# Exécution 2
# Sortie #2
```

## Bonnes pratiques

### 1. Toujours utiliser try/finally pour le nettoyage

Pour garantir que le code de nettoyage soit exécuté même en cas d'exception:

```python
@as_context_manager
def safe_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        # Ce code sera TOUJOURS exécuté
        release_resource(resource)
```

### 2. Choisir le bon décorateur

- **`@as_context_manager`**: Pour la plupart des cas (recommandé)
- **`@simple_context`**: Quand aucun nettoyage n'est nécessaire
- **`@with_setup_teardown`**: Pour séparer clairement setup et teardown
- **`@context_manager`**: Version personnalisée si vous ne voulez pas dépendre de contextlib

### 3. Documenter le comportement

Toujours documenter ce que fait votre context manager:

```python
@as_context_manager
def my_context(param):
    """
    Context manager qui fait X.

    Args:
        param: Description du paramètre

    Yields:
        Description de ce qui est yielded

    Example:
        with my_context(value) as result:
            # Utilisation
    """
    # Implémentation
```

### 4. Nommage clair

Utilisez des noms qui indiquent clairement qu'il s'agit d'un context manager:

- ✅ `database_connection`
- ✅ `temporary_directory`
- ✅ `suppress_output`
- ❌ `db` (trop vague)
- ❌ `temp` (pas clair)

### 5. Gestion des exceptions

Décidez si vous voulez propager les exceptions ou les gérer:

```python
@as_context_manager
def error_handling_example():
    try:
        yield
    except ValueError as e:
        # Gérer l'exception spécifique
        print(f"ValueError capturée: {e}")
        # Ne pas re-raise = exception supprimée
    except Exception:
        # Autres exceptions sont propagées
        raise
    finally:
        # Nettoyage toujours exécuté
        pass
```

## Tests

Pour exécuter les tests:

```bash
python run_decorator_tests.py
```

## Exemples complets

Pour voir tous les exemples en action:

```bash
python decorators.py
```

## License

Ce code est fourni à des fins éducatives.
