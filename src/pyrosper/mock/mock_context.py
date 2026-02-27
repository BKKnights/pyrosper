from .. import Symbol
from ..base_context import BaseContext
from .mock_experiment import MockExperiment
from .mock_pyrosper import MockPyrosper
from .mock_variant import MockVariant


mock_symbol = Symbol("test_symbol")


class MockContext(BaseContext[MockPyrosper]):
    def setup(cls) -> MockPyrosper:
        variant = MockVariant(name="test variant", picks={mock_symbol: "expected_result"})
        experiment = MockExperiment(name="test experiment", variants=[variant], is_enabled=True)
        return MockPyrosper().with_experiment(experiment)