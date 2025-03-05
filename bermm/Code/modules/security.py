import logging

class Security:
    def __init__(self):
        logging.info("Módulo de Seguridad inicializado.")
    
    def authenticate_user(self, user_id):
        logging.info(f"Autenticando usuario: {user_id}")
        return f"Usuario {user_id} autenticado correctamente."
