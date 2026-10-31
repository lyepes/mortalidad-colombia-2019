"""
Pagina "Tabla": las 10 principales causas de muerte en Colombia (2019),
con su codigo CIE-10, nombre y total de casos.
"""

import streamlit as st

from datos import (
    barra_lateral,
    cargar_muertes,
    miles,
    principales_causas,
    verificar_archivos,
)

TOP_N = 10

verificar_archivos()
barra_lateral()

st.title("Las 10 principales causas de muerte")
st.caption(
    "Defunciones no fetales de 2019 agrupadas por categoria de la CIE-10 (codigo "
    "de tres caracteres), ordenadas de mayor a menor. El nombre de cada causa "
    "proviene del catalogo del Anexo2."
)

datos = principales_causas(TOP_N)
total_pais = len(cargar_muertes())

c1, c2, c3 = st.columns(3)
c1.metric("Casos en estas 10 causas", miles(datos["casos"].sum()))
c2.metric("Participacion en el total", f"{datos['porcentaje'].sum():.1f} %")
c3.metric("Primera causa", datos.loc[0, "codigo"])

COLUMNAS = {
    "codigo": "Codigo CIE-10",
    "causa": "Nombre de la causa",
    "casos": "Total de casos",
    "porcentaje": "% del total",
    "capitulo_cie10": "Capitulo CIE-10",
}

st.dataframe(
    datos.rename(columns=COLUMNAS),
    width="stretch",
    hide_index=True,
    column_config={
        "Total de casos": st.column_config.ProgressColumn(
            "Total de casos",
            min_value=0,
            max_value=int(datos["casos"].max()),
            format="%d",
        ),
        "% del total": st.column_config.NumberColumn("% del total", format="%.2f %%"),
    },
)
st.caption(
    f"Las demás causas suman {miles(total_pais - datos['casos'].sum())} casos "
    f"de un total nacional de {miles(total_pais)}."
)

st.info(
    "Se esta tomando como referencia el Código de la CIE-10 tres caracteres"
)
