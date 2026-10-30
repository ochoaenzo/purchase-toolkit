"""Localización y extracción del campo Observaciones embebido en el PDF de una orden."""

import logging
import re
from pathlib import Path

from purchase_toolkit.extract.observations import ObservationsExtractor
from purchase_toolkit.utils.pdf import (
    ensure_folder_exists,
    list_pdf_files,
    read_pdf_text,
)
from purchase_toolkit.utils.pdf import (
    get_order_number as get_order_number_from_filename,
)

logger = logging.getLogger(__name__)


class PurchaseOrderObservationsExtractor:
    """Localiza y extrae el campo Observaciones desde el PDF de una orden de compra."""

    def __init__(
        self,
        order_number_pattern: str = r"(?i)^(\d{5})\.pdf$",
        field_separator: str = "|",
        key_value_separator: str = "=",
    ):
        """Inicializa el extractor.

        Args:
            order_number_pattern: expresión regular usada para reconocer el PDF
                de una orden de compra y extraer su número desde el nombre de
                archivo. Debe contener un único grupo de captura con el número
                de orden. Por defecto solo matchea el archivo base de la orden
                (ej. `10001.pdf`), no sus respaldos (ej. `10001_auth.pdf`).
            field_separator: carácter usado para separar los pares CLAVE=VALOR
                dentro de una misma línea de Observaciones.
            key_value_separator: carácter usado para separar la clave del valor
                dentro de un par.
        """
        self._order_number_pattern = order_number_pattern
        # Línea de Observaciones embebida en el PDF: uno o más pares CLAVE=VALOR,
        # delimitada por el separador de campo al principio y al final
        # (ej. "| A=B | C=D |").
        separator = re.escape(field_separator)
        self._observations_line_pattern = re.compile(
            rf"^\s*{separator}.*{separator}\s*$"
        )
        self._observations_extractor = ObservationsExtractor(
            field_separator=field_separator,
            key_value_separator=key_value_separator,
        )

    def get_order_number(self, filename: str) -> str | None:
        """Extrae el número de orden de compra a partir del nombre de archivo.

        Args:
            filename: nombre del archivo (no el path completo).

        Returns:
            El número de orden como string, o None si el nombre no matchea
            el patrón configurado.
        """
        return get_order_number_from_filename(filename, self._order_number_pattern)

    def find_observations_text(self, pdf_text: str) -> str:
        """Aísla, dentro del texto completo de un PDF, las líneas de Observaciones.

        Descarta todo el contenido del PDF que no tenga el formato
        `| CLAVE=VALOR | ... |` (líneas que empiezan y terminan con el
        separador de campo configurado).

        Args:
            pdf_text: texto completo extraído de un PDF (ver `utils.pdf.read_pdf_text`).

        Returns:
            Únicamente las líneas del texto que matchean el formato de
            Observaciones, unidas por salto de línea. Cadena vacía si ninguna
            línea matchea.
        """
        observation_lines = [
            line
            for line in pdf_text.splitlines()
            if self._observations_line_pattern.match(line)
        ]
        if not observation_lines:
            logger.warning("No se encontró texto de Observaciones en el PDF.")
        return "\n".join(observation_lines)

    def extract_from_pdf(self, pdf_path: Path) -> dict[str, str]:
        """Extrae los campos de Observaciones embebidos en un PDF de orden de compra.

        Args:
            pdf_path: path al PDF de la orden de compra ya emitida.

        Returns:
            Diccionario con los pares CLAVE=VALOR encontrados en el bloque de
            Observaciones. Diccionario vacío si no se encontró el bloque.
        """
        pdf_text = read_pdf_text(pdf_path)
        observations_text = self.find_observations_text(pdf_text)
        return self._observations_extractor.extract(observations_text)

    def extract_from_folder(self, source_folder: Path) -> dict[str, dict[str, str]]:
        """Extrae los campos de Observaciones de los PDF de órdenes de una carpeta.

        Solo se procesan los PDF de órdenes de compra, reconocidos por nombre
        de archivo (ver `get_order_number`). Los demás archivos (respaldos,
        presupuestos, etc.) se ignoran y quedan registrados en el log a nivel
        DEBUG.

        Args:
            source_folder: carpeta que contiene los PDF de órdenes de compra
                ya emitidas.

        Returns:
            Diccionario que mapea número de orden a los campos de Observaciones
            extraídos de su PDF correspondiente.

        Raises:
            FileNotFoundError: si `source_folder` no existe.
        """
        ensure_folder_exists(source_folder)

        pdf_files = list_pdf_files(source_folder)
        logger.info(
            "Se encontraron %d archivos PDF en %s",
            len(pdf_files),
            source_folder,
        )

        results: dict[str, dict[str, str]] = {}
        skipped_count = 0
        for file in pdf_files:
            order_number = self.get_order_number(file.name)
            if order_number is None:
                logger.debug(
                    "Archivo ignorado, no es un PDF de orden de compra: %s",
                    file.name,
                )
                skipped_count += 1
                continue

            fields = self.extract_from_pdf(file)
            results[order_number] = fields
            logger.debug(
                "Orden %s: %d campo(s) extraídos de %s",
                order_number,
                len(fields),
                file.name,
            )

        logger.info(
            "Extracción completa: %d orden(es) procesadas, %d archivo(s) ignorados.",
            len(results),
            skipped_count,
        )
        return results
