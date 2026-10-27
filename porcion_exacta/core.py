"""Contrato y reglas deterministas. Todos los pesos se expresan en gramos."""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4

RECIPES = {"ceviche": {"name": "Ceviche de pescado", "target_g": 150},
           "plancha": {"name": "Pescado a la plancha", "target_g": 200}}
SCOPE = {"branch_id": "sucursal-demo", "shift_id": "turno-demo",
         "ingredient_id": "pescado", "state": "limpio-listo-para-porcionar", "unit": "g"}
INVENTORY_FIELDS = ("initial_g", "incoming_g", "received_g", "sent_g", "final_g")


def grams(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise ValueError("El peso debe ser un número en gramos.")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Peso inválido.") from exc
    if not number.is_finite() or number < 0 or number > 1_000_000_000:
        raise ValueError("El peso debe ser finito, no negativo y menor o igual a 1 000 000 000 g.")
    if number != number.quantize(Decimal("0.001")):
        raise ValueError("Usa como máximo tres decimales en gramos.")
    return number


def identifier(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Cada registro necesita un identificador no vacío.")
    return value


def net_weight(gross_g, tare_g):
    net = grams(gross_g) - grams(tare_g)
    if net <= 0:
        raise ValueError("El peso bruto debe superar la tara.")
    return float(net)


def portion_alert(dish_id, weight_g):
    if dish_id not in RECIPES:
        raise ValueError("Plato desconocido.")
    weight = grams(weight_g)
    difference = weight - RECIPES[dish_id]["target_g"]
    return {"in_range": abs(difference) <= 5, "difference_g": float(difference),
            "action": "en rango" if abs(difference) <= 5 else "retirar" if difference > 0 else "agregar",
            "adjustment_g": 0 if abs(difference) <= 5 else float(abs(difference))}


def empty_shift():
    return {"scope": dict(SCOPE), "production": {"ceviche": 0, "plancha": 0},
            "portions": [], "movements": [],
            "inventory": {key: None for key in INVENTORY_FIELDS}, "audit": []}


def event(action, record_id, actor):
    return {"id": str(uuid4()), "at": datetime.now(timezone.utc).isoformat(),
            "action": action, "record_id": record_id, "actor": identifier(actor)}


def validate(data):
    if not isinstance(data["audit"], list):
        raise ValueError("El historial debe ser una lista.")
    scope = data["scope"]
    if set(scope) != set(SCOPE) or any(not isinstance(v, str) or not v.strip() for v in scope.values()):
        raise ValueError("Contexto incompleto.")
    if any(scope[k] != SCOPE[k] for k in ("ingredient_id", "state", "unit")):
        raise ValueError("Se requiere pescado limpio listo para porcionar, en gramos.")
    if set(data["production"]) != set(RECIPES):
        raise ValueError("La producción debe incluir ambos platos.")
    for count in data["production"].values():
        if type(count) is not int or count < 0:
            raise ValueError("La cantidad preparada debe ser un entero no negativo.")
    for key in INVENTORY_FIELDS:
        if data["inventory"][key] is not None:
            grams(data["inventory"][key])
    ids = set()
    portions = {}
    for group in ("portions", "movements"):
        for row in data[group]:
            rid = identifier(row["id"])
            if rid in ids:
                raise ValueError("Identificador duplicado: " + rid)
            ids.add(rid)
            if row["scope"] != scope:
                raise ValueError("No se pueden comparar registros de distinto contexto.")
            if group == "portions":
                if row["dish_id"] not in RECIPES or row["kind"] not in ("venta", "cortesía", "reposición"):
                    raise ValueError("Plato o tipo de preparación inválido.")
                if grams(row["initial_g"]) <= 0:
                    raise ValueError("La porción inicial debe ser positiva.")
                if row["final_g"] is not None and grams(row["final_g"]) <= 0:
                    raise ValueError("La porción final debe ser positiva.")
                portions[rid] = row
            else:
                grams(row["grams"])
                if row["kind"] not in ("merma", "otro uso") or type(row["approved"]) is not bool:
                    raise ValueError("Movimiento inválido.")
                identifier(row["evidence"])
    for row in data["movements"]:
        link = row.get("portion_id")
        if link is not None:
            portion = portions.get(link)
            if portion is None or portion["final_g"] is None or grams(portion["final_g"]) != grams(row["grams"]):
                raise ValueError("Un uso ya contabilizado debe referenciar una porción confirmada del mismo peso.")
    for dish in RECIPES:
        if sum(p["dish_id"] == dish for p in data["portions"]) > data["production"][dish]:
            raise ValueError("Hay más pesajes que platos preparados; revisa la producción.")


def register_portion(data, record_id, dish_id, kind, gross_g, tare_g):
    result = deepcopy(data)
    if dish_id not in RECIPES:
        raise ValueError("Plato desconocido.")
    identifier(record_id)
    existing = next((p for p in result["portions"] if p["id"] == record_id), None)
    row = {"id": record_id, "scope": dict(data["scope"]), "dish_id": dish_id,
           "kind": kind, "initial_g": net_weight(gross_g, tare_g), "final_g": None}
    if existing:
        if any(existing[k] != row[k] for k in ("dish_id", "kind", "initial_g")):
            raise ValueError("Ese identificador ya corresponde a otra captura.")
        return result
    result["portions"].append(row)
    result["production"][dish_id] += 1
    result["audit"].append(event("captura_inicial", record_id, "cocina-demo"))
    validate(result)
    return result


def confirm_portion(data, record_id, gross_g, tare_g):
    result = deepcopy(data)
    portion = next((p for p in result["portions"] if p["id"] == record_id), None)
    if portion is None:
        raise ValueError("Porción inexistente.")
    final = net_weight(gross_g, tare_g)
    if portion["final_g"] != final:
        previous = portion["final_g"]
        portion["final_g"] = final
        entry = event("confirmacion_final", record_id, "cocina-demo")
        entry.update({"previous_g": previous, "final_g": final})
        result["audit"].append(entry)
    validate(result)
    return result


def approve_movement(data, record_id, actor):
    result = deepcopy(data)
    row = next((m for m in result["movements"] if m["id"] == record_id), None)
    if row is None:
        raise ValueError("Movimiento inexistente.")
    if not row["approved"]:
        row["approved"] = True
        result["audit"].append(event("validacion_humana", record_id, actor))
    validate(result)
    return result


def reconcile(data):
    validate(data)
    standard = sum(Decimal(RECIPES[d]["target_g"]) * n for d, n in data["production"].items())
    weighed = sum((grams(p["final_g"]) for p in data["portions"] if p["final_g"] is not None), Decimal(0))
    documented = sum((grams(m["grams"]) for m in data["movements"] if m["approved"] and m.get("portion_id") is None), Decimal(0))
    missing = {d: data["production"][d] - sum(p["dish_id"] == d and p["final_g"] is not None for p in data["portions"]) for d in RECIPES}
    pending = [m["id"] for m in data["movements"] if not m["approved"]]
    inventory = data["inventory"]
    absent = [k for k in INVENTORY_FIELDS if inventory[k] is None]
    consumption = None if absent else (grams(inventory["initial_g"]) + grams(inventory["incoming_g"]) + grams(inventory["received_g"]) - grams(inventory["sent_g"]) - grams(inventory["final_g"]))
    issues = []
    if any(missing.values()):
        issues.append("Faltan pesos finales confirmados; la desviación es provisional.")
    if pending:
        issues.append("Hay movimientos pendientes de validación humana.")
    if absent:
        issues.append("Faltan campos de inventario: " + ", ".join(absent))
    if consumption is not None and consumption < 0:
        issues.append("El inventario produce consumo negativo; revisar movimientos y conteos.")
    return {"status": "incompleto" if issues else "completo", "standard_g": float(standard),
            "weighed_g": float(weighed), "inventory_consumption_g": None if consumption is None else float(consumption),
            "documented_g": float(documented), "portion_deviation_g": float(weighed - standard),
            "unexplained_g": None if consumption is None else float(consumption - weighed - documented),
            "missing_weighings": missing, "pending_movements": pending, "issues": issues}


def investigate(data):
    report = reconcile(data)
    return {"mode": "revision_determinista_sin_IA", "report": report,
            "facts": [f"Consumo pesado confirmado: {report['weighed_g']} g.",
                      f"Usos aprobados no incluidos en porciones: {report['documented_g']} g."],
            "evidence": [{"id": m["id"], "grams": m["grams"], "evidence": m["evidence"],
                          "approved": m["approved"], "portion_id": m.get("portion_id")} for m in data["movements"]],
            "hypotheses": [], "pending_data": report["issues"],
            "evaluation": "Los registros pendientes requieren validación humana. Una diferencia no demuestra su causa."}
