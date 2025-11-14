import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fetch_stock_data(ticker, start_date, end_date):
    """获取股票历史数据"""
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        print(f"No data fetched for {ticker} between {start_date} and {end_date}.")
        return None
    return df

def calculate_ma(data, window):
    """计算移动平均线(MA)"""
    if isinstance(data['Close'], pd.DataFrame):
        close = data['Close'].iloc[:, 0]
    else:
        close = data['Close']
    return close.rolling(window=window, min_periods=1).mean()

def calculate_ema(data, span):
    """计算指数平滑移动平均线(EMA)"""
    if isinstance(data['Close'], pd.DataFrame):
        close = data['Close'].iloc[:, 0]
    else:
        close = data['Close']
    return close.ewm(span=span, min_periods=1, adjust=False).mean()

def calculate_macd(data, fast_span=12, slow_span=26, signal_span=9):
    """计算MACD"""
    if isinstance(data['Close'], pd.DataFrame):
        close = data['Close'].iloc[:, 0]
    else:
        close = data['Close']
    
    fast_ema = close.ewm(span=fast_span, min_periods=1, adjust=False).mean()
    slow_ema = close.ewm(span=slow_span, min_periods=1, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_span, min_periods=1, adjust=False).mean()
    
    return macd_line, signal_line

def calculate_rsi(data, window=14):
    """计算RSI"""
    if isinstance(data['Close'], pd.DataFrame):
        close = data['Close'].iloc[:, 0]
    else:
        close = data['Close']
        
    delta = close.diff(1)
    delta.iloc[0] = 0
    
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss.replace(0, float('inf'))
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(data, window=20, std_dev=2):
    """计算布林带"""
    try:
        if isinstance(data['Close'], pd.DataFrame):
            close = data['Close'].iloc[:, 0]
        else:
            close = data['Close']
            
        sma = close.rolling(window=window, min_periods=1).mean()
        std = close.rolling(window=window, min_periods=1).std()
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
        
    except Exception as e:
        print(f"计算布林带时出错: {str(e)}")
        return None, None, None

def fetch_financials(ticker):
    """获取公司财务数据"""
    stock = yf.Ticker(ticker)
    try:
        financials = stock.financials
        cashflow = stock.cashflow
        balance_sheet = stock.balance_sheet
        revenue = financials.loc['Total Revenue'] if 'Total Revenue' in financials.index else None
        
        return {
            "financials": financials,
            "cashflow": cashflow,
            "balance_sheet": balance_sheet,
            "revenue": revenue
        }
    except Exception as e:
        print(f"Error fetching financials for {ticker}: {str(e)}")
        return None

