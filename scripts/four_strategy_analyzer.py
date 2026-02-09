#!/usr/bin/env python3
# 四策略投資分析器 (修正版 - 解決 numpy 數據類型和時間顯示問題)

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import yfinance as yf
import numpy as np

def convert_numpy_types(obj):
    """將 numpy 數據類型轉換為 Python 原生類型"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

class FourStrategyAnalyzer:
    """四策略投資分析器"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stock_list = [
            '2330.TW', '2317.TW', '2454.TW', '2308.TW', '2881.TW', '2882.TW',
            '1301.TW', '1303.TW', '2002.TW', '2412.TW', '1216.TW', '2357.TW',
            '2382.TW', '3008.TW', '3711.TW', '2303.TW', '2886.TW', '5880.TW',
            '2891.TW', '2892.TW'
        ]
        
        # 篩選條件
        self.criteria = {
            'min_volume': 1000,
            'max_pe_ratio': 30,
            'min_price': 10,
            'max_price': 500,
            'min_market_cap': 10_000_000_000
        }
    
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """獲取股票數據"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="60d")
            
            if hist.empty or 'currentPrice' not in info:
                return None
            
            # 計算技術指標
            close_prices = hist['Close']
            volumes = hist['Volume']
            
            # 20日均線
            ma20 = close_prices.rolling(20).mean().iloc[-1]
            current_price = close_prices.iloc[-1]
            
            # RSI 計算
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # MACD
            exp12 = close_prices.ewm(span=12).mean()
            exp26 = close_prices.ewm(span=26).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9).mean()
            macd_hist = macd - signal
            
            stock_data = {
                'symbol': symbol.replace('.TW', ''),
                'name': info.get('longName', symbol),
                'price': float(current_price),
                'ma20': float(ma20),
                'rsi': float(rsi),
                'macd': float(macd.iloc[-1]),
                'macd_signal': float(signal.iloc[-1]),
                'macd_hist': float(macd_hist.iloc[-1]),
                'volume': int(volumes.iloc[-1]),
                'avg_volume_20': float(volumes.rolling(20).mean().iloc[-1]),
                'pe_ratio': float(info.get('trailingPE', 0)) if info.get('trailingPE') else 0,
                'pb_ratio': float(info.get('priceToBook', 0)) if info.get('priceToBook') else 0,
                'dividend_yield': float(info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0,
                'market_cap': int(info.get('marketCap', 0)) if info.get('marketCap') else 0,
                'roe': float(info.get('returnOnEquity', 0) * 100) if info.get('returnOnEquity') else 0,
                'change_percent': float(((current_price - close_prices.iloc[-2]) / close_prices.iloc[-2]) * 100)
            }
            
            return stock_data
            
        except Exception as e:
            print(f"獲取 {symbol} 數據失敗: {str(e)}")
            return None
    
    def technical_strategy(self, stocks: List[Dict]) -> List[Dict]:
        """技術面主導策略"""
        results = []
        
        for stock in stocks:
            if not stock:
                continue
                
            # 技術面篩選條件
            conditions = [
                stock['price'] > stock['ma20'],  # 股價 > 20日均線
                stock['volume'] > stock['avg_volume_20'],  # 成交量 > 20日均量
                stock['rsi'] < 70,  # 避免超買
                stock['volume'] > self.criteria['min_volume'],
                self.criteria['min_price'] <= stock['price'] <= self.criteria['max_price']
            ]
            
            if all(conditions):
                # 計算策略分數
                score = 0
                if stock['price'] > stock['ma20']:
                    score += 30
                if stock['volume'] > stock['avg_volume_20']:
                    score += 25
                if stock['rsi'] < 30:  # 超賣區域
                    score += 25
                elif stock['rsi'] < 50:
                    score += 15
                if stock['macd_hist'] > 0:  # MACD 金叉
                    score += 20
                    
                stock['strategy_score'] = round(score, 2)
                results.append(stock)
        
        return sorted(results, key=lambda x: x['strategy_score'], reverse=True)[:10]
    
    def fundamental_strategy(self, stocks: List[Dict]) -> List[Dict]:
        """基本面主導策略"""
        results = []
        
        for stock in stocks:
            if not stock:
                continue
                
            # 基本面篩選條件
            conditions = [
                stock['pe_ratio'] > 0 and stock['pe_ratio'] < 25,  # 合理本益比
                stock['pb_ratio'] > 0 and stock['pb_ratio'] < 2,   # 合理股價淨值比
                stock['market_cap'] > self.criteria['min_market_cap'],
                self.criteria['min_price'] <= stock['price'] <= self.criteria['max_price'],
                stock['volume'] > self.criteria['min_volume']
            ]
            
            if all(conditions):
                # 計算策略分數
                score = 0
                # 價值投資評分
                if stock['pe_ratio'] < 15:
                    score += 30
                elif stock['pe_ratio'] < 20:
                    score += 20
                else:
                    score += 10
                    
                if stock['pb_ratio'] < 1.5:
                    score += 25
                elif stock['pb_ratio'] < 2:
                    score += 15
                else:
                    score += 5
                    
                if stock['dividend_yield'] > 4:
                    score += 25
                elif stock['dividend_yield'] > 2:
                    score += 15
                    
                if stock['roe'] > 15:
                    score += 20
                    
                stock['strategy_score'] = round(score, 2)
                results.append(stock)
        
        return sorted(results, key=lambda x: x['strategy_score'], reverse=True)[:10]
    
    def hybrid_strategy(self, stocks: List[Dict]) -> List[Dict]:
        """混合策略"""
        results = []
        
        for stock in stocks:
            if not stock:
                continue
                
            # 混合篩選條件
            conditions = [
                stock['price'] > stock['ma20'],  # 技術面趨勢
                stock['pe_ratio'] > 0 and stock['pe_ratio'] < 30,  # 基本面合理
                stock['volume'] > self.criteria['min_volume'],
                self.criteria['min_price'] <= stock['price'] <= self.criteria['max_price'],
                stock['market_cap'] > self.criteria['min_market_cap']
            ]
            
            if all(conditions):
                # 綜合策略分數
                score = 0
                # 技術面 (50%)
                if stock['price'] > stock['ma20']:
                    score += 25
                if stock['rsi'] < 50:
                    score += 15
                if stock['macd_hist'] > 0:
                    score += 10
                    
                # 基本面 (50%)
                if stock['pe_ratio'] < 20:
                    score += 20
                if stock['roe'] > 10:
                    score += 15
                if stock['dividend_yield'] > 3:
                    score += 15
                    
                stock['strategy_score'] = round(score, 2)
                results.append(stock)
        
        return sorted(results, key=lambda x: x['strategy_score'], reverse=True)[:10]
    
    def thematic_strategy(self, stocks: List[Dict]) -> Dict[str, List[Dict]]:
        """特定主題策略"""
        high_dividend = []
        growth_stocks = []
        value_stocks = []
        
        for stock in stocks:
            if not stock:
                continue
                
            # 高股息策略
            if (stock['dividend_yield'] > 4 and 
                stock['pe_ratio'] > 0 and stock['pe_ratio'] < 25 and
                stock['volume'] > self.criteria['min_volume']):
                stock_copy = stock.copy()
                stock_copy['strategy_score'] = round(stock['dividend_yield'] * 2 + 
                                                   (25 - stock['pe_ratio']) if stock['pe_ratio'] < 25 else 0, 2)
                high_dividend.append(stock_copy)
            
            # 成長股策略
            if (stock['roe'] > 15 and 
                stock['pe_ratio'] > 0 and stock['pe_ratio'] < 30 and
                stock['market_cap'] > 50_000_000_000 and
                stock['volume'] > self.criteria['min_volume']):
                stock_copy = stock.copy()
                stock_copy['strategy_score'] = round(stock['roe'] + 
                                                   (30 - stock['pe_ratio']) if stock['pe_ratio'] < 30 else 0, 2)
                growth_stocks.append(stock_copy)
            
            # 價值股策略
            if (stock['pe_ratio'] > 0 and stock['pe_ratio'] < 15 and
                stock['pb_ratio'] > 0 and stock['pb_ratio'] < 1.5 and
                stock['dividend_yield'] > 3 and
                stock['volume'] > self.criteria['min_volume']):
                stock_copy = stock.copy()
                stock_copy['strategy_score'] = round((15 - stock['pe_ratio']) + 
                                                   (1.5 - stock['pb_ratio']) * 10 + 
                                                   stock['dividend_yield'], 2)
                value_stocks.append(stock_copy)
        
        return {
            'high_dividend': sorted(high_dividend, key=lambda x: x['strategy_score'], reverse=True)[:5],
            'growth_stocks': sorted(growth_stocks, key=lambda x: x['strategy_score'], reverse=True)[:5],
            'value_stocks': sorted(value_stocks, key=lambda x: x['strategy_score'], reverse=True)[:5]
        }
    
    def analyze_all_strategies(self) -> Dict[str, Any]:
        """分析所有策略"""
        print("收集股票數據...")
        stocks = []
        for symbol in self.stock_list:
            stock_data = self.get_stock_data(symbol)
            if stock_data:
                stocks.append(stock_data)
            # 避免請求過快
            import time
            time.sleep(0.1)
        
        print(f"成功獲取 {len(stocks)} 支股票數據")
        
        # 執行四種策略
        technical_results = self.technical_strategy(stocks)
        fundamental_results = self.fundamental_strategy(stocks)
        hybrid_results = self.hybrid_strategy(stocks)
        thematic_results = self.thematic_strategy(stocks)
        
        result = {
            'date': self.today,
            'report_time': self.report_time,
            'timestamp': datetime.now().isoformat(),
            'total_stocks_analyzed': len(stocks),
            'technical_strategy': technical_results,
            'fundamental_strategy': fundamental_results,
            'hybrid_strategy': hybrid_results,
            'thematic_strategy': thematic_results,
            'data_source': 'Yahoo Finance + 技術指標計算'
        }
        
        # 轉換 numpy 類型
        return convert_numpy_types(result)

if __name__ == "__main__":
    analyzer = FourStrategyAnalyzer()
    results = analyzer.analyze_all_strategies()
    
    # 保存結果
    output_dir = "/home/admin/.openclaw/workspace/investment/reports"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/four_strategy_report_{results['date']}.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"四策略分析完成！結果已保存到: four_strategy_report_{results['date']}.json")
    
    # 顯示摘要
    print("\n📊 分析結果摘要:")
    print(f"技術面策略: {len(results['technical_strategy'])} 支股票")
    print(f"基本面策略: {len(results['fundamental_strategy'])} 支股票")  
    print(f"混合策略: {len(results['hybrid_strategy'])} 支股票")
    print(f"主題策略 - 高股息: {len(results['thematic_strategy']['high_dividend'])} 支")
    print(f"主題策略 - 成長股: {len(results['thematic_strategy']['growth_stocks'])} 支")
    print(f"主題策略 - 價值股: {len(results['thematic_strategy']['value_stocks'])} 支")