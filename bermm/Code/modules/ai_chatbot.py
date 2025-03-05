import openai
import logging
import sqlite3
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pyttsx3
from datetime import datetime

# Descargar recursos de análisis de emociones si no están disponibles
nltk.download('vader_lexicon')

# Configurar clave de OpenAI (Reemplázala con tu clave)
openai.api_key = "TU_CLAVE_OPENAI"

class AIChatbot:
    def __init__(self, language="es", personality="amigable"):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("AI Chatbot inicializado.")
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        self.conn = sqlite3.connect("chat_memory.db")
        self.cursor = self.conn.cursor()
        self.create_memory_table()

        self.predefined_responses = {
            "hola": ["Hola, ¿cómo estás?", "¡Hola! ¿En qué puedo ayudarte?"],
            "adiós": ["Adiós, que tengas un buen día.", "Hasta luego, vuelve pronto."],
            "cómo estás": ["Estoy funcionando correctamente. Gracias por preguntar."],
            "qué puedes hacer": ["Puedo responder preguntas, abrir aplicaciones, buscar información y más."],
            "qué hora es": [f"La hora actual es {datetime.now().strftime('%H:%M')}."]
        }
        
        self.language = language
        self.personality = personality

    def create_memory_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT UNIQUE,
                bot_response TEXT
            )
        """)
        self.conn.commit()

    def save_to_memory(self, user_input, bot_response):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO memory (user_input, bot_response) VALUES (?, ?)",
                                (user_input, bot_response))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error al guardar en memoria: {e}")

    def get_from_memory(self, user_input):
        self.cursor.execute("SELECT bot_response FROM memory WHERE user_input = ?", (user_input,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def analyze_sentiment(self, message):
        sentiment_score = self.sentiment_analyzer.polarity_scores(message)["compound"]
        if sentiment_score >= 0.5:
            return "positivo"
        elif sentiment_score <= -0.5:
            return "negativo"
        return "neutral"

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def get_response(self, message):
        message = message.lower()

        memory_response = self.get_from_memory(message)
        if memory_response:
            logging.info("Respuesta obtenida de la memoria.")
            return memory_response

        if message in self.predefined_responses:
            logging.info("Respuesta predefinida utilizada.")
            return self.predefined_responses[message][0]

        ai_response = self.get_ai_response(message)

        self.save_to_memory(message, ai_response)
        return ai_response

    def get_ai_response(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"Error en IA: {e}")
            return "Lo siento, hubo un error con el servicio de inteligencia artificial."

if __name__ == "__main__":
    chatbot = AIChatbot()
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "adiós"]:
            print("AI: Hasta luego.")
            chatbot.speak("Hasta luego.")
            break

        sentiment = chatbot.analyze_sentiment(user_input)
        if sentiment == "positivo":
            chatbot.speak("Me alegra escuchar eso.")
        elif sentiment == "negativo":
            chatbot.speak("Lamento que te sientas así. ¿En qué puedo ayudarte?")

        response = chatbot.get_response(user_input)
        print(f"AI: {response}")
        chatbot.speak(response)
