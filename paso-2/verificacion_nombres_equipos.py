"""Paso 2 c) - Verificacion de consistencia de nombres de club entre Matches.csv y EloRatings.csv.

Uso: python verificacion_nombres_equipos.py [ruta/Matches.csv] [ruta/EloRatings.csv] [--todas]
Por defecto analiza solo las 15 ligas del alcance; con --todas analiza el archivo completo.
Solo usa la libreria estandar de Python.
"""
import csv
import sys
from collections import Counter

args = [a for a in sys.argv[1:] if not a.startswith("--")]
matches_path = args[0] if len(args) > 0 else "Matches.csv"
elo_path = args[1] if len(args) > 1 else "EloRatings.csv"
ALCANCE = {"E0", "E1", "SP1", "SP2", "I1", "I2", "D1", "D2", "F1", "F2", "N1", "P1", "B1", "T1", "SC0"}
todas = "--todas" in sys.argv

with open(matches_path, encoding="utf-8") as f:
    partidos = [r for r in csv.DictReader(f) if todas or r["Division"] in ALCANCE]
with open(elo_path, encoding="utf-8") as f:
    elo = list(csv.DictReader(f))

# En algunas versiones del archivo las columnas de EloRatings vienen en minuscula o con distintas cabeceras
col_club = next((c for c in ("Club", "club", "Team", "team", "Name", "name") if c in elo[0]), None)
if not col_club:
    sys.exit(f"Error: No se encontró columna de club en '{elo_path}'. Columnas disponibles: {list(elo[0].keys())}")
clubes_elo = {r[col_club] for r in elo}

apariciones = Counter()
for r in partidos:
    apariciones[r["HomeTeam"]] += 1
    apariciones[r["AwayTeam"]] += 1

equipos = set(apariciones)
coinciden = equipos & clubes_elo
no_coinciden = equipos - clubes_elo
por_espacios = {e for e in no_coinciden if e.strip() in clubes_elo}
resto = no_coinciden - por_espacios
partidos_afectados = sum(
    1 for r in partidos if r["HomeTeam"] not in clubes_elo or r["AwayTeam"] not in clubes_elo
)

print("Alcance:", "archivo completo" if todas else "15 ligas europeas")
print(f"Partidos analizados: {len(partidos)} | Filas EloRatings.csv: {len(elo)}")
print(f"Equipos unicos en Matches.csv: {len(equipos)}")
print(f"Clubes unicos en EloRatings.csv: {len(clubes_elo)}")
print(f"Coinciden exactamente: {len(coinciden)} ({len(coinciden) / len(equipos):.1%})")
print(f"No coinciden: {len(no_coinciden)} ({len(no_coinciden) / len(equipos):.1%})")
print(f"  - por espacios sobrantes (se resuelven con TRIM): {len(por_espacios)}")
print(f"  - resto (escritos distinto o ausentes en EloRatings): {len(resto)}")
print(f"Partidos con al menos un equipo sin coincidencia: {partidos_afectados} "
      f"({partidos_afectados / len(partidos):.1%})")
print("\nResto, ordenado por cantidad de apariciones:")
for e in sorted(resto, key=lambda e: -apariciones[e]):
    print(f"  {e!r}: {apariciones[e]}")
