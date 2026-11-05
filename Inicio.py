
import streamlit as st

st.set_page_config(
    page_title="NutriScan",
    page_icon="🥗",
    layout="centered"
)

st.title("🥗 NUTRISCAN")

st.subheader("Detector inteligente de alimentos")

st.write(
    "Bienvenido a NutriScan. "
    "Selecciona una de las siguientes opciones "
    "para interactuar con el sistema."
)

st.divider()

st.markdown("### 📡 Aplicaciones disponibles")

st.page_link(
    "pages/1_Reconocimiento_Wokwi.py",
    label="Reconocimiento de alimentos y control Wokwi",
    icon="🤖"
)

st.page_link(
    "pages/2_Control_por_voz.py",
    label="Control y respuesta por voz",
    icon="🎙️"
)

st.divider()

st.info(
    "NutriScan integra inteligencia artificial, "
    "comunicación MQTT, reconocimiento de imágenes "
    "y respuestas auditivas."
)
