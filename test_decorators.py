"""
Tests unitaires pour les décorateurs de context managers.
"""

from decorators import (
    as_context_manager,
    context_manager,
    simple_context,
    with_setup_teardown
)


def test_as_context_manager_basic():
    """Test du décorateur as_context_manager avec un cas simple."""
    executed = []

    @as_context_manager
    def my_context():
        executed.append("enter")
        yield "value"
        executed.append("exit")

    with my_context() as value:
        executed.append("body")
        assert value == "value"

    assert executed == ["enter", "body", "exit"]


def test_as_context_manager_with_arguments():
    """Test avec des arguments passés à la fonction."""
    results = []

    @as_context_manager
    def accumulator(initial):
        results.append(f"start:{initial}")
        yield initial * 2
        results.append("end")

    with accumulator(5) as value:
        assert value == 10
        results.append("middle")

    assert results == ["start:5", "middle", "end"]


def test_as_context_manager_exception_handling():
    """Test de la gestion des exceptions dans le context manager."""
    cleanup_called = []

    @as_context_manager
    def error_context():
        cleanup_called.append("setup")
        try:
            yield
        finally:
            cleanup_called.append("cleanup")

    try:
        with error_context():
            cleanup_called.append("body")
            raise ValueError("test error")
    except ValueError:
        pass

    # Le cleanup doit être appelé même en cas d'erreur
    assert cleanup_called == ["setup", "body", "cleanup"]


def test_context_manager_custom():
    """Test du décorateur context_manager personnalisé."""
    log = []

    @context_manager
    def custom_ctx(name):
        log.append(f"open:{name}")
        yield name.upper()
        log.append(f"close:{name}")

    with custom_ctx("test") as value:
        log.append(f"use:{value}")
        assert value == "TEST"

    assert log == ["open:test", "use:TEST", "close:test"]


def test_simple_context():
    """Test du décorateur simple_context."""
    call_count = [0]

    @simple_context
    def get_value():
        call_count[0] += 1
        return 42

    with get_value() as value:
        assert value == 42

    # La fonction ne doit être appelée qu'une fois (à l'entrée)
    assert call_count[0] == 1


def test_simple_context_with_args():
    """Test simple_context avec des arguments."""

    @simple_context
    def compute(x, y):
        return x + y

    with compute(10, 20) as result:
        assert result == 30


def test_with_setup_teardown():
    """Test du décorateur with_setup_teardown."""
    state = {"resource": None, "cleaned": False}

    def cleanup(resource, exc_type, exc_val, exc_tb):
        state["cleaned"] = True
        if resource:
            resource["closed"] = True

    @with_setup_teardown(teardown_func=cleanup)
    def get_resource():
        resource = {"name": "test", "closed": False}
        state["resource"] = resource
        return resource

    with get_resource() as res:
        assert res["name"] == "test"
        assert not res["closed"]

    assert state["cleaned"]
    assert state["resource"]["closed"]


def test_nested_context_managers():
    """Test de l'imbrication de context managers."""
    order = []

    @as_context_manager
    def outer():
        order.append("outer_enter")
        yield "outer"
        order.append("outer_exit")

    @as_context_manager
    def inner():
        order.append("inner_enter")
        yield "inner"
        order.append("inner_exit")

    with outer() as o:
        order.append(f"using_{o}")
        with inner() as i:
            order.append(f"using_{i}")

    expected = [
        "outer_enter",
        "using_outer",
        "inner_enter",
        "using_inner",
        "inner_exit",
        "outer_exit"
    ]
    assert order == expected


def test_context_manager_returns_none():
    """Test quand le context manager ne yield aucune valeur."""

    @as_context_manager
    def no_yield_value():
        print("setup")
        yield
        print("teardown")

    with no_yield_value() as value:
        assert value is None


def test_reusable_context_manager():
    """Test qu'un context manager peut être utilisé plusieurs fois."""
    counter = [0]

    @as_context_manager
    def increment_context():
        counter[0] += 1
        yield counter[0]

    with increment_context() as val1:
        assert val1 == 1

    with increment_context() as val2:
        assert val2 == 2

    with increment_context() as val3:
        assert val3 == 3


# Exemples pratiques
# ==================

def test_database_connection_example():
    """Exemple pratique: simulation d'une connexion à une base de données."""
    connections = []

    class FakeConnection:
        def __init__(self, url):
            self.url = url
            self.connected = True
            connections.append(("open", url))

        def close(self):
            self.connected = False
            connections.append(("close", self.url))

        def execute(self, query):
            return f"Executed: {query}"

    @as_context_manager
    def database_connection(db_url):
        conn = FakeConnection(db_url)
        yield conn
        conn.close()

    with database_connection("sqlite:///test.db") as conn:
        result = conn.execute("SELECT * FROM users")
        assert result == "Executed: SELECT * FROM users"
        assert conn.connected

    assert not conn.connected
    assert connections == [
        ("open", "sqlite:///test.db"),
        ("close", "sqlite:///test.db")
    ]


def test_file_operations_example():
    """Exemple pratique: gestion de fichiers."""
    operations = []

    @as_context_manager
    def tracked_file(filename, mode):
        operations.append(f"opening {filename}")
        # Simulation: on ne crée pas vraiment de fichier
        file_obj = {"name": filename, "mode": mode, "closed": False}
        yield file_obj
        operations.append(f"closing {filename}")
        file_obj["closed"] = True

    with tracked_file("data.txt", "r") as f:
        operations.append(f"reading {f['name']}")
        assert not f["closed"]

    assert f["closed"]
    assert operations == [
        "opening data.txt",
        "reading data.txt",
        "closing data.txt"
    ]


def test_timer_example():
    """Exemple pratique: chronométrage."""
    import time

    @as_context_manager
    def timer(name):
        start = time.time()
        yield name
        elapsed = time.time() - start
        assert elapsed >= 0.01  # Au moins 10ms

    with timer("test_operation") as op_name:
        assert op_name == "test_operation"
        time.sleep(0.01)  # Simule une opération


def test_temporary_directory_example():
    """Exemple pratique: répertoire temporaire."""
    state = {"created": False, "deleted": False}

    @as_context_manager
    def temp_directory(prefix):
        dir_name = f"/tmp/{prefix}_123"
        state["created"] = True
        yield dir_name
        state["deleted"] = True

    with temp_directory("test") as tmpdir:
        assert tmpdir == "/tmp/test_123"
        assert state["created"]
        assert not state["deleted"]

    assert state["deleted"]


if __name__ == "__main__":
    print("Utilisez run_decorator_tests.py pour exécuter les tests")
