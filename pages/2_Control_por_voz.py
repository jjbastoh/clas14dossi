
import streamlit as st
import io
from gtts import gTTS


# ==========================================
# CONFIGURACION
# ==========================================

st.title("🎙️ Respuesta por voz")

st.subheader("NutriScan - Sistema auditivo")


# ==========================================
# VARIABLES COMPARTIDAS
# ==========================================

variables = {
    "nivel": "",
    "mensaje_voz": "",
    "alimento": ""
}

for clave, valor in variables.items():

    if clave not in st.session_state:
        st.session_state[clave] = valor


# ==========================================
# MOSTRAR RESULTADO
# ==========================================

if st.session_state.nivel:

    nivel = st.session_state.nivel

    st.write(
        f"Alimento identificado: "
        f"{st.session_state.alimento}"
    )

    if nivel == "bueno":

        st.success("🟢 ALIMENTO BUENO")

    elif nivel == "medio":

        st.warning("🟡 ALIMENTO MEDIO")

    elif nivel == "malo":

        st.error("🔴 ALIMENTO MALO")

    else:

        st.info("ALIMENTO NO IDENTIFICADO")


    # ======================================
    # GENERAR VOZ
    # ======================================

    st.divider()

    st.markdown("### 🔊 Reproducir resultado")

    if st.button(
        "🎙️ GENERAR RESPUESTA POR VOZ",
        use_container_width=True
    ):

        try:

            alimento = st.session_state.alimento

            # Generar mensaje completo según clasificación

            if nivel == "bueno":

                texto = (
                    f"El alimento identificado es {alimento}. "
                    "Su clasificación es alimento bueno. "
                    "Es una opción favorable para tu alimentación."
                )

            elif nivel == "medio":

                texto = (
                    f"El alimento identificado es {alimento}. "
                    "Su clasificación es alimento medio. "
                    "Se recomienda consumirlo con moderación."
                )

            elif nivel == "malo":

                texto = (
                    f"El alimento identificado es {alimento}. "
                    "Su clasificación es alimento malo. "
                    "Se recomienda evitar su consumo frecuente."
                )

            else:

                texto = (
                    f"El alimento identificado es {alimento}. "
                    "No fue posible determinar su clasificación."
                )

            with st.spinner("Generando audio..."):

                audio = io.BytesIO()

                tts = gTTS(
                    text=texto,
                    lang="es",
                    slow=False
                )

                tts.write_to_fp(audio)

                audio.seek(0)

                st.session_state.audio = audio.getvalue()

            st.success("Audio generado correctamente.")

        except Exception as e:

            st.error(
                f"Error generando audio: {e}"
            )


    # ======================================
    # REPRODUCIR AUDIO
    # ======================================

    if "audio" in st.session_state:

        st.audio(
            st.session_state.audio,
            format="audio/mp3"
        )

    st.info(
        st.session_state.mensaje_voz
    )


else:

    st.warning(
        "Todavia no hay un alimento analizado."
    )

    st.write(
        "Primero ingresa a Reconocimiento de alimentos "
        "y realiza un analisis."
    )

    st.page_link(
        "pages/1_Reconocimiento_Wokwi.py",
        label="Ir al reconocimiento de alimentos",
        icon="🤖"
    )


