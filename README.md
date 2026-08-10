# purchase-toolkit

Conjunto de librerías de Python para digitalizar y dar trazabilidad al circuito de órdenes de compra: auditoría de datos fuente, extracción de campos estructurados y unificación de documentos de respaldo.

## Contexto

Antes de este proyecto, el circuito de aprobación de órdenes de compra dependía enteramente de la revisión manual de las órdenes de compra y su información anexa: sin backup digital estructurado, sin forma sistemática de cruzar lo que se estaba por autorizar contra lo realmente exportado del ERP.

Hoy se dispone de backup digital no solo de la orden de compra en sí, sino también de su autorización, presupuestos y cualquier otra información relevante — todo unificado en un único archivo por orden.

Además, disponer de datos estructurados dentro de cada orden hizo posible automatizar otras tareas que antes no eran viables. Algunos ejemplos de lo que esto permite hoy:

- Detalle de órdenes de compra con pagos anticipados.
- Detalle de órdenes de compra correspondientes a servicios recurrentes (abonos), con la posibilidad de cruzarlas automáticamente contra otros reportes del sistema.

`purchase-toolkit` reemplaza ese proceso manual por un conjunto de herramientas independientes que:

- Verifican la integridad de los datos exportados del ERP antes de que un error se propague a etapas posteriores.
- Extraen, de forma agnóstica al caso de uso, todos los campos estructurados embebidos en cada orden (tipo de operación, tipo de cambio, condiciones de pago, presupuesto asociado), para que cualquier análisis posterior parta de la misma fuente de datos confiable.
- Unifican automáticamente los documentos de respaldo de cada orden (presupuesto, autorización, pedido) en un único archivo, respetando el orden que exige el circuito de aprobación.

## Principio de diseño

Cada herramienta (`audit`, `extract`, `merge`) se usa de forma aislada; ninguna depende internamente de otra. La orquestación de un flujo completo es decisión de quien las use, no del paquete.

## Módulos

| Módulo | Estado | Qué hace |
|---|---|---|
| [`merge`](src/purchase_toolkit/merge/README.md) | Completo | Unifica los PDF de respaldo de cada orden de compra en un único archivo. |
| [`extract`](src/purchase_toolkit/extract/README.md) | Completo | Extrae los campos estructurados embebidos en el texto de una orden de compra. |
| `audit` | En desarrollo | Verifica integridad interna y consistencia cruzada entre los datos fuente. |

## Instalación

Recomendada con `uv`:

```bash
uv add git+https://github.com/ochoaenzo/purchase-toolkit.git
```

O con `pip`:

```bash
pip install git+https://github.com/ochoaenzo/purchase-toolkit.git
```

## Uso

Cada módulo se documenta de forma independiente y autosuficiente en su propio README, con ejemplos completos de uso, comportamiento y extensión. Ver la tabla de módulos arriba.

## Stack técnico

- **Python:** 3.12+
- **Gestión de dependencias:** [`uv`](https://docs.astral.sh/uv/)
- **Linting:** [`ruff`](https://docs.astral.sh/ruff/)
- **Tests:** [`pytest`](https://docs.pytest.org/)
- **Manejo de PDF:** [`pypdf`](https://pypdf.readthedocs.io/)

## Licencia

[MIT](LICENSE)
