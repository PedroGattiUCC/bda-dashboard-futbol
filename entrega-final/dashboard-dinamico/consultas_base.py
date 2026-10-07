"""Definición y catálogo modular de las 12 preguntas de negocio oficiales
(Metodología HEFESTO v2) y generadores dinámicos de consultas SQL sobre el Data Mart.
"""

DICCIONARIO_TABLAS = {
    "FACT_COMPETENCIA": [
        ("id_tiempo", "INT (FK)", "Clave foránea a DIM_TIEMPO"),
        ("id_equipo_local", "INT (FK)", "Clave foránea a DIM_EQUIPO (club local)"),
        ("id_equipo_visitante", "INT (FK)", "Clave foránea a DIM_EQUIPO (club visitante)"),
        ("id_division", "INT (FK)", "Clave foránea a DIM_DIVISION (liga / torneo)"),
        ("id_pais", "INT (FK)", "Clave foránea a DIM_PAIS (país del torneo)"),
        ("goles_local", "SMALLINT", "Goles marcados por el equipo local"),
        ("goles_visitante", "SMALLINT", "Goles marcados por el equipo visitante"),
        ("resultado", "CHAR(1)", "'H' (local), 'D' (empate), 'A' (visitante)"),
        ("elo_local", "DECIMAL(6,2)", "Puntuación Elo del equipo local al momento del partido"),
        ("elo_visitante", "DECIMAL(6,2)", "Puntuación Elo del visitante al momento del partido"),
        ("amarillas_local", "SMALLINT", "Tarjetas amarillas al local"),
        ("amarillas_visitante", "SMALLINT", "Tarjetas amarillas al visitante"),
        ("rojas_local", "SMALLINT", "Tarjetas rojas al local"),
        ("rojas_visitante", "SMALLINT", "Tarjetas rojas al visitante"),
        ("puntos_local", "TINYINT", "3 (victoria), 1 (empate), 0 (derrota)"),
        ("puntos_visitante", "TINYINT", "3 (victoria), 1 (empate), 0 (derrota)"),
        ("victoria_local", "TINYINT", "1 si ganó local, 0 en caso contrario"),
        ("empate", "TINYINT", "1 si empataron, 0 en caso contrario"),
        ("victoria_visitante", "TINYINT", "1 si ganó visitante, 0 en caso contrario"),
    ],
    "DIM_EQUIPO": [
        ("id_equipo", "INT (PK)", "Identificador único de club"),
        ("nombre_equipo", "VARCHAR(100)", "Nombre unificado y canónico del club"),
    ],
    "DIM_DIVISION": [
        ("id_division", "INT (PK)", "Identificador único de división"),
        ("codigo_division", "VARCHAR(10)", "Código de la liga (ej: 'E0', 'SP1', 'I1')"),
        ("nombre_liga", "VARCHAR(100)", "Nombre formal (ej: 'Premier League', 'La Liga')"),
    ],
    "DIM_PAIS": [
        ("id_pais", "INT (PK)", "Identificador único de país"),
        ("codigo_pais", "CHAR(3)", "Código ISO (ej: 'ENG', 'ESP', 'ITA', 'GER', 'FRA')"),
        ("nombre_pais", "VARCHAR(50)", "Nombre del país (ej: 'Inglaterra', 'España')"),
    ],
    "DIM_TIEMPO": [
        ("id_tiempo", "INT (PK)", "Identificador único de fecha"),
        ("fecha", "DATE", "Fecha del partido (YYYY-MM-DD)"),
        ("temporada", "VARCHAR(20)", "Temporada competitiva (ej: '2024-2025')"),
        ("anio", "SMALLINT", "Año calendario"),
        ("mes", "TINYINT", "Mes del año (1-12)"),
        ("nombre_mes", "VARCHAR(20)", "Nombre del mes"),
        ("trimestre", "TINYINT", "Trimestre (1-4)"),
        ("dia_semana", "VARCHAR(20)", "Día de la semana"),
    ],
    "V_PARTICIPACION": [
        ("id_tiempo", "INT", "Clave foránea a DIM_TIEMPO"),
        ("id_division", "INT", "Clave foránea a DIM_DIVISION"),
        ("id_pais", "INT", "Clave foránea a DIM_PAIS"),
        ("id_equipo", "INT", "Club analizado (local o visitante)"),
        ("id_rival", "INT", "Club rival"),
        ("condicion", "VARCHAR(10)", "'Local' o 'Visitante'"),
        ("goles_favor", "SMALLINT", "Goles a favor en el partido"),
        ("goles_contra", "SMALLINT", "Goles en contra en el partido"),
        ("puntos", "TINYINT", "Puntos obtenidos (3, 1, 0)"),
        ("victoria", "TINYINT", "1 si ganó, 0 si no"),
        ("empate", "TINYINT", "1 si empató, 0 si no"),
        ("derrota", "TINYINT", "1 si perdió, 0 si no"),
        ("elo", "DECIMAL(6,2)", "Puntaje Elo del equipo en ese partido"),
        ("amarillas", "SMALLINT", "Tarjetas amarillas recibidas"),
        ("rojas", "SMALLINT", "Tarjetas rojas recibidas"),
    ],
}

PLANTILLAS_SQL_PROFE = {
    "Top 10 clubes con más victorias de la historia": """
SELECT e.nombre_equipo,
       COUNT(*) AS partidos_totales,
       SUM(p.victoria) AS victorias,
       ROUND(100.0 * SUM(p.victoria) / COUNT(*), 1) AS pct_victorias
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
GROUP BY e.id_equipo, e.nombre_equipo
HAVING COUNT(*) >= 100
ORDER BY victorias DESC
LIMIT 10;
""",
    "Partidos con mayor cantidad de goles totales": """
SELECT t.fecha,
       el.nombre_equipo AS local,
       f.goles_local,
       ev.nombre_equipo AS visitante,
       f.goles_visitante,
       (f.goles_local + f.goles_visitante) AS goles_totales,
       d.nombre_liga
FROM FACT_COMPETENCIA f
JOIN DIM_EQUIPO el ON el.id_equipo = f.id_equipo_local
JOIN DIM_EQUIPO ev ON ev.id_equipo = f.id_equipo_visitante
JOIN DIM_TIEMPO t  ON t.id_tiempo = f.id_tiempo
JOIN DIM_DIVISION d ON d.id_division = f.id_division
ORDER BY goles_totales DESC
LIMIT 10;
""",
    "Evolución anual de promedio de goles por partido": """
SELECT t.anio,
       COUNT(*) AS partidos,
       ROUND(AVG(f.goles_local + f.goles_visitante), 2) AS goles_promedio_partido
FROM FACT_COMPETENCIA f
JOIN DIM_TIEMPO t ON t.id_tiempo = f.id_tiempo
GROUP BY t.anio
ORDER BY t.anio ASC;
""",
    "Porcentaje de victorias de local por temporada": """
SELECT t.temporada,
       COUNT(*) AS partidos,
       ROUND(100.0 * AVG(f.victoria_local), 1) AS pct_gana_local,
       ROUND(100.0 * AVG(f.empate), 1) AS pct_empate,
       ROUND(100.0 * AVG(f.victoria_visitante), 1) AS pct_gana_visitante
FROM FACT_COMPETENCIA f
JOIN DIM_TIEMPO t ON t.id_tiempo = f.id_tiempo
GROUP BY t.temporada
ORDER BY t.temporada DESC
LIMIT 10;
""",
    "Clubes con mayor efectividad en una liga específica (ej: Premier League)": """
SELECT e.nombre_equipo,
       COUNT(*) AS partidos,
       SUM(p.victoria) AS victorias,
       ROUND(100.0 * AVG(p.victoria), 1) AS pct_victorias,
       ROUND(AVG(p.puntos), 2) AS puntos_promedio
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
JOIN DIM_DIVISION d ON d.id_division = p.id_division
WHERE d.codigo_division = 'E0'
GROUP BY e.id_equipo, e.nombre_equipo
HAVING COUNT(*) >= 50
ORDER BY pct_victorias DESC
LIMIT 10;
"""
}

PREGUNTAS_CATALOGO = [
    {
        "id": 1,
        "titulo": "¿Cuánto mejoró un equipo específico en 5 años?",
        "ejemplo": "Nottingham Forest",
        "indicadores": "Evolución de Elo — Perspectivas: Equipo, Tiempo",
        "descripcion": "Analiza la trayectoria del indicador Elo de un equipo a lo largo del tiempo, contrastando su valor inicial, evolución anual y salto competitivo.",
        "conclusion_oficial": "Nottingham Forest pasó de 1.466 puntos de Elo (septiembre de 2021, en Championship) a 1.780 (agosto de 2026): +314 puntos, un 21,4 % de crecimiento sostenido. El mayor salto ocurrió entre 2024 y 2025 al afianzarse en Premier League.",
        "tipo_grafico_default": "line",
        "sql_builder": lambda params: f"""
SELECT t.anio,
       ROUND(AVG(p.elo), 1) AS elo_promedio,
       ROUND(MIN(p.elo), 1) AS elo_minimo,
       ROUND(MAX(p.elo), 1) AS elo_maximo,
       COUNT(*)             AS partidos
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
JOIN DIM_TIEMPO t ON t.id_tiempo = p.id_tiempo
WHERE e.nombre_equipo = '{params.get("equipo", "Nottm Forest")}'
  AND p.elo IS NOT NULL
  AND t.fecha >= (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL {params.get("anios", 5)} YEAR
GROUP BY t.anio
ORDER BY t.anio ASC;
""",
        "sql_resumen_builder": lambda params: f"""
WITH v AS (
    SELECT t.fecha, p.elo
    FROM V_PARTICIPACION p
    JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
    JOIN DIM_TIEMPO t ON t.id_tiempo = p.id_tiempo
    WHERE e.nombre_equipo = '{params.get("equipo", "Nottm Forest")}'
      AND p.elo IS NOT NULL
      AND t.fecha >= (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL {params.get("anios", 5)} YEAR
), extremos AS (SELECT MIN(fecha) AS f0, MAX(fecha) AS f1 FROM v)
SELECT i.fecha AS fecha_inicial, i.elo AS elo_inicial,
       f.fecha AS fecha_final,   f.elo AS elo_final,
       ROUND(f.elo - i.elo, 1)                 AS variacion,
       ROUND(100.0 * (f.elo - i.elo) / i.elo, 1) AS pct_crecimiento
FROM extremos x
JOIN v i ON i.fecha = x.f0
JOIN v f ON f.fecha = x.f1;
"""
    },
    {
        "id": 2,
        "titulo": "¿Qué equipo tiende a ganar más contra otro según su historial? (Clásicos / Derbis)",
        "ejemplo": "Real Madrid vs Barcelona, Arsenal vs Tottenham",
        "indicadores": "% de victorias en enfrentamientos directos — Perspectivas: Equipo, Rival",
        "descripcion": "Compara el balance cara a cara (% victorias, empates y derrotas) entre rivales tradicionales o cualquier par de clubes seleccionado.",
        "conclusion_oficial": "En los derbis analizados, Arsenal domina a Tottenham (47 % victorias vs 20 %), Sevilla a Betis (43 % vs 18 %), Celtic a Rangers (47 % vs 31 %), Man United a Liverpool (44 % vs 35 %) e Inter a Milan (44 % vs 36 %). En el clásico español, Barcelona supera a Real Madrid en liga (46 % vs 33 %).",
        "tipo_grafico_default": "stacked_bar",
        "sql_builder": lambda params: (
            f"""
SELECT '{params.get("equipo_a", "Arsenal")} vs {params.get("equipo_b", "Tottenham")}' AS clasico,
       COUNT(*)                                     AS partidos,
       SUM(p.victoria)                              AS gana_a,
       SUM(p.empate)                                AS empates,
       SUM(p.derrota)                               AS gana_b,
       ROUND(100.0 * SUM(p.victoria) / COUNT(*), 1) AS pct_gana_a,
       ROUND(100.0 * SUM(p.empate) / COUNT(*), 1)   AS pct_empate,
       ROUND(100.0 * SUM(p.derrota) / COUNT(*), 1)  AS pct_gana_b
FROM DIM_EQUIPO ea
CROSS JOIN DIM_EQUIPO eb
JOIN V_PARTICIPACION p ON p.id_equipo = ea.id_equipo AND p.id_rival = eb.id_equipo
WHERE ea.nombre_equipo = '{params.get("equipo_a", "Arsenal")}'
  AND eb.nombre_equipo = '{params.get("equipo_b", "Tottenham")}'
GROUP BY ea.nombre_equipo, eb.nombre_equipo;
""" if params.get("modo_pareja", False) else
            """
WITH clasicos AS (
    SELECT 'Real Madrid' AS equipo_a, 'Barcelona' AS equipo_b
    UNION ALL SELECT 'Arsenal', 'Tottenham'
    UNION ALL SELECT 'Sevilla', 'Betis'
    UNION ALL SELECT 'Man United', 'Liverpool'
    UNION ALL SELECT 'Celtic', 'Rangers'
    UNION ALL SELECT 'Inter', 'Milan'
)
SELECT CONCAT(c.equipo_a, ' vs ', c.equipo_b)     AS clasico,
       COUNT(*)                                     AS partidos,
       SUM(p.victoria)                              AS gana_a,
       SUM(p.empate)                                AS empates,
       SUM(p.derrota)                               AS gana_b,
       ROUND(100.0 * SUM(p.victoria) / COUNT(*), 1) AS pct_gana_a,
       ROUND(100.0 * SUM(p.empate) / COUNT(*), 1)   AS pct_empate,
       ROUND(100.0 * SUM(p.derrota) / COUNT(*), 1)  AS pct_gana_b
FROM clasicos c
JOIN DIM_EQUIPO ea ON ea.nombre_equipo = c.equipo_a
JOIN DIM_EQUIPO eb ON eb.nombre_equipo = c.equipo_b
JOIN V_PARTICIPACION p ON p.id_equipo = ea.id_equipo AND p.id_rival = eb.id_equipo
GROUP BY c.equipo_a, c.equipo_b
ORDER BY partidos DESC;
"""
        )
    },
    {
        "id": 3,
        "titulo": "¿Existe ventaja de local?",
        "ejemplo": "En Europa y por Liga",
        "indicadores": "Ventaja de localía, Promedio de goles a favor / contra — Perspectivas: División, País",
        "descripcion": "Calcula el porcentaje de victorias locales contra visitantes y el diferencial de goles tanto a nivel continental consolidado como desagregado por liga.",
        "conclusion_oficial": "Existe una marcada ventaja de localía en todas las ligas europeas: el equipo local gana en promedio el 45,0 % de los partidos, mientras que el visitante solo el 28,1 % (ventaja neta de +16,9 puntos porcentuales) y marca 0,38 goles más por partido.",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
SELECT CONCAT(d.codigo_division, ' - ', d.nombre_liga)                    AS liga,
       COUNT(*)                                                             AS partidos,
       ROUND(100.0 * AVG(f.victoria_local), 1)                              AS pct_local,
       ROUND(100.0 * AVG(f.victoria_visitante), 1)                          AS pct_visitante,
       ROUND(100.0 * (AVG(f.victoria_local) - AVG(f.victoria_visitante)), 1) AS ventaja_pp,
       ROUND(AVG(f.goles_local), 2)                                         AS goles_local_prom,
       ROUND(AVG(f.goles_visitante), 2)                                     AS goles_visitante_prom,
       ROUND(AVG(f.goles_local) - AVG(f.goles_visitante), 2)                AS dif_goles
FROM FACT_COMPETENCIA f
JOIN DIM_DIVISION d ON d.id_division = f.id_division
GROUP BY d.id_division, d.codigo_division, d.nombre_liga
ORDER BY ventaja_pp DESC
LIMIT {params.get("limit", 20)};
"""
    },
    {
        "id": 4,
        "titulo": "¿Qué liga es más pareja?",
        "ejemplo": "Dispersión de brecha Elo entre rivales",
        "indicadores": "Paridad de la liga — Perspectivas: División, Tiempo",
        "descripcion": "Determina el grado de competitividad y paridad calculando el desvío estándar de la brecha de Elo entre equipos rivales (menor desvío = mayor paridad).",
        "conclusion_oficial": "Las segundas divisiones son significativamente más parejas que las ligas de élite. La Segunda División de España (desvío 72,5), la Ligue 2 de Francia (73,8) y la Serie B de Italia (76,1) encabezan el ranking de mayor paridad competitiva.",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
SELECT CONCAT(d.codigo_division, ' - ', d.nombre_liga)            AS liga,
       COUNT(*)                                                     AS partidos,
       SUM(f.elo_local IS NOT NULL AND f.elo_visitante IS NOT NULL) AS partidos_con_elo,
       ROUND(STDDEV_SAMP(f.elo_local - f.elo_visitante), 1)         AS desvio_brecha_elo,
       ROUND(AVG(ABS(f.elo_local - f.elo_visitante)), 1)            AS brecha_elo_media,
       ROUND(100.0 * AVG(f.empate), 1)                               AS pct_empates
FROM FACT_COMPETENCIA f
JOIN DIM_DIVISION d ON d.id_division = f.id_division
GROUP BY d.id_division, d.codigo_division, d.nombre_liga
HAVING partidos_con_elo >= {params.get("pct_min_elo", 80) / 100.0} * partidos
ORDER BY desvio_brecha_elo ASC
LIMIT {params.get("limit", 20)};
"""
    },
    {
        "id": 5,
        "titulo": "¿Qué liga acumula más tarjetas?",
        "ejemplo": "Promedio de tarjetas amarillas y rojas",
        "indicadores": "Promedio de tarjetas amarillas y rojas — Perspectivas: División, País",
        "descripcion": "Mide el nivel de fricción y disciplina deportiva calculando el promedio de tarjetas por partido en aquellas ligas con registro disciplinario riguroso.",
        "conclusion_oficial": "Las ligas de la península ibérica concentran la mayor cantidad de tarjetas: Primeira Liga de Portugal lidera con 5,09 amarillas por encuentro, seguida de cerca por La Liga de España con 5,02 amarillas por partido.",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
SELECT CONCAT(d.codigo_division, ' - ', d.nombre_liga)            AS liga,
       pa.nombre_pais                                               AS pais,
       COUNT(f.amarillas_local)                                     AS partidos_con_dato,
       ROUND(AVG(f.amarillas_local + f.amarillas_visitante), 2)     AS amarillas_x_partido,
       ROUND(AVG(f.rojas_local + f.rojas_visitante), 3)             AS rojas_x_partido
FROM FACT_COMPETENCIA f
JOIN DIM_DIVISION d ON d.id_division = f.id_division
JOIN DIM_PAIS pa    ON pa.id_pais = f.id_pais
GROUP BY d.id_division, d.codigo_division, d.nombre_liga, pa.nombre_pais
HAVING partidos_con_dato >= {params.get("min_partidos", 1000)}
ORDER BY {params.get("orden", "amarillas_x_partido")} DESC
LIMIT {params.get("limit", 20)};
"""
    },
    {
        "id": 6,
        "titulo": "¿Qué equipos tienen mejor estadística de visitante?",
        "ejemplo": "Últimos 5 años",
        "indicadores": "% de victorias y goles a favor como visitante — Perspectivas: Equipo, División",
        "descripcion": "Evalúa el poderío y regularidad de los clubes fuera de casa, analizando el porcentaje de victorias como visitante sobre un umbral mínimo de encuentros.",
        "conclusion_oficial": "Porto lidera en Europa con un 71,8 % de victorias a domicilio, seguido por PSV Eindhoven (70,9 %), Celtic (70,7 %), Sporting Lisboa (69,7 %) y Bayern Munich (68,5 %).",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
SELECT e.nombre_equipo                        AS equipo,
       GROUP_CONCAT(DISTINCT d.codigo_division)  AS divisiones,
       COUNT(*)                                  AS partidos_visitante,
       ROUND(100.0 * AVG(p.victoria), 1)         AS pct_victorias,
       ROUND(AVG(p.goles_favor), 2)              AS goles_favor_prom,
       ROUND(AVG(p.goles_contra), 2)             AS goles_contra_prom
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e   ON e.id_equipo = p.id_equipo
JOIN DIM_DIVISION d ON d.id_division = p.id_division
JOIN DIM_TIEMPO t   ON t.id_tiempo = p.id_tiempo
WHERE p.condicion = 'Visitante'
  AND t.fecha >= (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL {params.get("anios", 5)} YEAR
GROUP BY e.id_equipo, e.nombre_equipo
HAVING partidos_visitante >= {params.get("min_partidos", 60)}
ORDER BY pct_victorias DESC
LIMIT {params.get("limit", 15)};
"""
    },
    {
        "id": 7,
        "titulo": "¿Cuál es el porcentaje general de victorias por equipo?",
        "ejemplo": "Últimos 5 años (consolidado local + visitante)",
        "indicadores": "% de victorias, empates y derrotas — Perspectivas: Equipo, División, Tiempo",
        "descripcion": "Clasifica la efectividad deportiva integral de los clubes en el último lustro, calculando el ratio de victorias sobre el total de encuentros disputados.",
        "conclusion_oficial": "Celtic (76,9 %) y PSV Eindhoven (76,0 %) registran las tasas de victoria más altas de Europa en sus respectivas competencias locales, seguidos por Porto (75,0 %), Bayern Munich (73,8 %) y Sporting Lisboa (73,6 %).",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
SELECT e.nombre_equipo                        AS equipo,
       GROUP_CONCAT(DISTINCT d.codigo_division)  AS divisiones,
       COUNT(*)                                  AS partidos,
       ROUND(100.0 * AVG(p.victoria), 1)         AS pct_victorias,
       ROUND(100.0 * AVG(p.empate), 1)           AS pct_empates,
       ROUND(100.0 * AVG(p.derrota), 1)          AS pct_derrotas
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e   ON e.id_equipo = p.id_equipo
JOIN DIM_DIVISION d ON d.id_division = p.id_division
JOIN DIM_TIEMPO t   ON t.id_tiempo = p.id_tiempo
WHERE t.fecha >= (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL {params.get("anios", 5)} YEAR
GROUP BY e.id_equipo, e.nombre_equipo
HAVING partidos >= {params.get("min_partidos", 120)}
ORDER BY pct_victorias DESC
LIMIT {params.get("limit", 15)};
"""
    },
    {
        "id": 8,
        "titulo": "¿Cuál es el promedio de goles por equipo?",
        "ejemplo": "Últimos 5 años (atractivo ofensivo)",
        "indicadores": "Promedio de goles a favor y en contra — Perspectivas: Equipo, División, Tiempo",
        "descripcion": "Identifica a las escuadras con mayor poder ofensivo y potencial de entretenimiento/espectáculo comercial, calculando los goles anotados por partido.",
        "conclusion_oficial": "Bayern Munich se destaca con amplitud como el equipo más goleador de Europa, con un promedio de 2,98 goles a favor por partido en los últimos 5 años. Lo escoltan PSV (2,70), Celtic (2,60) y Manchester City (2,49).",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
SELECT e.nombre_equipo                        AS equipo,
       GROUP_CONCAT(DISTINCT d.codigo_division)  AS divisiones,
       COUNT(*)                                  AS partidos,
       ROUND(AVG(p.goles_favor), 2)              AS goles_favor_prom,
       ROUND(AVG(p.goles_contra), 2)             AS goles_contra_prom
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e   ON e.id_equipo = p.id_equipo
JOIN DIM_DIVISION d ON d.id_division = p.id_division
JOIN DIM_TIEMPO t   ON t.id_tiempo = p.id_tiempo
WHERE t.fecha >= (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL {params.get("anios", 5)} YEAR
GROUP BY e.id_equipo, e.nombre_equipo
HAVING partidos >= {params.get("min_partidos", 120)}
ORDER BY goles_favor_prom DESC
LIMIT {params.get("limit", 15)};
"""
    },
    {
        "id": 9,
        "titulo": "¿El equipo es consistente a lo largo de los años?",
        "ejemplo": "Ascensos, descensos y permanencia divisional",
        "indicadores": "Consistencia divisional, variabilidad de puntos — Perspectivas: Equipo, División, Tiempo",
        "descripcion": "Mide la estabilidad de las organizaciones deportivas a través de los cambios de categoría (ascensos y descensos) y la estabilidad en puntos ganados por fecha.",
        "conclusion_oficial": "FC Metz es el equipo con mayor inestabilidad divisional del dataset, registrando 15 cambios de categoría (efecto 'ascensor'). En contraste, instituciones como Athletic Bilbao, Lyon, Barcelona y Real Madrid mantuvieron el 100 % de permanencia en la máxima categoría sin descensos.",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: (
            f"""
WITH por_temporada AS (
    SELECT p.id_equipo, t.temporada, d.codigo_division,
           COUNT(*) AS partidos, SUM(p.puntos) AS puntos,
           ROW_NUMBER() OVER (PARTITION BY p.id_equipo, t.temporada ORDER BY COUNT(*) DESC) AS rn
    FROM V_PARTICIPACION p
    JOIN DIM_TIEMPO t   ON t.id_tiempo = p.id_tiempo
    JOIN DIM_DIVISION d ON d.id_division = p.id_division
    JOIN DIM_PAIS pa    ON pa.id_pais = p.id_pais
    WHERE pa.codigo_pais IN ({params.get("paises_in", "'ENG', 'GER', 'ITA', 'ESP', 'FRA'")})
    GROUP BY p.id_equipo, t.temporada, d.codigo_division
), division_principal AS (
    SELECT id_equipo, temporada, codigo_division, puntos / partidos AS puntos_x_partido,
           LAG(codigo_division) OVER (PARTITION BY id_equipo ORDER BY temporada) AS division_anterior
    FROM por_temporada
    WHERE rn = 1
)
SELECT e.nombre_equipo                                                             AS equipo,
       COUNT(*)                                                                    AS temporadas,
       COUNT(DISTINCT codigo_division)                                             AS divisiones_distintas,
       SUM(division_anterior IS NOT NULL AND division_anterior <> codigo_division) AS cambios_de_division,
       ROUND(AVG(puntos_x_partido), 2)                                             AS puntos_x_partido,
       ROUND(STDDEV_SAMP(puntos_x_partido), 2)                                     AS desvio_puntos_x_partido
FROM division_principal dp
JOIN DIM_EQUIPO e ON e.id_equipo = dp.id_equipo
GROUP BY e.id_equipo, e.nombre_equipo
HAVING temporadas >= {params.get("min_temporadas", 20)}
ORDER BY cambios_de_division DESC, desvio_puntos_x_partido DESC
LIMIT {params.get("limit", 15)};
""" if params.get("modo", "inconsistentes") == "inconsistentes" else
            f"""
WITH por_temporada AS (
    SELECT p.id_equipo, t.temporada, d.codigo_division,
           COUNT(*) AS partidos, SUM(p.puntos) AS puntos,
           ROW_NUMBER() OVER (PARTITION BY p.id_equipo, t.temporada ORDER BY COUNT(*) DESC) AS rn
    FROM V_PARTICIPACION p
    JOIN DIM_TIEMPO t   ON t.id_tiempo = p.id_tiempo
    JOIN DIM_DIVISION d ON d.id_division = p.id_division
    JOIN DIM_PAIS pa    ON pa.id_pais = p.id_pais
    WHERE pa.codigo_pais IN ({params.get("paises_in", "'ENG', 'GER', 'ITA', 'ESP', 'FRA'")})
    GROUP BY p.id_equipo, t.temporada, d.codigo_division
), division_principal AS (
    SELECT id_equipo, temporada, codigo_division, puntos / partidos AS puntos_x_partido,
           LAG(codigo_division) OVER (PARTITION BY id_equipo ORDER BY temporada) AS division_anterior
    FROM por_temporada
    WHERE rn = 1
)
SELECT e.nombre_equipo                                                             AS equipo,
       COUNT(*)                                                                    AS temporadas,
       MIN(codigo_division)                                                        AS division,
       SUM(division_anterior IS NOT NULL AND division_anterior <> codigo_division) AS cambios_de_division,
       ROUND(AVG(puntos_x_partido), 2)                                             AS puntos_x_partido,
       ROUND(STDDEV_SAMP(puntos_x_partido), 2)                                     AS desvio_puntos_x_partido
FROM division_principal dp
JOIN DIM_EQUIPO e ON e.id_equipo = dp.id_equipo
GROUP BY e.id_equipo, e.nombre_equipo
HAVING temporadas >= {params.get("min_temporadas", 25)} AND cambios_de_division = 0
ORDER BY desvio_puntos_x_partido ASC
LIMIT {params.get("limit", 10)};
"""
        )
    },
    {
        "id": 10,
        "titulo": "¿Cuáles son los equipos con mayor incremento de Elo?",
        "ejemplo": "Últimos 3 años (equipos revelación)",
        "indicadores": "Evolución de Elo — Perspectivas: Equipo, Tiempo",
        "descripcion": "Rastrea a los clubes de mayor progreso competitivo reciente comparando la puntuación Elo al inicio y al final de la ventana temporal.",
        "conclusion_oficial": "Como 1907 lidera con un aumento récord de +327 puntos de Elo tras su vertiginoso ascenso a la Serie A italiana, seguido por el Paris FC (+239 puntos) y el Brest (+184 puntos).",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
WITH v AS (
    SELECT e.nombre_equipo, t.fecha, p.elo,
           ROW_NUMBER() OVER (PARTITION BY p.id_equipo ORDER BY t.fecha)      AS orden_inicial,
           ROW_NUMBER() OVER (PARTITION BY p.id_equipo ORDER BY t.fecha DESC) AS orden_final,
           COUNT(*)     OVER (PARTITION BY p.id_equipo)                       AS partidos
    FROM V_PARTICIPACION p
    JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
    JOIN DIM_TIEMPO t ON t.id_tiempo = p.id_tiempo
    WHERE p.elo IS NOT NULL
      AND t.fecha >= (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL {params.get("anios", 3)} YEAR
)
SELECT i.nombre_equipo                          AS equipo,
       i.elo                                    AS elo_inicial,
       f.elo                                    AS elo_final,
       ROUND(f.elo - i.elo, 1)                  AS incremento,
       ROUND(100.0 * (f.elo - i.elo) / i.elo, 1)  AS pct_crecimiento,
       i.partidos
FROM v i
JOIN v f ON f.nombre_equipo = i.nombre_equipo AND f.orden_final = 1
WHERE i.orden_inicial = 1
  AND i.partidos >= {params.get("min_partidos", 30)}
  AND i.fecha < (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL {params.get("anios", 3)} YEAR + INTERVAL 3 MONTH
  AND f.fecha >= (SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL 1 YEAR
ORDER BY incremento DESC
LIMIT {params.get("limit", 15)};
"""
    },
    {
        "id": 11,
        "titulo": "¿Cuáles son los equipos con mayor promedio de rojas? (Fair Play)",
        "ejemplo": "Riesgo disciplinario para patrocinadores",
        "indicadores": "Promedio de tarjetas rojas y amarillas — Perspectivas: Equipo",
        "descripcion": "Identifica a las instituciones con peor conducta disciplinaria en el campo de juego, factor crítico para la evaluación de reputación de marca para sponsors.",
        "conclusion_oficial": "Boavista de Portugal es el equipo con mayor tasa de tarjetas rojas de Europa, con 0,213 expulsiones por partido (una expulsión cada 4,7 encuentros). Lo siguen Vitoria Setubal (0,188) y Sevilla (0,182).",
        "tipo_grafico_default": "barh",
        "sql_builder": lambda params: f"""
SELECT e.nombre_equipo                  AS equipo,
       COUNT(p.rojas)                      AS partidos_con_dato,
       ROUND(AVG(p.rojas), 3)              AS rojas_x_partido,
       ROUND(AVG(p.amarillas), 2)          AS amarillas_x_partido
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
GROUP BY e.id_equipo, e.nombre_equipo
HAVING partidos_con_dato >= {params.get("min_partidos", 200)}
ORDER BY {params.get("orden", "rojas_x_partido")} DESC
LIMIT {params.get("limit", 15)};
"""
    },
    {
        "id": 12,
        "titulo": "¿Qué países tienen equipos con mayor Elo?",
        "ejemplo": "Temporada 2025-2026",
        "indicadores": "Nivel de Elo — Perspectivas: País, Equipo, Tiempo",
        "descripcion": "Determina la cúspide de la jerarquía futbolística continental comparando el puntaje máximo y promedio de los clubes de cada nación.",
        "conclusion_oficial": "Inglaterra encabeza la jerarquía europea de la temporada 2025-2026 gracias al Arsenal (2.029 puntos de Elo), seguida de España (Real Madrid, 2.011), Francia (PSG, 1.995), Alemania (Bayern Munich, 1.984) e Italia (Inter, 1.977).",
        "tipo_grafico_default": "bar",
        "sql_builder": lambda params: f"""
WITH por_equipo AS (
    SELECT pa.id_pais, pa.nombre_pais, e.nombre_equipo, MAX(p.elo) AS elo_max,
           ROW_NUMBER() OVER (PARTITION BY pa.id_pais ORDER BY MAX(p.elo) DESC) AS rn
    FROM V_PARTICIPACION p
    JOIN DIM_PAIS pa   ON pa.id_pais = p.id_pais
    JOIN DIM_EQUIPO e  ON e.id_equipo = p.id_equipo
    JOIN DIM_TIEMPO t  ON t.id_tiempo = p.id_tiempo
    WHERE t.temporada = '{params.get("temporada", "2025-2026")}' AND p.elo IS NOT NULL
    GROUP BY pa.id_pais, pa.nombre_pais, e.id_equipo, e.nombre_equipo
)
SELECT nombre_pais                                  AS pais,
       COUNT(*)                                     AS equipos_con_elo,
       ROUND(AVG(elo_max), 1)                       AS elo_promedio_equipos,
       ROUND(MAX(elo_max), 1)                       AS elo_maximo,
       MAX(CASE WHEN rn = 1 THEN nombre_equipo END) AS mejor_equipo
FROM por_equipo
GROUP BY id_pais, nombre_pais
ORDER BY {params.get("orden", "elo_maximo")} DESC;
"""
    },
]

# Las 6 preguntas de negocio oficiales elegidas para la Entrega Final y Exposición
PREGUNTAS_OFICIALES = [p for p in PREGUNTAS_CATALOGO if p["id"] <= 6]

# Preguntas complementarias (7 a 12) disponibles por si el docente las solicita en la defensa
PREGUNTAS_COMPLEMENTARIAS = [p for p in PREGUNTAS_CATALOGO if p["id"] > 6]

