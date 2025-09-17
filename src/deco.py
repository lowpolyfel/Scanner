# -- coding: utf-8 --
"""
deco.py — Hilo de decodificación.
Selecciona el frame con mejor enfoque (Laplaciano), decodifica con pyzbar y,
si hay validador, realiza el toggle (apertura/cierre) contra la BD.
"""
import time
import cv2
from pyzbar.pyzbar import decode
from .util import varianza_laplaciana

class HiloDecodificador:
    def __init__(self, estado, simbolos, tam_ventana, decod_cada_n, validador=None):
        """
        :param estado: EstadoCompartido
        :param simbolos: lista de símbolos pyzbar (ver conf.SIMBOLOS)
        :param tam_ventana: tamaño de ventana de frames para evaluar enfoque
        :param decod_cada_n: periodicidad de muestreo (cada N ticks)
        :param validador: instancia de ValidadorRegistros o None
        """
        self.estado = estado
        self.simbolos = simbolos
        self.tam_ventana = tam_ventana
        self.decod_cada_n = decod_cada_n
        self.validador = validador

    def run(self):
        ticks = 0
        while not self.estado.detener:
            ticks += 1
            if ticks % self.decod_cada_n != 0:
                time.sleep(0.0)
                continue

            candidatos = self.estado.snapshot_ventana()
            if len(candidatos) < self.tam_ventana:
                time.sleep(0.0)
                continue

            mejor_enfoque = -1.0
            mejor_gray = None

            # Elegir el frame con mejor enfoque
            for color in candidatos:
                gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
                enfoque = varianza_laplaciana(gray)
                if enfoque > mejor_enfoque:
                    mejor_enfoque = enfoque
                    mejor_gray = gray

            if mejor_gray is None:
                time.sleep(0.0)
                continue

            # Decodificar
            detecciones = decode(mejor_gray, symbols=self.simbolos)
            if detecciones:
                d = detecciones[0]
                valor = d.data.decode("utf-8", errors="ignore")
                tipo  = d.type
                self.estado.actualizar_meta(valor, tipo, mejor_enfoque)
                print(f"[DETECT] tipo={tipo} valor={valor} enfoque={mejor_enfoque:.1f}")

                # Validación / Toggle con BD (doble escaneo)
                if self.validador:
                    try:
                        mensaje = self.validador.procesar_codigo(valor, tipo)
                        print(mensaje)  # <-- indicador claro en consola
                    except Exception as e:
                        print(f"[ERROR] Validación BD: {e}")

            time.sleep(0.0)  # ceder CPU


