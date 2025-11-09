"""
Utility script to export the FastAPI OpenAPI schema for frontend DTO sharing.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.main import app


def export_openapi(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    output_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")


if __name__ == "__main__":
    export_openapi(Path("shared/dtos/openapi.json"))
