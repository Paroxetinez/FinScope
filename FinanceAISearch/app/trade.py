import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from stock import (
    fetch_stock_data, calculate_ma, calculate_macd, 
    calculate_rsi, calculate_bollinger_bands
)

class TradingStrategy:
    def __init__(self, data):
        self.data = data.copy()
        if isinstance(self.data['Close'], pd.DataFrame):
            self.close = self.data['Close'].iloc[:, 0]
        else:
            self.close = self.data['Close']
        
        # 获取优化后的参数
        optimizer = ParameterOptimizer(data)
        self.params = optimizer.get_optimized_parameters()
        
    def generate_ma_cross_signals(self):
        """均线交叉策略"""
        try:
            p = self.params['MA']
            self.data['MA_Short'] = calculate_ma(self.data, p['short_period'])
            self.data['MA_Long'] = calculate_ma(self.data, p['long_period'])
            self.data['Signal'] = 0
            
            # 使用阈值来减少假信号
            diff_pct = (self.data['MA_Short'] - self.data['MA_Long']) / self.data['MA_Long']
            crosses = (diff_pct > p['signal_threshold']) & (diff_pct.shift(1) <= p['signal_threshold'])
            death_crosses = (diff_pct < -p['signal_threshold']) & (diff_pct.shift(1) >= -p['signal_threshold'])
            
            self.data.loc[crosses, 'Signal'] = 1
            self.data.loc[death_crosses, 'Signal'] = -1
            
            print(f"MA交叉策略 - 买入信号: {crosses.sum()}, 卖出信号: {death_crosses.sum()}")
            return self.data
            
        except Exception as e:
            print(f"MA交叉策略生成信号时出错: {str(e)}")
            return pd.DataFrame({'Close': self.close, 'Signal': 0}, index=self.data.index)

    def generate_rsi_signals(self):
        """RSI策略"""
        try:
            p = self.params['RSI']
            self.data['RSI'] = calculate_rsi(self.data, window=p['period'])
            self.data['Signal'] = 0
            
            # 使用优化后的超买超卖阈值
            oversold = self.data['RSI'] < p['oversold']
            overbought = self.data['RSI'] > p['overbought']
            
            self.data.loc[oversold, 'Signal'] = 1
            self.data.loc[overbought, 'Signal'] = -1
            
            print(f"RSI策略 - 买入信号: {oversold.sum()}, 卖出信号: {overbought.sum()}")
            return self.data
            
        except Exception as e:
            print(f"RSI策略生成信号时出错: {str(e)}")
            return pd.DataFrame({'Close': self.close, 'Signal': 0}, index=self.data.index)

    def generate_macd_signals(self):
        """MACD策略"""
        try:
            p = self.params['MACD']
            macd, signal = calculate_macd(self.data, 
                                        fast_span=p['fast_span'],
                                        slow_span=p['slow_span'],
                                        signal_span=p['signal_span'])
            self.data['Signal'] = 0
            
            # 使用阈值来减少假信号
            diff = macd - signal
            golden_cross = (diff > p['signal_threshold']) & (diff.shift(1) <= p['signal_threshold'])
            death_cross = (diff < -p['signal_threshold']) & (diff.shift(1) >= -p['signal_threshold'])
            
            self.data.loc[golden_cross, 'Signal'] = 1
            self.data.loc[death_cross, 'Signal'] = -1
            
            print(f"MACD策略 - 买入信号: {golden_cross.sum()}, 卖出信号: {death_cross.sum()}")
            return self.data
            
        except Exception as e:
            print(f"MACD策略生成信号时出错: {str(e)}")
            return pd.DataFrame({'Close': self.close, 'Signal': 0}, index=self.data.index)

    def generate_bb_signals(self):
        """布林带策略"""
        try:
            p = self.params['BB']
            upper, middle, lower = calculate_bollinger_bands(self.data, 
                                                           window=p['window'],
                                                           std_dev=p['std_dev'])
            self.data['Signal'] = 0
            
            # 使用阈值来减少假信号
            upper_diff = (self.close - upper) / upper
            lower_diff = (self.close - lower) / lower
            
            breakthrough_lower = lower_diff < -p['entry_threshold']
            breakthrough_upper = upper_diff > p['entry_threshold']
            
            self.data.loc[breakthrough_lower, 'Signal'] = 1
            self.data.loc[breakthrough_upper, 'Signal'] = -1
            
            print(f"布林带策略 - 买入信号: {breakthrough_lower.sum()}, 卖出信号: {breakthrough_upper.sum()}")
            return self.data
            
        except Exception as e:
            print(f"布林带策略生成信号时出错: {str(e)}")
            return pd.DataFrame({'Close': self.close, 'Signal': 0}, index=self.data.index)

    # ... [其他策略方法] ...

    def generate_combined_signals(self, weights=None):
        """组合策略"""
        try:
            # 使用市场分析器推荐的权重或默认权重
            if weights is None:
                analyzer = MarketAnalyzer(self.data)
                trend_info = analyzer.analyze_trend()
                if trend_info:
                    recommendations = analyzer.get_strategy_recommendations(trend_info)
                    weights = recommendations['weights']
                else:
                    weights = {'MA': 0.3, 'RSI': 0.2, 'MACD': 0.3, 'BB': 0.2}
            
            # 生成各个策略的信号
            ma_data = self.generate_ma_cross_signals()
            rsi_data = self.generate_rsi_signals()
            macd_data = self.generate_macd_signals()
            bb_data = self.generate_bb_signals()
            
            # 计算加权信号
            signals = pd.DataFrame({
                'MA': ma_data['Signal'] * weights['MA'],
                'RSI': rsi_data['Signal'] * weights['RSI'],
                'MACD': macd_data['Signal'] * weights['MACD'],
                'BB': bb_data['Signal'] * weights['BB']
            }, index=self.data.index)
            
            # 使用波动率信息来调整信号阈值
            vol_info = ParameterOptimizer(self.data).analyze_volatility()
            if vol_info['annual_volatility'] > 40:
                signal_threshold = 0.4  # 高波动需要更强的信号确认
            elif vol_info['annual_volatility'] < 20:
                signal_threshold = 0.2  # 低波动可以更敏感
            else:
                signal_threshold = 0.3  # 中等波动使用默认阈值
            
            # 生成最终信号
            weighted_signal = signals.sum(axis=1)
            self.data['Signal'] = np.where(weighted_signal > signal_threshold, 1,
                                         np.where(weighted_signal < -signal_threshold, -1, 0))
            
            # 添加确认信号
            self.data['Signal'] = self.confirm_signals(self.data['Signal'])
            
            print("\n组合策略信号统计:")
            print(f"买入信号: {(self.data['Signal'] == 1).sum()}")
            print(f"卖出信号: {(self.data['Signal'] == -1).sum()}")
            print(f"持有信号: {(self.data['Signal'] == 0).sum()}")
            
            return self.data
            
        except Exception as e:
            print(f"组合策略生成信号时出错: {str(e)}")
            return pd.DataFrame({'Close': self.close, 'Signal': 0}, index=self.data.index)

    def confirm_signals(self, signals, window=3):
        """
        确认信号，减少虚假信号
        要求信号在短期内保持一致才确认
        """
        confirmed = signals.copy()
        
        # 使用移动窗口来确认信号
        for i in range(window, len(signals)):
            if signals.iloc[i] != 0:  # 只处理非零信号
                # 检查前window个信号是否一致
                prev_signals = signals.iloc[i-window:i]
                if not all(s == 0 for s in prev_signals):  # 如果之前有信号
                    confirmed.iloc[i] = 0  # 取消当前信号
        
        return confirmed

def backtest_signals(data):
    """
    简单回测框架，计算策略收益和基准收益。
    """
    try:
        # 创建数据副本避免修改原始数据
        data = data.copy()
        
        # 确保数据包含必要的列
        required_columns = ['Close', 'Signal']
        if not all(col in data.columns for col in required_columns):
            raise KeyError(f"Missing required columns. Need: {required_columns}")
        
        # 计算持仓
        data['Position'] = data['Signal'].shift(1).fillna(0)
        
        # 计算收益
        data['Daily_Return'] = data['Close'].pct_change().fillna(0)
        data['Strategy_Return'] = data['Position'] * data['Daily_Return']

        # 累计收益计算
        cumulative_strategy = (1 + data['Strategy_Return']).cumprod()
        cumulative_benchmark = (1 + data['Daily_Return']).cumprod()

        # 计算性能指标
        total_days = len(data)
        winning_days = len(data[data['Strategy_Return'] > 0])
        win_rate = winning_days / total_days if total_days > 0 else 0
        
        # 计算最大回撤
        rolling_max = cumulative_strategy.expanding().max()
        daily_drawdown = cumulative_strategy / rolling_max - 1
        max_drawdown = daily_drawdown.min()

        # 计算年化收益率
        years = (data.index[-1] - data.index[0]).days / 365.25
        annual_return = (cumulative_strategy.iloc[-1] ** (1/years) - 1) if years > 0 else 0

        # 计算夏普比率
        risk_free_rate = 0.02  # 假设无风险利率为2%
        excess_returns = data['Strategy_Return'] - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0

        print("\n====== 回测结果 ======")
        print(f"回测期间: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"策略累计收益: {(cumulative_strategy.iloc[-1] - 1) * 100:.2f}%")
        print(f"基准累计收益: {(cumulative_benchmark.iloc[-1] - 1) * 100:.2f}%")
        print(f"年化收益率: {annual_return * 100:.2f}%")
        print(f"夏普比率: {sharpe_ratio:.2f}")
        print(f"胜率: {win_rate * 100:.2f}%")
        print(f"最大回撤: {max_drawdown * 100:.2f}%")
        print(f"交易次数: {(data['Signal'] != 0).sum()}")
        
        return data, cumulative_strategy

    except Exception as e:
        print(f"回测过程中出现错误: {str(e)}")
        return None, None

def test_strategies(ticker, start_date, end_date):
    """
    测试不同的交易策略
    """
    # 获取数据
    print(f"\n获��� {ticker} 从 {start_date} 到 {end_date} 的数据...")
    stock_data = fetch_stock_data(ticker, start_date, end_date)
    if stock_data is None:
        return
    
    # 分析市场趋势
    analyzer = MarketAnalyzer(stock_data)
    trend_info = analyzer.analyze_trend()
    
    if trend_info:
        print("\n====== 市场趋势分析 ======")
        print(f"价格趋势: {trend_info['price_trend']:.2f}%")
        print(f"均线趋势: {trend_info['ma_trend']:.2f}%")
        print(f"波动性: {trend_info['volatility']:.2f}%")
        print(f"市场状态: {trend_info['trend_type']['description']}")
        
        # 获取策略建议
        strategy_recommendations = analyzer.get_strategy_recommendations(trend_info)
        print("\n====== 策略建议 ======")
        print(f"当前市场: {strategy_recommendations['description']}")
        print("\n交易建议:")
        for suggestion in strategy_recommendations['suggestions']:
            print(suggestion)
            
        # 使用推荐的权重
        weights = strategy_recommendations['weights']
    else:
        weights = None
    
    # 创建策略实例
    strategy = TradingStrategy(stock_data)
    
    # 定义要测试的策略
    strategies = {
        'MA交叉策略': strategy.generate_ma_cross_signals,
        'RSI策略': strategy.generate_rsi_signals,
        'MACD策略': strategy.generate_macd_signals,
        '布林带策略': strategy.generate_bb_signals,
        '组合策略': strategy.generate_combined_signals
    }
    
    # 存储每个策略的结果
    results = {}
    
    for name, strategy_func in strategies.items():
        print(f"\n====== 测试 {name} ======")
        
        try:
            # 生成信号
            strategy_data = strategy_func()
            
            # 执行回测
            strategy_data, cumulative_returns = backtest_signals(strategy_data)
            
            if cumulative_returns is not None:
                # 计算月度收益
                monthly_returns = strategy_data['Strategy_Return'].groupby(pd.Grouper(freq='M')).sum()
                
                results[name] = {
                    'returns': cumulative_returns.iloc[-1],
                    'signals': strategy_data['Signal'].value_counts(),
                    'monthly_returns': monthly_returns,
                    'data': strategy_data  # 保存完整的策略数据
                }
        except Exception as e:
            print(f"{name} 测试失败: {str(e)}")
            continue
    
    # 比较策略结果
    print("\n====== 策略比较 ======")
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"累计收益: {(result['returns'] - 1) * 100:.2f}%")
        print("\n月度收益:")
        for date, ret in result['monthly_returns'].items():
            print(f"{date.strftime('%Y-%m')}: {ret*100:.2f}%")
        print("\n信号分布:")
        print(result['signals'])
    
    return results

def main():
    # 设置参数
    ticker = 'AAPL'
    end_date = datetime.now().date()
    
    # 参数化时间段选择
    periods = {
        '3个月': 90,
        '6个月': 180,
        '1年': 365,
        '3年': 365 * 3,
        '5年': 365 * 5
    }
    
    # 让用户选择时间段
    print("\n可选择的回测时间段:")
    for i, (period_name, _) in enumerate(periods.items(), 1):
        print(f"{i}. {period_name}")
    
    try:
        choice = int(input("\n请选择回测时间段 (输入数字): "))
        period_name = list(periods.keys())[choice - 1]
        days = periods[period_name]
        start_date = end_date - timedelta(days=days)
        
        print(f"\n分析 {ticker} 最近{period_name}的交易策略表现")
        print(f"分析期间: {start_date} 至 {end_date}")
        
        # 测试所有策略
        results = test_strategies(ticker, start_date, end_date)
        
        # 找出表现最好的策略
        if results:
            best_strategy = max(results.items(), key=lambda x: x[1]['returns'])
            print(f"\n====== 最佳策略: {best_strategy[0]} ======")
            print(f"累计收益: {(best_strategy[1]['returns'] - 1) * 100:.2f}%")
            
            # 显示最新的交易信号
            print("\n当前交易信号:")
            for name, result in results.items():
                latest_signal = result['data']['Signal'].iloc[-1]
                signal_map = {1: "买入", -1: "卖出", 0: "持有"}
                print(f"{name}: {signal_map.get(latest_signal, '未知')}")
                
    except (ValueError, IndexError) as e:
        print(f"输入错误: {str(e)}")
        print("请输入有效的数字 (1-5)")

class MarketAnalyzer:
    def __init__(self, data):
        self.data = data.copy()
        if isinstance(self.data['Close'], pd.DataFrame):
            self.close = self.data['Close'].iloc[:, 0]
        else:
            self.close = self.data['Close']
            
    def analyze_trend(self):
        """
        分析市场趋势
        返回: 'uptrend', 'downtrend', 或 'sideways'
        """
        try:
            # 计算关键指标
            self.data['MA_20'] = calculate_ma(self.data, 20)
            self.data['MA_50'] = calculate_ma(self.data, 50)
            self.data['ATR'] = self.calculate_atr()
            
            # 计算趋势强度
            price_trend = (self.close - self.close.shift(20)) / self.close.shift(20) * 100
            ma_trend = (self.data['MA_20'] - self.data['MA_50']) / self.data['MA_50'] * 100
            
            # 计算波动性
            volatility = self.data['ATR'] / self.close * 100
            
            # 获取最新数据
            current_price_trend = price_trend.iloc[-1]
            current_ma_trend = ma_trend.iloc[-1]
            current_volatility = volatility.iloc[-1]
            
            # 趋势判断
            trend_info = {
                'price_trend': current_price_trend,
                'ma_trend': current_ma_trend,
                'volatility': current_volatility,
                'trend_type': self.determine_trend_type(current_price_trend, current_ma_trend, current_volatility)
            }
            
            return trend_info
            
        except Exception as e:
            print(f"趋势分析错误: {str(e)}")
            return None
            
    def calculate_atr(self, period=14):
        """计算平均真实波幅(ATR)"""
        high = self.data['High']
        low = self.data['Low']
        close = self.data['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
        
    def determine_trend_type(self, price_trend, ma_trend, volatility):
        """
        根据各项指标确定趋势类型
        """
        trend_strength = (price_trend + ma_trend) / 2
        
        if trend_strength > 5 and volatility < 2:
            return {'type': 'strong_uptrend', 'description': '强势上涨趋势'}
        elif trend_strength > 2:
            return {'type': 'uptrend', 'description': '上涨趋势'}
        elif trend_strength < -5 and volatility < 2:
            return {'type': 'strong_downtrend', 'description': '强势下跌趋势'}
        elif trend_strength < -2:
            return {'type': 'downtrend', 'description': '下跌趋势'}
        elif volatility > 3:
            return {'type': 'volatile_sideways', 'description': '高波动盘整'}
        else:
            return {'type': 'sideways', 'description': '盘整'}

    def get_strategy_recommendations(self, trend_info):
        """
        根据市场趋势推荐交易策略
        """
        trend_type = trend_info['trend_type']['type']
        
        strategy_weights = {
            'strong_uptrend': {
                'MA': 0.4,    # 趋势跟踪
                'RSI': 0.1,   # 减少超买超卖权重
                'MACD': 0.4,  # 趋势确认
                'BB': 0.1     # 减少区间交易权重
            },
            'uptrend': {
                'MA': 0.35,
                'RSI': 0.15,
                'MACD': 0.35,
                'BB': 0.15
            },
            'strong_downtrend': {
                'MA': 0.4,
                'RSI': 0.2,   # 增加超买超卖权重
                'MACD': 0.3,
                'BB': 0.1
            },
            'downtrend': {
                'MA': 0.35,
                'RSI': 0.25,
                'MACD': 0.25,
                'BB': 0.15
            },
            'volatile_sideways': {
                'MA': 0.1,    # 减��趋势跟踪
                'RSI': 0.4,   # 增加超买超卖
                'MACD': 0.1,
                'BB': 0.4     # 增加区间交易
            },
            'sideways': {
                'MA': 0.2,
                'RSI': 0.3,
                'MACD': 0.2,
                'BB': 0.3
            }
        }
        
        return {
            'weights': strategy_weights.get(trend_type),
            'description': trend_info['trend_type']['description'],
            'suggestions': self.get_trading_suggestions(trend_type)
        }
        
    def get_trading_suggestions(self, trend_type):
        """
        根据趋势类型提供具体的交易建议
        """
        suggestions = {
            'strong_uptrend': [
                "1. 以趋势跟踪为主",
                "2. 回调时买入",
                "3. 持仓时间可以较长",
                "4. 止损位可以放宽"
            ],
            'uptrend': [
                "1. 结合趋势和震荡策略",
                "2. 关注支撑位买入",
                "3. 适度持仓",
                "4. 设置跟踪止损"
            ],
            'strong_downtrend': [
                "1. 以观望为主",
                "2. 不建议抄底",
                "3. 可以考虑做空",
                "4. 严格止损"
            ],
            'downtrend': [
                "1. 减少交易频率",
                "2. 等待反转信号",
                "3. 以保护资金为主",
                "4. 只在强支撑位考虑买入"
            ],
            'volatile_sideways': [
                "1. 使用区间交易策略",
                "2. 在支撑位买入，阻力位卖出",
                "3. 设置较窄的止损",
                "4. 获利及时了结"
            ],
            'sideways': [
                "1. 使用震荡策略",
                "2. 关注突破信号",
                "3. 控制仓位",
                "4. 设置合理止损"
            ]
        }
        return suggestions.get(trend_type, ["无具体建议"])

class ParameterOptimizer:
    def __init__(self, data):
        self.data = data.copy()
        if isinstance(self.data['Close'], pd.DataFrame):
            self.close = self.data['Close'].iloc[:, 0]
        else:
            self.close = self.data['Close']
            
    def analyze_volatility(self):
        """分析股票的历史波动特征"""
        # 计算历史波动率
        returns = self.close.pct_change()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        # 计算平均日波动幅度
        daily_range = (self.data['High'] - self.data['Low']) / self.data['Close']
        avg_range = daily_range.mean() * 100  # 转换为百分比
        
        return {
            'annual_volatility': volatility * 100,  # 转换为百分
            'avg_daily_range': avg_range,
            'price_level': self.close.mean()
        }
    
    def get_optimized_parameters(self):
        """根据股票特征优化策略参数"""
        vol_info = self.analyze_volatility()
        
        # 根据波动率调整参数
        params = {
            'MA': self.optimize_ma_params(vol_info),
            'RSI': self.optimize_rsi_params(vol_info),
            'MACD': self.optimize_macd_params(vol_info),
            'BB': self.optimize_bb_params(vol_info)
        }
        
        return params
    
    def optimize_ma_params(self, vol_info):
        """优化均线参数"""
        if vol_info['annual_volatility'] > 40:  # 高波动
            return {
                'short_period': 10,  # 使用更长的短期均线
                'long_period': 30,   # 使用更长的长期均线
                'signal_threshold': 0.02  # 需要更大的差距才触发信号
            }
        elif vol_info['annual_volatility'] < 20:  # 低波动
            return {
                'short_period': 5,
                'long_period': 20,
                'signal_threshold': 0.01
            }
        else:  # 中等波动
            return {
                'short_period': 8,
                'long_period': 25,
                'signal_threshold': 0.015
            }
    
    def optimize_rsi_params(self, vol_info):
        """优化RSI参数"""
        if vol_info['annual_volatility'] > 40:
            return {
                'period': 14,
                'oversold': 25,  # 更低的超卖阈值
                'overbought': 75  # 更高的超买阈值
            }
        elif vol_info['annual_volatility'] < 20:
            return {
                'period': 14,
                'oversold': 35,
                'overbought': 65
            }
        else:
            return {
                'period': 14,
                'oversold': 30,
                'overbought': 70
            }
    
    def optimize_macd_params(self, vol_info):
        """优化MACD参数"""
        if vol_info['annual_volatility'] > 40:
            return {
                'fast_span': 15,
                'slow_span': 30,
                'signal_span': 12,
                'signal_threshold': 0.02
            }
        elif vol_info['annual_volatility'] < 20:
            return {
                'fast_span': 12,
                'slow_span': 26,
                'signal_span': 9,
                'signal_threshold': 0.01
            }
        else:
            return {
                'fast_span': 13,
                'slow_span': 28,
                'signal_span': 10,
                'signal_threshold': 0.015
            }
    
    def optimize_bb_params(self, vol_info):
        """优化布林带参数"""
        if vol_info['annual_volatility'] > 40:
            return {
                'window': 25,
                'std_dev': 2.5,  # 更宽的带宽
                'entry_threshold': 0.02  # 需要更明显的突破
            }
        elif vol_info['annual_volatility'] < 20:
            return {
                'window': 15,
                'std_dev': 1.8,
                'entry_threshold': 0.01
            }
        else:
            return {
                'window': 20,
                'std_dev': 2.0,
                'entry_threshold': 0.015
            }

if __name__ == "__main__":
    main()
