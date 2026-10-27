"""Interfaz de muestra: ejecutar con python -m streamlit run app.py."""
import json
from pathlib import Path
from copy import deepcopy
from uuid import uuid4
import streamlit as st
from porcion_exacta.core import (
    RECIPES, INVENTORY_FIELDS, approve_movement, confirm_portion, event,
    grams, investigate, net_weight, portion_alert, reconcile, register_portion, validate,
)
from porcion_exacta.demo import scenario

ROOT = Path(__file__).parent
st.set_page_config(page_title="Porción Exacta · ThraiBit", page_icon="⚖️", layout="wide")
if "shift" not in st.session_state:
    st.session_state.shift = scenario("cocina")


def save(data):
    validate(data)
    normalized = deepcopy(data)
    for row in normalized["portions"]:
        for key in ("initial_g", "final_g"):
            if row[key] is not None:
                row[key] = float(grams(row[key]))
    for row in normalized["movements"]:
        row["grams"] = float(grams(row["grams"]))
    for key, value in normalized["inventory"].items():
        if value is not None:
            normalized["inventory"][key] = float(grams(value))
    st.session_state.shift = normalized


with st.sidebar:
    st.image(str(ROOT / "thraibit-kit" / "logos" / "thraibit-color.svg"), width=190)
    st.caption("Cada porción cuenta.")
    st.divider()
    page = st.radio("Pantalla", ["Cocina", "Cierre"])
    st.info("Modo de muestra · datos ficticios · sin servicios externos ni IA.")
    selection = st.selectbox("Cargar escenario", ["cocina", "consistente", "sobreporcionado", "incompleto"])
    st.caption("Cargar reemplaza los datos de esta sesión. Descarga el turno antes de cambiarlo.")
    if st.button("Cargar escenario seleccionado"):
        save(scenario(selection))
        st.rerun()
    st.caption("Zetaris, USL, Nightshift, H-MEM y Nemotron: pendientes de integrar y verificar.")

data = st.session_state.shift
st.title("Porción Exacta")
st.caption("por ThraiBit · Una sucursal · Turno de demostración · Pescado limpio listo para porcionar · Gramos")

if page == "Cocina":
    st.header("Pesa, ajusta y confirma")
    st.write("Pesa el pescado antes de cocinar o mezclar. Ingresa el peso bruto y la tara del recipiente.")
    left, right = st.columns([1, 1])
    with left:
        dish = st.selectbox("Plato", list(RECIPES), format_func=lambda d: RECIPES[d]["name"])
        target = RECIPES[dish]["target_g"]
        st.metric("Objetivo de receta", f"{target} g", "Tolerancia ±5 g", delta_color="off")
        st.caption("Gramajes ficticios para la demostración.")
        kind = st.selectbox("Tipo de preparación", ["venta", "cortesía", "reposición"])
        rid = st.text_input("ID único de porción", value="porcion-001", help="Usa otro ID para cada nueva porción. Repetir el mismo registro no duplica el consumo.")
        gross = st.number_input("Peso bruto inicial (g)", min_value=0.0, value=172.0, step=1.0)
        tare = st.number_input("Tara inicial (g)", min_value=0.0, value=0.0, step=1.0)
        try:
            net = net_weight(gross, tare)
            alert = portion_alert(dish, net)
            st.write(f"Peso neto: **{net:g} g**")
            if alert["in_range"]:
                st.success("Porción dentro del rango.")
            else:
                st.warning(f"{alert['action'].capitalize()} {alert['adjustment_g']:g} g para llegar a {target} g.")
        except ValueError as exc:
            st.warning(str(exc))
        if st.button("Guardar peso inicial", type="primary"):
            try:
                save(register_portion(data, rid, dish, kind, gross, tare))
                st.success("Peso inicial guardado. Confirma el peso final para contabilizarlo.")
                st.rerun()
            except (ValueError, KeyError) as exc:
                st.error(str(exc))
    with right:
        st.subheader("Confirmación final")
        if not data["portions"]:
            st.info("Guarda primero la captura inicial.")
        else:
            selected = st.selectbox("Porción a confirmar o corregir", [p["id"] for p in data["portions"]])
            row = next(p for p in data["portions"] if p["id"] == selected)
            st.write(f"{RECIPES[row['dish_id']]['name']} · Inicial: {row['initial_g']:g} g")
            final_gross = st.number_input("Peso bruto final (g)", min_value=0.0, value=150.0, step=1.0)
            final_tare = st.number_input("Tara final (g)", min_value=0.0, value=0.0, step=1.0)
            try:
                final_net = net_weight(final_gross, final_tare)
                final_alert = portion_alert(row["dish_id"], final_net)
                st.write(f"Peso neto final: **{final_net:g} g**")
                if not final_alert["in_range"]:
                    st.warning(f"Fuera de tolerancia: {final_alert['action']} {final_alert['adjustment_g']:g} g. Se conservará el peso real confirmado.")
            except ValueError as exc:
                st.warning(str(exc))
            if st.button("Confirmar peso final"):
                try:
                    save(confirm_portion(data, selected, final_gross, final_tare))
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        st.caption("Una corrección actualiza la misma porción. Se conservan la captura inicial y el historial de confirmaciones.")
    st.subheader("Porciones del turno")
    st.dataframe([{k: v for k, v in p.items() if k != "scope"} for p in data["portions"]], hide_index=True)

else:
    st.header("Conciliación del turno")
    st.write("Incluye ventas, cortesías y reposiciones en la cantidad preparada.")
    with st.expander("Editar producción e inventario", expanded=False):
        with st.form("closing"):
            counts = {d: st.number_input(f"Cantidad preparada · {r['name']}", min_value=0, value=data["production"][d], step=1) for d, r in RECIPES.items()}
            labels = dict(initial_g="Inventario inicial", incoming_g="Entradas", received_g="Transferencias recibidas", sent_g="Transferencias enviadas", final_g="Inventario final")
            inv = {key: st.number_input(labels[key] + " (g)", min_value=0.0, value=None if data["inventory"][key] is None else float(data["inventory"][key]), step=1.0) for key in INVENTORY_FIELDS}
            st.caption("Un campo vacío significa dato pendiente; cero significa cantidad verificada igual a cero.")
            if st.form_submit_button("Guardar conteos"):
                from copy import deepcopy
                updated = deepcopy(data)
                updated.update(production=counts, inventory=inv)
                updated["audit"].append(event("conteos_actualizados", data["scope"]["shift_id"], "encargado-demo"))
                try:
                    save(updated)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    report = reconcile(data)
    if report["status"] == "incompleto":
        st.warning("Cierre incompleto · Resultados provisionales")
        for issue in report["issues"]:
            st.write("• " + issue)
        for dish_id, missing in report["missing_weighings"].items():
            if missing:
                st.write(f"{RECIPES[dish_id]['name']}: {missing} pesaje(s) final(es) pendiente(s).")
    else:
        st.success("Registros completos. Las diferencias restantes requieren revisión; este estado no demuestra su causa.")
    cols = st.columns(3)
    cols[0].metric("Consumo estándar", f"{report['standard_g']:g} g")
    cols[1].metric("Consumo pesado", f"{report['weighed_g']:g} g")
    cols[2].metric("Consumo según inventario", "Pendiente" if report["inventory_consumption_g"] is None else f"{report['inventory_consumption_g']:g} g")
    cols = st.columns(3)
    cols[0].metric("Desviación de porcionado", f"{report['portion_deviation_g']:+g} g")
    cols[1].metric("Mermas y otros usos aprobados adicionales", f"{report['documented_g']:g} g")
    cols[2].metric("Diferencia sin explicar", "Pendiente" if report["unexplained_g"] is None else f"{report['unexplained_g']:+g} g")
    st.caption("Desviación positiva: más gramos pesados que el estándar; negativa: menos. Sin explicar positiva: inventario consumido mayor que porciones y usos documentados; negativa: registros mayores que consumo de inventario. Cero indica conciliación aritmética.")
    st.subheader("Investigar evidencia")
    st.caption("Revisión determinista sin agentes de IA. Los textos se generan sobre los registros actuales.")
    analysis = investigate(data)
    for fact in analysis["facts"]:
        st.write(fact)
    st.write(analysis["evaluation"])
    for movement in data["movements"]:
        with st.container(border=True):
            st.write(f"**{movement['id']} · {movement['kind']} · {movement['grams']:g} g**")
            st.write(movement["evidence"])
            if movement.get("portion_id"):
                st.caption("Ya incluido en porción " + movement["portion_id"] + ": no se resta de nuevo.")
            if movement["approved"]:
                st.success("Validado por el operador.")
            else:
                actor = st.text_input("Responsable de validación", key="actor_" + movement["id"])
                checked = st.checkbox("Revisé la evidencia y confirmo este registro", key="check_" + movement["id"])
                if st.button("Validar y recalcular", key="approve_" + movement["id"], disabled=not checked):
                    try:
                        save(approve_movement(data, movement["id"], actor))
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
    with st.expander("Registrar merma u otro uso"):
        with st.form("movement"):
            mid = st.text_input("ID único del movimiento", value="uso-" + uuid4().hex[:8])
            mkind = st.selectbox("Tipo de movimiento", ["merma", "otro uso"])
            amount = st.number_input("Cantidad (g)", min_value=0.001, value=10.0, step=1.0, format="%.3f")
            evidence = st.text_area("Evidencia o referencia del registro")
            link = st.selectbox("¿Ya incluido en una porción confirmada?", [""] + [p["id"] for p in data["portions"] if p["final_g"] is not None])
            if st.form_submit_button("Guardar pendiente de validación"):
                from copy import deepcopy
                updated = deepcopy(data)
                updated["movements"].append(dict(id=mid, scope=dict(data["scope"]), kind=mkind, grams=amount, evidence=evidence, approved=False, portion_id=link or None))
                updated["audit"].append(event("movimiento_pendiente", mid, "encargado-demo"))
                try:
                    save(updated)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

st.divider()
st.download_button("Descargar turno JSON", json.dumps(data, ensure_ascii=False, indent=2), "turno.json", "application/json")
st.download_button("Descargar informe y traza local", json.dumps({"data": data, "investigation": investigate(data), "trace": event("informe_local_sin_IA", data["scope"]["shift_id"], "ui")}, ensure_ascii=False, indent=2), "informe.json", "application/json")
with st.expander("Restaurar un turno descargado"):
    upload = st.file_uploader("Archivo turno.json", type="json")
    if st.button("Restaurar turno", disabled=upload is None):
        try:
            save(json.load(upload))
            st.rerun()
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            st.error("Turno inválido: " + str(exc))
with st.expander("Historial local de cambios"):
    st.json(data["audit"])
st.caption("Datos guardados en la sesión del navegador. Descarga el JSON para conservarlos antes de cerrar o reiniciar. No se han medido ahorros reales.")
