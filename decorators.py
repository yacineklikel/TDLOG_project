"""
Décorateurs pour transformer des fonctions en context managers.

Ce module fournit différentes approches pour créer des context managers
à partir de fonctions ordinaires.
"""

from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, TypeVar, Generic


# Approche 1: Utiliser contextlib.contextmanager (recommandé)
# ============================================================

def as_context_manager(func: Callable) -> Callable:
    """
    Décorateur qui transforme une fonction génératrice en context manager.

    La fonction doit utiliser yield pour séparer le code d'entrée et de sortie.

    IMPORTANT: Pour garantir que le code de nettoyage (cleanup) soit exécuté
    même en cas d'exception, utilisez try/finally autour du yield:

    Exemple avec gestion des exceptions:
        @as_context_manager
        def database_connection(db_url):
            conn = connect(db_url)
            print("Connexion établie")
            try:
                yield conn
            finally:
                print("Fermeture de la connexion")
                conn.close()

        with database_connection("sqlite:///test.db") as conn:
            conn.execute("SELECT * FROM users")
            # La connexion sera fermée même si une exception se produit
    """
    return contextmanager(func)


# Approche 2: Décorateur personnalisé avec classe
# ================================================

class ContextManagerWrapper:
    """Wrapper qui transforme une fonction en context manager."""

    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.generator = None

    def __enter__(self):
        """Appelé à l'entrée du bloc with."""
        self.generator = self.func(*self.args, **self.kwargs)
        try:
            self.result = next(self.generator)
            return self.result
        except StopIteration:
            # Si la fonction ne yield rien, retourner None
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Appelé à la sortie du bloc with."""
        if self.generator:
            try:
                next(self.generator)
            except StopIteration:
                pass
        return False  # Ne pas supprimer les exceptions


def context_manager(func: Callable) -> Callable:
    """
    Décorateur qui transforme une fonction génératrice en context manager.

    Version personnalisée sans dépendre de contextlib.

    Exemple:
        @context_manager
        def timer(name):
            start = time.time()
            print(f"Début de {name}")
            yield
            elapsed = time.time() - start
            print(f"{name} terminé en {elapsed:.2f}s")

        with timer("opération"):
            # code à chronométrer
            time.sleep(1)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return ContextManagerWrapper(func, *args, **kwargs)
    return wrapper


# Approche 3: Context manager pour fonction simple (sans teardown)
# =================================================================

class SimpleFunctionContextManager:
    """Context manager qui exécute une fonction à l'entrée du contexte."""

    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def __enter__(self):
        """Exécute la fonction et retourne son résultat."""
        self.result = self.func(*self.args, **self.kwargs)
        return self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ne fait rien à la sortie."""
        return False


def simple_context(func: Callable) -> Callable:
    """
    Décorateur qui transforme une fonction simple en context manager.

    La fonction est exécutée à l'entrée du contexte et son résultat
    est disponible via le 'as'. Pas de code de nettoyage.

    Exemple:
        @simple_context
        def get_config(filename):
            with open(filename) as f:
                return json.load(f)

        with get_config("config.json") as config:
            print(config["database"])
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return SimpleFunctionContextManager(func, *args, **kwargs)
    return wrapper


# Approche 4: Context manager avec callbacks
# ===========================================

class CallbackContextManager:
    """Context manager avec callbacks explicites pour setup et teardown."""

    def __init__(self, enter_callback: Callable, exit_callback: Callable = None):
        self.enter_callback = enter_callback
        self.exit_callback = exit_callback
        self.result = None

    def __enter__(self):
        self.result = self.enter_callback()
        return self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.exit_callback:
            self.exit_callback(self.result, exc_type, exc_val, exc_tb)
        return False


def with_setup_teardown(setup_func: Callable = None, teardown_func: Callable = None):
    """
    Décorateur qui crée un context manager avec setup et teardown explicites.

    Exemple:
        def cleanup(resource, exc_type, exc_val, exc_tb):
            resource.close()

        @with_setup_teardown(teardown_func=cleanup)
        def open_file(filename):
            return open(filename, 'r')

        with open_file("data.txt") as f:
            print(f.read())
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            def enter_callback():
                return func(*args, **kwargs)
            return CallbackContextManager(enter_callback, teardown_func)
        return wrapper

    # Permettre d'utiliser le décorateur avec ou sans parenthèses
    if setup_func is not None and callable(setup_func):
        return decorator(setup_func)
    return decorator


# Exemples d'utilisation
# ======================

if __name__ == "__main__":
    import time

    # Exemple 1: Context manager avec setup/teardown
    @as_context_manager
    def timed_operation(name):
        """Chronomètre une opération."""
        start = time.time()
        print(f"⏱️  Début de '{name}'")
        yield name
        elapsed = time.time() - start
        print(f"✅ '{name}' terminé en {elapsed:.3f}s")

    print("=== Exemple 1: Timer ===")
    with timed_operation("calcul complexe") as op_name:
        print(f"Exécution de {op_name}...")
        time.sleep(0.5)

    print()

    # Exemple 2: Context manager personnalisé
    @context_manager
    def indented_print(indent_level=2):
        """Imprime avec indentation dans le contexte."""
        spaces = " " * indent_level
        print(f"{spaces}[DÉBUT DU CONTEXTE]")
        yield spaces
        print(f"{spaces}[FIN DU CONTEXTE]")

    print("=== Exemple 2: Indentation ===")
    with indented_print(4) as indent:
        print(f"{indent}Ligne 1")
        print(f"{indent}Ligne 2")

    print()

    # Exemple 3: Context manager simple
    @simple_context
    def prepare_data():
        """Prépare des données."""
        print("Préparation des données...")
        return {"users": [1, 2, 3], "items": [4, 5, 6]}

    print("=== Exemple 3: Simple context ===")
    with prepare_data() as data:
        print(f"Données disponibles: {data}")

    print()

    # Exemple 4: Context manager avec callbacks
    class Resource:
        def __init__(self, name):
            self.name = name
            self.is_open = True
            print(f"📂 Ouverture de la ressource '{name}'")

        def close(self):
            self.is_open = False
            print(f"🔒 Fermeture de la ressource '{self.name}'")

    def cleanup_resource(resource, exc_type, exc_val, exc_tb):
        if resource:
            resource.close()

    @with_setup_teardown(teardown_func=cleanup_resource)
    def get_resource(name):
        return Resource(name)

    print("=== Exemple 4: Callbacks ===")
    with get_resource("database") as res:
        print(f"Utilisation de {res.name} (ouvert: {res.is_open})")

    print()
    print("=== Tous les exemples terminés! ===")
