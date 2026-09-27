INTERVAL_SCALE_POINTS = ((10.0, 0.0), (50.0, 16.5), (130.0, 33.0), (500.0, 66.0), (1000.0, 99.0))
INTERVAL_AXIS_MAX = 99.0


def interval_to_axis(interval: float) -> float:
    interval = max(10.0, min(1000.0, interval))
    for (x0, y0), (x1, y1) in zip(INTERVAL_SCALE_POINTS, INTERVAL_SCALE_POINTS[1:]):
        if interval <= x1:
            return y0 + (interval - x0) / (x1 - x0) * (y1 - y0)
    return INTERVAL_AXIS_MAX


def axis_to_interval(value: float) -> float:
    value = max(0.0, min(INTERVAL_AXIS_MAX, value))
    for (x0, y0), (x1, y1) in zip(INTERVAL_SCALE_POINTS, INTERVAL_SCALE_POINTS[1:]):
        if value <= y1:
            return x0 + (value - y0) / (y1 - y0) * (x1 - x0)
    return 1000.0
