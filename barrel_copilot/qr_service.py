"""
QR Code Generation & Mobile Traceability Service
Generates vector SVGs and printable labels for oak barrels.
Author: Cristián González Huenchún
"""

import io
from pathlib import Path
from typing import Optional
import qrcode
import qrcode.image.svg


def generar_enlace_inspeccion(
    barrica_id: str,
    base_url: str = "http://localhost:8070"
) -> str:
    """Genera la URL de inspección móvil para la ficha viva de la barrica."""
    return f"{base_url}/index.html?barrica={barrica_id}"


def generar_codigo_qr_svg(
    barrica_id: str,
    base_url: str = "http://localhost:8070",
    tamano_caja: int = 10,
    borde: int = 2
) -> str:
    """
    Genera un código QR en formato vectorial SVG nativo (ideal para impresión térmica o grabado láser).
    """
    enlace = generar_enlace_inspeccion(barrica_id, base_url)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=tamano_caja,
        border=borde,
        image_factory=qrcode.image.svg.SvgPathImage
    )
    qr.add_data(enlace)
    qr.make(fit=True)

    img = qr.make_image(attrib={'class': 'barrel-qr-svg'})
    stream = io.BytesIO()
    img.save(stream)
    return stream.getvalue().decode('utf-8')


def guardar_qr_en_disco(
    barrica_id: str,
    directorio_salida: str,
    base_url: str = "http://localhost:8070"
) -> str:
    """Guarda el código QR como archivo SVG en disco y retorna la ruta."""
    out_dir = Path(directorio_salida)
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_content = generar_codigo_qr_svg(barrica_id, base_url)
    file_path = out_dir / f"{barrica_id}.svg"
    file_path.write_text(svg_content, encoding="utf-8")
    return str(file_path)
