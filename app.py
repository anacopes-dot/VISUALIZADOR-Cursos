import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Visualizador de Datos", layout="wide")
st.title("📊 Mi Visualizador de Excel y Google Sheets")

# --- SECCIÓN DE CARGA DE DATOS ---
st.sidebar.header("1. Cargar Origen de Datos")
opcion = st.sidebar.radio("Seleccionar método:", ["Subir Archivo Excel", "Link de Google Sheets"])

df = None

if opcion == "Subir Archivo Excel":
    archivo_subido = st.sidebar.file_uploader("Arrastrá tu archivo .xlsx aquí", type=["xlsx"])
    if archivo_subido is not None:
        try:
            df = pd.read_excel(archivo_subido)
            st.success("¡Excel cargado con éxito!")
        except Exception as e:
            st.error(f"Error al leer el archivo Excel: {e}")

elif opcion == "Link de Google Sheets":
    url_input = st.sidebar.text_input("Pegá la URL completa de tu Google Sheet:")
    if url_input:
        try:
            # Truco para transformar la URL normal en formato de exportación CSV
            if "edit?" in url_input:
                url_csv = url_input.split("/edit?")[0] + "/export?format=csv"
            elif "edit#" in url_input:
                url_csv = url_input.split("/edit#")[0] + "/export?format=csv"
            else:
                url_csv = url_input
            
            df = pd.read_csv(url_csv)
            st.success("¡Google Sheet conectado con éxito!")
        except Exception as e:
            st.error("Error al conectar. Asegurate de que el Google Sheet esté configurado como 'Cualquier persona con el enlace puede ver'.")

# --- SECCIÓN DE VISUALIZACIÓN ---
if df is not None:
    st.write("### 🔍 Vista previa de los datos")
    st.dataframe(df.head(10)) # Muestra las primeras 10 filas

    # Detectar columnas disponibles
    columnas = df.columns.tolist()
    
    st.write("### 📈 Configuración del Gráfico")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        eje_x = st.selectbox("Eje X (Categorías o Fechas):", columnas)
    with col2:
        eje_y = st.selectbox("Eje Y (Valores Numéricos):", columnas)
    with col3:
        tipo_grafico = st.selectbox("Tipo de Gráfico:", ["Barras", "Líneas", "Dispersión", "Tarta"])

    # Generar el gráfico interactivo con Plotly
    st.write("### 📊 Resultado")
    if tipo_grafico == "Barras":
        fig = px.bar(df, x=eje_x, y=eje_y, title=f"{eje_y} por {eje_x}")
    elif tipo_grafico == "Líneas":
        fig = px.line(df, x=eje_x, y=eje_y, title=f"Evolución de {eje_y} por {eje_x}")
    elif tipo_grafico == "Dispersión":
        fig = px.scatter(df, x=eje_x, y=eje_y, title=f"Relación entre {eje_x} y {eje_y}")
    elif tipo_grafico == "Tarta":
        fig = px.pie(df, names=eje_x, values=eje_y, title=f"Distribución de {eje_y}")

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👋 Por favor, subí un archivo Excel o pegá un link de Google Sheets en la barra lateral para empezar.")
