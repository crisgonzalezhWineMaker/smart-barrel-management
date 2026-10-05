"""
SQLite Database Layer & Cellar Inventory Management
Preloads realistic winery dataset modeled after premium Chilean wineries (VIK / El Principal).
Author: Cristián González Huenchún
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .models import Barrica, Toneleria, OrigenRoble, NivelTostado, EstadoBarrica


DB_PATH_DEFAULT = Path(__file__).resolve().parent.parent / "cellar.db"


class CellarDatabase:
    """Administra la base de datos local SQLite de la cava de barricas."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH_DEFAULT
        self._mem_conn: Optional[sqlite3.Connection] = None
        if str(self.db_path) == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
        self._init_db()
        self._seed_if_empty()

    def get_connection(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS barricas (
                    id TEXT PRIMARY KEY,
                    rack TEXT NOT NULL,
                    posicion_x INTEGER NOT NULL,
                    posicion_y INTEGER NOT NULL,
                    toneleria TEXT NOT NULL,
                    origen_roble TEXT NOT NULL,
                    tostado TEXT NOT NULL,
                    capacidad_l REAL NOT NULL,
                    ano_compra INTEGER NOT NULL,
                    ano_uso INTEGER NOT NULL,
                    vino_contenido TEXT NOT NULL,
                    cosecha INTEGER NOT NULL,
                    lote TEXT NOT NULL,
                    ph REAL NOT NULL,
                    so2_libre_mg_l REAL NOT NULL,
                    fecha_ultimo_ouillage TEXT NOT NULL,
                    dias_sin_ouillage INTEGER NOT NULL,
                    merma_acumulada_l REAL NOT NULL,
                    estado TEXT NOT NULL,
                    notas_enologo TEXT DEFAULT ''
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS registro_operaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barrica_id TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    tipo_operacion TEXT NOT NULL, -- 'ouillage', 'sulfitado', 'cata', 'trasiego'
                    volumen_agregado_l REAL DEFAULT 0,
                    so2_agregado_g REAL DEFAULT 0,
                    observaciones TEXT,
                    operador TEXT DEFAULT 'Enólogo de Turno',
                    FOREIGN KEY (barrica_id) REFERENCES barricas(id)
                );
            """)

    def _seed_if_empty(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM barricas;")
            if cursor.fetchone()["total"] > 0:
                return

            # Cargar 36 barricas de muestra realista (Rack A: 18, Rack B: 18)
            hoy = datetime.now()
            barricas_muestra = []

            tonelerias_lista = [
                (Toneleria.TARANSAUD.value, OrigenRoble.FRANCES_ALLIER.value, NivelTostado.MEDIO_PLUS.value),
                (Toneleria.SEGUIN_MOREAU.value, OrigenRoble.FRANCES_TRONCAIS.value, NivelTostado.MEDIO.value),
                (Toneleria.RADOUX.value, OrigenRoble.FRANCES_VOSGES.value, NivelTostado.MEDIO.value),
                (Toneleria.SYLVAIN.value, OrigenRoble.FRANCES_ALLIER.value, NivelTostado.MEDIO_PLUS.value),
                (Toneleria.FRANCOIS_FRERES.value, OrigenRoble.FRANCES_TRONCAIS.value, NivelTostado.LIGERO.value),
                (Toneleria.CANTON.value, OrigenRoble.AMERICANO.value, NivelTostado.MEDIO.value)
            ]

            vinos_lista = [
                ("Cabernet Sauvignon (Cuartel 12 - VIK)", 2026, "LOTE-CS-VIK-01", 3.62, 32.0),
                ("Carmenere Selección (Cuartel 05 - VIK)", 2026, "LOTE-CARM-VIK-03", 3.68, 30.0),
                ("Cabernet Sauvignon Gran Reserva (El Principal)", 2025, "LOTE-CS-PRIN-02", 3.58, 34.0),
                ("Chardonnay Fermentado en Barrica (El Principal)", 2025, "LOTE-CHARD-01", 3.32, 28.0),
                ("Syrah Alta Expresión (Valle de Cachapoal)", 2026, "LOTE-SYR-04", 3.65, 31.0)
            ]

            idx = 1
            for rack_nombre in ["Rack A (Nave Principal)", "Rack B (Cava Subterránea)"]:
                for nivel_y in [1, 2, 3]:  # 3 niveles de altura
                    for col_x in [1, 2, 3, 4, 5, 6]:  # 6 posiciones por fila
                        ton, orig, tost = tonelerias_lista[(idx - 1) % len(tonelerias_lista)]
                        vino, cosecha, lote, ph, so2 = vinos_lista[(idx - 1) % len(vinos_lista)]
                        
                        ano_uso = 1 if idx % 3 == 0 else (2 if idx % 2 == 0 else 3)
                        ano_compra = 2026 - (ano_uso - 1)
                        capacidad = 300.0 if "Chardonnay" in vino else 225.0

                        # Generar variedad de estados operativos
                        if idx in [5, 14, 23, 31]:
                            dias_ouillage = 26
                            estado = EstadoBarrica.REQUIERE_OUILLAGE.value
                            merma = 1.35
                        elif idx in [8, 27]:
                            dias_ouillage = 12
                            so2 = 18.0  # Alerta SO2
                            estado = EstadoBarrica.ALERTA_SO2.value
                            merma = 0.40
                        else:
                            dias_ouillage = 8
                            estado = EstadoBarrica.OPTIMO.value
                            merma = 0.28

                        fecha_ult = (hoy - timedelta(days=dias_ouillage)).strftime("%Y-%m-%d")
                        barrica_id = f"BAR-{ano_compra}-{idx:03d}"

                        conn.execute("""
                            INSERT INTO barricas (
                                id, rack, posicion_x, posicion_y, toneleria, origen_roble, tostado,
                                capacidad_l, ano_compra, ano_uso, vino_contenido, cosecha, lote,
                                ph, so2_libre_mg_l, fecha_ultimo_ouillage, dias_sin_ouillage,
                                merma_acumulada_l, estado, notas_enologo
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            barrica_id, rack_nombre, col_x, nivel_y, ton, orig, tost,
                            capacidad, ano_compra, ano_uso, vino, cosecha, lote,
                            ph, so2, fecha_ult, dias_ouillage, merma, estado,
                            "Excelente integración tánica. Notas de vainilla noble y moca."
                        ))
                        idx += 1

    def obtener_todas(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM barricas ORDER BY rack, posicion_y DESC, posicion_x ASC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def obtener_por_id(self, barrica_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM barricas WHERE id = ?;", (barrica_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def registrar_ouillage(self, barrica_id: str, volumen_l: float, operador: str = "Cristián González H.") -> bool:
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE barricas
                SET fecha_ultimo_ouillage = ?, dias_sin_ouillage = 0, merma_acumulada_l = 0.0,
                    estado = ?
                WHERE id = ?;
            """, (hoy, EstadoBarrica.OPTIMO.value, barrica_id))
            conn.execute("""
                INSERT INTO registro_operaciones (barrica_id, fecha, tipo_operacion, volumen_agregado_l, operador)
                VALUES (?, ?, 'ouillage', ?, ?);
            """, (barrica_id, hoy, volumen_l, operador))
            return True

    def registrar_sulfitado(self, barrica_id: str, nuevo_so2: float, gramos_k2s2o5: float) -> bool:
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE barricas
                SET so2_libre_mg_l = ?,
                    estado = CASE WHEN dias_sin_ouillage >= 25 THEN 'Requiere Ouillage' ELSE 'Óptimo' END
                WHERE id = ?;
            """, (nuevo_so2, barrica_id))
            conn.execute("""
                INSERT INTO registro_operaciones (barrica_id, fecha, tipo_operacion, so2_agregado_g, observaciones)
                VALUES (?, ?, 'sulfitado', ?, ?);
            """, (barrica_id, hoy, gramos_k2s2o5, f"Ajustado a {nuevo_so2} mg/L SO2 libre"))
            return True
