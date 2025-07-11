"""Module to create openapi.json file"""

import json
import os
from pathlib import Path

import toml
from fastapi.openapi.utils import get_openapi


def load_env_from_toml(toml_path):
    """Load pytest env from pyproject.toml file"""
    config = toml.load(toml_path)
    env_vars = dict(
        [
            (row.split("=")[0], row.split("=")[1])
            for row in config.get("tool", dict())
            .get("pytest")
            .get("ini_options")
            .get("env")
        ]
    )
    for key, value in env_vars.items():
        os.environ[key] = str(value)


if __name__ == "__main__":
    env_toml_path = os.getenv(
        "TOML_PATH",
        Path("aind-metadata-service-server") / "pyproject.toml",
    )
    load_env_from_toml(env_toml_path)
    from aind_metadata_service_server.main import app

    specs = get_openapi(
        title=app.title if app.title else None,
        version=app.version if app.version else None,
        openapi_version=app.openapi_version if app.openapi_version else None,
        description=app.description if app.description else None,
        routes=app.routes if app.routes else None,
    )
    with open("openapi.json", "w") as f:
        json.dump(specs, f)
