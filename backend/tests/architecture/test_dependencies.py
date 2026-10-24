import ast
import subprocess
import sys
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[2] / "app"


def imported_modules(path: Path) -> list[str]:
    names: list[str] = []
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


@pytest.mark.parametrize(
    ("layer", "forbidden"),
    [
        (
            "domain",
            (
                "app.application",
                "app.infrastructure",
                "app.api",
                "app.bootstrap",
                "fastapi",
                "sqlalchemy",
                "pydantic",
            ),
        ),
        (
            "application",
            ("app.infrastructure", "app.api", "app.bootstrap", "fastapi", "sqlalchemy"),
        ),
        ("api", ("app.infrastructure", "app.bootstrap", "sqlalchemy")),
        ("infrastructure", ("app.api", "app.bootstrap")),
    ],
)
def test_dependency_direction(layer: str, forbidden: tuple[str, ...]) -> None:
    violations = []
    for path in (APP / layer).rglob("*.py"):
        for name in imported_modules(path):
            if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden):
                violations.append(f"{path.relative_to(APP)} imports {name}")
    assert not violations, "\n".join(violations)


def test_domain_imports_without_framework_or_database() -> None:
    script = """
from uuid import uuid4
from datetime import UTC,datetime,timedelta
from app.domain.entities.reservation import Reservation
from app.domain.entities.slot import Slot
import sys
slot=Slot(uuid4(), datetime(2035,1,2,tzinfo=UTC),datetime(2035,1,3,tzinfo=UTC),1000)
reservation=Reservation.place(uuid4(),slot,datetime(2035,1,1,tzinfo=UTC))
reservation.cancel()
assert not any(name.startswith(('fastapi','sqlalchemy','pydantic')) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=APP.parent, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "legacy",
    [
        "domain/entities.py",
        "application/ports.py",
        "infrastructure/models.py",
        "infrastructure/repositories.py",
        "api/routes.py",
        "api/schemas.py",
    ],
)
def test_aggregate_modules_do_not_regress_into_shared_files(legacy: str) -> None:
    assert not (APP / legacy).exists()
