import speech_recognition as sr

def listen_from_microphone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        print("🧠 Processing...")
        try:
            res = recognizer.recognize_google(audio)
            print(res)
            return res
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
            return "Speech recognition service is unavailable."
