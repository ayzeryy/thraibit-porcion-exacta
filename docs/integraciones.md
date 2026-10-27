# Estado de integraciones

## Fuentes revisadas

- ZIP local `ThraiBit_Documentacion_para_Codex.zip`: `LEER_PRIMERO.md`, `01_Pre_Submission_Self_Check.md`, propuesta y plan. Los PDF de Participant Setup y criterios USL no están incluidos.
- [Página oficial del evento](https://hackathon.genai.works/event/open-agent-hackathon-2026): consultada; el contenido accesible muestra fecha de cierre y encabezados de reglas, pero no despliega todas las secciones. No constituye verificación completa de cada requisito.
- [Meterless Engines](https://meterless.ai/engines.html): consultada; publica el contrato del Runtime y referencias de implementación H-MEM.
- [Zetaris getting started](https://zetaris.github.io/getting-started/): se intentó consultar; el navegador de investigación no pudo acceder al contenido. [Repositorio oficial de la guía](https://github.com/zetaris/getting-started): referencia para continuar.

## Pendientes verificables

| Integración | Estado | Evidencia necesaria |
|---|---|---|
| Zetaris | Sin adaptar ni conectar | Servicio disponible, registro de fuentes, consulta real desde Python |
| USL | Sin implementar | Tres fuentes como mínimo según el material proporcionado; DDL, 2–3 consultas por fuente y por USL, regla de calidad ejecutada y reflexión |
| Nightshift | Contrato público revisado; sin adaptar ni conectar | Runtime y token locales, consulta de modelos autorizada y respuesta real usada por el flujo |
| H-MEM | Referencia oficial localizada; implementación sin revisar | Seguir `engines/hmem/AGENTS.md`, adaptar referencia, pasar conformance y demostrar escritura aprobada y recuperación en otra sesión |
| Nemotron | Sin verificar disponibilidad | Modelo real servido por Nightshift registrado en cada solicitud; un ID de enrutamiento no prueba el modelo efectivo |
| Agentes | Roles diseñados; sin llamadas de IA | Analista, Investigador y Evaluador con evidencia, intercambios y revisión auténticos |

Nightshift publica un Runtime compatible con chat completions, autenticación Bearer y encabezados de aplicación y ámbito. La conexión se valida con modelos autorizados; salud del proceso no basta. Las credenciales deben configurarse localmente cuando se implemente el adaptador. No se han hecho llamadas de prueba a servicios privados ni se han supuesto credenciales.

H-MEM se referencia en [su motor oficial](https://github.com/Meterless/Meterless/tree/main/engines/hmem). La guía Engines pide validar la implementación con la suite de conformance. Un historial JSON de este prototipo no es H-MEM y un antecedente recuperado nunca prueba la causa del turno actual.

## Siguiente fase

1. Revisar las guías originales completas y la versión concreta de las herramientas instaladas con el equipo.
2. Preparar fuentes de recetas, producción/pesajes e inventario en Zetaris; implementar contrato semántico y calidad antes de usarlas para conciliar.
3. Conectar Nightshift, comprobar autorización/modelos y ejecutar una investigación real con límites de tiempo y degradación explícita a muestra.
4. Integrar H-MEM para guardar solo explicaciones aprobadas; probar recuperación entre procesos y conformance.
5. Registrar trazas reales por servicio y agente, sin tokens; repetir los tres casos y completar materiales de entrega.

No reemplazar las herramientas exigidas por SQLite, un archivo de memoria o un proveedor diferente y presentarlos como las integraciones del hackathon.
