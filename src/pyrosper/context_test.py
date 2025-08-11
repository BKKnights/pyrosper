"""
Test demonstrating how to use PyrosperContext.
"""

import asyncio
import pytest
from unittest.mock import Mock

from .context import BaseContext, get_current, instance_storage
from .mock.mock_experiment import MockExperiment
from .mock.mock_variant import MockVariant
from .symbol import Symbol
from .pyrosper import Pyrosper

class TestContext:
    """Tests for the Context class"""
    
    def test_context_init(self):
        """Test Context initialization"""
        ctx = BaseContext()
        assert ctx.instance_token is None
        assert ctx.pyrosper_instance is None

    @pytest.mark.asyncio
    async def test_setup_not_implemented(self):
        """Test that setup raises NotImplementedError by default"""
        ctx = BaseContext()
        with pytest.raises(NotImplementedError, match="Class must implement setup\\(\\)"):
            ctx.setup()
    
    def test_teardown_context_default(self):
        """Test that teardown_context doesn't raise by default"""
        ctx = BaseContext()
        # Should not raise any exception
        ctx.teardown_context()
    
    def test_context_as_context_manager(self):
        """Test Context as context manager"""
        mock_pyrosper = Mock()
        
        class TestContext2(BaseContext):
            def setup(self):
                return mock_pyrosper
        
        ctx = TestContext2()
        with ctx as pyrosper:
            assert pyrosper == mock_pyrosper
            # Check that context variables are set
            assert instance_storage.get() == mock_pyrosper
    
    def test_context_as_context_manager_with_exception(self):
        """Test Context as context manager handles exceptions properly"""
        mock_pyrosper = Mock()
        
        class TestContext2(BaseContext):
            def setup(self):
                return mock_pyrosper
        
        with pytest.raises(ValueError):
            with TestContext2() as pyrosper:
                raise ValueError("test exception")
        
        # Check that context variables are reset
        assert instance_storage.get() is None
    
    def test_context_teardown_called(self):
        """Test that teardown_context is called when exiting context"""
        mock_pyrosper = Mock()
        teardown_called = False
        
        class TestContext2(BaseContext):
            def setup(self):
                return mock_pyrosper
            
            def teardown_context(self):
                nonlocal teardown_called
                teardown_called = True
        
        with TestContext2():
            pass
        
        assert teardown_called
    
    def test_context_multiple_instances(self):
        """Test that multiple Context instances work independently"""
        mock_pyrosper1 = Mock()
        mock_pyrosper2 = Mock()
        
        class TestContext2(BaseContext):
            def __init__(self, pyrosper_instance):
                super().__init__()
                self.pyrosper_instance = pyrosper_instance
            
            def setup(self):
                return self.pyrosper_instance
        
        ctx1 = TestContext2(mock_pyrosper1)
        ctx2 = TestContext2(mock_pyrosper2)
        
        with ctx1 as pyrosper1:
            assert pyrosper1 == mock_pyrosper1
            with ctx2 as pyrosper2:
                assert pyrosper2 == mock_pyrosper2
                # Inner context should override outer
                assert instance_storage.get() == mock_pyrosper2
            
            # After inner context exits, should be back to outer
            assert instance_storage.get() == mock_pyrosper1
        
        # After both contexts exit, should be reset
        assert instance_storage.get() is None


class TestGetCurrent:
    """Tests for the get_current function"""
    
    def test_get_current_success(self):
        """Test get_current returns the current pyrosper instance"""
        mock_pyrosper = Mock()
        
        # Set the instance in context
        token = instance_storage.set(mock_pyrosper)
        try:
            result = get_current()
            assert result == mock_pyrosper
        finally:
            instance_storage.reset(token)
    
    def test_get_current_no_instance(self):
        """Test get_current raises RuntimeError when no instance is set"""
        # Ensure no instance is set
        assert instance_storage.get() is None
        
        with pytest.raises(RuntimeError, match="No pyrosper instance found in context"):
            get_current()
    
    def test_get_current_with_none_instance(self):
        """Test get_current raises RuntimeError when instance is None"""
        # Set None as the instance
        token = instance_storage.set(None)
        try:
            with pytest.raises(RuntimeError, match="No pyrosper instance found in context"):
                get_current()
        finally:
            instance_storage.reset(token)


    @pytest.mark.asyncio
    async def test_context_race_conditions(self):
        """Test that context prevents race conditions under load with multiple users"""
        key = Symbol("test_key")
        variant_index_a = 0
        variant_index_b = 1
        value_a = "value_a"
        value_b = "value_b"
        user_1 = "user_1"
        user_2 = "user_2"
        user_3 = "user_3"
        user_4 = "user_4"
        picks_a = {key: value_a}
        picks_b = {key: value_b}
        picks = [picks_a, picks_b]
        variant_a = MockVariant(name="A", picks=picks_a)
        variant_b = MockVariant(name="B", picks=picks_b)
        variants = [variant_a, variant_b]
        all_pyrosper_instances = []

        class MockContext(BaseContext):
            def setup(self):
                experiment = MockExperiment(
                    name="mock experiment",
                    variants=variants,
                )
                # Simulate setting up a user context with a specific variant
                return Pyrosper().with_experiment(experiment)

        class AbTest:
            injected: str

            def __init__(self):
                pyrosper = get_current()
                self.pyrosper = pyrosper
                self.injected = pyrosper.pick(key, str)


        async def user_task(user_id: str, variant_index: int, delay: float):
            with MockContext() as pyrosper:
                # Verify context
                if pyrosper in all_pyrosper_instances:
                    raise RuntimeError("Pyrosper instance reused across users")
                all_pyrosper_instances.append(pyrosper)
                await pyrosper.set_for_user(user_id)
                experiment = pyrosper.get_experiment("mock experiment")
                experiment.use_variant(variants[variant_index].name)
                current = get_current()
                algorithm = await experiment.get_algorithm()
                variant_index_from_experiment = await experiment.get_variant_index(algorithm)
                assert variant_index_from_experiment == variant_index
                assert current is pyrosper
                """Simulate a user task."""
                await asyncio.sleep(delay)
                ab_test = AbTest()
                should_be_current = get_current()
                assert should_be_current is pyrosper
                assert ab_test.pyrosper == pyrosper
                assert ab_test.injected == picks[variant_index][key]
                return f"{user_id} {ab_test.injected}"

        # Run users concurrently
        results = await asyncio.gather(
            user_task(user_1, variant_index_a, 5.1),
            user_task(user_2, variant_index_b, 0.01),
            user_task(user_3, variant_index_a, 0.05),
            user_task(user_4, variant_index_b, 0.02),
        )

        # Verify results
        assert results[0] == f"{user_1} {value_a}"
        assert results[1] == f"{user_2} {value_b}"
        assert results[2] == f"{user_3} {value_a}"
        assert results[3] == f"{user_4} {value_b}"

