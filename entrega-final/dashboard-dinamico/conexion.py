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
from sqlalchemy.engine import URL

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
    """Crea un engine de SQLAlchemy optimizado para Clever Cloud y MySQL remoto.
    Usa URL.create para evitar errores si la contraseña contiene caracteres especiales (@, :, etc.).
    """
    user = config.get("user", "root")
    password = config.get("password", "")
    host = config.get("host", "localhost")
    port = int(config.get("port", 3306))
    database = config.get("database", "dw_competencia_futbol")

    # URL segura sin interpolación de strings para caracteres especiales
    url = URL.create(
        drivername="mysql+mysqlconnector",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query={"charset": "utf8mb4"}
    )

    connect_args = {
        "connect_timeout": 15,
        "ssl_disabled": False,
        "ssl_verify_cert": False,  # Permite certificados emitidos en entornos de nube dinámica
    }

    return create_engine(
        url,
        pool_recycle=280,
        pool_pre_ping=True,
        connect_args=connect_args
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
    """Prueba la conectividad y devuelve (exito: bool, mensaje: str, necesita_migracion: bool)."""
    t0 = time.time()
    try:
        if tipo_origen in ("clever", "local"):
            cfg = config or obtener_config_por_defecto()
            engine = crear_engine_mysql(cfg)
            with engine.connect() as conn:
                # 1. Probar conectividad básica y credenciales
                conn.execute(text("SELECT 1"))
                
                # 2. Probar si existen las tablas del Data Mart
                try:
                    total = conn.execute(text("SELECT COUNT(*) FROM FACT_COMPETENCIA")).scalar()
                    ms = int((time.time() - t0) * 1000)
                    return True, f"✓ Conexión exitosa a MySQL ({cfg['host']}:{cfg['port']}) con {total:,} partidos en {ms} ms.", False
                except Exception:
                    ms = int((time.time() - t0) * 1000)
                    return False, f"⚠️ Conectado al servidor MySQL en {ms} ms, pero la tabla 'FACT_COMPETENCIA' no existe todavía. Necesitás inicializarla.", True

        else:
            ruta = Path(ruta_sqlite or RUTA_SQLITE_DEFAULT)
            if not ruta.exists():
                return False, f"El archivo de base SQLite no existe en: {ruta}", False
            conn = preparar_conexion_sqlite(ruta)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM FACT_COMPETENCIA")
            total = cur.fetchone()[0]
            conn.close()
            ms = int((time.time() - t0) * 1000)
            return True, f"✓ Base SQLite local activa ({total:,} partidos cargados) en {ms} ms.", False

    except Exception as e:
        msg = str(e)
        if "Access denied" in msg:
            return False, "❌ Error de autenticación (Access Denied): Usuario o contraseña incorrectos en Clever Cloud.", False
        elif "Unknown database" in msg:
            db_name = config.get('database') if config else 'desconocida'
            return False, f"❌ Base de datos no encontrada ('{db_name}'): En Clever Cloud el nombre de la base es el generado por el sistema (ej: 'bxxxxxxxx'), no 'dw_competencia_futbol'.", False
        elif "Can't connect to MySQL server" in msg or "timed out" in msg:
            h = config.get('host') if config else ''
            p = config.get('port') if config else 3306
            return False, f"❌ No se pudo conectar al host ('{h}:{p}'): Verificá que el Host de Clever Cloud esté bien escrito y el puerto sea 3306.", False
        return False, f"❌ Fallo de conexión: {msg}", False


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


def cargar_data_mart_en_clevercloud(config, callback_progreso=None):
    """Copia el esquema, las dimensiones, hechos y vistas desde SQLite hacia Clever Cloud MySQL."""
    import mysql.connector
    from migrar_a_clevercloud import DDL_TABLAS_CLEVER, DDL_VISTA_PARTICIPACION

    if not RUTA_SQLITE_DEFAULT.exists():
        return False, f"No se encontró el archivo de contingencia {RUTA_SQLITE_DEFAULT}."

    if callback_progreso:
        callback_progreso("Conectando con Clever Cloud MySQL...", 0.05)

    try:
        conn_my = mysql.connector.connect(
            host=config.get("host"),
            port=int(config.get("port", 3306)),
            user=config.get("user"),
            password=config.get("password"),
            database=config.get("database"),
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            ssl_disabled=False,
            ssl_verify_cert=False
        )
    except Exception as e:
        return False, f"No se pudo conectar a Clever Cloud: {e}"

    cur_my = conn_my.cursor()
    conn_lite = sqlite3.connect(str(RUTA_SQLITE_DEFAULT))
    cur_lite = conn_lite.cursor()

    try:
        # 1. Crear tablas DDL
        if callback_progreso:
            callback_progreso("Creando tablas de dimensiones y hechos...", 0.15)
        for ddl in DDL_TABLAS_CLEVER:
            cur_my.execute(ddl)
        conn_my.commit()

        # 2. Cargar datos en lotes
        tablas = ["DIM_TIEMPO", "DIM_EQUIPO", "DIM_DIVISION", "DIM_PAIS", "FACT_COMPETENCIA"]
        pesos = {"DIM_TIEMPO": 0.25, "DIM_EQUIPO": 0.35, "DIM_DIVISION": 0.40, "DIM_PAIS": 0.45, "FACT_COMPETENCIA": 0.85}

        for tabla in tablas:
            if callback_progreso:
                callback_progreso(f"Migrando registros de {tabla}...", pesos[tabla])
            
            cur_my.execute(f"SELECT COUNT(*) FROM {tabla}")
            existentes = cur_my.fetchone()[0]
            if existentes > 0:
                continue

            cur_lite.execute(f"SELECT * FROM {tabla}")
            columnas = [d[0] for d in cur_lite.description]
            placeholders = ", ".join(["%s"] * len(columnas))
            cols_str = ", ".join(columnas)
            sql_insert = f"INSERT INTO {tabla} ({cols_str}) VALUES ({placeholders})"

            lote = []
            tamano_lote = 5000 if tabla == "FACT_COMPETENCIA" else 1000
            for fila in cur_lite:
                fila_limpia = tuple(None if v is None else v for v in fila)
                lote.append(fila_limpia)
                if len(lote) >= tamano_lote:
                    cur_my.executemany(sql_insert, lote)
                    conn_my.commit()
                    lote = []
            if lote:
                cur_my.executemany(sql_insert, lote)
                conn_my.commit()

        # 3. Crear vista
        if callback_progreso:
            callback_progreso("Creando vista analítica V_PARTICIPACION...", 0.95)
        cur_my.execute(DDL_VISTA_PARTICIPACION)
        conn_my.commit()

        conn_my.close()
        conn_lite.close()

        if callback_progreso:
            callback_progreso("¡Data Mart cargado exitosamente en Clever Cloud!", 1.0)

        return True, "Data Mart cargado y validado exitosamente en Clever Cloud."

    except Exception as e:
        conn_my.close()
        conn_lite.close()
        return False, f"Error durante la carga a Clever Cloud: {e}"
