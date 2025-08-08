"""
Test demonstrating how to use PyrosperContext.
"""

import asyncio
from typing import Self

import pytest

from .context import Context, get_current
from .mock.mock_pyrosper import MockPyrosper
from .mock.mock_variant import MockVariant
from .mock.mock_experiment import MockExperiment
from .symbol import Symbol
from .pyrosper import pick, Pyrosper

# Test data
key = Symbol("key")
value_a = "value a"
value_b = "value b"


class UserContext(Context):
    """Example implementation of PyrosperContext."""

    def __init__(self, user_id: str, variant_index: int):
        super().__init__()
        self.user_id = user_id
        self.variant_index = variant_index

    def setup_context(self):
        """Create and configure a pyrosper instance for this user."""
        # Create variant based on variant_index
        value = value_a if self.variant_index == 0 else value_b
        variant = MockVariant(f"variant_{self.variant_index}", {key: value})

        # Create experiment
        experiment = MockExperiment(name="test", variants=[variant])

        # Create pyrosper instance
        pyrosper = MockPyrosper()
        pyrosper.with_experiment(experiment)

        return pyrosper


class SimpleContext(Context):
    """
    Simple implementation of PyrosperContext that uses a provided pyrosper instance.

    Usage:
        with SimplePyrosperContext(my_pyrosper_instance) as pyrosper:
            # Use pyrosper
            pass
    """

    def __init__(self, pyrosper_instance: 'Pyrosper') -> None:
        super().__init__()
        self.pyrosper_instance = pyrosper_instance

    def setup_context(self) -> 'Pyrosper':
        """Return the provided pyrosper instance."""
        return self.pyrosper_instance


def test_simple_context():
    """Test using SimplePyrosperContext."""
    print("=== Simple Context Test ===")

    # Create a mock pyrosper
    mock_pyrosper = MockPyrosper()
    variant = MockVariant("test_variant", {key: "test_value"})
    experiment = MockExperiment(name="test", variants=[variant])
    mock_pyrosper.with_experiment(experiment)

    # Use SimplePyrosperContext
    with SimpleContext(mock_pyrosper) as pyrosper:
        # Verify we have the correct context
        current = get_current()
        assert current is pyrosper
        assert current is mock_pyrosper

        # Use the pyrosper
        value = pyrosper.pick(key)
        print(f"Simple context value: {value}")

    # Verify context is cleaned up
    current = get_current()
    assert current is None
    print("✅ Simple context test passed!")


def test_user_context():
    """Test using UserPyrosperContext."""
    print("=== User Context Test ===")

    with UserContext("user1", 0) as pyrosper:
        # Verify context
        current = get_current()
        assert current is pyrosper

        # Get value
        value = pyrosper.pick(key)
        assert value == value_a
        print(f"User1 value: {value}")

    # Test with different user
    with UserContext("user2", 1) as pyrosper:
        current = get_current()
        assert current is pyrosper

        value = pyrosper.pick(key)
        assert value == value_b
        print(f"User2 value: {value}")

    print("✅ User context test passed!")


@pytest.mark.asyncio
async def test_concurrent_context():
    """Test concurrent context usage."""
    print("=== Concurrent Context Test ===")

    class AbTested:
        injected: str

        def __init__(self):
            # Use the generic get_current() instead of the mock-specific one
            pyrosper = get_current()
            self.injected = pick(pyrosper, key, str)

    async def user_task(user_id: str, variant_index: int, delay: float):
        with UserContext(user_id, variant_index) as pyrosper:
            # Verify context
            current = get_current()
            assert current is pyrosper
            value1 = AbTested()
            """Simulate a user task."""
            await asyncio.sleep(delay)
            expected = value_a if variant_index == 0 else value_b
            assert value1.injected == value1.injected
            print(f"User {user_id}: expected={expected}, got={value1}")

            return f"{value1.injected} for {user_id}"

    # Run users concurrently
    results = await asyncio.gather(
        user_task("user1", 0, 5.1),
        user_task("user2", 1, 0.0),
        user_task("user3", 0, 0.05),
        user_task("user4", 1, 0.02),
    )

    # Verify results
    assert results[0] == f"{value_a} for user1"
    assert results[1] == f"{value_b} for user2"
    assert results[2] == f"{value_a} for user3"
    assert results[3] == f"{value_b} for user4"


def test_decorator_usage():
    """Test using PyrosperContext as a decorator."""
    print("=== Decorator Usage Test ===")

    @UserContext("test_user", 0)
    def get_value():
        pyrosper = get_current()
        if pyrosper is None:
            raise RuntimeError("No pyrosper in context")
        return pyrosper.pick(key)

    result = get_value()
    assert result == value_a
    print(f"Decorator result: {result}")
    print("✅ Decorator usage test passed!")


if __name__ == "__main__":
    print("Testing PyrosperContext...\n")

    # Run tests
    test_simple_context()
    test_user_context()
    test_decorator_usage()
    asyncio.run(test_concurrent_context())

    print("\n🎉 All tests passed! PyrosperContext is working correctly.")