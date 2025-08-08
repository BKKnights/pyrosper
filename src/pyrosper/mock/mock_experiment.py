from typing import Optional, Self, TypeVar, Generic

from ..base_experiment import BaseExperiment
from .mock_algorithm import MockAlgorithm
from .mock_variant import MockVariant
from .mock_user_variant import MockUserVariant

MockAlgorithmType = TypeVar('MockAlgorithmType', bound='MockAlgorithm')
VariantType = TypeVar('VariantType', bound='MockVariant')
UserVariantType = TypeVar('UserVariantType', bound='MockUserVariant')

class MockExperiment(BaseExperiment[MockAlgorithm, MockVariant, MockUserVariant], Generic[MockAlgorithmType, VariantType]):
    user_id: str
    algorithm: Optional[MockAlgorithm] = None

    async def get_experiment(self) -> Optional[Self]:
        return self

    async def upsert_experiment(self, experiment: Self) -> Self:
        return type(self)(
            id=experiment.id,
            name=experiment.name,
            variants=experiment.variants,
            is_enabled=experiment.is_enabled,
            variant_index=experiment.variant_index,
        )

    async def delete_experiment(self, experiment: Self) -> None:
        pass

    async def get_user_variant(self, user_id: str, experiment_id: str) -> Optional[MockUserVariant]:
        pass

    async def upsert_user_variant(self, user_variant: MockUserVariant) -> None:
        pass

    async def delete_user_variant(self, user_variant: MockUserVariant) -> None:
        pass

    async def delete_user_variants(self) -> None:
        pass

    async def get_algorithm(self) -> MockAlgorithm:
        if self.algorithm:
            return self.algorithm
        self.algorithm = MockAlgorithm()
        return self.algorithm

    async def set_for_user(self, user_id: Optional[str] = None) -> None:
        if user_id is None:
            raise ValueError("User ID must be provided")
        await super().set_for_user(user_id)
        self.user_id = user_id

    async def get_variant_index(self, algorithm: MockAlgorithm) -> int:
        return algorithm.variant_index

    async def reward_algorithm(self, algorithm: MockAlgorithm, user_variant_index: int, score: float) -> MockAlgorithm:
        return MockAlgorithm()

    async def upsert_algorithm(self, algorithm: MockAlgorithm) -> None:
        pass

    async def delete_algorithm(self) -> None:
        pass