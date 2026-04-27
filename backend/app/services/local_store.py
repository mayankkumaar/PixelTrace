from __future__ import annotations

import json
from typing import Any

from app.core.config import settings


def write_json_record(category: str, record_id: str, data: dict[str, Any]) -> str:
    base = settings.data_dir / "records" / category
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{record_id}.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)
