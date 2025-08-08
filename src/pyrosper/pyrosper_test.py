import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from .mock.mock_experiment import MockExperiment
from .mock.mock_pyrosper import MockPyrosper
from .pyrosper import Pyrosper, pick
from .symbol import Symbol
from .mock.mock_variant import MockVariant
from .context import context


class TestPyrosper:
    """Comprehensive tests for the Pyrosper class"""
    
    @pytest.fixture
    def pyrosper(self):
        return Pyrosper()
    
    @pytest.fixture
    def mock_experiment(self):
        test_symbol = Symbol("test_symbol")
        return MockExperiment(
            name="test_experiment",
            variants=[
                MockVariant("control", {test_symbol: "control_value"}),
                MockVariant("variant_a", {test_symbol: "variant_a_value"}),
            ],
            is_enabled=True
        )
    
    @pytest.fixture
    def test_symbol(self, mock_experiment):
        # Get the actual symbol from the experiment to ensure we use the same instance
        return list(mock_experiment.variants[0].picks.keys())[0]
    
    def test_init(self, pyrosper):
        """Test Pyrosper initialization"""
        assert pyrosper.experiments == []
        assert pyrosper.used_symbols == set()
    
    @pytest.mark.asyncio
    async def test_set_for_user(self, pyrosper, mock_experiment):
        """Test set_for_user method"""
        pyrosper.experiments = [mock_experiment]
        await pyrosper.set_for_user("user123")
        # Verify that set_for_user was called on the experiment
        assert mock_experiment.user_id == "user123"
    
    @pytest.mark.asyncio
    async def test_set_for_user_no_experiments(self, pyrosper):
        """Test set_for_user with no experiments"""
        # Should not raise any exceptions
        await pyrosper.set_for_user("user123")
    
    def test_has_pick_true(self, pyrosper, mock_experiment, test_symbol):
        """Test has_pick returns True when symbol exists"""
        pyrosper.experiments = [mock_experiment]
        assert pyrosper.has_pick(test_symbol) is True
    
    def test_has_pick_false(self, pyrosper, mock_experiment):
        """Test has_pick returns False when symbol doesn't exist"""
        pyrosper.experiments = [mock_experiment]
        non_existent_symbol = Symbol("non_existent")
        assert pyrosper.has_pick(non_existent_symbol) is False
    
    def test_has_pick_no_experiments(self, pyrosper, test_symbol):
        """Test has_pick with no experiments"""
        assert pyrosper.has_pick(test_symbol) is False
    
    def test_pick_success(self, pyrosper, mock_experiment, test_symbol):
        """Test pick returns correct value"""
        pyrosper.experiments = [mock_experiment]
        result = pyrosper.pick(test_symbol, str)
        assert result == "control_value"
    
    def test_pick_not_found(self, pyrosper, mock_experiment):
        """Test pick raises ValueError when symbol not found"""
        pyrosper.experiments = [mock_experiment]
        non_existent_symbol = Symbol("non_existent")
        with pytest.raises(ValueError, match="Unable to find"):
            pyrosper.pick(non_existent_symbol, str)
    
    def test_pick_no_experiments(self, pyrosper, test_symbol):
        """Test pick with no experiments"""
        with pytest.raises(ValueError, match="Unable to find"):
            pyrosper.pick(test_symbol, str)
    
    def test_validate_success(self, pyrosper, mock_experiment):
        """Test validate with valid experiment"""
        result = pyrosper.validate(mock_experiment)
        # Get the actual symbol from the experiment
        actual_symbol = list(mock_experiment.variants[0].picks.keys())[0]
        assert result == {actual_symbol}
    
    def test_validate_duplicate_experiment_name(self, pyrosper, mock_experiment):
        """Test validate with duplicate experiment name"""
        pyrosper.experiments = [mock_experiment]
        duplicate_experiment = MockExperiment(
            name="test_experiment",  # Same name
            variants=[MockVariant("control", {"other_symbol": "value"})],
            is_enabled=True
        )
        with pytest.raises(ValueError, match='Experiment name "test_experiment" already used'):
            pyrosper.validate(duplicate_experiment)
    
    def test_validate_inconsistent_variants(self, pyrosper):
        """Test validate with inconsistent variant picks"""
        inconsistent_experiment = MockExperiment(
            name="inconsistent",
            variants=[
                MockVariant("control", {"symbol1": "value1", "symbol2": "value2"}),
                MockVariant("variant", {"symbol1": "value1"}),  # Missing symbol2
            ],
            is_enabled=True
        )
        with pytest.raises(ValueError, match='Variant "variant" contains picks not in "control"'):
            pyrosper.validate(inconsistent_experiment)
    
    def test_validate_duplicate_symbol(self, pyrosper, mock_experiment):
        """Test validate with duplicate symbol"""
        # Get the actual symbol from the experiment
        actual_symbol = list(mock_experiment.variants[0].picks.keys())[0]
        pyrosper.used_symbols = {actual_symbol}
        with pytest.raises(ValueError, match="Variant pick name Symbol\\(test_symbol\\) already used"):
            pyrosper.validate(mock_experiment)
    
    def test_with_experiment_success(self, pyrosper, mock_experiment):
        """Test with_experiment adds experiment successfully"""
        result = pyrosper.with_experiment(mock_experiment)
        assert result is pyrosper
        assert len(pyrosper.experiments) == 1
        assert pyrosper.experiments[0] == mock_experiment
        # Get the actual symbol from the experiment
        actual_symbol = list(mock_experiment.variants[0].picks.keys())[0]
        assert actual_symbol in pyrosper.used_symbols
    
    def test_get_experiment_success(self, pyrosper, mock_experiment):
        """Test get_experiment returns correct experiment"""
        pyrosper.experiments = [mock_experiment]
        result = pyrosper.get_experiment("test_experiment")
        assert result == mock_experiment
    
    def test_get_experiment_not_found(self, pyrosper):
        """Test get_experiment raises ValueError when experiment not found"""
        with pytest.raises(ValueError, match='Experiment "nonexistent" not found'):
            pyrosper.get_experiment("nonexistent")
    
    def test_experiment_exists_true(self, pyrosper, mock_experiment):
        """Test experiment_exists returns True when experiment exists"""
        pyrosper.experiments = [mock_experiment]
        assert pyrosper.experiment_exists("test_experiment") is True
    
    def test_experiment_exists_false(self, pyrosper):
        """Test experiment_exists returns False when experiment doesn't exist"""
        assert pyrosper.experiment_exists("nonexistent") is False
    
    def test_check_experiment_has_variant_success(self, pyrosper, mock_experiment):
        """Test check_experiment_has_variant with existing variant"""
        pyrosper.experiments = [mock_experiment]
        # Should not raise any exception
        pyrosper.check_experiment_has_variant("test_experiment", "control")
    
    def test_check_experiment_has_variant_not_found(self, pyrosper, mock_experiment):
        """Test check_experiment_has_variant with non-existent variant"""
        pyrosper.experiments = [mock_experiment]
        with pytest.raises(ValueError, match='Variant "nonexistent" does not exist in Experiment "test_experiment"'):
            pyrosper.check_experiment_has_variant("test_experiment", "nonexistent")
    
    def test_check_experiment_has_variant_experiment_not_found(self, pyrosper):
        """Test check_experiment_has_variant with non-existent experiment"""
        with pytest.raises(ValueError, match='Experiment "nonexistent" not found'):
            pyrosper.check_experiment_has_variant("nonexistent", "control")


class TestPickFunction:
    """Tests for the pick function"""
    
    def test_pick_success(self):
        """Test pick function returns correct value with correct type"""
        pyrosper = MockPyrosper()
        test_symbol = Symbol("test_symbol")
        
        class MyVariant:
            greeting: str
        
        class MyVariantA(MyVariant):
            greeting = 'Hello from Variant A!'
        
        variant_a = MyVariantA()
        pyrosper.experiments = [
            MockExperiment(
                name="test_experiment",
                variants=[
                    MockVariant(
                        name="A",
                        picks={test_symbol: variant_a},
                    )
                ],
                is_enabled=True
            )
        ]
        
        result = pick(pyrosper, test_symbol, MyVariant)
        assert result is not None
        assert result.greeting == variant_a.greeting
    
    def test_pick_symbol_not_found(self):
        """Test pick function raises ValueError when symbol not found"""
        pyrosper = MockPyrosper()
        test_symbol = Symbol("test_symbol")
        
        with pytest.raises(ValueError, match="Unable to find"):
            pick(pyrosper, test_symbol, str)
    
    def test_pick_wrong_type(self):
        """Test pick function raises TypeError when value has wrong type"""
        pyrosper = MockPyrosper()
        test_symbol = Symbol("test_symbol")
        
        pyrosper.experiments = [
            MockExperiment(
                name="test_experiment",
                variants=[
                    MockVariant(
                        name="A",
                        picks={test_symbol: "string_value"},
                    )
                ],
                is_enabled=True
            )
        ]
        
        with pytest.raises(TypeError, match="Expected type <class 'int'>, but got"):
            pick(pyrosper, test_symbol, int)


class TestContextDecorator:
    """Tests for the context decorator"""
    
    def test_context_sync_function(self):
        """Test context decorator with synchronous functions"""
        
        @context()
        def test_function():
            return "test_result"
        
        # Test that the function works normally
        result = test_function()
        assert result == "test_result"
        
        # Test that the function preserves its name
        assert test_function.__name__ == "test_function"
    
    def test_context_async_function(self):
        """Test context decorator with asynchronous functions"""
        
        @context()
        async def test_async_function():
            return "async_test_result"
        
        # Test that the async function works normally
        async def run_test():
            result = await test_async_function()
            assert result == "async_test_result"
            # Test that the function preserves its name
            assert test_async_function.__name__ == "test_async_function"
        
        asyncio.run(run_test())
    
    def test_context_with_exception(self):
        """Test context decorator properly handles exceptions"""
        
        @context()
        def test_function_with_exception():
            raise ValueError("test exception")
        
        with pytest.raises(ValueError, match="test exception"):
            test_function_with_exception()
    
    def test_context_async_with_exception(self):
        """Test context decorator properly handles async exceptions"""
        
        @context()
        async def test_async_function_with_exception():
            raise ValueError("async test exception")
        
        async def run_test():
            with pytest.raises(ValueError, match="async test exception"):
                await test_async_function_with_exception()
        
        asyncio.run(run_test())