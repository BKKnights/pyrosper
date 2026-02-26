from pyrosper import BaseContext, Symbol
from pyrosper.mock.mock_experiment import MockExperiment
from pyrosper.mock.mock_pyrosper import MockPyrosper
from pyrosper.mock.mock_variant import MockVariant


class TestInjection:
    def test_pick(self):

        my_symbol = Symbol("my_symbol")

        class MockContext(BaseContext[MockPyrosper]):
            def setup(self) -> MockPyrosper:
                variant = MockVariant(name="test variant", picks={my_symbol: "expected_result"})
                experiment = MockExperiment(name="test experiment", variants=[variant], is_enabled=True)
                return MockPyrosper().with_experiment(experiment)

        class MyClass:
            value = MockContext.pick(str, my_symbol)

            def do_something(self):
                should_be_int_instance = self.value
                return should_be_int_instance


        with MockContext() as pyrosper:
            my_class = MyClass()
            assert my_class.value == "expected_result"
            assert my_class.do_something() == "expected_result"