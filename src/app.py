# -- coding: utf-8 --
"""
app.py — Punto de entrada. Crea el estado y lanza los hilos de captura,
decodificación y render. Integra el validador (BD) y verifica conexión al inicio.
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

# Intentar cargar validador (PyMySQL). Si falta, continuar sin BD.
_VALIDADOR_DISPONIBLE = True
_VALIDADOR_ERROR = None
try:
    from .validador import ValidadorRegistros
except Exception as _e:
    ValidadorRegistros = None  # type: ignore
    _VALIDADOR_DISPONIBLE = False
    _VALIDADOR_ERROR = _e


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

    # Instancia del validador (si disponible) + prueba de conexión
    validador = None
    if _VALIDADOR_DISPONIBLE and ValidadorRegistros is not None:
        try:
            validador = ValidadorRegistros(estado)
            print("[OK] Validador BD cargado (PyMySQL). Probando conexión...")
            ok, detalle = validador.probar_conexion()
            if ok:
                print(f"[OK] Conexión a BD exitosa: {detalle}")
            else:
                print(f"[WARN] Falló la conexión a BD: {detalle}")
                print("      El escáner seguirá funcionando SIN validación contra BD.")
                validador = None
        except Exception as e:
            print(f"[WARN] No se pudo inicializar el validador BD: {type(e).__name__}: {e}")
            print("      Sugerencia: verifica que esté instalado 'python3-pymysql' y tus credenciales.")
            validador = None
    else:
        if _VALIDADOR_ERROR:
            print("[WARN] Validador BD deshabilitado (error de importación).")
            print(f"      Detalle: {type(_VALIDADOR_ERROR).__name__}: {_VALIDADOR_ERROR}")
            print("      Instala PyMySQL con: sudo apt install -y python3-pymysql")
            print("      Luego ejecuta: python3 -m src.app")

    captura = HiloCaptura(estado, INDICE_CAMARA, ANCHO, ALTO, FPS_OBJETIVO, FOURCC)
    decod   = HiloDecodificador(estado, SIMBOLOS, VENTANA_TAMANIO, DECODIFICAR_CADA_N, validador=validador)
    render  = HiloRender(estado)

    t1 = threading.Thread(target=captura.run, daemon=True)
    t2 = threading.Thread(target=decod.run,   daemon=True)
    t3 = threading.Thread(target=render.run,  daemon=True)

    t1.start(); t2.start(); t3.start()

    try:
        while not estado.detener:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("[INFO] Interrupción por teclado")
        estado.detener = True

    for t in (t1, t2, t3):
        t.join(timeout=1.0)


if __name__ == "__main__":
    main()
