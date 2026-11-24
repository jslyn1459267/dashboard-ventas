"""API REST de ventas 2026.

Ejecutar:  uvicorn api.main:app --reload
Docs:      http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException, Query

from api import datos

app = FastAPI(title="API de Ventas 2026", version="1.0.0",
              description="Datos de ventas mensuales, metas, regiones y categorías (miles de MXN).")


def _validar(desde: int, hasta: int) -> None:
    if desde > hasta:
        raise HTTPException(status_code=422, detail="'desde' no puede ser mayor que 'hasta'")


@app.get("/")
def raiz():
    return {"mensaje": "API de Ventas 2026", "endpoints": [
        "/resumen", "/ventas/mensuales", "/ventas/regiones", "/ventas/categorias"]}


@app.get("/resumen")
def get_resumen(desde: int = Query(1, ge=1, le=12), hasta: int = Query(12, ge=1, le=12)):
    _validar(desde, hasta)
    return datos.resumen(desde, hasta)


@app.get("/ventas/mensuales")
def get_mensuales(desde: int = Query(1, ge=1, le=12), hasta: int = Query(12, ge=1, le=12)):
    _validar(desde, hasta)
    return datos.ventas_mensuales(desde, hasta)


@app.get("/ventas/regiones")
def get_regiones():
    return datos.ventas_por_region()


@app.get("/ventas/categorias")
def get_categorias():
    return datos.ventas_por_categoria()
