"""
Tests for PyrosperContext with strong typing.
"""

import asyncio
import pytest
from .symbol import Symbol
from .mock.mock_experiment import MockExperiment
from .mock.mock_pyrosper import MockPyrosper
from .mock.mock_variant import MockVariant
from .mock.mock_context import MockContext


class TestStronglyTypedContext:
    """Tests for the strongly typed context solution"""
    
    def test_context_init(self):
        """Test Context initialization"""
        ctx = MockContext()
        assert ctx.instance_token is None
        assert ctx.pyrosper_instance is None
    
    def test_teardown_context_default(self):
        """Test that teardown_context doesn't raise by default"""
        ctx = MockContext()
        # Should not raise any exception
        ctx.teardown_context()
    
    def test_context_as_context_manager(self):
        """Test Context as context manager and get_current"""
        with MockContext() as pyrosper:
            assert isinstance(pyrosper, MockPyrosper)
            # Check that get_current works and returns the correct type
            current: MockPyrosper = MockContext.get_current()
            assert current is pyrosper
    
    def test_context_as_context_manager_with_exception(self):
        """Test Context as context manager handles exceptions properly"""
        with pytest.raises(ValueError):
            with MockContext():
                raise ValueError("test exception")
        
        # Check that context variables are reset
        with pytest.raises(RuntimeError, match="No pyrosper instance found in context"):
            MockContext.get_current()
    
    def test_context_teardown_called(self):
        """Test that teardown_context is called when exiting context"""
        teardown_called = False
        
        class MockTestContext(MockContext):
            def teardown_context(self):
                nonlocal teardown_called
                teardown_called = True
        
        with MockTestContext():
            pass
        
        assert teardown_called
    
    def test_context_multiple_instances(self):
        """Test that multiple Context instances work independently"""
        
        with MockContext() as pyrosper1:
            current1 = MockContext.get_current()
            assert current1 is pyrosper1
            
            with MockContext() as pyrosper2:
                current2 = MockContext.get_current()
                assert current2 is pyrosper2
                assert current2 is not pyrosper1
            
            # After inner context exits, should be back to outer
            assert MockContext.get_current() is pyrosper1
        
        # After both contexts exit, should be reset
        with pytest.raises(RuntimeError, match="No pyrosper instance found in context"):
            MockContext.get_current()

    @pytest.mark.asyncio
    async def test_context_race_conditions(self):
        """Test that context prevents race conditions under load with multiple users"""
        key = Symbol("test_key")
        value_a = "value_a"
        value_b = "value_b"
        user_1 = "user_1"
        user_2 = "user_2"
        
        picks_a = {key: value_a}
        picks_b = {key: value_b}
        
        variant_a = MockVariant(name="A", picks=picks_a)
        variant_b = MockVariant(name="B", picks=picks_b)

        class UserAContext(MockContext):
            def setup(self) -> MockPyrosper:
                experiment = MockExperiment(name="mock experiment", variants=[variant_a])
                return MockPyrosper().with_experiment(experiment)

        class UserBContext(MockContext):
            def setup(self) -> MockPyrosper:
                experiment = MockExperiment(name="mock experiment", variants=[variant_b])
                return MockPyrosper().with_experiment(experiment)

        async def user_task(ctx_class, user_id, expected_value, delay):
            with ctx_class() as pyrosper:
                await pyrosper.set_for_user(user_id)
                current = ctx_class.get_current()
                assert current is pyrosper
                
                await asyncio.sleep(delay)
                
                # Re-verify after sleep to check for interference
                assert ctx_class.get_current() is pyrosper
                val = pyrosper.pick(key, str)
                assert val == expected_value
                return f"{user_id} {val}"

        # Run users concurrently
        results = await asyncio.gather(
            user_task(UserAContext, user_1, value_a, 0.1),
            user_task(UserBContext, user_2, value_b, 0.05),
        )

        assert results[0] == f"{user_1} {value_a}"
        assert results[1] == f"{user_2} {value_b}"
