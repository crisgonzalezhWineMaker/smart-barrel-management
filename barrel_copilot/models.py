"""
Core Domain Models for Oak Barrels and Cellar Management
Author: Cristián González Huenchún
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, date


class Toneleria(str, Enum):
    TARANSAUD = "Taransaud"
    SEGUIN_MOREAU = "Seguin Moreau"
    RADOUX = "Radoux"
    SYLVAIN = "Sylvain"
    FRANCOIS_FRERES = "François Frères"
    DAMY = "Damy"
    NADALIE = "Nadalié"
    CANTON = "Canton"


class OrigenRoble(str, Enum):
    FRANCES_ALLIER = "Roble Francés (Allier)"
    FRANCES_TRONCAIS = "Roble Francés (Tronçais)"
    FRANCES_VOSGES = "Roble Francés (Vosges)"
    FRANCES_NEVERS = "Roble Francés (Nevers)"
    AMERICANO = "Roble Americano (Missouri/Virginia)"
    EUROPEO_ORIENTAL = "Roble Europeo (Cáucaso/Hungría)"


class NivelTostado(str, Enum):
    LIGERO = "Ligero (L)"
    MEDIO = "Medio (M)"
    MEDIO_PLUS = "Medio Plus (M+)"
    FUERTE = "Fuerte (H)"


class EstadoBarrica(str, Enum):
    OPTIMO = "Óptimo"
    REQUIERE_OUILLAGE = "Requiere Ouillage"
    ALERTA_SO2 = "Alerta SO₂ Bajo"
    RIESGO_VOLATIL = "Riesgo Acidez Volátil"
    LAVADO_MANTENCION = "En Lavado / Vacía"


@dataclass
class Barrica:
    """Representa una barrica individual física en la cava."""
    id: str  # Código único (ej: "BAR-2025-014")
    rack: str  # Identificador de rack (ej: "Rack A")
    posicion_x: int  # Columna (1-6)
    posicion_y: int  # Nivel de altura (1-3)
    toneleria: str
    origen_roble: str
    tostado: str
    capacidad_l: float  # 225.0 o 300.0 L
    ano_compra: int
    ano_uso: int  # 1 = 1er uso (nueva), 2 = 2do uso, etc.
    vino_contenido: str  # Ej: "Cabernet Sauvignon - Cuartel 12 VIK"
    cosecha: int
    lote: str
    ph: float
    so2_libre_mg_l: float
    fecha_ultimo_ouillage: str  # "YYYY-MM-DD"
    dias_sin_ouillage: int
    merma_acumulada_l: float
    estado: str
    notas_enologo: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def so2_molecular(self) -> float:
        """Calcula el SO2 molecular a 16°C."""
        pka = 1.81 + (0.005 * (16.0 - 20.0))
        return round(self.so2_libre_mg_l / (1.0 + 10.0 ** (self.ph - pka)), 3)
