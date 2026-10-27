# Contrato local v1

Entrada: objeto JSON completo de turno. Ver `input_examples/consistente.json` para el formato ejecutable.

| Campo | Contenido |
|---|---|
| `scope` | `branch_id`, `shift_id`, `ingredient_id`, `state`, `unit` |
| `production` | Enteros no negativos `ceviche` y `plancha`; incluye cortesías y reposiciones |
| `portions` | Lista de capturas; una por plato preparado y por ID |
| `movements` | Mermas y otros usos; las entradas y transferencias se totalizan en inventario |
| `inventory` | `initial_g`, `incoming_g`, `received_g`, `sent_g`, `final_g`; `null` si falta el dato |
| `audit` | Lista de eventos locales generados por capturas, correcciones y aprobaciones |

El contexto inicial es `sucursal-demo`, `turno-demo`, `pescado`, `limpio-listo-para-porcionar`, `g`. Los identificadores de sucursal y turno pueden cambiar si coinciden en todos los registros. Ingrediente, estado y unidad están limitados al alcance actual.

Una porción contiene `id`, copia del `scope`, `dish_id` (`ceviche` o `plancha`), `kind` (`venta`, `cortesía`, `reposición`), `initial_g` neto positivo y `final_g` neto positivo o `null` pendiente. Se descuenta tara antes de guardar. La producción puede superar las capturas para representar pesajes faltantes, pero no puede haber más capturas que producción.

Un movimiento contiene `id`, copia del `scope`, `kind` (`merma` u `otro uso`), `grams`, `evidence` no vacía, `approved` booleano y `portion_id` opcional. `portion_id: null` significa un uso adicional; un ID enlazado debe existir, tener final confirmado y coincidir en gramos: el uso ya se cuenta dentro de esa porción. Los ID de movimientos y porciones deben ser únicos dentro del turno. Al importar JSON, `approved` es un dato declarado por quien prepara la entrada; no representa autenticación ni evidencia externa verificada.

Los pesos admiten números JSON o cadenas numéricas, finitos, de 0 a 1 000 000 000 g y máximo tres decimales. Las porciones netas requieren más de cero. La interfaz captura números y tara por separado; el contrato almacena netos.

Salida: `ok`, el turno `data`, `investigation` con `report`, `facts`, `evidence`, `hypotheses`, `pending_data`, `evaluation`, y `trace`. Las diferencias conservan el signo. `status: completo` solo indica registros completos; no aprueba ni explica una diferencia distinta de cero. `status: incompleto` exige leer `issues` y `missing_weighings`.

Las funciones puras `register_portion`, `confirm_portion` y `approve_movement` devuelven una copia; nunca mutan el turno recibido. La CLI concilia una instantánea y permite aprobar un movimiento con `--approve ID --actor NOMBRE`. Para continuar con el turno actualizado, utiliza el campo `data` de la salida como nueva entrada.
