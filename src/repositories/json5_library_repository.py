from __future__ import annotations

import json
import re
from collections.abc import Sequence

from src.domain.models import Wave
from src.services.id_service import IdService


class Json5LibraryRepository:
    def __init__(self, id_service: IdService) -> None:
        self._ids = id_service

    def load(self, path: str) -> list[Wave]:
        content = self._read_text(path)
        return self.parse(content)

    def save(self, path: str, waves: Sequence[Wave]) -> None:
        content = self.format(waves)
        self._write_text(path, content)

    def parse(self, content: str) -> list[Wave]:
        clean = re.sub(r"//.*", "", content)
        clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)
        clean = re.sub(r"([a-zA-Z0-9_]+):", r'"\1":', clean)
        clean = clean.replace("'", '"')
        clean = re.sub(r",(\s*[\]}])", r"\1", clean)

        data = json.loads(clean)
        waves: list[Wave] = []
        for item in data:
            pulse_data = item["pulseData"]
            intervals = tuple(int(p[0:2], 16) for p in pulse_data)
            intensities = tuple(int(p[8:10], 16) for p in pulse_data)
            waves.append(
                Wave(
                    id=item.get("id", self._ids.new_id()),
                    name=item.get("name", "导入波形"),
                    intervals=intervals,
                    intensities=intensities,
                )
            )
        return waves

    def format(self, waves: Sequence[Wave]) -> str:
        items: list[str] = []
        for wave in waves:
            pulse_entries = [
                f"'{hex(wave.intervals[i])[2:].upper().zfill(2) * 4}"
                f"{hex(wave.intensities[i])[2:].upper().zfill(2) * 4}'"
                for i in range(wave.steps)
            ]
            separator = ",\n      "
            items.append(
                "  {\n"
                f"    id: '{wave.id}',\n"
                f"    name: '{wave.name}',\n"
                "    pulseData: [\n"
                f"      {separator.join(pulse_entries)}\n"
                "    ]\n"
                "  }"
            )
        return "[\n" + ",\n".join(items) + "\n]"

    def _read_text(self, path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    def _write_text(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
