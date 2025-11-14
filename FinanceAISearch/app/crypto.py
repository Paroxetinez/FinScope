import re
import openai
import numpy as np
import math
import logging
import argparse
import json
from ta import trend, momentum, volatility
import pandas as pd
from datetime import datetime, timedelta
import requests
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))  # app目录
parent_dir = os.path.dirname(current_dir)  # FinanceAISearch目录
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 第三方库导入

# 本地模块导入
try:
    from app.config import Config
    from app.models import User, Conversation, Message, RelatedQuestion, db
    from app.search import serper_search, process_search_results
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前Python路径: {sys.path}")
    raise

config = Config()
openai.api_key = ""

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 设置API Key
API_KEY = ''  # 请将此处替换为你的CoinMarketCap API密钥
BASE_URL = 'https://pro-api.coinmarketcap.com'


def chat_with_openai(sys_prompt, user_prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI API调用失败: {e}")
        return None


def generate_query(token_name):
    # 创建包含token_name的新闻查询
    query = f'"{token_name}" crypto'
    return query


def get_crypto_news(query):
    raw_results = serper_search(query)
    processed_results = process_search_results(raw_results)
    return processed_results


def fetch_token_metadata(token_identifier, identifier_type='name'):
    """
    查询代币的技术元数据
    """
    headers = {
        'X-CMC_PRO_API_KEY': API_KEY,
        'Accept': 'application/json'
    }

    # 确定查询参数
    endpoint_info = '/v2/cryptocurrency/info'
    params_info = {}

    # 先尝试通过名称查询
    if identifier_type == 'name':
        params_info = {'slug': token_identifier.lower()}
    elif identifier_type == 'symbol':
        params_info = {'symbol': token_identifier.upper()}
    elif identifier_type == 'address':
        params_info = {'address': token_identifier}
    else:
        raise ValueError("identifier_type 必须是 'name'、'symbol' 或 'address'")

    # 获取代币技术信息
    response_info = requests.get(
        BASE_URL + endpoint_info, headers=headers, params=params_info)
    if response_info.status_code != 200:
        error_message = response_info.json().get('status', {}).get('error_message', '未知错误')
        raise Exception(f"获取技术信息失败: {error_message}")

    info_data = response_info.json().get('data', {})

    # 确认是否有有效结果
    if not info_data:
        # 如果没有找到，尝试通过符号查询
        if identifier_type == 'name':
            # 通过符号查询
            params_info = {'symbol': token_identifier.upper()}
            response_info = requests.get(
                BASE_URL + endpoint_info, headers=headers, params=params_info)
            if response_info.status_code != 200:
                error_message = response_info.json().get('status', {}).get('error_message', '未知错误')
                raise Exception(f"获取技术信息失败: {error_message}")

            info_data = response_info.json().get('data', {})

    # 确认是否有有效结果
    if not info_data:
        raise Exception(f"未找到与 {token_identifier} 匹配的代币")

    # 处理返回的数据，确保只返回第一个代币的信息
    token_id = None
    token_info = None

    if isinstance(info_data, dict):
        # 如果是字典，直接使用
        token_id = list(info_data.keys())[0]  # 获取代币ID
        token_info = info_data[token_id]
    elif isinstance(info_data, list) and len(info_data) > 0:
        # 如果是列表，取第一个元素
        token_info = info_data[0]
        token_id = token_info.get('id')

    # 检查是否成功获取代币ID和信息
    if token_id is None or token_info is None:
        raise Exception(f"未能获取有效的代币信息，返回数据: {info_data}")

    return token_id, token_info


def fetch_token_historical_trends(token_id, interval='hourly', start_time=None, end_time=None):
    """
    查询代币的历史价格走势
    """
    headers = {
        'X-CMC_PRO_API_KEY': API_KEY,
        'Accept': 'application/json'
    }

    # 设置历史数据查询时间范围
    if not end_time:
        end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    if not start_time:
        start_time = (datetime.utcnow() - timedelta(days=7)
                      ).strftime('%Y-%m-%dT%H:%M:%SZ')

    # 获取代币历史价格走势
    endpoint_historical = '/v2/cryptocurrency/quotes/historical'
    params_historical = {
        'id': token_id,
        'time_start': start_time,
        'time_end': end_time,
        'interval': interval
    }
    response_historical = requests.get(
        BASE_URL + endpoint_historical, headers=headers, params=params_historical)
    if response_historical.status_code != 200:
        raise Exception(f"获取历史走势失败: {response_historical.json().get('status', {}).get('error_message', '未知错误')}")
    historical_data = response_historical.json().get('data', {}).get('quotes', [])

    return historical_data


def transform_backend_data_pandas(backend_data):
    """
    将后端返回的字典数据转换为适合处理的格式
    """
    df = pd.json_normalize(backend_data)

    if 'timestamp' not in df.columns or 'quote.USD.price' not in df.columns:
        raise KeyError("后端数据缺少必要的字段 'timestamp' 或 'quote.USD.price'")

    try:
        df['timestamp'] = pd.to_datetime(df['timestamp']).astype(int) // 10**9
    except AttributeError:
        df['timestamp'] = pd.to_datetime(
            df['timestamp']).view('int64') // 10**9

    df['price'] = df['quote.USD.price']

    data = {
        'timestamp': df['timestamp'].tolist(),
        'price': df['price'].tolist(),
    }

    return data


def process_stock_data(data):
    """
    将字典数据转换为 DataFrame，并计算技术指标
    """
    df = pd.DataFrame(data)

    # 将 Unix 时间戳转换为 datetime 对象
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # 设置时间戳为索引
    df.set_index('timestamp', inplace=True)

    # 计算 EMA (Exponential Moving Average)
    df['EMA_12'] = df['price'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['price'].ewm(span=26, adjust=False).mean()

    # 计算 MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # 计算 RSI (Relative Strength Index)
    rsi = momentum.RSIIndicator(close=df['price'], window=14)
    df['RSI'] = rsi.rsi()

    # 计算布林带
    bollinger = volatility.BollingerBands(close=df['price'], window=20, window_dev=2)
    df['Bollinger_High'] = bollinger.bollinger_hband()
    df['Bollinger_Low'] = bollinger.bollinger_lband()
    df['Bollinger_Middle'] = bollinger.bollinger_mavg()
    df['Bollinger_Width'] = df['Bollinger_High'] - df['Bollinger_Low']

    # 计算支撑位和阻力位
    df['support'] = df['price'].rolling(window=20).min()  # 20日最低价作为支撑位
    df['resistance'] = df['price'].rolling(window=20).max()  # 20日最高价作为阻力位

    return df


def extract_key_points(df):
    """
    从技术指标中提取关键点位和数据，并以文本格式返回。

    参数：
        df (pd.DataFrame): 包含技术指标的股票数据 DataFrame。

    返回：
        str: 包含强信号的文本报告。
    """
    report = []

    # 1. EMA 交叉信号
    df['EMA_Crossover'] = 0
    df['EMA_Crossover'] = np.where(df['EMA_12'] > df['EMA_26'], 1, -1)
    df['EMA_Signal'] = df['EMA_Crossover'].diff()

    # 2. MACD 信号
    df['MACD_Signal_Diff'] = df['MACD'] - df['MACD_Signal']
    df['MACD_Signal_Change'] = df['MACD_Signal_Diff'].diff()

    # 3. 布林带信号
    df['Bollinger_Signal'] = 0
    df['Bollinger_Signal'] = np.where(df['price'] >= df['Bollinger_High'], -1, df['Bollinger_Signal'])  # 强卖出信号
    df['Bollinger_Signal'] = np.where(df['price'] <= df['Bollinger_Low'], 1, df['Bollinger_Signal'])  # 强买入信号

    # 4. 同时检查强信号
    for idx, row in df.iterrows():
        signals = [0, 0]  # [EMA信号, MACD信号]

        # 检查EMA信号
        if row['EMA_Signal'] == 2:  # 强买入信号
            signals[0] = 1
        elif row['EMA_Signal'] == -2:  # 强卖出信号
            signals[0] = -1

        # 检查MACD信号
        if (row['MACD_Signal_Change'] > 0) and (row['MACD_Signal_Diff'] > 0):  # 强买入信号
            signals[1] = 1
        elif (row['MACD_Signal_Change'] < 0) and (row['MACD_Signal_Diff'] < 0):  # 强卖出信号
            signals[1] = -1

        # 检查布林带信号
        if row['Bollinger_Signal'] == 1:  # 强买入信号
            signals.append(1)
        elif row['Bollinger_Signal'] == -1:  # 强卖出信号
            signals.append(-1)

        # 判断是否有两个信号同向
        if signals.count(1) >= 2:
            report.append(f"强买入信号 - 时间: {idx}, 价格: {row['price']:.2f}")
        elif signals.count(-1) >= 2:
            report.append(f"强卖出信号 - 时间: {idx}, 价格: {row['price']:.2f}")

    # 5. 最新技术指标状态
    latest = df.iloc[-1]
    report.append("\n最新技术指标状态:")
    report.append(f"  - 最新价格: {latest['price']:.2f}")
    report.append(f"  - EMA12: {latest['EMA_12']:.2f}, EMA26: {latest['EMA_26']:.2f}")
    report.append(f"  - MACD: {latest['MACD']:.2f}, 信号线: {latest['MACD_Signal']:.2f}")
    report.append(f"  - 布林带上限: {latest['Bollinger_High']:.2f}, 布林带下限: {latest['Bollinger_Low']:.2f}")
    
    # 打印支撑位和阻力位
    report.append(f"  - 支撑位: {latest['support']:.2f}, 阻力位: {latest['resistance']:.2f}")

    return "\n".join(report)


def compress_to_n_points(df, target_points=10):
    """
    将DataFrame压缩到指定数量的数据点。
    """
    total_points = len(df)

    if total_points <= target_points:
        # 如果数据点少于或等于目标点数，重复最后一个点以达到目标
        if total_points == 0:
            raise ValueError("没有数据点可压缩")
        last_point = df.iloc[-1]
        padding = pd.DataFrame([last_point] * (target_points - total_points),
                               index=pd.date_range(start=df.index[-1] + timedelta(seconds=1),
                                                   periods=target_points - total_points,
                                                   freq='S'))
        df_compressed = pd.concat([df, padding])
        return df_compressed
    else:
        # 使用numpy.array_split将DataFrame分割成目标数量的部分
        split_dfs = np.array_split(df, target_points)
        aggregated = []

        for split in split_dfs:
            agg_dict = {
                'timestamp': split.index[0].strftime('%Y-%m-%d %H:%M:%S'),
                'open': round(split['price'].iloc[0], 2),
                'high': round(split['price'].max(), 2),
                'low': round(split['price'].min(), 2),
                'close': round(split['price'].iloc[-1], 2),
                'EMA_12_avg': round(split['EMA_12'].mean(), 2),
                'EMA_26_avg': round(split['EMA_26'].mean(), 2),
                'MACD_avg': round(split['MACD'].mean(), 2),
                'MACD_Signal_avg': round(split['MACD_Signal'].mean(), 2),
                'MACD_Hist_avg': round(split['MACD_Hist'].mean(), 2),
                'RSI_avg': round(split['RSI'].mean(), 2),
                'Bollinger_High_avg': round(split['Bollinger_High'].mean(), 2),
                'Bollinger_Low_avg': round(split['Bollinger_Low'].mean(), 2),
                'Bollinger_Middle_avg': round(split['Bollinger_Middle'].mean(), 2)
            }
            aggregated.append(agg_dict)

        df_compressed = pd.DataFrame(aggregated)
        return df_compressed


def compress_token_data_for_llm(token_identifier, identifier_type='name', fetch_interval='hourly', start_time=None, end_time=None):
    """
    自动压缩代币的技术分析和走势相关内容，并返回适合LLM分析的文本数据。

    参数：
        token_identifier (str): 代币的名称、符号或地址。
        identifier_type (str): 标识类型，可为 'name'、'symbol' 或 'address'。
        fetch_interval (str): 获取历史数据的时间间隔，如 'minutely', '5min', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'。
        start_time (str): 开始时间，格式 'YYYY-MM-DDTHH:MM:SSZ'，默认是当前时间的7天前。
        end_time (str): 结束时间，格式 'YYYY-MM-DDTHH:MM:SSZ'，默认是当前时间。

    返回：
        str: 包含代币元数据和压缩后的聚合数据的文本，适合LLM分析。
    """
    try:
        numeric_id, metadata = fetch_token_metadata(
            token_identifier, identifier_type=identifier_type)
        logging.info("精简元数据")
        print(metadata)
        simplified_metadata = {
            "id": metadata.get("id"),
            "name": metadata.get("name"),
            "symbol": metadata.get("symbol"),
            "description": metadata.get("description")  # 只保留描述
        }
        print(f"simplified_metadata {simplified_metadata}")
        print(f"获取到 {metadata.get('name')} 的ID: {numeric_id}")

        # 2. 使用获取到的数字ID查询历史数据
        print("正在获取历史数据...")
        historical_trends = fetch_token_historical_trends(numeric_id, interval=fetch_interval, start_time=start_time, end_time=end_time)

        # 3. 处理数据
        print("正在处理数据...")
        transformed_data = transform_backend_data_pandas(historical_trends)
        signal_df = process_stock_data(transformed_data)

        # 4. 分析数据
        print("\n技术分析结果")
        data = extract_key_points(signal_df)
        print(data)

        # 5. get related news
        print("\新闻搜索结果：")
        query = generate_query(token_identifier)
        serch_results = serper_search(query)
        print(serch_results)

        #汇总所有信息
        summary_text = f"代币名称: {metadata.get('name')}\n代币符号: {metadata.get('symbol')}\n描述: {metadata.get('description')}\n技术分析结果: {data}\n新闻搜索结果: {serch_results}"
        return summary_text
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return "Error occurred during data processing."


def get_all_infos(token_identifier, identifier_type):
    token_id, metadata = fetch_token_metadata(
        token_identifier, identifier_type=identifier_type)
    # 提取出metadata中的name
    token_name = metadata.get("name")
    print(token_name)



if __name__ == "__main__":
    # get token info for llm
    try:
        print(compress_token_data_for_llm(token_identifier="btc", identifier_type="symbol"))
    except Exception as e:
        print(f"发生错误: {str(e)}")
