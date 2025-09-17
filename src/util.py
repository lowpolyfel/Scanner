# -- coding: utf-8 --
"""
util.py — Funciones utilitarias (Laplaciano, HUD, cajas, propiedades de cámara).
"""
import cv2

def establecer_propiedades_camara(captura, ancho, alto, fps, fourcc_texto="MJPG"):
    captura.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
    captura.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)
    try:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_texto)
        captura.set(cv2.CAP_PROP_FOURCC, fourcc)
    except Exception:
        pass
    captura.set(cv2.CAP_PROP_FPS, fps)
    # latencia baja si está soportado
    try:
        captura.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass

def varianza_laplaciana(gray):
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def dibujar_cajas(frame, detecciones):
    """
    Dibuja rectángulos sobre el frame con base en rect de pyzbar.
    Usa r.left, r.top, r.width, r.height (propiedades estándar).
    """
    if not detecciones:
        return
    for det in detecciones:
        r = det.rect
        x, y, w, h = int(r.left), int(r.top), int(r.width), int(r.height)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        etiqueta = det.type
        (tw, th), base = cv2.getTextSize(etiqueta, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        y_texto = max(0, y-10)
        cv2.rectangle(frame, (x, y_texto-th-base), (x+tw, y_texto), (0,255,0), cv2.FILLED)
        cv2.putText(frame, etiqueta, (x, y_texto-4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

def hud(frame, texto_principal: str, subtexto: str = None, activo: bool = True):
    if not activo:
        return
    h, w = frame.shape[:2]
    alto_banner = max(60, int(0.08*h))
    cv2.rectangle(frame, (0,0), (w,alto_banner), (0,0,0), -1)
    principal = texto_principal if texto_principal else "Esperando lectura..."
    (tw, th), _ = cv2.getTextSize(principal, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
    cv2.putText(frame, principal, (10, min(alto_banner-14, 10+th+10)),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
    if subtexto:
        cv2.putText(frame, subtexto, (10, alto_banner-12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)
