"""
Script pour exécuter les tests des décorateurs sans pytest.
"""

import sys
from test_decorators import (
    test_as_context_manager_basic,
    test_as_context_manager_with_arguments,
    test_as_context_manager_exception_handling,
    test_context_manager_custom,
    test_simple_context,
    test_simple_context_with_args,
    test_with_setup_teardown,
    test_nested_context_managers,
    test_context_manager_returns_none,
    test_reusable_context_manager,
    test_database_connection_example,
    test_file_operations_example,
    test_timer_example,
    test_temporary_directory_example,
)


def run_test(test_func):
    """Exécute un test et affiche le résultat."""
    try:
        test_func()
        print(f"✅ {test_func.__name__}")
        return True
    except AssertionError as e:
        print(f"❌ {test_func.__name__}: {e}")
        return False
    except Exception as e:
        print(f"❌ {test_func.__name__}: Exception: {e}")
        return False


def main():
    """Exécute tous les tests."""
    tests = [
        test_as_context_manager_basic,
        test_as_context_manager_with_arguments,
        test_as_context_manager_exception_handling,
        test_context_manager_custom,
        test_simple_context,
        test_simple_context_with_args,
        test_with_setup_teardown,
        test_nested_context_managers,
        test_context_manager_returns_none,
        test_reusable_context_manager,
        test_database_connection_example,
        test_file_operations_example,
        test_timer_example,
        test_temporary_directory_example,
    ]

    print("=" * 60)
    print("Exécution des tests de décorateurs")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for test in tests:
        if run_test(test):
            passed += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"Résultats: {passed} tests réussis, {failed} tests échoués")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
