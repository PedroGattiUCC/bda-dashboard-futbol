"""Genera una base SQLite de contingencia (dw_contingencia.sqlite) a partir de los datos
del Paso 4 (Matches.csv + mapeos).

Permite que el tablero dinámico funcione 100% de manera autónoma en la exposición
incluso sin conexión a internet o sin MySQL instalado en la máquina del frente de clase.
"""

import sys
import sqlite3
from pathlib import Path
import pandas as pd

DIR_ACTUAL = Path(__file__).resolve().parent
DIR_PASO4 = DIR_ACTUAL.parent.parent / "paso-4"
RUTA_CSV = DIR_PASO4 / "datos" / "Matches.csv"
RUTA_MAPEO_DIV = DIR_PASO4 / "mapeos" / "mapeo_divisiones.csv"
RUTA_MAPEO_EQ = DIR_PASO4 / "mapeos" / "mapeo_equipos.csv"
RUTA_SQLITE = DIR_ACTUAL / "dw_contingencia.sqlite"

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
DIAS_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo"
}


def construir_sqlite():
    if not RUTA_CSV.exists():
        print(f"Error: no se encontró {RUTA_CSV}")
        return False

    print(f"Leyendo mapeos desde {DIR_PASO4 / 'mapeos'}...")
    df_map_div = pd.read_csv(RUTA_MAPEO_DIV)
    df_map_eq = pd.read_csv(RUTA_MAPEO_EQ)
    mapa_equipos = dict(zip(df_map_eq["nombre_origen"].str.strip(), df_map_eq["nombre_canonico"].str.strip()))
    divisiones_validas = set(df_map_div["codigo_division"].str.strip())

    print(f"Cargando dataset {RUTA_CSV.name} (~45 MB)...")
    cols_necesarias = [
        "MatchDate", "Division", "HomeTeam", "AwayTeam",
        "FTHome", "FTAway", "FTResult", "HomeElo", "AwayElo",
        "HomeYellow", "AwayYellow", "HomeRed", "AwayRed"
    ]
    df = pd.read_csv(RUTA_CSV, usecols=cols_necesarias, low_memory=False)

    print("Limpiando y filtrando datos según reglas de HEFESTO Paso 4...")
    # Filtro de ligas del alcance
    df["Division"] = df["Division"].astype(str).str.strip()
    df = df[df["Division"].isin(divisiones_validas)].copy()

    # Normalizar nombres de equipos
    df["HomeTeam"] = df["HomeTeam"].astype(str).str.strip().map(lambda x: mapa_equipos.get(x, x))
    df["AwayTeam"] = df["AwayTeam"].astype(str).str.strip().map(lambda x: mapa_equipos.get(x, x))

    # Parsear fechas
    df["MatchDate"] = pd.to_datetime(df["MatchDate"], errors="coerce")
    df = df.dropna(subset=["MatchDate", "FTHome", "FTAway", "FTResult"])
    df["fecha"] = df["MatchDate"].dt.strftime("%Y-%m-%d")

    # Mapeo de país por división
    div_a_pais = dict(zip(df_map_div["codigo_division"].str.strip(), df_map_div["codigo_pais"].str.strip()))
    div_a_nombre_liga = dict(zip(df_map_div["codigo_division"].str.strip(), df_map_div["nombre_liga"].str.strip()))
    df["codigo_pais"] = df["Division"].map(div_a_pais)

    # 1. Dimensión Tiempo
    fechas_unicas = df["MatchDate"].drop_duplicates().sort_values().reset_index(drop=True)
    dim_tiempo = pd.DataFrame({
        "fecha": fechas_unicas.dt.strftime("%Y-%m-%d"),
        "temporada": fechas_unicas.apply(
            lambda d: f"{d.year}-{d.year+1}" if d.month >= 7 else f"{d.year-1}-{d.year}"
        ),
        "anio": fechas_unicas.dt.year,
        "mes": fechas_unicas.dt.month,
        "nombre_mes": fechas_unicas.dt.month.map(MESES_ES),
        "trimestre": fechas_unicas.dt.quarter,
        "dia_semana": fechas_unicas.dt.dayofweek.map(DIAS_ES)
    })
    dim_tiempo["id_tiempo"] = range(1, len(dim_tiempo) + 1)
    mapa_tiempo = dict(zip(dim_tiempo["fecha"], dim_tiempo["id_tiempo"]))

    # 2. Dimensión Equipo
    equipos_unicos = sorted(list(set(df["HomeTeam"]).union(set(df["AwayTeam"]))))
    dim_equipo = pd.DataFrame({
        "id_equipo": range(1, len(equipos_unicos) + 1),
        "nombre_equipo": equipos_unicos
    })
    mapa_equipo = dict(zip(dim_equipo["nombre_equipo"], dim_equipo["id_equipo"]))

    # 3. Dimensión División
    dim_division = df_map_div[["codigo_division", "nombre_liga"]].drop_duplicates().reset_index(drop=True)
    dim_division["id_division"] = range(1, len(dim_division) + 1)
    mapa_div = dict(zip(dim_division["codigo_division"], dim_division["id_division"]))

    # 4. Dimensión País
    paises_unicos = df_map_div[["codigo_pais", "nombre_pais"]].drop_duplicates().reset_index(drop=True)
    paises_unicos["id_pais"] = range(1, len(paises_unicos) + 1)
    mapa_pais = dict(zip(paises_unicos["codigo_pais"], paises_unicos["id_pais"]))

    # 5. Tabla de Hechos
    print("Construyendo FACT_COMPETENCIA...")
    fact = pd.DataFrame()
    fact["id_tiempo"] = df["fecha"].map(mapa_tiempo)
    fact["id_equipo_local"] = df["HomeTeam"].map(mapa_equipo)
    fact["id_equipo_visitante"] = df["AwayTeam"].map(mapa_equipo)
    fact["id_division"] = df["Division"].map(mapa_div)
    fact["id_pais"] = df["codigo_pais"].map(mapa_pais)
    fact["goles_local"] = df["FTHome"].astype(int)
    fact["goles_visitante"] = df["FTAway"].astype(int)
    fact["resultado"] = df["FTResult"].astype(str).str.strip()
    fact["elo_local"] = pd.to_numeric(df["HomeElo"], errors="coerce").round(2)
    fact["elo_visitante"] = pd.to_numeric(df["AwayElo"], errors="coerce").round(2)
    fact["amarillas_local"] = pd.to_numeric(df["HomeYellow"], errors="coerce")
    fact["amarillas_visitante"] = pd.to_numeric(df["AwayYellow"], errors="coerce")
    fact["rojas_local"] = pd.to_numeric(df["HomeRed"], errors="coerce")
    fact["rojas_visitante"] = pd.to_numeric(df["AwayRed"], errors="coerce")

    fact["puntos_local"] = fact["resultado"].map({"H": 3, "D": 1, "A": 0})
    fact["puntos_visitante"] = fact["resultado"].map({"H": 0, "D": 1, "A": 3})
    fact["victoria_local"] = (fact["resultado"] == "H").astype(int)
    fact["empate"] = (fact["resultado"] == "D").astype(int)
    fact["victoria_visitante"] = (fact["resultado"] == "A").astype(int)

    # Eliminar duplicados si existieran
    fact = fact.drop_duplicates(subset=["id_tiempo", "id_equipo_local", "id_equipo_visitante", "id_division", "id_pais"])

    # Escribir en SQLite
    if RUTA_SQLITE.exists():
        RUTA_SQLITE.unlink()

    print(f"Guardando Data Mart en {RUTA_SQLITE}...")
    conn = sqlite3.connect(str(RUTA_SQLITE))
    dim_tiempo.to_sql("DIM_TIEMPO", conn, if_exists="replace", index=False)
    dim_equipo.to_sql("DIM_EQUIPO", conn, if_exists="replace", index=False)
    dim_division.to_sql("DIM_DIVISION", conn, if_exists="replace", index=False)
    paises_unicos.to_sql("DIM_PAIS", conn, if_exists="replace", index=False)
    fact.to_sql("FACT_COMPETENCIA", conn, if_exists="replace", index=False)

    print("Creando vista V_PARTICIPACION e índices en SQLite...")
    cur = conn.cursor()
    cur.execute("""
    CREATE VIEW IF NOT EXISTS V_PARTICIPACION AS
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
    """)

    # Índices para acelerar queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fc_local ON FACT_COMPETENCIA(id_equipo_local);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fc_visit ON FACT_COMPETENCIA(id_equipo_visitante);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fc_tiempo ON FACT_COMPETENCIA(id_tiempo);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fc_div ON FACT_COMPETENCIA(id_division);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dt_fecha ON DIM_TIEMPO(fecha);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_de_nombre ON DIM_EQUIPO(nombre_equipo);")

    conn.commit()
    conn.close()

    print(f"¡Éxito! SQLite de contingencia generado correctamente ({len(fact):,} partidos).")
    return True


if __name__ == "__main__":
    construir_sqlite()
