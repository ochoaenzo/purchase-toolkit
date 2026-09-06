"""Utilidades genéricas para el manejo de archivos PDF.

Funciones de uso compartido entre las herramientas del paquete
(`merge`, `extract`, `audit`), sin lógica específica de ninguna de ellas.
"""

import re
from pathlib import Path

from pypdf import PdfReader


def get_order_number(filename: str, pattern: str = r"^(\d{5})") -> str | None:
    """Extrae el número de orden de compra a partir del nombre de archivo.

    Args:
        filename: nombre del archivo (no el path completo).
        pattern: expresión regular con un único grupo de captura correspondiente
            al número de orden.

    Returns:
        El número de orden como string, o None si el nombre no matchea el patrón.
    """
    match = re.match(pattern, filename)
    return match.group(1) if match else None


def list_pdf_files(folder: Path) -> list[Path]:
    """Lista los archivos `.pdf` de primer nivel dentro de `folder`.

    Args:
        folder: carpeta a inspeccionar. Debe existir.

    Returns:
        Lista de paths a archivos `.pdf` (comparación de extensión insensible
        a mayúsculas/minúsculas). No incluye subcarpetas.
    """
    return [
        file
        for file in folder.iterdir()
        if file.is_file() and file.suffix.lower() == ".pdf"
    ]


def ensure_folder_exists(folder: Path) -> None:
    """Valida que `folder` exista.

    Args:
        folder: carpeta a validar.

    Raises:
        FileNotFoundError: si `folder` no existe.
    """
    if not folder.exists():
        raise FileNotFoundError(f"La carpeta no existe: {folder}")


def ensure_folder_created(folder: Path) -> None:
    """Crea `folder` (y sus padres) si no existe. No falla si ya existe."""
    folder.mkdir(parents=True, exist_ok=True)


def read_pdf_text(pdf_path: Path) -> str:
    """Lee y concatena el texto de todas las páginas de un PDF.

    Args:
        pdf_path: path al archivo PDF.

    Returns:
        Texto de todas las páginas, en orden, unidas por salto de línea.
        Las páginas sin texto extraíble contribuyen con una cadena vacía.
    """
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)
