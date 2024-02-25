import streamlit as st
from cache import mapa_nombres_p_numbers
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import yfinance as yf
import statsmodels.api as sm
import plotly.graph_objs as go
from funtions import (download_csv, read_csv_from_keyword, count_data_rows, 
                       get_ticker_value, calculate_dates, mostrar_informacion_etf, 
                       obtener_informacion_stock, mostrar_componentes_etf, calcular_y_mostrar_rendimiento_riesgo,
                       generate_colors)
from metodology import medologia
import io

ticker = "IYJ"

# Función principal para mostrar en Streamlit
def show():
    st.title(":factory: Industrial :factory:")
    etf_name = "Industrials"
    product_number = mapa_nombres_p_numbers.get(etf_name)
    
    if product_number:
        ticker_value = get_ticker_value(product_number)
        ticker_value = ticker_value.strip()
        st.write(f"El ticker de Blackrock que usamos como componentes del etf es: {ticker_value}")
        
        mostrar_informacion_etf(ticker_value)
        st.write("---")
        st.subheader("Componentes del ETF")
        #mostrar_componentes_etf(ticker_value, product_number)
                
        if download_csv(product_number):
            file_path = 'Components.csv'
            components_info = read_csv_from_keyword(file_path, 'Ticker')
            if components_info['Weight (%)'].isnull().any():
                components_info.dropna(subset=['Weight (%)'], inplace=True)
            components_info = components_info[components_info['Weight (%)'] >= 0]
            selected_columns = ['Ticker', 'Name', 'Market Value', 'Weight (%)', 'Shares', 'Price']
            filtered_df = components_info[selected_columns]
            top_15_tickers = filtered_df['Ticker'].tolist()

            selected_columns = ['Ticker', 'Name', 'Market Value', 'Weight (%)', 'Shares', 'Price']
            filtered_df = components_info[selected_columns]
            ticker_value = ticker_value.replace('\r\n', '')
            num_total_datos = count_data_rows(components_info)

            Dato_Calculo = st.slider('Ingresa el número de componentes para el cálculo', 0, num_total_datos, 15)

            descarga_datos = Dato_Calculo
            top_15_tickers = filtered_df['Ticker'].head(descarga_datos).tolist()
            top_15_tickers.insert(0, ticker_value)


            # Calcula el peso porcentual y crea una nueva columna para la leyenda
            filtered_df['Legend'] = filtered_df.apply(lambda row: f"{row['Ticker']} ({row['Weight (%)']:.1f}%)", axis=1)

            num_components = len(filtered_df['Ticker'].unique())
            color_sequence = generate_colors(num_components)

            fig = px.pie(filtered_df, values='Weight (%)', names='Legend', 
                         title=f'Peso Porcentual de cada componente (%) de {etf_name}', 
                         color='Legend', color_discrete_sequence=color_sequence)

            # Actualizar trazas para configurar la posición y la información del texto
            fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='radial')
                        # Configurar el diseño para mostrar la leyenda
            # Aumentar el tamaño de la fuente de la leyenda
            fig.update_layout(
                showlegend=True, 
                legend=dict(font=dict(size=18)),  # Ajusta el tamaño según tus necesidades
                uniformtext_minsize=10, 
                uniformtext_mode='hide'
            )

            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"Número total de componentes: {num_total_datos}")
                            
           # Botón para descargar datos históricos y mostrar rendimientos y riesgo
            if st.button(f'Cálculo de Rendimiento - Riesgo para el índice Industrial'):
                with st.spinner('... Calculando ...'):
                    start_date_str, end_date_str = calculate_dates()
                    num_tickers = len(top_15_tickers)
                    # Crear una barra de progreso
                    progress_bar = st.progress(0)
                    # Inicializar variable para actualizar la barra de progreso
                    progress_count = 0
                    # Diccionario para almacenar los datos históricos
                    historical_data = {}
                    # Descargar los datos para cada ticker
                    for ticker in top_15_tickers:
                        historical_data[ticker] = yf.download(ticker, start=start_date_str, end=end_date_str)
                        # Actualizar la barra de progreso
                        progress_text = "Descargando Precios Históricos. Por favor, espera ..."
                        progress_count += 1
                        progress_bar.progress(progress_count / num_tickers, text=progress_text )                    
                    st.success('  Cálculos Hechos', icon="✅")

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
                        # Verificar si los datos están vacíos
                        if asset_data.empty:
                            print(f"Datos vacíos para {ticker}, omitiendo.")
                            continue               
                        # Calcular rendimientos diarios
                        asset_returns = asset_data['Adj Close'].pct_change().dropna()

                        # Verificar si los rendimientos están vacíos después del cálculo
                        if asset_returns.empty:
                            print(f"Rendimientos vacíos para {ticker}, omitiendo.")
                            continue
                        
                        # Alinear fechas entre el activo y el índice de referencia
                        aligned_data = pd.concat([benchmark_returns, asset_returns], axis=1).dropna()
                        aligned_data.columns = ['Benchmark', 'Asset']

                        # Verificar que los datos alineados no están vacíos
                        if aligned_data.empty:
                            print(f"Datos alineados vacíos para {ticker}, omitiendo.")
                            continue
                        
                        # Ejecutar regresión lineal
                        X = aligned_data['Benchmark']
                        y = aligned_data['Asset']

                        if X.empty or y.empty:
                            print(f"Datos vacíos para {ticker}, omitiendo.")
                            continue
                        
                        X = sm.add_constant(X)  # Agregar una constante para calcular el intercepto
                        model = sm.OLS(y, X).fit()

                        # Calcular Alpha Anualizado, Beta y Riesgo Total
                        alpha_annualized[ticker] = round(model.params['const'] * 252  * 100,3)# Suponiendo 252 días de trading al año
                        beta[ticker] = round(model.params['Benchmark'],3)
                        total_risk[ticker] = round(model.mse_resid * 252 * 100, 4)

                    # Resumen de los resultados
                    results_summary = pd.DataFrame({
                        'Alpha Anual': alpha_annualized,
                        'Beta': beta,
                        'Riesgo Anual': total_risk
                    })


 # -------Creaci    ón de la gráfica de burbujas para Alpha Anual vs Riesgo Anual
                    fig_burbujas_alpha = go.Figure()
                    # Agregar las burbujas con etiquetas de ticker
                    fig_burbujas_alpha.add_trace(go.Scatter(
                        x=results_summary['Riesgo Anual'],
                        y=results_summary['Alpha Anual'],
                        mode='markers+text',  # Modo para mostrar marcadores y texto
                        marker=dict(size=abs(results_summary['Alpha Anual']) + 3),  # Ajustar el tamaño de las burbujas según tus preferencias
                        text=results_summary.index,  # Muestra el ticker de cada componente
                        hoverinfo='text+x+y',  # Configura la información mostrada al pasar el mouse sobre la burbuja
                        textposition='bottom right',  # Posición del texto en relación con el marcador
                        textfont=dict(
                            family="Arial, sans-serif",
                            size=10,
                            color="black"
                        )
                    ))

                    # Configuración adicional de la gráfica
                    fig_burbujas_alpha.update_layout(
                        title='Alpha Anual y Riesgo Anual de los Componentes',
                        xaxis_title='Riesgo Anual (%)',
                        yaxis_title='Alpha Anual (%)',
                        # Añadir línea horizontal punteada roja en el valor cero del eje Y
                        shapes=[
                            dict(
                                type='line',
                                yref='y', y0=0, y1=0,
                                xref='paper', x0=0, x1=1,
                                line=dict(
                                    color='red',
                                    width=1,
                                    dash='dash'
                                )
                            )
                        ]
                    )

                    # Mostrar la gráfica en Streamlit
                    st.plotly_chart(fig_burbujas_alpha, use_container_width=True)

                    # Creación de la gráfica de burbujas para Beta vs Riesgo Total
                    fig_burbujas_beta = go.Figure()

                    # Agregar las burbujas con etiquetas de ticker
                    fig_burbujas_beta.add_trace(go.Scatter(
                        x=results_summary['Beta'],
                        y=results_summary['Riesgo Anual'],
                        mode='markers+text',  # Modo para mostrar marcadores y texto
                        marker=dict(size=10),  # Ajustar el tamaño de las burbujas según tus preferencias
                        text=results_summary.index,  # Muestra el ticker de cada componente
                        hoverinfo='text+x+y',  # Configura la información mostrada al pasar el mouse sobre la burbuja
                        textposition='bottom right',  # Posición del texto en relación con el marcador
                        textfont=dict(
                            family="Arial, sans-serif",
                            size=10,
                            color="black"
                        )
                    ))

                    # Agregar la línea punteada roja en Beta = 1
                    fig_burbujas_beta.add_trace(go.Scatter(
                        x=[1, 1],
                        y=[results_summary['Riesgo Anual'].min(), results_summary['Riesgo Anual'].max()],
                        mode='lines',
                        line=dict(color='red', width=2, dash='dash'),
                        showlegend=False
                    ))

                    # Configuración adicional de la gráfica
                    fig_burbujas_beta.update_layout(
                        title='Relación entre Beta y Riesgo Anual de los Componentes',
                        xaxis_title='Beta',
                        yaxis_title='Riesgo Anual (%)',
                        xaxis=dict(range=[results_summary['Beta'].min() - 0.5, results_summary['Beta'].max() + 0.5]),  # Ajustar el rango del eje X si es necesario
                        showlegend=False  # Desactivar la leyenda
                    )

                    # Mostrar la gráfica en Streamlit
                    st.plotly_chart(fig_burbujas_beta, use_container_width=True)
# --------------    -----------------------------------------------------------------------
                    # Calcular el promedio de 'Alpha Anual'
                    alpha_mean = results_summary['Alpha Anual'].mean()
                    # Filtrar el DataFrame para obtener solo las filas con un 'Alpha Anual' superior al promedio
                    above_average_alpha = results_summary[results_summary['Alpha Anual'] > alpha_mean]
                    # Organizar la nueva tabla por 'Alpha Anual'
                    sorted_above_average_alpha = above_average_alpha.sort_values(by='Alpha Anual', ascending=False)
                    # Seleccionar las columnas adicionales que queremos incluir en el nuevo DataFrame
                    columns_to_include = ['Alpha Anual', 'Beta', 'Riesgo Anual']
                    # Asegurándonos de que el índice (que podría ser el símbolo) también esté incluido en el DataFrame
                    ticker_above_average_df = sorted_above_average_alpha[columns_to_include].copy()
                    ticker_above_average_df['Symbol'] = ticker_above_average_df.index
                    # Reorganizar las columnas para que 'Symbol' sea la primera
                    ticker_above_average_df = ticker_above_average_df[['Symbol'] + columns_to_include]
                    # Exportar el DataFrame a un archivo CSV
                    csv_path_above_average = "above_average_alpha_list.csv"
                    ticker_above_average_df.to_csv(csv_path_above_average, index=False)
                    # Obtenemos el ticker del ETF que será la línea roja más gruesa
                    etf_ticker = top_15_tickers[0]
                    # Creamos un dataframe vacío para almacenar los precios históricos
                    historical_prices_df = pd.DataFrame()
                    # Rellenamos el dataframe con los precios históricos de cada símbolo, incluyendo el ETF
                    for symbol in ticker_above_average_df['Symbol'].unique():  # Usamos 'Symbol' en lugar de 'Ticker'
                        historical_prices_df[symbol] = historical_data[symbol]['Close']  # Asumimos que existe una columna 'Close' para el precio de cierre
                    # Aseguramos que los datos del ETF estén incluidos
                    historical_prices_df[etf_ticker] = historical_data[etf_ticker]['Close']
                    # Calcular los rendimientos acumulados base cero
                    cumulative_returns = (historical_prices_df.pct_change() + 1).cumprod() - 1

                    # Filtrar el DataFrame 'historical_prices_df' para incluir solo los componentes con Alpha Anual superior al promedio
                    components_with_high_alpha = ticker_above_average_df['Symbol']
                    filtered_historical_prices_df = historical_prices_df[components_with_high_alpha]

                    # Calcular los rendimientos acumulados base cero para los componentes filtrados
                    cumulative_returns_filtered = (filtered_historical_prices_df.pct_change() + 1).cumprod() - 1

                    # Crear una figura de Plotly
                    fig = go.Figure()

                    # Agregar una línea para cada componente filtrado
                    for symbol in cumulative_returns_filtered.columns:
                        if symbol == etf_ticker:
                            # ETF ticker con línea más gruesa y roja
                            fig.add_trace(go.Scatter(x=cumulative_returns_filtered.index, y=cumulative_returns_filtered[symbol], mode='lines', name=symbol, line=dict(color='red', width=5)))
                        else:
                            # Otros componentes con línea estándar
                            fig.add_trace(go.Scatter(x=cumulative_returns_filtered.index, y=cumulative_returns_filtered[symbol], mode='lines', name=symbol))

                    # Tamaño de la fuente para las anotaciones
                    font_size = 9  # Ajusta este valor según tus necesidades

                    # Agregar anotaciones para cada línea
                    for symbol in cumulative_returns_filtered.columns:
                        last_date = cumulative_returns_filtered.index[-1]
                        last_value = cumulative_returns_filtered[symbol].iloc[-1]
                        fig.add_annotation(
                            x=last_date, 
                            y=last_value, 
                            text=symbol, 
                            showarrow=False, 
                            font=dict(size=font_size),
                            yshift=10
                        )

                    # Configuración del layout de la gráfica
                    fig.update_layout(
                        title=f"Cumulative Returns Alpha > Media: {etf_ticker}",
                        xaxis_title='Date',
                        yaxis_title='Cumulative Returns',
                        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5),
                        margin=dict(l=0, r=0, t=30, b=0),
                        width=1200,  # Ancho de la gráfica
                        height=600   # Altura de la gráfica
                    )

                    # Mostrar el gráfico en Streamlit
                    st.plotly_chart(fig, use_container_width=True)


                    # Filtrar las empresas con Beta > 1
                    empresas_beta_mayor_1 = ticker_above_average_df[ticker_above_average_df['Beta'] > 1]

                    # Organizar las empresas filtradas por Riesgo Anual
                    empresas_ordenadas_por_riesgo = empresas_beta_mayor_1.sort_values(by='Riesgo Anual', ascending=True)
                    BetaMayor1List = empresas_ordenadas_por_riesgo['Symbol']

                    # Crear un DataFrame para almacenar los precios históricos de las empresas filtradas
                    historical_prices_beta_mayor_1_df = pd.DataFrame()

                    # Rellenar el DataFrame con los precios históricos de cada símbolo, incluyendo el ETF
                    for symbol in BetaMayor1List:
                        if symbol in historical_data:
                            historical_prices_beta_mayor_1_df[symbol] = historical_data[symbol]['Close']

                    # Incluir también los datos del ETF
                    if etf_ticker in historical_data:
                        historical_prices_beta_mayor_1_df[etf_ticker] = historical_data[etf_ticker]['Close']

                    # Calcular los rendimientos acumulados base cero
                    cumulative_returns_beta_mayor_1 = (historical_prices_beta_mayor_1_df.pct_change() + 1).cumprod() - 1


                    # Crear una figura de Plotly
                    fig = go.Figure()

                    # Agregar una línea para cada empresa filtrada
                    for symbol in cumulative_returns_beta_mayor_1.columns:
                        if symbol == etf_ticker:
                            # ETF ticker con línea más gruesa y roja
                            fig.add_trace(go.Scatter(x=cumulative_returns_beta_mayor_1.index, y=cumulative_returns_beta_mayor_1[symbol], mode='lines', name=symbol, line=dict(color='red', width=3)))
                        else:
                            # Empresas con Beta > 1
                            fig.add_trace(go.Scatter(x=cumulative_returns_beta_mayor_1.index, y=cumulative_returns_beta_mayor_1[symbol], mode='lines', name=symbol))

                    # Tamaño de la fuente para las anotaciones
                    font_size = 10  # Ajusta este valor según tus necesidades

                    # Agregar anotaciones para cada línea
                    for symbol in cumulative_returns_beta_mayor_1.columns:
                        last_date = cumulative_returns_beta_mayor_1.index[-1]
                        last_value = cumulative_returns_beta_mayor_1[symbol].iloc[-1]
                        fig.add_annotation(
                            x=last_date, 
                            y=last_value, 
                            text=symbol,  # Texto de la anotación
                            showarrow=False, 
                            font=dict(size=font_size),
                            yshift=10
                        )

                    # Configuración del layout de la gráfica
                    fig.update_layout(
                        title="Cumulative Returns Base Zero for Companies with Beta > 1 and ETF",
                        xaxis_title='Date',
                        yaxis=dict(
                            title='Cumulative Returns',
                            tickformat='.0%',  # Formato de porcentaje para el eje Y
                        ),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5),
                        margin=dict(l=0, r=0, t=30, b=0),
                        width=1200,
                        height=600
                    )

                    # Mostrar el gráfico en Streamlit
                    st.plotly_chart(fig, use_container_width=True)


                    # Filtrar las empresas con Beta < 1
                    empresas_beta_menor_1 = ticker_above_average_df[ticker_above_average_df['Beta'] < 1]
                    empresas_ordenadas_por_riesgo_menor_1 = empresas_beta_menor_1.sort_values(by='Riesgo Anual', ascending=True)
                    Beta_Menor_1 = empresas_ordenadas_por_riesgo_menor_1['Symbol']

                    # Crear un DataFrame para almacenar los precios históricos de las empresas filtradas
                    historical_prices_beta_menor_1_df = pd.DataFrame()

                    # Rellenar el DataFrame con los precios históricos de cada símbolo, incluyendo el ETF
                    for symbol in Beta_Menor_1:
                        if symbol in historical_data:
                            historical_prices_beta_menor_1_df[symbol] = historical_data[symbol]['Close']

                    # Incluir también los datos del ETF
                    if etf_ticker in historical_data:
                        historical_prices_beta_menor_1_df[etf_ticker] = historical_data[etf_ticker]['Close']

                    # Calcular los rendimientos acumulados base cero
                    cumulative_returns_beta_menor_1 = (historical_prices_beta_menor_1_df.pct_change() + 1).cumprod() - 1

                    # Crear una figura de Plotly
                    fig = go.Figure()

                    # Agregar una línea para cada empresa filtrada
                    for symbol in cumulative_returns_beta_menor_1.columns:
                        if symbol == etf_ticker:
                            # ETF ticker con línea más gruesa y roja
                            fig.add_trace(go.Scatter(x=cumulative_returns_beta_menor_1.index, y=cumulative_returns_beta_menor_1[symbol], mode='lines', name=symbol, line=dict(color='red', width=3)))
                        else:
                            # Empresas con Beta < 1
                            fig.add_trace(go.Scatter(x=cumulative_returns_beta_menor_1.index, y=cumulative_returns_beta_menor_1[symbol], mode='lines', name=symbol))

                    # Tamaño de la fuente para las anotaciones
                    font_size = 10  # Ajusta este valor según tus necesidades

                    # Agregar anotaciones para cada línea
                    for symbol in cumulative_returns_beta_menor_1.columns:
                        last_date = cumulative_returns_beta_menor_1.index[-1]
                        last_value = cumulative_returns_beta_menor_1[symbol].iloc[-1]
                        fig.add_annotation(
                            x=last_date, 
                            y=last_value, 
                            text=symbol,  # Texto de la anotación
                            showarrow=False, 
                            font=dict(size=font_size),
                            yshift=10
                        )

                    # Configuración del layout de la gráfica
                    fig.update_layout(
                        title="Cumulative Returns Base Zero for Companies with Beta < 1 and ETF",
                        xaxis_title='Date',
                        yaxis=dict(
                            title='Cumulative Returns',
                            tickformat='.0%',  # Formato de porcentaje para el eje Y
                        ),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5),
                        margin=dict(l=0, r=0, t=30, b=0),
                        width=1200,
                        height=600
                    )

                    # Mostrar el gráfico en Streamlit
                    st.plotly_chart(fig, use_container_width=True)              
                    ### Descarga del Archivo Apha > Promedio 
                    csv = io.StringIO()
                    ticker_above_average_df.to_csv(csv, index=False)
                    csv.seek(0)
                    csv_as_text = csv.getvalue()

                    # Crear un botón de descarga en Streamlit
                    csv_file_name = f"Alpha_Mayor_Promedio_{etf_name}.csv"
                    st.download_button(
                        label="Descargar Alpha > Promedio",
                        data=csv_as_text,
                        file_name=csv_file_name,
                        mime='text/csv'
                    )
        else:  
            st.write("Error al descargar el archivo CSV.")
        texto_metodologia = medologia()
        st.write(texto_metodologia)
    else:
        st.write("Nombre del ETF no encontrado.")

if __name__ == "__main__":
    show()