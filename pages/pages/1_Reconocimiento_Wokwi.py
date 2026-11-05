
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
# INICIALIZAR VARIABLES COMPARTIDAS
# ==========================================

if "nivel" not in st.session_state:
    st.session_state.nivel = ""

if "alimento" not in st.session_state:
    st.session_state.alimento = ""

if "justificacion" not in st.session_state:
    st.session_state.justificacion = ""

if "mensaje_voz" not in st.session_state:
    st.session_state.mensaje_voz = ""

if "confianza" not in st.session_state:
    st.session_state.confianza = 0.0


# ==========================================
# API KEY
# ==========================================

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
# RECONOCIMIENTO Y CLASIFICACION
# ==========================================

def analizar_alimento(image, client):

    imagen_base64 = encode_image(image)

    mime_type = image.type

    prompt = """
    Eres NutriScan, un sistema de reconocimiento
    y evaluacion nutricional de alimentos.

    Analiza la imagen, identifica el alimento
    y clasificalo en una de estas categorias:

    BUENO:
    Alimentos generalmente nutritivos y adecuados
    para formar parte de una alimentacion equilibrada.

    MEDIO:
    Alimentos cuyo consumo depende de la cantidad,
    preparacion, ingredientes o frecuencia.

    MALO:
    Productos con caracteristicas nutricionales
    desfavorables, como exceso de azucares libres,
    sodio o grasas saturadas, cuando exista
    evidencia suficiente para determinarlo.

    REGLAS:

    - No clasifiques solamente por apariencia.
    - No inventes ingredientes ni nutrientes.
    - Si no puedes identificar el alimento,
      utiliza NO_IDENTIFICADO.
    - Si no tienes informacion suficiente,
      indica que la clasificacion es preliminar.
    - Responde en español.
    - Devuelve exclusivamente JSON valido.

    Estructura:

    {
      "alimento": "nombre",
      "nivel": "bueno, medio, malo o no_identificado",
      "justificacion": "explicacion",
      "confianza": 0.0,
      "voz": "mensaje para comunicar el resultado"
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

    return json.loads(
        response.choices[0].message.content
    )


# ==========================================
# ENVIAR RESULTADO A MQTT
# ==========================================

def enviar_mqtt(nivel):

    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION1,
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

    info = cliente.publish(
        MQTT_TOPIC,
        json.dumps(mensaje),
        qos=1
    )

    info.wait_for_publish()

    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        raise RuntimeError("Error publicando mensaje MQTT")

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

        st.error("Ingresa tu API Key.")

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


            # Guardar resultados compartidos

            nivel = resultado["nivel"].lower().strip()

            if nivel not in [
                "bueno",
                "medio",
                "malo",
                "no_identificado"
            ]:
                raise ValueError("Clasificacion no valida")

            st.session_state.alimento = resultado["alimento"]

            st.session_state.nivel = nivel

            st.session_state.justificacion = (
                resultado["justificacion"]
            )

            st.session_state.confianza = float(
                resultado["confianza"]
            )

            st.session_state.mensaje_voz = (
                resultado["voz"]
            )


            # Mostrar resultado

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


            st.write("### Justificacion")

            st.write(
                st.session_state.justificacion
            )

            st.write(
                f"Confianza estimada: "
                f"{st.session_state.confianza * 100:.1f}%"
            )


            # Enviar a Wokwi

            if nivel in ["bueno", "medio", "malo"]:

                with st.spinner("Enviando a Wokwi mediante MQTT..."):

                    enviar_mqtt(nivel)

                st.success(
                    "Resultado enviado al ESP32 correctamente."
                )

            else:

                st.warning(
                    "No se envio ningun comando al ESP32."
                )


        except Exception as e:

            st.error(
                f"Error: {e}"
            )


# ==========================================
# MOSTRAR ULTIMO RESULTADO
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

