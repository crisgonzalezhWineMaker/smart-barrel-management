"""
Evaporative Loss Modeling & Ouillage (Topping-Up) Scheduling
Simulates the 'Part des Anges' (Angel's Share) in oak barrels as a function of cellar climate.
Author: Cristián González Huenchún
"""

from typing import Dict, Any


def calcular_tasa_evaporacion(
    temperatura_c: float,
    humedad_relativa_pct: float,
    capacidad_barrica_l: float = 225.0,
    ano_uso: int = 1
) -> Dict[str, float]:
    """
    Calcula la tasa de transpiración y evaporación de vino a través de las duelas de roble.

    Factores físicos:
    - Humedad óptima de cava: 75% - 85% HR.
    - Si HR < 70%: La evaporación de agua se acelera drásticamente, aumentando la merma volumétrica.
    - Temperatura de guarda óptima: 14°C - 16°C. Si T > 18°C, la cinética de pérdida se incrementa.
    - Madera nueva (1er uso): Mayor porosidad y absorción inicial que maderas de 3er uso.

    Returns:
        Diccionario con tasa en mL/día, L/mes y porcentaje de merma anual estimado.
    """
    # Tasa base para 225 L a 15°C y 80% HR: aprox. 24 mL/día (aprox. 8.8 L/año = 3.9% anual)
    tasa_base_ml_dia = 24.0 * (capacidad_barrica_l / 225.0)

    # Factor térmico (Q10 aproximado para evaporación en cava)
    factor_temp = 1.0 + (max(0.0, temperatura_c - 15.0) * 0.08) - (max(0.0, 15.0 - temperatura_c) * 0.04)

    # Factor de humedad relativa
    # A 85% HR -> factor 0.75; a 60% HR -> factor 1.60
    factor_hr = 1.0 + ((80.0 - humedad_relativa_pct) * 0.025)
    factor_hr = max(0.5, min(2.5, factor_hr))

    # Factor de uso de madera (barricas nuevas absorben más en los primeros 6 meses)
    factor_uso = 1.25 if ano_uso == 1 else (1.0 if ano_uso == 2 else 0.85)

    ml_dia = tasa_base_ml_dia * factor_temp * factor_hr * factor_uso
    l_mes = (ml_dia * 30.4) / 1000.0
    l_ano = (ml_dia * 365.25) / 1000.0
    pct_anual = (l_ano / capacidad_barrica_l) * 100.0

    return {
        "ml_por_dia": round(ml_dia, 1),
        "litros_por_mes": round(l_mes, 2),
        "litros_por_ano": round(l_ano, 2),
        "merma_porcentual_anual": round(pct_anual, 2)
    }


def calcular_necesidad_ouillage(
    dias_desde_ultimo_ouillage: int,
    temperatura_c: float,
    humedad_relativa_pct: float,
    capacidad_barrica_l: float = 225.0
) -> Dict[str, Any]:
    """
    Evalúa el estado de merma y determina la urgencia del próximo relleno.

    Umbrales de Gestión en Bodega Boutique:
    - Normal / Seguro: < 14 días (Merma < 0.5 L)
    - Atención: 15 a 24 días (Merma 0.5 - 1.2 L)
    - Crítico / Ouillage Urgente: >= 25 días (Merma > 1.2 L, formación de cámara de aire)
    """
    tasa = calcular_tasa_evaporacion(temperatura_c, humedad_relativa_pct, capacidad_barrica_l)
    merma_acumulada_l = (tasa["ml_por_dia"] * dias_desde_ultimo_ouillage) / 1000.0

    if dias_desde_ultimo_ouillage >= 25 or merma_acumulada_l >= 1.2:
        urgencia = "Urgente"
        estado_alerta = "danger"
        recomendacion = "Ejecutar ouillage inmediatamente. Riesgo inminente de picado acético por Acetobacter aceti."
    elif dias_desde_ultimo_ouillage >= 15 or merma_acumulada_l >= 0.6:
        urgencia = "Próximo (Esta Semana)"
        estado_alerta = "warning"
        recomendacion = "Programar relleno dentro de los próximos 3 a 5 días laborables."
    else:
        urgencia = "Óptimo"
        estado_alerta = "optimal"
        recomendacion = "Nivel de vino adecuado. Barrica llena sin cámara de aire significativa."

    return {
        "dias_transcurridos": dias_desde_ultimo_ouillage,
        "merma_acumulada_litros": round(merma_acumulada_l, 2),
        "urgencia": urgencia,
        "nivel_alerta": estado_alerta,
        "vino_requerido_relleno_l": round(merma_acumulada_l, 2),
        "recomendacion": recomendacion
    }
