import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List
from .mock.mock_algorithm import MockAlgorithm
from .mock.mock_experiment import MockExperiment
from .mock.mock_variant import MockVariant
from .mock.mock_user_variant import MockUserVariant


id: str
name: str
user_id: str
index: int
is_enabled: bool
user_variant: MockUserVariant
mock_algorithm: MockAlgorithm
variant1: MockVariant
variant2: MockVariant
variants: List[MockVariant]
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
    user_variant = MockUserVariant(experiment_id="", user_id=user_id, index=index)
    mock_algorithm = MockAlgorithm()
    variant1 = MockVariant("control set", {"foo": MagicMock()})
    variant2 = MockVariant("b", {"foo": MagicMock()})
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
    user_variant = MockUserVariant(
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
    mock_experiment.variant_index = 0
    result = await mock_experiment.get_variant(user_id)
    assert result is None

@pytest.mark.asyncio
async def test_get_variant_when_enabled():
    global mock_experiment, user_id, variant1
    mock_experiment.is_enabled = True
    mock_experiment.variant_index = 0
    result = await mock_experiment.get_variant(user_id)
    assert result == variant1
