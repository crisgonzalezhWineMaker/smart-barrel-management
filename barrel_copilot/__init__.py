"""
Smart Barrel Copilot & Cellar QR Intelligence
Professional Oak Aging, Evaporative Loss (Ouillage), and Traceability Management.
Author: Cristián González Huenchún (Agronomist & M.Sc. Enology Candidate, University of Chile)
"""

from .models import Barrica, Toneleria, OrigenRoble, NivelTostado, EstadoBarrica
from .ouillage import calcular_tasa_evaporacion, calcular_necesidad_ouillage
from .so2_safety import calcular_microadicion_so2_barrica, evaluar_riesgo_brettanomyces
from .qr_service import generar_codigo_qr_svg, generar_enlace_inspeccion
from .database import CellarDatabase

__version__ = "1.0.0"
__author__ = "Cristián González Huenchún"
__all__ = [
    "Barrica",
    "Toneleria",
    "OrigenRoble",
    "NivelTostado",
    "EstadoBarrica",
    "calcular_tasa_evaporacion",
    "calcular_necesidad_ouillage",
    "calcular_microadicion_so2_barrica",
    "evaluar_riesgo_brettanomyces",
    "generar_codigo_qr_svg",
    "generar_enlace_inspeccion",
    "CellarDatabase"
]
