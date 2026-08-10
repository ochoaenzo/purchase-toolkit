"""Ejemplo de uso

Agrupa los PDF individuales de cada orden de compra en un único archivo por
orden, usando purchase_toolkit.merge.PurchaseOrderPdfMerger.
"""

import logging
from pathlib import Path

from purchase_toolkit.merge.purchase_orders_pdf import PurchaseOrderPdfMerger

# Reemplazá estos paths por los reales en tu máquina antes de correr el script.
SOURCE_FOLDER = Path("ruta/a/tus/pdf/individuales")
DESTINATION_FOLDER = Path("ruta/a/tus/pdf/unificados")


def main() -> None:
    # El toolkit no imprime nada por consola; el nivel de verbosidad se define acá.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.getLogger("pypdf").setLevel(logging.ERROR)

    # Agrupar los PDF por orden de compra.
    merger = PurchaseOrderPdfMerger()
    merger.merge(SOURCE_FOLDER, DESTINATION_FOLDER)


if __name__ == "__main__":
    main()
