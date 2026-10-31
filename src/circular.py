"""
Pagina "Grafico circular": las 10 ciudades con menor mortalidad registrada
en Colombia (2019).
"""

import plotly.express as px
import streamlit as st

from datos import (
    SEQ,
    SUPERFICIE,
    TINTA,
    TINTA_SUAVE,
    barra_lateral,
    ciudades_menor_mortalidad,
    miles,
    muertes_por_municipio,
    municipios_sin_registros,
    verificar_archivos,
)

TOP_N = 10

verificar_archivos()
barra_lateral()

st.title("Las 10 ciudades con menor mortalidad")
st.caption(
    "Municipios con menos defunciones no fetales registradas en 2019. Se excluyen "
    "las areas no municipalizadas y la isla, que no son ciudades, y los municipios "
    "sin ningun registro, que se listan mas abajo."
)

datos = ciudades_menor_mortalidad(TOP_N)
sin_registros = municipios_sin_registros()
municipal = muertes_por_municipio()

c1, c2, c3 = st.columns(3)
c1.metric("Muertes en estas 10 ciudades", miles(datos["muertes"].sum()))
c2.metric("Ciudades sin ningun registro", int((sin_registros["tipo"] == "Municipio").sum()))
c3.metric("Mediana nacional por municipio", miles(municipal["muertes"].median()))

izq, der = st.columns([3, 2])
with izq:
    # El color codifica magnitud (las porciones vienen ordenadas), no identidad:
    # con diez categorias la paleta categorica se agotaria. La identidad la
    # llevan la etiqueta directa de cada porcion y la tabla de al lado.
    pasos = SEQ[2 : 2 + len(datos)]
    fig = px.pie(
        datos,
        names="municipio",
        values="muertes",
        color_discrete_sequence=pasos,
        custom_data=["departamento", "porcentaje"],
        hole=0.45,
    )
    fig.update_traces(
        sort=False,
        direction="clockwise",
        textinfo="label",
        textposition="outside",
        textfont=dict(color=TINTA, size=12),
        marker=dict(line=dict(color=SUPERFICIE, width=2)),
        hovertemplate="<b>%{label}</b> (%{customdata[0]})<br>Muertes: %{value}"
        "<br>Participacion en el grupo: %{customdata[1]}%<extra></extra>",
    )
    fig.update_layout(
        height=480,
        margin=dict(l=60, r=60, t=20, b=20),
        paper_bgcolor=SUPERFICIE,
        font=dict(color=TINTA, size=13),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")

with der:
    st.dataframe(
        datos[["municipio", "departamento", "muertes", "porcentaje"]].rename(
            columns={
                "municipio": "Ciudad",
                "departamento": "Departamento",
                "muertes": "Muertes",
                "porcentaje": "% del grupo",
            }
        ),
        width="stretch",
        hide_index=True,
    )
    st.caption(
        "Nueve de las diez ciudades registran una sola muerte, asi que sus porciones "
        "son practicamente identicas. La tabla es la lectura fiable del detalle."
    )

st.warning(
    "No se incluyeron los municipios con mortalidad cero"
)
