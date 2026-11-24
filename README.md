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

---

## Versión Streamlit + API

El dashboard también se transformó a **Streamlit**, alimentado por una **API REST (FastAPI)** con los mismos datos.

```
api/
  datos.py        # datos y lógica (KPIs, ventas mensuales, regiones, categorías)
  main.py         # API FastAPI
streamlit_app.py  # dashboard en Streamlit que consume la API
requirements.txt
```

### Endpoints de la API
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/resumen?desde=1&hasta=12` | KPIs del periodo (ventas, meta, cumplimiento, unidades, ticket, mejor mes) |
| GET | `/ventas/mensuales?desde=1&hasta=12` | Ventas, meta, unidades y % de cumplimiento por mes |
| GET | `/ventas/regiones` | Ventas anuales por región con % de participación |
| GET | `/ventas/categorias` | Ventas anuales por categoría con % de participación |

### Ejecutar en local
```bash
pip install -r requirements.txt
uvicorn api.main:app --port 8000      # terminal 1 → docs en http://127.0.0.1:8000/docs
streamlit run streamlit_app.py        # terminal 2 → http://localhost:8501
```

El dashboard lee la URL de la API de la variable `API_URL` (o `st.secrets["API_URL"]`). Si la API no responde, usa la misma lógica de `api/datos.py` en modo local, así que también funciona publicado en **Streamlit Community Cloud** (archivo principal: `streamlit_app.py`).

### Qué incluye el dashboard
- Filtro de periodo (rango de meses) en la barra lateral
- 4 KPIs: ventas totales (con % vs meta), unidades, ticket promedio y mejor mes
- Ventas mensuales (línea), ventas por región (barras), participación por categoría (dona) y cumplimiento de meta mensual (barras azul/naranja)
- Tabla con los datos mensuales
