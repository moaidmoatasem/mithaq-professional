import os
import sys
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.ai_generated

# Add src to Python path
sys.path.insert(0, os.path.abspath("src"))

from cherenkov.autonomous_generated.api.slackdiscordconnector import SlackDiscordConnector


class TestSlackDiscordConnector:
    def test_parse_integrations(self):
        connector = SlackDiscordConnector()
        connector.parse_integrations({"SLACK_API_TOKEN": "test_token", "DISCORD_WEBHOOK_URL": ""})
        assert connector.slack_enabled is True
        assert connector.discord_enabled is False

    def test_check_status_slack_success(self):
        # We need to mock sys.modules['slack_sdk'] and 'discord_webhook' so that check_status doesn't fail on import
        mock_slack_sdk = MagicMock()
        mock_discord_webhook = MagicMock()

        mock_client = mock_slack_sdk.WebClient.return_value
        mock_client.test_api_call.return_value = {"ok": True}

        with patch.dict(
            "sys.modules", {"slack_sdk": mock_slack_sdk, "discord_webhook": mock_discord_webhook}
        ):
            connector = SlackDiscordConnector()
            connector.SLACK_API_TOKEN = "actual_valid_token"
            connector.check_status()

            # The token shouldn't be overwritten to 'Valid Token'
            assert connector.SLACK_API_TOKEN == "actual_valid_token"
            assert connector.slack_enabled is True

    def test_check_status_slack_env_token(self):
        mock_slack_sdk = MagicMock()
        mock_discord_webhook = MagicMock()

        mock_client = mock_slack_sdk.WebClient.return_value
        mock_client.test_api_call.return_value = {"ok": True}

        with patch.dict(
            "sys.modules", {"slack_sdk": mock_slack_sdk, "discord_webhook": mock_discord_webhook}
        ):
            with patch.dict(os.environ, {"SLACK_API_TOKEN": "env_token"}):
                connector = SlackDiscordConnector()
                connector.check_status()

                assert connector.SLACK_API_TOKEN == "env_token"
                assert connector.slack_enabled is True
