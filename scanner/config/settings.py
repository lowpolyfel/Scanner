import os
try:
    from .conf_privado import *  # opcional; define BD_HOST, etc.
except Exception:
    pass

SETTINGS = {
    "BD_HOST": os.getenv("BD_HOST", globals().get("BD_HOST", "127.0.0.1")),
    "BD_PUERTO": int(os.getenv("BD_PUERTO", globals().get("BD_PUERTO", 3306))),
    "BD_USUARIO": os.getenv("BD_USUARIO", globals().get("BD_USUARIO", "fel")),
    "BD_CONTRASENA": os.getenv("BD_CONTRASENA", globals().get("BD_CONTRASENA", "feli123")),
    "BD_NOMBRE": os.getenv("BD_NOMBRE", globals().get("BD_NOMBRE", "bd_test")),
    "COOLDOWN_MILLIS": int(os.getenv("COOLDOWN_MILLIS", globals().get("COOLDOWN_MILLIS", 500))),
    "MODO_REGISTRO": os.getenv("MODO_REGISTRO", globals().get("MODO_REGISTRO", "operador")),
}
