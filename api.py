import requests
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt 

def get_stock_data(symbol, start_date, end_date):
    api_key = 'IE6F252F3FWX1UUO'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full'
    response = requests.get(url)
    data = response.json()['Time Series (Daily)']
    df = pd.DataFrame(columns=['Date','Open','High','Low','Close','Adj Close','Volume'])
    for date in data:
        if start_date <= date <= end_date:
            row = [date, float(data[date]['1. open']), float(data[date]['2. high']),float(data[date]['3. low']),
                   float(data[date]['4. close']),float(data[date]['5. adjusted close']),float(data[date]['6. volume'])]
            df.loc[len(df)] = row
    return df

'''def calculate_technical_indicators(stock_data, sma_length=20, rsi_length=14, bb_length=20, bb_std=2):
    stock_data.ta.sma(length=sma_length, append=True)
    stock_data.ta.rsi(length=rsi_length, append=True)
    stock_data.ta.bbands(length=bb_length, std=bb_std, append=True)
    stock_data.ta.macd(append=True)
    return stock_data'''

#df = get_stock_data('AAPL', '2022-01-01', '2022-05-01')
#print(df)

'''
ticker = 'AAPL'
start_date = '2022-01-01'
end_date = '2022-05-01'

stock_data = get_stock_data(ticker, start_date, end_date)
stock_data = calculate_technical_indicators(stock_data)

print(stock_data.tail())'''


def calculate_technical_indicators(stock_data, sma_length=20, rsi_length=14,bb_length=20, bb_std=2):
    stock_data.ta.sma(length=sma_length, append=True)
    stock_data.ta.rsi(length=rsi_length, append=True)
    stock_data.ta.bbands(length=bb_length, std=bb_std, append=True)

    '''stock_data['Signal'] = None
    stock_data.loc[stock_data['SMA_20'] > stock_data['SMA_20'].shift(1), 'Signal'] = 'BUY'
    stock_data.loc[stock_data['SMA_20'] < stock_data['SMA_20'].shift(1), 'Signal'] = 'SELL' '''

    return stock_data


def simulate_trading(stock_data, capital):
    position = None
    buy_price = 0.0
    total_shares = 0
    portfolio_value = capital
    stock_data['Signal'] = ''  # Agregar una columna 'Signal' al DataFrame
    for index, row in stock_data.iterrows():
        if index == 0:
            continue
        previous_row = stock_data.iloc[index - 1]
        if row['SMA_20'] < previous_row['SMA_20']:
            # Cruce bajista del indicador (señal de compra)
            if position == 'SELL':
                # Vender acciones
                portfolio_value += total_shares * row['Close']
                total_shares = 0
            position = 'BUY'
            buy_price = row['Close']
            total_shares = int(portfolio_value / buy_price)
            portfolio_value -= total_shares * buy_price
            stock_data.at[index, 'Signal'] = 'BUY'  # Almacenar la señal de compra en la columna 'Signal'
            stock_data.at[index, 'Shares'] = total_shares  # Almacenar la cantidad de acciones en la columna 'Shares'
            stock_data.at[index, 'Portfolio Value'] = portfolio_value  # Almacenar el valor del portafolio en la columna 'Portfolio Value'
            print(f"BUY: {row['Date']} - Price: {buy_price} - Shares: {total_shares} - Portfolio Value: {portfolio_value}")
        elif row['SMA_20'] > previous_row['SMA_20']:
            # Cruce alcista del indicador (señal de venta)
            if position == 'BUY':
                # Comprar acciones
                portfolio_value += total_shares * row['Close']
                total_shares = 0
            position = 'SELL'
            sell_price = row['Close']
            total_shares = int(total_shares)
            portfolio_value += total_shares * sell_price
            stock_data.at[index, 'Signal'] = 'SELL'  # Almacenar la señal de venta en la columna 'Signal'
            stock_data.at[index, 'Shares'] = total_shares  # Almacenar la cantidad de acciones en la columna 'Shares'
            stock_data.at[index, 'Portfolio Value'] = portfolio_value  # Almacenar el valor del portafolio en la columna 'Portfolio Value'
            print(f"SELL: {row['Date']} - Price: {sell_price} - Shares: {total_shares} - Portfolio Value: {portfolio_value}")

def plot_stock_data(stock_data):
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['Date'], stock_data['Close'])
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Stock Prices')
    plt.grid(True)
    
    # Guardar el gráfico en un archivo HTML
    plt.savefig('stock_chart.pmg', format='png')

ticker = 'AAPL'
start_date = '2022-01-01'
end_date = '2022-05-01'
capital = 10000  # Capital ficticio inicial

stock_data = get_stock_data(ticker, start_date, end_date)
stock_data = calculate_technical_indicators(stock_data)

#simulate_trading(stock_data, capital)
#plot_stock_data(stock_data)