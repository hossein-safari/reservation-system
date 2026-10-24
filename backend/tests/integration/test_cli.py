import sys

import pytest
from fastapi.testclient import TestClient

from app import cli


def test_admin_cli_uses_application_command(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    answers = iter(["CLI Administrator", "cli@example.com"])
    monkeypatch.setattr(sys, "argv", ["reservation", "create-admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(cli, "getpass", lambda _: "cli-password-123")
    cli.main()
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "cli@example.com",
            "password": "cli-password-123",
        },
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
    assert "cli-password-123" not in capsys.readouterr().out


def test_invalid_cli_input_does_not_echo_password(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["Name", "invalid-email"])
    monkeypatch.setattr(sys, "argv", ["reservation", "create-admin"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    monkeypatch.setattr(cli, "getpass", lambda _: "short")
    with pytest.raises(SystemExit) as failure:
        cli.main()
    assert "short" not in str(failure.value)
