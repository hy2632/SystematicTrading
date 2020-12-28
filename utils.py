import numpy as np
from pandas_datareader import data
import matplotlib.pyplot as plt

def plot_Stock_Price(start_date, end_date, *stock_names, figsize=(10,6)):
    df = [data.get_data_yahoo(stock_name, start_date, end_date) for stock_name in stock_names]
    fig, ax1 = plt.subplots(figsize = figsize)

    # ax1.set_title(f"{stock_name} {start_date} - {end_date}", fontdict={"size":20})
    ax1.set_xlabel("date")
    ax1.xaxis.grid(True, which="major", color='gray', linestyle="--", alpha=0.25)
    

    ax1.set_ylabel("$ Close")
    ax1.yaxis.grid(True, which="major", color='gray', linestyle="--", alpha=0.25)

    maxClose = [np.max(stock["Close"]) for stock in df]
    globalMaxClose = np.max(maxClose)
    # Get the order of magnitude of maximum of $Close
    magnitude = np.floor(np.log10(globalMaxClose))
    ax1.set_ylim(bottom=0, top = np.ceil(globalMaxClose/10**(magnitude))*10**(magnitude))
    
    for stock in df:
        ax1.plot(stock.index, stock["Close"])
    
    ax1.legend(stock_names)

    plt.show()

def trade(stockname: str, start_date: str, end_date: str, investmentValue: int):
    df = data.get_data_yahoo(stockname, start_date, end_date)
    plot_Stock_Price(start_date, end_date, stockname)

    out = df.iloc[-1]["Close"]/df.iloc[0]["Close"] * investmentValue
    print(f"Investment: {investmentValue}\n")
    print(f"Return: {out}\n")
    gain = out - investmentValue
    print(f"Gain: {gain}\n")

    days = (df.index[-1] - df.index[0]).days
    annualRateOfReturn = ((gain / investmentValue)**(1/days) - 1)*365
    print(f"Annual rate of return: {annualRateOfReturn}\n" )
