"""Genera entradas y salidas ejecutando el mismo núcleo que la aplicación."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from porcion_exacta.demo import scenario
from porcion_exacta.runtime import run


def main():
    for directory in ("input_examples", "output_examples"):
        (ROOT / directory).mkdir(exist_ok=True)
    for name in ("consistente", "sobreporcionado", "incompleto"):
        data = scenario(name)
        result = run(data, ROOT / "logs")
        (ROOT / "input_examples" / (name + ".json")).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (ROOT / "output_examples" / (name + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(name + ": " + result["investigation"]["report"]["status"])


if __name__ == "__main__":
    main()
