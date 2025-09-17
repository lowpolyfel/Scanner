# -- coding: utf-8 --
"""
deco.py — Hilo de decodificación (elige el frame con mejor enfoque).
"""
import time
import cv2
from pyzbar.pyzbar import decode
from .util import varianza_laplaciana

class HiloDecodificador:
    def __init__(self, estado, simbolos, tam_ventana, decod_cada_n):
        self.estado = estado
        self.simbolos = simbolos
        self.tam_ventana = tam_ventana
        self.decod_cada_n = decod_cada_n

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

            mejor_idx = -1
            mejor_enfoque = -1.0
            mejor_gray = None
            mejor_color = None

            for i, color in enumerate(candidatos):
                gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
                enfoque = varianza_laplaciana(gray)
                if enfoque > mejor_enfoque:
                    mejor_enfoque = enfoque
                    mejor_gray = gray
                    mejor_color = color
                    mejor_idx = i

            if mejor_gray is None:
                time.sleep(0.0)
                continue

            detecciones = decode(mejor_gray, symbols=self.simbolos)
            if detecciones:
                d = detecciones[0]
                valor = d.data.decode("utf-8", errors="ignore")
                tipo = d.type
                self.estado.actualizar_meta(valor, tipo, mejor_enfoque)
                print(f"[DETECT] tipo={tipo} valor={valor} enfoque={mejor_enfoque:.1f}")

            time.sleep(0.0)  # ceder CPU
