"""
Pagina "Grafico de lineas": total de muertes por mes en Colombia (2019),
mostrando las variaciones a lo largo del ano.
"""

import plotly.express as px
import streamlit as st

from datos import (
    MESES,
    REJILLA,
    SERIES,
    SUPERFICIE,
    TINTA,
    TINTA_SUAVE,
    agregar,
    barra_lateral,
    estilizar,
    miles,
    verificar_archivos,
)

verificar_archivos()
barra_lateral()

st.title("Total de muertes por mes")
st.caption(
    "Total nacional de defunciones no fetales registradas en cada mes de 2019. "
    "La línea punteada marca el promedio mensual."
)

datos = agregar("mes").sort_values("mes")
datos["mes_nombre"] = datos["mes"].map(MESES)
promedio = datos["muertes"].mean()

fig = px.line(datos, x="mes_nombre", y="muertes", markers=True)
fig.update_traces(
    line=dict(color=SERIES[0], width=2),
    marker=dict(size=9, color=SERIES[0], line=dict(color=SUPERFICIE, width=2)),
    hovertemplate="<b>%{x}</b><br>Muertes: %{y:,}<extra></extra>",
)
# Referencia del promedio: una sola escala, sin segundo eje.
fig.add_hline(
    y=promedio,
    line_dash="dot",
    line_color=TINTA_SUAVE,
    line_width=1,
    annotation_text=f"Promedio mensual: {miles(promedio)}",
    annotation_position="top left",
    annotation_font=dict(color=TINTA_SUAVE, size=12),
)
# Etiquetas directas solo en el maximo y el minimo, no en cada punto.
maximo = datos.loc[datos["muertes"].idxmax()]
minimo = datos.loc[datos["muertes"].idxmin()]
for fila, desplazamiento in ((maximo, 18), (minimo, -18)):
    fig.add_annotation(
        x=fila["mes_nombre"],
        y=fila["muertes"],
        text=f"<b>{miles(fila['muertes'])}</b>",
        showarrow=False,
        yshift=desplazamiento,
        font=dict(color=TINTA, size=12),
    )
fig.update_yaxes(title="Muertes", rangemode="tozero", gridcolor=REJILLA)
fig.update_xaxes(title="Mes (2019)")
st.plotly_chart(estilizar(fig), width="stretch")

variacion = (maximo["muertes"] - minimo["muertes"]) / minimo["muertes"] * 100
c1, c2, c3 = st.columns(3)
c1.metric(f"Mes con más muertes: {maximo['mes_nombre']}", miles(maximo["muertes"]))
c2.metric(f"Mes con menos muertes: {minimo['mes_nombre']}", miles(minimo["muertes"]))
c3.metric("Diferencia entre extremos", f"{variacion:.1f} %")

st.info(    
    "Al comparar meses conviene tener en cuenta su duración."
)

with st.expander("Ver los datos de la gráfica"):
    st.dataframe(
        datos[["mes", "mes_nombre", "muertes"]].rename(
            columns={"mes": "Mes (número)", "mes_nombre": "Mes", "muertes": "Muertes"}
        ),
        width="stretch",
        hide_index=True,
    )
