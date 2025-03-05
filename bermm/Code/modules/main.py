import logging
import os
from ai_chatbot import AIChatbot
from vision import VisionModule
from avatar import AvatarModule
from voice import VoiceAssistant
from system_control import SystemControl

# Configuración del logging para depuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Bermm:
    def __init__(self):
        logging.info("Iniciando BERMM...")
        
        # Inicializar módulos
        self.chatbot = AIChatbot()
        self.vision = VisionModule(camera_index=0, mode="detection", display_window=False)
        self.avatar = AvatarModule(camera_enabled=False)
        self.voice = VoiceAssistant()
        self.system_control = SystemControl()

        logging.info("Todos los módulos de BERMM han sido cargados.")

    def start(self):
        """Método para iniciar el sistema y habilitar las interacciones."""
        logging.info("BERMM está ahora en funcionamiento.")
        while True:
            user_input = input("Tú: ")
            if user_input.lower() in ["salir", "adiós"]:
                logging.info("Cerrando BERMM...")
                break

            # Pasar el mensaje al chatbot
            response = self.chatbot.get_response(user_input)
            print(f"BERMM: {response}")

            # Activar el avatar si está habilitado
            self.avatar.speak(response)

            # Manejo de comandos del sistema
            self.system_control.execute_command(user_input)

if __name__ == "__main__":
    bermm = Bermm()
    bermm.start()
