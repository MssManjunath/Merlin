import ctypes
import os
from gtts import gTTS
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

# Suppress ALSA errors
try:
    ctypes.CDLL('libasound.so.2').snd_lib_error_set_handler(None)
except OSError:
    pass

# ElevenLabs client
client = ElevenLabs(api_key="sk_15056b5f1edf0083ce060c232b3e91c3bade20fb9f2990fe")

def speak(text):
    print("🔊 Speaking:", text)

    try:
        # Try ElevenLabs
        audio_stream = client.text_to_speech.convert_as_stream(
            text=text,
            voice_id="Xb7hH8MSUJpSbSDYk0k2",
            model_id="eleven_multilingual_v2"
        )
        stream(audio_stream)
    except Exception as e:
        print("⚠️ ElevenLabs failed, falling back to gTTS:", e)
        try:
            tts = gTTS(text=text, lang='en')
            tts.save("temp.mp3")
            os.system("ffplay -nodisp -autoexit -loglevel quiet temp.mp3")
        except Exception as gtts_error:
            print("❌ gTTS failed too:", gtts_error)




def play_sound(file):
    os.system(f"aplay {file} >/dev/null 2>&1")