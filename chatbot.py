import streamlit as st
from langchain_openai import ChatOpenAI
from streamlit_extras.colored_header import colored_header
from langdetect import detect
from PIL import Image
import pytesseract
import fitz
from docx import Document
import pandas as pd
import speech_recognition as sr
import tempfile
import mysql.connector
import os
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import re

chatbot_name = "AURA"

st.set_page_config(
    page_title=chatbot_name + " - AI",
    page_icon="img/aura_avatar.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
        :root {
            --unab-negro: #000000;
            --unab-gris-muy-oscuro: #121212;
            --unab-gris-oscuro: #2E2E2E;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(
                260deg,
                var(--unab-negro) 0%,
                var(--unab-gris-muy-oscuro) 40%,
                var(--unab-gris-oscuro) 100%
            );
        }

        .st-emotion-cache-11z2sv9 {
            background-color: #bfd9ff;
        }


        .st-emotion-cache-bbrpxx {
            color: white;
        }


        .st-emotion-cache-4zpzjl {
            background-color: #e71a88;
        }

        .st-emotion-cache-jmw8un {
            background-color: #C6C6C6;
        }

        .st-emotion-cache-janbn0 {
            background-color: #121212;
        
        }

        .st-emotion-cache-p4micv {
            width: 2.5rem;
            height: 2.5rem;
        }

    </style>
""", unsafe_allow_html=True)

# Función para detectar idioma
def detectar_idioma(texto):
    try:
        return detect(texto)
    except:
        return "es"

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: white;'>AURA IA</h1>
        <div style='background: var(--unab-azul-oscuro); height: 3px; width: 50%; margin: auto;'></div>
    </div>
    """, unsafe_allow_html=True)

    idioma_seleccionado = st.radio("🌐 Idioma", ["Español", "Inglés"], index=0)
    tema = st.selectbox("📘 Tema Académico", ["General", "Matemáticas", "Programación", "IA", "Calidad de Software"])
    explicativo = st.toggle("🧠 Explicación paso a paso")
    respuesta_con_voz = st.toggle("🔊 ¿Responder con voz?", value=False)
    velocidad_voz = st.selectbox("🎚️ Velocidad de voz", ["Normal", "Lenta"], index=0)
    st.session_state.respuesta_con_voz = respuesta_con_voz
    st.session_state.slow_voice = True if velocidad_voz == "Lenta" else False

    with st.expander("⚙️ Configuración avanzada", expanded=True):
        model_name = st.selectbox("🧠 Modelo AI", ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"], index=0)
        temperature = st.slider("🎨 Creatividad", 0.0, 1.0, 0.2, 0.1)
        max_length = st.slider("🔯 Longitud de respuesta", 50, 300, 150)

    uploaded_file = st.file_uploader("📄 Sube un archivo (PDF, imagen, Word o Excel)", type=["pdf", "png", "jpg", "docx", "xlsx"])
    if "texto_extraido" not in st.session_state:
        st.session_state.texto_extraido = ""

    if uploaded_file:
        texto_extraido = ""
        if uploaded_file.type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in doc:
                texto_extraido += page.get_text()
        elif "image" in uploaded_file.type:
            img = Image.open(uploaded_file)
            texto_extraido = pytesseract.image_to_string(img, lang='spa+eng')
            st.image(img, caption="Imagen cargada", use_container_width=True)
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            texto_extraido = "\n".join([para.text for para in doc.paragraphs])
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            texto_extraido = df.to_string(index=False)

        st.session_state.texto_extraido = texto_extraido
        st.markdown("#### 🫾 Texto extraído")
        st.code(texto_extraido, language="markdown")

    if st.button("🔄 Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎙️ Grabar mensaje de voz")

    audio_bytes = audio_recorder(
        pause_threshold=0.5,
        sample_rate=41000,
        icon_size="2x",
        recording_color="#e71a88",
        neutral_color="#C6C6C6",
        icon_name="robot",
        text="Presiona para grabar",
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            try:
                texto_voz = recognizer.recognize_google(audio_data, language="es-ES")
                st.success("✅ Texto reconocido:")

                
                st.write(texto_voz)

                if st.button("➡️ Enviar como pregunta", key="btn_audio_send"):
                    st.session_state.messages.append({"role": "user", "content": texto_voz})
                    st.session_state.audio_pendiente = True
                    st.rerun()
            except Exception as e:
                st.error(f"❌ No se pudo reconocer el audio: {e}")

    st.markdown("---")
    st.markdown("### 🗃️ Consulta a base de datos MySQL")

    consulta_usuario = st.text_input("Escribe una pregunta sobre la base de datos", key="consulta_mysql")

    if consulta_usuario:
        prompt_sql = f"""
        Eres un experto en bases de datos. Convierte la siguiente instrucción en una consulta SQL segura:
        "{consulta_usuario}"
        """
        try:
            consulta_sql = st.session_state.llm.invoke([{"role": "user", "content": prompt_sql}]).content.strip()
            st.markdown("#### 🧠 Consulta generada o respuesta del modelo:")
            
            # Limpieza y validación
            consulta_limpia = re.sub(r'--.*', '', consulta_sql).strip()
            primer_comando = consulta_limpia.lower().split()[0]

            comandos_permitidos = ["select", "show", "describe", "insert", "update"]

            if primer_comando in comandos_permitidos:
                st.code(consulta_sql, language="sql")

                conn = mysql.connector.connect(
                    host=st.secrets["DB_HOST"],
                    user=st.secrets["DB_USER"],
                    password=st.secrets["DB_PASSWORD"],
                    database=st.secrets["DB_NAME"]
                )

                cursor = conn.cursor()
                cursor.execute(consulta_sql)

                if primer_comando == "select":
                    resultados = cursor.fetchall()
                    st.markdown("#### 📊 Resultados:")
                    for row in resultados:
                        st.write(row)
                else:
                    conn.commit()
                    st.success("✅ Consulta ejecutada correctamente.")

                cursor.close()
                conn.close()
            else:
                st.warning("⚠️ Solo se permiten SELECT, SHOW, DESCRIBE, INSERT y UPDATE.")
        except Exception as e:
            st.error(f"❌ Error al ejecutar la consulta: {e}")


# Encabezado principal
colored_header(label="🤖    " + chatbot_name + " AI - Chat Bot", description="Tu asistente académico", color_name="blue-30")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Cargar modelo
@st.cache_resource
def load_llm():
    return ChatOpenAI(
        model=st.session_state.get("model_name", "gpt-3.5-turbo"),
        temperature=st.session_state.get("temperature", 0.2),
        max_tokens=st.session_state.get("max_length", 150),
        api_key=st.secrets["OPENAI_API_KEY"]
    )

try:
    st.session_state.llm = load_llm()
except Exception as e:
    st.error(f"Error al cargar el modelo: {str(e)}")
    st.stop()


# imagen del avatar
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar_icon = None
        if message["role"] == "user":
            avatar_icon = "img/user_avatar.png"  # Ruta o URL del avatar del usuario
        elif message["role"] == "assistant":
            avatar_icon = "img/aura_avatar.png" # Ruta o URL del avatar del chatbot

        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])



# Entrada por chat
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.audio_pendiente = True
    st.rerun()

# Procesamiento (voz o texto)
if st.session_state.get("audio_pendiente"):
    try:
        st.session_state.messages = [
            {
                "role": "system",
                "content": f"""
                Eres {chatbot_name}, un tutor virtual creado por estudiantes de la Universidad Dr. Andrés Bello (UNAB) en marzo de 2025, en El Salvador.
                Tu rol es ayudar en temas académicos como {tema}.
                Responde en el idioma seleccionado: {idioma_seleccionado}.
                {"Explica tus respuestas paso a paso." if explicativo else ""}
                Si no sabes la respuesta, admite que no la sabes.
                """
            }
        ] + [m for m in st.session_state.messages if m["role"] != "system"]

        chat_history = st.session_state.messages[-4:]
        if st.session_state.texto_extraido:
            chat_history.append({
                "role": "user",
                "content": "Este es el contenido del archivo que subí:\n" + st.session_state.texto_extraido
            })

        with st.spinner("AURA está pensando..."):
            response = st.session_state.llm.invoke(chat_history).content

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant", avatar="img/aura_avatar.png"):
            st.markdown(response)

        if st.session_state.get("respuesta_con_voz", False):
            try:
                idioma_gtts = "es" if idioma_seleccionado == "Español" else "en"
                tts = gTTS(text=response, lang=idioma_gtts, slow=st.session_state.slow_voice)
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                st.audio(audio_path, format="audio/mp3")
            except Exception as e:
                st.warning(f"No se pudo generar audio: {e}")

        st.session_state.audio_pendiente = False
    except Exception as e:
        st.error(f"Error procesando la respuesta: {e}")
