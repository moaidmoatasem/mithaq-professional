import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock sys.modules for qdrant_client and sentence_transformers
mock_qdrant = MagicMock()
mock_st = MagicMock()
sys.modules["qdrant_client"] = mock_qdrant
sys.modules["qdrant_client.models"] = mock_qdrant.models
sys.modules["sentence_transformers"] = mock_st

from cherenkov.ai.lattice_bridge import embed_and_store, label_false_positive, query_similar_targets


@pytest.mark.asyncio
@patch("qdrant_client.QdrantClient")
@patch("sentence_transformers.SentenceTransformer")
async def test_embed_and_store(mock_sentence_transformer, mock_qdrant_client):
    # Setup mocks
    mock_st_instance = MagicMock()
    mock_sentence_transformer.return_value = mock_st_instance
    mock_st_instance.encode.return_value = MagicMock()
    mock_st_instance.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]

    mock_qc_instance = MagicMock()
    mock_qdrant_client.return_value = mock_qc_instance

    # Also mock PointStruct
    mock_point_struct = MagicMock()
    sys.modules["qdrant_client.models"].PointStruct = mock_point_struct

    trace = {"findings": "test finding"}

    # Call the function
    point_id = await embed_and_store(trace)

    # Verify
    mock_sentence_transformer.assert_called_once_with("all-MiniLM-L6-v2")
    mock_st_instance.encode.assert_called_once_with("test finding")

    mock_qdrant_client.assert_called_once_with(url="http://localhost:6333")
    mock_qc_instance.upsert.assert_called_once()

    args, kwargs = mock_qc_instance.upsert.call_args
    assert args[0] == "cherenkov_findings"
    assert "points" in kwargs

    assert isinstance(point_id, str)
    assert len(point_id) > 0


@pytest.mark.asyncio
@patch("qdrant_client.QdrantClient")
@patch("sentence_transformers.SentenceTransformer")
async def test_query_similar_targets(mock_sentence_transformer, mock_qdrant_client):
    # Setup mocks
    mock_st_instance = MagicMock()
    mock_sentence_transformer.return_value = mock_st_instance
    mock_st_instance.encode.return_value = MagicMock()
    mock_st_instance.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]

    mock_qc_instance = MagicMock()
    mock_qdrant_client.return_value = mock_qc_instance

    mock_result_1 = MagicMock()
    mock_result_1.payload = {"key": "value1"}
    mock_result_2 = MagicMock()
    mock_result_2.payload = {"key": "value2"}

    mock_qc_instance.search.return_value = [mock_result_1, mock_result_2]

    # Call the function
    results = await query_similar_targets("target url")

    # Verify
    mock_sentence_transformer.assert_called_once_with("all-MiniLM-L6-v2")
    mock_st_instance.encode.assert_called_once_with("target url")

    mock_qdrant_client.assert_called_once_with(url="http://localhost:6333")
    mock_qc_instance.search.assert_called_once_with(
        "cherenkov_findings", query_vector=[0.1, 0.2, 0.3], limit=5
    )

    assert results == [{"key": "value1"}, {"key": "value2"}]


@pytest.mark.asyncio
@patch("qdrant_client.QdrantClient")
@patch("sentence_transformers.SentenceTransformer")
async def test_query_similar_targets_exception(mock_sentence_transformer, mock_qdrant_client):
    # Setup mocks
    mock_st_instance = MagicMock()
    mock_sentence_transformer.return_value = mock_st_instance
    mock_st_instance.encode.return_value = MagicMock()
    mock_st_instance.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]

    mock_qc_instance = MagicMock()
    mock_qdrant_client.return_value = mock_qc_instance

    # Simulate exception in search
    mock_qc_instance.search.side_effect = Exception("Search error")

    # Call the function
    results = await query_similar_targets("target url")

    # Verify empty list is returned on exception
    assert results == []


@pytest.mark.asyncio
@patch("qdrant_client.QdrantClient")
async def test_label_false_positive(mock_qdrant_client):
    # Setup mock
    mock_qc_instance = MagicMock()
    mock_qdrant_client.return_value = mock_qc_instance

    finding_id = "test-finding-id"

    # Call the function
    await label_false_positive(finding_id)

    # Verify
    mock_qdrant_client.assert_called_once_with(url="http://localhost:6333")
    mock_qc_instance.set_payload.assert_called_once_with(
        "cherenkov_findings", payload={"is_false_positive": True}, points=[finding_id]
    )


@pytest.mark.asyncio
@patch("qdrant_client.QdrantClient")
async def test_label_false_positive_exception(mock_qdrant_client):
    # Setup mock
    mock_qc_instance = MagicMock()
    mock_qdrant_client.return_value = mock_qc_instance

    # Simulate exception
    mock_qc_instance.set_payload.side_effect = Exception("Payload error")

    finding_id = "test-finding-id"

    # Call the function (should not raise)
    try:
        await label_false_positive(finding_id)
    except Exception as e:
        pytest.fail(f"Exception was not caught: {e}")
