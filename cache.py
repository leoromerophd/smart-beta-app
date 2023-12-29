# Lista de tickers y nombres de los ETFs
tickers = ["OEF", "IYW", "IYH", "IYZ", "IYM", "IYF", "IYC", "IYK",
           "IYE", "IYR", "IYJ", "IDU", "SOXX", "IGV", "IVE", "IVW", 
           "IYG", "ITB", "IJH"]

nombres = ["S&P",
           "Technology",
           "Health",
           "Telecom",
           "Materials",
           "Financials",
           "Consumer Serv",
           "Consumer Goods",
           "Energy",
           "Real Estate",
           "Industrials",
           "Utilities",
           "Semiconductor",
           "Software",
           "Value",
           "Growth",
           "Finserv",
           "Homebuilders",
           "Midcap"]

p_numbers = ["239723", "239522", "239511", "239523", "239503",
             "239508", "239506", "239505", "239507",
             "239520", "239514", "239524", "239705", "239771",
             "239728", "239725", "239509", "239512", "239763"]

# Creando un diccionario para mapear nombres a números de producto
mapa_nombres_p_numbers = {nombre: p_number for nombre, p_number in zip(nombres, p_numbers)}

# Posibles Adicciones 
# IJH  Midcap iShares Core S&P Mid-Cap ETF
# IJR Small-Cap 