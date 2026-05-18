from unittest.mock import MagicMock, patch

import pytest
from cherenkov.ai.lattice_bridge import (
    COLLECTION,
    MODEL_NAME,
    QDRANT_URL,
    _ensure_collection,
    embed_and_store,
    label_false_positive,
    query_similar_targets,
)
from qdrant_client.models import Distance, VectorParams


def test_ensure_collection_exists():
    client = MagicMock()
    _ensure_collection(client)
    client.get_collection.assert_called_once_with(COLLECTION)
    client.create_collection.assert_not_called()


def test_ensure_collection_not_exists():
    client = MagicMock()
    client.get_collection.side_effect = Exception("Not found")
    _ensure_collection(client)
    client.get_collection.assert_called_once_with(COLLECTION)
    client.create_collection.assert_called_once_with(
        COLLECTION, vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )


@pytest.mark.asyncio
@patch("cherenkov.ai.lattice_bridge._get_client")
@patch("cherenkov.ai.lattice_bridge._get_model")
@patch("cherenkov.ai.lattice_bridge._ensure_collection")
async def test_embed_and_store(mock_ensure, mock_get_model, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_model = MagicMock()
    mock_encoded = MagicMock()
    mock_encoded.tolist.return_value = [0.1, 0.2, 0.3]
    mock_model.encode.return_value = mock_encoded
    mock_get_model.return_value = mock_model

    trace = {"findings": "XSS found", "trace_id": "test_trace_123"}
    point_id = await embed_and_store(trace)

    mock_ensure.assert_called_once_with(mock_client)
    mock_model.encode.assert_called_once_with("XSS found")

    mock_client.upsert.assert_called_once()
    call_args = mock_client.upsert.call_args
    assert call_args[0][0] == COLLECTION
    points = call_args[1]["points"]
    assert len(points) == 1
    assert points[0].vector == [0.1, 0.2, 0.3]
    assert points[0].payload == trace

    assert str(points[0].id) == point_id


@pytest.mark.asyncio
@patch("cherenkov.ai.lattice_bridge._get_client")
@patch("cherenkov.ai.lattice_bridge._get_model")
async def test_query_similar_targets_success(mock_get_model, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_model = MagicMock()
    mock_encoded = MagicMock()
    mock_encoded.tolist.return_value = [0.4, 0.5, 0.6]
    mock_model.encode.return_value = mock_encoded
    mock_get_model.return_value = mock_model

    mock_result1 = MagicMock()
    mock_result1.payload = {"target": "test1"}
    mock_result2 = MagicMock()
    mock_result2.payload = {"target": "test2"}
    mock_client.search.return_value = [mock_result1, mock_result2]

    results = await query_similar_targets("test query", limit=2)

    mock_model.encode.assert_called_once_with("test query")
    mock_client.search.assert_called_once_with(COLLECTION, query_vector=[0.4, 0.5, 0.6], limit=2)
    assert results == [{"target": "test1"}, {"target": "test2"}]


@pytest.mark.asyncio
@patch("cherenkov.ai.lattice_bridge._get_client")
@patch("cherenkov.ai.lattice_bridge._get_model")
async def test_query_similar_targets_exception(mock_get_model, mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_model = MagicMock()
    mock_get_model.return_value = mock_model

    mock_client.search.side_effect = Exception("Qdrant Error")

    results = await query_similar_targets("test query")

    assert results == []


@pytest.mark.asyncio
@patch("cherenkov.ai.lattice_bridge._get_client")
async def test_label_false_positive_success(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    await label_false_positive("12345")

    mock_client.set_payload.assert_called_once_with(
        COLLECTION, payload={"is_false_positive": True}, points=[12345]
    )


@pytest.mark.asyncio
@patch("cherenkov.ai.lattice_bridge._get_client")
async def test_label_false_positive_exception(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.set_payload.side_effect = Exception("Update Error")

    # Should not raise exception
    await label_false_positive("12345")
    mock_client.set_payload.assert_called_once()
