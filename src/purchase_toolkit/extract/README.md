# extract

Extracción de campos estructurados a partir del texto del campo Observaciones de una orden de compra.

## Instalación

Este módulo forma parte del paquete `purchase-toolkit`. No requiere instalación separada; una vez instalado el paquete, se importa directamente:

```python
from purchase_toolkit.extract.observations import ObservationsExtractor
```

## Uso básico

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

`extract` recibe el texto ya aislado del campo Observaciones (como string) y devuelve un diccionario con todos los pares clave-valor encontrados. No se ocupa de localizar ni extraer ese texto desde un PDF; esa responsabilidad queda fuera del módulo.

## Comportamiento

### Formato esperado

El texto se compone de líneas, cada una con uno o más pares `CLAVE=VALOR` agrupados entre un separador de campo (`|` por defecto). El extractor no distingue a qué línea pertenecía cada clave: el resultado es siempre un único diccionario plano con todas las claves encontradas en el texto completo, sin importar en qué línea estaban agrupadas.

### Totalidad de los campos

El extractor no valida las claves contra ninguna lista predefinida: devuelve cualquier par `CLAVE=VALOR` que encuentre, sin distinción. Esto incluye claves dinámicas (por ejemplo, distintas variantes de una misma familia de claves con un sufijo variable), que se extraen igual que cualquier otra sin necesidad de conocerlas de antemano.

### Sin validación de tipos

Los valores se devuelven siempre como string, tal cual aparecen en el texto. El extractor no valida formato (fechas, números, separador decimal, etc.) ni convierte tipos — esa responsabilidad queda del lado de quien consuma los campos extraídos.

### Manejo de casos inválidos

- Un fragmento sin el separador clave-valor se ignora y se registra como advertencia.
- Una clave vacía se ignora y se registra como advertencia.
- Si una clave aparece más de una vez en el texto, se conserva el último valor encontrado y se registra como advertencia.
- Espacios en blanco alrededor de clave y valor se eliminan automáticamente.
- Un texto vacío o sin ningún par válido devuelve un diccionario vacío, sin lanzar ninguna excepción.

## Extensión

Los separadores usados para interpretar el texto son configurables, para adaptarse a otros formatos sin modificar la clase:

```python
# Por defecto: "|" separa campos, "=" separa clave de valor
extractor = ObservationsExtractor()

# Ejemplo alternativo: ";" separa campos, ":" separa clave de valor
extractor = ObservationsExtractor(field_separator=";", key_value_separator=":")
```

## Logging

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

## Manejo de errores

`extract` no lanza excepciones ante texto mal formado: los fragmentos inválidos se ignoran y se registran como advertencia, sin interrumpir el procesamiento del resto del texto.

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
