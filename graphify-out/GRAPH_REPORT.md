# Graph Report - PROYECTO BDA  (2026-10-07)

## Corpus Check
- 28 files · ~95,694 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 213 nodes · 209 edges · 22 communities (17 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Paso 4: Integración de datos con Python + Jupyter — explicación para el grupo
- conexion.py
- Manual Integral: Dashboard Dinámico en Render y Clever Cloud MySQL
- Resumen de correcciones, Paso 4 y Entrega Final — para el grupo
- Entrega Final: Dashboard sobre el Modelo Estrella — Guía del Entregable
- b) Tablas de Dimensiones
- generar_dashboard.py
- Paso 3: Modelo Lógico del Data Warehouse — Guía del Entregable
- construir_sqlite
- 7. Estrategia y Guión para la Exposición Oral en Clase (Frente al Docente)
- GUÍA DE TRABAJO PRÁCTICO #2 — DATA WAREHOUSE CON METODOLOGÍA HEFESTO
- Paso 2: Análisis de la Fuente de Datos — Guía del Entregable
- Paso 4: Integración de Datos (Metodología HEFESTO)
- Dashboard — Competencia entre Equipos
- Paso 1: Análisis de Requerimientos — Guía del Entregable
- Paso 4: Integración de Datos (ETL) — Guía del Entregable
- Paso 2: Análisis de la Fuente de Datos (Metodología HEFESTO)
- entrega_requerimientos.md
- rules/graphify.md
- workflows/graphify.md
- fuente.md
- verificacion_nombres_equipos.py

## God Nodes (most connected - your core abstractions)
1. `Manual Integral: Dashboard Dinámico en Render y Clever Cloud MySQL` - 10 edges
2. `Paso 4: Integración de datos con Python + Jupyter — explicación para el grupo` - 10 edges
3. `GUÍA DE TRABAJO PRÁCTICO #2 — DATA WAREHOUSE CON METODOLOGÍA HEFESTO` - 9 edges
4. `5. Notebook 1 — `01_carga_dw.ipynb`, paso por paso` - 8 edges
5. `Paso 4: Integración de Datos (Metodología HEFESTO)` - 8 edges
6. `Resumen de correcciones, Paso 4 y Entrega Final — para el grupo` - 7 edges
7. `Dashboard — Competencia entre Equipos` - 7 edges
8. `ejecutar_consulta()` - 6 edges
9. `7. Estrategia y Guión para la Exposición Oral en Clase (Frente al Docente)` - 6 edges
10. `Paso 3: Modelo Lógico del Data Warehouse — Guía del Entregable` - 6 edges

## Surprising Connections (you probably didn't know these)
- `generar_dump()` --calls--> `construir_sqlite()`  [EXTRACTED]
  entrega-final/dashboard-dinamico/exportar_dump_sql.py → entrega-final/dashboard-dinamico/generar_sqlite_contingencia.py
- `migrar()` --calls--> `construir_sqlite()`  [EXTRACTED]
  entrega-final/dashboard-dinamico/migrar_a_clevercloud.py → entrega-final/dashboard-dinamico/generar_sqlite_contingencia.py

## Import Cycles
- None detected.

## Communities (22 total, 5 thin omitted)

### Community 0 - "Paso 4: Integración de datos con Python + Jupyter — explicación para el grupo"
Cohesion: 0.07
Nodes (27): 1. Qué es esto y por qué usamos Python + Jupyter, 2. Organización del Paso 4 (Integración de Datos), 3.1 ¿Qué es Jupyter y qué es un notebook?, 3.2 Python comparado con C++, 3.3 pandas: trabajar con tablas, 3.4 Las otras librerías, 3. Conceptos básicos (lo mínimo para entender los notebooks), 4.1 Requisitos (+19 more)

### Community 1 - "conexion.py"
Cohesion: 0.11
Nodes (17): Tablero Analítico Dinámico — Data Mart de Competencia de Fútbol (HEFESTO v2)…, _adaptar_sql_para_sqlite(), crear_engine_mysql(), ejecutar_consulta(), obtener_config_por_defecto(), preparar_conexion_sqlite(), probar_conexion(), Gestor de conexiones resiliente a bases de datos: - Clever Cloud MySQL (Remoto… (+9 more)

### Community 2 - "Manual Integral: Dashboard Dinámico en Render y Clever Cloud MySQL"
Cohesion: 0.11
Nodes (19): 1. Contexto y Objetivo de esta Implementación Dinámica, 2. Arquitectura de la Solución en la Nube, 3. Inventario de Archivos en `dashboard-dinamico/`, 4. Guía Paso a Paso: Configurar Clever Cloud (MySQL en la Nube), 5. Guía Paso a Paso: Desplegar el Dashboard en Render, 6. Cómo Ejecutarlo en Local (En tu Computadora), 8. Resumen de Respuestas Clave ante Posibles Preguntas del Profesor, Componentes y sus roles: (+11 more)

### Community 3 - "Resumen de correcciones, Paso 4 y Entrega Final — para el grupo"
Cohesion: 0.12
Nodes (16): 1. ¿Por qué existen dos archivos en la fuente?, 1. Separación Estricta de Entregables: Paso 4 vs. Entrega Final, 2. Qué pasó con el archivo `EloRatings.csv` y cómo explicarlo, 2. ¿Qué se creía al principio?, 3. Decisiones clave que cambian y ordenan el trabajo, 3. ¿Qué descubrimos al auditar los datos reales? (Pedido de corrección P2), 4. ¿Cuál fue su uso real en el proyecto?, 4. Estado de los 4 Pasos de Hefesto v2 (+8 more)

### Community 4 - "Entrega Final: Dashboard sobre el Modelo Estrella — Guía del Entregable"
Cohesion: 0.14
Nodes (11): 📁 Archivos de esta Carpeta, Dashboard Dinámico para la Exposición Final en Clase, 📚 Documentación Completa para la Defensa, ⚡ Inicio Rápido (En 2 Minutos), Opción 1: Ejecución Local en tu Computadora, Opción 2: Despliegue en la Nube (Clever Cloud + Render), 1. Objetivo Metodológico de la Entrega Final, 2. Inventario y Función de Archivos (+3 more)

### Community 5 - "b) Tablas de Dimensiones"
Cohesion: 0.17
Nodes (11): 1\. Dimensión: `DIM_TIEMPO`, 2\. Dimensión: `DIM_EQUIPO`, 3\. Dimensión: `DIM_DIVISION`, 4\. Dimensión: `DIM_PAIS`, a) Tipo de Modelo Lógico del DW, b) Tablas de Dimensiones, c) Tablas de Hechos, d) Uniones (Diagrama del Modelo Lógico Final) (+3 more)

### Community 6 - "generar_dashboard.py"
Cohesion: 0.36
Nodes (9): conectar(), estilo(), fmt(), graficar(), main(), Genera dashboard.md: cada pregunta de negocio del Paso 1 con su consulta SQL…, Divide un archivo SQL en sentencias. Devuelve (titulo_chequeo, sql)., sentencias() (+1 more)

### Community 7 - "Paso 3: Modelo Lógico del Data Warehouse — Guía del Entregable"
Cohesion: 0.20
Nodes (9): 1. Objetivo Metodológico del Paso 3, 1. ¿Por qué se eligió un Esquema en Estrella (Star Schema)?, 2. Dimensión con Roles (*Role-Playing Dimension*): `DIM_EQUIPO`, 2. Inventario y Función de Archivos, 3. Clave Primaria Compuesta en `FACT_COMPETENCIA`, 3. Decisiones de Modelado y Justificación Técnica, 4. Estructura de Tablas del Data Warehouse, 5. Verificación del DDL (+1 more)

### Community 8 - "construir_sqlite"
Cohesion: 0.28
Nodes (6): generar_dump(), Exporta el Data Mart completo a un script SQL autónomo…, construir_sqlite(), Genera una base SQLite de contingencia (dw_contingencia.sqlite) a partir de los…, migrar(), Script de migración automatizado hacia Clever Cloud MySQL (o cualquier MySQL…

### Community 9 - "7. Estrategia y Guión para la Exposición Oral en Clase (Frente al Docente)"
Cohesion: 0.22
Nodes (9): 7. Estrategia y Guión para la Exposición Oral en Clase (Frente al Docente), Caso A: Pregunta 1 (Evolución de Elo — Nottingham Forest), Caso B: Pregunta 2 (Historial de Clásicos), Caso C: Pregunta 3 a 12, 💻 Consola SQL en Vivo: Para Preguntas Sorpresa del Docente, 📊 Demostración de las Preguntas Oficiales (Minutos 2 a 5), 🚀 El "Momento Decisivo": Modificación de Consultas SQL en Vivo, 🎤 Introducción (Minuto 0 a 1): Puesta en Contexto (+1 more)

### Community 10 - "GUÍA DE TRABAJO PRÁCTICO #2 — DATA WAREHOUSE CON METODOLOGÍA HEFESTO"
Cohesion: 0.20
Nodes (9): Consigna 1: Paso 1 — Análisis de Requerimientos, Consigna 2: Paso 2 — Análisis de la fuente de datos, Consigna 3: Paso 3 — Modelo Lógico del DW, Consigna 4: Paso 4 — Integración de Datos, De qué se trata este TP, Elección del tema y del archivo de datos, Entrega final: Dashboard sobre el modelo estrella, GUÍA DE TRABAJO PRÁCTICO #2 — DATA WAREHOUSE CON METODOLOGÍA HEFESTO (+1 more)

### Community 11 - "Paso 2: Análisis de la Fuente de Datos — Guía del Entregable"
Cohesion: 0.22
Nodes (8): 1. Objetivo Metodológico del Paso 2, 2. Inventario y Función de Archivos, 3. Aspectos Clave a Defender ante el Profesor, 4. Cómo ejecutar el script de verificación, A. ¿Qué pasó con `EloRatings.csv` y qué uso se le dio?, B. Corrección del Perfil de Datos (48 columnas reales), C. Tratamiento de Valores Nulos en Tarjetas, Paso 2: Análisis de la Fuente de Datos — Guía del Entregable

### Community 12 - "Paso 4: Integración de Datos (Metodología HEFESTO)"
Cohesion: 0.22
Nodes (8): 1. Organización del flujo ETL y orden de ejecución, 2. Volcado en un área intermedia (staging), 3. Calidad de datos: qué se encontró y cómo se resolvió, 4. Carga de las dimensiones, 5. Carga de la tabla de hechos, 6. Verificación de la carga, 7. Política de actualización, Paso 4: Integración de Datos (Metodología HEFESTO)

### Community 13 - "Dashboard — Competencia entre Equipos"
Cohesion: 0.25
Nodes (7): 1. ¿Cuánto mejoró un equipo específico en 5 años? (ejemplo: Nottingham Forest), 2. ¿Qué equipo tiende a ganar más contra otro según su historial? (clásicos), 3. ¿Existe ventaja de local?, 4. ¿Qué liga es más pareja?, 5. ¿Qué liga acumula más tarjetas?, 6. ¿Qué equipos tienen mejor estadística de visitante? (últimos 5 años), Dashboard — Competencia entre Equipos

### Community 14 - "Paso 1: Análisis de Requerimientos — Guía del Entregable"
Cohesion: 0.33
Nodes (5): 1. Objetivo Metodológico del Paso 1, 2. Inventario y Función de Archivos, 3. Estructura de `entrega_requerimientos.md`, 4. Preguntas Frecuentes para la Defensa, Paso 1: Análisis de Requerimientos — Guía del Entregable

### Community 15 - "Paso 4: Integración de Datos (ETL) — Guía del Entregable"
Cohesion: 0.33
Nodes (5): 1. Objetivo Metodológico del Paso 4, 2. Inventario y Función de Archivos, 3. Instrucciones de Ejecución del ETL (Python + Jupyter), 4. Resultados de Verificación y Balance, Paso 4: Integración de Datos (ETL) — Guía del Entregable

### Community 16 - "Paso 2: Análisis de la Fuente de Datos (Metodología HEFESTO)"
Cohesion: 0.50
Nodes (3): Paso 2: Análisis de la Fuente de Datos (Metodología HEFESTO), **TABLA 1 - Archivo Auxiliar de Control: `EloRatings.csv`**, **TABLA 2 - Archivo Principal de Partidos: `Matches.csv` (48 columnas reales)**

## Knowledge Gaps
- **117 isolated node(s):** `graphify`, `Workflow: graphify`, `A) Paso 4 — Integración de Datos (ETL)`, `B) Entrega Final — Dashboard sobre el modelo estrella`, `1. ¿Por qué existen dos archivos en la fuente?` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 152 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Manual Integral: Dashboard Dinámico en Render y Clever Cloud MySQL` connect `Manual Integral: Dashboard Dinámico en Render y Clever Cloud MySQL` to `7. Estrategia y Guión para la Exposición Oral en Clase (Frente al Docente)`, `Entrega Final: Dashboard sobre el Modelo Estrella — Guía del Entregable`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `7. Estrategia y Guión para la Exposición Oral en Clase (Frente al Docente)` connect `7. Estrategia y Guión para la Exposición Oral en Clase (Frente al Docente)` to `Manual Integral: Dashboard Dinámico en Render y Clever Cloud MySQL`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **What connects `graphify`, `Workflow: graphify`, `A) Paso 4 — Integración de Datos (ETL)` to the rest of the system?**
  _117 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Paso 4: Integración de datos con Python + Jupyter — explicación para el grupo` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._
- **Should `conexion.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11462450592885376 - nodes in this community are weakly interconnected._
- **Should `Manual Integral: Dashboard Dinámico en Render y Clever Cloud MySQL` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `Resumen de correcciones, Paso 4 y Entrega Final — para el grupo` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._