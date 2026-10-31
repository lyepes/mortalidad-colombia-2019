"""
Carga de datos, paleta y utilidades compartidas por las paginas del tablero.

Fuentes:
  - data/Anexo1.NoFetal2019_CE_15-03-23.xlsx  -> registros individuales de defuncion
  - data/Divipola_CE_.xlsx (Hoja3)            -> catalogo oficial DIVIPOLA con coordenadas

Las funciones de carga estan cacheadas con @st.cache_data, asi que el Anexo1 se
lee del disco una sola vez por sesion aunque se visiten varias paginas.
"""

import re
from pathlib import Path

import pandas as pd
import streamlit as st

# El codigo vive en src/ y los datos en data/, ambos dentro de la raiz del
# proyecto, de modo que hay que subir un nivel desde este archivo.
DATA = Path(__file__).resolve().parent.parent / "data"
ANEXO1 = DATA / "Anexo1.NoFetal2019_CE_15-03-23.xlsx"
DIVIPOLA = DATA / "Divipola_CE_.xlsx"
ANEXO2 = DATA / "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"
RANGOS_EDAD = DATA / "RangoEdadAproximado.xlsx"

# Hoja3 trae dos filas de encabezado combinadas ("Departamento | Codigo/Nombre", etc.),
# asi que se omiten y se nombran las columnas a mano.
HOJA_DIVIPOLA = "Hoja3"
COLS_HOJA3 = ["cod_dep", "departamento", "cod_mun", "municipio", "tipo", "lon", "lat"]

# Columnas del Anexo1 que alimentan las vistas.
COLS_ANEXO1 = [
    "COD_DANE",
    "COD_DEPARTAMENTO",
    "COD_MUERTE",
    "MES",
    "HORA",
    "SEXO",
    "GRUPO_EDAD1",
    "MANERA_MUERTE",
    "AREA_DEFUNCION",
    "SITIO_DEFUNCION",
]

# --- Paleta -----------------------------------------------------------------
# Categorica en orden fijo (nunca ciclado) y secuencial de un solo tono.
SERIES = [
    "#2a78d6",  # azul
    "#eb6834",  # naranja
    "#1baf7a",  # aqua
    "#eda100",  # amarillo
    "#e87ba4",  # magenta
    "#008300",  # verde
    "#4a3aa7",  # violeta
    "#e34948",  # rojo
]
SEQ = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]
SUPERFICIE = "#ffffff"  # separador de 2px entre rellenos
TINTA = "#0b0b0b"
TINTA_SUAVE = "#52514e"
REJILLA = "#e8e6e1"

# --- Diccionarios de codigos DANE ------------------------------------------
MESES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}
SEXO = {1: "Hombre", 2: "Mujer", 3: "Indeterminado"}
AREA = {
    1: "Cabecera municipal",
    2: "Centro poblado",
    3: "Rural disperso",
    9: "Sin informacion",
}
SITIO = {
    1: "Hospital / clinica",
    2: "Centro o puesto de salud",
    3: "Domicilio",
    4: "Lugar de trabajo",
    5: "Via publica",
    6: "Otro",
    9: "Sin informacion",
}

# Homicidio por arma de fuego en la CIE-10. El grupo X95 ("agresion con disparo
# de otras armas de fuego, y las no especificadas") se subdivide de X950 a X959
# solo por el lugar del hecho (vivienda, calle, comercio...), asi que el prefijo
# agrupa el total de casos.
# El Anexo2 es el catalogo CIE-10. Su hoja unica trae siete filas de portada
# antes del encabezado real, y una fila por codigo de cuatro caracteres.
HOJA_CIE10 = "Final"
COLS_CIE10 = ["capitulo", "nombre_capitulo", "cod3", "desc3", "cod4", "desc4"]

COD_ARMA_FUEGO = "X95"
DESC_ARMA_FUEGO = "Agresión con disparo de otras armas de fuego, y las no especificadas"

# Dimensiones categoricas reutilizables. Todas tienen como maximo 7 categorias,
# asi que la paleta de 8 slots nunca se cicla.
DIMENSIONES = {
    "Manera de muerte": "manera",
    "Sexo": "sexo",
    "Area de defuncion": "area",
    "Sitio de defuncion": "sitio",
}


# ------------------------------------------------------------------ carga

@st.cache_data(show_spinner="Cargando Anexo1 (registros de defuncion)...")
def cargar_muertes() -> pd.DataFrame:
    """Un registro por defuncion, con las dimensiones ya etiquetadas."""
    df = pd.read_excel(ANEXO1, usecols=COLS_ANEXO1)
    df = df.dropna(subset=["COD_DEPARTAMENTO"])
    # En el Anexo1 el codigo de departamento es entero (5 = Antioquia); DIVIPOLA
    # lo usa como texto de dos digitos ("05"), que es la llave comun.
    df["cod_dep"] = df["COD_DEPARTAMENTO"].astype(int).astype(str).str.zfill(2)
    # COD_DANE identifica el municipio con cinco digitos (76001 = Santiago de Cali).
    df["cod_mun"] = df["COD_DANE"].astype("Int64").astype(str).str.zfill(5)
    df["cod_muerte"] = df["COD_MUERTE"].astype(str).str.strip().str.upper()
    df["mes"] = df["MES"].astype(int)
    df["mes_nombre"] = df["mes"].map(MESES)
    df["hora"] = df["HORA"].astype(int)
    df["grupo_edad"] = df["GRUPO_EDAD1"].astype(int)
    df["sexo"] = df["SEXO"].map(SEXO).fillna("Sin informacion")
    df["area"] = df["AREA_DEFUNCION"].map(AREA).fillna("Sin informacion")
    df["sitio"] = df["SITIO_DEFUNCION"].map(SITIO).fillna("Sin informacion")
    df["manera"] = df["MANERA_MUERTE"].astype(str).str.strip()
    return df[
        ["cod_dep", "cod_mun", "cod_muerte", "mes", "mes_nombre", "hora",
         "grupo_edad", "sexo", "area", "sitio", "manera"]
    ]


@st.cache_data(show_spinner="Cargando Divipola (Hoja3)...")
def cargar_divipola() -> pd.DataFrame:
    """Catalogo DIVIPOLA completo: 1.122 entidades (municipios, islas y areas no
    municipalizadas) con codigo de departamento y coordenadas."""
    df = pd.read_excel(
        DIVIPOLA,
        sheet_name=HOJA_DIVIPOLA,
        skiprows=2,
        header=None,
        names=COLS_HOJA3,
        dtype={"cod_dep": str, "cod_mun": str},
    )
    df["cod_dep"] = df["cod_dep"].str.strip().str.zfill(2)
    df["departamento"] = df["departamento"].str.strip()
    # Las coordenadas vienen como texto con coma decimal (-75,581775).
    for col in ("lon", "lat"):
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ".", regex=False), errors="coerce"
        )
    return df


def _titulo(serie: pd.Series) -> pd.Series:
    """Capitalizacion normal dejando las preposiciones en minuscula."""
    menores = {"De", "Del", "La", "Las", "Los", "Y"}
    return serie.str.title().apply(
        lambda s: " ".join(
            p.lower() if i and p in menores else p for i, p in enumerate(s.split(" "))
        )
    )


@st.cache_data
def tabla_departamentos() -> pd.DataFrame:
    """Muertes por departamento, con nombre oficial, centroide y numero de
    entidades territoriales tomados de DIVIPOLA Hoja3."""
    muertes = cargar_muertes()
    divipola = cargar_divipola()

    deptos = (
        divipola.groupby("cod_dep")
        .agg(
            departamento=("departamento", "first"),
            municipios=("cod_mun", "nunique"),
            lon=("lon", "mean"),
            lat=("lat", "mean"),
        )
        .reset_index()
    )
    conteo = (
        muertes["cod_dep"].value_counts().rename_axis("cod_dep").reset_index(name="muertes")
    )

    tabla = deptos.merge(conteo, on="cod_dep", how="left")
    tabla["muertes"] = tabla["muertes"].fillna(0).astype(int)
    tabla["porcentaje"] = (tabla["muertes"] / tabla["muertes"].sum() * 100).round(2)
    tabla["etiqueta"] = _titulo(tabla["departamento"])
    return tabla.sort_values("muertes", ascending=False).reset_index(drop=True)


@st.cache_data
def agregar(*columnas: str) -> pd.DataFrame:
    """Conteo de muertes agrupado por las columnas indicadas."""
    muertes = cargar_muertes()
    return (
        muertes.groupby(list(columnas), dropna=False).size().reset_index(name="muertes")
    )


@st.cache_data
def ciudades_violentas(top_n: int = 5) -> pd.DataFrame:
    """Municipios con mas homicidios por arma de fuego (CIE-10 X95*).

    El conteo es absoluto, no una tasa por habitante: el Anexo1 no trae poblacion,
    de modo que las ciudades grandes aparecen arriba en parte por su tamano.
    """
    muertes = cargar_muertes()
    divipola = cargar_divipola()

    casos = muertes[muertes["cod_muerte"].str.startswith(COD_ARMA_FUEGO)]
    tabla = (
        casos["cod_mun"].value_counts().rename_axis("cod_mun").reset_index(name="homicidios")
    )
    tabla = tabla.merge(
        divipola[["cod_mun", "municipio", "departamento"]], on="cod_mun", how="left"
    )
    tabla["municipio"] = _titulo(tabla["municipio"])
    tabla["departamento"] = _titulo(tabla["departamento"])
    tabla["porcentaje"] = (tabla["homicidios"] / tabla["homicidios"].sum() * 100).round(2)
    return tabla.head(top_n).reset_index(drop=True)


@st.cache_data
def total_homicidios_arma_fuego() -> int:
    """Total nacional de homicidios con codigo X95*, para contextualizar el ranking."""
    muertes = cargar_muertes()
    return int(muertes["cod_muerte"].str.startswith(COD_ARMA_FUEGO).sum())


@st.cache_data
def muertes_por_municipio() -> pd.DataFrame:
    """Muertes por municipio, partiendo del catalogo DIVIPOLA Hoja3.

    La base son las 1.122 entidades de Hoja3, de modo que los municipios sin
    ningun registro en el Anexo1 aparecen con cero y no desaparecen del conteo.
    Un registro del Anexo1 (municipio 94663, Mapiripana) no existe en Hoja3 y
    por eso queda fuera de esta agregacion municipal; si esta contado en la
    agregacion por departamento, que usa COD_DEPARTAMENTO.
    """
    muertes = cargar_muertes()
    divipola = cargar_divipola()

    conteo = (
        muertes["cod_mun"].value_counts().rename_axis("cod_mun").reset_index(name="muertes")
    )
    tabla = divipola[["cod_mun", "municipio", "departamento", "tipo"]].merge(
        conteo, on="cod_mun", how="left"
    )
    tabla["muertes"] = tabla["muertes"].fillna(0).astype(int)
    tabla["municipio"] = _titulo(tabla["municipio"])
    tabla["departamento"] = _titulo(tabla["departamento"])
    return tabla


@st.cache_data
def ciudades_menor_mortalidad(top_n: int = 10) -> pd.DataFrame:
    """Las ciudades con menos muertes registradas en 2019.

    Criterios, necesarios porque el extremo bajo esta lleno de empates:
      - Solo entidades de tipo "Municipio": las areas no municipalizadas y la
        isla no son ciudades.
      - Solo municipios con al menos una muerte registrada. Los que tienen cero
        se listan aparte con municipios_sin_registros(), porque un cero puede
        significar tanto ausencia de defunciones como falta de reporte.
      - Ante empates, orden alfabetico, para que el resultado sea estable.

    El conteo es absoluto, no una tasa por habitante: el Anexo1 no trae
    poblacion, asi que estos municipios figuran abajo sobre todo por su tamano.
    """
    tabla = muertes_por_municipio()
    ciudades = tabla[(tabla["tipo"] == "Municipio") & (tabla["muertes"] > 0)]
    ciudades = ciudades.sort_values(["muertes", "municipio"]).head(top_n)
    total = ciudades["muertes"].sum()
    ciudades = ciudades.copy()
    ciudades["porcentaje"] = (ciudades["muertes"] / total * 100).round(2)
    return ciudades.reset_index(drop=True)


@st.cache_data
def municipios_sin_registros() -> pd.DataFrame:
    """Entidades de DIVIPOLA sin ninguna defuncion registrada en el Anexo1."""
    tabla = muertes_por_municipio()
    return (
        tabla[tabla["muertes"] == 0]
        .sort_values(["departamento", "municipio"])
        .reset_index(drop=True)
    )


@st.cache_data(show_spinner="Cargando Anexo2 (catalogo CIE-10)...")
def cargar_cie10() -> pd.DataFrame:
    """Catalogo CIE-10 al nivel de categoria (codigo de tres caracteres).

    El Anexo1 registra la causa de muerte unas veces con cuatro caracteres
    (I219) y otras con tres (C61): 22.735 de los 244.355 registros usan la forma
    corta. Por eso el cruce se hace al nivel de tres caracteres, que es la
    categoria de la CIE-10 y cubre el 100% de los registros.
    """
    df = pd.read_excel(
        ANEXO2,
        sheet_name=HOJA_CIE10,
        skiprows=7,
        header=None,
        names=COLS_CIE10,
    )
    for col in COLS_CIE10:
        df[col] = df[col].astype(str).str.strip()
    df["cod3"] = df["cod3"].str.upper()
    # El catalogo escribe las descripciones en Title Case ("Infarto Agudo Del
    # Miocardio"); se pasan a capitalizacion de oracion para que se lean mejor.
    df["desc3"] = df["desc3"].str.capitalize()
    return df[["cod3", "desc3", "capitulo", "nombre_capitulo"]].drop_duplicates("cod3")


@st.cache_data
def principales_causas(top_n: int = 10) -> pd.DataFrame:
    """Causas de muerte mas frecuentes, al nivel de categoria CIE-10."""
    muertes = cargar_muertes()
    catalogo = cargar_cie10()

    conteo = (
        muertes["cod_muerte"]
        .str[:3]
        .value_counts()
        .rename_axis("codigo")
        .reset_index(name="casos")
    )
    conteo["porcentaje"] = (conteo["casos"] / conteo["casos"].sum() * 100).round(2)
    tabla = conteo.merge(catalogo, left_on="codigo", right_on="cod3", how="left")
    tabla["causa"] = tabla["desc3"].fillna("Sin descripcion en el Anexo2")
    tabla["capitulo_cie10"] = tabla["nombre_capitulo"].fillna("Sin clasificar")
    return (
        tabla.sort_values("casos", ascending=False)
        .head(top_n)
        .reset_index(drop=True)[["codigo", "causa", "casos", "porcentaje", "capitulo_cie10"]]
    )


@st.cache_data(show_spinner="Cargando rangos de edad...")
def cargar_rangos_edad() -> pd.DataFrame:
    """Tabla de referencia que agrupa los codigos de GRUPO_EDAD1 en etapas del
    ciclo de vida.

    El archivo trae una fila de encabezado y luego una fila por etapa, con los
    codigos escritos como rango ("0-4", "25-28") o como valor unico ("11").
    """
    df = pd.read_excel(
        RANGOS_EDAD,
        sheet_name=0,
        skiprows=1,
        header=None,
        names=["categoria", "codigos", "rango_edad"],
    )
    for col in ("categoria", "codigos", "rango_edad"):
        df[col] = df[col].astype(str).str.strip()

    # El separador del archivo es un guion largo (0-4), no un guion simple.
    limites = df["codigos"].apply(lambda t: re.findall(r"\d+", t))
    df["cod_min"] = limites.str[0].astype(int)
    df["cod_max"] = limites.str[-1].astype(int)
    df["etiqueta"] = df["categoria"] + "<br>" + df["rango_edad"]
    return df


@st.cache_data
def muertes_por_ciclo_vida() -> pd.DataFrame:
    """Muertes agrupadas en las etapas del ciclo de vida de la tabla de rangos.

    Los rangos de la tabla cubren los codigos 0 a 29 sin huecos ni solapes, que
    son exactamente los valores presentes en el Anexo1, de modo que ningun
    registro queda sin clasificar.
    """
    muertes = cargar_muertes()
    rangos = cargar_rangos_edad()

    # Un corte por cada limite superior: pd.cut asigna cada codigo a su etapa.
    cortes = [rangos["cod_min"].min() - 0.5] + [c + 0.5 for c in rangos["cod_max"]]
    etapa = pd.cut(
        muertes["grupo_edad"],
        bins=cortes,
        labels=rangos["categoria"].tolist(),
        ordered=False,
    )

    conteo = (
        etapa.value_counts()
        .reindex(rangos["categoria"].tolist())
        .rename_axis("categoria")
        .reset_index(name="muertes")
    )
    tabla = rangos.merge(conteo, on="categoria", how="left")
    tabla["muertes"] = tabla["muertes"].fillna(0).astype(int)
    tabla["porcentaje"] = (tabla["muertes"] / tabla["muertes"].sum() * 100).round(2)
    return tabla


@st.cache_data
def nombres_departamento() -> pd.DataFrame:
    """Llave cod_dep -> etiqueta legible, para unir con los agregados."""
    return tabla_departamentos()[["cod_dep", "etiqueta"]]


# ------------------------------------------------------------------ estilo

def estilizar(fig, altura: int = 560, leyenda: bool = False):
    """Rejilla y ejes recesivos, tipografia en tinta, leyenda solo si hace falta."""
    fig.update_layout(
        height=altura,
        margin=dict(l=0, r=10, t=10, b=0),
        plot_bgcolor=SUPERFICIE,
        paper_bgcolor=SUPERFICIE,
        font=dict(color=TINTA, size=13),
        showlegend=leyenda,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            title_text="",
            font=dict(color=TINTA_SUAVE),
        ),
        hoverlabel=dict(bgcolor=SUPERFICIE, font_size=13),
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=REJILLA,
        tickfont=dict(color=TINTA_SUAVE),
        title_font=dict(color=TINTA_SUAVE),
    )
    fig.update_yaxes(
        gridcolor=REJILLA,
        zeroline=False,
        linecolor=REJILLA,
        tickfont=dict(color=TINTA_SUAVE),
        title_font=dict(color=TINTA_SUAVE),
    )
    return fig


def miles(n) -> str:
    """Formato de miles con punto, como se usa en Colombia."""
    return f"{int(n):,}".replace(",", ".")


def verificar_archivos() -> None:
    """Detiene la app con un mensaje claro si falta alguna fuente de datos."""
    for ruta in (ANEXO1, DIVIPOLA, ANEXO2, RANGOS_EDAD):
        if not ruta.exists():
            st.error(
                f"No se encuentra el archivo requerido: `{ruta.name}` "
                "en la carpeta `data/`."
            )
            st.stop()


def barra_lateral() -> None:
    """Totales fijos que acompanan a todas las paginas."""
    tabla = tabla_departamentos()
    with st.sidebar:
        st.metric("Total de muertes", miles(tabla["muertes"].sum()))
        st.metric("Departamentos", len(tabla))        
        st.caption("Periodo: año 2019 completo.")
