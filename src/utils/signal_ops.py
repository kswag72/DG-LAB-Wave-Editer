import math


def generate_wave(
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
        if wave_type == 0:
            p = t * cycles * math.pi * 2
            v = (math.sin(p - math.pi / 2) + 1) / 2 * amplitude + offset
        elif wave_type == 1:
            p = t * cycles * math.pi * 2
            v = (amplitude if math.sin(p) >= 0 else 0) + offset
        elif wave_type == 2:
            v = ((t * cycles) % 1) * amplitude + offset
        elif wave_type == 3:
            v = (1 - abs(((t * cycles) % 1) * 2 - 1)) * amplitude + offset
        elif wave_type == 4:
            v = coeff * (t**exponent) * amplitude + offset
        elif wave_type == 5:
            v = coeff * (t**2) * amplitude + exponent * t * amplitude + offset
        elif wave_type == 6:
            if abs(exponent) < 0.01:
                v = t * amplitude * coeff + offset
            else:
                v = coeff * (math.exp(exponent * t) - 1) / (math.exp(exponent) - 1) * amplitude + offset
        elif wave_type == 7:
            if abs(exponent) < 0.01:
                v = t * amplitude * coeff + offset
            else:
                v = coeff * math.log(1 + t * (math.e**exponent - 1)) / exponent * amplitude + offset
        elif wave_type == 8:
            v = amplitude * (1 - math.exp(-exponent * t * 5)) * coeff + offset
        elif wave_type == 9:
            v = amplitude * (0.5 + 0.5 * math.tanh((t - 0.5) * exponent * 4)) * coeff + offset
        else:
            v = 0
        v = max(0, v)
        result[range_lo + i] = int(v)
    return result


def smooth_array(arr: list[int], n: int) -> list[int]:
    r = list(arr)
    for i in range(1, n - 1):
        r[i] = int(arr[i - 1] * 0.25 + arr[i] * 0.5 + arr[i + 1] * 0.25)
    return r
