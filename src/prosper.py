from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Set, TypeVar, Any
from base_experiment import BaseExperiment


T = TypeVar('T')
ExperimentType = TypeVar('ExperimentType', bound='BaseExperiment')


class Prosper(Generic[ExperimentType]):
    def __init__(self):
        self.experiments: List[ExperimentType] = []
        self.used_symbols: Set[object] = set()

    async def set_for_user(self, user_id: Optional[str] = None) -> None:
        for experiment in self.experiments:
            await experiment.set_for_user(user_id)

    def has_pick(self, symbol: object) -> bool:
        return any(experiment.has_pick(symbol) for experiment in self.experiments)

    def pick(self, symbol: object) -> T:
        for experiment in self.experiments:
            if experiment.has_pick(symbol):
                return experiment.pick(symbol)
        raise ValueError(f"Unable to find {symbol}")

    def validate(self, experiment: ExperimentType) -> Set[object]:
        if any(existing_experiment.name == experiment.name for existing_experiment in self.experiments):
            raise ValueError(f'Experiment name "{experiment.name}" already used')

        pick_symbols = set(experiment.variants[0].picks.keys())
        for variant in experiment.variants[1:]:
            variant_pick_symbols = set(variant.picks.keys())
            if variant_pick_symbols != pick_symbols:
                raise ValueError(
                    f'Variant "{variant.name}" contains picks not in "{experiment.variants[0].name}"'
                )

        for symbol in pick_symbols:
            if symbol in self.used_symbols:
                raise ValueError(f'Variant pick name {symbol} already used')

        return pick_symbols

    def with_experiment(self, experiment: ExperimentType) -> 'Prosper':
        new_symbols = self.validate(experiment)
        self.experiments.append(experiment)
        self.used_symbols.update(new_symbols)
        return self

    def get_experiment(self, experiment_name: str) -> ExperimentType:
        for experiment in self.experiments:
            if experiment.name == experiment_name:
                return experiment
        raise ValueError(f'Experiment "{experiment_name}" not found')

    def experiment_exists(self, experiment_name: str) -> bool:
        try:
            self.get_experiment(experiment_name)
            return True
        except ValueError:
            return False

    def check_experiment_has_variant(self, experiment_name: str, variant_name: str) -> None:
        experiment = self.get_experiment(experiment_name)
        variant_names = {variant.name for variant in experiment.variants}
        if variant_name not in variant_names:
            raise ValueError(f'Variant "{variant_name}" does not exist in Experiment "{experiment_name}".')


def pick(service_identifier: object):
    def decorator(target: Any, target_key: str):
        def getter(self):
            prosper = getattr(self, 'prosper', None)
            if prosper is None:
                raise ValueError('.prosper property missing')
            if not prosper.has_pick(service_identifier):
                raise ValueError(f'Pick {service_identifier} is not available')
            return prosper.pick(service_identifier)

        setattr(target, target_key, property(getter))
    return decorator