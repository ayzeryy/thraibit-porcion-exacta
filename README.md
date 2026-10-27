# Porción Exacta, por ThraiBit

**Cada porción cuenta.** Control de porciones y conciliación de pescado limpio al cierre del turno, para el Open Agent Hackathon 2026.

Estado: prototipo local funcional en Python y Streamlit. Los datos y gramajes son ficticios. El modo de muestra ejecuta cálculos reales sin credenciales, red ni respuestas de IA guardadas. **Todavía no implementa agentes de IA ni las integraciones exigidas para la entrega.**

## Ejecutar en Windows con Git Bash

Desde la carpeta del repositorio, con Python 3.10 o posterior instalado:

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m streamlit run app.py
```

Si `.venv` ya existe, omite el primer comando. No hace falta activar el entorno. Abre la dirección local que indique Streamlit, normalmente `http://localhost:8501`. Para detenerlo, presiona `Ctrl+C`.

## Recorrido de demostración

1. En Cocina, selecciona ceviche (150 g ±5 g), ID `porcion-001`, peso bruto 172 g y tara 0 g. La alerta indica retirar 22 g.
2. Guarda el peso inicial y confirma 150 g como peso bruto final, tara 0 g.
3. Selecciona pescado a la plancha (200 g ±5 g), cambia el ID a `porcion-002` y registra 200 g. Selecciona esa porción en confirmación y confirma 200 g finales.
4. Abre Cierre. El inventario ficticio inicial es 1000 g y el final 600 g: consumo 400 g frente a 350 g pesados. La diferencia provisional es +50 g.
5. Revisa la ficha ficticia `merma-001` de 40 g. Escribe el responsable, marca la comprobación de evidencia y pulsa **Validar y recalcular**.
6. Los usos aprobados pasan a 40 g; quedan **+10 g sin explicar**. El registro está completo, pero la causa de esos 10 g sigue sin establecerse.

Los escenarios de la barra lateral reemplazan la sesión al pulsar Cargar. Descarga antes el turno si quieres conservarlo. Puedes restaurar el archivo `turno.json` desde la aplicación. El informe incluye resultados, evidencia e historial; el archivo de turno es la entrada programática.

## Ejecución programática

Entrada y salida JSON, sin interacción ni interfaz:

```bash
./.venv/Scripts/python.exe -m porcion_exacta --demo consistente
./.venv/Scripts/python.exe -m porcion_exacta --input input_examples/sobreporcionado.json
./.venv/Scripts/python.exe -m porcion_exacta --input input_examples/incompleto.json --approve merma-001 --actor "Encargado demo" > cierre-validado.json
```

También acepta stdin con `--input -`. Devuelve código 0 y `ok: true` en ejecuciones correctas; los errores devuelven código 2 y `ok: false`. Un cierre incompleto es un resultado válido con `status: incompleto`. Cada ejecución CLI genera una traza JSONL en `logs/` con UUID, hora UTC, hash de la entrada y cálculos de esa ejecución; también la incluye en stdout. Son trazas **locales deterministas**, no evidencia de llamadas a agentes o patrocinadores. `--log-dir` permite cambiar la carpeta.

Para regenerar los tres pares de ejemplos mediante cálculos actuales:

```bash
./.venv/Scripts/python.exe scripts/generate_examples.py
```

Los resultados en `output_examples/` son referencias producidas por ejecuciones reales sobre datos ficticios; la aplicación no los lee. Sus UUID y fechas cambian al regenerarlos.

| Caso | Estándar | Pesado | Inventario consumido | Desviación | Sin explicar |
|---|---:|---:|---:|---:|---:|
| Consistente | 350 g | 350 g | 350 g | 0 g | 0 g |
| Sobreporcionado | 350 g | 372 g | 372 g | +22 g | 0 g |
| Incompleto, antes de aprobar | 350 g | 350 g | 400 g | 0 g | +50 g provisional |
| Tras aprobar merma de 40 g | 350 g | 350 g | 400 g | 0 g | +10 g |

## Reglas y contrato

Consulta [el contrato JSON](docs/contrato.md) y los archivos de `input_examples/` antes de integrar otras fuentes.

- Consumo estándar = suma de cantidades preparadas × receta (ceviche 150 g, plancha 200 g).
- Consumo pesado = suma de pesos finales confirmados; la captura inicial no se suma.
- Consumo según inventario = inicial + entradas + transferencias recibidas − enviadas − final.
- Desviación = pesado − estándar. Positiva significa sobreporcionado neto; negativa, menos gramos que el estándar. Con pesajes faltantes es provisional.
- Sin explicar = inventario consumido − pesado − usos aprobados adicionales. Positiva significa consumo de inventario mayor que el documentado; negativa, registros mayores que consumo de inventario. El signo no establece una causa.
- Los ID evitan duplicados. Corregir una porción conserva el peso inicial y actualiza el final del mismo registro; el historial conserva finales anteriores. Repetir una captura idéntica o una aprobación no duplica eventos ni consumo.
- Ventas, cortesías y reposiciones cuentan como producción. Una merma ya incluida en una porción debe vincularse por `portion_id` y peso coincidente; no se resta otra vez. Usa otro ID para cada consumo físico distinto; el sistema no detecta dos ID diferentes referidos al mismo hecho.
- Cada registro debe coincidir en sucursal, turno, ingrediente, unidad y estado. No convierte pescado entero, cocinado o kilogramos. Se calculan cantidades con `Decimal`, hasta tres decimales de gramo.
- Producción declarada superior a pesajes finales, movimientos sin aprobar o inventario pendiente generan cierre incompleto. `null` significa dato pendiente; cero es un conteo registrado de cero. Consumo de inventario negativo exige revisión.

## Arquitectura y trabajo entre dos integrantes

| Archivo o carpeta | Responsabilidad | Propuesta de responsable |
|---|---|---|
| `porcion_exacta/core.py` | Validación, capturas, aprobación y fórmulas puras | A |
| `porcion_exacta/demo.py` | Construcción de datos ficticios | A |
| `porcion_exacta/runtime.py`, `__main__.py` | CLI JSON y trazas | A |
| `app.py`, `.streamlit/`, `thraibit-kit/` | Cocina, cierre y marca | B |
| `tests/`, `docs/`, ejemplos | Verificación y acuerdos | Coordinar antes de editar |

Acuerden esta asignación antes de trabajar simultáneamente. Usen ramas pequeñas (`codex/logica`, `codex/interfaz`, por ejemplo), intercambien el contrato y ejecuten las pruebas antes de integrar en `main`. La lógica no importa Streamlit y puede reutilizarse desde otro adaptador.

```bash
./.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Incluye pruebas de las fórmulas, los tres escenarios, tara, tolerancias, duplicados, correcciones, faltantes, contexto incompatible, transferencias, signos, doble contabilización y entrada CLI. La prueba Streamlit recorre 172 → 150 g, segundo plato, cierre y validación humana.

## Integraciones y próximos pasos

Revisados el plan local y el ZIP `ThraiBit_Documentacion_para_Codex.zip` proporcionado por el usuario. Su Self-Check pide Zetaris, Nightshift y al menos un Meterless Engine funcional; Nightshift por sí solo no acredita un Engine. Los documentos de propuesta anteriores mencionan uno o tres platos: aquí prevalece la solicitud actual de **dos platos**.

Consulta [estado y fuentes de integraciones](docs/integraciones.md). Zetaris/USL, Nightshift, H-MEM y Nemotron **no están conectados ni se han probado**. No hay adaptadores ficticios que simulen esas conexiones. Los roles previstos son Analista (desviaciones), Investigador (evidencia) y Evaluador (contraste y validación); la revisión actual es determinista y distingue hechos, datos pendientes y una lista de hipótesis vacía.

Quedan por realizar: aprovisionamiento y consulta real de Zetaris; tres fuentes, DDL y consultas USL y regla de calidad; peticiones Nightshift y agentes con intercambio y revisión reales; H-MEM con conformance y recuperación entre sesiones; modelo Nemotron efectivo si se busca ese premio; video, presentación y envío. El prototipo local no acredita estos requisitos.

## Persistencia y límites

El turno vive en `st.session_state`; no hay base de datos, concurrencia entre operadores, autenticación ni auditoría inmutable. Descarga el turno para conservarlo antes de cerrar o recargar la sesión. El nombre del validador identifica una acción de demostración, sin verificar su identidad. Las trazas de CLI y los informes de interfaz contienen datos locales de la ejecución; no representan logs de IA. No hay conexión de básculas, ventas ni gestión de múltiples sucursales. No se han medido ahorros reales.

`.env`, sus variantes privadas, `.venv` y `logs/` están ignorados por Git; `.env.example` solo documenta el modo actual y no contiene secretos. La aplicación todavía no lee `.env` ni activa servicios al cambiar `SAMPLE_MODE`; únicamente funciona en muestra. Las opciones de servicios se añadirán al implementar sus contratos. No compartan credenciales por chat ni las incluyan en capturas, logs o commits.
