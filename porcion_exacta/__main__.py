"""Entrada/salida JSON, con trazas generadas en cada ejecución real."""
import argparse
import json
import sys
from .core import approve_movement
from .demo import scenario
from .runtime import run


def main():
    parser = argparse.ArgumentParser(description="Conciliar un turno de Porción Exacta")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Archivo JSON o - para stdin")
    source.add_argument("--demo", choices=["consistente", "sobreporcionado", "incompleto"])
    parser.add_argument("--approve", help="ID de movimiento que el operador valida explícitamente")
    parser.add_argument("--actor", help="Nombre del responsable de la validación")
    parser.add_argument("--log-dir", default="logs", help="Carpeta de trazas locales JSONL")
    args = parser.parse_args()
    try:
        if args.demo:
            data = scenario(args.demo)
        elif args.input == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.input, encoding="utf-8-sig") as handle:
                data = json.load(handle)
        if args.approve:
            if not args.actor:
                raise ValueError("--approve requiere --actor.")
            data = approve_movement(data, args.approve, args.actor)
        result = run(data, args.log_dir)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError, AttributeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
