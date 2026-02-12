#!/usr/bin/env python3
# 交易建議計算模組 - 為四策略系統提供完整買賣點

class TradingAdvisor:
    """交易建議計算器"""
    
    def __init__(self):
        pass
    
    def calculate_technical_targets(self, stock_data):
        """計算技術面交易建議"""
        price = stock_data['price']
        ma20 = stock_data['ma20']
        rsi = stock_data['rsi']
        
        # 買點計算
        if price > ma20:
            buy_zone = (ma20 * 0.98, ma20 * 0.99)  # 接近均線時買入
        else:
            buy_zone = (price * 0.95, price * 0.97)  # 回檔時買入
        
        # 獲利目標
        if rsi < 50:  # 低風險
            targets = [
                price * 1.05,  # +5%
                price * 1.10,  # +10%
                price * 1.15   # +15%
            ]
        elif rsi < 65:  # 中等風險
            targets = [
                price * 1.04,
                price * 1.08,
                price * 1.12
            ]
        else:  # 高風險 (接近超買)
            targets = [
                price * 1.03,
                price * 1.06,
                price * 1.09
            ]
        
        # 停損點
        if price > ma20:
            stop_loss = ma20 * 0.95  # 均線下方5%
        else:
            stop_loss = price * 0.92  # 現價下方8%
        
        return {
            'buy_zone': buy_zone,
            'targets': targets,
            'stop_loss': stop_loss,
            'risk_level': 'low' if rsi < 50 else 'medium' if rsi < 65 else 'high'
        }
    
    def calculate_fundamental_targets(self, stock_data):
        """計算基本面交易建議"""
        price = stock_data['price']
        pe_ratio = stock_data['pe_ratio']
        dividend_yield = stock_data['dividend_yield']
        roe = stock_data['roe']
        
        # 基於本益比的買點
        if pe_ratio < 12:  # 低估
            buy_zone = (price * 0.95, price * 0.98)
        elif pe_ratio < 18:  # 合理
            buy_zone = (price * 0.97, price * 0.99)
        else:  # 高估
            buy_zone = (price * 0.90, price * 0.95)
        
        # 基於股息和ROE的獲利目標
        base_return = dividend_yield + roe * 0.3
        if base_return > 15:  # 高回報
            targets = [
                price * 1.06,
                price * 1.12,
                price * 1.18
            ]
        elif base_return > 10:  # 中等回報
            targets = [
                price * 1.05,
                price * 1.10,
                price * 1.15
            ]
        else:  # 低回報
            targets = [
                price * 1.04,
                price * 1.08,
                price * 1.12
            ]
        
        # 停損點基於基本面
        if pe_ratio < 15 and dividend_yield > 3:
            stop_loss = price * 0.88  # 12% 停損
        else:
            stop_loss = price * 0.85  # 15% 停損
        
        return {
            'buy_zone': buy_zone,
            'targets': targets,
            'stop_loss': stop_loss,
            'expected_return': base_return
        }
    
    def calculate_hybrid_targets(self, stock_data):
        """計算混合策略交易建議"""
        tech_targets = self.calculate_technical_targets(stock_data)
        fund_targets = self.calculate_fundamental_targets(stock_data)
        
        # 綜合兩者
        buy_low = max(tech_targets['buy_zone'][0], fund_targets['buy_zone'][0])
        buy_high = min(tech_targets['buy_zone'][1], fund_targets['buy_zone'][1])
        
        # 取較保守的獲利目標
        targets = [
            min(tech_targets['targets'][0], fund_targets['targets'][0]),
            min(tech_targets['targets'][1], fund_targets['targets'][1]),
            min(tech_targets['targets'][2], fund_targets['targets'][2])
        ]
        
        # 取較嚴格的停損
        stop_loss = max(tech_targets['stop_loss'], fund_targets['stop_loss'])
        
        return {
            'buy_zone': (buy_low, buy_high),
            'targets': targets,
            'stop_loss': stop_loss,
            'strategy': 'hybrid'
        }
    
    def calculate_thematic_targets(self, stock_data, strategy_type):
        """計算特定主題策略交易建議"""
        if strategy_type == 'high_dividend':
            # 高股息策略 - 重視穩定性和股息保護
            price = stock_data['price']
            dividend_yield = stock_data['dividend_yield']
            
            buy_zone = (price * 0.96, price * 0.98)
            targets = [
                price * 1.04,
                price * 1.08,
                price * 1.12
            ]
            stop_loss = price * 0.88  # 較寬鬆停損，因股息提供保護
            
        elif strategy_type == 'growth':
            # 成長股策略 - 重視成長潛力
            price = stock_data['price']
            roe = stock_data['roe']
            
            buy_zone = (price * 0.94, price * 0.97)
            targets = [
                price * 1.08,
                price * 1.16,
                price * 1.24
            ]
            stop_loss = price * 0.82  # 較嚴格停損，因波動大
            
        else:  # value
            # 價值股策略 - 重視安全邊際
            price = stock_data['price']
            pe_ratio = stock_data['pe_ratio']
            
            buy_zone = (price * 0.92, price * 0.96)
            targets = [
                price * 1.06,
                price * 1.12,
                price * 1.18
            ]
            stop_loss = price * 0.85
            
        return {
            'buy_zone': buy_zone,
            'targets': targets,
            'stop_loss': stop_loss,
            'strategy_type': strategy_type
        }
    
    def format_trading_advice(self, stock_data, strategy, strategy_type=None):
        """格式化交易建議為人類可讀格式"""
        if strategy == 'technical':
            advice = self.calculate_technical_targets(stock_data)
        elif strategy == 'fundamental':
            advice = self.calculate_fundamental_targets(stock_data)
        elif strategy == 'hybrid':
            advice = self.calculate_hybrid_targets(stock_data)
        else:  # thematic
            advice = self.calculate_thematic_targets(stock_data, strategy_type)
        
        # 格式化數字
        buy_min = round(advice['buy_zone'][0], 2)
        buy_max = round(advice['buy_zone'][1], 2)
        target1 = round(advice['targets'][0], 2)
        target2 = round(advice['targets'][1], 2)
        target3 = round(advice['targets'][2], 2)
        stop_loss = round(advice['stop_loss'], 2)
        
        return {
            'buy_point': f"{buy_min} - {buy_max}",
            'target1': target1,
            'target2': target2,
            'target3': target3,
            'stop_loss': stop_loss,
            'profit_target1_pct': round((target1 / stock_data['price'] - 1) * 100, 1),
            'profit_target2_pct': round((target2 / stock_data['price'] - 1) * 100, 1),
            'profit_target3_pct': round((target3 / stock_data['price'] - 1) * 100, 1),
            'stop_loss_pct': round((stop_loss / stock_data['price'] - 1) * 100, 1)
        }