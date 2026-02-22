from __future__ import annotations

from dataclasses import dataclass

MAX_STEPS = 100


@dataclass(frozen=True, slots=True)
class Wave:
    id: str
    name: str
    intervals: tuple[int, ...]
    intensities: tuple[int, ...]

    @property
    def steps(self) -> int:
        return len(self.intervals)

    def validate(self) -> None:
        if len(self.intervals) != len(self.intensities):
            msg = "intervals/intensities length mismatch"
            raise ValueError(msg)
        if not 1 <= self.steps <= MAX_STEPS:
            msg = f"steps out of range: {self.steps}"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class WaveItem:
    wave: Wave

    @property
    def name(self) -> str:
        return self.wave.name


@dataclass(frozen=True, slots=True)
class GapItem:
    ms: int
    label: str = "静默"

    @property
    def name(self) -> str:
        return self.label

    def validate(self) -> None:
        if self.ms < 0:
            msg = "gap ms must be >= 0"
            raise ValueError(msg)


SequenceEntry = WaveItem | GapItem


@dataclass(frozen=True, slots=True)
class RawSection:
    freq_start_ms: float
    freq_end_ms: float
    section_time: float
    freq_mode: str | bool
    pulse: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class RawConfig:
    sections: tuple[RawSection, ...]
    sleep_time: float
    speed_factor: int
