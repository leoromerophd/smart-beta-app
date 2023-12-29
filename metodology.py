import streamlit as st 

def medologia():
    texto = """
    ---
    ## Explicación del Cálculo: 
    
    *Smart Beta App*, extrae todos los componentes de un ETF[^1]  y calcula su *Alpha, Beta y Riesgo Total*. 
    Se hace la descarga de datos diarios y se trasforman a su cambio porcentual respecto del día anterior para el último año de precios 
    de negociación. Se hace una regresión lineal de los cambios porcentuales de cada uno de los 
    componentes para estimar *Alpha*[^2]. Se entiende por Alpha a los rendimientos acumulados diarios por encima del 
    índice de referencia respecto de un nivel de error. Esto quire decir; en la gráfica de burbujas que tiene al Riesgo 
    Anual en el eje horizontal, respecto de Alpha Anual en el eje vertical; que las empresas que están encima de la línea roja (cero) tuvieron mejores rendimeintos acumulados anuales (Alphas) que el ETF. 
    Por tanto, en esta gráfica buscaremos a las empresas que estén en la parte superior izquierda con menos riesgo y más
    retorno. Cada regresión toma como regresor de referencia el ETF al cual pertenencen los componentes y **no** respecto del S&P o del Nasdaq. 
    Para obtener los datos anuales se componen los resultados diarios por 252 días[^3]. Tras el cálculo del Alpha de cada componente, 
    se hace el cálculo el *Alpha promedio* de todos los componentes y se filtran los datos para seleccionar únicamente los componentes 
    que tienen un rendimiento mejor que el promedio de todos los componentes del ETF. Para crear las gráficas, se filtran los resultados respecto de los resultados de *Beta*, y sólo se
    incluyen las empresas del ETF que tienen un Alpha mayor al promedio. Se considera que una empresa 
    con Beta > 1 reaccionará de manera más fuerte ante un cambio porcentual del índice. Esto es; si el Beta de la empresa es 1.2; por cada cambio porcentual del índice en 1%, el precio 
    de la acción debería reaccionar alrededor de 1.2 %. Por tanto Empresas con Beta mayor a uno y Alpha positivo deberían 
    reaccionar más fuerte ante cambios del mercado; pero aún a pesar de las caídas generar rendimientos
    constantes respecto del desempeño de sus pares en razón a su Alpha positivo. En cambio, empresas con Beta < 1 deberían 
    ser más conservadoras ante movimientos fuertes de mercado; pero aún así, mantener rendimeintos constantes
    con Alphas por encima del promedio del mercado.

    [^1]: www.blackrock.com: El App busca el ETF que corresponde a cada sector y descarga sus componentes.
    La lista de los ETFs es: "OEF", "IYW", "IYH", "IYZ", "IYM", "IYF", "IYC", "IYK", "IYE", "IYR", "IYJ", "IDU", "SOXX", "IGV", "IVE", "IVW",
    "IYG", "ITB", "IJH"
    [^2]: Para más información del concepto de *Alpha* se puede consultar el capítulo 6 del libro de Investments: 
    Bodie Z. Kane A. & Marcus A. J. (2014). *Investments* (Tenth). McGraw-Hill Education. 
    [^3]: Cada año de negociación del mercado accionario sin contar fines de semana está compuesto en promedio por 252
    días hábiles.
    
    """
    return texto