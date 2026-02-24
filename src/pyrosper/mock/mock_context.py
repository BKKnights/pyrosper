from ..base_context import BaseContext
from .mock_experiment import MockExperiment
from .mock_pyrosper import MockPyrosper
from .mock_variant import MockVariant


class MockContext(BaseContext[MockPyrosper]):
    def setup(self) -> MockPyrosper:
        variant = MockVariant(name="test variant", picks={"test_value": "expected_result"})
        experiment = MockExperiment(name="test experiment", variants=[variant], is_enabled=True)
        return MockPyrosper().with_experiment(experiment)