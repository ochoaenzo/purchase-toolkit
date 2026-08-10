# merge

Unificación de archivos PDF individuales de una misma orden de compra en un único archivo por orden.

## Instalación

Este módulo forma parte del paquete `purchase-toolkit`. No requiere instalación separada; una vez instalado el paquete, se importa directamente:

```python
from purchase_toolkit.merge.purchase_orders_pdf import PurchaseOrderPdfMerger
```

## Uso básico

```python
from pathlib import Path
from purchase_toolkit.merge.purchase_orders_pdf import PurchaseOrderPdfMerger

merger = PurchaseOrderPdfMerger()
merger.merge(
    source_folder=Path("ruta/a/archivos/individuales"),
    destination_folder=Path("ruta/a/archivos/unificados"),
)
```

Esto toma todos los archivos `.pdf` de `source_folder`, los agrupa por número de orden de compra, y escribe un archivo `<numero_de_orden>.pdf` por cada grupo en `destination_folder`. Si `destination_folder` no existe, se crea automáticamente.

## Comportamiento

### Agrupamiento

Los archivos se agrupan según el número de orden de compra extraído de su nombre. Por defecto, se espera que el nombre de archivo comience con un número de 5 dígitos (ej. `25305.pdf`, `25305_auth.pdf`, `25305_ppto.pdf` pertenecen todos a la orden `25305`).

Un archivo cuyo nombre no coincide con el patrón esperado se ignora (no se incluye en ningún PDF combinado) y queda registrado en el log como advertencia.

### Orden de las páginas

Dentro de cada PDF combinado, el archivo cuyo nombre no lleva sufijo (ej. `25305.pdf`) queda siempre como primera página, seguido por el resto de los archivos del mismo grupo en orden alfabético de nombre de archivo (ej. `25305_auth.pdf` antes que `25305_ppto.pdf`).

## Extensión

El patrón usado para reconocer el número de orden es configurable, para adaptarse a otros esquemas de naming sin modificar la clase:

```python
# Por defecto: número de 5 dígitos al inicio del nombre
merger = PurchaseOrderPdfMerger()

# Ejemplo alternativo: prefijo alfanumérico de 2 letras + 3 dígitos
merger = PurchaseOrderPdfMerger(order_number_pattern=r"^([A-Z]{2}\d{3})")
```

El patrón debe ser una expresión regular con un único grupo de captura correspondiente al número de orden.

También se puede usar el método `get_order_number` de forma aislada, sin llamar a `merge`, para simplemente extraer el número de orden de un nombre de archivo:

```python
merger.get_order_number("25305_auth.pdf")  # "25305"
merger.get_order_number("sin_numero.pdf")  # None
```

## Logging

El módulo usa el sistema estándar de `logging` de Python, bajo el logger `purchase_toolkit.merge.purchase_orders_pdf`. No imprime nada por consola directamente (`print`); es responsabilidad de quien use el módulo configurar el nivel de verbosidad deseado, por ejemplo:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Niveles utilizados:

- **INFO** — inicio y fin del proceso, con el conteo de archivos encontrados, órdenes procesadas y archivos ignorados:
  ```
  INFO: Se encontraron 28 archivos PDF en /ruta/tmp_in
  INFO: Unificación completa: 13 orden(es) de compra procesadas, 2 archivo(s) ignorados.
  ```
- **DEBUG** — detalle de cada orden procesada individualmente:
  ```
  DEBUG: Orden 25305: 3 archivo(s) unificados en /ruta/tmp_out/25305.pdf
  ```
- **WARNING** — un archivo no matchea el patrón configurado y fue ignorado:
  ```
  WARNING: Archivo ignorado, no matchea el patrón de orden: notas.pdf
  ```

## Manejo de errores

El método `merge` lanza `FileNotFoundError` si `source_folder` no existe. No se capturan ni silencian otras excepciones (por ejemplo, errores al leer un PDF corrupto); estas se propagan tal cual las lanza `pypdf`.

## Referencia de la API

`PurchaseOrderPdfMerger(order_number_pattern: str = r"^(\d{5})")`

Constructor. Recibe el patrón usado para extraer el número de orden del nombre de archivo.

`get_order_number(filename: str) -> str | None`

Extrae el número de orden de compra de un nombre de archivo. Devuelve `None` si no matchea el patrón configurado.

`merge(source_folder: Path, destination_folder: Path) -> None`

Agrupa y unifica los PDF de `source_folder` en un archivo por orden de compra dentro de `destination_folder`. Lanza `FileNotFoundError` si `source_folder` no existe.
