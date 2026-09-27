import math

Ia = 100

def gen_oa():
    r = []
    r.extend(range(10, 50, 1))
    r.extend(range(50, 80, 2))
    r.extend(range(80, 100, 5))
    r.extend(range(100, 200, 10))
    r.extend([200, 233, 266, 300, 333, 366])
    r.extend(range(400, 600, 50))
    r.extend(range(600, 1001, 100))
    return r

Oa = gen_oa()

def mu(e):
    if e == 0:
        return 0
    if e < 10:
        return 10
    if 10 <= e <= 100:
        return e
    if 100 < e <= 600:
        return (e - 100) / 5 + 100
    if 600 < e <= 1000:
        return (e - 600) / 10 + 200
    return 0

def jn(pts, n):
    if n <= 1:
        return [pts[0]]
    step = (len(pts) - 1) / (n - 1)
    result = []
    for i in range(n):
        p = i * step
        lo = int(p)
        hi = min(lo + 1, len(pts) - 1)
        if lo == hi:
            result.append(pts[lo])
        else:
            result.append(pts[lo] + (pts[hi] - pts[lo]) * (p - lo))
    return result

def xu(freq4, val4):
    a = bytearray(8)
    for t in range(4):
        a[t] = int(mu(freq4[t])) & 0xFF
    for t in range(4):
        a[t + 4] = int(val4[t]) & 0xFF
    return a.hex().upper()

def parse_raw(raw_str):
    data = raw_str
    if data.startswith("Dungeonlab+pulse:"):
        data = data[len("Dungeonlab+pulse:"):]

    header_str, rest = data.split("=", 1)
    header = [int(x) for x in header_str.split(",")]

    sleep_code = header[0]
    speed_factor = header[1]

    if sleep_code == 0:
        sleep_time = 0
    else:
        sleep_time = math.floor((sleep_code - 1) / 10) / 10 + 0.1

    section_strs = rest.split("+section+")
    sections = []

    for sec_str in section_strs:
        params_str, kf_str = sec_str.split("/", 1)
        params = [int(x) for x in params_str.split(",")]

        kf_pairs = kf_str.split(",")
        pulse = []
        for kf in kf_pairs:
            parts = kf.split("-")
            pulse.append(int(parts[0]))

        freq_start = Oa[params[0]] if params[0] < len(Oa) else 10
        freq_end = Oa[params[1]] if params[1] < len(Oa) else 10
        section_time = params[2] * 0.1

        freq_mode_map = {1: False, 2: "inSection", 3: "inPulse", 4: "perPulse"}
        freq_mode = freq_mode_map.get(params[3], False)

        if freq_mode:
            freq = [freq_start, freq_end]
        else:
            freq = freq_start

        sections.append({
            "pulse": pulse,
            "sectionTime": section_time,
            "freq": freq,
            "freqMode": freq_mode,
        })

    return {
        "sections": sections,
        "sleepTime": sleep_time,
        "speedFactor": speed_factor,
    }

def eu(config):
    sections = config["sections"]
    speed_factor = config.get("speedFactor", 1)

    all_freq = []
    all_val = []

    for sec in sections:
        pulse_time = len(sec["pulse"]) * Ia
        if sec["sectionTime"] > 0:
            D = max(1, math.ceil(sec["sectionTime"] * 1000 / pulse_time))
        else:
            D = 1
        k = len(sec["pulse"]) * D

        N = sec["freq"] if isinstance(sec["freq"], list) else [sec["freq"], sec["freq"]]

        C = []
        mode = sec["freqMode"]
        if mode == "inSection":
            C = jn(N, k)
        elif mode == "inPulse":
            single = jn(N, len(sec["pulse"]))
            for _ in range(D):
                C.extend(single)
        elif mode == "perPulse":
            per = jn(N, D)
            for s_val in per:
                for _ in range(len(sec["pulse"])):
                    C.append(s_val)
        else:
            C = [N[0]] * k

        w = []
        for _ in range(D):
            w.extend(sec["pulse"])

        all_freq.extend(C)
        all_val.extend(w)

    s = 4
    if speed_factor == 2:
        s = 2
    elif speed_factor == 4:
        s = 1

    d = []
    u = []
    for c in range(len(all_freq)):
        for _ in range(s):
            d.append(all_freq[c])
            u.append(all_val[c])

    if config.get("sleepTime", 0) > 0:
        sleep_entries = math.ceil(config["sleepTime"] * 1000 / Ia) * 4
        for _ in range(sleep_entries):
            d.append(10)
            u.append(0)

    if len(d) % 4 != 0:
        pad = 4 - len(d) % 4
        for _ in range(pad):
            d.append(10)
            u.append(0)

    result = []
    for c in range(0, len(d), 4):
        freq4 = d[c:c + 4]
        val4 = u[c:c + 4]
        result.append(xu(freq4, val4))

    return result


print("=" * 60)
print("EXAMPLE 1")
raw1 = "Dungeonlab+pulse:35,1,8=0,20,0,1,1/0-1,20-0,40-0,60-0,80-0,100-1,100-1,100-1"
config1 = parse_raw(raw1)
print(f"Config: {config1}")

expected1 = [
    "0A0A0A0A00000000", "0A0A0A0A14141414", "0A0A0A0A28282828", "0A0A0A0A3C3C3C3C",
    "0A0A0A0A50505050", "0A0A0A0A64646464", "0A0A0A0A64646464", "0A0A0A0A64646464",
    "0A0A0A0A00000000", "0A0A0A0A00000000", "0A0A0A0A00000000", "0A0A0A0A00000000",
]

result1 = eu(config1)
print(f"\nGenerated: {len(result1)} entries")
print(f"Expected:  {len(expected1)} entries")
print(f"Count match: {len(result1) == len(expected1)}")

all_match1 = True
for i, (gen, exp) in enumerate(zip(result1, expected1)):
    match = gen == exp
    if not match:
        all_match1 = False
    status = "OK" if match else "MISMATCH"
    print(f"  {i:2d}: gen={gen} exp={exp} {status}")

print(f"\nAll match: {all_match1}")

print("\n" + "=" * 60)
print("EXAMPLE 2")
raw2 = "Dungeonlab+pulse:5,1,8=0,20,35,3,1/0-1,25-0,50-0,75-0,100-1,100-1,100-1,0-1,0-0,0-1+section+0,20,21,1,1/0-1,100-1"
config2 = parse_raw(raw2)
print(f"Sections: {len(config2['sections'])}")
for si, sec in enumerate(config2["sections"]):
    print(f"  Section {si+1}: pulse_len={len(sec['pulse'])}, freq={sec['freq']}, mode={sec['freqMode']}, time={sec['sectionTime']}")

expected2 = [
    "0A0A0A0A00000000", "0A0A0A0A00000000", "0A0A0A0A00000000", "0A0A0A0A00000000",
    "0C0C0C0C19191919", "0C0C0C0C19191919", "0C0C0C0C19191919", "0C0C0C0C19191919",
    "0E0E0E0E32323232", "0E0E0E0E32323232", "0E0E0E0E32323232", "0E0E0E0E32323232",
    "1010101048484848", "1010101048484848", "1010101048484848", "1010101048484848",
    "1212121264646464", "1212121264646464", "1212121264646464", "1212121264646464",
    "1515151564646464", "1515151564646464", "1515151564646464", "1515151564646464",
    "1717171764646464", "1717171764646464", "1717171764646464", "1717171764646464",
    "1919191900000000", "1919191900000000", "1919191900000000", "1919191900000000",
    "1B1B1B1B00000000", "1B1B1B1B00000000", "1B1B1B1B00000000", "1B1B1B1B00000000",
    "1E1E1E1E00000000", "1E1E1E1E00000000", "1E1E1E1E00000000", "1E1E1E1E00000000",
    "0A0A0A0A00000000", "0A0A0A0A00000000", "0A0A0A0A00000000", "0A0A0A0A00000000",
    "0A0A0A0A09090909", "0A0A0A0A09090909", "0A0A0A0A09090909", "0A0A0A0A09090909",
    "0A0A0A0A12121212", "0A0A0A0A12121212", "0A0A0A0A12121212", "0A0A0A0A12121212",
    "0A0A0A0A1C1C1C1C", "0A0A0A0A1C1C1C1C", "0A0A0A0A1C1C1C1C", "0A0A0A0A1C1C1C1C",
    "0A0A0A0A25252525", "0A0A0A0A25252525", "0A0A0A0A25252525", "0A0A0A0A25252525",
    "0A0A0A0A2E2E2E2E", "0A0A0A0A2E2E2E2E",
    "0A0A0A0A37373737", "0A0A0A0A37373737",
    "0A0A0A0A41414141", "0A0A0A0A41414141",
    "0A0A0A0A4A4A4A4A", "0A0A0A0A4A4A4A4A",
    "0A0A0A0A53535353", "0A0A0A0A53535353",
    "0A0A0A0A5D5D5D5D", "0A0A0A0A5D5D5D5D",
    "0A0A0A0A64646464",
    "0A0A0A0A00000000",
]

result2 = eu(config2)
print(f"\nGenerated: {len(result2)} entries")
print(f"Expected:  {len(expected2)} entries")
print(f"Count match: {len(result2) == len(expected2)}")

all_match2 = True
mismatches = 0
for i in range(max(len(result2), len(expected2))):
    gen = result2[i] if i < len(result2) else "---"
    exp = expected2[i] if i < len(expected2) else "---"
    match = gen == exp
    if not match:
        all_match2 = False
        mismatches += 1
    status = "OK" if match else "MISMATCH"
    print(f"  {i:2d}: gen={gen} exp={exp} {status}")

print(f"\nAll match: {all_match2}, mismatches: {mismatches}")
