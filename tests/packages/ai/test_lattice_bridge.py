import pytest
from unittest.mock import patch, MagicMock

from cherenkov.ai.lattice_bridge import embed_and_store, query_similar_targets, label_false_positive

@pytest.mark.asyncio
@patch('cherenkov.ai.lattice_bridge._client')
@patch('cherenkov.ai.lattice_bridge._model')
async def test_embed_and_store_success(mock_model, mock_client):
    mock_qdrant = MagicMock()
    mock_client.return_value = mock_qdrant

    mock_sentence_model = MagicMock()
    mock_sentence_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    mock_model.return_value = mock_sentence_model

    trace = {"findings": "test findings", "trace_id": "123"}
    pid = await embed_and_store(trace)

    assert pid != ""
    mock_qdrant.upsert.assert_called_once()
    mock_qdrant.get_collection.assert_called_once()

@pytest.mark.asyncio
@patch('cherenkov.ai.lattice_bridge._client')
@patch('cherenkov.ai.lattice_bridge._model')
async def test_query_similar_targets_success(mock_model, mock_client):
    mock_qdrant = MagicMock()

    mock_result = MagicMock()
    mock_result.payload = {"id": 1, "target": "test"}
    mock_qdrant.search.return_value = [mock_result]

    mock_client.return_value = mock_qdrant

    mock_sentence_model = MagicMock()
    mock_sentence_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    mock_model.return_value = mock_sentence_model

    results = await query_similar_targets("test target", limit=1)

    assert len(results) == 1
    assert results[0] == {"id": 1, "target": "test"}
    mock_qdrant.search.assert_called_once()

@pytest.mark.asyncio
@patch('cherenkov.ai.lattice_bridge._client')
async def test_label_false_positive_success(mock_client):
    mock_qdrant = MagicMock()
    mock_client.return_value = mock_qdrant

    await label_false_positive("12345")

    mock_qdrant.set_payload.assert_called_once()
    _, kwargs = mock_qdrant.set_payload.call_args
    assert kwargs['payload'] == {'is_false_positive': True}
    assert kwargs['points'] == [12345]

@pytest.mark.asyncio
@patch('cherenkov.ai.lattice_bridge._client')
async def test_graceful_qdrant_failure(mock_client):
    mock_client.side_effect = Exception("Connection refused")

    pid = await embed_and_store({"findings": "test"})
    assert pid == ""

    results = await query_similar_targets("test target")
    assert results == []

    # Should not raise exception
    await label_false_positive("12345")
