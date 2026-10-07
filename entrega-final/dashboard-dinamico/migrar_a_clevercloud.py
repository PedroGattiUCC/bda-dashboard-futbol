"""Script de migración automatizado hacia Clever Cloud MySQL (o cualquier MySQL remoto).

Permite cargar el Data Mart (dimensiones, hechos, índices y la vista V_PARTICIPACION)
en la base de datos de Clever Cloud para la entrega final y la defensa en clase.

Uso:
  python migrar_a_clevercloud.py --host bxxxx-mysql.services.clever-cloud.com \\
                                 --user uxxxx \\
                                 --password pxxxx \\
                                 --database bxxxx
"""

import os
import sys
import argparse
import sqlite3
import time
from pathlib import Path
import mysql.connector

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DIR_ACTUAL = Path(__file__).resolve().parent
RUTA_SQLITE = DIR_ACTUAL / "dw_contingencia.sqlite"

DDL_TABLAS_CLEVER = [
    # 1. DIM_TIEMPO
    """
    CREATE TABLE IF NOT EXISTS DIM_TIEMPO (
        id_tiempo INT NOT NULL,
        fecha DATE NOT NULL,
        temporada VARCHAR(20) NOT NULL,
        anio SMALLINT NOT NULL,
        mes TINYINT NOT NULL,
        nombre_mes VARCHAR(20) NOT NULL,
        trimestre TINYINT NOT NULL,
        dia_semana VARCHAR(20) NOT NULL,
        PRIMARY KEY (id_tiempo),
        UNIQUE KEY uq_dim_tiempo_fecha (fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    # 2. DIM_EQUIPO
    """
    CREATE TABLE IF NOT EXISTS DIM_EQUIPO (
        id_equipo INT NOT NULL,
        nombre_equipo VARCHAR(100) NOT NULL,
        PRIMARY KEY (id_equipo),
        UNIQUE KEY uq_dim_equipo_nombre (nombre_equipo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    # 3. DIM_DIVISION
    """
    CREATE TABLE IF NOT EXISTS DIM_DIVISION (
        id_division INT NOT NULL,
        codigo_division VARCHAR(10) NOT NULL,
        nombre_liga VARCHAR(100) NOT NULL,
        PRIMARY KEY (id_division),
        UNIQUE KEY uq_dim_division_codigo (codigo_division)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    # 4. DIM_PAIS
    """
    CREATE TABLE IF NOT EXISTS DIM_PAIS (
        id_pais INT NOT NULL,
        codigo_pais CHAR(3) NOT NULL,
        nombre_pais VARCHAR(50) NOT NULL,
        PRIMARY KEY (id_pais),
        UNIQUE KEY uq_dim_pais_codigo (codigo_pais)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    # 5. FACT_COMPETENCIA
    """
    CREATE TABLE IF NOT EXISTS FACT_COMPETENCIA (
        id_tiempo INT NOT NULL,
        id_equipo_local INT NOT NULL,
        id_equipo_visitante INT NOT NULL,
        id_division INT NOT NULL,
        id_pais INT NOT NULL,
        goles_local SMALLINT NOT NULL,
        goles_visitante SMALLINT NOT NULL,
        resultado CHAR(1) NOT NULL,
        elo_local DECIMAL(6,2) NULL,
        elo_visitante DECIMAL(6,2) NULL,
        amarillas_local SMALLINT NULL,
        amarillas_visitante SMALLINT NULL,
        rojas_local SMALLINT NULL,
        rojas_visitante SMALLINT NULL,
        puntos_local TINYINT NOT NULL,
        puntos_visitante TINYINT NOT NULL,
        victoria_local TINYINT NOT NULL,
        empate TINYINT NOT NULL,
        victoria_visitante TINYINT NOT NULL,
        PRIMARY KEY (id_tiempo, id_equipo_local, id_equipo_visitante, id_division, id_pais),
        KEY idx_fc_local (id_equipo_local),
        KEY idx_fc_visit (id_equipo_visitante),
        KEY idx_fc_tiempo (id_tiempo),
        KEY idx_fc_div (id_division)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
]

DDL_VISTA_PARTICIPACION = """
CREATE OR REPLACE VIEW V_PARTICIPACION AS
SELECT f.id_tiempo, f.id_division, f.id_pais,
       f.id_equipo_local     AS id_equipo,
       f.id_equipo_visitante AS id_rival,
       'Local'               AS condicion,
       f.goles_local         AS goles_favor,
       f.goles_visitante     AS goles_contra,
       f.puntos_local        AS puntos,
       f.victoria_local      AS victoria,
       f.empate              AS empate,
       f.victoria_visitante  AS derrota,
       f.elo_local           AS elo,
       f.amarillas_local     AS amarillas,
       f.rojas_local         AS rojas
FROM FACT_COMPETENCIA f
UNION ALL
SELECT f.id_tiempo, f.id_division, f.id_pais,
       f.id_equipo_visitante, f.id_equipo_local, 'Visitante',
       f.goles_visitante, f.goles_local, f.puntos_visitante,
       f.victoria_visitante, f.empate, f.victoria_local,
       f.elo_visitante, f.amarillas_visitante, f.rojas_visitante
FROM FACT_COMPETENCIA f;
"""


def migrar(host, port, user, password, database):
    print(f"============================================================")
    print(f"🚀 INICIANDO MIGRACIÓN A CLEVER CLOUD MYSQL")
    print(f"Destino: {user}@{host}:{port}/{database}")
    print(f"============================================================")

    if not RUTA_SQLITE.exists():
        print(f"Generando base local de contingencia primero...")
        from generar_sqlite_contingencia import construir_sqlite
        construir_sqlite()

    conn_sqlite = sqlite3.connect(str(RUTA_SQLITE))
    cur_lite = conn_sqlite.cursor()

    print("\n[1/5] Conectando a Clever Cloud MySQL...")
    try:
        conn_mysql = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )
    except Exception as e:
        print(f"❌ Error al conectar a Clever Cloud: {e}")
        return False

    cur_my = conn_mysql.cursor()

    print("\n[2/5] Creando esquema DDL de tablas...")
    for ddl in DDL_TABLAS_CLEVER:
        cur_my.execute(ddl)
    conn_mysql.commit()
    print("✓ Tablas DIM_TIEMPO, DIM_EQUIPO, DIM_DIVISION, DIM_PAIS y FACT_COMPETENCIA verificadas.")

    tablas = ["DIM_TIEMPO", "DIM_EQUIPO", "DIM_DIVISION", "DIM_PAIS", "FACT_COMPETENCIA"]
    print("\n[3/5] Migrando datos en lotes...")

    for tabla in tablas:
        # Verificar si ya tiene datos
        cur_my.execute(f"SELECT COUNT(*) FROM {tabla}")
        filas_existentes = cur_my.fetchone()[0]
        if filas_existentes > 0:
            print(f"  • {tabla}: Ya contiene {filas_existentes:,} registros. Omitiendo recarga.")
            continue

        cur_lite.execute(f"SELECT * FROM {tabla}")
        columnas = [desc[0] for desc in cur_lite.description]
        placeholders = ", ".join(["%s"] * len(columnas))
        cols_str = ", ".join(columnas)
        sql_insert = f"INSERT INTO {tabla} ({cols_str}) VALUES ({placeholders})"

        lote = []
        tamano_lote = 5000 if tabla == "FACT_COMPETENCIA" else 1000
        total_migrado = 0
        t0 = time.time()

        for fila in cur_lite:
            # Reemplazar None o NaN
            fila_limpia = tuple(None if v is None else v for v in fila)
            lote.append(fila_limpia)
            if len(lote) >= tamano_lote:
                cur_my.executemany(sql_insert, lote)
                conn_mysql.commit()
                total_migrado += len(lote)
                print(f"    -> {tabla}: {total_migrado:,} registros insertados...", end="\r")
                lote = []

        if lote:
            cur_my.executemany(sql_insert, lote)
            conn_mysql.commit()
            total_migrado += len(lote)

        segundos = round(time.time() - t0, 1)
        print(f"  ✓ {tabla}: {total_migrado:,} registros migrados con éxito ({segundos}s).")

    print("\n[4/5] Creando vista analítica V_PARTICIPACION...")
    cur_my.execute(DDL_VISTA_PARTICIPACION)
    conn_mysql.commit()
    print("✓ Vista V_PARTICIPACION creada correctamente.")

    print("\n[5/5] Verificación final de integridad...")
    cur_my.execute("SELECT COUNT(*) FROM FACT_COMPETENCIA")
    total_hechos = cur_my.fetchone()[0]
    cur_my.execute("SELECT COUNT(*) FROM V_PARTICIPACION")
    total_part = cur_my.fetchone()[0]

    print(f"✓ Total en FACT_COMPETENCIA: {total_hechos:,} partidos.")
    print(f"✓ Total en V_PARTICIPACION: {total_part:,} perspectivas de juego (debe ser exactamente el doble).")

    conn_mysql.close()
    conn_sqlite.close()

    print("\n============================================================")
    print("🎉 MIGRACIÓN COMPLETADA CON ÉXITO")
    print("Tu base de datos en Clever Cloud está lista para ser consumida")
    print("por la aplicación web en Render o en tu computadora.")
    print("============================================================\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migración del Data Mart a Clever Cloud MySQL")
    parser.add_argument("--host", default=os.environ.get("MYSQL_HOST"), help="Host de Clever Cloud")
    parser.add_argument("--port", type=int, default=int(os.environ.get("MYSQL_PORT", 3306)), help="Puerto (default: 3306)")
    parser.add_argument("--user", default=os.environ.get("MYSQL_USER"), help="Usuario de Clever Cloud")
    parser.add_argument("--password", default=os.environ.get("MYSQL_PASSWORD"), help="Contraseña de Clever Cloud")
    parser.add_argument("--database", default=os.environ.get("MYSQL_DATABASE"), help="Nombre de Base de Datos en Clever Cloud")

    args = parser.parse_args()

    host = args.host or input("Ingrese MYSQL_HOST (ej: bxxxx-mysql.services.clever-cloud.com): ").strip()
    port = args.port
    user = args.user or input("Ingrese MYSQL_USER (ej: uxxxx): ").strip()
    password = args.password or input("Ingrese MYSQL_PASSWORD: ").strip()
    database = args.database or input("Ingrese MYSQL_DATABASE (ej: bxxxx): ").strip()

    migrar(host, port, user, password, database)
