#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 15:46:35 2019

@author: dpong
"""

import bs4 as bs
import datetime as dt
import os
import pandas as pd
import quandl
import pickle
import requests
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

def save_sp500_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text,'lxml')
    table = soup.find('table',{'class':'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        string_len = len(ticker) - 1
        tickers_clean = ticker[0:string_len]    
        tickers.append(tickers_clean)
    with open('sp500tickers.pickle','wb') as f:
        pickle.dump(tickers,f)
    return tickers

def get_data_from_quandl(reload_sp500=False):
    quandl.ApiConfig.api_key = "MYSsxrxJt_P37mBkd5Xy"
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open('sp500tickers.pickle','rb') as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    for ticker in tickers:
        try:
            if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
                quandl_ticker = 'WIKI/'+ticker
                df = quandl.get(quandl_ticker,start_date="2000-01-01",end_date="2016-12-31")
                df.to_csv('stock_dfs/{}.csv'.format(ticker))
            else:
                print('Already have {}'.format(ticker))
        except:
            pass
    
def compile_data():
    with open('sp500tickers.pickle','rb') as f: 
        tickers = pickle.load(f)
    main_df = pd.DataFrame()
    for ticker in tickers:
        try:
            if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
                pass
            else:
                df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
                df.set_index('Date',inplace=True)
                df.rename(columns = {'Adj. Close':ticker},inplace=True)
                df.drop(['Open','High','Low','Close','Volume'],1,inplace=True)
                df.drop(['Adj. Open','Adj. High','Adj. Low','Adj. Volume'],1,inplace=True)
                df.drop(['Ex-Dividend','Split Ratio'],1,inplace=True)
                if main_df.empty:
                    main_df = df
                else:
                    main_df = main_df.join(df,how='outer')       
        except:
            pass
    main_df.to_csv('sp500_joined_closes.csv')


def visualize_data():
    df = pd.read_csv('sp500_joined_closes.csv')
    
    df_corr = df.corr()
    
    print(df_corr.head())
    
    data = df_corr.values
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    
    heatmap = ax.pcolor(data,cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0])+0.5,minor=False)
    ax.set_yticks(np.arange(data.shape[1])+0.5,minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    
    column_lables = df_corr.columns
    row_lables = df_corr.index
    
    ax.set_xticklabels(column_lables)
    ax.set_yticklabels(row_lables)
    
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    #fig.savefig('sp500_corr_heatmap',dpi=300)   #optional
        
            



            
            
            
            
            
            
    
    