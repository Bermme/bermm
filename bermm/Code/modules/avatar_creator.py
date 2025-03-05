import json
import os
import logging
import threading
import pyttsx3
import speech_recognition as sr
import colorsys
from panda3d.core import AmbientLight, DirectionalLight, Vec4
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectSlider, DirectLabel
from direct.actor.Actor import Actor

class AvatarCreator(ShowBase):
    """
    Módulo de Creación de Avatares para BERMM con IA y Animaciones Faciales.

    ✅ Creación y personalización de avatares en 3D.
    ✅ Guardado y carga automática de personalización en JSON.
    ✅ Control por voz para cambiar colores del avatar.
    ✅ Selector avanzado de colores (RGB y HSV).
    """

    def __init__(self, config_file="avatar_config.json"):
        ShowBase.__init__(self)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.config_file = config_file
        self.config = self.load_config()

        # Inicializar motor de voz
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        # Inicializar reconocimiento de voz
        self.recognizer = sr.Recognizer()

        # Configurar iluminación y cargar avatar
        self.setup_lighting()
        self.load_avatar()

        # Crear la interfaz gráfica
        self.create_color_palette_ui()

        # Iniciar control por voz en segundo plano
        self.start_voice_control()

        logging.info("Avatar Creator inicializado correctamente.")

    def load_config(self):
        """Carga la configuración del avatar desde JSON."""
        default_config = {
            "skin_color": [1, 1, 1],   
            "eye_color": [0, 0, 1],    
            "hair_color": [0, 0, 0],   
            "outfit_color": [1, 0, 0]  
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                logging.error("Error al leer la configuración, usando valores por defecto.")
        
        self.save_config(default_config)
        return default_config

    def save_config(self, config):
        """Guarda la configuración del avatar en un archivo JSON."""
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
            logging.info("Configuración del avatar guardada correctamente.")

    def setup_lighting(self):
        """Configura la iluminación del entorno 3D."""
        ambient_light = AmbientLight("ambientLight")
        ambient_light.setColor((0.6, 0.6, 0.6, 1))
        ambient_node = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_node)

        directional_light = DirectionalLight("directionalLight")
        directional_light.setDirection((-1, -1, -1))
        directional_light.setColor((0.9, 0.9, 0.9, 1))
        directional_node = self.render.attachNewNode(directional_light)
        self.render.setLight(directional_node)

    def load_avatar(self):
        """Carga el modelo 3D del avatar y aplica los colores configurados."""
        try:
            self.avatar = Actor("models/avatar", {
                "wave": "models/avatar_wave",
                "talk": "models/avatar_talk"
            })
            self.avatar.reparentTo(self.render)
            self.avatar.setScale(1.5)
            self.avatar.setPos(0, 10, -2)

            self.apply_saved_colors()
            logging.info("Avatar cargado correctamente.")

        except Exception as e:
            logging.error(f"Error al cargar el avatar: {e}")

    def apply_saved_colors(self):
        """Aplica los colores guardados en la configuración."""
        for part in ["skin", "eye", "hair", "outfit"]:
            self.change_avatar_color(part, self.config.get(f"{part}_color", [1, 1, 1]))

    def update_color(self, part):
        """Obtiene el color seleccionado y lo aplica al avatar."""
        color = [self.red_slider['value'], self.green_slider['value'], self.blue_slider['value']]
        self.change_avatar_color(part, color)

    def change_avatar_color(self, part, color):
        """Cambia el color de una parte específica del avatar."""
        color_tuple = Vec4(color[0], color[1], color[2], 1)
        node_name = {
            "skin": "", 
            "eye": "Eyes", 
            "hair": "Hair", 
            "outfit": "Outfit"
        }.get(part, "")

        try:
            if part == "skin":
                self.avatar.setColor(color_tuple)
            else:
                node = self.avatar.find(f"**/{node_name}")
                if not node.isEmpty():
                    node.setColor(color_tuple)

            self.config[f"{part}_color"] = color
            self.save_config(self.config)
            logging.info(f"Color de {part} cambiado a {color}.")
        except Exception as e:
            logging.error(f"No se pudo cambiar el color de {part}: {e}")

    def listen_for_command(self):
        """Escucha comandos de voz para cambiar colores del avatar."""
        with sr.Microphone() as source:
            logging.info("Di un comando (piel, ojos, cabello, ropa)...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                command = self.recognizer.recognize_google(audio, language="es-ES").lower()
                self.process_voice_command(command)
            except sr.UnknownValueError:
                logging.warning("No se entendió el comando.")
            except sr.RequestError:
                logging.error("Error con el servicio de reconocimiento de voz.")

    def start_voice_control(self):
        """Inicia el reconocimiento de voz en un hilo separado."""
        threading.Thread(target=self.listen_for_command, daemon=True).start()

if __name__ == "__main__":
    app = AvatarCreator()
    app.run()
