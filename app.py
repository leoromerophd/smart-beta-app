import streamlit as st
import sp
import techno
import consumo
import industrial
import financials
import semis
import software
import energy 
import value
import growth
import midcap

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Configuración de la página
st.image("./images/Banner.png")

# Función para aplicar CSS personalizado desde un archivo
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Aplicar el CSS personalizado
local_css('./style.css')


# Nombres de las pestañas
tab_names = ["S&P", "Tecnología", "Consumo", "Industrial", 
             "Financiera", "Semis", "Software", "Energy", 
             "Value", "Growth", "Midcap"]


# Inicializar la pestaña activa en el estado de la sesión
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = "S&P"

# Creación de las pestañas
tabs = st.tabs(tab_names)

# Función para mostrar el contenido de la pestaña
def show_tab_content(tab_name):
    if tab_name == "S&P":
        sp.show()
    elif tab_name == "Tecnología":
        techno.show()
    elif tab_name == "Consumo":
        consumo.show()
    elif tab_name == "Industrial":
        industrial.show()
    elif tab_name == "Financiera":
        financials.show()
    elif tab_name == "Semis":
        semis.show()
    elif tab_name == "Software":
        software.show()
    elif tab_name == "Energy":
        energy.show()
    elif tab_name == "Value":
        value.show()
    elif tab_name == "Growth":
        growth.show()
    elif tab_name == "Midcap":
        midcap.show()


# Mostrar contenido basado en la pestaña activa
for i, tab_name in enumerate(tab_names):
    with tabs[i]:
        show_tab_content(tab_name)

