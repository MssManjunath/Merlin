import speech_recognition as sr
from .speaking_module import play_sound

def listen_from_microphone(timeout=5, phrase_time_limit=10, language="en-US"):
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Calibrating for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected (timeout).")
            return "No speech detected"

    # Try recognizing the speech
    print("🧠 Processing...")
    try:
        transcript = recognizer.recognize_google(audio, language=language)
        print("✅ You said:", transcript)
        return transcript
    
    except sr.UnknownValueError:
        print("🤷 Sorry, I didn't catch that.")
        return "Sorry, I didn't catch that."
    
    except sr.RequestError:
        print("❌ Speech recognition service is unavailable.")
        return "Speech recognition service is unavailable."


def listen_passive():
    return listen_from_microphone(timeout=3, phrase_time_limit=4)

def listen_active():
    play_sound("start_beep.wav")
    transcript = listen_from_microphone(timeout=6, phrase_time_limit=10)
    play_sound("end_chime.wav")
    return transcript
