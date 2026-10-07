# Graph Report - PROYECTO BDA  (2026-10-04)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 24 nodes · 44 edges · 6 communities (3 shown, 3 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- entrega-final/generar_dashboard.py
- log
- cargar_dw.py
- verificacion_nombres_equipos.py
- comparar_con_archivo
- sentencias

## God Nodes (most connected - your core abstractions)
1. `log()` - 7 edges
2. `main()` - 7 edges
3. `main()` - 5 edges
4. `ejecutar_archivo()` - 5 edges
5. `imprimir_tabla()` - 5 edges
6. `comparar_con_archivo()` - 5 edges
7. `graficar()` - 4 edges
8. `volcar_csv()` - 4 edges
9. `sentencias()` - 4 edges
10. `fmt()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `conectar()`  [INFERRED]
  correcciones/entrega-final/generar_dashboard.py → correcciones/paso-4/cargar_dw.py
- `main()` --calls--> `sentencias()`  [INFERRED]
  correcciones/entrega-final/generar_dashboard.py → correcciones/paso-4/cargar_dw.py

## Import Cycles
- None detected.

## Communities (6 total, 3 thin omitted)

### Community 0 - "entrega-final/generar_dashboard.py"
Cohesion: 0.52
Nodes (6): estilo(), fmt(), graficar(), main(), Genera dashboard.md: cada pregunta de negocio del Paso 1 con su consulta SQL…, tabla_md()

### Community 1 - "log"
Cohesion: 0.47
Nodes (6): conectar(), log(), main(), Vuelca el CSV tal cual (todo como texto) en STG_PARTIDOS., volcar_csv(), volcar_mapeos()

### Community 2 - "cargar_dw.py"
Cohesion: 0.60
Nodes (4): ejecutar_archivo(), formatear(), imprimir_tabla(), Paso 4 - Integración de datos: carga completa del Data Mart…

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `sentencias()` connect `sentencias` to `entrega-final/generar_dashboard.py`, `cargar_dw.py`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `comparar_con_archivo()` connect `comparar_con_archivo` to `log`, `cargar_dw.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `volcar_csv()` connect `log` to `cargar_dw.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `conectar()` and `sentencias()`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._