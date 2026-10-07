"""Tablero Analítico Dinámico — Data Mart de Competencia de Fútbol (HEFESTO v2)
Diseñado para la Exposición Final en Clase con Render y Clever Cloud MySQL.

Permite modificar parámetros en vivo, alterar consultas SQL en tiempo real,
generar gráficos interactivos y responder preguntas ad-hoc del docente.
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
import streamlit as st

# Configuración inicial de Streamlit
st.set_page_config(
    page_title="Dashboard Dinámico — BDA Fútbol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos locales
DIR_ACTUAL = Path(__file__).resolve().parent
if str(DIR_ACTUAL) not in sys.path:
    sys.path.append(str(DIR_ACTUAL))

import conexion
import consultas_base

# Intentar importar plotly para gráficos interactivos; si no, fallback a matplotlib
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAY_PLOTLY = True
except ImportError:
    HAY_PLOTLY = False
    import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# GESTIÓN DE ESTADO Y CONECTIVIDAD
# -----------------------------------------------------------------------------
if "tipo_origen" not in st.session_state:
    st.session_state["tipo_origen"] = "clever" if os.environ.get("MYSQL_HOST") else "sqlite"

if "cfg_mysql" not in st.session_state:
    st.session_state["cfg_mysql"] = conexion.obtener_config_por_defecto()

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR): CONECTIVIDAD Y MODOS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Conexión al Data Mart")
    
    opciones_origen = {
        "clever": "☁️ Clever Cloud MySQL (Nube)",
        "local": "💻 MySQL Local (localhost:3306)",
        "sqlite": "🛡️ Contingencia Offline (SQLite Local)"
    }
    
    tipo_sel = st.selectbox(
        "Origen de Datos:",
        options=list(opciones_origen.keys()),
        format_func=lambda k: opciones_origen[k],
        index=list(opciones_origen.keys()).index(st.session_state["tipo_origen"])
    )
    st.session_state["tipo_origen"] = tipo_sel

    if tipo_sel in ("clever", "local"):
        with st.expander("🔧 Credenciales MySQL", expanded=(tipo_sel == "clever")):
            host_def = st.session_state["cfg_mysql"].get("host", "localhost")
            port_def = st.session_state["cfg_mysql"].get("port", 3306)
            user_def = st.session_state["cfg_mysql"].get("user", "root")
            db_def = st.session_state["cfg_mysql"].get("database", "dw_competencia_futbol")
            
            host = st.text_input("Host:", value=host_def)
            port = st.number_input("Puerto:", value=int(port_def), step=1)
            user = st.text_input("Usuario:", value=user_def)
            password = st.text_input("Contraseña:", value=st.session_state["cfg_mysql"].get("password", ""), type="password")
            database = st.text_input("Base de datos:", value=db_def)
            
            st.session_state["cfg_mysql"] = {
                "host": host, "port": port, "user": user, "password": password, "database": database
            }

    if st.button("⚡ Probar Conexión", use_container_width=True):
        with st.spinner("Probando conexión..."):
            ok, msg = conexion.probar_conexion(
                st.session_state["tipo_origen"],
                st.session_state["cfg_mysql"]
            )
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.divider()

    st.markdown("## 🧭 Navegación")
    modo = st.radio(
        "Seleccione el modo de trabajo:",
        options=[
            "📊 12 Preguntas de Negocio (Dinámico)",
            "💻 Consola SQL en Vivo (Preguntas del Profesor)",
            "🔍 Explorador del Data Mart"
        ]
    )

    st.divider()
    st.markdown("""
    **Metodología:** HEFESTO v2  
    **Proceso:** Competencia entre Equipos  
    **Alcance:** 15 Ligas / 10 Países  
    """)

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL
# -----------------------------------------------------------------------------
st.title("⚽ Tablero de Control Dinámico — Data Mart de Fútbol")
st.caption("Bases de Datos Avanzadas | Defensa Oral Final | Render + Clever Cloud MySQL")

# Badge de estado de conexión
if st.session_state["tipo_origen"] == "clever":
    st.info(f"🌐 **Motor activo:** Clever Cloud MySQL (`{st.session_state['cfg_mysql']['host']}` / `{st.session_state['cfg_mysql']['database']}`)")
elif st.session_state["tipo_origen"] == "local":
    st.info(f"💻 **Motor activo:** MySQL Local (`localhost:{st.session_state['cfg_mysql']['port']}` / `{st.session_state['cfg_mysql']['database']}`)")
else:
    st.warning("🛡️ **Motor activo:** Modo Contingencia Offline (SQLite Embebido con 132.256 partidos). Ideal si falla la red en la exposición.")

st.write("")

# -----------------------------------------------------------------------------
# MODO 1: LAS 12 PREGUNTAS DE NEGOCIO DINÁMICAS
# -----------------------------------------------------------------------------
if modo == "📊 12 Preguntas de Negocio (Dinámico)":
    catalogo = consultas_base.PREGUNTAS_CATALOGO
    opciones_preguntas = [f"P{p['id']}: {p['titulo']}" for p in catalogo]
    
    idx_p = st.selectbox(
        "Seleccione la Pregunta de Negocio a exponer:",
        range(len(catalogo)),
        format_func=lambda i: opciones_preguntas[i]
    )
    pregunta = catalogo[idx_p]

    st.subheader(f"Pregunta {pregunta['id']}: {pregunta['titulo']}")
    st.markdown(f"**Indicadores & Perspectivas:** `{pregunta['indicadores']}`")
    st.markdown(f"*{pregunta['descripcion']}*")

    st.markdown("### 🎛️ Parámetros Dinámicos para la Exposición")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    params = {}
    pid = pregunta["id"]

    # Controles específicos por cada pregunta
    if pid == 1:
        with col1:
            params["equipo"] = st.text_input("Equipo a evaluar:", value="Nottm Forest", help="Podés cambiar a 'Arsenal', 'Real Madrid', 'Barcelona', etc.")
        with col2:
            params["anios"] = st.slider("Ventana de años:", min_value=1, max_value=15, value=5)
        with col3:
            tipo_graf = st.selectbox("Tipo de gráfico:", ["line", "bar", "scatter"], index=0)

    elif pid == 2:
        with col1:
            modo_pareja = st.checkbox("Comparar enfrentamiento libre entre 2 clubes", value=False)
            params["modo_pareja"] = modo_pareja
        if modo_pareja:
            with col2:
                params["equipo_a"] = st.text_input("Equipo A:", value="Arsenal")
            with col3:
                params["equipo_b"] = st.text_input("Equipo B:", value="Tottenham")
        else:
            with col2:
                st.info("Mostrando los 6 derbis oficiales consolidados.")
        tipo_graf = "stacked_bar"

    elif pid == 3:
        with col1:
            params["limit"] = st.slider("Cantidad de ligas:", min_value=5, max_value=25, value=15)
        with col2:
            metrica_y = st.selectbox("Métrica a graficar:", ["ventaja_pp", "pct_local", "dif_goles"], index=0)
        with col3:
            tipo_graf = st.selectbox("Tipo de gráfico:", ["barh", "bar"], index=0)

    elif pid == 4:
        with col1:
            params["pct_min_elo"] = st.slider("% mínimo de partidos con Elo:", min_value=50, max_value=100, value=80)
        with col2:
            params["limit"] = st.slider("Ligas a mostrar:", min_value=5, max_value=20, value=15)
        with col3:
            tipo_graf = st.selectbox("Tipo de gráfico:", ["barh", "bar"], index=0)

    elif pid == 5:
        with col1:
            params["min_partidos"] = st.number_input("Partidos mínimos:", value=1000, step=100)
        with col2:
            params["orden"] = st.selectbox("Ordenar por:", ["amarillas_x_partido", "rojas_x_partido"], index=0)
        with col3:
            params["limit"] = st.slider("Ligas a mostrar:", min_value=5, max_value=20, value=15)
        tipo_graf = "barh"

    elif pid == 6:
        with col1:
            params["anios"] = st.slider("Ventana de años:", min_value=1, max_value=10, value=5)
        with col2:
            params["min_partidos"] = st.number_input("Partidos visitante mínimos:", value=60, step=10)
        with col3:
            params["limit"] = st.slider("Top equipos:", min_value=5, max_value=30, value=15)
        tipo_graf = "barh"

    elif pid == 7:
        with col1:
            params["anios"] = st.slider("Ventana de años:", min_value=1, max_value=10, value=5)
        with col2:
            params["min_partidos"] = st.number_input("Partidos totales mínimos:", value=120, step=10)
        with col3:
            params["limit"] = st.slider("Top equipos:", min_value=5, max_value=30, value=15)
        tipo_graf = "barh"

    elif pid == 8:
        with col1:
            params["anios"] = st.slider("Ventana de años:", min_value=1, max_value=10, value=5)
        with col2:
            params["min_partidos"] = st.number_input("Partidos mínimos:", value=120, step=10)
        with col3:
            params["limit"] = st.slider("Top equipos:", min_value=5, max_value=30, value=15)
        tipo_graf = "barh"

    elif pid == 9:
        with col1:
            params["modo"] = st.radio("Enfoque:", ["inconsistentes", "consistentes"], format_func=lambda x: "Menos consistentes (ascensores)" if x == "inconsistentes" else "Más consistentes (sin descenso)")
        with col2:
            paises_str = st.text_input("Países a incluir (códigos):", value="'ENG', 'GER', 'ITA', 'ESP', 'FRA'")
            params["paises_in"] = paises_str
        with col3:
            params["min_temporadas"] = st.slider("Temporadas mínimas:", min_value=10, max_value=30, value=20 if params["modo"] == "inconsistentes" else 25)
            params["limit"] = 15
        tipo_graf = "barh"

    elif pid == 10:
        with col1:
            params["anios"] = st.slider("Ventana de años:", min_value=1, max_value=10, value=3)
        with col2:
            params["min_partidos"] = st.number_input("Partidos mínimos con Elo:", value=30, step=5)
        with col3:
            params["limit"] = st.slider("Top equipos revelación:", min_value=5, max_value=25, value=15)
        tipo_graf = "barh"

    elif pid == 11:
        with col1:
            params["min_partidos"] = st.number_input("Partidos con dato de tarjetas:", value=200, step=50)
        with col2:
            params["orden"] = st.selectbox("Ordenar por:", ["rojas_x_partido", "amarillas_x_partido"], index=0)
        with col3:
            params["limit"] = st.slider("Top equipos:", min_value=5, max_value=25, value=15)
        tipo_graf = "barh"

    elif pid == 12:
        with col1:
            params["temporada"] = st.selectbox("Temporada:", ["2025-2026", "2024-2025", "2023-2024", "2022-2023", "2021-2022"], index=0)
        with col2:
            params["orden"] = st.selectbox("Métrica de ranking:", ["elo_maximo", "elo_promedio_equipos"], index=0)
        with col3:
            tipo_graf = st.selectbox("Tipo de gráfico:", ["bar", "barh"], index=0)

    # Generar la consulta SQL base
    sql_generada = pregunta["sql_builder"](params).strip()

    st.markdown("### 📝 Consulta SQL sobre el Modelo Estrella")
    
    # Opción de edición en vivo
    editar_sql = st.checkbox("✏️ Modificar consulta SQL en vivo (para consignas del profesor)", value=False)
    
    if editar_sql:
        sql_a_ejecutar = st.text_area("Editor de Consulta SQL:", value=sql_generada, height=220)
    else:
        st.code(sql_generada, language="sql")
        sql_a_ejecutar = sql_generada

    # Ejecutar consulta
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        ejecutar = st.button("🚀 Ejecutar Consulta", use_container_width=True)

    # Siempre ejecutamos o mostramos el resultado
    with st.spinner("Consultando el Data Mart..."):
        df, duracion, error = conexion.ejecutar_consulta(
            sql_a_ejecutar,
            tipo_origen=st.session_state["tipo_origen"],
            config=st.session_state["cfg_mysql"]
        )

    if error:
        st.error(f"❌ Error en la ejecución de la consulta SQL: {error}")
    elif df.empty:
        st.warning("⚠️ La consulta no arrojó resultados con los filtros seleccionados.")
    else:
        # Métricas de ejecución
        m1, m2, m3 = st.columns(3)
        m1.metric("Filas retornadas", len(df))
        m2.metric("Tiempo de ejecución", f"{duracion*1000:.1f} ms")
        m3.metric("Columnas", len(df.columns))

        st.markdown("### 📈 Visualización Gráfica Interactiva")

        # Renderizado de gráfico según la pregunta
        if HAY_PLOTLY:
            fig = None
            if pid == 1:
                fig = px.line(
                    df, x="anio", y="elo_promedio", markers=True,
                    title=f"Evolución de Elo: {params.get('equipo')} por Año",
                    labels={"anio": "Año", "elo_promedio": "Elo Promedio"}
                )
                fig.update_traces(line_color="#2a78d6", marker=dict(size=8, color="#eb6834"))
            elif pid == 2:
                if params.get("modo_pareja", False):
                    fig = px.bar(
                        df, x="clasico", y=["pct_gana_a", "pct_empate", "pct_gana_b"],
                        title="Balance Histórico del Enfrentamiento Directo",
                        labels={"value": "% de partidos", "variable": "Resultado"},
                        barmode="stack",
                        color_discrete_sequence=["#2a78d6", "#898781", "#eb6834"]
                    )
                else:
                    fig = px.bar(
                        df, y="clasico", x=["pct_gana_a", "pct_empate", "pct_gana_b"],
                        orientation="h",
                        title="Resultados de Clásicos Europeos (% de Partidos)",
                        labels={"value": "% de partidos", "variable": "Resultado"},
                        barmode="stack",
                        color_discrete_sequence=["#2a78d6", "#898781", "#eb6834"]
                    )
            elif pid == 3:
                fig = px.bar(
                    df, y="liga", x=metrica_y if 'metrica_y' in locals() else "ventaja_pp",
                    orientation="h",
                    title="Ventaja de Localía por Liga",
                    labels={"ventaja_pp": "Ventaja (Puntos Porcentuales)", "liga": "Liga"},
                    color_discrete_sequence=["#2a78d6"]
                )
            elif pid == 4:
                fig = px.bar(
                    df, y="liga", x="desvio_brecha_elo",
                    orientation="h",
                    title="Paridad Competitiva: Menor desvío de brecha Elo = Mayor paridad",
                    labels={"desvio_brecha_elo": "Desvío Estándar", "liga": "Liga"},
                    color_discrete_sequence=["#1baf7a"]
                )
            elif pid == 5:
                y_col = params.get("orden", "amarillas_x_partido")
                fig = px.bar(
                    df, y="liga", x=y_col,
                    orientation="h",
                    title=f"Tarjetas por Partido: {y_col}",
                    labels={y_col: y_col.replace('_', ' ').capitalize(), "liga": "Liga"},
                    color_discrete_sequence=["#eb6834"]
                )
            elif pid in (6, 7):
                fig = px.bar(
                    df, y="equipo", x="pct_victorias",
                    orientation="h",
                    title="Efectividad de Victorias (%)",
                    labels={"pct_victorias": "% de Victorias", "equipo": "Club"},
                    color_discrete_sequence=["#2a78d6"]
                )
            elif pid == 8:
                fig = px.bar(
                    df, y="equipo", x="goles_favor_prom",
                    orientation="h",
                    title="Atractivo Ofensivo: Promedio de Goles a Favor por Partido",
                    labels={"goles_favor_prom": "Goles / Partido", "equipo": "Club"},
                    color_discrete_sequence=["#eb6834"]
                )
            elif pid == 9:
                metr = "cambios_de_division" if params.get("modo") == "inconsistentes" else "desvio_puntos_x_partido"
                fig = px.bar(
                    df, y="equipo", x=metr,
                    orientation="h",
                    title=f"Consistencia Divisional: {metr}",
                    labels={metr: metr.replace('_', ' ').capitalize(), "equipo": "Club"},
                    color_discrete_sequence=["#1baf7a"]
                )
            elif pid == 10:
                fig = px.bar(
                    df, y="equipo", x="incremento",
                    orientation="h",
                    title=f"Mayor Crecimiento Elo en {params.get('anios', 3)} años",
                    labels={"incremento": "Puntos Elo Ganados", "equipo": "Club"},
                    color_discrete_sequence=["#2a78d6"]
                )
            elif pid == 11:
                col_y = params.get("orden", "rojas_x_partido")
                fig = px.bar(
                    df, y="equipo", x=col_y,
                    orientation="h",
                    title=f"Fair Play: {col_y}",
                    labels={col_y: col_y.replace('_', ' ').capitalize(), "equipo": "Club"},
                    color_discrete_sequence=["#d9534f"]
                )
            elif pid == 12:
                metr = params.get("orden", "elo_maximo")
                fig = px.bar(
                    df, x="pais", y=metr,
                    title=f"Jerarquía Elo por País ({params.get('temporada')}): {metr}",
                    labels={metr: metr.replace('_', ' ').capitalize(), "pais": "País"},
                    color_discrete_sequence=["#2a78d6"],
                    text="mejor_equipo" if "mejor_equipo" in df.columns else None
                )

            if fig:
                fig.update_layout(
                    template="plotly_dark",
                    margin=dict(l=20, r=20, t=50, b=20),
                    height=450
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(df.set_index(df.columns[0]))

        st.markdown("### 📋 Tabla de Resultados Consolidados")
        st.dataframe(df, use_container_width=True)

        # Botón de descarga de datos
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar datos (CSV)",
            data=csv_data,
            file_name=f"resultado_pregunta_{pid}.csv",
            mime="text/csv"
        )

        st.markdown("### 💡 Conclusión Analítica y Decisión Estratégica")
        st.success(pregunta["conclusion_oficial"])

# -----------------------------------------------------------------------------
# MODO 2: CONSOLA SQL EN VIVO (PREGUNTAS DEL PROFESOR)
# -----------------------------------------------------------------------------
elif modo == "💻 Consola SQL en Vivo (Preguntas del Profesor)":
    st.subheader("💻 Consola SQL en Vivo — Interacción Libre para la Exposición")
    st.markdown("""
    Esta consola está diseñada para **responder al instante a cualquier pregunta sorpresa del docente**
    durante la defensa oral. Podés seleccionar plantillas rápidas o redactar consultas SQL desde cero
    sobre las tablas del Data Mart (`FACT_COMPETENCIA`, `DIM_EQUIPO`, `DIM_DIVISION`, `DIM_PAIS`, `DIM_TIEMPO`, `V_PARTICIPACION`).
    """)

    col_izq, col_der = st.columns([2, 1])

    with col_der:
        st.markdown("#### 📚 Plantillas Rápidas (1 Clic)")
        plantillas = consultas_base.PLANTILLAS_SQL_PROFE
        sel_plantilla = st.selectbox("Seleccione un ejemplo:", list(plantillas.keys()))
        sql_ejemplo = plantillas[sel_plantilla]

        with st.expander("📖 Diccionario de Tablas del DW", expanded=False):
            for t_nombre, cols in consultas_base.DICCIONARIO_TABLAS.items():
                st.markdown(f"**`{t_nombre}`**")
                for c_nom, c_tipo, c_desc in cols[:6]:
                    st.caption(f"• `{c_nom}` ({c_tipo}): {c_desc}")
                if len(cols) > 6:
                    st.caption(f"*... y {len(cols)-6} columnas más.*")

    with col_izq:
        if "sql_consola" not in st.session_state:
            st.session_state["sql_consola"] = sql_ejemplo.strip()

        if st.button("Cargar Plantilla al Editor"):
            st.session_state["sql_consola"] = sql_ejemplo.strip()

        sql_input = st.text_area(
            "Editor SQL en Vivo:",
            value=st.session_state["sql_consola"],
            height=260
        )
        st.session_state["sql_consola"] = sql_input

        btn_run = st.button("▶ Ejecutar Consulta Libre", type="primary", use_container_width=True)

    if btn_run or sql_input:
        df_res, dur, err_res = conexion.ejecutar_consulta(
            sql_input,
            tipo_origen=st.session_state["tipo_origen"],
            config=st.session_state["cfg_mysql"]
        )

        if err_res:
            st.error(f"❌ Error de ejecución SQL: {err_res}")
        elif df_res.empty:
            st.info("ℹ️ La consulta se ejecutó con éxito pero no devolvió filas.")
        else:
            st.success(f"✓ Consulta ejecutada con éxito: {len(df_res)} filas en {dur*1000:.1f} ms.")
            
            st.markdown("#### Resultados")
            st.dataframe(df_res, use_container_width=True)

            # Generador dinámico de gráficos sobre cualquier consulta libre
            if len(df_res.columns) >= 2 and len(df_res) > 0 and HAY_PLOTLY:
                st.markdown("#### 📊 Generador Rápido de Gráfico para la Respuesta")
                g1, g2, g3 = st.columns(3)
                col_x = g1.selectbox("Eje X (Categoría):", df_res.columns, index=0)
                col_y = g2.selectbox("Eje Y (Métrica):", df_res.columns, index=min(1, len(df_res.columns)-1))
                tipo_g = g3.selectbox("Tipo de Gráfico:", ["Barras", "Barras Horizontales", "Líneas", "Dispersión", "Torta"])

                if tipo_g == "Barras":
                    f_libre = px.bar(df_res, x=col_x, y=col_y, title=f"{col_y} según {col_x}", template="plotly_dark")
                elif tipo_g == "Barras Horizontales":
                    f_libre = px.bar(df_res, y=col_x, x=col_y, orientation="h", title=f"{col_y} según {col_x}", template="plotly_dark")
                elif tipo_g == "Líneas":
                    f_libre = px.line(df_res, x=col_x, y=col_y, markers=True, title=f"Evolución de {col_y} por {col_x}", template="plotly_dark")
                elif tipo_g == "Dispersión":
                    f_libre = px.scatter(df_res, x=col_x, y=col_y, title=f"Dispersión de {col_y} vs {col_x}", template="plotly_dark")
                elif tipo_g == "Torta":
                    f_libre = px.pie(df_res, names=col_x, values=col_y, title=f"Distribución de {col_y} por {col_x}", template="plotly_dark")

                f_libre.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=400)
                st.plotly_chart(f_libre, use_container_width=True)

# -----------------------------------------------------------------------------
# MODO 3: EXPLORADOR DEL DATA MART
# -----------------------------------------------------------------------------
elif modo == "🔍 Explorador del Data Mart":
    st.subheader("🔍 Explorador Multidimensional del Data Mart")
    st.markdown("Visualización de esquemas, granularidad y volumen de registros en las tablas del modelo estrella.")

    tablas_dw = ["FACT_COMPETENCIA", "DIM_EQUIPO", "DIM_DIVISION", "DIM_PAIS", "DIM_TIEMPO", "V_PARTICIPACION"]
    sel_tabla = st.selectbox("Seleccione una tabla o vista:", tablas_dw)

    with st.spinner("Leyendo metadatos y muestra..."):
        sql_count = f"SELECT COUNT(*) AS total_registros FROM {sel_tabla};"
        df_cnt, _, _ = conexion.ejecutar_consulta(sql_count, st.session_state["tipo_origen"], st.session_state["cfg_mysql"])
        
        sql_sample = f"SELECT * FROM {sel_tabla} LIMIT 25;"
        df_sample, _, _ = conexion.ejecutar_consulta(sql_sample, st.session_state["tipo_origen"], st.session_state["cfg_mysql"])

    if not df_cnt.empty:
        total_filas = df_cnt.iloc[0, 0]
        st.metric("Total de registros en esta tabla", f"{total_filas:,}")

    st.markdown(f"#### Muestra de los primeros registros de `{sel_tabla}`:")
    st.dataframe(df_sample, use_container_width=True)

    if sel_tabla in consultas_base.DICCIONARIO_TABLAS:
        st.markdown(f"#### Atributos y Claves de `{sel_tabla}`:")
        columnas_info = consultas_base.DICCIONARIO_TABLAS[sel_tabla]
        df_info = pd.DataFrame(columnas_info, columns=["Campo", "Tipo / Restricción", "Descripción"])
        st.table(df_info)
