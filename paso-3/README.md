# Paso 3: Modelo Lógico del Data Warehouse — Guía del Entregable

Este directorio contiene los archivos correspondientes a la **Consigna 3: Paso 3 — Modelo Lógico del DW** de la Metodología HEFESTO v2.

---

## 1. Objetivo Metodológico del Paso 3

El propósito de este hito es transformar el Modelo Conceptual Ampliado del Paso 2 en una estructura lógica relacional multidimensional lista para ser implementada en un Sistema Gestor de Bases de Datos (en nuestro caso, MySQL 8.0+):
1. **a) Tipo de Modelo Lógico:** Elegir el tipo de esquema (Estrella, Copo de Nieve o Constelación) y fundamentar sólidamente la elección técnica.
2. **b) Tablas de Dimensiones:** Diseñar una tabla de dimensión por cada perspectiva identificada, incorporando claves subrogadas autoincrementales y renombrando campos para claridad analítica.
3. **c) Tablas de Hechos:** Diseñar la tabla central de hechos con su clave primaria compuesta por las claves foráneas de las dimensiones relacionadas y un campo por cada medida/indicador atómico.
4. **d) Uniones (Diagrama Lógico):** Modelar las relaciones de integridad referencial entre las tablas de dimensiones y la tabla de hechos.
5. **DDL Ejecutable:** Escribir el script SQL con las sentencias `CREATE TABLE`, claves primarias, foráneas, restricciones e índices, probado y ejecutable sin errores.

---

## 2. Inventario y Función de Archivos

| Archivo | Tipo | Descripción y Función |
| :--- | :--- | :--- |
| **`entrega_modelo_logico.md`** | **Documento Principal de Entrega** | Informe técnico que justifica la elección del Esquema en Estrella, detalla la estructura de cada dimensión (`DIM_TIEMPO`, `DIM_EQUIPO`, `DIM_DIVISION`, `DIM_PAIS`), especifica la tabla `FACT_COMPETENCIA` y presenta el diagrama entidad-relación en Mermaid (`erDiagram`). |
| **`entrega_modelo_logico.sql`** | **Script DDL Real (MySQL 8.0)** | Código SQL ejecutable que crea la base de datos `dw_competencia_futbol`, define las 5 tablas con tipos de datos óptimos (InnoDB, utf8mb4), claves foráneas con restricciones de integridad, restricciones de dominio (`CHECK`) y 5 índices B-tree para acelerar consultas analíticas. |
| **`README.md`** | **Guía Explicativa Interna** | Este archivo: explica el marco metodológico del Paso 3, el rol de cada entregable y cómo justificar las decisiones de modelado. |

---

## 3. Decisiones de Modelado y Justificación Técnica

### 1. ¿Por qué se eligió un Esquema en Estrella (Star Schema)?
* **Proceso de negocio único:** Se analiza exclusivamente un evento atómico: partidos disputados entre clubes. No existen múltiples procesos interrelacionados que demanden un esquema en constelación.
* **Eficiencia analítica y simplicidad de consultas:** El esquema en estrella desnormaliza deliberadamente jerarquías para evitar *JOINs* en cascada. Modelar `DIM_PAIS` de forma independiente permite filtrar métricas a nivel país directamente sin pasar por `DIM_DIVISION` (lo que ocurriría en un copo de nieve).
* **Compatibilidad BI:** Es el estándar por excelencia para herramientas de reporting, cubos OLAP y tableros interactivos.

### 2. Dimensión con Roles (*Role-Playing Dimension*): `DIM_EQUIPO`
* En cada partido intervienen dos equipos: el local y el visitante (rival).
* En lugar de duplicar tablas físicas, se modela un catálogo unificado de equipos en `DIM_EQUIPO` y la tabla de hechos `FACT_COMPETENCIA` se vincula a ella a través de dos claves foráneas diferenciadas:
  * `id_equipo_local` $\rightarrow$ `DIM_EQUIPO(id_equipo)`
  * `id_equipo_visitante` $\rightarrow$ `DIM_EQUIPO(id_equipo)`

### 3. Clave Primaria Compuesta en `FACT_COMPETENCIA`
Siguiendo las reglas de la Metodología Hefesto, la clave primaria de la tabla de hechos se conforma por la tupla compuesta de sus claves foráneas:
$$(id\_tiempo, id\_equipo\_local, id\_equipo\_visitante, id\_division, id\_pais)$$
Esto garantiza matemáticamente que no pueda existir duplicación de un mismo enfrentamiento en una misma fecha y competición.

---

## 4. Estructura de Tablas del Data Warehouse

```text
DIM_TIEMPO (id_tiempo [PK], fecha, temporada, anio, mes, nombre_mes, trimestre, dia_semana)
DIM_EQUIPO (id_equipo [PK], nombre_equipo)
DIM_DIVISION (id_division [PK], codigo_division, nombre_liga)
DIM_PAIS (id_pais [PK], codigo_pais, nombre_pais)

FACT_COMPETENCIA (
    id_tiempo [PK, FK],
    id_equipo_local [PK, FK],
    id_equipo_visitante [PK, FK],
    id_division [PK, FK],
    id_pais [PK, FK],
    goles_local, goles_visitante, resultado,
    elo_local, elo_visitante,
    amarillas_local, amarillas_visitante, rojas_local, rojas_visitante,
    puntos_local, puntos_visitante, victoria_local, empate, victoria_visitante
)
```

---

## 5. Verificación del DDL

El script `entrega_modelo_logico.sql` fue ejecutado y validado en **MySQL 8.0.45**, compilando de forma limpia sin advertencias ni errores. Es invocado automáticamente por los scripts de carga del Paso 4.
