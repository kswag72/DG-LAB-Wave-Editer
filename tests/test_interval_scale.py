import unittest

from src.ui.interval_scale import axis_to_interval, interval_to_axis


class IntervalScaleTests(unittest.TestCase):
    def test_breakpoints_in_both_directions(self) -> None:
        for interval, value in ((10, 0), (50, 16.5), (130, 33), (500, 66), (1000, 99)):
            with self.subTest(interval=interval):
                self.assertEqual(interval_to_axis(interval), value)
                self.assertEqual(axis_to_interval(value), interval)

    def test_segment_midpoints_keep_fractional_values(self) -> None:
        for interval, value in ((30, 8.25), (90, 24.75), (315, 49.5), (750, 82.5)):
            with self.subTest(interval=interval):
                self.assertAlmostEqual(interval_to_axis(interval), value)
                self.assertAlmostEqual(axis_to_interval(value), interval)

    def test_internal_boundaries_are_continuous(self) -> None:
        for interval, value in ((50, 16.5), (130, 33), (500, 66)):
            with self.subTest(interval=interval):
                self.assertAlmostEqual(interval_to_axis(interval - 1e-6), value, delta=1e-6)
                self.assertAlmostEqual(interval_to_axis(interval + 1e-6), value, delta=1e-6)
                self.assertLess(interval_to_axis(interval - 1e-6), interval_to_axis(interval + 1e-6))

    def test_full_input_range_is_monotonic_and_reversible(self) -> None:
        values = [interval_to_axis(interval) for interval in range(10, 1001)]
        self.assertTrue(all(left < right for left, right in zip(values, values[1:])))
        for interval, value in zip(range(10, 1001), values):
            self.assertAlmostEqual(axis_to_interval(value), interval, places=10)


if __name__ == "__main__":
    unittest.main()
