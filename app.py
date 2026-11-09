import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Analíticas League of Legends LAS", layout="wide", initial_sidebar_state="collapsed")
st.title("League of Legends Rendimiento de Invocadores - LAS")

# 2. CONEXIÓN Y CARGA DE DATOS
@st.cache_data
def load_data():
    secrets = st.secrets["tidb"]
    conexion = f"mysql+pymysql://{secrets['username']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/{secrets['database']}"
    engine = create_engine(conexion)
    # Recuerda mantener los backticks para el nombre de tu tabla
    query = "SELECT * FROM `fact_player,match_stats`"
    return pd.read_sql(query, engine)

df = load_data()

# 3. FILTROS GLOBALES
jugadores = df['summoner_name'].unique()
jugador_seleccionado = st.selectbox("Busca un Invocador", jugadores)
df_filtrado = df[df['summoner_name'] == jugador_seleccionado]

# 4. MÉTRICAS GLOBALES
victorias = df_filtrado['win'].sum()
partidas = len(df_filtrado)
derrotas = partidas - victorias
win_rate = (victorias / partidas * 100) if partidas > 0 else 0

kills = df_filtrado['kills'].sum()
assists = df_filtrado['assists'].sum()
deaths = df_filtrado['deaths'].sum()
kda = (kills + assists) / deaths if deaths > 0 else 0
daño_total = df_filtrado['total_damage'].sum()

st.markdown("---")

# 5. RESUMEN SUPERIOR (Gráfico de Anillo y Tarjetas)
col_kpi1, col_kpi2, col_kpi3, col_grafico = st.columns([1, 1, 1, 1])

col_kpi1.metric("Win Rate %", f"{win_rate:.1f}%")
col_kpi2.metric("KDA Promedio", f"{kda:.2f}")
col_kpi3.metric("Daño Total", f"{daño_total:,.0f}")

with col_grafico:
    # Gráfico de anillo
    fig = go.Figure(data=[go.Pie(
        labels=['Victorias', 'Derrotas'], 
        values=[victorias, derrotas], 
        hole=.7, 
        marker_colors=['#3b82f6', '#ef4444']
    )])
    fig.update_layout(
        showlegend=False, 
        margin=dict(t=0, b=0, l=0, r=0),
        height=150, # Altura reducida para que encaje con los KPIs
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 6. CUADRÍCULA INFERIOR (Estilo OP.GG: 1/3 Izquierda, 2/3 Derecha)
col_izq, col_der = st.columns([1, 2])

# --- COLUMNA IZQUIERDA: Estilo de Juego ---
with col_izq:
    st.subheader("Estilo de juego")
    
    # Aquí puedes dinamizar estos valores calculándolos desde tu DataFrame
    st.write("Mago")
    st.progress(0.89)
    
    st.write("Tirador")
    st.progress(0.06)
    
    st.write("Luchador")
    st.progress(0.05)

# --- COLUMNA DERECHA: Historial de Partidas ---
with col_der:
    st.subheader("Partidas Recientes")

    #Ordenado de mayor a menor para ver las últimas partidas primero
    try:
        ultimas_partidas = df_filtrado.sort_values(by='match_id', ascending=False).head(10)
    except KeyError:
        ultimas_partidas = df_filtrado.head(10) # Fallback si no hay columna de fecha
    
    for index, row in ultimas_partidas.iterrows():
        bg_color = "#28344e" if row['win'] else "#59343b"
        borde_color = "#5383e8" if row['win'] else "#e84057"
        resultado = "Victoria" if row['win'] else "Derrota"
        
        # Inyección de la tarjeta HTML para cada partida
        st.markdown(f"""
        <div style="
            background-color: {bg_color}; 
            border-radius: 8px; 
            padding: 15px; 
            margin-bottom: 10px; 
            display: flex; 
            justify-content: space-between;
            align-items: center;
            border-left: 6px solid {borde_color};
        ">
            <div>
                <h4 style="margin:0; color: {borde_color}">{resultado}</h4>
                <p style="margin:0; font-size:12px; color: #9e9eb1;">{row['champion_name']}</p>
            </div>
            <div style="text-align: center;">
                <h3 style="margin:0; font-size: 16px;">{row['kills']} / <span style="color: #e84057;">{row['deaths']}</span> / {row['assists']}</h3>
                <p style="margin:0; font-size:12px; color: #9e9eb1;">KDA</p>
            </div>
            <div style="text-align: right;">
                <p style="margin:0; font-size:12px;">Duración: {row.get('duration_minutes', 'N/A')} min</p>
            </div>
        </div>
        """, unsafe_allow_html=True)