# -- coding: utf-8 --
"""
cam.py — Hilo de captura de cámara (grab/retrieve para reducir latencia).
"""
import time
import cv2
from .util import establecer_propiedades_camara

class HiloCaptura:
    def __init__(self, estado, indice_camara, ancho, alto, fps, fourcc):
        self.estado = estado
        self.indice = indice_camara
        self.ancho = ancho
        self.alto = alto
        self.fps = fps
        self.fourcc = fourcc

    def run(self):
        print("[INFO] abriendo cámara...")
        cap = cv2.VideoCapture(self.indice, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.indice, cv2.CAP_ANY)
            if not cap.isOpened():
                print("[ERROR] no se pudo abrir la cámara")
                self.estado.detener = True
                return

        print("[OK] cámara abierta")
        establecer_propiedades_camara(cap, self.ancho, self.alto, self.fps, self.fourcc)

        leimos_alguno = False
        while not self.estado.detener:
            if not cap.grab():
                time.sleep(0.001)
                continue
            ok, frame = cap.retrieve()
            if not ok or frame is None:
                continue
            if not leimos_alguno:
                print("[OK] recibiendo frames")
                leimos_alguno = True

            # UI
            self.estado.actualizar_frame(frame)
            # Ventana de decodificación (BGR)
            self.estado.agregar_a_ventana(frame)

        cap.release()
        print("[OK] cámara liberada")
