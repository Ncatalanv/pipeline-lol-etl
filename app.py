import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go

#Importación ETL
from extract import RiotDataExtractor
from transform import transform_match_data
from load import load_to_database

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

# 3. BÚSQUEDA DE JUGADOR Y ETL
busqueda = st.text_input("🔍 Busca un Invocador (Obligatorio incluir Tag, Ej: Faker#KR1)")

if not busqueda:
    st.info("👆 Escribe el nombre de un jugador y su tag para ver sus estadísticas o descargarlas.")
    st.stop()

# Validar formato Riot ID
if "#" not in busqueda:
    st.error("⚠️ Formato incorrecto. Debes incluir el '#' y el Tag (Ejemplo: miNombre#LAS)")
    st.stop()

# Armar el string de conexión a TiDB desde los secrets de Streamlit
secrets = st.secrets["tidb"]
db_url = f"mysql+pymysql://{secrets['username']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/{secrets['database']}"

# Filtrar base local
# Filtrar por "Nombre#TAG" ignorando mayúsculas y espacios
df_filtrado = df[df['summoner_name'].str.lower() == busqueda.strip().lower()]

# Si el jugador no existe localmente, activar el Pipeline
if df_filtrado.empty:
    st.warning(f"El invocador '{busqueda}' no está en la base de datos local.")
    
    if st.button("Extraer datos desde Riot Games"):
        with st.spinner(f"Ejecutando pipeline ETL para {busqueda}..."):
            try:
                # --- PREPARACIÓN DE ENTORNO PARA LA NUBE ---
                # Inyectamos los secrets en el sistema operativo para que tus scripts crean que leen un .env
                os.environ["RIOT_API_KEY"] = st.secrets["riot"]["api_key"]
                os.environ["DB_CONNECTION_STRING"] = db_url
                
                # Separar nombre y tag para la API
                game_name, tag_line = busqueda.split("#")
                game_name = game_name.strip()
                tag_line = tag_line.strip()
                
                # --- EXTRACCIÓN ---
                extractor = RiotDataExtractor()
                puuid = extractor.get_puuid(game_name, tag_line)
                match_ids = extractor.get_match_ids(puuid, count=10) # Trae las últimas 10 partidas
                
                datos_crudos = []
                for m_id in match_ids:
                    detalle = extractor.get_match_detail(m_id)
                    if detalle:
                        datos_crudos.append(detalle)
                
                # --- TRANSFORMACIÓN ---
                # Pasamos la lista de JSONs y nos devuelve el DataFrame de Pandas limpio
                df_limpio = transform_match_data(datos_crudos)
                
                # --- CARGA ---
                # Usa el string de conexión que inyectamos arriba y sube a TiDB
                # Nota: usamos el nombre exacto de la tabla con los acentos graves (backticks) por si SQL lo requiere
                load_to_database(df_limpio, table_name="`fact_player,match_stats`")
                
                # --- FIN DEL PIPELINE ---
                st.cache_data.clear()
                st.success("¡Pipeline completado! Datos insertados en TiDB. Recargando...")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error en la ejecución del ETL: {e}")
    st.stop()

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

# 6. CUADRÍCULA INFERIOR
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