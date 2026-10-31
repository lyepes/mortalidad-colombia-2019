"""
Pagina "Mapa": distribucion total de muertes por departamento en Colombia (2019).

Se dibuja con las coordenadas de DIVIPOLA Hoja3, sin archivos de geometria externos.
"""

import plotly.express as px
import streamlit as st

from datos import (
    SEQ,
    SUPERFICIE,
    TINTA,
    barra_lateral,
    tabla_departamentos,
    verificar_archivos,
)

verificar_archivos()
barra_lateral()

st.title("Mapa de muertes por departamento")
st.caption(
    "Visualización de la distribución total de muertes por departamento en Colombia para el año 2019"
)

tabla = tabla_departamentos()

fig = px.scatter_geo(
    tabla,
    lon="lon",
    lat="lat",
    size="muertes",
    color="muertes",
    color_continuous_scale=SEQ,
    hover_name="etiqueta",
    custom_data=["muertes", "porcentaje", "municipios"],
    size_max=60,
    labels={"muertes": "Muertes"},
)
fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Muertes: %{customdata[0]:,}"
    "<br>Participacion: %{customdata[1]}%"
    "<br>Entidades DIVIPOLA: %{customdata[2]}<extra></extra>",
    marker_line_color=SUPERFICIE,
    marker_line_width=2,
)
# Mapa base propio de Plotly; showsubunits dibuja los limites departamentales.
fig.update_geos(
    resolution=50,
    showcountries=True,
    countrycolor="#9aa0a6",
    showsubunits=True,
    subunitcolor="#d0d4d9",
    showland=True,
    landcolor="#f5f5f3",
    showocean=True,
    oceancolor="#e8f1f8",
    lonaxis_range=[-80.5, -66.5],
    lataxis_range=[-4.6, 13.8],
)
fig.update_layout(
    height=620,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor=SUPERFICIE,
    font=dict(color=TINTA),
    coloraxis_colorbar=dict(title="Muertes"),
)
st.plotly_chart(fig, width="stretch")

# Respaldo tabular del mapa: las burbujas pequenas no se comparan a simple vista.
with st.expander("Ver los datos del mapa"):
    st.dataframe(
        tabla[["etiqueta", "muertes", "porcentaje"]].rename(
            columns={               
                "etiqueta": "Departamento",
                "muertes": "Muertes",
                "porcentaje": "% del total"               
            }
        ),
        width="stretch",
        hide_index=True,
    )
