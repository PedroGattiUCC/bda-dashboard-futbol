"""Tablero Analítico Dinámico — Data Mart de Competencia de Fútbol (HEFESTO v2)
Optimizado para la Exposición Final en Clase con Render y Clever Cloud MySQL.

Centrado en las 6 Preguntas de Negocio Oficiales Seleccionadas,
con múltiples gráficos interactivos por pregunta, KPIs destacados y editor SQL en vivo.
"""

import os
import sys
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

import plotly.express as px
import plotly.graph_objects as go

# Paleta corporativa deportiva
COLOR_AZUL = "#2a78d6"
COLOR_NARANJA = "#eb6834"
COLOR_VERDE = "#1baf7a"
COLOR_ROJO = "#e04f5f"
COLOR_GRIS = "#898781"
TEMA_PLOTLY = "plotly_dark"

# -----------------------------------------------------------------------------
# GESTIÓN DE ESTADO Y CONECTIVIDAD
# -----------------------------------------------------------------------------
if "tipo_origen" not in st.session_state:
    st.session_state["tipo_origen"] = "clever" if os.environ.get("MYSQL_HOST") else "sqlite"

if "cfg_mysql" not in st.session_state:
    st.session_state["cfg_mysql"] = conexion.obtener_config_por_defecto()

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR): CONECTIVIDAD Y NAVEGACIÓN
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚽ Menú Principal")

    modo = st.radio(
        "Modo de Exposición:",
        options=[
            "📊 6 Preguntas Oficiales (Entrega Final)",
            "💻 Consola SQL Libre (Preguntas del Docente)",
            "🔍 Explorador del Data Mart"
        ]
    )

    st.divider()

    st.markdown("### ⚙️ Conexión al Data Mart")
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
        with st.expander("🔧 Credenciales MySQL", expanded=False):
            host = st.text_input("Host:", value=st.session_state["cfg_mysql"].get("host", "localhost"))
            port = st.number_input("Puerto:", value=int(st.session_state["cfg_mysql"].get("port", 3306)), step=1)
            user = st.text_input("Usuario:", value=st.session_state["cfg_mysql"].get("user", "root"))
            password = st.text_input("Contraseña:", value=st.session_state["cfg_mysql"].get("password", ""), type="password")
            database = st.text_input("Base de datos:", value=st.session_state["cfg_mysql"].get("database", "dw_competencia_futbol"))
            
            st.session_state["cfg_mysql"] = {
                "host": host, "port": port, "user": user, "password": password, "database": database
            }

    col_btn_test, _ = st.columns([1, 0.1])
    if col_btn_test.button("⚡ Test Conexión", use_container_width=True):
        with st.spinner("Probando conexión..."):
            ok, msg, necesita_migrar = conexion.probar_conexion(
                st.session_state["tipo_origen"],
                st.session_state["cfg_mysql"]
            )
            st.session_state["test_status"] = (ok, msg, necesita_migrar)

    if "test_status" in st.session_state:
        ok, msg, necesita_migrar = st.session_state["test_status"]
        if ok:
            st.success(msg)
        else:
            if necesita_migrar:
                st.warning(msg)
                st.markdown("👇 **Tu base en Clever Cloud está vacía. Hacé clic para poblarla:**")
                if st.button("🚀 Cargar Data Mart en Clever Cloud (1 Clic)", type="primary", use_container_width=True):
                    prog_bar = st.progress(0)
                    prog_lbl = st.empty()
                    def cb(texto, val):
                        prog_lbl.caption(texto)
                        prog_bar.progress(val)

                    ok_mig, msg_mig = conexion.cargar_data_mart_en_clevercloud(st.session_state["cfg_mysql"], cb)
                    if ok_mig:
                        st.success(msg_mig)
                        del st.session_state["test_status"]
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg_mig)
            else:
                st.error(msg)
                if st.button("👉 Conmutar a Modo Offline (SQLite)", use_container_width=True):
                    st.session_state["tipo_origen"] = "sqlite"
                    if "test_status" in st.session_state:
                        del st.session_state["test_status"]
                    st.rerun()

    st.divider()
    ver_complementarias = st.checkbox("🔍 Habilitar preguntas 7 a 12 (opcional)", value=False)

    st.markdown("""
    **Metodología:** HEFESTO v2  
    **Proceso:** Competencia entre Equipos  
    **Granularidad:** 1 fila por partido  
    """)

# -----------------------------------------------------------------------------
# ENCABEZADO PRINCIPAL Y ESTADO
# -----------------------------------------------------------------------------
col_header, col_badge = st.columns([3, 1.2])

with col_header:
    st.title("⚽ Tablero Analítico — Data Mart de Fútbol")
    st.caption("Bases de Datos Avanzadas | Defensa Oral Final | Metodología HEFESTO v2")

with col_badge:
    if st.session_state["tipo_origen"] == "clever":
        st.success("🟢 **Clever Cloud MySQL** (Nube)")
    elif st.session_state["tipo_origen"] == "local":
        st.info("💻 **MySQL Local** (`localhost:3306`)")
    else:
        st.warning("🛡️ **Offline Activo** (132.256 partidos)")

st.write("")

# -----------------------------------------------------------------------------
# MODO 1: LAS 6 PREGUNTAS OFICIALES (CON MÚLTIPLES GRÁFICOS Y KPIS)
# -----------------------------------------------------------------------------
if modo == "📊 6 Preguntas Oficiales (Entrega Final)":
    # Lista de preguntas a mostrar (las 6 oficiales por defecto, o las 12 si se activó el checkbox)
    if ver_complementarias:
        catalogo = consultas_base.PREGUNTAS_CATALOGO
    else:
        catalogo = consultas_base.PREGUNTAS_OFICIALES

    opciones_preguntas = [f"Pregunta {p['id']}: {p['titulo']}" for p in catalogo]
    
    # Selector prominente
    idx_p = st.selectbox(
        "🎯 Seleccione la Pregunta de Negocio a exponer:",
        range(len(catalogo)),
        format_func=lambda i: opciones_preguntas[i]
    )
    pregunta = catalogo[idx_p]
    pid = pregunta["id"]

    # Fila de Filtros Rápidos Dinámicos
    st.markdown("#### 🎛️ Parámetros Dinámicos en Vivo")
    c_filt1, c_filt2, c_filt3 = st.columns([1.2, 1, 1])
    params = {}

    if pid == 1:
        with c_filt1:
            params["equipo"] = st.text_input("Club a analizar:", value="Nottm Forest", help="Podés cambiar a 'Arsenal', 'Real Madrid', 'Barcelona', etc.")
        with c_filt2:
            params["anios"] = st.slider("Ventana de años:", min_value=1, max_value=10, value=5)
        with c_filt3:
            st.info("💡 Consejo: Cambiá el club frente al profesor para ver el recálculo dinámico.")

    elif pid == 2:
        with c_filt1:
            modo_pareja = st.checkbox("Comparar enfrentamiento libre entre 2 clubes", value=False)
            params["modo_pareja"] = modo_pareja
        if modo_pareja:
            with c_filt2:
                params["equipo_a"] = st.text_input("Equipo A:", value="Arsenal")
            with c_filt3:
                params["equipo_b"] = st.text_input("Equipo B:", value="Tottenham")
        else:
            with c_filt2:
                st.caption("Analizando los 6 derbis oficiales del Data Mart.")
            with c_filt3:
                st.info("Activá el checkbox para comparar cualquier par de clubes.")

    elif pid == 3:
        with c_filt1:
            params["limit"] = st.slider("Cantidad de ligas a visualizar:", min_value=5, max_value=15, value=15)
        with c_filt2:
            st.caption("Compara victorias locales vs visitantes y goles.")
        with c_filt3:
            st.info("Muestra ventaja neta y comparativa de goles.")

    elif pid == 4:
        with c_filt1:
            params["pct_min_elo"] = st.slider("% mínimo de partidos con Elo:", min_value=50, max_value=100, value=80)
        with c_filt2:
            params["limit"] = st.slider("Ligas a visualizar:", min_value=5, max_value=15, value=15)
        with c_filt3:
            st.caption("Menor desvío estándar = Mayor paridad.")

    elif pid == 5:
        with c_filt1:
            params["min_partidos"] = st.number_input("Partidos mínimos con dato:", value=1000, step=100)
        with c_filt2:
            params["orden"] = st.selectbox("Ordenar ranking por:", ["amarillas_x_partido", "rojas_x_partido"], index=0)
        with c_filt3:
            params["limit"] = st.slider("Ligas:", min_value=5, max_value=15, value=12)

    elif pid == 6:
        with c_filt1:
            params["anios"] = st.slider("Ventana de tiempo (años):", min_value=1, max_value=10, value=5)
        with c_filt2:
            params["min_partidos"] = st.number_input("Partidos visitante mínimos:", value=60, step=10)
        with c_filt3:
            params["limit"] = st.slider("Top equipos:", min_value=5, max_value=25, value=15)

    elif pid > 6:
        with c_filt1:
            params["limit"] = st.slider("Cantidad de registros:", min_value=5, max_value=25, value=15)

    # Construir consulta SQL parametrizada
    sql_base = pregunta["sql_builder"](params).strip()

    # Ejecución de la consulta
    with st.spinner("Consultando el Data Mart multidimensional..."):
        df, duracion, error = conexion.ejecutar_consulta(
            sql_base,
            tipo_origen=st.session_state["tipo_origen"],
            config=st.session_state["cfg_mysql"]
        )

    if error:
        st.error(f"❌ Error al consultar la base de datos: {error}")
    elif df.empty:
        st.warning("⚠️ La consulta no arrojó resultados con los filtros actuales.")
    else:
        # PESTAÑAS INTUITIVAS PARA LA EXPOSICIÓN
        tab_graficos, tab_tabla, tab_sql, tab_conclusion = st.tabs([
            "📊 Visualizaciones y KPIs",
            "📋 Datos Tabulados",
            "💻 Consulta SQL en Vivo",
            "💡 Conclusión de Negocio"
        ])

        # ---------------------------------------------------------------------
        # PESTAÑA 1: VISUALIZACIONES Y KPIS (MÚLTIPLES GRÁFICOS POR PREGUNTA)
        # ---------------------------------------------------------------------
        with tab_graficos:
            # --- PREGUNTA 1: EVOLUCIÓN DE ELO ---
            if pid == 1:
                # KPIs
                f_ini = df.iloc[0]["elo_promedio"]
                f_fin = df.iloc[-1]["elo_promedio"]
                var_neta = round(f_fin - f_ini, 1)
                pct_crec = round(100.0 * var_neta / f_ini, 1)
                total_partidos = int(df["partidos"].sum())

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Elo Inicial", f"{f_ini:.1f}")
                k2.metric("Elo Final", f"{f_fin:.1f}")
                k3.metric("Crecimiento Neto", f"{var_neta:+.1f} pts", delta=f"{pct_crec:+.1f} %")
                k4.metric("Partidos Disputados", f"{total_partidos:,}")

                # Gráficos en 2 columnas
                g_col1, g_col2 = st.columns([1.5, 1])

                with g_col1:
                    # Gráfico 1: Evolución con banda Min-Max
                    fig1 = go.Figure()
                    fig1.add_trace(go.Scatter(
                        x=df["anio"], y=df["elo_maximo"],
                        mode='lines', line=dict(width=0), showlegend=False
                    ))
                    fig1.add_trace(go.Scatter(
                        x=df["anio"], y=df["elo_minimo"],
                        mode='lines', line=dict(width=0), fill='tonexty',
                        fillcolor='rgba(42, 120, 214, 0.15)', name='Rango Min-Max'
                    ))
                    fig1.add_trace(go.Scatter(
                        x=df["anio"], y=df["elo_promedio"],
                        mode='lines+markers', name='Elo Promedio',
                        line=dict(color=COLOR_AZUL, width=3),
                        marker=dict(size=8, color=COLOR_NARANJA)
                    ))
                    fig1.update_layout(
                        title=f"Evolución de Elo Anual ({params.get('equipo')})",
                        xaxis_title="Año", yaxis_title="Puntaje Elo",
                        template=TEMA_PLOTLY, height=380,
                        margin=dict(l=20, r=20, t=45, b=20)
                    )
                    st.plotly_chart(fig1, use_container_width=True)

                with g_col2:
                    # Gráfico 2: Partidos disputados por año
                    fig2 = px.bar(
                        df, x="anio", y="partidos",
                        title="Partidos Disputados por Año",
                        labels={"anio": "Año", "partidos": "Partidos"},
                        template=TEMA_PLOTLY, color_discrete_sequence=[COLOR_VERDE]
                    )
                    fig2.update_layout(height=380, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig2, use_container_width=True)

                # Gráfico 3: Volatilidad anual (Rango Máx - Mín)
                df_vol = df.copy()
                df_vol["brecha_anual"] = df_vol["elo_maximo"] - df_vol["elo_minimo"]
                fig3 = px.bar(
                    df_vol, x="anio", y="brecha_anual",
                    title="Volatilidad Competitiva Anual (Elo Máximo − Elo Mínimo)",
                    labels={"anio": "Año", "brecha_anual": "Amplitud Elo (pts)"},
                    template=TEMA_PLOTLY, color_discrete_sequence=[COLOR_NARANJA]
                )
                fig3.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig3, use_container_width=True)

            # --- PREGUNTA 2: HISTORIAL DE CLÁSICOS ---
            elif pid == 2:
                if params.get("modo_pareja", False):
                    # Modo libre 2 clubes
                    r = df.iloc[0]
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("Partidos Totales", int(r["partidos"]))
                    k2.metric(f"Victorias {params.get('equipo_a')}", f"{int(r['gana_a'])} ({r['pct_gana_a']} %)")
                    k3.metric("Empates", f"{int(r['empates'])} ({r['pct_empate']} %)")
                    k4.metric(f"Victorias {params.get('equipo_b')}", f"{int(r['gana_b'])} ({r['pct_gana_b']} %)")

                    g_col1, g_col2 = st.columns(2)
                    with g_col1:
                        fig1 = px.pie(
                            values=[r["pct_gana_a"], r["pct_empate"], r["pct_gana_b"]],
                            names=[params.get("equipo_a"), "Empate", params.get("equipo_b")],
                            title="Distribución de Resultados (%)",
                            hole=0.45,
                            color_discrete_sequence=[COLOR_AZUL, COLOR_GRIS, COLOR_NARANJA],
                            template=TEMA_PLOTLY
                        )
                        fig1.update_layout(height=380)
                        st.plotly_chart(fig1, use_container_width=True)

                    with g_col2:
                        fig2 = px.bar(
                            x=[params.get("equipo_a"), "Empate", params.get("equipo_b")],
                            y=[r["gana_a"], r["empates"], r["gana_b"]],
                            title="Cantidad Absoluta de Partidos",
                            labels={"x": "Resultado", "y": "Partidos"},
                            color_discrete_sequence=[COLOR_AZUL],
                            template=TEMA_PLOTLY
                        )
                        fig2.update_layout(height=380)
                        st.plotly_chart(fig2, use_container_width=True)
                else:
                    # Modo clásico oficial múltiple
                    k1, k2, k3 = st.columns(3)
                    k1.metric("Derbis Analizados", len(df))
                    k2.metric("Partidos Totales", f"{int(df['partidos'].sum()):,}")
                    k3.metric("Mayor Diferencia", "Arsenal vs Tottenham (+27 pp)")

                    g_col1, g_col2 = st.columns([1.6, 1])
                    with g_col1:
                        fig1 = px.bar(
                            df, y="clasico", x=["pct_gana_a", "pct_empate", "pct_gana_b"],
                            orientation="h",
                            title="Distribución de Resultados en Clásicos Europeos (% de Partidos)",
                            labels={"value": "% de partidos", "variable": "Resultado", "clasico": "Clásico"},
                            barmode="stack",
                            color_discrete_sequence=[COLOR_AZUL, COLOR_GRIS, COLOR_NARANJA],
                            template=TEMA_PLOTLY
                        )
                        fig1.update_layout(height=400, margin=dict(l=20, r=20, t=45, b=20))
                        st.plotly_chart(fig1, use_container_width=True)

                    with g_col2:
                        fig2 = px.bar(
                            df, y="clasico", x="partidos",
                            orientation="h",
                            title="Volumen de Partidos por Clásico",
                            labels={"partidos": "Total Partidos", "clasico": "Clásico"},
                            color_discrete_sequence=[COLOR_VERDE],
                            template=TEMA_PLOTLY
                        )
                        fig2.update_layout(height=400, margin=dict(l=20, r=20, t=45, b=20))
                        st.plotly_chart(fig2, use_container_width=True)

            # --- PREGUNTA 3: VENTAJA DE LOCALÍA ---
            elif pid == 3:
                # KPIs continentales consolidados
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Victorias Local (Media)", "45.0 %")
                k2.metric("Victorias Visitante (Media)", "28.1 %")
                k3.metric("Ventaja Neta de Local", "+16.9 pp", delta="Local domina")
                k4.metric("Diferencial de Goles", "+0.36 goles", delta="Favor local")

                g_col1, g_col2 = st.columns([1.5, 1])

                with g_col1:
                    # Gráfico 1: Ventaja en puntos porcentuales
                    fig1 = px.bar(
                        df, y="liga", x="ventaja_pp",
                        orientation="h",
                        title="Ventaja de Localía por Liga (% Victoria Local − % Visitante)",
                        labels={"ventaja_pp": "Ventaja (puntos porcentuales)", "liga": "Liga"},
                        color="ventaja_pp",
                        color_continuous_scale="Blues",
                        template=TEMA_PLOTLY
                    )
                    fig1.update_layout(height=420, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig1, use_container_width=True)

                with g_col2:
                    # Gráfico 2: Distribución continental
                    fig2 = px.pie(
                        values=[45.0, 26.9, 28.1],
                        names=["Victoria Local", "Empate", "Victoria Visitante"],
                        title="Distribución Total en Europa (%)",
                        hole=0.45,
                        color_discrete_sequence=[COLOR_AZUL, COLOR_GRIS, COLOR_NARANJA],
                        template=TEMA_PLOTLY
                    )
                    fig2.update_layout(height=420, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig2, use_container_width=True)

                # Gráfico 3: Comparativa de goles Local vs Visitante
                if "goles_local_prom" in df.columns:
                    fig3 = px.bar(
                        df, y="liga", x=["goles_local_prom", "goles_visitante_prom"],
                        barmode="group",
                        orientation="h",
                        title="Comparativa de Goles por Partido: Local vs Visitante",
                        labels={"value": "Promedio de Goles", "variable": "Condición", "liga": "Liga"},
                        color_discrete_sequence=[COLOR_AZUL, COLOR_NARANJA],
                        template=TEMA_PLOTLY
                    )
                    fig3.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig3, use_container_width=True)

            # --- PREGUNTA 4: PARIDAD DE LIGAS ---
            elif pid == 4:
                k1, k2, k3 = st.columns(3)
                k1.metric("Liga Más Pareja", "Segunda División (ESP)", delta="Desvío 72.5")
                k2.metric("2da Más Pareja", "Ligue 2 (FRA)", delta="Desvío 73.8")
                k3.metric("Conclusión Metodológica", "Segundas divisiones superan a Primera")

                g_col1, g_col2 = st.columns([1.5, 1])

                with g_col1:
                    # Gráfico 1: Desvío estándar de la brecha Elo
                    fig1 = px.bar(
                        df, y="liga", x="desvio_brecha_elo",
                        orientation="h",
                        title="Paridad Competitiva: Desvío de Brecha Elo (Menor = Más Pareja)",
                        labels={"desvio_brecha_elo": "Desvío Estándar Elo", "liga": "Liga"},
                        color="desvio_brecha_elo",
                        color_continuous_scale="Greens_r",
                        template=TEMA_PLOTLY
                    )
                    fig1.update_layout(height=420, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig1, use_container_width=True)

                with g_col2:
                    # Gráfico 2: % Empates
                    fig2 = px.bar(
                        df, y="liga", x="pct_empates",
                        orientation="h",
                        title="Porcentaje de Empates por Liga (%)",
                        labels={"pct_empates": "% Empates", "liga": "Liga"},
                        color_discrete_sequence=[COLOR_VERDE],
                        template=TEMA_PLOTLY
                    )
                    fig2.update_layout(height=420, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig2, use_container_width=True)

                # Gráfico 3: Matriz Cuadrante de Paridad
                fig3 = px.scatter(
                    df, x="brecha_elo_media", y="pct_empates",
                    text="liga", size="partidos",
                    title="Cuadrante de Paridad: Brecha Elo Media vs % Empates",
                    labels={"brecha_elo_media": "Brecha Elo Media (pts)", "pct_empates": "% Empates"},
                    template=TEMA_PLOTLY, color="desvio_brecha_elo",
                    color_continuous_scale="Viridis"
                )
                fig3.update_traces(textposition='top center')
                fig3.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig3, use_container_width=True)

            # --- PREGUNTA 5: TARJETAS POR LIGA ---
            elif pid == 5:
                k1, k2, k3 = st.columns(3)
                k1.metric("Líder Amarillas", "Primeira Liga (POR)", delta="5.09 amarillas/partido")
                k2.metric("2do Lugar Amarillas", "La Liga (ESP)", delta="5.02 amarillas/partido")
                k3.metric("Fricción Ibérica", "España y Portugal duplican a Inglaterra y Alemania")

                g_col1, g_col2 = st.columns(2)

                with g_col1:
                    fig1 = px.bar(
                        df, y="liga", x="amarillas_x_partido",
                        orientation="h",
                        title="Tarjetas Amarillas por Partido por Liga",
                        labels={"amarillas_x_partido": "Amarillas / Partido", "liga": "Liga"},
                        color="amarillas_x_partido",
                        color_continuous_scale="YlOrBr",
                        template=TEMA_PLOTLY
                    )
                    fig1.update_layout(height=400, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig1, use_container_width=True)

                with g_col2:
                    fig2 = px.bar(
                        df, y="liga", x="rojas_x_partido",
                        orientation="h",
                        title="Tarjetas Rojas por Partido por Liga",
                        labels={"rojas_x_partido": "Rojas / Partido", "liga": "Liga"},
                        color="rojas_x_partido",
                        color_continuous_scale="Reds",
                        template=TEMA_PLOTLY
                    )
                    fig2.update_layout(height=400, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig2, use_container_width=True)

                # Gráfico 3: Matriz de Fricción
                fig3 = px.scatter(
                    df, x="amarillas_x_partido", y="rojas_x_partido",
                    text="liga", color="pais",
                    title="Matriz de Disciplina: Amarillas vs Rojas (Clúster Ibérico vs Anglosajón)",
                    labels={"amarillas_x_partido": "Amarillas / Partido", "rojas_x_partido": "Rojas / Partido"},
                    template=TEMA_PLOTLY
                )
                fig3.update_traces(textposition='top right', marker=dict(size=12))
                fig3.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig3, use_container_width=True)

            # --- PREGUNTA 6: MEJORES VISITANTES ---
            elif pid == 6:
                top1 = df.iloc[0]
                k1, k2, k3 = st.columns(3)
                k1.metric("Mejor Visitante", f"{top1['equipo']}", delta=f"{top1['pct_victorias']} % victorias")
                k2.metric("Poder de Fuego Fuera", f"{top1['goles_favor_prom']} goles/partido")
                k3.metric("Filtro Mínimo", f"{params.get('min_partidos', 60)} partidos de visitante")

                g_col1, g_col2 = st.columns([1.5, 1])

                with g_col1:
                    fig1 = px.bar(
                        df, y="equipo", x="pct_victorias",
                        orientation="h",
                        text="pct_victorias",
                        title=f"Top {len(df)} Equipos por % de Victorias Fuera de Casa (Últimos {params.get('anios', 5)} Años)",
                        labels={"pct_victorias": "% de Victorias Visitante", "equipo": "Club"},
                        color="pct_victorias",
                        color_continuous_scale="Blues",
                        template=TEMA_PLOTLY
                    )
                    fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig1.update_layout(height=450, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig1, use_container_width=True)

                with g_col2:
                    fig2 = px.bar(
                        df.head(10), y="equipo", x=["goles_favor_prom", "goles_contra_prom"],
                        orientation="h",
                        barmode="group",
                        title="Top 10: Goles a Favor vs Contra (Visitante)",
                        labels={"value": "Promedio Goles", "variable": "Métrica", "equipo": "Club"},
                        color_discrete_sequence=[COLOR_AZUL, COLOR_ROJO],
                        template=TEMA_PLOTLY
                    )
                    fig2.update_layout(height=450, margin=dict(l=20, r=20, t=45, b=20))
                    st.plotly_chart(fig2, use_container_width=True)

                # Gráfico 3: Matriz de Efectividad
                fig3 = px.scatter(
                    df, x="goles_favor_prom", y="pct_victorias",
                    text="equipo", size="partidos_visitante",
                    title="Matriz de Efectividad de Visitante: Goles a Favor vs % Victorias",
                    labels={"goles_favor_prom": "Goles a Favor / Partido", "pct_victorias": "% Victorias"},
                    template=TEMA_PLOTLY, color="pct_victorias", color_continuous_scale="Teal"
                )
                fig3.update_traces(textposition='top center')
                fig3.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig3, use_container_width=True)

            # --- PREGUNTAS COMPLEMENTARIAS (7 a 12) ---
            elif pid > 6:
                st.info(f"Visualizando Pregunta Complementaria {pid}: {pregunta['titulo']}")
                fig = px.bar(df, y=df.columns[0], x=df.columns[1], orientation="h", template=TEMA_PLOTLY)
                st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------------------------
        # PESTAÑA 2: DATOS TABULADOS
        # ---------------------------------------------------------------------
        with tab_tabla:
            st.markdown("#### 📋 Resultados Consolidados sobre el Modelo Estrella")
            st.dataframe(df, use_container_width=True)

            csv_exp = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar Tabla en CSV",
                data=csv_exp,
                file_name=f"pregunta_{pid}_datos.csv",
                mime="text/csv"
            )

        # ---------------------------------------------------------------------
        # PESTAÑA 3: CONSULTA SQL EN VIVO (MODIFICABLE ANTE EL PROFESOR)
        # ---------------------------------------------------------------------
        with tab_sql:
            st.markdown("#### 💻 Consulta SQL Ejecutada sobre el Modelo Estrella")
            st.caption("Esta consulta se ejecuta exclusivamente sobre `FACT_COMPETENCIA` o la vista auxiliar `V_PARTICIPACION`.")
            
            editar_vivo = st.checkbox("✏️ Abrir Editor SQL para modificar la consulta en vivo ante el docente", value=False)
            
            if editar_vivo:
                sql_editado = st.text_area("Editor SQL:", value=sql_base, height=240)
                if st.button("🚀 Re-ejecutar SQL Modificado"):
                    df_custom, d_c, err_c = conexion.ejecutar_consulta(
                        sql_editado,
                        tipo_origen=st.session_state["tipo_origen"],
                        config=st.session_state["cfg_mysql"]
                    )
                    if err_c:
                        st.error(f"Error SQL: {err_c}")
                    else:
                        st.success(f"Consulta ejecutada en {d_c*1000:.1f} ms ({len(df_custom)} filas).")
                        st.dataframe(df_custom, use_container_width=True)
            else:
                st.code(sql_base, language="sql")

        # ---------------------------------------------------------------------
        # PESTAÑA 4: CONCLUSIÓN DE NEGOCIO (HEFESTO)
        # ---------------------------------------------------------------------
        with tab_conclusion:
            st.markdown("#### 💡 Interpretación de Negocio y Decisión para Sponsors")
            st.success(pregunta["conclusion_oficial"])
            st.markdown(f"**Indicadores & Perspectivas:** `{pregunta['indicadores']}`")
            st.markdown(f"**Justificación:** *{pregunta['descripcion']}*")

# -----------------------------------------------------------------------------
# MODO 2: CONSOLA SQL LIBRE (PREGUNTAS DEL PROFESOR)
# -----------------------------------------------------------------------------
elif modo == "💻 Consola SQL Libre (Preguntas del Docente)":
    st.subheader("💻 Consola SQL Libre — Consultas Ad-hoc en Vivo")
    st.markdown("""
    Diseñada para **responder al instante a cualquier requerimiento sorpresa del profesor**.
    Podés usar las plantillas rápidas de 1 clic o redactar consultas SQL desde cero sobre el Data Mart.
    """)

    c_izq, c_der = st.columns([2, 1])

    with c_der:
        st.markdown("#### 📚 Plantillas Rápidas")
        plantillas = consultas_base.PLANTILLAS_SQL_PROFE
        sel_pl = st.selectbox("Seleccione plantilla:", list(plantillas.keys()))
        sql_plantilla = plantillas[sel_pl]

        if st.button("Cargar Plantilla al Editor"):
            st.session_state["sql_consola"] = sql_plantilla.strip()

        with st.expander("📖 Diccionario de Tablas", expanded=False):
            for t_nom, cols in consultas_base.DICCIONARIO_TABLAS.items():
                st.markdown(f"**`{t_nom}`**")
                for c_n, c_t, c_d in cols[:5]:
                    st.caption(f"• `{c_n}`: {c_d}")

    with c_izq:
        if "sql_consola" not in st.session_state:
            st.session_state["sql_consola"] = sql_plantilla.strip()

        sql_input = st.text_area(
            "Editor SQL:",
            value=st.session_state["sql_consola"],
            height=260
        )
        st.session_state["sql_consola"] = sql_input

        btn_run = st.button("▶ Ejecutar Consulta", type="primary", use_container_width=True)

    if btn_run or sql_input:
        df_l, dur_l, err_l = conexion.ejecutar_consulta(
            sql_input,
            tipo_origen=st.session_state["tipo_origen"],
            config=st.session_state["cfg_mysql"]
        )
        if err_l:
            st.error(f"❌ Error SQL: {err_l}")
        elif df_l.empty:
            st.info("ℹ️ Consulta ejecutada con éxito (0 filas devueltas).")
        else:
            st.success(f"✓ {len(df_l)} filas devueltas en {dur_l*1000:.1f} ms.")
            st.dataframe(df_l, use_container_width=True)

            if len(df_l.columns) >= 2 and len(df_l) > 0:
                st.markdown("#### 📊 Generador Rápido de Gráfico")
                g1, g2, g3 = st.columns(3)
                col_x = g1.selectbox("Eje X:", df_l.columns, index=0)
                col_y = g2.selectbox("Eje Y:", df_l.columns, index=min(1, len(df_l.columns)-1))
                tg = g3.selectbox("Tipo:", ["Barras Horizontales", "Barras Verticales", "Líneas", "Dona"])

                if tg == "Barras Horizontales":
                    f_lib = px.bar(df_l, y=col_x, x=col_y, orientation="h", template=TEMA_PLOTLY)
                elif tg == "Barras Verticales":
                    f_lib = px.bar(df_l, x=col_x, y=col_y, template=TEMA_PLOTLY)
                elif tg == "Líneas":
                    f_lib = px.line(df_l, x=col_x, y=col_y, markers=True, template=TEMA_PLOTLY)
                elif tg == "Dona":
                    f_lib = px.pie(df_l, names=col_x, values=col_y, hole=0.45, template=TEMA_PLOTLY)

                st.plotly_chart(f_lib, use_container_width=True)

# -----------------------------------------------------------------------------
# MODO 3: EXPLORADOR DEL DATA MART
# -----------------------------------------------------------------------------
elif modo == "🔍 Explorador del Data Mart":
    st.subheader("🔍 Explorador Multidimensional del Data Mart")
    tablas_dw = ["FACT_COMPETENCIA", "DIM_EQUIPO", "DIM_DIVISION", "DIM_PAIS", "DIM_TIEMPO", "V_PARTICIPACION"]
    sel_t = st.selectbox("Seleccione tabla o vista:", tablas_dw)

    with st.spinner("Cargando..."):
        df_cnt, _, _ = conexion.ejecutar_consulta(f"SELECT COUNT(*) AS total FROM {sel_t};", st.session_state["tipo_origen"], st.session_state["cfg_mysql"])
        df_s, _, _ = conexion.ejecutar_consulta(f"SELECT * FROM {sel_t} LIMIT 25;", st.session_state["tipo_origen"], st.session_state["cfg_mysql"])

    if not df_cnt.empty:
        st.metric("Total de registros", f"{df_cnt.iloc[0, 0]:,}")

    st.markdown("#### Muestra de registros:")
    st.dataframe(df_s, use_container_width=True)
