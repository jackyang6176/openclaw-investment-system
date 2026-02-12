#!/usr/bin/env python3
# 完整交易建議系統 - 包含買賣點、獲利目標、停損點

import json
from datetime import datetime

class CompleteTradingAdvisor:
    """完整交易建議系統"""
    
    def __init__(self):
        self.chinese_names = {
            '2330': '台積電',
            '2317': '鴻海', 
            '2454': '聯發科',
            '2308': '台達電',
            '2881': '富邦金',
            '2882': '國泰金',
            '1301': '台塑',
            '1303': '南亞',
            '2002': '中鋼',
            '2412': '中華電',
            '1216': '統一',
            '2357': '華碩',
            '2382': '廣達',
            '3008': '大立光',
            '3711': '日月光投控',
            '2303': '聯電',
            '2886': '兆豐金',
            '5880': '合庫金',
            '2891': '中信金',
            '2892': '第一金'
        }
    
    def calculate_trading_points(self, stock_data):
        """計算完整的交易建議"""
        symbol = stock_data['symbol']
        name = self.chinese_names.get(symbol, symbol)
        price = stock_data['price']
        ma20 = stock_data.get('ma20', 0)
        rsi = stock_data.get('rsi', 50)
        pe_ratio = stock_data.get('pe_ratio', 0)
        dividend_yield = stock_data.get('dividend_yield', 0)
        roe = stock_data.get('roe', 0)
        
        # 計算建議買點（基於技術面和基本面）
        if ma20 > 0:
            buy_point_base = ma20 * 0.98  # 20日均線下方2%
        else:
            buy_point_base = price * 0.95  # 現價下方5%
            
        # 根據基本面調整買點
        if pe_ratio > 0 and pe_ratio < 15:  # 低本益比
            buy_point_adjustment = 1.02  # 可以稍高買入
        elif pe_ratio > 25:  # 高本益比
            buy_point_adjustment = 0.98  # 應該更低買入
        else:
            buy_point_adjustment = 1.0
            
        buy_point = round(buy_point_base * buy_point_adjustment, 2)
        
        # 計算獲利目標（基於技術面阻力位和基本面估值）
        profit_target_1 = round(price * 1.05, 2)  # +5%
        profit_target_2 = round(price * 1.10, 2)  # +10%
        profit_target_3 = round(price * 1.15, 2)  # +15%
        
        # 根據基本面調整獲利目標
        if dividend_yield > 4:  # 高股息
            profit_target_1 = round(price * 1.04, 2)
            profit_target_2 = round(price * 1.08, 2)
            profit_target_3 = round(price * 1.12, 2)
        elif roe > 20:  # 高ROE成長股
            profit_target_1 = round(price * 1.06, 2)
            profit_target_2 = round(price * 1.12, 2)
            profit_target_3 = round(price * 1.18, 2)
            
        # 計算停損點（基於技術面支撐位和風險管理）
        if ma20 > 0:
            stop_loss_base = ma20 * 0.95  # 20日均線下方5%
        else:
            stop_loss_base = price * 0.90  # 現價下方10%
            
        # 根據波動性調整停損
        volatility_factor = 1.0
        if rsi > 70:  # 超買，需要更緊的停損
            volatility_factor = 0.95
        elif rsi < 30:  # 超賣，可以稍寬的停損
            volatility_factor = 1.05
            
        stop_loss = round(stop_loss_base * volatility_factor, 2)
        
        return {
            'symbol': symbol,
            'name': name,
            'current_price': price,
            'buy_point': buy_point,
            'profit_target_1': profit_target_1,
            'profit_target_2': profit_target_2,
            'profit_target_3': profit_target_3,
            'stop_loss': stop_loss,
            'analysis_factors': {
                'technical': f"20日均線: {ma20:.2f}, RSI: {rsi:.1f}",
                'fundamental': f"本益比: {pe_ratio:.1f}, 股利殖利率: {dividend_yield:.1f}%, ROE: {roe:.1f}%"
            }
        }
    
    def generate_complete_report(self, analysis_result):
        """生成完整交易建議報告"""
        report = {
            'date': analysis_result.get('date', datetime.now().strftime('%Y-%m-%d')),
            'report_time': analysis_result.get('report_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'strategies': {}
        }
        
        # 技術面策略交易建議
        technical_advice = []
        for stock in analysis_result.get('technical_strategy', []):
            advice = self.calculate_trading_points(stock)
            technical_advice.append(advice)
        report['strategies']['technical'] = technical_advice
        
        # 基本面策略交易建議
        fundamental_advice = []
        for stock in analysis_result.get('fundamental_strategy', []):
            advice = self.calculate_trading_points(stock)
            fundamental_advice.append(advice)
        report['strategies']['fundamental'] = fundamental_advice
        
        # 混合策略交易建議
        hybrid_advice = []
        for stock in analysis_result.get('hybrid_strategy', []):
            advice = self.calculate_trading_points(stock)
            hybrid_advice.append(advice)
        report['strategies']['hybrid'] = hybrid_advice
        
        # 主題策略交易建議
        thematic_advice = {}
        for theme, stocks in analysis_result.get('thematic_strategy', {}).items():
            theme_advice = []
            for stock in stocks:
                advice = self.calculate_trading_points(stock)
                theme_advice.append(advice)
            thematic_advice[theme] = theme_advice
        report['strategies']['thematic'] = thematic_advice
        
        return report