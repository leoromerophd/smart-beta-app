import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.pyplot as plt
import statsmodels.api as sm
import colorsys


# Función para descargar el archivo CSV
def download_csv(product_number):
    endpoint = 'https://www.blackrock.com/us/individual/products/'
    csv_url = f'{endpoint}{product_number}/ishares-whatever-name/1464253357814.ajax?fileType=csv'
    headers = {'User-Agent': 'Mozilla/5.0 ...'}  # Tu User-Agent aquí
    response = requests.get(csv_url, headers=headers)
    if response.status_code == 200:
        with open('Components.csv', 'wb') as f:
            f.write(response.content)
        return True
    return False

# Función para leer el CSV
def read_csv_from_keyword(file_path, keyword):
    start_row = 0  # Inicialización de start_row
    try:
        with open(file_path, 'r', encoding='utf-8') as f:  # Especifica la codificación aquí
            for i, line in enumerate(f):
                if keyword in line:
                    start_row = i
                    break
            else:
                # Opcional: Manejar el caso en que el keyword no se encuentra
                print(f"Keyword '{keyword}' no encontrado en el archivo.")
                return pd.DataFrame()  # Retorna un DataFrame vacío si el keyword no se encuentra

        return pd.read_csv(file_path, skiprows=start_row, encoding='utf-8')  # Asegúrate de especificar la misma codificación aquí
    except UnicodeDecodeError:
        # Manejar el caso en que la codificación 'utf-8' no funcione
        with open(file_path, 'r', encoding='ISO-8859-1') as f:  # Prueba con 'ISO-8859-1' o 'latin1'
            for i, line in enumerate(f):
                if keyword in line:
                    start_row = i
                    break
            else:
                print(f"Keyword '{keyword}' no encontrado en el archivo.")
                return pd.DataFrame()

        return pd.read_csv(file_path, skiprows=start_row, encoding='ISO-8859-1')  # Utiliza la misma codificación aquí

# Función para contar el número de datos en un dataframe
def count_data_rows(dataframe):
    return dataframe.shape[0]

# Función para obtener el valor del ticker
def get_ticker_value(product_number):
    url = f'https://www.blackrock.com/us/individual/products/{product_number}/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ticker_element = soup.find('p', {'class': 'identifier chiclet one eq ishares-fund-data'})
        return ticker_element.text if ticker_element else 'No se encontró el ticker'
    return 'Error al obtener el ticker'


# Función para calcular las fechas
def calculate_dates():
    end_date = datetime.now() + timedelta(days=1)
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date = end_date - timedelta(days=365)
    start_date_str = start_date.strftime('%Y-%m-%d')
    return start_date_str, end_date_str

# Función para obtener información del Ticker en yfinance 
def obtener_informacion_stock(ticker):
    ticket_info = yf.Ticker(ticker)
    info = ticket_info.info
    return {
        'description': info.get('longBusinessSummary'),
        'name': info.get('shortName'),
        'threeYearAverageReturn': info.get('threeYearAverageReturn'),
        'fiveYearAverageReturn': info.get('fiveYearAverageReturn'),
        'lastClose': info.get('regularMarketPreviousClose'),
        'previousClose': info.get('previousClose'),
        'open': info.get('open'),
        'dayLow': info.get('dayLow'),
        'dayHigh': info.get('dayHigh'),
        'fiftyDayAverage': info.get('fiftyDayAverage'),
        'twoHundredDayAverage': info.get('twoHundredDayAverage'),
        'yield': info.get('yield'),
        'totalAssets': info.get('totalAssets'),
        'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow'),
        'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
        'fiftyDayAverage': info.get('fiftyDayAverage'),
        'trailingAnnualDividendRate': info.get('trailingAnnualDividendRate'),
        'ytdReturn': info.get('ytdReturn'),
        'beta3Year': info.get('beta3Year'),
    }

def mostrar_informacion_etf(ticker_value):
    etf_data = obtener_informacion_stock(ticker_value)
    descripcion_etf = etf_data.get('description')
    name_etf = etf_data.get('name')
    st.subheader(name_etf)
    st.write(descripcion_etf)

    lastClose = etf_data.get('regularMarketPreviousClose')
    previousClose = etf_data.get('previousClose')
    open = etf_data.get('open')
    dayLow = etf_data.get('dayLow')
    dayHigh = etf_data.get('dayHigh')
    threeYearAverageReturn = round(etf_data.get('threeYearAverageReturn'), 2) * 100
    fiveYearAverageReturn = round(etf_data.get('fiveYearAverageReturn'), 2) * 100
    twoHundredDayAverage = round(etf_data.get('twoHundredDayAverage'), 2)

    yields = etf_data.get('yield')
    totalAssets = etf_data.get('totalAssets')
    fiftyTwoWeekLow = etf_data.get('fiftyTwoWeekLow')
    fiftyTwoWeekHigh = etf_data.get('fiftyTwoWeekHigh')
    fiftyDayAverage = etf_data.get('fiftyDayAverage')
    trailingAnnualDividendRate = etf_data.get('trailingAnnualDividendRate')
    ytdReturn = etf_data.get('ytdReturn')
    beta3Year = etf_data.get('beta3Year')

    st.markdown(f"""
    |Last Close| Previous Close| Open| High | Low | 3Y Av. Return.(%) |  5Y Av. Return.(%)| 200 Average (Price) |
    |---------|--------------|-----|--------|---------| -------- | -----------| ------|
    |{lastClose}|{previousClose}|{open:}|{ dayHigh}|{ dayLow}|{threeYearAverageReturn:.2f}|{fiveYearAverageReturn:.2f}|{twoHundredDayAverage:.3f}|
    |**Yield**| **Total Assets**  | **52 Week Low** | **52 Week High** | **50 Day Average**  | **Annual Dividend Rate (%)** | **YTD Return (%)** | **Beta 3-Year** |
    |{yields * 100 :.3f} | {totalAssets} | {fiftyTwoWeekLow} | {fiftyTwoWeekHigh:.3f} | {fiftyDayAverage:.3f} | {trailingAnnualDividendRate:.3f} | {ytdReturn *100 :.2f} | {beta3Year:.3f} |            
    """)

def mostrar_componentes_etf(ticker_value, product_number):
    if download_csv(product_number):
        file_path = 'Components.csv'
        components_info = read_csv_from_keyword(file_path, 'Ticker')
        if components_info['Weight (%)'].isnull().any():
            components_info.dropna(subset=['Weight (%)'], inplace=True)
        components_info = components_info[components_info['Weight (%)'] >= 0]

        selected_columns = ['Ticker', 'Name', 'Market Value', 'Weight (%)', 'Shares', 'Price']
        filtered_df = components_info[selected_columns]
        ticker_value = ticker_value.replace('\r\n', '')
        num_total_datos = count_data_rows(components_info)

        descarga_datos = num_total_datos - 10
        top_15_tickers = filtered_df['Ticker'].head(descarga_datos).tolist()
        top_15_tickers.insert(0, ticker_value)

        plt.figure(figsize=(10, 8))
        plt.pie(filtered_df['Weight (%)'], labels=filtered_df['Ticker'], autopct='%1.1f%%')
        plt.title(f'Peso Porcentual de cada componente (%) de {ticker_value}')
        plt.axis('equal')
        st.pyplot(plt)
        st.write(f"Número total de componentes: {num_total_datos}")
    else:
        st.write("Error al descargar el archivo CSV.")

def calcular_y_mostrar_rendimiento_riesgo(top_15_tickers, historical_data):
    # Inicializar diccionarios para almacenar los resultados
    alpha_annualized = {}
    beta = {}
    total_risk = {}

    # Índice de referencia es el primer elemento en top_15_tickers
    benchmark_ticker = top_15_tickers[0]
    benchmark_returns = historical_data[benchmark_ticker]['Adj Close'].pct_change().dropna()

    # Loop a través de cada ticker en top_15_tickers
    for ticker in top_15_tickers[1:]:  # Excluimos el índice de referencia
        asset_data = historical_data[ticker]
        if asset_data.empty:
            st.write(f"Datos vacíos para {ticker}, omitiendo.")
            continue
        asset_returns = asset_data['Adj Close'].pct_change().dropna()
        if asset_returns.empty:
            st.write(f"Rendimientos vacíos para {ticker}, omitiendo.")
            continue

        # Alinear fechas entre el activo y el índice de referencia
        aligned_data = pd.concat([benchmark_returns, asset_returns], axis=1).dropna()
        aligned_data.columns = ['Benchmark', 'Asset']

        if aligned_data.empty:
            st.write(f"Datos alineados vacíos para {ticker}, omitiendo.")
            continue

        # Ejecutar regresión lineal
        X = sm.add_constant(aligned_data['Benchmark'])  # Agregar una constante para calcular el intercepto
        y = aligned_data['Asset']
        model = sm.OLS(y, X).fit()

        # Calcular Alpha Anualizado, Beta y Riesgo Total
        alpha_annualized[ticker] = round(model.params['const'] * 252 * 100, 3)  # Suponiendo 252 días de trading al año
        beta[ticker] = round(model.params['Benchmark'], 3)
        total_risk[ticker] = round(model.mse_resid * 252 * 100, 4)

    # Resumen de los resultados
    results_summary = pd.DataFrame({
        'Alpha Anual': alpha_annualized,
        'Beta': beta,
        'Riesgo Anual': total_risk
    })

    # Mostrar los resultados en Streamlit
    st.subheader("Análisis de Rendimiento y Riesgo de Componentes")
    st.table(results_summary)

# Obtener información del ETF 
def generate_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        lightness = 0.6
        saturation = 0.95
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append(f'rgb({int(rgb[2]*10)}, {int(rgb[2]*120)}, {int(rgb[0]*200)})')
    return colors    