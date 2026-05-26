from __future__ import annotations

import hashlib
import json
from typing import Any


def build_generation_input_hash(context: dict[str, Any]) -> str:
    normalized = json.dumps(context, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
