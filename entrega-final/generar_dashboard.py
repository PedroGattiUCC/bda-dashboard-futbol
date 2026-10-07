"""Genera dashboard.md: cada pregunta de negocio del Paso 1 con su consulta SQL
(sobre el modelo estrella), el resultado real y su gráfico.

Uso (después de ejecutar 01_carga_dw.ipynb en paso-4):
  $env:MYSQL_PASSWORD="..."   (o set MYSQL_PASSWORD=... en cmd)
  python generar_dashboard.py
"""
import os
import re
import sys
from decimal import Decimal
from pathlib import Path

import matplotlib
import mysql.connector

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(__file__).resolve().parent
DB = "dw_competencia_futbol"
GRAFICOS = BASE / "graficos"
SALIDA = BASE / "dashboard.md"
VISTA_SQL = BASE / "sql" / "07_vista_dashboard.sql"


def conectar(database=None):
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=database,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
    )


def sentencias(ruta):
    """Divide un archivo SQL en sentencias. Devuelve (titulo_chequeo, sql)."""
    texto = Path(ruta).read_text(encoding="utf-8")
    for bloque in re.split(r";[ \t]*(?:\r?\n|$)", texto):
        titulo = None
        lineas = []
        for linea in bloque.splitlines():
            marca = re.match(r"\s*--\s*@chequeo:\s*(.+)", linea)
            if marca:
                titulo = marca.group(1).strip()
            elif not linea.strip().startswith("--"):
                lineas.append(linea)
        sql = "\n".join(lineas).strip()
        if sql:
            yield titulo, sql

# Paleta de referencia (categórica en orden fijo + tintas neutras)
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA_2, MUTED, GRILLA, EJE, FONDO = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"

HACE_5_ANIOS = "(SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL 5 YEAR"
HACE_3_ANIOS = "(SELECT MAX(fecha) FROM DIM_TIEMPO) - INTERVAL 3 YEAR"

PREGUNTAS = [
    {
        "n": 1,
        "titulo": "¿Cuánto mejoró un equipo específico en 5 años? (ejemplo: Nottingham Forest)",
        "indicadores": "Evolución de Elo — Perspectivas: Equipo, Tiempo",
        "consultas": [
            f"""SELECT t.anio,
       ROUND(AVG(p.elo), 1) AS elo_promedio,
       ROUND(MIN(p.elo), 1) AS elo_minimo,
       ROUND(MAX(p.elo), 1) AS elo_maximo,
       COUNT(*)             AS partidos
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
JOIN DIM_TIEMPO t ON t.id_tiempo = p.id_tiempo
WHERE e.nombre_equipo = 'Nottm Forest'
  AND p.elo IS NOT NULL
  AND t.fecha >= {HACE_5_ANIOS}
GROUP BY t.anio
ORDER BY t.anio""",
            f"""WITH v AS (
    SELECT t.fecha, p.elo
    FROM V_PARTICIPACION p
    JOIN DIM_EQUIPO e ON e.id_equipo = p.id_equipo
    JOIN DIM_TIEMPO t ON t.id_tiempo = p.id_tiempo
    WHERE e.nombre_equipo = 'Nottm Forest'
      AND p.elo IS NOT NULL
      AND t.fecha >= {HACE_5_ANIOS}
), extremos AS (SELECT MIN(fecha) AS f0, MAX(fecha) AS f1 FROM v)
SELECT i.fecha AS fecha_inicial, i.elo AS elo_inicial,
       f.fecha AS fecha_final,   f.elo AS elo_final,
       ROUND(f.elo - i.elo, 1)               AS variacion,
       ROUND(100 * (f.elo - i.elo) / i.elo, 1) AS pct_crecimiento
FROM extremos x
JOIN v i ON i.fecha = x.f0
JOIN v f ON f.fecha = x.f1""",
        ],
        "grafico": {"tipo": "linea", "x": "anio", "y": "elo_promedio",
                    "titulo": "Nottingham Forest: Elo promedio por año", "ylabel": "Elo promedio"},
    },
    {
        "n": 2,
        "titulo": "¿Qué equipo tiende a ganar más contra otro según su historial? (clásicos)",
        "indicadores": "% de victorias en enfrentamientos directos — Perspectivas: Equipo, Rival",
        "consultas": [
            """WITH clasicos AS (
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
       ROUND(100 * SUM(p.victoria) / COUNT(*), 1)   AS pct_gana_a,
       ROUND(100 * SUM(p.empate) / COUNT(*), 1)     AS pct_empate,
       ROUND(100 * SUM(p.derrota) / COUNT(*), 1)    AS pct_gana_b
FROM clasicos c
JOIN DIM_EQUIPO ea ON ea.nombre_equipo = c.equipo_a
JOIN DIM_EQUIPO eb ON eb.nombre_equipo = c.equipo_b
JOIN V_PARTICIPACION p ON p.id_equipo = ea.id_equipo AND p.id_rival = eb.id_equipo
GROUP BY c.equipo_a, c.equipo_b
ORDER BY partidos DESC""",
        ],
        "grafico": {"tipo": "apilado", "x": "clasico", "y": ["pct_gana_a", "pct_empate", "pct_gana_b"],
                    "leyenda": ["Gana el primero", "Empate", "Gana el segundo"],
                    "titulo": "Resultados de los clásicos (% de partidos)", "xlabel": "% de partidos"},
    },
    {
        "n": 3,
        "titulo": "¿Existe ventaja de local?",
        "indicadores": "Ventaja de localía, Promedio de goles a favor / en contra — Perspectivas: División",
        "consultas": [
            """SELECT COUNT(*)                                   AS partidos,
       ROUND(100 * AVG(victoria_local), 1)        AS pct_gana_local,
       ROUND(100 * AVG(empate), 1)                AS pct_empate,
       ROUND(100 * AVG(victoria_visitante), 1)    AS pct_gana_visitante,
       ROUND(AVG(goles_local), 2)                 AS goles_local_prom,
       ROUND(AVG(goles_visitante), 2)             AS goles_visitante_prom
FROM FACT_COMPETENCIA""",
            """SELECT CONCAT(d.codigo_division, ' - ', d.nombre_liga)                     AS liga,
       COUNT(*)                                                              AS partidos,
       ROUND(100 * AVG(f.victoria_local), 1)                                 AS pct_local,
       ROUND(100 * AVG(f.victoria_visitante), 1)                             AS pct_visitante,
       ROUND(100 * (AVG(f.victoria_local) - AVG(f.victoria_visitante)), 1)  AS ventaja_pp,
       ROUND(AVG(f.goles_local) - AVG(f.goles_visitante), 2)                 AS dif_goles
FROM FACT_COMPETENCIA f
JOIN DIM_DIVISION d ON d.id_division = f.id_division
GROUP BY d.id_division, d.codigo_division, d.nombre_liga
ORDER BY ventaja_pp DESC""",
        ],
        "grafico": {"consulta": 1, "tipo": "barh", "x": "liga", "y": "ventaja_pp",
                    "titulo": "Ventaja de localía por liga (% victorias local − % victorias visitante)",
                    "xlabel": "puntos porcentuales"},
        "filas_max": 40,
    },
    {
        "n": 4,
        "titulo": "¿Qué liga es más pareja?",
        "indicadores": "Paridad de la liga — Perspectivas: División, Tiempo",
        "consultas": [
            """SELECT CONCAT(d.codigo_division, ' - ', d.nombre_liga)            AS liga,
       COUNT(*)                                                     AS partidos,
       SUM(f.elo_local IS NOT NULL AND f.elo_visitante IS NOT NULL) AS partidos_con_elo,
       ROUND(STDDEV_SAMP(f.elo_local - f.elo_visitante), 1)         AS desvio_brecha_elo,
       ROUND(AVG(ABS(f.elo_local - f.elo_visitante)), 1)            AS brecha_elo_media,
       ROUND(100 * AVG(f.empate), 1)                                AS pct_empates
FROM FACT_COMPETENCIA f
JOIN DIM_DIVISION d ON d.id_division = f.id_division
GROUP BY d.id_division, d.codigo_division, d.nombre_liga
HAVING partidos_con_elo >= 0.8 * partidos
ORDER BY desvio_brecha_elo""",
        ],
        "grafico": {"tipo": "barh", "x": "liga", "y": "desvio_brecha_elo",
                    "titulo": "Paridad: desvío de la brecha de Elo entre rivales (menor = más pareja)",
                    "xlabel": "desvío estándar de (Elo local − Elo visitante)"},
        "nota": "Solo ligas con Elo en al menos el 80 % de sus partidos (en el resto el indicador no es representativo).",
        "filas_max": 40,
    },
    {
        "n": 5,
        "titulo": "¿Qué liga acumula más tarjetas?",
        "indicadores": "Promedio de tarjetas amarillas y rojas — Perspectivas: División, País",
        "consultas": [
            """SELECT CONCAT(d.codigo_division, ' - ', d.nombre_liga)            AS liga,
       pa.nombre_pais                                               AS pais,
       COUNT(f.amarillas_local)                                     AS partidos_con_dato,
       ROUND(AVG(f.amarillas_local + f.amarillas_visitante), 2)     AS amarillas_x_partido,
       ROUND(AVG(f.rojas_local + f.rojas_visitante), 3)             AS rojas_x_partido
FROM FACT_COMPETENCIA f
JOIN DIM_DIVISION d ON d.id_division = f.id_division
JOIN DIM_PAIS pa    ON pa.id_pais = f.id_pais
GROUP BY d.id_division, d.codigo_division, d.nombre_liga, pa.nombre_pais
HAVING partidos_con_dato >= 1000
ORDER BY amarillas_x_partido DESC""",
        ],
        "grafico": {"tipo": "barh", "x": "liga", "y": "amarillas_x_partido",
                    "titulo": "Tarjetas amarillas por partido, por liga", "xlabel": "amarillas por partido"},
        "nota": "Solo partidos con dato de tarjetas (las ligas sin ese dato no se promedian como 0).",
        "filas_max": 40,
    },
    {
        "n": 6,
        "titulo": "¿Qué equipos tienen mejor estadística de visitante? (últimos 5 años)",
        "indicadores": "% de victorias y Promedio de goles a favor como visitante — Perspectivas: Equipo, División",
        "consultas": [
            f"""SELECT e.nombre_equipo                        AS equipo,
       GROUP_CONCAT(DISTINCT d.codigo_division)  AS divisiones,
       COUNT(*)                                  AS partidos_visitante,
       ROUND(100 * AVG(p.victoria), 1)           AS pct_victorias,
       ROUND(AVG(p.goles_favor), 2)              AS goles_favor_prom,
       ROUND(AVG(p.goles_contra), 2)             AS goles_contra_prom
FROM V_PARTICIPACION p
JOIN DIM_EQUIPO e   ON e.id_equipo = p.id_equipo
JOIN DIM_DIVISION d ON d.id_division = p.id_division
JOIN DIM_TIEMPO t   ON t.id_tiempo = p.id_tiempo
WHERE p.condicion = 'Visitante'
  AND t.fecha >= {HACE_5_ANIOS}
GROUP BY e.id_equipo, e.nombre_equipo
HAVING partidos_visitante >= 60
ORDER BY pct_victorias DESC
LIMIT 15""",
        ],
        "grafico": {"tipo": "barh", "x": "equipo", "y": "pct_victorias",
                    "titulo": "Top 15 visitantes: % de victorias fuera de casa (últimos 5 años)",
                    "xlabel": "% de victorias como visitante"},
    },
]

# Respuesta escrita a partir de los resultados de la carga del 2026-09-03.
# Si se recarga con otra versión del archivo, revisar que sigan siendo válidas.
RESPUESTAS = {
    1: "Nottingham Forest pasó de 1466 puntos de Elo (septiembre de 2021, en Championship) a 1780 (agosto de 2026): "
       "+314 puntos, un 21,4 % de crecimiento. El mayor salto fue entre 2024 y 2025.",
    2: "Arsenal domina a Tottenham (gana el 47 % contra el 20 %) y Sevilla a Betis (43 % vs 18 %); Celtic a Rangers "
       "(47 % vs 31 %), Man United a Liverpool (44 % vs 35 %) e Inter a Milan (44 % vs 36 %). En el clásico español "
       "gana más Barcelona (46 % vs 33 %).",
    3: "Sí. En total el local gana el 45,0 % de los partidos contra el 28,1 % del visitante (+16,9 puntos porcentuales) "
       "y convierte 1,50 goles contra 1,14. La ventaja es mayor en La Liga (19,5 pp) y menor en la Premiership escocesa (10,6 pp).",
    4: "Las segundas divisiones son las más parejas (Segunda División, Ligue 2 y Serie B: desvío de ~80-85 puntos de Elo "
       "y ~30 % de empates). Entre las primeras divisiones la más pareja es la Ligue 1; las menos parejas son la "
       "Eredivisie, la Premiership escocesa y la Primeira Liga.",
    5: "La Primeira Liga (5,09 amarillas por partido), La Liga (5,02) y la Segunda División española (5,00). "
       "Portugal y España también encabezan las rojas (~0,29 por partido). Las ligas inglesas y la Eredivisie son las que menos acumulan (~3 amarillas).",
    6: "En los últimos 5 años, Porto (gana el 71,8 % de sus partidos como visitante), PSV (70,9 %) y Celtic (70,7 %). "
       "Entre las cinco grandes ligas, Bayern Munich (65,5 %), Paris SG y Barcelona.",
}

def fmt(v):
    if v is None:
        return "—"
    if isinstance(v, Decimal):
        return f"{v.normalize():f}" if v == v.to_integral() else str(v)
    return str(v)


def tabla_md(cols, filas, maximo):
    lineas = ["| " + " | ".join(cols) + " |", "|" + "|".join(" --- " for _ in cols) + "|"]
    for f in filas[:maximo]:
        lineas.append("| " + " | ".join(fmt(v).replace("|", "/") for v in f) + " |")
    if len(filas) > maximo:
        lineas.append(f"\n*({len(filas) - maximo} filas más no mostradas)*")
    return "\n".join(lineas)


def estilo(ax, titulo):
    ax.set_facecolor(FONDO)
    ax.figure.set_facecolor(FONDO)
    ax.set_title(titulo, loc="left", color=TINTA, fontsize=11, pad=12)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(EJE)
    ax.tick_params(colors=TINTA_2, labelsize=8.5, length=0)
    ax.grid(axis="x", color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)


def graficar(spec, cols, filas, ruta):
    datos = {c: [r[i] for r in filas] for i, c in enumerate(cols)}
    tipo = spec["tipo"]
    alto = max(3.2, 0.32 * len(filas) + 1.4) if tipo != "linea" else 3.6
    fig, ax = plt.subplots(figsize=(8.5, alto), dpi=130)
    estilo(ax, spec["titulo"])
    if tipo == "linea":
        x = [int(v) for v in datos[spec["x"]]]
        y = [float(v) for v in datos[spec["y"]]]
        ax.plot(x, y, color=AZUL, linewidth=2, marker="o", markersize=5)
        for xi, yi in zip(x, y):
            ax.annotate(f"{yi:.0f}", (xi, yi), textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=8, color=TINTA_2)
        ax.set_xticks(x)
        ax.set_ylabel(spec["ylabel"], color=MUTED, fontsize=9)
        ax.grid(axis="y", color=GRILLA, linewidth=0.8)
        ax.grid(axis="x", visible=False)
        ax.spines["left"].set_visible(False)
        ax.margins(y=0.2)
    elif tipo == "apilado":
        etiquetas = list(reversed(datos[spec["x"]]))
        izquierda = [0.0] * len(etiquetas)
        for serie, nombre, color in zip(spec["y"], spec["leyenda"], [AZUL, MUTED, NARANJA]):
            valores = [float(v) for v in reversed(datos[serie])]
            barras = ax.barh(etiquetas, valores, left=izquierda, color=color, height=0.6,
                             edgecolor=FONDO, linewidth=2, label=nombre)
            ax.bar_label(barras, labels=[f"{v:.0f}%" for v in valores], label_type="center",
                         fontsize=8, color="white")
            izquierda = [a + b for a, b in zip(izquierda, valores)]
        ax.set_xlim(0, 100)
        ax.set_xlabel(spec["xlabel"], color=MUTED, fontsize=9)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
                  fontsize=8.5, labelcolor=TINTA_2, bbox_transform=ax.transAxes)
        ax.set_title(spec["titulo"], loc="left", color=TINTA, fontsize=11, pad=28)
    elif tipo == "barh":
        etiquetas = list(reversed([str(v) for v in datos[spec["x"]]]))
        valores = list(reversed([float(v) for v in datos[spec["y"]]]))
        barras = ax.barh(etiquetas, valores, color=AZUL, height=0.65)
        ax.bar_label(barras, labels=[fmt(Decimal(str(v))) for v in valores], padding=3,
                     fontsize=7.5, color=TINTA_2)
        ax.axvline(0, color=EJE, linewidth=1)
        ax.set_xlabel(spec["xlabel"], color=MUTED, fontsize=9)
        ax.margins(x=0.12, y=0.01)
    elif tipo == "punto":
        etiquetas = list(reversed([str(v) for v in datos[spec["x"]]]))
        valores = list(reversed([float(v) for v in datos[spec["y"]]]))
        ax.hlines(etiquetas, min(valores) - 50, valores, color=GRILLA, linewidth=1.5)
        ax.plot(valores, etiquetas, "o", color=AZUL, markersize=7)
        for v, e in zip(valores, etiquetas):
            ax.annotate(f"{v:.0f}", (v, e), textcoords="offset points", xytext=(8, -3),
                        fontsize=7.5, color=TINTA_2)
        ax.set_xlabel(spec["xlabel"], color=MUTED, fontsize=9)
        ax.margins(x=0.08)
    fig.tight_layout()
    fig.savefig(ruta, facecolor=FONDO)
    plt.close(fig)


def main():
    GRAFICOS.mkdir(exist_ok=True)
    cnx = conectar(DB)
    cur = cnx.cursor()
    for _, sql in sentencias(VISTA_SQL):
        cur.execute(sql)
    cnx.commit()

    md = [
        "# Dashboard — Competencia entre Equipos",
        "",
        "Cada pregunta de negocio del Paso 1 se responde con una consulta SQL sobre el modelo estrella "
        "`dw_competencia_futbol` (`FACT_COMPETENCIA` + dimensiones), nunca sobre el archivo original. "
        "Los resultados y gráficos se generan con `generar_dashboard.py`.",
        "",
        "Para los indicadores \"por equipo\" se usa la vista `V_PARTICIPACION` (`sql/07_vista_dashboard.sql`), "
        "construida solo con `FACT_COMPETENCIA`: presenta cada partido dos veces, una desde el punto de vista "
        "de cada equipo, para no repetir el `CASE` local/visitante en todas las consultas.",
        "",
        "Alcance: 15 ligas europeas de 10 países (E0, E1, SP1, SP2, I1, I2, D1, D2, F1, F2, N1, P1, B1, T1, SC0), "
        "todas con temporada de julio a junio y datos de 2000 a 2026. Las ventanas \"últimos N años\" se calculan "
        "desde la última fecha cargada en `DIM_TIEMPO` (2026-09-03).",
        "",
    ]
    for p in PREGUNTAS:
        md += [f"## {p['n']}. {p['titulo']}", "", f"**Indicadores:** {p['indicadores']}", ""]
        if p.get("nota"):
            md += [f"> {p['nota']}", ""]
        resultados = []
        for i, sql in enumerate(p["consultas"]):
            cur.execute(sql)
            cols, filas = list(cur.column_names), cur.fetchall()
            resultados.append((cols, filas))
            if len(p["consultas"]) > 1:
                md += [f"**Consulta {i + 1}:**", ""]
            md += ["```sql", sql, "```", "", "**Resultado:**", "",
                   tabla_md(cols, filas, p.get("filas_max", 20)), ""]
        spec = p["grafico"]
        cols, filas = resultados[spec.get("consulta", 0)]
        ruta = GRAFICOS / f"pregunta_{p['n']:02d}.png"
        graficar(spec, cols, filas, ruta)
        md += [f"![{spec['titulo']}](graficos/{ruta.name})", "",
               f"**Respuesta:** {RESPUESTAS[p['n']]}", "", "---", ""]
        print(f"Pregunta {p['n']}: {len(filas)} filas, gráfico {ruta.name}")
    cur.close()
    cnx.close()
    SALIDA.write_text("\n".join(md), encoding="utf-8")
    print(f"Generado {SALIDA}")


if __name__ == "__main__":
    main()
