"""
Unit Tests for Smart Barrel Copilot (Zero-dependency standard unittest)
Author: Cristián González Huenchún
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from barrel_copilot.models import Barrica, EstadoBarrica
from barrel_copilot.ouillage import calcular_tasa_evaporacion, calcular_necesidad_ouillage
from barrel_copilot.so2_safety import calcular_microadicion_so2_barrica, evaluar_riesgo_brettanomyces
from barrel_copilot.qr_service import generar_codigo_qr_svg, generar_enlace_inspeccion
from barrel_copilot.database import CellarDatabase


class TestSmartBarrelCopilot(unittest.TestCase):

    def setUp(self):
        # Crear base de datos temporal en memoria
        self.db = CellarDatabase(db_path=Path(":memory:"))

    def tearDown(self):
        self.db.close()

    def test_database_seed_36_barricas(self):
        barricas = self.db.obtener_todas()
        self.assertEqual(len(barricas), 36)
        # Verificar presencia de barricas que requieren ouillage
        ouillage_count = sum(1 for b in barricas if b["estado"] == EstadoBarrica.REQUIERE_OUILLAGE.value)
        self.assertGreater(ouillage_count, 0)

    def test_tasa_evaporacion_ouillage(self):
        # A 15°C y 80% HR, barrica 225L de 1er uso
        tasa = calcular_tasa_evaporacion(temperatura_c=15.0, humedad_relativa_pct=80.0, capacidad_barrica_l=225.0, ano_uso=1)
        self.assertGreater(tasa["ml_por_dia"], 15.0)
        self.assertLess(tasa["ml_por_dia"], 40.0)
        self.assertGreater(tasa["litros_por_ano"], 6.0)

    def test_necesidad_ouillage_urgente(self):
        # 26 días sin relleno -> debe ser urgente
        necesidad = calcular_necesidad_ouillage(dias_desde_ultimo_ouillage=26, temperatura_c=16.0, humedad_relativa_pct=75.0)
        self.assertEqual(necesidad["urgencia"], "Urgente")
        self.assertEqual(necesidad["nivel_alerta"], "danger")
        self.assertGreater(necesidad["merma_acumulada_litros"], 0.8)

    def test_microadicion_so2_barrica(self):
        # Barrica de 225L con 18 mg/L SO2 libre, objetivo 32 mg/L -> delta 14 mg/L
        # Gramos K2S2O5 = (14 * 2.25) / 5 = 6.3 g
        res = calcular_microadicion_so2_barrica(capacidad_l=225.0, so2_libre_actual_mg_l=18.0, so2_libre_objetivo_mg_l=32.0, ph=3.60)
        self.assertEqual(res["delta_so2_mg_l"], 14.0)
        self.assertAlmostEqual(res["gramos_k2s2o5_polvo"], 6.30, places=1)
        self.assertGreater(res["so2_molecular_post_ajuste"], res["so2_molecular_actual"])

    def test_evaluacion_riesgo_brettanomyces(self):
        # Bajo SO2 (16 mg/L) a pH 3.70 en barrica vieja (3er uso)
        eval_riesgo = evaluar_riesgo_brettanomyces(so2_libre_mg_l=16.0, ph=3.70, ano_uso_barrica=3, meses_en_roble=14)
        self.assertEqual(eval_riesgo["nivel_riesgo"], "Crítico / Alto Riesgo")
        self.assertGreaterEqual(eval_riesgo["score_riesgo"], 60)

    def test_qr_generation(self):
        svg = generar_codigo_qr_svg("BAR-2025-014")
        self.assertIn("<svg", svg)
        self.assertIn("barrel-qr-svg", svg)

    def test_registrar_ouillage_database(self):
        barricas = self.db.obtener_todas()
        b_id = barricas[0]["id"]
        exito = self.db.registrar_ouillage(b_id, volumen_l=1.2)
        self.assertTrue(exito)
        actualizada = self.db.obtener_por_id(b_id)
        self.assertEqual(actualizada["dias_sin_ouillage"], 0)
        self.assertEqual(actualizada["merma_acumulada_l"], 0.0)
        self.assertEqual(actualizada["estado"], EstadoBarrica.OPTIMO.value)


if __name__ == "__main__":
    unittest.main()
