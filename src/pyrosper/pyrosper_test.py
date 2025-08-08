import asyncio

from .mock.mock_experiment import MockExperiment
from .mock.mock_pyrosper import MockPyrosper
from .pyrosper import pick
from .symbol import Symbol
from .mock.mock_variant import MockVariant
from .context import context

def test_pick_def():
    pyrosper = MockPyrosper()
    test_property_provider_symbol = Symbol("test_property_provider")

    class MyVariant:
        greeting: str

    class MyVariantA(MyVariant):
        greeting = 'Hello from Variant A!'

    class MyVariantB(MyVariant):
        greeting = 'Hello from Variant B!'

    variant_a = MyVariantA()
    variant_b = MyVariantB()
    pyrosper.experiments = [
        MockExperiment(
            name="test_experiment",
            variants=[
                MockVariant(
                    name="A",
                    picks={test_property_provider_symbol: variant_a},
                ),
                MockVariant(
                    name="B",
                    picks={test_property_provider_symbol: variant_b},
                )
            ],
            is_enabled=True
        )
    ]
    class TestClass:
        test_property = pick(pyrosper, test_property_provider_symbol, MyVariant)


    instance = TestClass()
    assert instance.test_property is not None
    assert instance.test_property.greeting == variant_a.greeting


def test_pyrosper_context_sync_function():
    """Test pyrosper_context decorator with synchronous functions"""
    
    @context()
    def test_function():
        return "test_result"
    
    # Test that the function works normally
    result = test_function()
    assert result == "test_result"
    
    # Test that the function preserves its name
    assert test_function.__name__ == "test_function"


def test_pyrosper_context_async_function():
    """Test pyrosper_context decorator with asynchronous functions"""
    
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