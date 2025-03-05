import speech_recognition as sr
import pyttsx3
import logging
import pyautogui
import os
import platform
import json

try:
    import tolk  # Biblioteca para compatibilidad con lectores de pantalla (NVDA, JAWS, etc.)
except ImportError:
    tolk = None

try:
    import accessible_output2.outputs.auto  # Para mayor compatibilidad con sistemas de accesibilidad
    output = accessible_output2.outputs.auto.Auto()
except ImportError:
    output = None


class Accessibility:
    """
    Módulo de Accesibilidad de BERMM.

    Funcionalidades:
    - Conversión de texto a voz con soporte para múltiples motores (pyttsx3, NVDA, Tolk, JAWS).
    - Reconocimiento de voz optimizado con ajuste de ruido ambiental.
    - Compatibilidad con lectores de pantalla y OCR.
    - Configuración personalizada mediante archivo JSON.
    - Control de funciones de accesibilidad por comandos de voz.
    - Soporte para alto contraste y mejor visibilidad en pantallas.
    """

    def __init__(self, config_file="accessibility_config.json"):
        """
        Inicializa el módulo con opciones personalizadas desde un archivo JSON.

        :param config_file: Ruta al archivo de configuración.
        """
        self.setup_logging()
        self.engine = self.init_text_to_speech_engine()
        self.recognizer = sr.Recognizer()
        self.nvda_installed = self.is_nvda_installed()
        self.config = self.load_config(config_file)
        self.initialize_screen_reader_support()

    def setup_logging(self):
        """
        Configura el sistema de logging para el módulo.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def init_text_to_speech_engine(self):
        """
        Inicializa el motor de texto a voz.

        :return: Instancia del motor pyttsx3.
        """
        try:
            engine = pyttsx3.init()
            return engine
        except Exception as e:
            logging.error(f"Error al inicializar el motor de texto a voz: {e}")
            return None

    def load_config(self, config_file):
        """
        Carga la configuración de accesibilidad desde un archivo JSON.
        Si el archivo no existe, se crea con valores predeterminados.

        :param config_file: Ruta al archivo JSON de configuración.
        :return: Diccionario con la configuración cargada.
        """
        default_config = {
            "language": "es-ES",
            "voice_speed": 150,
            "high_contrast": False,
            "enable_screen_reader": True
        }
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as file:
                    config = json.load(file)
                    logging.info("Configuración cargada correctamente.")
                    return config
            except json.JSONDecodeError as e:
                logging.error(f"Error al decodificar el archivo de configuración: {e}")
        else:
            self.save_config(default_config, config_file)
        return default_config

    def save_config(self, config, config_file):
        """
        Guarda la configuración en un archivo JSON.

        :param config: Diccionario de configuración.
        :param config_file: Ruta al archivo JSON de configuración.
        """
        try:
            with open(config_file, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=4)
                logging.info("Configuración guardada correctamente.")
        except IOError as e:
            logging.error(f"Error al guardar el archivo de configuración: {e}")

    def initialize_screen_reader_support(self):
        """
        Inicializa el soporte para lectores de pantalla si las bibliotecas están disponibles.
        """
        if tolk:
            try:
                tolk.load()
                logging.info("Tolk cargado correctamente.")
            except Exception as e:
                logging.error(f"Error al cargar Tolk: {e}")
        if output:
            logging.info("Salida de accesibilidad inicializada correctamente.")

    def text_to_speech(self, text):
        """
        Convierte texto en voz y lo reproduce con el motor más accesible disponible.

        Prioridad:
        1. NVDA si está instalado en Windows.
        2. Tolk (compatibilidad con JAWS y lectores de pantalla).
        3. accessible_output2 (soporte adicional).
        4. pyttsx3 (motor TTS interno de Python).

        :param text: Texto que se debe leer en voz alta.
        """
        if not text:
            logging.warning("No se proporcionó texto para convertir a voz.")
            return
        try:
            if self.nvda_installed:
                os.system(f'nvdaControllerClient speak "{text}"')
            elif tolk and tolk.is_loaded():
                tolk.speak(text)
            elif output:
                output.speak(text)
            elif self.engine:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                logging.error("No hay motor de texto a voz disponible.")
            logging.info(f"Texto hablado: {text}")
        except Exception as e:
            logging.error(f"Error al convertir texto a voz: {e}")

    def speech_to_text(self):
        """
        Convierte voz en texto utilizando reconocimiento de voz con ajuste de ruido.

        :return: Texto reconocido o mensaje de error.
        """
        with sr.Microphone() as source:
            logging.info("Escuchando...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language=self.config.get("language", "es-ES"))
                logging.info(f"Texto reconocido: {text}")
                return text.lower()
            except sr.UnknownValueError:
                logging.warning("No se pudo entender el audio.")
                return "No entendí lo que dijiste."
            except sr.RequestError as e:
                logging.error(f"Error en el servicio de reconocimiento de voz: {e}")
                return "Error en el reconocimiento de voz."

    def read_screen_text(self):
        """
        Captura el texto visible en la pantalla y lo lee en voz alta.


::contentReference[oaicite:8]{index=8}
 
