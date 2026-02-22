from __future__ import annotations

import math

from src.domain.models import RawConfig, RawSection

_FREQ_TABLE: list[int] = []
_FREQ_TABLE.extend(range(10, 50, 1))
_FREQ_TABLE.extend(range(50, 80, 2))
_FREQ_TABLE.extend(range(80, 100, 5))
_FREQ_TABLE.extend(range(100, 200, 10))
_FREQ_TABLE.extend([200, 233, 266, 300, 333, 366])
_FREQ_TABLE.extend(range(400, 600, 50))
_FREQ_TABLE.extend(range(600, 1001, 100))

_PROTOCOL_PREFIX = "Dungeonlab+pulse:"
_SECTION_SEPARATOR = "+section+"
_ZERO_FRAME = "0A0A0A0A00000000"
_SUB_CYCLES = 4
_BASE_TICK_MS = 100


class ConversionService:
    """Bidirectional converter between Dungeonlab raw strings and V3 frame arrays."""

    def parse_raw(self, raw_str: str) -> RawConfig:
        data = raw_str
        if data.startswith(_PROTOCOL_PREFIX):
            data = data[len(_PROTOCOL_PREFIX) :]

        header_str, rest = data.split("=", 1)
        header = [int(x) for x in header_str.split(",")]

        sleep_code = header[0]
        speed_factor = header[1]

        if sleep_code == 0:
            sleep_time = 0.0
        else:
            sleep_time = math.floor((sleep_code - 1) / 10) / 10 + 0.1

        section_strs = rest.split(_SECTION_SEPARATOR)
        sections: list[RawSection] = []

        for sec_str in section_strs:
            params_str, kf_str = sec_str.split("/", 1)
            params = [int(x) for x in params_str.split(",")]

            points: list[float] = []
            for kf in kf_str.split(","):
                points.append(float(kf.split("-")[0]))

            freq_start = _FREQ_TABLE[params[0]] if params[0] < len(_FREQ_TABLE) else 10
            freq_end = _FREQ_TABLE[params[1]] if params[1] < len(_FREQ_TABLE) else 10
            section_time = params[2] * 0.1

            freq_mode_map: dict[int, str | bool] = {
                1: False,
                2: "inSection",
                3: "inPulse",
                4: "perPulse",
            }
            freq_mode = freq_mode_map.get(params[3], False)

            sections.append(
                RawSection(
                    freq_start_ms=float(freq_start),
                    freq_end_ms=float(freq_end),
                    section_time=section_time,
                    freq_mode=freq_mode,
                    pulse=tuple(points),
                )
            )

        return RawConfig(
            sections=tuple(sections),
            sleep_time=sleep_time,
            speed_factor=speed_factor,
        )

    def raw_to_v3(self, raw_str: str) -> list[str]:
        config = self.parse_raw(raw_str)
        return self._config_to_v3(config)

    def v3_to_raw(self, frames: list[str]) -> str:
        """Reconstruct a single-section raw string from V3 frames.

        The conversion is lossy: multi-section structure and freq-mode
        metadata cannot be recovered from flat V3 frames.
        """
        freq_values: list[float] = []
        intensity_values: list[float] = []

        for frame in frames:
            freq_byte = int(frame[0:2], 16)
            intensity_byte = int(frame[8:10], 16)
            freq_ms = self._decode_freq_byte(freq_byte)
            freq_values.append(freq_ms)
            intensity_values.append(float(intensity_byte))

        if not freq_values:
            return f"{_PROTOCOL_PREFIX}0,1,8=0,0,0,1,1/0-1"

        while intensity_values and intensity_values[-1] == 0.0:
            intensity_values.pop()
            freq_values.pop()

        if not intensity_values:
            return f"{_PROTOCOL_PREFIX}0,1,8=0,0,0,1,1/0-1"

        avg_freq = sum(freq_values) / len(freq_values)
        freq_idx = self._find_closest_freq_index(avg_freq)

        point_parts = [f"{v:.6g}-1" for v in intensity_values]
        duration = len(intensity_values)

        joined = ",".join(point_parts)
        return f"{_PROTOCOL_PREFIX}0,1,8={freq_idx},0,{duration},1,1/{joined}"

    def _config_to_v3(self, config: RawConfig) -> list[str]:
        all_freq: list[float] = []
        all_val: list[float] = []

        for sec in config.sections:
            pulse_time = len(sec.pulse) * _BASE_TICK_MS
            if sec.section_time > 0:
                loops = max(1, math.ceil(sec.section_time * 1000 / pulse_time))
            else:
                loops = 1
            total_points = len(sec.pulse) * loops

            freq_pair = (
                [sec.freq_start_ms, sec.freq_end_ms] if sec.freq_mode else [sec.freq_start_ms, sec.freq_start_ms]
            )

            freq_seq = self._build_freq_sequence(freq_pair, sec.freq_mode, len(sec.pulse), loops, total_points)

            val_seq: list[float] = []
            for _ in range(loops):
                val_seq.extend(sec.pulse)

            all_freq.extend(freq_seq)
            all_val.extend(val_seq)

        sub = _SUB_CYCLES
        if config.speed_factor == 2:
            sub = 2
        elif config.speed_factor == 4:
            sub = 1

        expanded_freq: list[float] = []
        expanded_val: list[float] = []
        for i in range(len(all_freq)):
            for _ in range(sub):
                expanded_freq.append(all_freq[i])
                expanded_val.append(all_val[i])

        if config.sleep_time > 0:
            sleep_entries = math.ceil(config.sleep_time * 1000 / _BASE_TICK_MS) * _SUB_CYCLES
            for _ in range(sleep_entries):
                expanded_freq.append(10.0)
                expanded_val.append(0.0)

        if len(expanded_freq) % _SUB_CYCLES != 0:
            pad = _SUB_CYCLES - len(expanded_freq) % _SUB_CYCLES
            for _ in range(pad):
                expanded_freq.append(10.0)
                expanded_val.append(0.0)

        result: list[str] = []
        for i in range(0, len(expanded_freq), _SUB_CYCLES):
            freq4 = expanded_freq[i : i + _SUB_CYCLES]
            val4 = expanded_val[i : i + _SUB_CYCLES]
            result.append(self._encode_frame(freq4, val4))

        return result

    def _build_freq_sequence(
        self,
        freq_pair: list[float],
        freq_mode: str | bool,
        pulse_len: int,
        loops: int,
        total_points: int,
    ) -> list[float]:
        if freq_mode == "inSection":
            return _interpolate(freq_pair, total_points)
        if freq_mode == "inPulse":
            single = _interpolate(freq_pair, pulse_len)
            seq: list[float] = []
            for _ in range(loops):
                seq.extend(single)
            return seq
        if freq_mode == "perPulse":
            per = _interpolate(freq_pair, loops)
            seq = []
            for val in per:
                seq.extend([val] * pulse_len)
            return seq
        return [freq_pair[0]] * total_points

    def _encode_frame(self, freq4: list[float], val4: list[float]) -> str:
        buf = bytearray(8)
        for i in range(4):
            buf[i] = int(_encode_freq(freq4[i])) & 0xFF
        for i in range(4):
            buf[i + 4] = int(val4[i]) & 0xFF
        return buf.hex().upper()

    def _decode_freq_byte(self, byte_val: int) -> float:
        if byte_val <= 10:
            return float(byte_val)
        if byte_val <= 100:
            return float(byte_val)
        if byte_val <= 200:
            return (byte_val - 100) * 5.0 + 100
        return (byte_val - 200) * 10.0 + 600

    def _find_closest_freq_index(self, freq_ms: float) -> int:
        best_idx = 0
        best_diff = abs(_FREQ_TABLE[0] - freq_ms)
        for i, val in enumerate(_FREQ_TABLE):
            diff = abs(val - freq_ms)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        return best_idx


def _encode_freq(freq_ms: float) -> float:
    if freq_ms == 0:
        return 0
    if freq_ms < 10:
        return 10
    if freq_ms <= 100:
        return freq_ms
    if freq_ms <= 600:
        return (freq_ms - 100) / 5 + 100
    if freq_ms <= 1000:
        return (freq_ms - 600) / 10 + 200
    return 0


def _interpolate(pts: list[float], n: int) -> list[float]:
    if n <= 1:
        return [pts[0]]
    step = (len(pts) - 1) / (n - 1)
    result: list[float] = []
    for i in range(n):
        p = i * step
        lo = int(p)
        hi = min(lo + 1, len(pts) - 1)
        if lo == hi:
            result.append(pts[lo])
        else:
            result.append(pts[lo] + (pts[hi] - pts[lo]) * (p - lo))
    return result
