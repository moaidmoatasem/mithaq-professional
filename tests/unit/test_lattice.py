"""Unit tests for the LATTICE adaptive learning bridge."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cherenkov.core.base_scanner import Finding, ScanResult, Severity


@pytest.mark.asyncio
async def test_embed_and_store_empty_findings():
    from cherenkov.ai.lattice import embed_and_store

    result = ScanResult(target="https://example.com", scanner_name="test", findings=[])
    count = await embed_and_store(result)
    assert count == 0


@pytest.mark.asyncio
async def test_embed_and_store_writes_vectors():
    from cherenkov.ai.lattice import embed_and_store

    result = ScanResult(
        target="https://bank.example.com",
        scanner_name="xss_scanner",
        findings=[
            Finding(
                title="Reflected XSS",
                severity=Severity.HIGH,
                description="Input reflected without encoding",
                cwe="CWE-79",
                remediation="Encode output",
            )
        ],
    )

    fake_vector = [0.1] * 768

    with (
        patch("cherenkov.ai.lattice._ablation") as mock_ablation,
        patch("httpx.AsyncClient") as mock_client_cls,
    ):
        mock_san = MagicMock()
        mock_san.success = True
        mock_san.sanitized = result.findings[0].model_dump()
        mock_ablation.sanitize.return_value = mock_san

        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        # collection exists
        mock_client.get.return_value = MagicMock(status_code=200)
        # embed returns vector
        mock_client.post.return_value = MagicMock(
            status_code=200, json=lambda: {"embedding": fake_vector}
        )
        # upsert succeeds
        mock_client.put.return_value = MagicMock(status_code=200)

        count = await embed_and_store(result)

    assert count == 1


@pytest.mark.asyncio
async def test_query_similar_targets_returns_empty_on_ollama_failure():
    from cherenkov.ai.lattice import query_similar_targets

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = MagicMock(status_code=500, json=lambda: {})

        results = await query_similar_targets("https://target.com")

    assert results == []


@pytest.mark.asyncio
async def test_label_false_positive():
    from cherenkov.ai.lattice import label_false_positive

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = MagicMock(status_code=200)

        ok = await label_false_positive("deadbeef12345678")

    assert ok is True
