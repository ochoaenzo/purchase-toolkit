# utils

Utilidades genéricas de manejo de archivos PDF, de uso interno para `merge`, `extract` y `audit`. No expone funcionalidad propia ni figura en la tabla de "Módulos" del [README principal](../../../README.md).

`merge`, `extract` y `audit` importan de `utils`; no se importan entre sí — ver [principio de diseño](../../../README.md#principio-de-diseño).

## Instalación

Este módulo forma parte del paquete `purchase-toolkit`. No requiere instalación separada:

```python
from purchase_toolkit.utils.pdf import get_order_number, list_pdf_files, read_pdf_text
```

## Referencia de la API

Todas las funciones son libres (no hay clases ni estado compartido).

```python
get_order_number(filename: str, pattern: str = r"^(\d{5})") -> str | None
```

Extrae el número de orden de compra a partir del nombre de archivo, según el patrón dado (debe tener un único grupo de captura). Devuelve `None` si no matchea.

```python
list_pdf_files(folder: Path) -> list[Path]
```

Lista los archivos `.pdf` de primer nivel dentro de `folder` (extensión insensible a mayúsculas/minúsculas, no incluye subcarpetas).

```python
ensure_folder_exists(folder: Path) -> None
```

Valida que `folder` exista. Lanza `FileNotFoundError` si no.

```python
ensure_folder_created(folder: Path) -> None
```

Crea `folder` (y sus padres) si no existe. No falla si ya existe.

```python
read_pdf_text(pdf_path: Path) -> str
```

Lee y concatena el texto de todas las páginas de un PDF, unidas por salto de línea.

## Manejo de errores

Ninguna de estas funciones captura ni silencia excepciones más allá de lo documentado explícitamente (`ensure_folder_exists`): errores al leer un PDF corrupto o inaccesible se propagan tal cual los lanza `pypdf`.
