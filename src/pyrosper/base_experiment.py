from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Self, Type, Any
from .variant import Variant
from .user_variant import UserVariant

AlgorithmType = TypeVar('AlgorithmType')
UserVariantType = TypeVar('UserVariantType', bound='UserVariant')
ExperimentType = TypeVar('ExperimentType', bound='BaseExperiment')
VariantType = TypeVar('VariantType', bound='Variant')
ExperimentIdType = TypeVar('ExperimentIdType')
UserIdType = TypeVar('UserIdType')
UserVariantIdType = TypeVar('UserVariantIdType')
PickType = TypeVar('PickType')

class BaseExperiment(ABC, Generic[AlgorithmType, VariantType, UserVariantType, ExperimentIdType, UserIdType, UserVariantIdType]):
    variant_index: int
    name: str
    variants: List[VariantType]
    _is_enabled: bool
    id: Optional[ExperimentIdType]

    def __init__(self, name: str, variants: List[VariantType], id: Optional[ExperimentIdType] = None, *args: Any, **kwargs: Any):
        self.variant_index = 0
        self.name = name
        self.variants = variants
        self.id = id

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    @abstractmethod
    def is_enabled(self, value: bool) -> None:
        self._is_enabled = value

    async def _get_user_variant_index(self, user_id: "UserIdType") -> Optional[int]:
        experiment = await self.get_experiment()
        if experiment and experiment.id:
            user_variant = await self.get_user_variant(user_id, experiment.id)
            if user_variant:
                return user_variant.index
        return None

    async def _upsert_user_variant_index(self, user_id: "UserIdType", index: int) -> None:
        experiment = await self.get_experiment()
        if not experiment or not experiment.id:
            return
        user_variant = await self.get_user_variant(user_id=user_id, experiment_id=experiment.id)
        if user_variant:
            await self.upsert_user_variant(user_variant=user_variant)

    async def _remove_index(self, user_id: "UserIdType") -> None:
        experiment = await self.get_experiment()
        if not experiment or not experiment.id:
            raise ValueError("Experiment not found")
        user_variant = await self.get_user_variant(user_id=user_id, experiment_id=experiment.id)
        if user_variant:
            await self.delete_user_variant(user_variant=user_variant)

    def _check_variants(self) -> None:
        if len(self.variants) < 1:
            raise ValueError("Empty variants")

    @abstractmethod
    async def get_experiment(self) -> Optional['Self']:
        pass

    @abstractmethod
    async def upsert_experiment(self, experiment) -> 'Self':
        pass

    @abstractmethod
    async def delete_experiment(self, experiment) -> None:
        pass

    @abstractmethod
    async def get_user_variant(self, user_id: "UserIdType", experiment_id: "ExperimentIdType") -> Optional["UserVariantType"]:
        pass

    @abstractmethod
    async def upsert_user_variant(self, user_variant: UserVariantType) -> None:
        pass

    @abstractmethod
    async def delete_user_variant(self, user_variant: UserVariantType) -> None:
        pass

    @abstractmethod
    async def delete_user_variants(self) -> None:
        pass

    @abstractmethod
    async def get_algorithm(self) -> AlgorithmType:
        pass

    @abstractmethod
    async def get_variant_index(self, algorithm: AlgorithmType) -> int:
        pass

    @abstractmethod
    async def reward_algorithm(self, algorithm: AlgorithmType, user_variant_index: int, score: float) -> AlgorithmType:
        pass

    @abstractmethod
    async def upsert_algorithm(self, algorithm: AlgorithmType) -> None:
        pass

    @abstractmethod
    async def delete_algorithm(self) -> None:
        pass

    def reset(self) -> None:
        self.variant_index = 0
        self.is_enabled = False
        self.id = None

    async def complete_for_user(self, user_id: "UserIdType", score: float) -> None:
        if not self.is_enabled:
            return
        user_variant_index = await self._get_user_variant_index(user_id)
        if user_variant_index is None:
            return
        await self._remove_index(user_id)
        algorithm = await self.get_algorithm()
        updated_algorithm = await self.reward_algorithm(algorithm, user_variant_index, score)
        await self.upsert_algorithm(updated_algorithm)

    async def set_for_user(self, user_id: Optional["UserIdType"] = None) -> None:
        experiment = await self.get_experiment()
        if experiment:
            self.is_enabled = bool(experiment.is_enabled)
            self.id = experiment.id
            await self.set_variant_index_for_user(user_id)
            return
        self.reset()

    def use_variant(self, variant_name: str) -> None:
        variant = next((v for v in self.variants if v.name == variant_name), None)
        if not variant:
            raise ValueError(f'Variant with name "{variant_name}" not found')
        self.variant_index = self.variants.index(variant)

    def safe_enable(self) -> None:
        self.is_enabled = True

    def safe_disable(self) -> None:
        self.is_enabled = False

    async def set_variant_index_for_user(self, user_id: Optional["UserIdType"] = None) -> None:
        algorithm = await self.get_algorithm()
        if not user_id:
            self.variant_index = await self.get_variant_index(algorithm)
            return

        existing_user_variant_index = await self._get_user_variant_index(user_id)
        if isinstance(existing_user_variant_index, int):
            self.variant_index = existing_user_variant_index
            return

        self.variant_index = await self.get_variant_index(algorithm)
        await self._upsert_user_variant_index(user_id, self.variant_index)

    async def get_variant(self, user_id: "UserIdType") -> Optional[Variant]:
        self._check_variants()
        if not self.is_enabled:
            return None
        await self.set_variant_index_for_user(user_id)
        return self.variants[self.variant_index]

    def has_pick(self, symbol: object) -> bool:
        self._check_variants()
        return symbol in self.variants[0].picks

    def pick(self, symbol: object, type_of_pick: Type[PickType]) -> PickType:
        self._check_variants()
        variant_index = self.variant_index or 0
        value = self.variants[variant_index].get_pick(symbol)
        if value is None:
            raise RuntimeError(f"`unable to find {symbol}")
        if not isinstance(value, type_of_pick):
            raise TypeError(f"Expected type {type_of_pick}, but got {value} for symbol {symbol}")
        return value

    async def enable(self) -> None:
        experiment = await self.get_experiment()
        if not experiment:
            experiment = await self.upsert_experiment(self)
        new_algorithm = await self.get_algorithm()
        await self.upsert_algorithm(new_algorithm)
        experiment.is_enabled = True
        await self.upsert_experiment(experiment)

    async def disable(self) -> None:
        experiment = await self.get_experiment()
        if not experiment:
            raise ValueError("Experiment not found")
        await self.delete_user_variants()
        await self.delete_experiment(self)
        await self.delete_algorithm()
        self.reset()