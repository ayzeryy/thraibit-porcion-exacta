"""Trazas de ejecución local; no representan llamadas a modelos o servicios."""
import hashlib
import json
from pathlib import Path
from .core import event, investigate


def run(data, log_dir="logs"):
    analysis = investigate(data)
    trace = event("conciliacion_local_sin_IA", data["scope"]["shift_id"], "cli")
    trace["input_sha256"] = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    trace["mode"] = "muestra_sin_servicios"
    trace["report"] = analysis["report"]
    folder = Path(log_dir)
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / (trace["id"] + ".jsonl")).open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(trace, ensure_ascii=True) + "\n")
    return {"ok": True, "data": data, "investigation": analysis, "trace": trace}
