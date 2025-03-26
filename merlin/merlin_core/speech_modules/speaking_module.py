import pyttsx3

tts = pyttsx3.init()

def speak(text):
    voices = tts.getProperty('voices')
    tts.setProperty('voice',voices[0].id)
    print("🔊 Speaking:", text)
    tts.say(text)
    tts.runAndWait()
