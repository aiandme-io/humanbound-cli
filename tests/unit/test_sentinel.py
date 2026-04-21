"""
Unit tests for `hb sentinel` commands (connect, status, disconnect).

Sentinel has Azure deployment logic that's not mockable in unit tests,
so we focus on auth guards, help text, and the webhook-based commands.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from humanbound_cli.main import cli
from humanbound_cli.exceptions import NotAuthenticatedError, APIError
from conftest import platform_runner


runner = CliRunner()

RUNNER_PATCH = "humanbound_cli.commands.sentinel.get_runner"


def _make_mock_client(**overrides):
    mock = MagicMock()
    mock.is_authenticated.return_value = True
    mock.organisation_id = "org-123"
    mock.project_id = "proj-456"
    mock._organisation_id = "org-123"
    mock._project_id = "proj-456"
    mock._username = "tester"
    mock._email = "test@example.com"
    mock.base_url = "http://test.local/api"
    for k, v in overrides.items():
        setattr(mock, k, v)
    return mock


MOCK_WEBHOOK_RESULT = {
    "id": "wh-sentinel-001",
    "name": "Sentinel Connector",
    "url": "https://my-func.azurewebsites.net/api/webhook",
    "is_active": True,
    "event_types": [
        "finding.created",
        "finding.regressed",
        "posture.grade_changed",
    ],
}


class TestHappyPath:
    def test_sentinel_help(self):
        """sentinel --help shows group description."""
        result = runner.invoke(cli, ["sentinel", "--help"])
        assert result.exit_code == 0
        assert "sentinel" in result.output.lower()
        assert "connect" in result.output.lower()
        assert "status" in result.output.lower()
        assert "disconnect" in result.output.lower()

    def test_sentinel_connect_help(self):
        """sentinel connect --help shows --url option."""
        result = runner.invoke(cli, ["sentinel", "connect", "--help"])
        assert result.exit_code == 0
        assert "--url" in result.output
        assert "--secret" in result.output
        assert "--name" in result.output

    def test_sentinel_status_help(self):
        """sentinel status --help works."""
        result = runner.invoke(cli, ["sentinel", "status", "--help"])
        assert result.exit_code == 0

    @patch(RUNNER_PATCH)
    @patch("humanbound_cli.commands.sentinel._load_sentinel_config")
    @patch("humanbound_cli.commands.sentinel._save_sentinel_config")
    def test_connect_creates_webhook(self, mock_save, mock_load, MockClient):
        """connect --url creates a webhook and saves config."""
        mock = _make_mock_client()
        mock.create_webhook.return_value = MOCK_WEBHOOK_RESULT
        mock.test_webhook.return_value = {"status": "ok"}
        mock_get_runner.return_value = platform_runner(mock)
        mock_load.return_value = {}  # No existing connection

        result = runner.invoke(cli, [
            "sentinel", "connect",
            "--url", "https://my-func.azurewebsites.net/api/webhook",
            "--secret", "test-secret-123",
        ])
        assert result.exit_code == 0
        assert "wh-sentinel-001" in result.output or "Webhook created" in result.output
        mock.create_webhook.assert_called_once()
        call_kwargs = mock.create_webhook.call_args
        assert call_kwargs[1]["url"] == "https://my-func.azurewebsites.net/api/webhook"
        mock_save.assert_called_once()

    @patch(RUNNER_PATCH)
    @patch("humanbound_cli.commands.sentinel._load_sentinel_config")
    @patch("humanbound_cli.commands.sentinel._save_sentinel_config")
    def test_connect_auto_generates_secret(self, mock_save, mock_load, MockClient):
        """connect without --secret auto-generates one."""
        mock = _make_mock_client()
        mock.create_webhook.return_value = MOCK_WEBHOOK_RESULT
        mock.test_webhook.return_value = {"status": "ok"}
        mock_get_runner.return_value = platform_runner(mock)
        mock_load.return_value = {}

        result = runner.invoke(cli, [
            "sentinel", "connect",
            "--url", "https://my-func.azurewebsites.net/api/webhook",
        ])
        assert result.exit_code == 0
        # Secret should have been auto-generated (64 hex chars)
        call_kwargs = mock.create_webhook.call_args[1]
        assert len(call_kwargs["secret"]) == 64  # secrets.token_hex(32) = 64 chars


class TestErrorCases:
    @patch(RUNNER_PATCH)
    def test_connect_not_authenticated(self, mock_get_runner):
        """connect fails when not authenticated."""
        mock = _make_mock_client()
        mock.is_authenticated.return_value = False
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, [
            "sentinel", "connect",
            "--url", "https://example.com/webhook",
        ])
        assert result.exit_code != 0
        assert "Not authenticated" in result.output or "login" in result.output.lower()

    @patch(RUNNER_PATCH)
    def test_connect_no_org(self, mock_get_runner):
        """connect fails when no org selected."""
        mock = _make_mock_client(organisation_id=None, _organisation_id=None)
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, [
            "sentinel", "connect",
            "--url", "https://example.com/webhook",
        ])
        assert result.exit_code != 0
        assert "organisation" in result.output.lower() or "org" in result.output.lower()

    @patch(RUNNER_PATCH)
    @patch("humanbound_cli.commands.sentinel._load_sentinel_config")
    def test_connect_api_error(self, mock_load, MockClient):
        """connect handles APIError from create_webhook."""
        mock = _make_mock_client()
        mock.create_webhook.side_effect = APIError("Webhook limit reached", status_code=422)
        mock_get_runner.return_value = platform_runner(mock)
        mock_load.return_value = {}

        result = runner.invoke(cli, [
            "sentinel", "connect",
            "--url", "https://example.com/webhook",
            "--secret", "test",
        ])
        assert result.exit_code != 0

    @patch(RUNNER_PATCH)
    @patch("humanbound_cli.commands.sentinel._require_sentinel_config")
    def test_status_not_authenticated(self, mock_config, MockClient):
        """status fails when not authenticated."""
        mock = _make_mock_client()
        mock.is_authenticated.return_value = False
        mock_get_runner.return_value = platform_runner(mock)
        mock_config.return_value = {"webhook_id": "wh-001"}

        result = runner.invoke(cli, ["sentinel", "status"])
        assert result.exit_code != 0

    def test_connect_missing_url(self):
        """connect without --url fails."""
        result = runner.invoke(cli, ["sentinel", "connect"])
        assert result.exit_code != 0
        assert "url" in result.output.lower() or "Missing" in result.output or "required" in result.output.lower()
