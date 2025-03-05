import speech_recognition as sr
import pyttsx3
import logging

class VoiceAssistant:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        logging.info("Asistente de voz inicializado.")

    def listen(self):
        """Escucha la entrada de voz y la convierte en texto."""
        with sr.Microphone() as source:
            logging.info("Escuchando...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language="es-ES")
                logging.info(f"Texto reconocido: {text}")
                return text.lower()
            except sr.UnknownValueError:
                logging.warning("No se pudo entender el audio.")
                return None
            except sr.RequestError:
                logging.error("Error con el servicio de reconocimiento de voz.")
                return None

    def speak(self, text):
        """Convierte texto a voz y lo reproduce."""
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    while True:
        command = assistant.listen()
        if command:
            if "salir" in command:
                assistant.speak("Cerrando asistente de voz.")
                break
            assistant.speak(f"Dijiste: {command}")
