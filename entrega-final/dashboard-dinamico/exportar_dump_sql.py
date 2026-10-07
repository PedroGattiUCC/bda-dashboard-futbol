"""Exporta el Data Mart completo a un script SQL autónomo (dump_dw_clevercloud.sql)
listo para ser importado directamente en Clever Cloud (vía phpMyAdmin, DBeaver o mysql CLI).

No incluye sentencias 'CREATE DATABASE' o 'USE' para respetar los permisos
de las bases de datos asignadas en la capa gratuita de Clever Cloud.
"""

import sqlite3
import time
from pathlib import Path

DIR_ACTUAL = Path(__file__).resolve().parent
RUTA_SQLITE = DIR_ACTUAL / "dw_contingencia.sqlite"
RUTA_DUMP = DIR_ACTUAL / "dump_dw_clevercloud.sql"


def generar_dump():
    if not RUTA_SQLITE.exists():
        print("Generando SQLite primero...")
        from generar_sqlite_contingencia import construir_sqlite
        construir_sqlite()

    print(f"Leyendo Data Mart desde {RUTA_SQLITE}...")
    conn = sqlite3.connect(str(RUTA_SQLITE))
    cur = conn.cursor()

    t0 = time.time()
    print(f"Escribiendo script SQL en {RUTA_DUMP}...")

    with open(RUTA_DUMP, "w", encoding="utf-8") as f:
        f.write("-- =============================================================================\n")
        f.write("-- DUMP DATA MART DE COMPETENCIA DE FUTBOL (HEFESTO v2) PARA CLEVER CLOUD\n")
        f.write("-- Compatible con phpMyAdmin, MySQL Workbench, DBeaver y MySQL CLI\n")
        f.write("-- =============================================================================\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        f.write("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';\n\n")

        # 1. DDL
        from migrar_a_clevercloud import DDL_TABLAS_CLEVER, DDL_VISTA_PARTICIPACION
        for ddl in DDL_TABLAS_CLEVER:
            f.write(ddl.strip() + "\n\n")

        # 2. INSERTS
        tablas = ["DIM_TIEMPO", "DIM_EQUIPO", "DIM_DIVISION", "DIM_PAIS", "FACT_COMPETENCIA"]
        for tabla in tablas:
            print(f"  • Volcando tabla {tabla}...")
            cur.execute(f"SELECT * FROM {tabla}")
            columnas = [desc[0] for desc in cur.description]
            cols_str = ", ".join(columnas)

            lote = []
            tamano_lote = 1000

            for fila in cur:
                valores_formateados = []
                for v in fila:
                    if v is None:
                        valores_formateados.append("NULL")
                    elif isinstance(v, (int, float)):
                        valores_formateados.append(str(v))
                    else:
                        escaped = str(v).replace("\\", "\\\\").replace("'", "''")
                        valores_formateados.append(f"'{escaped}'")
                lote.append(f"({', '.join(valores_formateados)})")

                if len(lote) >= tamano_lote:
                    f.write(f"INSERT INTO {tabla} ({cols_str}) VALUES\n" + ",\n".join(lote) + ";\n")
                    lote = []

            if lote:
                f.write(f"INSERT INTO {tabla} ({cols_str}) VALUES\n" + ",\n".join(lote) + ";\n")

            f.write("\n")

        # 3. VISTA
        f.write("-- Vista Analítica V_PARTICIPACION\n")
        f.write(DDL_VISTA_PARTICIPACION.strip() + "\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

    conn.close()
    duracion = round(time.time() - t0, 1)
    tam_mb = round(RUTA_DUMP.stat().st_size / (1024 * 1024), 2)
    print(f"✓ ¡Dump completado! Archivo: {RUTA_DUMP.name} ({tam_mb} MB) en {duracion}s.")


if __name__ == "__main__":
    generar_dump()
