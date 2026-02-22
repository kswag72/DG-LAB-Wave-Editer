from __future__ import annotations

import math
from collections.abc import Sequence

from src.domain.models import MAX_STEPS, Wave
from src.services.id_service import IdService

INTENSITY_MIN = 0
INTENSITY_MAX = 100
INTERVAL_MIN = 10
INTERVAL_MAX = 1000


class WaveService:
    def __init__(self, id_service: IdService) -> None:
        self._ids = id_service

    def create_wave(
        self,
        *,
        name: str,
        intervals: Sequence[int],
        intensities: Sequence[int],
        wave_id: str | None = None,
    ) -> Wave:
        return Wave(
            id=wave_id or self._ids.new_id(),
            name=name,
            intervals=tuple(intervals),
            intensities=tuple(intensities),
        )

    def clamp_intensity(self, value: int) -> int:
        return max(INTENSITY_MIN, min(INTENSITY_MAX, value))

    def clamp_interval(self, value: int) -> int:
        return max(INTERVAL_MIN, min(INTERVAL_MAX, value))

    def apply_generated_values(
        self,
        intervals: list[int],
        intensities: list[int],
        *,
        result: Sequence[int],
        target: int,
        range_lo: int,
        range_hi: int,
    ) -> tuple[list[int], list[int]]:
        for i in range(range_lo, range_hi + 1):
            if target == 0:
                intensities[i] = self.clamp_intensity(result[i])
            else:
                intervals[i] = self.clamp_interval(result[i])
        return intervals, intensities

    def smooth(self, intervals: list[int], intensities: list[int], steps: int) -> tuple[list[int], list[int]]:
        return self._smooth_array(intervals, steps), self._smooth_array(intensities, steps)

    def generate_values(
        self,
        *,
        wave_type: int,
        cycles: int,
        amplitude: int,
        steps: int,
        exponent: float = 2.0,
        coeff: float = 1.0,
        offset: float = 0.0,
        range_lo: int = 0,
        range_hi: int | None = None,
    ) -> list[int]:
        if range_hi is None:
            range_hi = steps - 1
        range_lo = max(0, min(range_lo, steps - 1))
        range_hi = max(range_lo, min(range_hi, steps - 1))
        span = range_hi - range_lo + 1

        result = [0] * steps
        for i in range(span):
            t = i / (span - 1) if span > 1 else 0
            v = self._compute_wave_value(wave_type, t, cycles, amplitude, exponent, coeff, offset)
            result[range_lo + i] = int(max(0, v))
        return result

    def _compute_wave_value(
        self,
        wave_type: int,
        t: float,
        cycles: int,
        amplitude: int,
        exponent: float,
        coeff: float,
        offset: float,
    ) -> float:
        if wave_type == 0:
            phase = t * cycles * math.pi * 2
            return (math.sin(phase - math.pi / 2) + 1) / 2 * amplitude + offset
        if wave_type == 1:
            phase = t * cycles * math.pi * 2
            return (amplitude if math.sin(phase) >= 0 else 0) + offset
        if wave_type == 2:
            return ((t * cycles) % 1) * amplitude + offset
        if wave_type == 3:
            return (1 - abs(((t * cycles) % 1) * 2 - 1)) * amplitude + offset
        if wave_type == 4:
            return coeff * (t**exponent) * amplitude + offset
        if wave_type == 5:
            return coeff * (t**2) * amplitude + exponent * t * amplitude + offset
        if wave_type == 6:
            if abs(exponent) < 0.01:
                return t * amplitude * coeff + offset
            return coeff * (math.exp(exponent * t) - 1) / (math.exp(exponent) - 1) * amplitude + offset
        if wave_type == 7:
            if abs(exponent) < 0.01:
                return t * amplitude * coeff + offset
            return coeff * math.log(1 + t * (math.e**exponent - 1)) / exponent * amplitude + offset
        if wave_type == 8:
            return amplitude * (1 - math.exp(-exponent * t * 5)) * coeff + offset
        if wave_type == 9:
            return amplitude * (0.5 + 0.5 * math.tanh((t - 0.5) * exponent * 4)) * coeff + offset
        return 0

    def _smooth_array(self, arr: list[int], length: int) -> list[int]:
        smoothed = list(arr)
        for i in range(1, length - 1):
            smoothed[i] = int(arr[i - 1] * 0.25 + arr[i] * 0.5 + arr[i + 1] * 0.25)
        return smoothed
