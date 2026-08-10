"""Extracción de campos estructurados del campo Observaciones de una orden de compra."""

import logging

logger = logging.getLogger(__name__)


class ObservationsExtractor:
    """Parsea el esquema CLAVE=VALOR del campo Observaciones de una orden de compra."""

    def __init__(self, field_separator: str = "|", key_value_separator: str = "="):
        """Inicializa el extractor.

        Args:
            field_separator: carácter usado para separar los pares CLAVE=VALOR
                dentro de una misma línea.
            key_value_separator: carácter usado para separar la clave del valor
                dentro de un par.
        """
        self._field_separator = field_separator
        self._key_value_separator = key_value_separator

    def extract(self, text: str) -> dict[str, str]:
        """Extrae todos los pares CLAVE=VALOR presentes en el texto.

        Args:
            text: texto del campo Observaciones a parsear.

        Returns:
            Diccionario con cada clave encontrada y su valor asociado.
        """
        fields: dict[str, str] = {}

        for line in text.splitlines():
            for fragment in line.split(self._field_separator):
                fragment = fragment.strip()
                if not fragment:
                    continue

                parts = fragment.split(self._key_value_separator, maxsplit=1)
                if len(parts) != 2:
                    logger.warning("Fragmento ignorado, formato inválido: %r", fragment)
                    continue

                key, value = parts[0].strip(), parts[1].strip()
                if not key:
                    logger.warning("Fragmento ignorado, clave vacía: %r", fragment)
                    continue

                if key in fields:
                    logger.warning(
                        "Clave duplicada '%s', se conserva el último valor: %s",
                        key,
                        value,
                    )
                fields[key] = value

        logger.info(
            "Se extrajeron %d campo(s) del texto de Observaciones.",
            len(fields),
        )
        return fields
