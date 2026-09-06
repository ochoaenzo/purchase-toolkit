# extract

Extracción de campos estructurados a partir del texto del campo Observaciones de una orden de compra.

El módulo tiene dos clases con responsabilidades distintas:

- **`ObservationsExtractor`** — parsea el esquema `CLAVE=VALOR` a partir de un texto ya aislado (string). No abre PDFs.
- **`PurchaseOrderObservationsExtractor`** — dado el PDF de una orden de compra ya emitida, localiza el bloque de texto de Observaciones embebido en él y lo parsea, reutilizando `ObservationsExtractor` internamente.

## Instalación

Este módulo forma parte del paquete `purchase-toolkit`. No requiere instalación separada; una vez instalado el paquete, se importa directamente:

```python
from purchase_toolkit.extract.observations import ObservationsExtractor
from purchase_toolkit.extract.purchase_order_pdf import PurchaseOrderObservationsExtractor
```

## `ObservationsExtractor`

### Uso básico

```python
from purchase_toolkit.extract.observations import ObservationsExtractor

texto = """
| TIPO_OC=ABONO | FECHA_ABONO=2026-07 |
| PRESUPUESTO=1234 |
"""

extractor = ObservationsExtractor()
campos = extractor.extract(texto)
# {'TIPO_OC': 'ABONO', 'FECHA_ABONO': '2026-07', 'PRESUPUESTO': '1234'}
```

`ObservationsExtractor.extract` recibe el texto ya aislado del campo Observaciones (como string) y devuelve un diccionario con todos los pares clave-valor encontrados. No se ocupa de localizar ni extraer ese texto desde un PDF; esa responsabilidad la cubre `PurchaseOrderObservationsExtractor`, documentada más abajo.

### Comportamiento

#### Formato esperado

El texto se compone de líneas, cada una con uno o más pares `CLAVE=VALOR` agrupados entre un separador de campo (`|` por defecto). El extractor no distingue a qué línea pertenecía cada clave: el resultado es siempre un único diccionario plano con todas las claves encontradas en el texto completo, sin importar en qué línea estaban agrupadas.

#### Totalidad de los campos

El extractor no valida las claves contra ninguna lista predefinida: devuelve cualquier par `CLAVE=VALOR` que encuentre, sin distinción. Esto incluye claves dinámicas (por ejemplo, distintas variantes de una misma familia de claves con un sufijo variable), que se extraen igual que cualquier otra sin necesidad de conocerlas de antemano.

#### Sin validación de tipos

Los valores se devuelven siempre como string, tal cual aparecen en el texto. El extractor no valida formato (fechas, números, separador decimal, etc.) ni convierte tipos — esa responsabilidad queda del lado de quien consuma los campos extraídos.

#### Manejo de casos inválidos

- Un fragmento sin el separador clave-valor se ignora y se registra como advertencia.
- Una clave vacía se ignora y se registra como advertencia.
- Si una clave aparece más de una vez en el texto, se conserva el último valor encontrado y se registra como advertencia.
- Espacios en blanco alrededor de clave y valor se eliminan automáticamente.
- Un texto vacío o sin ningún par válido devuelve un diccionario vacío, sin lanzar ninguna excepción.

### Extensión

Los separadores usados para interpretar el texto son configurables, para adaptarse a otros formatos sin modificar la clase:

```python
# Por defecto: "|" separa campos, "=" separa clave de valor
extractor = ObservationsExtractor()

# Ejemplo alternativo: ";" separa campos, ":" separa clave de valor
extractor = ObservationsExtractor(field_separator=";", key_value_separator=":")
```

### Logging

El módulo usa el sistema estándar de `logging` de Python, bajo el logger `purchase_toolkit.extract.observations`. No imprime nada por consola directamente (`print`); es responsabilidad de quien use el módulo configurar el nivel de verbosidad deseado, por ejemplo:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Niveles utilizados:

- **INFO** — fin del proceso, con la cantidad de campos extraídos:
  ```
  INFO: Se extrajeron 3 campo(s) del texto de Observaciones.
  ```
- **WARNING** — un fragmento no tiene el formato esperado, una clave está vacía, o una clave aparece duplicada:
  ```
  WARNING: Fragmento ignorado, formato inválido: 'texto_sin_formato'
  WARNING: Clave duplicada 'PRESUPUESTO', se conserva el último valor encontrado: 2222
  ```

### Manejo de errores

`ObservationsExtractor.extract` no lanza excepciones ante texto mal formado: los fragmentos inválidos se ignoran y se registran como advertencia, sin interrumpir el procesamiento del resto del texto.

## `PurchaseOrderObservationsExtractor`

El texto de Observaciones se genera con un formulario externo ([`purchase-order-observations`](https://github.com/ochoaenzo/purchase-order-observations)), se pega manualmente en el ERP al emitir la orden, y reaparece embebido como texto plano dentro del PDF de la orden ya emitida, con formato de líneas `| CLAVE=VALOR | CLAVE=VALOR |`. `PurchaseOrderObservationsExtractor` abre ese PDF, localiza únicamente esas líneas dentro de todo el contenido del PDF, y delega el parseo en `ObservationsExtractor`.

### Uso básico

```python
from pathlib import Path
from purchase_toolkit.extract.purchase_order_pdf import PurchaseOrderObservationsExtractor

extractor = PurchaseOrderObservationsExtractor()

# Un único PDF
campos = extractor.extract_from_pdf(Path("ordenes/10001.pdf"))
# {'TIPO_OC': 'ABONO', 'FECHA_ABONO': '2026-07', 'PRESUPUESTO': '1234'}

# Todos los PDF de una carpeta, agrupados por número de orden
resultados = extractor.extract_from_folder(Path("ordenes/"))
# {'10001': {...}, '10002': {...}}
```

### Comportamiento

#### Localización del texto de Observaciones

`find_observations_text` recorre línea por línea el texto completo extraído del PDF y conserva únicamente las que empiezan y terminan con el separador de campo (`|` por defecto) — el resto del contenido del PDF (razón social, montos, etc.) se descarta antes de llegar a `ObservationsExtractor`. Si ninguna línea matchea, devuelve una cadena vacía y registra una advertencia.

#### Número de orden

El número de orden se extrae del nombre de archivo con [`purchase_toolkit.utils.pdf.get_order_number`](../utils/README.md#referencia-de-la-api), la misma función que usa [`merge`](../merge/README.md#extensión), con el mismo patrón por defecto — configurable vía `order_number_pattern`.

#### Procesamiento por carpeta

`extract_from_folder` agrupa el resultado por número de orden. Un archivo cuyo nombre no matchea el patrón configurado se ignora y queda registrado en el log como advertencia, igual que en `merge`.

### Extensión

```python
# Por defecto: número de 5 dígitos al inicio del nombre, "|" separa campos, "=" separa clave de valor
extractor = PurchaseOrderObservationsExtractor()

# Personalizando patrón de orden y separadores del texto de Observaciones
extractor = PurchaseOrderObservationsExtractor(
    order_number_pattern=r"^([A-Z]{2}\d{3})",
    field_separator=";",
    key_value_separator=":",
)
```

### Logging

Usa el logger `purchase_toolkit.extract.purchase_order_pdf`, con niveles INFO/DEBUG/WARNING análogos a los de `merge` (ver [`merge/README.md`](../merge/README.md#logging)), más un WARNING específico cuando no se encuentra texto de Observaciones en un PDF. Al delegar el parseo en `ObservationsExtractor`, cada llamada a `extract_from_pdf` también emite los registros de ese logger (`purchase_toolkit.extract.observations`), descriptos en la sección [Logging](#logging) de `ObservationsExtractor` más arriba.

### Manejo de errores

`extract_from_folder` lanza `FileNotFoundError` si `source_folder` no existe. No se capturan ni silencian otras excepciones (por ejemplo, errores al leer un PDF corrupto); estas se propagan tal cual las lanza `pypdf`.

## Referencia de la API

### `ObservationsExtractor`

```python
ObservationsExtractor(field_separator: str = "|", key_value_separator: str = "=")
```

Constructor. Recibe los separadores usados para interpretar el texto.

```python
extract(text: str) -> dict[str, str]
```

Extrae todos los pares `CLAVE=VALOR` presentes en el texto.

### `PurchaseOrderObservationsExtractor`

```python
PurchaseOrderObservationsExtractor(
    order_number_pattern: str = r"^(\d{5})",
    field_separator: str = "|",
    key_value_separator: str = "=",
)
```

Constructor. Recibe el patrón de número de orden y los separadores usados internamente por `ObservationsExtractor`.

```python
get_order_number(filename: str) -> str | None
```

Extrae el número de orden de compra de un nombre de archivo. Devuelve `None` si no matchea el patrón configurado.

```python
find_observations_text(pdf_text: str) -> str
```

Aísla, dentro del texto completo de un PDF, las líneas con formato `| CLAVE=VALOR | ... |`. Devuelve cadena vacía si ninguna matchea.

```python
extract_from_pdf(pdf_path: Path) -> dict[str, str]
```

Lee el PDF, localiza el texto de Observaciones y devuelve los campos extraídos.

```python
extract_from_folder(source_folder: Path) -> dict[str, dict[str, str]]
```

Extrae los campos de Observaciones de todos los PDF de `source_folder`, agrupados por número de orden. Lanza `FileNotFoundError` si `source_folder` no existe.
