# -- coding: utf-8 --
"""
db.py — Acceso a MySQL/MariaDB usando PyMySQL (paquete APT: python3-pymysql).
No requiere pip. Mantiene la misma interfaz que la versión con mysql-connector.
"""
from typing import Optional, Dict, Any
import pymysql
from pymysql.cursors import DictCursor
from .conf import (BD_HOST, BD_PUERTO, BD_USUARIO, BD_CONTRASENA, BD_NOMBRE)

class BaseDatos:
    def __init__(self):
        # Conexión por operación (simple y robusto en Raspberry). autocommit=True
        self._conn_args = dict(
            host=BD_HOST,
            port=int(BD_PUERTO),
            user=BD_USUARIO,
            password=BD_CONTRASENA,
            database=BD_NOMBRE,
            charset="utf8mb4",
            autocommit=True,
            cursorclass=DictCursor,
        )

    def _conn(self):
        return pymysql.connect(**self._conn_args)

    # ------- Consultas de validación -------
    def buscar_operador_por_gafete(self, numero_gafete: str) -> Optional[Dict[str, Any]]:
        sql = """SELECT id_operador, nombre, apellido, id_maquina_asignada, activo
                 FROM operadores WHERE numero_gafete=%s"""
        with self._conn() as cn, cn.cursor() as cur:
            cur.execute(sql, (numero_gafete,))
            return cur.fetchone()

    def buscar_maquina_por_codigo(self, codigo_maquina: str) -> Optional[Dict[str, Any]]:
        sql = """SELECT id_maquina, codigo_maquina, nombre, activo
                 FROM maquinas WHERE codigo_maquina=%s"""
        with self._conn() as cn, cn.cursor() as cur:
            cur.execute(sql, (codigo_maquina,))
            return cur.fetchone()

    # ------- Inserts cuando se cierra sesión -------
    def insertar_registro_operador(self, id_operador: int, id_maquina: int, inicio, fin, tarea=None) -> None:
        sql = """INSERT INTO registros_operador (id_operador, id_maquina, inicio_operacion, fin_operacion, tarea)
                 VALUES (%s, %s, %s, %s, %s)"""
        with self._conn() as cn, cn.cursor() as cur:
            cur.execute(sql, (id_operador, id_maquina, inicio, fin, tarea))

    def insertar_registro_maquina(self, id_maquina: int, inicio, fin, observaciones=None) -> None:
        sql = """INSERT INTO registros_maquina (id_maquina, inicio_operacion, fin_operacion, observaciones)
                 VALUES (%s, %s, %s, %s)"""
        with self._conn() as cn, cn.cursor() as cur:
            cur.execute(sql, (id_maquina, inicio, fin, observaciones))
