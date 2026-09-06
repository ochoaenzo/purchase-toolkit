"""Unificación de archivos PDF individuales de una misma orden de compra."""

import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from purchase_toolkit.utils.pdf import (
    ensure_folder_created,
    ensure_folder_exists,
    list_pdf_files,
)
from purchase_toolkit.utils.pdf import (
    get_order_number as get_order_number_from_filename,
)

logger = logging.getLogger(__name__)


class PurchaseOrderPdfMerger:
    """Combina los PDF de una misma orden de compra en un único archivo."""

    def __init__(self, order_number_pattern: str = r"^(\d{5})"):
        """Inicializa el merger.

        Args:
            order_number_pattern: expresión regular usada para extraer el número
                de orden de compra desde el nombre de archivo. Debe contener un
                único grupo de captura con el número de orden.
        """
        self._order_number_pattern = order_number_pattern

    def get_order_number(self, filename: str) -> str | None:
        """Extrae el número de orden de compra a partir del nombre de archivo.

        Args:
            filename: nombre del archivo (no el path completo).

        Returns:
            El número de orden como string, o None si el nombre no matchea
            el patrón configurado.
        """
        return get_order_number_from_filename(filename, self._order_number_pattern)

    def merge(self, source_folder: Path, destination_folder: Path) -> None:
        """Agrupa los PDF de `source_folder` en un archivo por orden de compra.

        Los archivos se agrupan por número de orden (ver `get_order_number`).
        Dentro de cada grupo, el archivo base de la orden (sin sufijo) queda
        siempre primero, seguido por los archivos de respaldo (presupuesto,
        autorización, etc.) en orden alfabético de nombre de archivo.

        Args:
            source_folder: carpeta que contiene los PDF individuales a agrupar.
            destination_folder: carpeta donde se escribe un PDF por orden de compra.
                Se crea si no existe.

        Raises:
            FileNotFoundError: si `source_folder` no existe.
        """
        ensure_folder_exists(source_folder)
        ensure_folder_created(destination_folder)

        pdf_files = list_pdf_files(source_folder)
        logger.info(
            "Se encontraron %d archivos PDF en %s",
            len(pdf_files),
            source_folder,
        )

        order_groups: dict[str, list[Path]] = {}
        skipped_count = 0
        for file in pdf_files:
            order_number = self.get_order_number(file.name)
            if order_number is None:
                logger.warning(
                    "Archivo ignorado, no matchea el patrón de orden: %s",
                    file.name,
                )
                skipped_count += 1
                continue
            order_groups.setdefault(order_number, []).append(file)

        for order_number, files in order_groups.items():
            # Orden alfabético: el archivo base (sin sufijo) siempre precede
            # a los archivos de respaldo (que llevan sufijo).
            files.sort(key=lambda f: f.name)

            writer = PdfWriter()
            for file in files:
                reader = PdfReader(file)
                for page in reader.pages:
                    writer.add_page(page)

            output_path = destination_folder / f"{order_number}.pdf"
            with output_path.open("wb") as output_file:
                writer.write(output_file)

            logger.debug(
                "Orden %s: %d archivo(s) unificados en %s",
                order_number,
                len(files),
                output_path,
            )

        logger.info(
            "Unificación completa: %d orden(es) procesadas, %d archivo(s) ignorados.",
            len(order_groups),
            skipped_count,
        )
