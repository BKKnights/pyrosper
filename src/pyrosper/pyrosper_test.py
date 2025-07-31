from .mock_experiment import MockExperiment
from .mock_pyrosper import MockPyrosper
from .pyrosper import pick
from .symbol import Symbol
from .mock_variant import MockVariant

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