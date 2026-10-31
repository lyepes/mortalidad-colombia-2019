"""
Pagina "Grafico de barras apiladas": total de muertes por sexo en cada
departamento (2019), para comparar la brecha entre hombres y mujeres.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from datos import (
    REJILLA,
    SERIES,
    SUPERFICIE,
    TINTA_SUAVE,
    agregar,
    barra_lateral,
    estilizar,
    miles,
    nombres_departamento,
    verificar_archivos,
)

# Orden fijo por frecuencia nacional, para que el color siga a la categoria y no
# a su posicion en la grafica. Los tres primeros slots de la paleta son los que
# se validaron como distinguibles en cualquier combinacion de pares.
ORDEN_SEXO = ["Hombre", "Mujer", "Indeterminado"]
COLORES = dict(zip(ORDEN_SEXO, SERIES))

verificar_archivos()
barra_lateral()

st.title("Muertes por sexo en cada departamento")
st.caption(
    "Comparación del total de defunciones entre hombres y mujeres en los "
    "33 departamentos durante 2019."
)

datos = agregar("cod_dep", "sexo").merge(nombres_departamento(), on="cod_dep")
totales = datos.groupby("cod_dep")["muertes"].transform("sum")
datos["pct"] = datos["muertes"] / totales * 100

# Resumen por departamento: total, proporcion de hombres y razon hombre/mujer.
resumen = (
    datos.pivot_table(index="etiqueta", columns="sexo", values="muertes", fill_value=0)
    .reindex(columns=ORDEN_SEXO, fill_value=0)
)
resumen["Total"] = resumen.sum(axis=1)
resumen["pct_hombre"] = (resumen["Hombre"] / resumen["Total"] * 100).round(1)
resumen["razon"] = (resumen["Hombre"] / resumen["Mujer"].replace(0, pd.NA)).round(2)

hombres = int(resumen["Hombre"].sum())
mujeres = int(resumen["Mujer"].sum())
indeterminado = int(resumen["Indeterminado"].sum())
total_pais = hombres + mujeres + indeterminado
mayor_brecha = resumen["pct_hombre"].idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Hombres", miles(hombres), f"{hombres / total_pais * 100:.1f} % del total")
c2.metric("Mujeres", miles(mujeres), f"{mujeres / total_pais * 100:.1f} % del total")
c3.metric("Razón nacional hombre/mujer", f"{hombres / mujeres:.2f}")
c4.metric(
    f"Mayor brecha: {mayor_brecha}",
    f"{resumen.loc[mayor_brecha, 'pct_hombre']:.1f} % hombres",
)

izq, der = st.columns([3, 1])
with izq:
    modo = st.radio(
        "Escala",
        ["Numero de muertes", "Participacion (100 %)"],
        horizontal=True,
    )
with der:
    orden = st.selectbox("Ordenar por", ["Total de muertes", "Proporción de hombres"])

if orden == "Total de muertes":
    orden_dep = resumen.sort_values("Total")["Total"].index.tolist()
else:
    orden_dep = resumen.sort_values("pct_hombre")["pct_hombre"].index.tolist()

if modo == "Participacion (100 %)":
    columna_valor, titulo_x = "pct", "Participacion (%)"
else:
    columna_valor, titulo_x = "muertes", "Muertes"

fig = px.bar(
    datos,
    x=columna_valor,
    y="etiqueta",
    color="sexo",
    orientation="h",
    color_discrete_map=COLORES,
    category_orders={"etiqueta": orden_dep, "sexo": ORDEN_SEXO},
    custom_data=["muertes", "pct"],
)
fig.update_traces(
    # Separador de 2px del color de la superficie entre segmentos.
    marker_line_color=SUPERFICIE,
    marker_line_width=2,
    hovertemplate="<b>%{y}</b><br>%{fullData.name}<br>Muertes: %{customdata[0]:,}"
    "<br>Participacion: %{customdata[1]:.1f} %<extra></extra>",
)
fig.update_xaxes(title=titulo_x, showgrid=True, gridcolor=REJILLA)
fig.update_yaxes(title="", showgrid=False)
fig = estilizar(fig, altura=1080, leyenda=True)
fig.update_layout(barmode="stack", bargap=0.25)

if modo == "Participacion (100 %)":
    # Referencia visual de la paridad: a la izquierda de la linea, mayoria de
    # hombres; ningun departamento la cruza.
    fig.add_vline(
        x=50,
        line_dash="dot",
        line_color=TINTA_SUAVE,
        line_width=1,
        annotation_text="50 %",
        annotation_position="top",
        annotation_font=dict(color=TINTA_SUAVE, size=12),
    )
    fig.update_xaxes(range=[0, 100])

st.plotly_chart(fig, width="stretch")

st.info(
    f"En los 33 departamentos mueren más hombres que mujeres"    
)

if indeterminado:
    st.caption(
        f"La categoría Indeterminado reune {indeterminado} registros en todo el país "
        f"({indeterminado / total_pais * 100:.2f} % del total), "
        "así que su segmento es demasiado delgado para verse en la gráfica."
    )

with st.expander("Ver los datos de la gráfica"):
    tabla = resumen.loc[orden_dep[::-1]].copy()
    tabla.columns = [
        "Hombre", "Mujer", "Indeterminado", "Total", "% hombres", "Razón H/M"
    ]
    st.dataframe(tabla.rename_axis("Departamento"), width="stretch")
