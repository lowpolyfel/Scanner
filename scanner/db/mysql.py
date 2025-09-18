import pymysql
from scanner.config.settings import SETTINGS

def get_connection():
    return pymysql.connect(
        host=SETTINGS["BD_HOST"],
        port=SETTINGS["BD_PUERTO"],
        user=SETTINGS["BD_USUARIO"],
        password=SETTINGS["BD_CONTRASENA"],
        database=SETTINGS["BD_NOMBRE"],
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
