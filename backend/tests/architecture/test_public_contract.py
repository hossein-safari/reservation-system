import json
from pathlib import Path

from app.config import Settings
from app.main import create_app


def test_refactor_preserves_public_openapi_contract() -> None:
    reference = Path(__file__).parent / "openapi.json"
    app = create_app(Settings(app_env="test", database_url="sqlite://"))
    try:
        assert app.openapi() == json.loads(reference.read_text())
    finally:
        app.state.container.close()
