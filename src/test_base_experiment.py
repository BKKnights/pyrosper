import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Optional, List, Self
from base_experiment import BaseExperiment, Variant, ExperimentType
from user_variant import UserVariant


class MockAlgorithm:
    pass

class MockExperiment(BaseExperiment[MockAlgorithm, Variant]):
    async def get_experiment(self) -> Optional[Self]:
        return self

    async def upsert_experiment(self, experiment: ExperimentType) -> Self:
        return type(self)(
            id=experiment.id,
            name=experiment.name,
            variants=experiment.variants,
            is_enabled=experiment.is_enabled,
            variant_index=experiment.variant_index,
        )

    async def delete_experiment(self, experiment: ExperimentType) -> None:
        pass

    async def get_user_variant(self, user_id: str, experiment_id: str) -> Optional[UserVariant]:
        pass

    async def upsert_user_variant(self, user_variant: UserVariant) -> None:
        pass

    async def delete_user_variant(self, user_variant: UserVariant) -> None:
        pass

    async def delete_user_variants(self) -> None:
        pass

    async def get_algorithm(self) -> MockAlgorithm:
        return MockAlgorithm()

    async def get_variant_index(self, algorithm: MockAlgorithm) -> int:
        return 0

    async def reward_algorithm(self, algorithm: MockAlgorithm, user_variant_index: int, score: float) -> MockAlgorithm:
        return MockAlgorithm()

    async def upsert_algorithm(self, algorithm: MockAlgorithm) -> None:
        pass

    async def delete_algorithm(self) -> None:
        pass

id: str
name: str
user_id: str
index: int
is_enabled: bool
user_variant: UserVariant
mock_algorithm: MockAlgorithm
variant1: Variant
variant2: Variant
variants: List[Variant]
variant_index: int
id: str
mock_experiment: MockExperiment

@pytest.fixture(autouse=True)
def setup_function():
    """
    Setup function to initialize the test environment.
    This function can be used to mock dependencies or set up any required state.
    """
    global id, name, user_id, index, is_enabled, user_variant, mock_algorithm, variant1, variant2, variants, variant_index, mock_experiment
    id = "456"
    name = "name"
    user_id = "123"
    index = 0
    is_enabled = True
    user_variant = UserVariant(experiment_id="", user_id=user_id, index=index)
    mock_algorithm = MockAlgorithm()
    variant1 = Variant("control set", {"foo": MagicMock()})
    variant2 = Variant("b", {"foo": MagicMock()})
    variants = [variant1, variant2]
    variant_index = 999999
    mock_experiment = MockExperiment(
        id=id,
        name=name,
        variants=variants,
        is_enabled=is_enabled,
        variant_index=variant_index,
    )


@pytest.mark.asyncio
async def test_complete_for_user_when_disabled(mocker):
    global mock_experiment, user_id
    mock_experiment.is_enabled = False
    mock_get_experiment = mocker.patch.object(mock_experiment, 'get_experiment', AsyncMock(return_value=mock_experiment))
    await mock_experiment.complete_for_user(user_id, 1)
    mock_get_experiment.assert_not_called()

@pytest.mark.asyncio
async def test_complete_for_user_when_enabled_and_no_experiment(mocker):
    global mock_experiment, user_id
    mock_experiment.is_enabled = True
    mock_get_experiment = mocker.patch.object(mock_experiment, 'get_experiment', AsyncMock(return_value=None))
    await mock_experiment.complete_for_user(user_id, 1)
    mock_get_experiment.assert_called()

@pytest.mark.asyncio
async def test_complete_for_user_when_enabled_and_user_variant_exists(mocker):
    global mock_experiment, user_id, mock_algorithm
    score = 1
    mock_experiment.is_enabled = True
    mocker.patch.object(mock_experiment, '_remove_index', AsyncMock(return_value=None))
    mocker.patch.object(mock_experiment, '_get_user_variant_index', AsyncMock(return_value=user_variant.index))
    mock_get_algorithm = mocker.patch.object(mock_experiment, 'get_algorithm', AsyncMock(return_value=mock_algorithm))
    mock_reward_algorithm = mocker.patch.object(mock_experiment, 'reward_algorithm', AsyncMock(return_value=mock_algorithm))
    await mock_experiment.complete_for_user(user_id, score)
    mock_get_algorithm.assert_called()
    mock_reward_algorithm.assert_called_with(mock_algorithm, user_variant.index, score)

@pytest.mark.asyncio
async def test_set_for_user_when_experiment_exists(mocker):
    global mock_experiment, user_id
    replacement_experiment = MockExperiment(
        name="replacement",
        variants=[Variant("control set", {"foo": MagicMock()}), Variant("b", {"foo": MagicMock()})],
        is_enabled=True,
        variant_index=0,
        id='123'
    )
    mocker.patch.object(mock_experiment, 'get_experiment', AsyncMock(return_value=replacement_experiment))
    await mock_experiment.set_for_user()
    assert mock_experiment.is_enabled
    assert mock_experiment.id == replacement_experiment.id

@pytest.mark.asyncio
async def test_set_for_user_when_no_experiment(mocker):
    global mock_experiment, user_id
    mocker.patch.object(mock_experiment, 'get_experiment', AsyncMock(return_value=None))
    await mock_experiment.set_for_user()
    assert mock_experiment.is_enabled == False
    assert mock_experiment.id is None

def test_use_variant_when_variant_not_found():
    global mock_algorithm
    with pytest.raises(ValueError):
        mock_experiment.use_variant("nonexistent")

def test_use_variant_when_variant_found():
    global mock_experiment, variant1, variant2
    assert mock_experiment.variant_index != 1
    mock_experiment.use_variant("b")
    assert mock_experiment.variant_index == 1

def test_safe_enable():
    global mock_experiment
    mock_experiment.safe_enable()
    assert mock_experiment.is_enabled == True

def test_safe_disable():
    global mock_experiment
    mock_experiment.safe_disable()
    assert mock_experiment.is_enabled == False

@pytest.mark.asyncio
async def test_set_variant_index_for_user_when_disabled_w_user_id_false(mocker):
    global mock_experiment, mock_algorithm
    mock_experiment.is_enabled = False
    variant_index = mock_experiment.variant_index = 42
    mock_get_variant_index = mocker.patch.object(mock_experiment, 'get_variant_index', AsyncMock(return_value=42))
    await mock_experiment.set_variant_index_for_user()

    assert mock_experiment.variant_index == variant_index
    mock_get_variant_index.assert_called_once()

@pytest.mark.asyncio
async def test_set_variant_index_for_user_when_disabled_w_user_id_true_w_existing_experiment_w_no_user_variant_return(mocker):
    global mock_experiment, mock_algorithm, user_id, variant_index
    variant_index = 3
    mock_get_variant_index = mocker.patch.object(mock_experiment, 'get_variant_index', AsyncMock(return_value=variant_index))
    await mock_experiment.set_variant_index_for_user(user_id)
    mock_get_variant_index.assert_called_once()
    assert mock_experiment.variant_index == 3

@pytest.mark.asyncio
async def test_set_variant_index_for_user_when_disabled_w_user_id_true_w_existing_experiment_w_no_user_variant_upserts_user_variant(mocker):
    global mock_experiment, mock_algorithm, user_id, variant_index
    variant_index = 4
    mock_upsert_user_variant = mocker.patch.object(mock_experiment, '_upsert_user_variant_index', AsyncMock(return_value=42))
    mock_get_variant_index = mocker.patch.object(mock_experiment, 'get_variant_index', AsyncMock(return_value=variant_index))
    await mock_experiment.set_variant_index_for_user(user_id)
    mock_upsert_user_variant.assert_called_once_with(user_id, variant_index)
    assert mock_experiment.variant_index == 4

@pytest.mark.asyncio
async def test_set_variant_index_for_user_when_disabled_w_user_id_true_w_existing_experiment_w_sets_variant_index(mocker):
    global mock_experiment, mock_algorithm, user_id
    variant_index = mock_experiment.variant_index = 2
    mock_get_variant_index = mocker.patch.object(mock_experiment, 'get_variant_index', AsyncMock(return_value=variant_index))
    await mock_experiment.set_variant_index_for_user(user_id)
    mock_get_variant_index.assert_called_once()
    assert mock_experiment.variant_index == 2

@pytest.mark.asyncio
async def test_set_variant_index_for_user_when_disabled_w_user_id_true_w_existing_experiment_w_calls_get_user_variant(mocker):
    global mock_experiment, mock_algorithm, user_id, variant_index
    experiment_id = '456'
    variant_index = mock_experiment.variant_index = 2
    user_variant = UserVariant(
        id='123',
        experiment_id=experiment_id,
        user_id=user_id,
        index=variant_index,
    )
    mock_get_variant_index = mocker.patch.object(mock_experiment, 'get_variant_index', AsyncMock(return_value=variant_index))
    mocker.patch.object(mock_experiment, '_get_user_variant_index', AsyncMock(return_value=None))
    mocker.patch.object(mock_experiment, 'get_user_variant', AsyncMock(return_value=user_variant))
    mocker.patch.object(mock_experiment, 'get_experiment', AsyncMock(return_value=mock_experiment))
    mocker.patch.object(mock_experiment, 'get_algorithm', AsyncMock(return_value=mock_algorithm))
    mock_upsert_user_variant = mocker.patch.object(mock_experiment, 'upsert_user_variant', AsyncMock(return_value=None))
    await mock_experiment.set_variant_index_for_user(user_id)
    mock_get_variant_index.assert_called_once_with(mock_algorithm)
    mock_upsert_user_variant.assert_called_once_with(
        user_variant=user_variant,
    )

@pytest.mark.asyncio
async def test_get_variant_when_disabled():
    mock_experiment.is_enabled = False
    result = await mock_experiment.get_variant(user_id)
    assert result is None

@pytest.mark.asyncio
async def test_get_variant_when_enabled():
    global mock_experiment, user_id, variant1
    mock_experiment.is_enabled = True
    result = await mock_experiment.get_variant(user_id)
    assert result == variant1
