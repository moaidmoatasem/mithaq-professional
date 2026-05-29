"""Tests for the canonical LATTICE bridge (cherenkov.core.lattice_bridge)."""

from unittest.mock import MagicMock, patch

import pytest

MODULE = "cherenkov.core.lattice_bridge"


@pytest.fixture(autouse=True)
def _reset_lattice_singleton():
    """Reset the module-level lazy client between tests."""
    import cherenkov.core.lattice_bridge as lb

    lb._client = None
    lb._collection_ready = False
    yield
    lb._client = None
    lb._collection_ready = False


@patch(f"{MODULE}._get_client")
@patch(f"{MODULE}._embed")
def test_embed_and_store_success(mock_embed, mock_get_client):
    from cherenkov.core.lattice_bridge import embed_and_store

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_embed.return_value = [0.1] * 384

    ok = embed_and_store(
        "fid-1", "XSS Reflected", "Input reflected", "https://t.com", "xss", "HIGH", "CWE-79"
    )

    assert ok is True
    mock_client.upsert.assert_called_once()


@patch(f"{MODULE}._get_client")
def test_embed_and_store_qdrant_offline(mock_get_client):
    from cherenkov.core.lattice_bridge import embed_and_store

    mock_get_client.return_value = None

    ok = embed_and_store("fid-2", "SQLi", "SQL injection", "https://t.com", "sqli", "CRITICAL")

    assert ok is False


@patch(f"{MODULE}._get_client")
@patch(f"{MODULE}._embed")
def test_query_similar_targets(mock_embed, mock_get_client):
    from cherenkov.core.lattice_bridge import query_similar_targets

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_embed.return_value = [0.1] * 384

    hit = MagicMock()
    hit.id = 123
    hit.score = 0.95
    hit.payload = {
        "finding_id": "abc",
        "title": "XSS",
        "target": "https://t.com",
        "scanner": "xss",
        "is_false_positive": False,
    }
    mock_client.search.return_value = [hit]

    results = query_similar_targets("XSS Reflected", "Input reflected", 5, True)

    assert len(results) == 1
    assert results[0].title == "XSS"
    assert results[0].score == 0.95


@patch(f"{MODULE}._get_client")
def test_query_similar_qdrant_offline(mock_get_client):
    from cherenkov.core.lattice_bridge import query_similar_targets

    mock_get_client.return_value = None

    results = query_similar_targets("test", "desc")

    assert results == []


@patch(f"{MODULE}._get_client")
def test_label_false_positive(mock_get_client):
    from cherenkov.core.lattice_bridge import label_false_positive

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    ok = label_false_positive("deadbeef12345678")

    assert ok is True
    mock_client.set_payload.assert_called_once()


@patch(f"{MODULE}._get_client")
def test_label_false_positive_qdrant_offline(mock_get_client):
    from cherenkov.core.lattice_bridge import label_false_positive

    mock_get_client.return_value = None

    ok = label_false_positive("deadbeef12345678")

    assert ok is False


@patch(f"{MODULE}._get_client")
def test_vector_count(mock_get_client):
    from cherenkov.core.lattice_bridge import vector_count

    mock_client = MagicMock()
    mock_info = MagicMock()
    mock_info.vectors_count = 42
    mock_client.get_collection.return_value = mock_info
    mock_get_client.return_value = mock_client

    assert vector_count() == 42


@patch(f"{MODULE}._get_client")
def test_vector_count_offline(mock_get_client):
    from cherenkov.core.lattice_bridge import vector_count

    mock_get_client.return_value = None

    assert vector_count() == 0
