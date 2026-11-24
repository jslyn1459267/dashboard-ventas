# Dashboard de Ventas 2026

Dashboard interactivo en HTML + JavaScript puro (sin librerías externas), basado en el dashboard compartido del repositorio base.

## Archivos
| Archivo | Descripción |
|---|---|
| `index.html` | Dashboard: KPIs, gráficas SVG y tooltips |
| `datos.js` | Datos de ventas, metas, unidades, regiones y categorías |

## Cómo verlo
Abre `index.html` en el navegador, o activa **GitHub Pages** (Settings → Pages → rama `main`).

## Cambios respecto al repositorio base
**Gráfica eliminada: "Unidades vendidas por mes".**
Mostraba la misma tendencia que *Ventas mensuales*, porque el ticket promedio casi no cambia (~$250 por unidad) y la forma de ambas curvas es prácticamente idéntica. El total de unidades sigue visible en el KPI "Unidades vendidas".

**Gráfica agregada: "Cumplimiento de meta mensual".**
Barras divergentes que muestran, mes a mes, qué porcentaje por encima (azul) o por debajo (naranja) de la meta quedaron las ventas. Usa el campo `metas` de `datos.js`, que el dashboard base no mostraba en ningún lado. Esto permite detectar rápido los meses problemáticos (p. ej. septiembre, −8 %), algo que la línea de ventas por sí sola no deja ver.
