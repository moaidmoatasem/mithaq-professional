import sys
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

# Mock httpx to avoid ModuleNotFoundError
mock_httpx = MagicMock()
sys.modules["httpx"] = mock_httpx

from src.mithaq.autonomous_generated.misc.smartretrier import SmartRetrier

class TestSmartRetrier(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.base_url = "http://api.example.com"
        self.retrier = SmartRetrier(self.base_url, max_retries=2)

        # Setup httpx mocks
        self.mock_client = MagicMock()
        self.mock_client.get = AsyncMock()
        self.mock_client.__aenter__ = AsyncMock(return_value=self.mock_client)
        self.mock_client.__aexit__ = AsyncMock()
        mock_httpx.AsyncClient.return_value = self.mock_client
        mock_httpx.HTTPError = Exception

    async def test_fetch_data_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_client.get.return_value = mock_response

        response = await self.retrier.fetch_data("/test")

        self.assertEqual(response, mock_response)
        self.mock_client.get.assert_called_once_with("http://api.example.com/test")

    async def test_fetch_data_retry_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Fail once, then succeed
        self.mock_client.get.side_effect = [Exception("Network error"), mock_response]

        # Override sleep to speed up test
        with unittest.mock.patch("asyncio.sleep", return_value=None):
            response = await self.retrier.fetch_data("/test")

        self.assertEqual(response, mock_response)
        self.assertEqual(self.mock_client.get.call_count, 2)

    async def test_fetch_data_max_retries_reached(self):
        self.mock_client.get.side_effect = Exception("Persistent error")

        with unittest.mock.patch("asyncio.sleep", return_value=None):
            with self.assertRaisesRegex(Exception, "Max retries reached"):
                await self.retrier.fetch_data("/test")

        self.assertEqual(self.mock_client.get.call_count, 2)

if __name__ == "__main__":
    unittest.main()
