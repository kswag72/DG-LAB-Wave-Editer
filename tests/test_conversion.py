from __future__ import annotations

import unittest
from pathlib import Path

from src.services.conversion_service import ConversionService


class ConversionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.converter = ConversionService()
        self.raw = (Path(__file__).parent / "fixtures" / "headerless_multi_section.raw").read_text().strip()

    def test_headerless_example_preserves_all_sections_and_decimal_points(self) -> None:
        config = self.converter.parse_raw(self.raw)
        self.assertEqual((config.sleep_time, config.speed_factor), (0.0, 1))
        self.assertEqual(len(config.sections), 10)
        self.assertEqual([len(section.pulse) for section in config.sections], [30, 8] + [2] * 8)
        self.assertEqual(config.sections[0].pulse[1], 16.67)
        self.assertEqual(config.sections[0].pulse[-1], 45.08)
        self.assertEqual(config.sections[2].freq_start_ms, 11.0)
        self.assertEqual(config.sections[-1].pulse, (0.0, 20.0))

    def test_headerless_conversion_matches_explicit_default_header(self) -> None:
        prefix = "Dungeonlab+pulse:"
        data = self.raw.removeprefix(prefix)
        explicit = self.converter.raw_to_v3(prefix + "0,1,8=" + data)
        for raw in (self.raw, data, "\n " + self.raw + " \n"):
            with self.subTest(raw_start=raw[:30]):
                self.assertEqual(self.converter.raw_to_v3(raw), explicit)
        self.assertEqual(len(explicit), 200)
        self.assertTrue(all(len(frame) == 16 for frame in explicit))
        intervals, intensities = self.converter.v3_frames_to_wave_data(explicit)
        self.assertEqual(intervals, [10] * 46 + [11] * 14 + [10] * 140)
        self.assertEqual(intensities[:7], [0, 16, 33, 50, 66, 83, 100])
        self.assertEqual(intensities[30:38], [100, 85, 71, 57, 42, 28, 14, 0])
        self.assertEqual(intensities[46:60], [100, 0] * 7)
        self.assertEqual(intensities[60:], [0, 20] * 70)

    def test_headerless_single_section(self) -> None:
        frames = self.converter.raw_to_v3("Dungeonlab+pulse:0,0,0,1,1/0-1,100-1")
        self.assertEqual(frames, ["0A0A0A0A00000000", "0A0A0A0A64646464"])

    def test_explicit_header_keeps_sleep_and_speed_settings(self) -> None:
        raw = "Dungeonlab+pulse:11,2,8=0,0,0,1,1/0-1,100-1"
        config = self.converter.parse_raw(raw)
        self.assertEqual((config.sleep_time, config.speed_factor), (0.2, 2))
        self.assertEqual(
            self.converter.raw_to_v3(raw),
            ["0A0A0A0A00006464", "0A0A0A0A00000000", "0A0A0A0A00000000"],
        )
