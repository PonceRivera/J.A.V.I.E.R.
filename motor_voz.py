import requests
import os
import ctypes
import speech_recognition as sr
import time
import uuid
import glob
import pyaudio
import subprocess

try:
    from faster_whisper import WhisperModel
    print("[SISTEMA] Cargando modelo de voz Whisper (Inteligencia Avanzada, 100% offline)...")
    # Cargamos el modelo 'small' que es muy rápido y preciso, optimizado para CPU.
    whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
    USAR_WHISPER = True
    print("[SISTEMA] Whisper cargado correctamente. JAVIER ahora tiene oídos perfectos.")
except Exception as e:
    print(f"[SISTEMA] No se pudo cargar Whisper, se usará Google básico de respaldo. Error: {e}")
    USAR_WHISPER = False

API_KEY = "sk_d6dd973d10518be093d0847f520b9249a3bbf88c51655f13"

on_estado_cambio = None

_current_alias = None
PTT_PRESIONADO = False

def limpiar_mp3_viejos(archivo_excluido=None):
    """Borra todos los archivos temporales de audio excepto el indicado."""
    for f in glob.glob("temp_*.mp3"):
        if archivo_excluido and os.path.basename(f) == os.path.basename(archivo_excluido):
            continue
        try:
            os.remove(f)
        except:
            pass

# Limpiar al inicio
limpiar_mp3_viejos()

def detener_audio():
    """Detiene cualquier audio de JAVIER que se esté reproduciendo actualmente."""
    global _current_alias
    if _current_alias:
        ctypes.windll.winmm.mciSendStringW(f"stop {_current_alias}", None, 0, None)
        ctypes.windll.winmm.mciSendStringW(f"close {_current_alias}", None, 0, None)
        _current_alias = None

def limpiar_texto(texto):
    """Elimina símbolos de markdown para que ElevenLabs no los lea literalmente."""
    texto = texto.replace('*', '').replace('#', '').replace('_', '')
    texto = texto.replace('`', '').replace('~', '')
    texto = texto.replace("J.A.V.I.E.R.", "Javier").replace("J.A.V.I.E.R", "Javier")
    texto = texto.replace("EE. UU.", "Estados Unidos").replace("EE.UU.", "Estados Unidos")
    return texto

MAX_CHARS_VOZ = 800  # Límite para no agotar créditos de ElevenLabs

def _fallback_edge_tts(texto, temp_file):
    print("[SISTEMA] ElevenLabs falló. Usando voz de respaldo gratuita (Edge TTS)...")
    try:
        cmd = [r".\venv\Scripts\python.exe", "-m", "edge_tts", "--text", texto, "--write-media", temp_file, "--voice", "es-MX-JorgeNeural"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        path = os.path.abspath(temp_file)
        global _current_alias
        _current_alias = f"javier_{uuid.uuid4().hex[:8]}"
        ctypes.windll.winmm.mciSendStringW(f'open "{path}" type mpegvideo alias {_current_alias}', None, 0, None)
        ctypes.windll.winmm.mciSendStringW(f"play {_current_alias}", None, 0, None)
        
        # Limpiar MP3s viejos
        limpiar_mp3_viejos(temp_file)
    except Exception as e:
        print(f"Error en voz de respaldo: {e}")

def hablar(texto):
    """Convierte texto a voz y lo reproduce asincrónicamente (sin bloquear)."""
    detener_audio()
    print(f"\nJ.A.V.I.E.R.: {texto}")

    texto_para_hablar = limpiar_texto(texto)

    # Si el texto es muy largo, resumir para no gastar créditos de voz
    if len(texto_para_hablar) > MAX_CHARS_VOZ:
        # Contar cuántas oraciones hay y dar un resumen corto
        oraciones = [s.strip() for s in texto_para_hablar.split('.') if s.strip()]
        texto_para_hablar = (
            f"{texto_para_hablar[:MAX_CHARS_VOZ].rsplit(' ', 1)[0]}... "
            f"La respuesta completa está visible en el chat."
        )

    url = "https://api.elevenlabs.io/v1/text-to-speech/cjVigY5qzO86Huf0OWal?optimize_streaming_latency=3"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    data = {
        "text": texto_para_hablar,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    temp_file = f"temp_{uuid.uuid4().hex[:8]}.mp3"

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(temp_file, "wb") as f:
                f.write(response.content)

            path = os.path.abspath(temp_file)
            global _current_alias
            _current_alias = f"javier_{uuid.uuid4().hex[:8]}"
            ctypes.windll.winmm.mciSendStringW(f'open "{path}" type mpegvideo alias {_current_alias}', None, 0, None)
            ctypes.windll.winmm.mciSendStringW(f"play {_current_alias}", None, 0, None)
            
            # Limpiar MP3s viejos (excepto el que acabamos de crear y reproducir)
            limpiar_mp3_viejos(temp_file)
        else:
            print(f"Error HTTP: {response.status_code} - {response.text}")
            _fallback_edge_tts(texto_para_hablar, temp_file)
    except Exception as e:
        print(f"Error reproduciendo audio: {e}")
        _fallback_edge_tts(texto_para_hablar, temp_file)


recognizer = sr.Recognizer()

def escuchar_comando():
    """Escucha el micrófono usando modo Push-To-Talk."""
    global on_estado_cambio, PTT_PRESIONADO

    print("\n[MIC] Esperando a que presiones el botón HABLAR en la interfaz...")
    
    while not PTT_PRESIONADO:
        time.sleep(0.05)

    if on_estado_cambio:
        on_estado_cambio("escuchando")

    print("[MIC] Grabando audio (suelta el botón para enviar)...")
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []

    while PTT_PRESIONADO:
        data = stream.read(1024, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    if on_estado_cambio:
        on_estado_cambio("procesando")

    if len(frames) < 5:
        if on_estado_cambio:
            on_estado_cambio("listo")
        return "none"

    # Convertir los frames de PyAudio a un AudioData de SpeechRecognition
    audio_data = b''.join(frames)
    audio = sr.AudioData(audio_data, 16000, 2)

    try:
        print("[OK] Reconociendo...")
        if USAR_WHISPER:
            temp_wav = f"temp_mic_{uuid.uuid4().hex[:8]}.wav"
            with open(temp_wav, "wb") as f:
                f.write(audio.get_wav_data())
            segments, _ = whisper_model.transcribe(temp_wav, language="es", beam_size=5)
            texto = " ".join([segment.text for segment in segments]).strip()
            try:
                os.remove(temp_wav)
            except:
                pass
            if not texto:
                return "none"
        else:
            texto = recognizer.recognize_google(audio, language='es-MX')
            
        texto_low = texto.lower()
        
        print(f"Tu dijiste: {texto}")
        # Cortar a JAVIER si estaba hablando
        detener_audio()
        return texto_low
        
    except sr.UnknownValueError:
        return "none"
    except sr.RequestError as e:
        print(f"Error de conexion: {e}")
        return "none"
    finally:
        if on_estado_cambio:
            on_estado_cambio("listo")

