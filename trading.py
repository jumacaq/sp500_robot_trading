import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import time

# Título de la aplicación
st.title('Robot de Trading para el índice S&P 500')

# Sidebar para interacción con el usuario
st.sidebar.title("Configuración")

# 1. Selector de ticker
ticker = st.sidebar.selectbox("Selecciona el ticker", ["SPY","^GSPC", "AAPL", "GOOGL", "TSLA"], index=0)

# 2. Intervalo de tiempo para actualizar datos
intervalo = st.sidebar.slider("Frecuencia de actualización (min)", 1, 15, 5)

# 3. Rango de fechas
fecha_inicio = st.sidebar.date_input("Fecha de inicio", pd.to_datetime("2010-01-01"))
fecha_fin = st.sidebar.date_input("Fecha de fin", pd.to_datetime("today"))

# 5. Botón para ejecutar el análisis
ejecutar = st.sidebar.button("Ejecutar análisis")

# Función para descargar y actualizar datos en tiempo real
def datos_historicos(ticker, start_date, end_date):
    datos = yf.download(ticker, start=start_date, end=end_date)
    datos = datos[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
    return datos

# Resto de las funciones del robot (extraer tendencia, limpiar datos, tomar decisiones, visualización)

def extraer_tendencia(datos_SP500):
    precio_actual = datos_SP500['Close'].iloc[-1]
    precio_previo = datos_SP500['Close'].iloc[-2]
    tendencia = 'Alcista' if precio_actual > precio_previo else 'Bajista' if precio_actual < precio_previo else 'Lateral'
    return precio_actual, tendencia

def limpieza_datos(datos_SP500):
    df_clean = datos_SP500.copy()
    df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
    df_clean = df_clean[~df_clean['Close'].isnull()]
    df_clean = df_clean[df_clean['Volume'] > 0]
    valor = df_clean['Close']
    Q1 = valor.quantile(0.25)
    Q3 = valor.quantile(0.75)
    seleccion = (valor >= Q1) & (valor <= Q3)
    df_clean = df_clean[seleccion]
    media_sp500 = df_clean['Close'].mean().round(2)
    return media_sp500

def tomar_decision(precio_actual, tendencia, media_sp500):
    if (precio_actual >= media_sp500) and (tendencia == 'Alcista'):
        return 'Vender'
    elif (precio_actual < media_sp500) and (tendencia == 'Bajista'):
        return 'Comprar'
    else:
        return 'Esperar'

def visualizacion(datos_SP500, decision, media_sp500):
    datos_SP500['Promedio'] = media_sp500
    color_decision = {'Vender': 'green', 'Comprar': 'red', 'Esperar': 'brown'}[decision]

    plt.figure(figsize=(16, 5))
    plt.title('GRAFICO PARA DECIDIR COMPRA-VENTA DE INDICE SP-500', fontsize=20, weight='bold')
    plt.xlabel('Fecha')
    plt.ylabel('Precio Actual en USD')
    plt.plot(datos_SP500.index, datos_SP500['Close'], label='Precio de Cierre', color='Blue')
    plt.plot(datos_SP500.index, datos_SP500['Promedio'], label='Precio Promedio', color='Red', linestyle='dashdot')
    plt.annotate(f'Decisión: {decision}', xy=(datos_SP500.index[-1], datos_SP500['Close'].iloc[-1]), fontsize=12, color=color_decision, weight='bold')
    plt.legend()
    plt.grid()
    st.pyplot(plt)

# Automatización al hacer clic en "Ejecutar análisis"
if ejecutar:
    # Descargar los datos históricos
    datos_SP500 = datos_historicos(ticker, fecha_inicio, fecha_fin)
    
    # Extraer tendencia
    precio_actual, tendencia = extraer_tendencia(datos_SP500)
    
    # Limpiar datos y calcular promedio
    media_sp500 = limpieza_datos(datos_SP500)
    
    # Tomar decisión
    decision = tomar_decision(precio_actual, tendencia, media_sp500)
    
    # Visualizar el resultado
    visualizacion(datos_SP500, decision, media_sp500)
    
    # Actualización en tiempo real
    while True:
        time.sleep(intervalo * 60)  # Convertir minutos a segundos
        new_data = yf.download(ticker, period='1d', interval='5m')
        datos_SP500 = pd.concat([datos_SP500, new_data]).drop_duplicates()
        precio_actual, tendencia = extraer_tendencia(datos_SP500)
        media_sp500 = limpieza_datos(datos_SP500)
        decision = tomar_decision(precio_actual, tendencia, media_sp500)
        visualizacion(datos_SP500, decision, media_sp500)
