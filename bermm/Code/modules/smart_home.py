import logging

class SmartHome:
    def __init__(self):
        logging.info("Módulo de Casa Inteligente inicializado.")
    
    def control_device(self, device_name, action):
        logging.info(f"Ejecutando {action} en {device_name}.")
        return f"{device_name} ha sido {action}."
