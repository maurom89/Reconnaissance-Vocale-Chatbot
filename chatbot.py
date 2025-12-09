# -------------------------------
# Import libraries
# -------------------------------
import streamlit as st
from groq import Groq
import json
import speech_recognition as sr
from gtts import gTTS
import os

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="🎤",
    layout="wide"
)

# -------------------------------
# Initialize Groq Client
# -------------------------------
client = Groq(api_key=)  # <<< CHANGE THIS

# -------------------------------
# Memory
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# Get AI Response
# -------------------------------
def get_ai_response(user_message):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

# -------------------------------
# Clear Chat
# -------------------------------
def clear_chat():
    st.session_state.messages = []
    st.rerun()

# -------------------------------
# Download Chat
# -------------------------------
def download_chat():
    if st.session_state.messages:
        return json.dumps(st.session_state.messages, indent=2)
    return None

# -------------------------------
# TTS – Make AI Speak
# -------------------------------
def speak_text(text):
    try:
        audio_path = os.path.join(os.getcwd(), "ai_voice.mp3")
        tts = gTTS(text=text, lang="fr")
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"Erreur TTS : {e}")
        return None

# -------------------------------
# Voice Recording (Your Working Code)
# -------------------------------
def record_voice():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.5

    try:
        with microphone as source:
            st.info("🎤 Écoute en cours... Parlez maintenant.")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            st.info("🔄 Traitement de votre voix...")

            text = recognizer.recognize_google(audio, language="fr-FR")
            st.success(f"🗣️ Vous avez dit : {text}")
            return text

    except sr.WaitTimeoutError:
        st.error("⏰ Aucun son détecté.")
    except sr.UnknownValueError:
        st.error("❓ Impossible de comprendre l'audio.")
    except sr.RequestError:
        st.error("🌐 Problème Internet pour la transcription.")
    except Exception as e:
        st.error(f"⚠️ Erreur : {e}")

    return None

# -------------------------------
# UI Header
# -------------------------------
st.title("🤖 Assistant Vocal IA")
st.write("Parlez ou écrivez... Je réponds aussi avec une voix humaine 🔊")

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("📖 Instructions")
    st.markdown("""
    **Deux façons d'utiliser l'assistant :**

    - 📝 Tapez un message
    - 🎤 Cliquez sur le bouton micro et parlez

    **Conseils Micro :**
    - Parlez clairement
    - Soyez proche du micro
    - Attendez les messages "Écoute" / "Traitement"
    """)

# -------------------------------
# Model Info
# -------------------------------
with st.expander("ℹ️ Modèle utilisé", expanded=True):
    st.markdown("""
    **LLaMA 3.1 – 8B Instant**
    
    - IA rapide et efficace  
    - Compréhension du français  
    - Parfait pour conversation  
    """)

# -------------------------------
# Buttons (Clear / Download)
# -------------------------------
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("🗑️ Effacer"):
        clear_chat()

with col2:
    data = download_chat()
    if data:
        st.download_button(
            label="📥 Télécharger",
            data=data,
            file_name="chat.json",
            mime="application/json"
        )

# -------------------------------
# Display Chat History
# -------------------------------
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# -------------------------------
# VOICE INPUT SECTION
# -------------------------------
col_input, col_voice = st.columns([4, 1])

with col_voice:
    use_voice = st.button("🎤 Micro", use_container_width=True)

if use_voice:
    spoken = record_voice()

    if spoken:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": spoken})
        st.chat_message("user").write(spoken)

        # AI thinking
        with st.spinner("🤔 Réflexion..."):
            reply = get_ai_response(spoken)

        # Add AI reply
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)

        # SPEAK AI REPLY 🔊
        audio_file = speak_text(reply)
        if audio_file:
            st.audio(audio_file, format="audio/mp3")

        st.rerun()

# -------------------------------
# TEXT INPUT SECTION
# -------------------------------
if prompt := st.chat_input("Écrivez ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("🤔 Réflexion..."):
        reply = get_ai_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)

    # SPEAK AI REPLY 🔊
    audio_file = speak_text(reply)
    if audio_file:
        st.audio(audio_file, format="audio/mp3")