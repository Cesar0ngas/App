import streamlit as st
import numpy as np
import altair as alt
import time
from pymongo import MongoClient
import pandas as pd
import pymongo
import matplotlib.pyplot as plt
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Instagram Analysis",
    page_icon="🦝",
)

# Función para cargar datos con caché
@st.cache_data
def load_data():
    try:
        # Conexión a MongoDB
        MONGO_URI = "mongodb+srv://cesarcorrea:MfXGcFDodXyjA2zW@cluster0.rwqzs.mongodb.net/?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        
        db = client["instagram_data"]
        collection = db["posts"]
        
        # Extracción de datos
        data = list(collection.find({}, {'_id': 0, 'username': 1, 'likes': 1, 'comments': 1}))
        return pd.json_normalize(data)
    
    except pymongo.errors.ServerSelectionTimeoutError as err:
        st.error("Error de conexión a la base de datos: No se pudo conectar a MongoDB.")
        st.error(f"Detalles del error: {err}")
        return pd.DataFrame()  # Retornar un DataFrame vacío

# Menú de navegación en la barra lateral
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
    
    st.write("""
        In this section, you will be able to analyze the interaction of Instagram users based on their posts. 
        Here you will be able to visualize the relationship between likes and comments for each selected user. 
        Use the button to load the data and then select the users of interest to generate an interactive graph.
        
        Explore and discover who are the most popular users with the highest level of engagement on their posts! 📊
    """)
    
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False

    # Botón para cargar datos y barra de progreso
    if st.button("Load Data") or st.session_state.data_loaded:
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        if not st.session_state.data_loaded:
            data_load_state = st.text('Loading Data...')
            for i in range(1, 101):
                time.sleep(0.01)
                progress_bar.progress(i)
                status_text.text(f"{i}% Complete")
            
            st.session_state.df = load_data()
            st.session_state.data_loaded = True
            progress_bar.empty()
            status_text.empty()
            data_load_state.text("¡Data successfully loaded!")
        
        # Verificar si hay datos cargados
        df = st.session_state.df
        if df.empty:
            st.error("No data found. Verify the connection and the database query.")
        else:
            st.write("Data loaded:")
            st.dataframe(df, use_container_width=True)  # Mostrar todo el dataframe
            unique_users = df['username'].unique()
            st.write(f"Total unique users loaded: {len(unique_users)}")
            
            # Selección de usuarios y visualización de los datos filtrados
            usernames = st.multiselect("Choose users", unique_users)
            if usernames:
                filtered_data = df[df['username'].isin(usernames)]
                
                # Gráfico de Altair (Interacción entre Likes y Comentarios)
                scatter_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
                    x='likes:Q',
                    y='comments:Q',
                    color='username:N',
                    tooltip=['username', 'likes', 'comments']
                ).properties(
                    title='Ratio of Likes to Comments per User'
                )
                st.altair_chart(scatter_plot, use_container_width=True)
                
                # Gráfico de Matplotlib (Barras Apiladas de Likes y Comentarios)
                st.write("### Chart of Likes and Comments by User (Matplotlib)")
                fig, ax = plt.subplots()
                ax.bar(filtered_data['username'], filtered_data['likes'], label='Likes', color='skyblue')
                ax.bar(filtered_data['username'], filtered_data['comments'], bottom=filtered_data['likes'], label='Comments', color='orange')
                ax.set_ylabel("Quantity")
                ax.set_title("Likes and Comments per User")
                ax.legend()
                st.pyplot(fig)
                
                # Gráfico de Plotly (Gráfico de Barras Interactivo)
                st.write("### Interactive Chart of Likes and Comments per User (Plotly)")
                fig_plotly = px.bar(
                    filtered_data,
                    x='username',
                    y=['likes', 'comments'],
                    title="Likes and Comments per User",
                    labels={'value': 'Quantity', 'variable': 'Metric'},
                    barmode='group'
                )
                st.plotly_chart(fig_plotly)
                
            else:
                st.write("Select at least one user to display the graph.")
