from __future__ import annotations


class Json5PulseRepository:
    def save(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
