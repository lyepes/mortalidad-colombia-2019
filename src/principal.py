"""
Pagina principal del tablero de muertes no fetales en Colombia (2019).

Este archivo es el punto de entrada: define el menu y delega cada vista a su
propio archivo. Ejecutar siempre con:

    streamlit run principal.py

Menu actual:
  - Mapa               -> mapa.py
  - Grafico de lineas  -> lineas.py
  - Grafico de barras  -> barras.py
  - Grafico circular   -> circular.py
  - Tabla              -> tabla.py
  - Barras apiladas    -> apiladas.py
  - Histograma         -> histograma.py

Fuentes de datos (ver datos.py):
  - data/Anexo1.NoFetal2019_CE_15-03-23.xlsx
  - data/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx (catalogo CIE-10)
  - data/Divipola_CE_.xlsx (Hoja3)
  - data/RangoEdadAproximado.xlsx (etapas del ciclo de vida)
"""

import streamlit as st

st.set_page_config(
    page_title="Muertes no fetales en Colombia 2019",
    page_icon="📊",
    layout="wide",
)

# Cada entrada del menu apunta a un archivo propio. La pagina marcada con
# default=True es la que se abre al iniciar la aplicacion.
PAGINAS = [
    st.Page("mapa.py", title="Mapa", icon="🗺️", default=True),
    st.Page("lineas.py", title="Gráfico de líneas", icon="📈"),
    st.Page("barras.py", title="Gráfico de barras", icon="📊"),
    st.Page("circular.py", title="Gráfico circular", icon="🥧"),
    st.Page("tabla.py", title="Tabla", icon="📋"),
    st.Page("apiladas.py", title="Gráfico de barras apiladas", icon="🧱"),
    st.Page("histograma.py", title="Histograma", icon="📶"),
]

# position="hidden" desactiva el menu automatico, que Streamlit dibuja en lo alto
# de la barra lateral y fuera del flujo de elementos. Al construirlo a mano con
# st.page_link se controla el orden: primero el titulo entre lineas y despues las
# opciones. st.page_link marca sola la pagina activa.
menu = st.navigation(PAGINAS, position="hidden")

with st.sidebar:
    st.divider()
    st.markdown("### Menu")
    st.divider()
    for pagina in PAGINAS:
        st.page_link(pagina)

menu.run()
