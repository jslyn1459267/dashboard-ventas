"""Datos y lógica de negocio de la API de ventas 2026 (montos en miles de MXN)."""

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
VENTAS = [412, 398, 455, 470, 502, 488, 515, 540, 497, 563, 610, 688]
METAS = [400, 410, 440, 460, 480, 500, 520, 530, 540, 560, 600, 650]
UNIDADES = [1650, 1590, 1820, 1880, 2010, 1950, 2060, 2160, 1990, 2250, 2440, 2750]
REGIONES = {"Centro": 2140, "Norte": 1720, "Occidente": 1310, "Sureste": 820, "Bajío": 648}
CATEGORIAS = {"Electrónica": 2210, "Hogar": 1580, "Ropa": 1240, "Deportes": 960, "Juguetes": 648}


def _rango(desde: int = 1, hasta: int = 12) -> range:
    if not (1 <= desde <= hasta <= 12):
        raise ValueError("Rango de meses inválido: usa 1 <= desde <= hasta <= 12")
    return range(desde - 1, hasta)


def ventas_mensuales(desde: int = 1, hasta: int = 12) -> list[dict]:
    """Ventas, meta, unidades y cumplimiento (%) por mes."""
    return [
        {
            "mes_num": i + 1,
            "mes": MESES[i],
            "ventas": VENTAS[i],
            "meta": METAS[i],
            "unidades": UNIDADES[i],
            "cumplimiento_pct": round((VENTAS[i] - METAS[i]) / METAS[i] * 100, 2),
        }
        for i in _rango(desde, hasta)
    ]


def resumen(desde: int = 1, hasta: int = 12) -> dict:
    """KPIs del periodo seleccionado."""
    filas = ventas_mensuales(desde, hasta)
    total = sum(f["ventas"] for f in filas)
    meta = sum(f["meta"] for f in filas)
    unidades = sum(f["unidades"] for f in filas)
    mejor = max(filas, key=lambda f: f["ventas"])
    return {
        "desde": desde,
        "hasta": hasta,
        "ventas_totales": total,
        "meta_total": meta,
        "cumplimiento_pct": round((total - meta) / meta * 100, 2),
        "unidades": unidades,
        "ticket_promedio_mxn": round(total * 1000 / unidades, 2),
        "mejor_mes": mejor["mes"],
        "ventas_mejor_mes": mejor["ventas"],
        "meses_bajo_meta": sum(1 for f in filas if f["ventas"] < f["meta"]),
    }


def _ranking(datos: dict, clave: str) -> list[dict]:
    total = sum(datos.values())
    return [
        {clave: k, "ventas": v, "participacion_pct": round(v / total * 100, 2)}
        for k, v in sorted(datos.items(), key=lambda kv: kv[1], reverse=True)
    ]


def ventas_por_region() -> list[dict]:
    return _ranking(REGIONES, "region")


def ventas_por_categoria() -> list[dict]:
    return _ranking(CATEGORIAS, "categoria")
