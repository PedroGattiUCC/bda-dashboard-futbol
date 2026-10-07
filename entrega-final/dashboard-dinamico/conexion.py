"""Gestor de conexiones resiliente a bases de datos:
- Clever Cloud MySQL (Remoto en la nube)
- MySQL Local (Desarrollo local)
- SQLite Contingencia (Respaldo offline 100% autónomo para la exposición)
"""

import os
import time
import math
import sqlite3
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

DIR_ACTUAL = Path(__file__).resolve().parent
RUTA_SQLITE_DEFAULT = DIR_ACTUAL / "dw_contingencia.sqlite"


class StddevSamp:
    """Implementación de STDDEV_SAMP para emulación completa en SQLite."""
    def __init__(self):
        self.values = []

    def step(self, value):
        if value is not None:
            try:
                self.values.append(float(value))
            except (ValueError, TypeError):
                pass

    def finalize(self):
        n = len(self.values)
        if n < 2:
            return None
        mean = sum(self.values) / n
        variance = sum((x - mean) ** 2 for x in self.values) / (n - 1)
        return round(math.sqrt(variance), 4)


def obtener_config_por_defecto():
    """Lee las credenciales configuradas en el entorno (Render o máquina local)."""
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", 3306)),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "dw_competencia_futbol"),
    }


def crear_engine_mysql(config):
    """Crea un engine de SQLAlchemy optimizado para MySQL / Clever Cloud."""
    user = config.get("user", "root")
    password = config.get("password", "")
    host = config.get("host", "localhost")
    port = config.get("port", 3306)
    database = config.get("database", "dw_competencia_futbol")

    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    return create_engine(
        url,
        pool_recycle=300,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10}
    )


def preparar_conexion_sqlite(ruta_sqlite=None):
    """Abre conexión SQLite registrando funciones de compatibilidad con MySQL."""
    ruta = ruta_sqlite or RUTA_SQLITE_DEFAULT
    conn = sqlite3.connect(str(ruta), check_same_thread=False)
    
    # Registro de funciones emuladas
    conn.create_aggregate("stddev_samp", 1, StddevSamp)
    conn.create_aggregate("stddev", 1, StddevSamp)
    conn.create_function("concat", -1, lambda *args: "".join(str(a) if a is not None else "" for a in args))
    
    return conn


def probar_conexion(tipo_origen, config=None, ruta_sqlite=None):
    """Prueba la conectividad y devuelve (exito: bool, mensaje: str)."""
    t0 = time.time()
    try:
        if tipo_origen in ("clever", "local"):
            cfg = config or obtener_config_por_defecto()
            engine = crear_engine_mysql(cfg)
            with engine.connect() as conn:
                res = conn.execute(text("SELECT 1")).scalar()
                # Verificar si existe FACT_COMPETENCIA
                conn.execute(text("SELECT COUNT(*) FROM FACT_COMPETENCIA")).scalar()
            ms = int((time.time() - t0) * 1000)
            return True, f"Conexión exitosa a MySQL ({cfg['host']}:{cfg['port']}) en {ms} ms."
        else:
            ruta = Path(ruta_sqlite or RUTA_SQLITE_DEFAULT)
            if not ruta.exists():
                return False, f"El archivo de base SQLite no existe en: {ruta}"
            conn = preparar_conexion_sqlite(ruta)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM FACT_COMPETENCIA")
            total = cur.fetchone()[0]
            conn.close()
            ms = int((time.time() - t0) * 1000)
            return True, f"Base SQLite local activa ({total:,} partidos cargados) en {ms} ms."
    except Exception as e:
        return False, f"Fallo de conexión: {str(e)}"


def _adaptar_sql_para_sqlite(sql):
    """Adapta sintaxis temporal de MySQL (ej: INTERVAL 5 YEAR) para SQLite si es necesario."""
    import re
    # 1. Casos compuestos: - INTERVAL N YEAR + INTERVAL M MONTH
    sql_adaptado = re.sub(
        r"\(SELECT MAX\(fecha\) FROM DIM_TIEMPO\)\s*-\s*INTERVAL\s+(\d+)\s+YEAR\s*\+\s*INTERVAL\s+(\d+)\s+MONTH",
        r"DATE((SELECT MAX(fecha) FROM DIM_TIEMPO), '-\1 year', '+\2 month')",
        sql,
        flags=re.IGNORECASE
    )
    # 2. Casos simples: - INTERVAL N YEAR
    sql_adaptado = re.sub(
        r"\(SELECT MAX\(fecha\) FROM DIM_TIEMPO\)\s*-\s*INTERVAL\s+(\d+)\s+YEAR",
        r"DATE((SELECT MAX(fecha) FROM DIM_TIEMPO), '-\1 year')",
        sql_adaptado,
        flags=re.IGNORECASE
    )
    return sql_adaptado


def ejecutar_consulta(sql, tipo_origen="clever", config=None, ruta_sqlite=None):
    """Ejecuta una consulta SQL y retorna (DataFrame, tiempo_segundos, error_str)."""
    t0 = time.time()
    try:
        if tipo_origen in ("clever", "local"):
            cfg = config or obtener_config_por_defecto()
            engine = crear_engine_mysql(cfg)
            with engine.connect() as conn:
                df = pd.read_sql_query(text(sql), conn)
            duracion = time.time() - t0
            return df, duracion, None
        else:
            # Modo SQLite contingencia
            conn = preparar_conexion_sqlite(ruta_sqlite)
            sql_final = _adaptar_sql_para_sqlite(sql)
            df = pd.read_sql_query(sql_final, conn)
            conn.close()
            duracion = time.time() - t0
            return df, duracion, None
    except Exception as e:
        duracion = time.time() - t0
        return pd.DataFrame(), duracion, str(e)
