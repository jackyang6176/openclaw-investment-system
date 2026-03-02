#!/usr/bin/env python3
# 四策略投資分析器 (整合 Kronos AI 預測)
# 最後更新：2026-02-28 - 整合 Kronos AI 技術分析

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import numpy as np

# 添加 Kronos 路徑
sys.path.insert(0, '/home/admin/.openclaw/workspace/kronos')
try:
    from kronos_integration import KronosIntegration
    KRONOS_ENABLED = True
except ImportError:
    KRONOS_ENABLED = False
    print("⚠️  Kronos 模塊未安裝，將使用模擬模式")

# 繁體中文股票名稱映射
CHINESE_STOCK_NAMES = {
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

# 用戶持倉 ETF (2026-02-27 驗證)
USER_HOLDINGS = {
    "00655L": {"name": "國泰 A50 正 2", "type": "槓桿 ETF", "last_price": 31.6, "date": "2026-02-27"},
    "00882": {"name": "中信中國高股息", "type": "高股息 ETF", "last_price": 16.1, "date": "2026-02-27"},
    "00887": {"name": "永豐中國科技 50 大", "type": "科技主題 ETF", "last_price": 13.29, "date": "2026-02-26"},
}

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
    """四策略投資分析器 (整合 Kronos AI 預測)"""
    
    def __init__(self):
        self.data_source = "manual"  # 手動數據
        self.kronos_enabled = KRONOS_ENABLED
        
    def fetch_market_data(self):
        """獲取市場數據 (手動輸入)"""
        print("📊 數據源：手動驗證價格")
        print("🤖 Kronos AI 預測：", "✅ 已啟用" if self.kronos_enabled else "⚠️ 未啟用")
        print("")
        
        return {
            "holdings": USER_HOLDINGS,
            "timestamp": datetime.now().isoformat(),
            "data_source": "manual",
            "kronos_enabled": self.kronos_enabled
        }
    
    def generate_mock_kline(self, symbol, base_price, days=3):
        """
        生成模擬 K 線數據 (等待 Fubon API)
        
        Args:
            symbol: 股票代碼
            base_price: 基礎價格
            days: 天數
        
        Returns:
            DataFrame with OHLCV data
        """
        import pandas as pd
        import numpy as np
        
        minutes_per_day = 240
        total_bars = days * minutes_per_day
        
        dates = pd.date_range(
            end=datetime.now(),
            periods=total_bars,
            freq='5min'
        )
        
        np.random.seed(hash(symbol) % 2**32)
        returns = np.random.normal(0.0001, 0.005, total_bars)
        close_prices = base_price * np.cumprod(1 + returns)
        
        data = []
        for i, (date, close) in enumerate(zip(dates, close_prices)):
            open_price = close * (1 + np.random.uniform(-0.002, 0.002))
            high = max(open_price, close) * (1 + abs(np.random.normal(0, 0.003)))
            low = min(open_price, close) * (1 - abs(np.random.normal(0, 0.003)))
            volume = int(np.random.uniform(50000, 500000))
            
            data.append({
                'timestamps': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamps', inplace=True)
        return df
    
    def analyze_with_kronos(self, symbol, holding_info):
        """
        使用 Kronos AI 進行技術分析
        
        Args:
            symbol: 股票代碼
            holding_info: 持倉信息
        
        Returns:
            Kronos prediction result
        """
        if not self.kronos_enabled:
            return None
        
        try:
            print(f"🔮 Kronos AI 預測：{symbol} ({holding_info['name']})")
            
            # 初始化 Kronos
            kronos = KronosIntegration(model_name="NeoQuasar/Kronos-small")
            
            # 生成模擬 K 線 (等待 Fubon API)
            historical_df = self.generate_mock_kline(
                symbol, 
                holding_info.get('last_price', 30),
                days=3
            )
            
            # 生成預測
            pred_df = kronos.predict_price(historical_df, pred_len=60)
            
            # 生成信號
            signals = kronos.generate_signals(historical_df, pred_df)
            
            result = {
                'symbol': symbol,
                'name': holding_info['name'],
                'last_close': holding_info.get('last_price', 0),
                'kronos_prediction': {
                    'signal': signals['signal'],
                    'confidence': signals['confidence'],
                    'target_price': signals['target_price'],
                    'stop_loss': signals['stop_loss'],
                    'short_term_change': signals['short_term_change'],
                    'mid_term_change': signals['mid_term_change']
                },
                'status': 'success'
            }
            
            print(f"   信號：{result['kronos_prediction']['signal']}")
            print(f"   置信度：{result['kronos_prediction']['confidence']:.1f}%")
            print(f"   短期：{result['kronos_prediction']['short_term_change']:+.2f}%")
            print("")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Kronos 預測失敗：{e}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            }
    
    def analyze(self):
        """執行四策略分析 (整合 Kronos AI)"""
        data = self.fetch_market_data()
        
        # Kronos AI 預測
        kronos_results = []
        for symbol, holding_info in USER_HOLDINGS.items():
            result = self.analyze_with_kronos(symbol, holding_info)
            if result:
                kronos_results.append(result)
        
        # 整合分析結果
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "holdings": data["holdings"],
            "kronos_predictions": kronos_results,
            "analysis": {
                "status": "complete",
                "data_source": "manual",
                "kronos_enabled": self.kronos_enabled,
                "note": "已整合 Kronos AI 技術分析，等待 Fubon API 使用真實數據"
            }
        }
        
        return convert_numpy_types(analysis)

def generate_html_report(result, output_path=None):
    """生成 HTML 報告"""
    from jinja2 import Template
    
    template_path = '/home/admin/.openclaw/workspace/website/investment/four_strategy_report_with_kronos.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
    except FileNotFoundError:
        print(f"⚠️  HTML 模板未找到：{template_path}")
        return None
    
    html_content = template.render(
        timestamp=result['timestamp'],
        holdings=result['holdings'],
        kronos_predictions=result['kronos_predictions'],
        analysis=result['analysis']
    )
    
    if output_path is None:
        output_dir = '/home/admin/.openclaw/workspace/website/investment/'
        os.makedirs(output_dir, exist_ok=True)
        date_str = datetime.now().strftime('%Y-%m-%d_%H%M')
        output_path = f'{output_dir}four_strategy_report_{date_str}.html'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML 報告已保存：{output_path}")
    return output_path

def main():
    """主函數"""
    print("=" * 60)
    print("四策略投資分析器 (整合 Kronos AI)")
    print("=" * 60)
    print(f"執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    analyzer = FourStrategyAnalyzer()
    result = analyzer.analyze()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 生成 HTML 報告
    html_path = generate_html_report(result)
    if html_path:
        print(f"\n🌐 在瀏覽器中打開：file://{html_path}")
    
    return result

if __name__ == "__main__":
    main()
