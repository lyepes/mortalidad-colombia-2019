"""
Pagina "Grafico de barras": las 5 ciudades mas violentas de Colombia (2019),
medidas por homicidios con arma de fuego (CIE-10 X95*).
"""

import plotly.express as px
import streamlit as st

from datos import (
    COD_ARMA_FUEGO,
    DESC_ARMA_FUEGO,
    REJILLA,
    SEQ,
    SUPERFICIE,
    TINTA,
    barra_lateral,
    ciudades_violentas,
    estilizar,
    miles,
    total_homicidios_arma_fuego,
    verificar_archivos,
)

TOP_N = 5

verificar_archivos()
barra_lateral()

st.title("Las 5 ciudades más violentas de Colombia")
st.caption(
    f"Homicidios con arma de fuego registrados en 2019, código CIE-10 "
    f"{COD_ARMA_FUEGO}*: {DESC_ARMA_FUEGO.lower()}. Incluye los diez subcódigos "
    f"{COD_ARMA_FUEGO}0 a {COD_ARMA_FUEGO}9, que distinguen el lugar del hecho "
    "(vivienda, calle, comercio y otros)."
)

datos = ciudades_violentas(TOP_N)
total_nacional = total_homicidios_arma_fuego()

c1, c2, c3 = st.columns(3)
c1.metric("Homicidios en el país", miles(total_nacional))
c2.metric(f"Concentrados en estas {TOP_N} ciudades", miles(datos["homicidios"].sum()))
c3.metric("Participacion de las 5", f"{datos['porcentaje'].sum():.1f} %")

# Barras horizontales: los nombres de ciudad son largos y se leen mejor asi.
grafica = datos.sort_values("homicidios")
fig = px.bar(
    grafica,
    x="homicidios",
    y="municipio",
    orientation="h",
    color="homicidios",
    color_continuous_scale=SEQ,
    text="homicidios",
    custom_data=["departamento", "porcentaje"],
)
fig.update_traces(
    texttemplate="%{text:,}",
    textposition="outside",
    textfont=dict(color=TINTA, size=13),
    cliponaxis=False,
    marker_line_color=SUPERFICIE,
    marker_line_width=2,
    hovertemplate="<b>%{y}</b> (%{customdata[0]})<br>Homicidios: %{x:,}"
    "<br>Participacion nacional: %{customdata[1]}%<extra></extra>",
)
fig.update_xaxes(title="Homicidios con arma de fuego", showgrid=True, gridcolor=REJILLA)
fig.update_yaxes(title="", showgrid=False)
fig = estilizar(fig, altura=380)
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, width="stretch")

with st.expander("Ver los datos de la gráfica"):
    st.dataframe(
        datos[["municipio", "departamento", "homicidios", "porcentaje"]].rename(
            columns={
                "municipio": "Ciudad",
                "departamento": "Departamento",
                "homicidios": "Homicidios",
                "porcentaje": "% del total nacional",
            }
        ),
        width="stretch",
        hide_index=True,
    )
