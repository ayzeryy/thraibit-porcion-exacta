import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class AppFlowTests(unittest.TestCase):
    def test_kitchen_closure_and_human_approval(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("Retirar 22 g" in w.value for w in app.warning))
        next(b for b in app.button if b.label == "Guardar peso inicial").click().run()
        self.assertEqual(len(app.exception), 0)
        next(b for b in app.button if b.label == "Confirmar peso final").click().run()
        next(s for s in app.selectbox if s.label == "Plato").set_value("plancha").run()
        next(t for t in app.text_input if t.label == "ID único de porción").set_value("porcion-002")
        next(n for n in app.number_input if n.label == "Peso bruto inicial (g)").set_value(200.0)
        next(b for b in app.button if b.label == "Guardar peso inicial").click().run()
        next(s for s in app.selectbox if s.label == "Porción a confirmar o corregir").set_value("porcion-002").run()
        next(n for n in app.number_input if n.label == "Peso bruto final (g)").set_value(200.0)
        next(b for b in app.button if b.label == "Confirmar peso final").click().run()
        app.radio[0].set_value("Cierre").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(next(m for m in app.metric if m.label == "Diferencia sin explicar").value, "+50 g")
        next(t for t in app.text_input if t.label == "Responsable de validación").set_value("Encargado")
        app.checkbox[0].check().run()
        next(b for b in app.button if b.label == "Validar y recalcular").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(next(m for m in app.metric if m.label == "Diferencia sin explicar").value, "+10 g")
        self.assertEqual(next(m for m in app.metric if m.label == "Consumo pesado").value, "350 g")


if __name__ == "__main__":
    unittest.main()
