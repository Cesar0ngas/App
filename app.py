import streamlit as st
import numpy as np
import altair as alt
import time
from pymongo import MongoClient
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Analysis",
    page_icon="🦝",
)

# Función para cargar datos con cache para evitar recarga completa
@st.cache_data
def load_data():
    try:
        client = MongoClient("mongodb+srv://cesarcorrea:aRi2Ys8pCaXcZZhd@cluster0.rwqzs.mongodb.net/instagram_data?retryWrites=true&w=majority&serverSelectionTimeoutMS=5000")
        db = client["instagram_data"]
        collection = db["posts"]
        data = list(collection.find({}, {'_id': 0, 'username': 1, 'likes': 1, 'comments': 1}))
        return pd.json_normalize(data)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        st.error("Error de conexión a la base de datos: No se pudo conectar a MongoDB.")
        st.error(f"Detalles del error: {err}")
        return pd.DataFrame()  # Retornar un DataFrame vacío



# Menú de navegación en la barra lateral (Welcome y Data Analysis)
page = st.sidebar.selectbox("Select a Page", ["Welcome", "Data Analysis"])

if page == "Welcome":
    st.write("# Post Analysis Instagram! 📸")
    st.write("""
        Welcome to the Instagram Analytics app, a tool designed to provide valuable insights into engagement and content on Instagram.
        This app helps brands, influencers, and social media analysts better understand user behavior and content reception on Instagram.

        ### What can you do with this app?
        - Visualize Engagement: Explore which users have the most engagement on their posts through graphs showing the number of likes and comments.
        - Content Status: Quickly identify the proportion of active versus inactive content to understand engagement dynamics.
        - Post Timing: See how posting activity fluctuates over time to spot significant patterns or events.
        - User Popularity: Find out who the most popular users are in terms of likes, which can be useful for collaboration or marketing strategies.
        - Comment Content Analysis: Through a word cloud, visualize the most frequent words in comments to get an idea of ​common trends and themes.
        - Comment Distribution: Analyze how comments are distributed on posts to measure the degree of audience engagement.
    """)

elif page == "Data Analysis":
    st.write("# Data Analysis Page")
    
    # Agregar un "choro" o texto introductorio
    st.write("""
        En esta sección, podrás analizar la interacción de los usuarios de Instagram en base a sus publicaciones. 
        Aquí podrás visualizar la relación entre los likes y comentarios de cada usuario seleccionado. 
        Utiliza el botón para cargar los datos y luego selecciona los usuarios de interés para generar un gráfico interactivo.
        
        ¡Explora y descubre quiénes son los usuarios más populares y con mayor nivel de engagement en sus publicaciones! 📊
    """)
    
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False

    # Botón para cargar datos y barra de progreso
    if st.button("Load Data") or st.session_state.data_loaded:
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        # Cargar los datos solo si no están en el estado de sesión
        if not st.session_state.data_loaded:
            data_load_state = st.text('Cargando datos...')
            for i in range(1, 101):
                time.sleep(0.01)
                progress_bar.progress(i)
                status_text.text(f"{i}% Complete")
            
            st.session_state.df = load_data()
            st.session_state.data_loaded = True  # Marcar que los datos se han cargado
            progress_bar.empty()
            status_text.empty()
            data_load_state.text("¡Datos cargados con éxito!")
        
        # Lista de usuarios únicos
        df = st.session_state.df
        unique_users = df['username'].unique()
        st.write(f"Total de usuarios únicos cargados: {len(unique_users)}")
        
        # Selección de usuarios y visualización de los datos filtrados (sin valores seleccionados por defecto)
        usernames = st.multiselect("Elige usuarios", unique_users)
        if usernames:
            filtered_data = df[df['username'].isin(usernames)]
            
            # Gráfico de dispersión para mostrar relación entre likes y comments
            scatter_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
                x='likes:Q',
                y='comments:Q',
                color='username:N',
                tooltip=['username', 'likes', 'comments']
            ).properties(
                title='Relación entre Likes y Comentarios por Usuario'
            )
            
            st.altair_chart(scatter_plot, use_container_width=True)
        else:
            st.write("Selecciona al menos un usuario para visualizar el gráfico.")
