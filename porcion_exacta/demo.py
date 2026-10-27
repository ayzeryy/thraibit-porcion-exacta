"""Datos ficticios; cada escenario ejecuta los cálculos reales."""
from .core import empty_shift, register_portion, confirm_portion


def scenario(name="incompleto"):
    if name not in ("consistente", "sobreporcionado", "incompleto", "cocina"):
        raise ValueError("Escenario desconocido.")
    data = empty_shift()
    data["inventory"] = dict(initial_g=1000, incoming_g=0, received_g=0, sent_g=0, final_g=600)
    data["movements"] = [{"id": "merma-001", "scope": dict(data["scope"]), "kind": "merma",
                          "grams": 40, "approved": False, "portion_id": None,
                          "evidence": "Ficha ficticia M-001: 40 g de pescado limpio caído durante preparación; verificar con encargado."}]
    if name == "cocina":
        return data
    data = register_portion(data, "porcion-001", "ceviche", "venta", 172, 0)
    data = confirm_portion(data, "porcion-001", 172 if name == "sobreporcionado" else 150, 0)
    data = register_portion(data, "porcion-002", "plancha", "cortesía", 200, 0)
    data = confirm_portion(data, "porcion-002", 200, 0)
    if name != "incompleto":
        data["movements"] = []
        data["inventory"]["final_g"] = 628 if name == "sobreporcionado" else 650
    return data
