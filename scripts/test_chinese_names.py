#!/usr/bin/env python3
# 測試繁體中文股票名稱

import sys
import os
sys.path.append(os.path.dirname(__file__))

from four_strategy_analyzer import FourStrategyAnalyzer

def test_chinese_names():
    """測試繁體中文股票名稱"""
    print("📊 執行四策略分析...")
    analyzer = FourStrategyAnalyzer()
    results = analyzer.analyze_all_strategies()
    
    # 測試用例
    test_cases = {
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
    
    all_passed = True
    
    # 檢查所有策略中的股票名稱
    strategies = [
        ('技術面', results['technical_strategy']),
        ('基本面', results['fundamental_strategy']),
        ('混合策略', results['hybrid_strategy']),
        ('高股息', results['thematic_strategy']['high_dividend']),
        ('成長股', results['thematic_strategy']['growth_stocks']),
        ('價值股', results['thematic_strategy']['value_stocks'])
    ]
    
    for strategy_name, stocks in strategies:
        if not stocks:
            continue
            
        print(f"\n🔍 {strategy_name} 策略:")
        for stock in stocks:
            symbol = stock['symbol']
            actual_name = stock['name']
            expected_name = test_cases.get(symbol, f"未知-{symbol}")
            
            if actual_name == expected_name:
                print(f"  ✅ {symbol}: {actual_name}")
            else:
                print(f"  ❌ {symbol}: 期望 '{expected_name}', 實際 '{actual_name}'")
                all_passed = False
    
    if all_passed:
        print("\n🎉 所有股票名稱測試通過！")
        return True
    else:
        print("\n❌ 部分股票名稱測試失敗！")
        return False

if __name__ == "__main__":
    success = test_chinese_names()
    sys.exit(0 if success else 1)