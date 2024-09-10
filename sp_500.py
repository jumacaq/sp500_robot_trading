import streamlit as st
import pandas as pd
import yfinance as yf
import time
import matplotlib.pyplot as plt

# Función para descargar y actualizar datos en tiempo real
@st.cache_data
def datos_historicos(ticker):
    datos = yf.download(ticker, start="2010-01-01", end="2024-08-27")
    datos = datos[['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
    new_data = yf.download(ticker, period='1d', interval='5m')
    datos = pd.concat([datos, new_data]).drop_duplicates()
    return datos

# Función para extraer tendencia
def extraer_tendencia(datos_SP500):
    precio_actual = datos_SP500['Close'].iloc[-1]
    precio_previo = datos_SP500['Close'].iloc[-2]

    if precio_actual > precio_previo:
        tendencia = 'Alcista'
    elif precio_actual < precio_previo:
        tendencia = 'Bajista'
    else:
        tendencia = 'Lateral'
    return precio_actual, tendencia

# Función para limpiar los datos
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

# Función de toma de decisión
def tomar_decision(precio_actual, tendencia, media_sp500):
    if (precio_actual >= media_sp500) and (tendencia == 'Alcista'):
        decision = 'Vender'
    elif (precio_actual < media_sp500) and (tendencia == 'Bajista'):
        decision = 'Comprar'
    else:
        decision = 'Esperar'
    return decision

# Función de visualización
def visualizacion(datos_SP500, decision, media_sp500):
    datos_SP500['Promedio'] = media_sp500
    color_decision = {'Vender': 'green', 'Comprar': 'red', 'Esperar': 'brown'}[decision]

    plt.rc('figure', figsize=(16, 5), facecolor='#E8DEE1')
    plt.title('GRAFICO PARA DECIDIR COMPRA-VENTA DE INDICE SP-500', fontsize=20, weight='bold')
    plt.xlabel('Fecha')
    plt.ylabel('Precio Actual en USD')
    plt.plot(datos_SP500.index, datos_SP500['Close'], label='Precio de Cierre', color='Blue')
    plt.plot(datos_SP500.index, datos_SP500['Promedio'], label='Precio Promedio', color='Red', linestyle='dashdot')
    plt.annotate(f'Decisión: {decision}', xy=(datos_SP500.index[-1], 210), fontsize=12, color=color_decision, weight='bold')
    plt.legend()
    plt.grid()
    st.pyplot(plt)

# Interfaz de Streamlit
st.title('Robot de Trading S&P 500')
st.write('Monitorización en tiempo real del índice S&P 500 y toma de decisiones de compra-venta.')

# Descargar los datos históricos y actualizar en tiempo real
ticker = 'SPY'
st.write('Descargando datos de S&P 500...')
datos_SP500 = datos_historicos(ticker)

# Extraer tendencia y limpiar datos
precio_actual, tendencia = extraer_tendencia(datos_SP500)
media_sp500 = limpieza_datos(datos_SP500)

# Tomar decisión
decision = tomar_decision(precio_actual, tendencia, media_sp500)

# Mostrar resultados
st.write(f'Precio Actual: ${precio_actual}')
st.write(f'Tendencia Actual: {tendencia}')
st.write(f'Precio Promedio: ${media_sp500}')
st.write(f'Decisión: {decision}')

# Mostrar visualización
visualizacion(datos_SP500, decision, media_sp500)
