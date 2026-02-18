from src.pyrosper.base_context import BaseContext
from .mock_experiment import MockExperiment
from .mock_pyrosper import MockPyrosper
from .mock_variant import MockVariant


class MockContext(BaseContext[MockPyrosper]):
    def setup(self) -> MockPyrosper:
        variant = MockVariant(name="test variant", picks={})
        experiment = MockExperiment(name="test experiment", variants=[variant])
        return MockPyrosper().with_experiment(experiment)