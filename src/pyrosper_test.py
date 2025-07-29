from src.mock_experiment import MockExperiment
from src.pyrosper import Pyrosper, pick
from src.symbol import Symbol
from src.variant import Variant

def test_pick_def():
    pyrosper = Pyrosper()
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
                Variant(
                    name="A",
                    picks={test_property_provider_symbol: variant_a},
                ),
                Variant(
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