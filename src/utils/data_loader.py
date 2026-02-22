import json
import math
import random
import re


def parse_json5_content(content: str) -> list[dict]:
    clean = re.sub(r"//.*", "", content)
    clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)
    clean = re.sub(r"([a-zA-Z0-9_]+):", r'"\1":', clean)
    clean = clean.replace("'", '"')
    clean = re.sub(r",(\s*[\]}])", r"\1", clean)
    data = json.loads(clean)
    result = []
    for item in data:
        result.append(
            {
                "id": item.get("id", hex(random.getrandbits(32))[2:]),
                "name": item.get("name", "导入波形"),
                "intervals": [int(p[0:2], 16) for p in item["pulseData"]],
                "intensities": [int(p[8:10], 16) for p in item["pulseData"]],
                "steps": len(item["pulseData"]),
            }
        )
    return result


def format_pulse_export(sequence: list[dict]) -> str:
    lines = []
    for s in sequence:
        if s["type"] == "wave":
            for i in range(s["steps"]):
                h, v = (
                    hex(s["intervals"][i])[2:].upper().zfill(2) * 4,
                    hex(s["intensities"][i])[2:].upper().zfill(2) * 4,
                )
                lines.append(f"'{h}{v}'")
        else:
            for _ in range(math.ceil(s["ms"] / 100)):
                lines.append("'0A0A0A0A00000000'")
    sep = ",\n    "
    return (
        "{\n"
        f"  id: '{hex(random.getrandbits(32))[2:]}',\n"
        "  name: '导出结果',\n"
        "  pulseData: [\n"
        f"    {sep.join(lines)}\n"
        "  ]\n"
        "}"
    )


def format_library_export(wave_lib: list[dict]) -> str:
    items = []
    for w in wave_lib:
        pd = [
            f"'{hex(w['intervals'][i])[2:].upper().zfill(2) * 4}{hex(w['intensities'][i])[2:].upper().zfill(2) * 4}'"
            for i in range(w["steps"])
        ]
        sep = ",\n      "
        items.append(
            f"  {{\n    id: '{w['id']}',\n    name: '{w['name']}',\n    pulseData: [\n      {sep.join(pd)}\n    ]\n  }}"
        )
    return "[\n" + ",\n".join(items) + "\n]"
