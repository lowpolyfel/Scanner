# -- coding: utf-8 --
"""
rend.py — Hilo de renderizado (ventana, FPS, HUD y teclado).
"""
import time
from collections import deque
import cv2
from .util import hud, dibujar_cajas

class HiloRender:
    def __init__(self, estado, titulo_ventana="Barcode Scanner (Realtime UI)"):
        self.estado = estado
        self.titulo = titulo_ventana

    def run(self):
        fps_ventana = deque(maxlen=30)
        t_prev = time.perf_counter()

        while not self.estado.detener:
            frame = self.estado.leer_frame()
            if frame is None:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.estado.detener = True
                continue

            # FPS
            ahora = time.perf_counter()
            dt = ahora - t_prev
            t_prev = ahora
            if dt > 0:
                fps_ventana.append(1.0 / dt)
            fps_real = (sum(fps_ventana) / len(fps_ventana)) if fps_ventana else 0.0

            # Escala de preview
            vis = frame
            escala = self.estado.escala_preview
            if escala != 1.0:
                vis = cv2.resize(frame, (0, 0), fx=escala, fy=escala, interpolation=cv2.INTER_LINEAR)

            detecciones = self.estado.leer_detecciones()
            dibujar_cajas(vis, detecciones, escala=escala)

            mensaje_validacion, indicador_activo = self.estado.leer_validacion()
            if indicador_activo:
                self._dibujar_indicador_aceptado(vis, mensaje_validacion)

            # HUD
            valor, tipo, mejor_enfoque = self.estado.leer_meta()
            texto = f"{tipo}: {valor}" if valor else ""
            sub = f"Cap {frame.shape[1]}x{frame.shape[0]} | Preview x{escala:.2f} | FPS {fps_real:0.1f} | BestFocus {mejor_enfoque:0.1f}"
            hud(vis, texto, sub, activo=self.estado.hud_activo)

            # Mostrar
            cv2.imshow(self.titulo, vis)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("[INFO] salida solicitada")
                self.estado.detener = True
            elif key == ord('d'):
                print("[INFO] El resaltado de cajas está siempre activo.")
            elif key == ord('h'):
                self.estado.hud_activo = not self.estado.hud_activo
                print(f"[INFO] HUD {'on' if self.estado.hud_activo else 'off'}")
            elif key == ord('1'):
                self.estado.escala_preview = 0.3; print("[INFO] escala 0.30")
            elif key == ord('2'):
                self.estado.escala_preview = 0.5; print("[INFO] escala 0.50")
            elif key == ord('3'):
                self.estado.escala_preview = 0.75; print("[INFO] escala 0.75")
            elif key == ord('4'):
                self.estado.escala_preview = 1.0; print("[INFO] escala 1.00")

        cv2.destroyAllWindows()
        print("[OK] ventana cerrada")

    def _dibujar_indicador_aceptado(self, frame, mensaje: str):
        h, w = frame.shape[:2]
        alto = max(60, int(0.12 * h))
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - alto), (w, h), (0, 180, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        texto_ok = "CÓDIGO ACEPTADO"
        cv2.putText(frame, texto_ok, (10, h - alto + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        if mensaje:
            cv2.putText(frame, mensaje, (10, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)
