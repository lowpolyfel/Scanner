# -- coding: utf-8 --
"""
app.py — Punto de entrada. Crea el estado y lanza los hilos de captura, decodificación y render.
"""
import time
import threading
import cv2

from .conf import (
    INDICE_CAMARA, ANCHO, ALTO, FPS_OBJETIVO, FOURCC,
    ESCALA_PREVIEW_INICIAL, DECODIFICAR_CADA_N, VENTANA_TAMANIO,
    DIBUJAR_CAJAS_INICIAL, HUD_ACTIVO_INICIAL, SIMBOLOS
)
from .status import EstadoCompartido
from .cam import HiloCaptura
from .deco import HiloDecodificador
from .rend import HiloRender

def main():
    try:
        cv2.setUseOptimized(True)
        cv2.setNumThreads(1)  # Evita contención en CPUs modestas (Raspberry Pi)
    except Exception:
        pass

    estado = EstadoCompartido(
        tam_ventana=VENTANA_TAMANIO,
        escala_preview=ESCALA_PREVIEW_INICIAL,
        dibujar_cajas=DIBUJAR_CAJAS_INICIAL,
        hud_activo=HUD_ACTIVO_INICIAL
    )

    captura = HiloCaptura(estado, INDICE_CAMARA, ANCHO, ALTO, FPS_OBJETIVO, FOURCC)
    decod   = HiloDecodificador(estado, SIMBOLOS, VENTANA_TAMANIO, DECODIFICAR_CADA_N)
    render  = HiloRender(estado)

    t1 = threading.Thread(target=captura.run, daemon=True)
    t2 = threading.Thread(target=decod.run,   daemon=True)
    t3 = threading.Thread(target=render.run,  daemon=True)

    t1.start(); t2.start(); t3.start()

    try:
        while not estado.detener:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("[INFO] interrupción por teclado")
        estado.detener = True

    for t in (t1, t2, t3):
        t.join(timeout=1.0)

if __name__ == "__main__":
    main()
