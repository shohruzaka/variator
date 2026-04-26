"""Sozlamalarni o'qish (9-bosqich).

Bu modul `config.yaml` faylidan standart qiymatlarni o'qiydi.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    """Loyiha sozlamalari."""

    variants_count: int = 5
    questions_per_variant: int | None = None
    base_seed: int = 42
    output_dir: str = "output"

    @classmethod
    def load(cls, config_path: str | Path = "config.yaml") -> "Config":
        """YAML fayldan sozlamalarni o'qiydi. Agar fayl yo'q bo'lsa, default qaytaradi."""
        path = Path(config_path)
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            try:
                data: dict[str, Any] = yaml.safe_load(f) or {}
            except yaml.YAMLError:
                data = {}

        return cls(
            variants_count=data.get("variants_count", 5),
            questions_per_variant=data.get("questions_per_variant", None),
            base_seed=data.get("base_seed", 42),
            output_dir=data.get("output_dir", "output"),
        )
