import numpy as np
import pandas_datareader as pdr
from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd

def strategy_modeling(
        principal = 1e5,
        strategy = 'Early_Profit_Taker',
        tol_hi = 0.1,
        tol_lo = 0.05,
        position_hi = 1,
        position_lo = 0.1,
        data = BABA,
    ):
    """
        This module compare two different transaction strategies: "Early Profit Taker" and "Early Loss Taker", mentioned by Robert Carver
        in his book Systematic Trading. The previous one is mankind's instinction, while the latter one usually outperforms.
        
        ## Author
        Hua Yao (hy2632@columbia.edu)
        
        ## Reference:
        Robert Carver, Systematic Trading: A unique new method for designing trading and investing systems, Page 15.

        Parameters:
        ---------
                principal: int, your principal
                strategy: str, 'Early_Profit_Taker' / 'Early_Loss_Taker'
                tol_hi: the higher threshold of percentage change in price since last transaction
                tol_lo: the lower...
                position_hi: high position 高仓位
                position_lo: low position 低仓位
                data = BABA: pandas_datareader.data.get_data_yahoo style dataframe. Used "Adj Close" as the stock price.
    
    """



    start_date = data.index[0]
    end_date = data.index[-1]

    last_transaction = 0

    position = np.ones(len(data)) * position_hi
    num_stocks = np.ones(len(data)) * principal * position_hi / data.iloc[0]["Adj Close"]
    book_value = np.ones(len(data)) * principal


    if strategy == 'Early_Profit_Taker':
        tol_profit = tol_lo
        tol_loss = tol_hi
    else: 
        assert strategy == 'Early_Loss_Taker'
        tol_profit = tol_hi
        tol_loss = tol_lo
    
    for idx in range(1, len(data)):
        book_value[idx] = book_value[idx - 1] + num_stocks[idx] * (data.iloc[idx]["Adj Close"] / data.iloc[idx - 1]["Adj Close"] - 1)
        if position[idx] == position_lo: # currently in position_lo and last transaction was selling, now buy
            if data.iloc[idx]["Adj Close"] / data.iloc[last_transaction]["Adj Close"] - 1 > tol_loss: # the price increases over the tolerance of loss after selling
                position[idx + 1:] = position_hi # buy
                num_stocks[idx + 1:] = (book_value[idx] * position_hi) / data.iloc[idx]["Adj Close"] # num_stocks decided at buying, high position
                last_transaction = idx # record
            else:
                continue
        else: # currently in position_hi and last transaction was buying
            if (data.iloc[idx]["Adj Close"] / data.iloc[last_transaction]["Adj Close"] - 1 > tol_profit) | \
                (data.iloc[idx]["Adj Close"] / data.iloc[last_transaction]["Adj Close"] - 1 < - tol_loss): # the price increases over the tolerance of profit or decreases over the tolerance of loss after buying
                position[idx + 1:] = position_lo # sell out to position_lo
                num_stocks[idx + 1:] = (book_value[idx] * position_lo) / data.iloc[idx]["Adj Close"] # num_stocks decided at selling, low position
                last_transaction = idx
            else:
                continue
            
    return position, num_stocks, book_value-principal

def plot_strategy_comparison(
    principal = 1e5,
    tol_hi = 0.3,
    tol_lo = 0.1,
    position_hi = 1,
    position_lo = 0.1,
    data = BABA,
):

    position, num_stocks, gain = strategy_modeling(
                                            principal,
                                            'Early_Profit_Taker',
                                            tol_hi,
                                            tol_lo,
                                            position_hi,
                                            position_lo,
                                            data,
                                        )
    position_, num_stocks_, gain_ = strategy_modeling(
                                            principal,
                                            'Early_Loss_Taker',
                                            tol_hi,
                                            tol_lo,
                                            position_hi,
                                            position_lo,
                                            data,
                                        )

    # gridspec_kw: https://stackoverflow.com/questions/10388462/matplotlib-different-size-subplots
    fig,ax = plt.subplots(3, 1, sharex=True, figsize=(14,12), gridspec_kw={'height_ratios': [3, 2, 2]})
    ax[0].plot(data.index, data["Adj Close"])
    ax[0].set_ylabel("Price")
    ax[1].plot(data.index, position)
    ax[1].plot(data.index, position_)
    ax[1].set_ylim(0, 1)
    ax[1].legend(["Early_Profit_Taker", "Early_Loss_Taker"])
    ax[1].set_ylabel("Position")
    ax[2].plot(data.index, gain)
    ax[2].plot(data.index, gain_)
    ax[2].legend(["Early_Profit_Taker", "Early_Loss_Taker"])
    ax[2].set_ylabel("Profits")

    plt.show()
