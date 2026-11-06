import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Configuración para que el dashboard ocupe toda la pantalla y use modo oscuro por defecto
st.set_page_config(page_title="LoL Analytics", layout="wide")
st.title("League of Legends Player Performance")

# 1. Conexión a TiDB con caché para no consultar la BD en cada clic
@st.cache_data
def load_data():
    secrets = st.secrets["tidb"]
    conexion = f"mysql+pymysql://{secrets['username']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/{secrets['database']}"
    engine = create_engine(conexion)
    query = "SELECT * FROM `fact_player,match_stats`"
    return pd.read_sql(query, engine)

df = load_data()

# 2. Filtro interactivo (Slicer)
jugadores = df['summoner_name'].unique()
jugador_seleccionado = st.selectbox("Selecciona un Invocador", jugadores)

# Filtrar el modelo de datos (Reemplaza el filtro manual de Power BI)
df_filtrado = df[df['summoner_name'] == jugador_seleccionado]

# 3. Cálculo de KPIs
victorias = df_filtrado['win'].sum()
partidas = len(df_filtrado)
win_rate = (victorias / partidas * 100) if partidas > 0 else 0

kills = df_filtrado['kills'].sum()
assists = df_filtrado['assists'].sum()
deaths = df_filtrado['deaths'].sum()
kda = (kills + assists) / deaths if deaths > 0 else 0

daño_total = df_filtrado['total_damage'].sum()

# 4. Tarjetas de métricas (Cards)
col1, col2, col3 = st.columns(3)
col1.metric("Win Rate %", f"{win_rate:.1f}%")
col2.metric("KDA Promedio", f"{kda:.2f}")
col3.metric("Daño Total", f"{daño_total:,.0f}")

# 5. Gráfico de barras (Daño o KDA por campeón)
st.subheader("Daño Total por Campeón")
df_campeones = df_filtrado.groupby('champion_name')['total_damage'].sum().reset_index()
st.bar_chart(df_campeones.set_index('champion_name'))