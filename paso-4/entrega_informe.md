# Paso 4: Integración de Datos (Metodología HEFESTO)

**Punto de partida:** el modelo lógico de `entrega_modelo_logico.sql` (Paso 3), base `dw_competencia_futbol` en MySQL 8.0.

**Herramienta elegida:** Implementación integral en **Python** estructurada en el notebook interactivo `01_carga_dw.ipynb` (siguiendo las recomendaciones de la cátedra para garantizar trazabilidad celda a celda). Se utilizan las librerías `pandas` para la ingesta masiva en memoria, auditoría de calidad, limpieza, homologación y estructuración multidimensional, y `SQLAlchemy` junto a `mysql-connector-python` para la ejecución del DDL y la persistencia directa en el motor relacional MySQL 8.0.

**Alcance:** el archivo trae 38 ligas, pero el Data Mart se carga solo con las **15 ligas europeas** definidas en el Paso 2 (E0, E1, SP1, SP2, I1, I2, D1, D2, F1, F2, N1, P1, B1, T1, SC0). El resto de los partidos se analiza igualmente en la etapa de auditoría de calidad (para que los chequeos se hagan sobre el archivo completo de 238.858 registros) y luego se filtra y registra bajo el motivo "Liga fuera del alcance".

---

## 1. Organización del flujo ETL y orden de ejecución

De acuerdo con la metodología HEFESTO y la guía del TP, este paso abarca exclusivamente el **proceso de integración de datos (ETL)**: extracción a staging en memoria, aseguramiento de la calidad, limpieza/transformación, población del modelo estrella en MySQL y verificación matemática de consistencia. El tablero de visualización y análisis de preguntas de negocio se entrega de forma separada en la carpeta `entrega-final/`.

```text
paso-4/
├── entrega_informe.md        <- este informe de integración y calidad
├── 01_carga_dw.ipynb         <- notebook ETL oficial (Python + pandas + MySQL)
├── EXPLICACION_ETL_PYTHON.md <- guía pedagógica detallada del notebook
├── requirements.txt          <- librerías requeridas (pandas, sqlalchemy, mysql-connector-python, jupyterlab)
├── datos/
│   └── Matches.csv           <- dataset real de partidos (48 columnas, ~45 MB)
├── mapeos/
│   ├── mapeo_equipos.csv     <- variantes de nombre de equipo -> nombre canónico
│   └── mapeo_divisiones.csv  <- las 15 divisiones del alcance -> liga y país
└── README.md                 <- guía del entregable y manual de ejecución
```

| Orden | Etapa en `01_carga_dw.ipynb` | Qué hace |
| :---- | :---- | :---- |
| 0 | Inicialización del entorno | Importa librerías, define rutas y ejecuta el DDL de `../paso-3/entrega_modelo_logico.sql` para crear la base `dw_competencia_futbol` y sus tablas vacías |
| 1 | Extracción a Staging en memoria | Lee `Matches.csv` completo (**238.858 filas**, 48 columnas como texto) y carga las tablas auxiliares de mapeo |
| 2 | Chequeos de calidad de datos | Ejecuta los 15 controles de integridad, nulos, rangos y consistencia sobre el DataFrame crudo |
| 3 | Limpieza y normalización | Genera el DataFrame limpio (132.256 filas), normaliza textos, unifica clubes y registra los 106.602 descartes |
| 4 | Construcción multidimensional | Genera los DataFrames de dimensiones (`DIM_TIEMPO`, `DIM_EQUIPO`, `DIM_DIVISION`, `DIM_PAIS`) con claves subrogadas y la tabla `FACT_COMPETENCIA` con métricas derivadas |
| 5 | Carga física a MySQL | Persiste dimensiones y hechos en MySQL mediante `to_sql(..., if_exists="append")`, respetando claves primarias y foráneas |
| 6 | Verificación matemática y balance | Valida conteos por tabla, balance de filas con diferencia 0, e integridad referencial y de métricas contra el CSV original |

**Cómo ejecutarlo:**

```powershell
pip install -r requirements.txt
jupyter lab
```
Abrir `01_carga_dw.ipynb` y ejecutar el cuaderno completo (*Run → Run All Cells*). Al llegar a la celda de conexión a base de datos, solicitará la contraseña de MySQL de forma interactiva (o puede preconfigurarse con `$env:MYSQL_PASSWORD = "..."`). La ejecución completa toma aproximadamente 60 segundos.

*(Nota: Para la visualización interactiva y el reporte de respuestas a las preguntas de negocio, remitirse a `../entrega-final/dashboard.md` y `../entrega-final/dashboard.ipynb`).*

---

## 2. Volcado en un área intermedia (staging)

El archivo se vuelca **tal cual viene** en `STG_PARTIDOS`: una fila por línea del CSV, todas las columnas como texto y un `id_fila` con el número de línea del archivo, para poder rastrear cualquier problema hasta el origen. Se usa la collation `utf8mb4_0900_bin`, que distingue mayúsculas y espacios finales, para que los chequeos detecten diferencias como `'Ajax'` / `'Ajax '`.

| Tabla de staging | Contenido |
| :---- | :---- |
| `STG_PARTIDOS` | Datos crudos del archivo: **238.858 filas** (se omitió 1 línea en blanco al final del archivo) |
| `STG_MAPEO_EQUIPOS` | 4 variantes de nombre -> nombre canónico |
| `STG_MAPEO_DIVISION` | Las 15 divisiones del alcance con su liga y su país |
| `STG_PARTIDOS_NORM` | Datos con tipos convertidos, textos normalizados y nombres unificados |
| `STG_PARTIDOS_LIMPIO` | Filas válidas, listas para cargar el modelo |
| `STG_DESCARTES` | Filas descartadas y el motivo |

---

## 3. Calidad de datos: qué se encontró y cómo se resolvió

Los chequeos de `02_calidad.sql` corren sobre el **archivo completo** (238.858 partidos). La columna "En el alcance" indica cuántos casos caen dentro de las 15 ligas que se cargan.

| # | Chequeo | Archivo completo | En el alcance | Decisión |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Partidos por alcance | 38 ligas | 15 ligas, **132.257 partidos** (2000-07-28 a 2026-09-03) | Los otros 106.601 partidos (23 ligas) **se descartan** como "Liga fuera del alcance" |
| 2 | Nulos en columnas clave (fecha, división, equipos) | 0 | 0 | — |
| 3 | Partidos sin goles ni resultado | 4 | 1 (F2, 2025-12-05, Bastia–Red Star) | **Se descarta** (partido suspendido o sin dato): no aporta a ningún indicador |
| 4 | Fechas con formato inválido | 0 | 0 | — |
| 5 | Resultado fuera del dominio H/D/A | 0 | 0 | — |
| 6 | Resultado inconsistente con los goles | 0 | 0 | Igualmente el resultado se deriva de los goles, para garantizar la coherencia |
| 7 | Partidos sin Elo (local o visitante) | 37 % de los partidos locales | **3,1 %** (4.140 partidos) | **Se deja en `NULL`** (no se imputa) |
| 8 | Tarjetas vacías | 46,6 % | **35,0 %** (46.310 partidos) | **Se dejan en `NULL`** (imputar 0 bajaría los promedios). Los promedios se calculan solo con partidos con dato |
| 9 | Valores fuera de rango | 1 | 1: Zaragoza–Oviedo (SP2, 2020-11-13) con **9 rojas** al visitante | Imposible en un partido terminado (con 5 expulsados se suspende). **El valor se reemplaza por `NULL`** y el partido se conserva |
| 10 | Goles > 15, amarillas > 15, Elo fuera de 800-2500 | 0 | 0 | — |
| 11 | Nombres con espacios sobrantes | 11 equipos | Los 11 (`'Kaiserslautern '` ×33, `'Ajax '`, `'Feyenoord '`, `'Piacenza '`, etc.) | `TRIM()` |
| 12 | Caracteres mal codificados | `King\x92s Lynn` (U+0092 en vez de apóstrofo) | 0 (juega en la National League, fuera del alcance) | La regla de reemplazo queda igual en `03_limpieza.sql` |
| 13 | Mismo club escrito de dos formas | 15 grupos de variantes | 4: `Nott'm Forest`/`Nottm Forest` (la fuente cambia la escritura en 2024), `M'gladbach`/`MGladbach` (en 2025), `Roda JC`/`Roda` (en 2010), `Preußen Münster`/`Preussen Munster` | Tabla `mapeo_equipos.csv`. Sin esto, por ejemplo, la historia de Nottingham Forest quedaría partida en dos equipos y no se podría medir su evolución |
| 14 | Partidos duplicados (fecha + local + visitante) | 0 | 0 | La regla igual queda implementada (se conserva la primera aparición) |
| 15 | Local y visitante iguales | 0 | 0 | — |

**Resultado de la limpieza:** 238.858 filas en el archivo → **132.256 filas limpias** + **106.602 descartadas** (106.601 por liga fuera del alcance + 1 sin resultado). Se corrigieron 0 resultados y se anuló 1 valor fuera de rango.

---

## 4. Carga de las dimensiones

Cada dimensión se puebla con los valores únicos de `STG_PARTIDOS_LIMPIO`, y su clave subrogada se genera con `AUTO_INCREMENT`:

| Dimensión | Filas | Origen |
| :---- | :---- | :---- |
| `DIM_TIEMPO` | 6.321 | Fechas distintas con partidos. Se derivan temporada, año, mes, nombre del mes, trimestre y día de la semana |
| `DIM_EQUIPO` | 577 | Unión de locales y visitantes ya normalizados (592 nombres crudos en el alcance − 11 por espacios − 4 variantes unificadas) |
| `DIM_DIVISION` | 15 | Código de división + nombre de la liga |
| `DIM_PAIS` | 10 | País derivado de la división |

**Temporada:** se calcula con corte en julio (`2021-07-01` a `2022-06-30` → `'2021-2022'`), que es el calendario de las 15 ligas del alcance.

---

## 5. Carga de la tabla de hechos

`FACT_COMPETENCIA` recibe un registro por partido (granularidad definida en el Paso 2). Para cada fila de `STG_PARTIDOS_LIMPIO` se busca la clave correspondiente en cada dimensión (`fecha` → `id_tiempo`, nombre del local → `id_equipo_local`, nombre del visitante → `id_equipo_visitante`, código de división → `id_division`, país → `id_pais`). Además se calculan los hechos derivados: puntos de cada equipo (3/1/0) y las banderas `victoria_local`, `empate` y `victoria_visitante`.

**Filas cargadas: 132.256.**

---

## 6. Verificación de la carga

**Conteos por tabla:**

| Tabla | Filas |
| :---- | :---- |
| `DIM_TIEMPO` | 6.321 |
| `DIM_EQUIPO` | 577 |
| `DIM_DIVISION` | 15 |
| `DIM_PAIS` | 10 |
| `FACT_COMPETENCIA` | 132.256 |

**Balance de filas:** 238.858 (archivo) = 132.256 (hechos) + 106.602 (descartes) → diferencia **0**.

**Comparación de totales del DW contra el archivo original** (calculados en Python leyendo `Matches.csv` directamente, con los mismos criterios de alcance y de descarte):

| Medida | Archivo CSV | DW | Estado |
| :---- | :---- | :---- | :---- |
| Partidos del alcance con resultado | 132.256 | 132.256 | OK |
| Goles totales | 348.954 | 348.954 | OK |
| Tarjetas rojas | 18.356 | 18.356 | OK |

**Otros controles (todos en 0 / sin diferencias):**

* Partidos y goles por división, DW vs staging: ninguna división con diferencias.
* Tarjetas amarillas (337.275) y rojas (18.356), DW vs tabla limpia: iguales.
* Claves de hechos sin su fila en la dimensión: 0.
* Filas con banderas o puntos incoherentes con el resultado: 0.

**Conclusión:** no se perdieron ni se duplicaron datos. Las únicas filas que no llegaron al DW son las descartadas a propósito (ligas fuera del alcance y 1 partido sin resultado), y quedan registradas en `STG_DESCARTES` con su motivo.

---

## 7. Política de actualización

Para este TP la carga es única. Si el archivo se recibiera periódicamente (el autor del dataset lo actualiza a medida que se juegan las fechas), la actualización se plantearía así:

| Componente | Tipo de actualización | Cómo |
| :---- | :---- | :---- |
| Staging (`STG_PARTIDOS`) | **Recarga completa** en cada ejecución | Se vacía y se vuelve a volcar el archivo completo (≈240.000 filas, menos de 1 minuto). Así los chequeos de calidad siempre corren sobre el archivo vigente. Para sumar una liga al alcance alcanza con agregarla a `mapeo_divisiones.csv` |
| Tablas de mapeo | **Recarga completa** | Se vuelven a leer los CSV de `mapeos/`. Si aparece un equipo nuevo con una variante de nombre, se agrega una fila al CSV |
| `DIM_TIEMPO`, `DIM_EQUIPO`, `DIM_DIVISION`, `DIM_PAIS` | **Incremental** (solo altas) | `INSERT ... SELECT` de los valores que todavía no existen (`WHERE NOT EXISTS`). Las claves existentes no cambian, así los hechos ya cargados siguen siendo válidos. Si un club cambia de nombre se sobrescribe el nombre (SCD tipo 1) mediante la tabla de mapeo |
| `FACT_COMPETENCIA` | **Incremental con ventana de reproceso** | Se insertan los partidos nuevos (fecha + local + visitante que no estén en la tabla de hechos). Además se borran y se vuelven a cargar los últimos **30 días**, para tomar correcciones tardías de la fuente (resultados cargados después, tarjetas o Elo corregidos) |
| Todo el modelo | **Recarga completa programada** | Al comienzo de cada temporada (julio), ejecución completa de `01_carga_dw.ipynb`, para absorber correcciones históricas de la fuente |

**Frecuencia propuesta:** semanal (los lunes, después de cada fin de semana de partidos). Es suficiente para las preguntas del negocio, que miran tendencias por temporada y por año, no resultados en tiempo real.

**Controles en cada actualización:** se ejecutan los chequeos de calidad y las verificaciones matemáticas documentadas en las celdas 2 y 6 de `01_carga_dw.ipynb`. Si el balance de filas o la comparación de totales contra el archivo no dan 0, la carga se marca como fallida y el DW conserva el estado previo.

> **Nota técnica sobre la implementación en Jupyter (`01_carga_dw.ipynb`):** El notebook implementa esta dinámica de persistencia: antes de ejecutar el DDL comprueba si las tablas ya existen en el servidor MySQL local. Si ya existen, **no las borra**, protegiendo el DW contra sobreescrituras accidentales al reiniciar el kernel. Además, al guardar datos valida los registros existentes para evitar duplicados e insertar únicamente las novedades en dimensiones y hechos. Si se requiere una reconstrucción total, el parámetro `RECREAR_TABLAS = True` en la configuración permite forzar la recarga completa.
