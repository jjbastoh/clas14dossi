import streamlit as st

st.set_page_config(page_title="Interfaces Multimodales", page_icon="📡")

st.title("INTERFACES MULTIMODALES")
st.subheader("Control de actuadores por MQTT")

st.write(
    "Selecciona una de las aplicaciones en el menú lateral "
    "o usa los accesos directos de abajo."
)

st.page_link("pages/1_Control_por_voz.py", label="Control por voz", icon="🎙️")
st.page_link("pages/2_Control_MQTT.py", label="Control con botones y slider", icon="🎛️")
