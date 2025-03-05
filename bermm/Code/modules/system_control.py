import os
import platform
import subprocess
import logging

class SystemControl:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Módulo de Control del Sistema inicializado.")

    def execute_command(self, command):
        """Ejecuta comandos del sistema basados en la entrada del usuario."""
        command = command.lower()
        
        if "abrir navegador" in command:
            self.open_browser()
        elif "abrir bloc de notas" in command:
            self.open_notepad()
        elif "apagar computadora" in command:
            self.shutdown()
        elif "reiniciar computadora" in command:
            self.restart()
        else:
            logging.warning("Comando no reconocido: %s", command)

    def open_browser(self):
        """Abre el navegador predeterminado."""
        try:
            if platform.system() == "Windows":
                os.system("start chrome" if self.is_program_installed("chrome") else "start msedge")
            elif platform.system() == "Linux":
                os.system("xdg-open https://www.google.com")
            elif platform.system() == "Darwin":
                os.system("open -a Safari")
            logging.info("Navegador abierto.")
        except Exception as e:
            logging.error("Error al abrir el navegador: %s", e)

    def open_notepad(self):
        """Abre el Bloc de Notas en Windows."""
        try:
            if platform.system() == "Windows":
                os.system("notepad")
            else:
                logging.warning("El Bloc de Notas solo está disponible en Windows.")
        except Exception as e:
            logging.error("Error al abrir el Bloc de Notas: %s", e)

    def shutdown(self):
        """Apaga la computadora."""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 0")
            elif platform.system() == "Linux" or platform.system() == "Darwin":
                os.system("shutdown now")
            logging.info("Orden de apagado enviada.")
        except Exception as e:
            logging.error("Error al apagar la computadora: %s", e)

    def restart(self):
        """Reinicia la computadora."""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /t 0")
            elif platform.system() == "Linux" or platform.system() == "Darwin":
                os.system("reboot")
            logging.info("Orden de reinicio enviada.")
        except Exception as e:
            logging.error("Error al reiniciar la computadora: %s", e)

    def is_program_installed(self, program):
        """Verifica si un programa está instalado en Windows."""
        try:
            output = subprocess.check_output(f"where {program}", shell=True, stderr=subprocess.DEVNULL)
            return bool(output.strip())
        except subprocess.CalledProcessError:
            return False

if __name__ == "__main__":
    system_control = SystemControl()
    while True:
        user_command = input("Introduce un comando del sistema (o 'salir' para terminar): ")
        if user_command.lower() == "salir":
            break
        system_control.execute_command(user_command)
