# Entrega Final: Dashboard sobre el Modelo Estrella — Guía del Entregable

Este directorio contiene los archivos correspondientes a la **Entrega Final: Dashboard sobre el modelo estrella** de la Metodología HEFESTO v2.

---

## 1. Objetivo Metodológico de la Entrega Final

Una vez cargado y validado el Data Mart multidimensional en MySQL, el objetivo final es **explotar la información para responder a las preguntas de negocio iniciales**:
1. Responder con rigor cada una de las **6 preguntas de negocio** formuladas en el Paso 1.
2. Extraer los datos **exclusivamente mediante consultas SQL sobre el modelo estrella** (`FACT_COMPETENCIA` y sus dimensiones relacionadas), **nunca sobre el archivo CSV original**.
3. Representar los resultados mediante **tablas de datos consolidadas** y **gráficos visuales trazables** a las consultas ejecutadas.
4. Redactar una conclusión analítica y ejecutiva por cada pregunta, orientada a la toma de decisiones estratégicas de sponsors deportivos.

---

## 2. Inventario y Función de Archivos

| Archivo / Carpeta | Tipo | Descripción y Función |
| :--- | :--- | :--- |
| **`dashboard.md`** | **Documento Principal de Entrega** | Informe formal exigido por la consigna final: contiene las 6 preguntas de negocio, cada una con su consulta SQL sobre el modelo estrella, la tabla de resultados reales, el gráfico visual correspondiente y su conclusión analítica. |
| **`dashboard.ipynb`** | **Notebook Interactivo de Demostración** | Cuaderno de Jupyter que ejecuta las 6 consultas SQL contra MySQL, procesa los DataFrames y renderiza los gráficos de forma interactiva. Ideal para proyectar en la defensa oral. |
| **`generar_dashboard.py`** | **Script Generador Automatizado** | Programa en Python que crea la vista auxiliar, ejecuta las 6 consultas SQL contra MySQL, genera las 6 figuras `.png` en la subcarpeta `graficos/` y ensambla automáticamente el documento `dashboard.md`. |
| **`requirements.txt`** | **Dependencias de Software** | Librerías necesarias para ejecutar el tablero y generar gráficos (`matplotlib`, `pandas`, `sqlalchemy`, `mysql-connector-python`, `jupyterlab`). |
| **`sql/`** | **Scripts SQL Auxiliares** | Contiene `07_vista_dashboard.sql`, que crea la vista `V_PARTICIPACION` (proyección de cada partido desde el rol de cada equipo) para simplificar las consultas analíticas del tablero sin alterar el modelo físico. |
| **`graficos/`** | **Visualizaciones Gráficas** | Las 6 imágenes en alta resolución (`pregunta_01.png` a `pregunta_06.png`) referenciadas e insertadas en `dashboard.md`. |
| **`dashboard-dinamico/`** | **Tablero Web Dinámico para Exposición** | Aplicación interactiva en Streamlit preparada para Render y Clever Cloud MySQL (o contingencia offline), con editor SQL en vivo y gráficos dinámicos para responder preguntas del docente en clase. Ver [`MANUAL_EXPOSICION_Y_DESPLIEGUE.md`](dashboard-dinamico/MANUAL_EXPOSICION_Y_DESPLIEGUE.md). |
| **`README.md`** | **Guía Explicativa Interna** | Este archivo: describe los entregables finales y cómo defender los hallazgos ante la cátedra. |

---

## 3. Síntesis de Respuestas a las 6 Preguntas de Negocio

Para la defensa del trabajo, los integrantes del grupo deben dominar los siguientes hallazgos analíticos:

1. **Evolución a 5 años (Nottingham Forest):** Creció **+314 puntos de Elo** (+21,4 %), pasando de 1.469 en 2021 a 1.783 en 2026 tras su ascenso a la Premier League.
2. **Historial de Clásicos:** En los derbis analizados, Arsenal supera a Tottenham (47 % vs 20 % de victorias) y Barcelona supera a Real Madrid (46 % vs 33 % en liga).
3. **Ventaja de Localía:** Es contundente en toda Europa: el equipo local gana el **45,0 %** de los encuentros, frente a solo un **28,1 %** del visitante.
4. **Paridad de Ligas:** Las segundas divisiones son las más parejas de Europa (menor dispersión de brecha Elo entre rivales: Segunda División española, Ligue 2 francesa y Serie B italiana).
5. **Disciplina por Liga:** Las ligas con mayor promedio de tarjetas amarillas por partido son la Primeira Liga de Portugal (5,09) y La Liga de España (5,02).
6. **Mejores Visitantes:** Los clubes más efectivos fuera de casa en los últimos 5 años son Porto (71,8 % de victorias visitante), PSV (70,9 %) y Celtic (70,7 %).

---

## 4. Cómo regenerar el Dashboard y los Gráficos

Si se cargan nuevos datos o se desea reconstruir las imágenes y el informe:

```powershell
pip install -r requirements.txt
$env:MYSQL_PASSWORD = "tu_password_de_mysql"
python generar_dashboard.py
```
El script creará la vista analítica en MySQL, ejecutará las 6 consultas, regenerará las 6 imágenes en `graficos/` y escribirá el informe final en `dashboard.md`.
