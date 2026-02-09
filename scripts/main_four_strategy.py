#!/usr/bin/env python3
# 四策略投資分析主執行腳本

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from four_strategy_analyzer import FourStrategyAnalyzer
from four_strategy_report_generator import FourStrategyReportGeneratorFixed as FourStrategyReportGenerator
from notifier import DiscordNotifier
from trading_day_checker import TradingDayChecker
from datetime import datetime
import json

def main():
    """主執行函數"""
    print("=" * 70)
    print("OpenClaw 四策略投資分析系統 - 2026-02-09")
    print("策略分區: 技術面 | 基本面 | 混合策略 | 特定主題")
    print("=" * 70)
    
    # 檢查是否為交易日
    checker = TradingDayChecker()
    if not checker.is_trading_day(datetime.today().date()):
        print(f"\n❌ 今日非台灣股市交易日")
        print("系統將跳過今日分析。")
        return True
    
    try:
        # 1. 執行四策略投資分析
        print("\n[1/4] 執行四策略投資分析...")
        analyzer = FourStrategyAnalyzer()
        analysis_result = analyzer.analyze_all_strategies()
        
        # 2. 生成HTML報告
        print("\n[2/4] 生成四策略HTML報告...")
        generator = FourStrategyReportGenerator()
        html_path = generator.save_report(analysis_result)
        
        # 3. 發送Discord通知
        print("\n[3/4] 發送Discord通知...")
        notifier = DiscordNotifier()
        notification_sent = notifier.send_daily_report(analysis_result, html_path)
        
        # 4. 保存JSON報告
        json_path = f"/home/admin/.openclaw/workspace/investment/reports/four_strategy_report_{analysis_result['date']}.json"
        # 轉換 numpy 數據類型為 Python 原生類型
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            else:
                return obj
        
        analysis_result_clean = convert_numpy_types(analysis_result)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result_clean, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ 四策略投資分析完成！")
        print(f"   報告網址: http://aiothome.top/investment/four_strategy_report_{analysis_result['date']}.html")
        print(f"   生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   分析股票: {analysis_result['total_stocks_analyzed']}支")
        print(f"   技術面策略: {len(analysis_result['technical_strategy'])}支推薦")
        print(f"   基本面策略: {len(analysis_result['fundamental_strategy'])}支推薦")
        print(f"   混合策略: {len(analysis_result['hybrid_strategy'])}支推薦")
        thematic = analysis_result['thematic_strategy']
        print(f"   主題策略: 高股息({len(thematic['high_dividend'])}) + 成長股({len(thematic['growth_stocks'])}) + 價值股({len(thematic['value_stocks'])})")
        
        if notification_sent:
            print("   Discord通知: 已發送 ✓")
        else:
            print("   Discord通知: 未發送 (請檢查配置)")
        
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)