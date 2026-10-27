import json
from copy import deepcopy
import subprocess
import sys
import unittest
from porcion_exacta.core import (
    approve_movement, confirm_portion, empty_shift, grams, net_weight,
    portion_alert, reconcile, register_portion,
)
from porcion_exacta.demo import scenario


class CoreTests(unittest.TestCase):
    def test_consistent(self):
        report = reconcile(scenario("consistente"))
        self.assertEqual(report["status"], "completo")
        self.assertEqual(report["standard_g"], 350)
        self.assertEqual(report["weighed_g"], 350)
        self.assertEqual(report["inventory_consumption_g"], 350)
        self.assertEqual(report["unexplained_g"], 0)

    def test_overportion(self):
        report = reconcile(scenario("sobreporcionado"))
        self.assertEqual(report["portion_deviation_g"], 22)
        self.assertEqual(report["unexplained_g"], 0)

    def test_pending_validation_recalculates(self):
        data = scenario("incompleto")
        before = reconcile(data)
        self.assertEqual((before["status"], before["unexplained_g"]), ("incompleto", 50))
        after_data = approve_movement(data, "merma-001", "Encargado")
        after = reconcile(after_data)
        self.assertEqual((after["status"], after["unexplained_g"]), ("completo", 10))
        self.assertEqual(reconcile(data)["unexplained_g"], 50)
        self.assertEqual(approve_movement(after_data, "merma-001", "Encargado"), after_data)

    def test_tare_and_alert(self):
        self.assertEqual(net_weight(222, 50), 172)
        self.assertEqual(portion_alert("ceviche", 172)["adjustment_g"], 22)
        self.assertEqual(portion_alert("plancha", 190)["action"], "agregar")
        for weight in (145, 150, 155):
            self.assertTrue(portion_alert("ceviche", weight)["in_range"])
        self.assertFalse(portion_alert("ceviche", 155.001)["in_range"])
        with self.assertRaises(ValueError):
            net_weight(20, 30)

    def test_initial_final_idempotency_and_corrections(self):
        data = register_portion(empty_shift(), "p1", "ceviche", "reposición", 222, 50)
        self.assertEqual(reconcile(data)["weighed_g"], 0)
        self.assertEqual(reconcile(data)["status"], "incompleto")
        self.assertEqual(register_portion(data, "p1", "ceviche", "reposición", 222, 50), data)
        with self.assertRaises(ValueError):
            register_portion(data, "p1", "ceviche", "venta", 180, 0)
        data = confirm_portion(data, "p1", 201, 50)
        data = confirm_portion(data, "p1", 200, 50)
        self.assertEqual(data["portions"][0]["initial_g"], 172)
        self.assertEqual(reconcile(data)["weighed_g"], 150)
        self.assertEqual(data["audit"][-1]["previous_g"], 151)
        self.assertEqual(confirm_portion(data, "p1", 200, 50), data)

    def test_missing_production_weighing(self):
        data = scenario("consistente")
        data["production"]["plancha"] = 2
        self.assertEqual(reconcile(data)["missing_weighings"]["plancha"], 1)
        self.assertEqual(reconcile(data)["status"], "incompleto")

    def test_scope_and_duplicates(self):
        for key, value in (("unit", "kg"), ("shift_id", "otro"), ("state", "entero"), ("ingredient_id", "arroz"), ("branch_id", "otra")):
            data = scenario("consistente")
            data["portions"][0]["scope"][key] = value
            with self.assertRaises(ValueError):
                reconcile(data)
        data = scenario("consistente")
        data["portions"].append(deepcopy(data["portions"][0]))
        with self.assertRaises(ValueError):
            reconcile(data)

    def test_linked_movement_not_counted_twice(self):
        data = scenario("incompleto")
        movement = data["movements"][0]
        movement.update(grams=150, portion_id="porcion-001", approved=True)
        self.assertEqual(reconcile(data)["documented_g"], 0)
        movement["grams"] = 149
        with self.assertRaises(ValueError):
            reconcile(data)

    def test_inventory_sign_transfers_and_missing(self):
        data = scenario("consistente")
        data["inventory"].update(incoming_g=30, received_g=20, sent_g=60)
        self.assertEqual(reconcile(data)["unexplained_g"], -10)
        data["inventory"]["final_g"] = None
        self.assertIsNone(reconcile(data)["unexplained_g"])
        self.assertEqual(reconcile(data)["status"], "incompleto")
        data["inventory"]["final_g"] = 2000
        self.assertEqual(reconcile(data)["status"], "incompleto")

    def test_invalid_numbers(self):
        for value in (True, -1, "NaN", "Infinity", "1e100", None, "texto", 0.0001):
            with self.assertRaises(ValueError, msg=str(value)):
                grams(value)
        self.assertEqual(net_weight("0.3", "0.1"), 0.2)

    def test_cli_json_and_errors(self):
        result = subprocess.run([sys.executable, "-m", "porcion_exacta", "--demo", "incompleto", "--approve", "merma-001", "--actor", "Encargado"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["investigation"]["report"]["unexplained_g"], 10)
        result = subprocess.run([sys.executable, "-m", "porcion_exacta", "--input", "-"], input='{"scope": {}}', capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
