# -- coding: utf-8 --
"""
validador.py — Valida códigos contra BD y realiza toggle de sesiones:
Primer escaneo: abre sesión en memoria (NO escribe en BD).
Segundo escaneo (mismo código): cierra sesión y escribe en BD.
Incluye anti-rebote, prueba de conexión y logs claros.
"""
from datetime import datetime, timezone
import threading
import time

from .conf import MODO_REGISTRO, COOLDOWN_MILLIS
from .db import BaseDatos

def ahora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class ValidadorRegistros:
    def __init__(self, estado):
        self.estado = estado
        self.bd = BaseDatos()
        self.lock = threading.Lock()
        self.sesiones_operador = {}   # numero_gafete -> {id_operador, id_maquina, inicio}
        self.sesiones_maquina  = {}   # codigo_maquina -> {id_maquina, inicio}
        self.ultimo_codigo = None
        self.ultimo_ms = 0

    def probar_conexion(self):
        """Proxy para app.py: imprime/retorna estado de la BD."""
        return self.bd.probar_conexion()

    def _debounce(self, codigo: str) -> bool:
        ahora_ms = int(time.time() * 1000)
        if codigo == self.ultimo_codigo and (ahora_ms - self.ultimo_ms) < COOLDOWN_MILLIS:
            return True  # ignorar
        self.ultimo_codigo = codigo
        self.ultimo_ms = ahora_ms
        return False

    def procesar_codigo(self, codigo: str, tipo_simbolo: str) -> str:
        if self._debounce(codigo):
            return "Ignorado (anti-rebote)"
        with self.lock:
            if MODO_REGISTRO == "operador":
                return self._toggle_por_operador(codigo)
            elif MODO_REGISTRO == "maquina":
                return self._toggle_por_maquina(codigo)
            else:
                return f"[ERROR] MODO_REGISTRO inválido: {MODO_REGISTRO}"

    # --------- Modo OPERADOR ---------
    def _toggle_por_operador(self, numero_gafete: str) -> str:
        op = self.bd.buscar_operador_por_gafete(numero_gafete)
        if not op:
            return f"[ERROR] Operador no encontrado: {numero_gafete}"
        if not op["activo"]:
            return f"[ERROR] Operador inactivo: {numero_gafete}"

        id_operador = op["id_operador"]
        id_maquina  = op["id_maquina_asignada"]
        if not id_maquina:
            return f"[ERROR] Operador sin máquina asignada (gafete: {numero_gafete})"

        # Toggle en memoria
        if numero_gafete in self.sesiones_operador:
            info = self.sesiones_operador.pop(numero_gafete)
            inicio = info["inicio"]
            fin = ahora_utc()
            if fin <= inicio:
                fin = inicio.replace(microsecond=(inicio.microsecond + 1) % 1000000)
            try:
                self.bd.insertar_registro_operador(
                    id_operador=id_operador,
                    id_maquina=id_maquina,
                    inicio=inicio,
                    fin=fin,
                    tarea=None
                )
                return (f"[OK] Cierre OPERADOR — gafete={numero_gafete} "
                        f"(operador_id={id_operador}, maquina_id={id_maquina}, "
                        f"inicio={inicio}, fin={fin})")
            except Exception as e:
                # Reponer estado si falla BD
                self.sesiones_operador[numero_gafete] = info
                return f"[ERROR] BD al cerrar registro operador: {e}"
        else:
            self.sesiones_operador[numero_gafete] = {
                "id_operador": id_operador,
                "id_maquina": id_maquina,
                "inicio": ahora_utc(),
            }
            return (f"[OK] Apertura OPERADOR — gafete={numero_gafete} "
                    f"(operador_id={id_operador}, maquina_id={id_maquina})")

    # --------- Modo MÁQUINA ---------
    def _toggle_por_maquina(self, codigo_maquina: str) -> str:
        mq = self.bd.buscar_maquina_por_codigo(codigo_maquina)
        if not mq:
            return f"[ERROR] Máquina no encontrada: {codigo_maquina}"
        if not mq["activo"]:
            return f"[ERROR] Máquina inactiva: {codigo_maquina}"

        id_maquina = mq["id_maquina"]
        if codigo_maquina in self.sesiones_maquina:
            info = self.sesiones_maquina.pop(codigo_maquina)
            inicio = info["inicio"]
            fin = ahora_utc()
            if fin <= inicio:
                fin = inicio.replace(microsecond=(inicio.microsecond + 1) % 1000000)
            try:
                self.bd.insertar_registro_maquina(
                    id_maquina=id_maquina,
                    inicio=inicio,
                    fin=fin,
                    observaciones=None
                )
                return (f"[OK] Cierre MÁQUINA — codigo={codigo_maquina} "
                        f"(maquina_id={id_maquina}, inicio={inicio}, fin={fin})")
            except Exception as e:
                self.sesiones_maquina[codigo_maquina] = info
                return f"[ERROR] BD al cerrar registro máquina: {e}"
        else:
            self.sesiones_maquina[codigo_maquina] = {
                "id_maquina": id_maquina,
                "inicio": ahora_utc(),
            }
            return (f"[OK] Apertura MÁQUINA — codigo={codigo_maquina} "
                    f"(maquina_id={id_maquina})")
