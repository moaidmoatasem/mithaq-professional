import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

pytestmark = pytest.mark.ai_generated

from cherenkov.autonomous_generated.misc.smartretrier import SmartRetrier


class TestSmartRetrier(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.base_url = "http://api.example.com"
        self.retrier = SmartRetrier(self.base_url, max_retries=2)

        # We will use patch to mock httpx.AsyncClient in the tests
        self.patcher = patch(
            "cherenkov.autonomous_generated.misc.smartretrier.httpx.AsyncClient",
            new_callable=MagicMock,
        )
        self.mock_async_client_class = self.patcher.start()

        self.mock_client = AsyncMock()
        self.mock_client.get = AsyncMock()
        self.mock_client.__aenter__ = AsyncMock(return_value=self.mock_client)
        self.mock_client.__aexit__ = AsyncMock()

        self.mock_async_client_class.return_value = self.mock_client

    async def asyncTearDown(self):
        self.patcher.stop()

    async def test_fetch_data_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_client.get.return_value = mock_response

        response = await self.retrier.fetch_data("/test")

        self.assertEqual(response, mock_response)
        self.mock_client.get.assert_called_once_with("http://api.example.com/test", timeout=10.0)

    async def test_fetch_data_retry_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Fail once, then succeed
        self.mock_client.get.side_effect = [httpx.RequestError("Network error"), mock_response]

        # Override sleep to speed up test
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            response = await self.retrier.fetch_data("/test")

        self.assertEqual(response, mock_response)
        self.assertEqual(self.mock_client.get.call_count, 2)

    async def test_fetch_data_max_retries_reached(self):
        self.mock_client.get.side_effect = httpx.RequestError("Persistent error")

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with self.assertRaisesRegex(Exception, "Max retries reached"):
                await self.retrier.fetch_data("/test")

        self.assertEqual(self.mock_client.get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
