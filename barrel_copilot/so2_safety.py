"""
Barrel Sulfur Dioxide Management & Brettanomyces Microbial Safety
Precision micro-additions and wood hygiene monitoring.
Author: Cristián González Huenchún
"""

import math
from typing import Dict, Any


def calcular_microadicion_so2_barrica(
    capacidad_l: float,
    so2_libre_actual_mg_l: float,
    so2_libre_objetivo_mg_l: float = 32.0,
    ph: float = 3.60
) -> Dict[str, Any]:
    """
    Calcula la micro-adición exacta de Metabisulfito de Potasio para una barrica individual (225 L / 300 L).

    En bodega se utilizan frecuentemente:
    - Solución acuosa de bisulfito de potasio al 5% o 8%.
    - Metabisulfito de potasio en polvo disuelto previamente en 1 L de vino.
    - Pastillas efervescentes calibradas (Sulfitation tablets de 2g o 5g).
    """
    if capacidad_l <= 0 or so2_libre_actual_mg_l < 0 or so2_libre_objetivo_mg_l < 0:
        raise ValueError("Parámetros deben ser valores no negativos.")

    delta_so2 = max(0.0, so2_libre_objetivo_mg_l - so2_libre_actual_mg_l)
    volumen_hl = capacidad_l / 100.0

    # K2S2O5 (g) = (ΔSO2 [mg/L] * hL) / 5.0
    gramos_k2s2o5 = (delta_so2 * volumen_hl) / 5.0

    # Solución de bisulfito al 5% (50 g/L SO2 disponible -> 1 mL aporta 50 mg SO2)
    # mL solución al 5% = (ΔSO2 mg/L * Capacidad L) / 50 mg/mL
    ml_solucion_5pct = (delta_so2 * capacidad_l) / 50.0

    pka = 1.81 + (0.005 * (15.0 - 20.0))  # Cava a 15°C
    so2_molecular_actual = so2_libre_actual_mg_l / (1.0 + math.pow(10.0, (ph - pka)))
    so2_molecular_proyectado = so2_libre_objetivo_mg_l / (1.0 + math.pow(10.0, (ph - pka)))

    return {
        "capacidad_barrica_l": capacidad_l,
        "delta_so2_mg_l": round(delta_so2, 1),
        "gramos_k2s2o5_polvo": round(gramos_k2s2o5, 2),
        "ml_solucion_bisulfito_5pct": round(ml_solucion_5pct, 1),
        "so2_molecular_actual": round(so2_molecular_actual, 3),
        "so2_molecular_post_ajuste": round(so2_molecular_proyectado, 3)
    }


def evaluar_riesgo_brettanomyces(
    so2_libre_mg_l: float,
    ph: float,
    ano_uso_barrica: int,
    meses_en_roble: int
) -> Dict[str, Any]:
    """
    Evalúa el índice de susceptibilidad microbiológica de una barrica a contaminación por Brettanomyces bruxellensis.
    Madera vieja (3er uso o más) y bajo SO2 molecular conllevan el riesgo más severo.
    """
    pka = 1.81
    so2_mol = so2_libre_mg_l / (1.0 + math.pow(10.0, (ph - pka)))

    puntos_riesgo = 0
    if so2_mol < 0.40:
        puntos_riesgo += 50
    elif so2_mol < 0.55:
        puntos_riesgo += 25

    if ano_uso_barrica >= 3:
        puntos_riesgo += 30
    elif ano_uso_barrica == 2:
        puntos_riesgo += 15

    if meses_en_roble >= 12:
        puntos_riesgo += 20

    if puntos_riesgo >= 60:
        nivel_riesgo = "Crítico / Alto Riesgo"
        accion = "Urgente: Muestreo de laboratorio (qPCR o epifluorescencia para Brettanomyces) y corrección inmediata de SO2."
    elif puntos_riesgo >= 30:
        nivel_riesgo = "Moderado"
        accion = "Control preventivo: mantención de ouillage estricto y chequeo de sulfuroso quincenal."
    else:
        nivel_riesgo = "Bajo / Protegido"
        accion = "Población microbiana bajo control por presión selectiva del SO2 molecular."

    return {
        "so2_molecular_mg_l": round(so2_mol, 3),
        "score_riesgo": puntos_riesgo,
        "nivel_riesgo": nivel_riesgo,
        "accion_recomendada": accion
    }
