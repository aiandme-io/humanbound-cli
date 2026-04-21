"""
Unit tests for the `hb test` command.

Mocked HumanboundClient — no live API needed.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from humanbound_cli.main import cli
from humanbound_cli.exceptions import NotAuthenticatedError, APIError
from conftest import (
    MOCK_EXPERIMENT, MOCK_EXPERIMENT_RUNNING, MOCK_FINDING, MOCK_FINDING_2,
    MOCK_LOG, MOCK_LOG_PASS, MOCK_PROVIDER, MOCK_POSTURE, MOCK_POSTURE_TRENDS,
    MOCK_PROJECT, assert_exit_ok, assert_exit_error,
    platform_runner,
)

RUNNER_PATCH = "humanbound_cli.commands.test.get_runner"
runner = CliRunner()


def _make_client(**overrides):
    m = MagicMock()
    m.is_authenticated.return_value = True
    m.organisation_id = "org-123"
    m.project_id = "proj-456"
    m._organisation_id = "org-123"
    m._project_id = "proj-456"
    m.base_url = "http://test.local/api"
    # Defaults for the test command flow
    m.list_providers.return_value = [MOCK_PROVIDER]
    m.post.return_value = {"id": "exp-new"}
    m.get.return_value = MOCK_PROJECT
    m.get_experiment_status.return_value = {"status": "Finished"}
    m.get_experiment.return_value = MOCK_EXPERIMENT
    m.list_findings.return_value = {"data": [MOCK_FINDING], "total": 1}
    m.get_posture_trends.return_value = {"data_points": []}
    for k, v in overrides.items():
        setattr(m, k, v)
    return m


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestHappyPath:
    @patch(RUNNER_PATCH)
    def test_basic_invocation(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test"])
        assert_exit_ok(result)
        assert "exp-new" in result.output
        mock.post.assert_called_once()

    @patch(RUNNER_PATCH)
    def test_wait_completes_immediately(self, mock_get_runner):
        mock = _make_client()
        mock.get_experiment_status.return_value = {"status": "Finished"}
        mock.get_experiment.return_value = {
            **MOCK_EXPERIMENT,
            "results": {"stats": {"total": 50, "pass": 36, "fail": 14}, "insights": []},
        }
        mock.get.side_effect = [
            MOCK_PROJECT,  # project check for default_integration
            MOCK_POSTURE,  # posture fetch in _display_results
        ]
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--wait"])
        assert_exit_ok(result)
        assert "Experiment Complete" in result.output or "exp-789" in result.output

    @patch(RUNNER_PATCH)
    def test_deep_flag_sets_system_level(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--deep"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("testing_level") == "system"

    @patch(RUNNER_PATCH)
    def test_full_flag_sets_acceptance_level(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--full"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("testing_level") == "acceptance"

    @patch(RUNNER_PATCH)
    def test_no_auto_start(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--no-auto-start"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("auto_start") is False


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestErrorCases:
    @patch(RUNNER_PATCH)
    def test_not_authenticated(self, mock_get_runner):
        mock = _make_client()
        mock.is_authenticated.return_value = False
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test"])
        assert result.exit_code != 0
        assert "Not authenticated" in result.output

    @patch(RUNNER_PATCH)
    def test_no_project(self, mock_get_runner):
        mock = _make_client()
        mock.project_id = None
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test"])
        assert result.exit_code != 0
        assert "No project selected" in result.output

    @patch(RUNNER_PATCH)
    def test_no_providers(self, mock_get_runner):
        mock = _make_client()
        mock.list_providers.return_value = []
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test"])
        assert result.exit_code != 0
        assert "No providers" in result.output

    @patch(RUNNER_PATCH)
    def test_api_error_on_creation(self, mock_get_runner):
        mock = _make_client()
        mock.post.side_effect = APIError("fail", 500)
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test"])
        assert result.exit_code != 0
        assert "fail" in result.output.lower() or "Error" in result.output


# ---------------------------------------------------------------------------
# Flags
# ---------------------------------------------------------------------------

class TestFlags:
    @patch(RUNNER_PATCH)
    def test_category_flag(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--category", "humanbound/behavioral/qa"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("test_category") == "humanbound/behavioral/qa"

    @patch(RUNNER_PATCH)
    def test_test_category_flag(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--test-category", "humanbound/behavioral/qa"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("test_category") == "humanbound/behavioral/qa"

    @patch(RUNNER_PATCH)
    def test_testing_level_flag(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--testing-level", "system"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("testing_level") == "system"

    @patch(RUNNER_PATCH)
    def test_name_flag(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--name", "my-experiment"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("name") == "my-experiment"

    @patch(RUNNER_PATCH)
    def test_description_flag(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--description", "My test run"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("description") == "My test run"

    @patch(RUNNER_PATCH)
    def test_lang_code_conversion(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--lang", "de"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        assert payload.get("lang") == "german"

    @patch(RUNNER_PATCH)
    def test_endpoint_json_string(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        endpoint_json = '{"chat_completion":{"endpoint":"https://bot.example.com"}}'
        result = runner.invoke(cli, ["test", "--endpoint", endpoint_json])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        config = payload.get("configuration", {})
        assert "integration" in config

    @patch(RUNNER_PATCH)
    def test_context_string(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--context", "Authenticated as Alice"])
        assert_exit_ok(result)
        call_data = mock.post.call_args
        payload = call_data[1].get("data", call_data[0][1] if len(call_data[0]) > 1 else {})
        config = payload.get("configuration", {})
        assert config.get("context") == "Authenticated as Alice"

    @patch(RUNNER_PATCH)
    def test_fail_on_flag(self, mock_get_runner):
        mock = _make_client()
        mock.get_experiment.return_value = {
            **MOCK_EXPERIMENT,
            "results": {
                "stats": {"total": 50, "pass": 36, "fail": 14},
                "insights": [{"severity": "high", "explanation": "bad"}],
            },
        }
        mock.get.side_effect = [
            MOCK_PROJECT,  # project check
            MOCK_POSTURE,  # posture in _display_results
        ]
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test", "--wait", "--fail-on", "high"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

class TestOutputFormat:
    @patch(RUNNER_PATCH)
    def test_help_text(self, mock_get_runner):
        result = runner.invoke(cli, ["test", "--help"])
        assert_exit_ok(result)
        assert "security tests" in result.output.lower() or "test" in result.output.lower()

    @patch(RUNNER_PATCH)
    def test_output_includes_experiment_id(self, mock_get_runner):
        mock = _make_client()
        mock_get_runner.return_value = platform_runner(mock)
        result = runner.invoke(cli, ["test"])
        assert_exit_ok(result)
        assert "exp-new" in result.output
