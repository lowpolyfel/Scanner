#!/usr/bin/env python3
"""
Punto de entrada de Scanner.
Uso: python3 -m scanner.app.main
"""
from scanner.config.settings import SETTINGS
from scanner.db.mysql import get_connection
print("[BOOT] Scanner iniciado")
print("[CONF] BD:", SETTINGS["BD_HOST"], SETTINGS["BD_PUERTO"], SETTINGS["BD_NOMBRE"])
try:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1+1 AS ok")
        print("[DB] Ping:", cur.fetchone())
    conn.close()
except Exception as e:
    print("[DB] Error de conexión:", e)
