"""Dashboard de Ventas 2026 en Streamlit, alimentado por la API de ventas (api/main.py).

Ejecutar en local:
    uvicorn api.main:app --port 8000        # terminal 1: la API
    streamlit run streamlit_app.py          # terminal 2: el dashboard

La URL de la API se toma de la variable de entorno API_URL o de st.secrets["API_URL"]
(por defecto http://127.0.0.1:8000). Si la API no responde, el dashboard usa la misma
lógica de la API en modo local para que siempre se pueda visualizar (p. ej. en Streamlit Cloud).
"""
import os

import altair as alt
import pandas as pd
import requests
import streamlit as st

from api import datos as api_local

AZUL, NARANJA = "#2a78d6", "#eb6834"
CATEGORICOS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]

st.set_page_config(page_title="Dashboard de Ventas 2026", page_icon="📊", layout="wide")


# ---------------------------------------------------------------- Cliente de la API
def _api_url() -> str:
    try:
        url = st.secrets.get("API_URL")
    except Exception:  # no hay secrets.toml
        url = None
    return (url or os.getenv("API_URL") or "http://127.0.0.1:8000").rstrip("/")


API_URL = _api_url()

LOCAL = {
    "/resumen": api_local.resumen,
    "/ventas/mensuales": api_local.ventas_mensuales,
    "/ventas/regiones": lambda: api_local.ventas_por_region(),
    "/ventas/categorias": lambda: api_local.ventas_por_categoria(),
}


@st.cache_data(ttl=60, show_spinner=False)
def consultar(endpoint: str, **params):
    """GET a la API; si no responde, ejecuta el mismo endpoint en modo local."""
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=3)
        r.raise_for_status()
        return r.json(), "api"
    except requests.RequestException:
        return LOCAL[endpoint](**params), "local"


def ancho_completo(fn, obj, **kw):
    """Ocupa todo el ancho; compatible con versiones nuevas (width) y anteriores de Streamlit."""
    try:
        return fn(obj, width="stretch", **kw)
    except TypeError:
        return fn(obj, use_container_width=True, **kw)


def mxn(v: float) -> str:
    return f"${v:,.0f}k"


# ---------------------------------------------------------------- Barra lateral
st.sidebar.header("Filtros")
desde, hasta = st.sidebar.select_slider(
    "Periodo", options=list(range(1, 13)), value=(1, 12),
    format_func=lambda m: api_local.MESES[m - 1],
)
st.sidebar.caption("El periodo afecta los KPIs y las gráficas mensuales. "
                   "Regiones y categorías son totales anuales.")

# ---------------------------------------------------------------- Datos
res, fuente1 = consultar("/resumen", desde=desde, hasta=hasta)
mensual, fuente2 = consultar("/ventas/mensuales", desde=desde, hasta=hasta)
regiones, fuente3 = consultar("/ventas/regiones")
categorias, fuente4 = consultar("/ventas/categorias")
df_mes = pd.DataFrame(mensual)
df_reg = pd.DataFrame(regiones)
df_cat = pd.DataFrame(categorias)
en_linea = all(f == "api" for f in (fuente1, fuente2, fuente3, fuente4))

# ---------------------------------------------------------------- Encabezado + KPIs
st.title("📊 Dashboard de Ventas 2026")
st.caption(f"Montos en miles de MXN · Periodo: {api_local.MESES[desde - 1]}–{api_local.MESES[hasta - 1]}")
if en_linea:
    st.sidebar.success(f"Conectado a la API: {API_URL}")
else:
    st.sidebar.info("API no disponible: usando los datos de la API en modo local.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Ventas totales", mxn(res["ventas_totales"]),
          f"{res['cumplimiento_pct']:+.1f}% vs meta")
k2.metric("Unidades vendidas", f"{res['unidades']:,}")
k3.metric("Ticket promedio", f"${res['ticket_promedio_mxn']:,.0f}")
k4.metric("Mejor mes", res["mejor_mes"], mxn(res["ventas_mejor_mes"]), delta_color="off")

orden_meses = df_mes["mes"].tolist()

# ---------------------------------------------------------------- Fila 1
c1, c2 = st.columns(2)
with c1:
    st.subheader("Ventas mensuales")
    st.caption("Evolución de las ventas en el periodo")
    linea = (
        alt.Chart(df_mes)
        .mark_line(color=AZUL, strokeWidth=2, point=alt.OverlayMarkDef(color=AZUL, size=40))
        .encode(
            x=alt.X("mes:N", sort=orden_meses, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("ventas:Q", title="Miles de MXN", scale=alt.Scale(zero=True)),
            tooltip=[alt.Tooltip("mes:N", title="Mes"), alt.Tooltip("ventas:Q", title="Ventas", format=",")],
        )
        .properties(height=300)
    )
    ancho_completo(st.altair_chart, linea)

with c2:
    st.subheader("Ventas por región")
    st.caption("Total anual por región, de mayor a menor")
    barras = (
        alt.Chart(df_reg)
        .mark_bar(color=AZUL, cornerRadiusEnd=4)
        .encode(
            y=alt.Y("region:N", sort="-x", title=None),
            x=alt.X("ventas:Q", title="Miles de MXN"),
            tooltip=[alt.Tooltip("region:N", title="Región"), alt.Tooltip("ventas:Q", title="Ventas", format=","),
                     alt.Tooltip("participacion_pct:Q", title="% del total")],
        )
    )
    etiquetas = barras.mark_text(align="left", dx=4, color="gray").encode(text=alt.Text("ventas:Q", format=","))
    ancho_completo(st.altair_chart, (barras + etiquetas).properties(height=300))

# ---------------------------------------------------------------- Fila 2
c3, c4 = st.columns(2)
with c3:
    st.subheader("Participación por categoría")
    st.caption("Porcentaje de las ventas anuales por categoría")
    pastel = (
        alt.Chart(df_cat)
        .mark_arc(innerRadius=60, stroke="white", strokeWidth=2)
        .encode(
            theta=alt.Theta("ventas:Q"),
            color=alt.Color("categoria:N", title="Categoría",
                            sort=df_cat["categoria"].tolist(),
                            scale=alt.Scale(domain=df_cat["categoria"].tolist(), range=CATEGORICOS)),
            tooltip=[alt.Tooltip("categoria:N", title="Categoría"), alt.Tooltip("ventas:Q", title="Ventas", format=","),
                     alt.Tooltip("participacion_pct:Q", title="Participación %")],
        )
        .properties(height=300)
    )
    ancho_completo(st.altair_chart, pastel)

with c4:
    st.subheader("Cumplimiento de meta mensual")
    st.caption("Diferencia entre ventas reales y meta de cada mes (%)")
    df_meta = df_mes.assign(estado=lambda d: d["cumplimiento_pct"].map(
        lambda v: "Arriba de la meta" if v >= 0 else "Debajo de la meta"))
    meta = (
        alt.Chart(df_meta)
        .mark_bar(cornerRadius=4)
        .encode(
            x=alt.X("mes:N", sort=orden_meses, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("cumplimiento_pct:Q", title="% vs meta"),
            color=alt.Color("estado:N", title=None,
                            scale=alt.Scale(domain=["Arriba de la meta", "Debajo de la meta"], range=[AZUL, NARANJA]),
                            legend=alt.Legend(orient="top")),
            tooltip=[alt.Tooltip("mes:N", title="Mes"), alt.Tooltip("ventas:Q", title="Real", format=","),
                     alt.Tooltip("meta:Q", title="Meta", format=","),
                     alt.Tooltip("cumplimiento_pct:Q", title="Diferencia %", format="+.1f")],
        )
    )
    cero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="gray").encode(y="y:Q")
    ancho_completo(st.altair_chart, (meta + cero).properties(height=300))
    if res["meses_bajo_meta"]:
        st.caption(f"⚠️ {res['meses_bajo_meta']} mes(es) por debajo de la meta en el periodo.")

# ---------------------------------------------------------------- Tabla
with st.expander("Ver datos mensuales"):
    ancho_completo(
        st.dataframe, df_mes.drop(columns="mes_num").rename(columns={
            "mes": "Mes", "ventas": "Ventas", "meta": "Meta", "unidades": "Unidades",
            "cumplimiento_pct": "Cumplimiento %"}),
        hide_index=True,
    )

st.caption(f"Fuente: API de Ventas 2026 · {API_URL if en_linea else 'modo local (api/datos.py)'}")
