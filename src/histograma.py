"""
Pagina "Histograma": distribucion de las muertes a lo largo del ciclo de vida
(2019), agrupando GRUPO_EDAD1 segun la tabla RangoEdadAproximado.xlsx.
"""

import plotly.express as px
import streamlit as st

from datos import (
    REJILLA,
    SERIES,
    SUPERFICIE,
    TINTA,
    TINTA_SUAVE,
    barra_lateral,
    cargar_muertes,
    cargar_rangos_edad,
    estilizar,
    miles,
    muertes_por_ciclo_vida,
    verificar_archivos,
)

verificar_archivos()
barra_lateral()

st.title("Distribución de muertes por etapa del ciclo de vida")
st.caption(
    "Defunciones no fetales de 2019 agrupando los códigos de GRUPO_EDAD1 según los "
    "rangos definidos en RangoEdadAproximado.xlsx."
)

datos = muertes_por_ciclo_vida()
total = int(datos["muertes"].sum())

# "Edad desconocida" no es una etapa del ciclo de vida sino un residuo de
# registro, de modo que puede sacarse de la grafica sin perder el patron.
incluir_desconocida = st.checkbox(
    "Incluir la categoría Edad desconocida",
    value=False,
    help="Son 23 registros en todo el país, invisibles a escala de la gráfica.",
)
grafica = datos if incluir_desconocida else datos[datos["categoria"] != "Edad desconocida"]

# Las etapas a partir de la vejez concentran la mayor parte de las muertes.
adultos_mayores = int(
    datos.loc[datos["categoria"].isin(["Vejez", "Longevidad / Centenarios"]), "muertes"].sum()
)
pico = datos.loc[datos["muertes"].idxmax()]
minimo = grafica.loc[grafica["muertes"].idxmin()]

c1, c2, c3 = st.columns(3)
c1.metric("Total de muertes", miles(total))
c2.metric("De 60 años o más", miles(adultos_mayores), f"{adultos_mayores / total * 100:.1f} % del total")
c3.metric(f"Etapa con más muertes: {pico['categoria']}", miles(pico["muertes"]))

# Una sola serie: el color no codifica identidad, el eje x ya ordena las etapas
# del ciclo de vida de la mas temprana a la mas tardia.
fig = px.bar(
    grafica,
    x="etiqueta",
    y="muertes",
    text="muertes",
    custom_data=["categoria", "rango_edad", "codigos", "porcentaje"],
)
fig.update_traces(
    marker_color=SERIES[0],
    marker_line_color=SUPERFICIE,
    marker_line_width=2,
    texttemplate="%{text:,}",
    textposition="outside",
    textfont=dict(color=TINTA, size=12),
    cliponaxis=False,
    hovertemplate="<b>%{customdata[0]}</b><br>Edad: %{customdata[1]}"
    "<br>Codigos GRUPO_EDAD1: %{customdata[2]}"
    "<br>Muertes: %{y:,}<br>Participacion: %{customdata[3]}%<extra></extra>",
)
fig.update_xaxes(title="", showgrid=False, tickfont=dict(size=11))
fig.update_yaxes(title="Muertes", showgrid=True, gridcolor=REJILLA)
st.plotly_chart(estilizar(fig, altura=560), width="stretch")

st.warning(
    "Las etapas no tienen la misma amplitud: 'Mortalidad neonatal' cubre menos de "
    "un mes y 'Vejez' veinticinco años."
)

with st.expander("Ver la tabla de rangos y los datos de la gráfica"):
    st.dataframe(
        datos[["categoria", "codigos", "rango_edad", "muertes", "porcentaje"]].rename(
            columns={
                "categoria": "Categoria",
                "codigos": "Codigos DANE (GRUPO_EDAD1)",
                "rango_edad": "Rango de edad aproximado",
                "muertes": "Muertes",
                "porcentaje": "% del total",
            }
        ),
        width="stretch",
        hide_index=True,
    )
