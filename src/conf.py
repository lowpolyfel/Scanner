# -- coding: utf-8 --
"""
conf.py — Parámetros de configuración y constantes del sistema.
"""
from pyzbar.pyzbar import ZBarSymbol

# --- Cámara ---
INDICE_CAMARA = 0
ANCHO = 1920
ALTO = 1080
FPS_OBJETIVO = 60
FOURCC = "MJPG"           # Suele permitir 1080p60 en webcams USB

# --- Previsualización/UI ---
ESCALA_PREVIEW_INICIAL = 0.5      # 0.3–1.0 (teclas 1–4)
DECODIFICAR_CADA_N = 3            # cada N ciclos del hilo decodificador
VENTANA_TAMANIO = 5               # evaluamos N frames por lote (best focus)

DIBUJAR_CAJAS_INICIAL = False     # tecla 'd'
HUD_ACTIVO_INICIAL = True         # tecla 'h'

# Símbolos a detectar (puedes ajustar)
SIMBOLOS = [
    ZBarSymbol.EAN13, ZBarSymbol.EAN8, ZBarSymbol.UPCA, ZBarSymbol.UPCE,
    ZBarSymbol.CODE39, ZBarSymbol.CODE93, ZBarSymbol.CODE128,
    ZBarSymbol.I25, ZBarSymbol.DATABAR, ZBarSymbol.DATABAR_EXP,
    ZBarSymbol.CODABAR, ZBarSymbol.PDF417, ZBarSymbol.QRCODE

]

# --- Base de Datos (ajusta credenciales locales) ---
BD_HOST = "localhost"
BD_PUERTO = 3306
BD_USUARIO = "fel"
BD_CONTRASENA = "feli123"
BD_NOMBRE = "bd_test"

# --- Modo de registro ---
#   "operador" => toggle en registros_operador por numero_gafete (usa id_maquina_asignada)
#   "maquina"  => toggle en registros_maquina por codigo_maquina
MODO_REGISTRO = "operador"

# Anti-rebote (evitar múltiples activaciones por el mismo código en frames consecutivos)
COOLDOWN_MILLIS = 1500
