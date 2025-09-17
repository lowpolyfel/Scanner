# -- coding: utf-8 --
"""
status.py — Contiene el estado compartido entre hilos con sus cerrojos.
"""
import threading
from collections import deque
from typing import Optional
import numpy as np

class EstadoCompartido:
    def __init__(self, tam_ventana: int, escala_preview: float,
                 dibujar_cajas: bool, hud_activo: bool):
        # Último frame para UI
        self._ultimo_frame: Optional[np.ndarray] = None
        self._lock_frame = threading.Lock()

        # Ventana de frames (solo color BGR) para decodificación
        self.ventana_decod = deque(maxlen=tam_ventana)
        self._lock_ventana = threading.Lock()

        # Metadatos de detección
        self._ultimo_valor: str = ""
        self._ultimo_tipo: str = ""
        self._mejor_enfoque: float = 0.0
        self._lock_meta = threading.Lock()

        # Flags y UI
        self.detener = False
        self.escala_preview = escala_preview
        self.dibujar_cajas = dibujar_cajas
        self.hud_activo = hud_activo

    # --- Accesores seguros ---
    def actualizar_frame(self, frame):
        with self._lock_frame:
            self._ultimo_frame = frame

    def leer_frame(self):
        with self._lock_frame:
            return self._ultimo_frame

    def agregar_a_ventana(self, frame):
        with self._lock_ventana:
            self.ventana_decod.append(frame)

    def snapshot_ventana(self):
        with self._lock_ventana:
            return list(self.ventana_decod)

    def actualizar_meta(self, valor: str, tipo: str, enfoque: float):
        with self._lock_meta:
            self._ultimo_valor = valor
            self._ultimo_tipo = tipo
            self._mejor_enfoque = enfoque

    def leer_meta(self):
        with self._lock_meta:
            return self._ultimo_valor, self._ultimo_tipo, self._mejor_enfoque
