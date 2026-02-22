from __future__ import annotations

import math
from collections.abc import Sequence

from src.domain.models import GapItem, SequenceEntry, Wave, WaveItem
from src.services.id_service import IdService
from src.services.wave_service import WaveService

GAP_STEP_MS = 100
GAP_INTERVAL = 10
GAP_INTENSITY = 0


class SequenceService:
    def __init__(self, id_service: IdService, wave_service: WaveService) -> None:
        self._ids = id_service
        self._waves = wave_service

    def merge_to_wave(self, items: Sequence[SequenceEntry], *, name: str = "合成素材") -> Wave:
        intervals: list[int] = []
        intensities: list[int] = []

        for entry in items:
            if isinstance(entry, WaveItem):
                intervals.extend(entry.wave.intervals)
                intensities.extend(entry.wave.intensities)
            else:
                gap_steps = self._gap_steps(entry.ms)
                intervals.extend([GAP_INTERVAL] * gap_steps)
                intensities.extend([GAP_INTENSITY] * gap_steps)

        return self._waves.create_wave(
            name=name,
            intervals=intervals,
            intensities=intensities,
        )

    def build_pulse_lines(self, items: Sequence[SequenceEntry]) -> list[str]:
        lines: list[str] = []
        for entry in items:
            if isinstance(entry, WaveItem):
                wave = entry.wave
                for i in range(wave.steps):
                    interval_hex = hex(wave.intervals[i])[2:].upper().zfill(2) * 4
                    intensity_hex = hex(wave.intensities[i])[2:].upper().zfill(2) * 4
                    lines.append(f"{interval_hex}{intensity_hex}")
            else:
                gap_steps = self._gap_steps(entry.ms)
                lines.extend(["0A0A0A0A00000000"] * gap_steps)
        return lines

    def format_pulse_export(self, items: Sequence[SequenceEntry]) -> str:
        lines = self.build_pulse_lines(items)
        quoted_lines = [f"'{line}'" for line in lines]
        separator = ",\n    "
        pulse_id = self._ids.new_id()
        return (
            f"{{\n  id: '{pulse_id}',\n  name: '导出结果',\n  pulseData: [\n    {separator.join(quoted_lines)}\n  ]\n}}"
        )

    def _gap_steps(self, ms: int) -> int:
        return math.ceil(ms / GAP_STEP_MS) if ms > 0 else 0
