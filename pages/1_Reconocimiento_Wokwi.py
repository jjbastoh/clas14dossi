
import streamlit as st
import json
import base64
import paho.mqtt.client as mqtt

from openai import OpenAI


# ==========================================
# CONFIGURACION
# ==========================================

st.title("🤖 Reconocimiento de alimentos")
st.subheader("NutriScan - Inteligencia artificial")

MQTT_SERVER = "157.230.214.127"
MQTT_PORT = 1883
MQTT_TOPIC = "nutriscan/resultado"


# ==========================================
# VARIABLES COMPARTIDAS
# ==========================================

variables = {
    "nivel": "",
    "alimento": "",
    "justificacion": "",
    "mensaje_voz": "",
    "confianza": 0.0
}

for clave, valor in variables.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor


# ==========================================
# VERIFICAR OPENAI
# ==========================================

st.caption("Sistema de reconocimiento NutriScan")

api_key = st.text_input(
    "Ingresa tu API Key de OpenAI",
    type="password"
)


# ==========================================
# CODIFICAR IMAGEN
# ==========================================

def encode_image(image):

    return base64.b64encode(
        image.getvalue()
    ).decode("utf-8")


# ==========================================
# ANALIZAR ALIMENTO
# ==========================================

def analizar_alimento(image, client):

    imagen_base64 = encode_image(image)

    mime_type = image.type

    prompt = """
    Eres NutriScan, un sistema de reconocimiento
    y evaluacion nutricional de alimentos.

    Analiza la imagen e identifica el alimento.

    Clasifica el alimento en:

    BUENO:
    Alimentos generalmente nutritivos y adecuados
    para una alimentacion equilibrada.

    MEDIO:
    Alimentos cuyo consumo depende de la cantidad,
    preparacion e ingredientes.

    MALO:
    Productos con caracteristicas nutricionales
    desfavorables, como exceso de azucares libres,
    sodio o grasas saturadas, cuando exista
    evidencia suficiente.

    REGLAS:

    - No inventes ingredientes.
    - No inventes nutrientes.
    - No clasifiques solamente por apariencia.
    - Si no identificas el alimento utiliza
      NO_IDENTIFICADO.
    - La confianza debe ser un valor entre 0 y 1.
    - Responde en español.
    - Devuelve exclusivamente JSON valido.

    ESTRUCTURA:

    {
      "alimento": "nombre",
      "nivel": "bueno",
      "justificacion": "explicacion",
      "confianza": 0.90,
      "voz": "El alimento ha sido identificado."
    }
    """

    response = client.chat.completions.create(

        model="gpt-4o",

        messages=[
            {
                "role": "user",
                "content": [

                    {
                        "type": "text",
                        "text": prompt
                    },

                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                f"data:{mime_type};base64,"
                                f"{imagen_base64}"
                            )
                        }
                    }

                ]
            }
        ],

        response_format={
            "type": "json_object"
        },

        max_tokens=800
    )

    contenido = response.choices[0].message.content

    if not contenido:
        raise ValueError("OpenAI no devolvio resultados.")

    return json.loads(contenido)


# ==========================================
# ENVIAR RESULTADO MQTT
# ==========================================

def enviar_mqtt(nivel):

    cliente = mqtt.Client(
        client_id="NutriScan_Streamlit"
    )

    cliente.connect(
        MQTT_SERVER,
        MQTT_PORT,
        60
    )

    mensaje = {
        "nivel": nivel
    }

    try:

        info = cliente.publish(
            MQTT_TOPIC,
            json.dumps(mensaje),
            qos=1
        )

        info.wait_for_publish(timeout=10)

        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError("Error publicando MQTT")

    finally:

        cliente.disconnect()


# ==========================================
# SELECCION DE IMAGEN
# ==========================================

st.markdown("### 📸 Selecciona una imagen")

opcion = st.radio(
    "Fuente de imagen:",
    ["Cargar imagen", "Usar cámara"],
    horizontal=True
)

if opcion == "Cargar imagen":

    imagen = st.file_uploader(
        "Selecciona un alimento",
        type=["jpg", "jpeg", "png"]
    )

else:

    imagen = st.camera_input(
        "Toma una fotografía"
    )


if imagen:

    st.image(
        imagen,
        caption="Imagen seleccionada",
        use_container_width=True
    )


# ==========================================
# BOTON ANALIZAR
# ==========================================

if st.button(
    "🔍 ANALIZAR Y ENVIAR A WOKWI",
    use_container_width=True
):

    if not api_key:

        st.error("Ingresa tu API Key de OpenAI.")

    elif imagen is None:

        st.warning("Debes seleccionar una imagen.")

    else:

        try:

            with st.spinner("Analizando alimento..."):

                client = OpenAI(
                    api_key=api_key
                )

                resultado = analizar_alimento(
                    imagen,
                    client
                )

            nivel = str(
                resultado.get("nivel", "")
            ).lower().strip()

            if nivel not in [
                "bueno",
                "medio",
                "malo",
                "no_identificado"
            ]:

                raise ValueError(
                    "Clasificacion no valida."
                )

            confianza = float(
                resultado.get("confianza", 0)
            )

            if not 0 <= confianza <= 1:
                raise ValueError("Confianza fuera de rango.")

            st.session_state.alimento = (
                resultado.get("alimento", "No identificado")
            )

            st.session_state.nivel = nivel

            st.session_state.justificacion = (
                resultado.get("justificacion", "")
            )

            st.session_state.confianza = confianza

            st.session_state.mensaje_voz = (
                resultado.get("voz", "")
            )

            st.divider()

            st.subheader("Resultado del reconocimiento")

            st.write(
                "Alimento:",
                st.session_state.alimento
            )

            if nivel == "bueno":

                st.success("🟢 ALIMENTO BUENO")

            elif nivel == "medio":

                st.warning("🟡 ALIMENTO MEDIO")

            elif nivel == "malo":

                st.error("🔴 ALIMENTO MALO")

            else:

                st.info("ALIMENTO NO IDENTIFICADO")

            st.markdown("### Justificación")

            st.write(
                st.session_state.justificacion
            )

            st.write(
                f"Confianza estimada: "
                f"{confianza * 100:.1f}%"
            )

            if nivel in ["bueno", "medio", "malo"]:

                with st.spinner("Enviando resultado a Wokwi..."):

                    enviar_mqtt(nivel)

                st.success(
                    "Resultado enviado al ESP32 correctamente."
                )

            else:

                st.warning(
                    "No se envio ningun comando al ESP32."
                )

        except Exception as e:

            st.error(f"Error: {e}")


# ==========================================
# ULTIMO RESULTADO
# ==========================================

if st.session_state.nivel:

    st.divider()

    st.caption("Ultimo resultado almacenado")

    st.write(
        f"Alimento: {st.session_state.alimento}"
    )

    st.write(
        f"Clasificacion: {st.session_state.nivel.upper()}"
    )

