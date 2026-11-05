
import streamlit as st
import io
from gtts import gTTS


# ==========================================
# CONFIGURACION
# ==========================================

st.title("🎙️ Respuesta por voz")

st.subheader("NutriScan - Sistema auditivo")


# ==========================================
# VERIFICAR RESULTADO COMPARTIDO
# ==========================================

if "nivel" not in st.session_state:
    st.session_state.nivel = ""

if "mensaje_voz" not in st.session_state:
    st.session_state.mensaje_voz = ""

if "alimento" not in st.session_state:
    st.session_state.alimento = ""


# ==========================================
# MOSTRAR INFORMACION
# ==========================================

if st.session_state.nivel:

    nivel = st.session_state.nivel

    st.write(
        f"Alimento identificado: {st.session_state.alimento}"
    )

    if nivel == "bueno":

        st.success("🟢 ALIMENTO BUENO")

    elif nivel == "medio":

        st.warning("🟡 ALIMENTO MEDIO")

    elif nivel == "malo":

        st.error("🔴 ALIMENTO MALO")


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

            with st.spinner("Generando audio..."):

                texto = st.session_state.mensaje_voz

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

