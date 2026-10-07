# Paso 1: Análisis de Requerimientos — Guía del Entregable

Este directorio contiene los archivos correspondientes a la **Consigna 1: Paso 1 — Análisis de Requerimientos** de la Metodología HEFESTO v2.

---

## 1. Objetivo Metodológico del Paso 1

El propósito de este primer hito es establecer el punto de partida del Data Warehouse:
1. **Identificar y formalizar el proceso de negocio:** Delimitar el fenómeno transaccional atómico que se produce de forma repetitiva y genera registros cuantificables. En este proyecto: la **Competencia entre Equipos** de fútbol (cada partido jugado).
2. **Formular preguntas de negocio:** Plantear preguntas de análisis complejas orientadas a la toma de decisiones estratégicas (en nuestro caso, evaluación de rendimiento para potenciales sponsors o inversores deportivos).
3. **Identificar perspectivas e indicadores:** Descomponer conceptualmente cada pregunta en qué se quiere medir (indicadores numéricos) y bajo qué ejes de análisis (perspectivas). **En este paso los indicadores no llevan fórmulas matemáticas**, solo su nombre conceptual.
4. **Construir el Modelo Conceptual:** Graficar el diagrama conceptual estándar con las perspectivas a la izquierda, el proceso de negocio en el centro y los indicadores a la derecha.

---

## 2. Inventario y Función de Archivos

| Archivo | Tipo | Descripción y Función |
| :--- | :--- | :--- |
| **`entrega_requerimientos.md`** | **Documento Principal de Entrega** | Contiene el informe formal del Paso 1 con la presentación del tema, las 12 preguntas de negocio formuladas, la matriz de indicadores y perspectivas por pregunta, y el diagrama conceptual en sintaxis Mermaid (`graph LR`). |
| **`README.md`** | **Guía Explicativa Interna** | Este archivo: resume el propósito metodológico del paso, explica la estructura interna y brinda pautas para la defensa ante la cátedra. |

---

## 3. Estructura de `entrega_requerimientos.md`

El documento de entrega se divide en cuatro partes esenciales:

1. **Presentación del proceso de negocio y dataset:**
   * Proceso de negocio: **Competencia entre Equipos**.
   * Fuente elegida: Dataset histórico de fútbol europeo (Kaggle).
   * **Alcance del análisis:** Se delimita a **15 ligas europeas de 10 países** (Inglaterra E0/E1, España SP1/SP2, Italia I1/I2, Alemania D1/D2, Francia F1/F2, Países Bajos N1, Portugal P1, Bélgica B1, Turquía T1 y Escocia SC0). Esta decisión asegura homogeneidad en calendarios (julio a junio) y cobertura continua de puntuación Elo desde el año 2000 al 2026.
2. **Preguntas de negocio (12 preguntas):**
   * Supera ampliamente el mínimo de 5 preguntas complejas exigidas por la consigna.
   * Abarcan temáticas de evolución histórica (Preguntas 1 y 10), rivalidad directa (Pregunta 2), ventaja de localía (Pregunta 3), paridad competitiva (Pregunta 4), disciplina y fair play (Preguntas 5 y 11), rendimiento de visitante (Pregunta 6), efectividad general (Pregunta 7), atractivo ofensivo (Pregunta 8), consistencia divisional (Pregunta 9) y jerarquía por países (Pregunta 12).
3. **Indicadores y perspectivas por pregunta:**
   * **Perspectivas identificadas:** `EQUIPO`, `RIVAL`, `DIVISION`, `PAIS` y `TIEMPO`.
   * **Indicadores conceptuales:** `Evolución de Elo`, `Nivel de Elo`, `Consistencia del equipo`, `Puntos obtenidos`, `Paridad de la liga`, `Promedio de goles a favor`, `Promedio de goles en contra`, `% de victorias`, `% de victorias en enfrentamientos directos`, `Ventaja de localía`, `Promedio de tarjetas amarillas` y `Promedio de tarjetas rojas`.
4. **Modelo Conceptual:**
   * Diagrama Mermaid (`graph LR`) con flujo horizontal: Perspectivas $\rightarrow$ Proceso Central (`COMPETENCIA ENTRE EQUIPOS`) $\rightarrow$ Indicadores.

---

## 4. Preguntas Frecuentes para la Defensa

* **¿Por qué el nodo central se llama "COMPETENCIA ENTRE EQUIPOS" y no "Rendimiento"?**
  * Porque el rendimiento es una valoración o un indicador, mientras que la metodología exige modelar un **proceso de negocio o evento real**. Lo que realmente ocurre en el mundo real y genera registros son los partidos disputados (la competencia entre dos clubes).
* **¿Por qué en este paso no se definieron las fórmulas matemáticas (`SUM`, `AVG`, etc.)?**
  * Porque el Paso 1 de Hefesto es puramente de análisis de requerimientos con el usuario. Las fórmulas matemáticas y la especificación de funciones de agregación pertenecen al **Paso 2 (Análisis de los OLTP / Fuentes de datos)**, una vez que se confrontan los indicadores con las columnas reales del archivo.
* **¿Por qué `Temporada` no es una perspectiva separada?**
  * Porque la temporada es una jerarquía temporal o atributo derivado de la fecha del partido, por lo que pertenece a la perspectiva **Tiempo**.
