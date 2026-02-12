#!/usr/bin/env python3
# 四策略投資分析系統 - 整合版（包含完整交易建議）

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

from four_strategy_analyzer import FourStrategyAnalyzer
from four_strategy_report_generator_integrated import FourStrategyReportGeneratorIntegrated
from notifier import DiscordNotifier
from trading_day_checker import TradingDayChecker

def main():
    """主執行函數"""
    print("=" * 70)
    print("OpenClaw 四策略投資分析系統 - 整合版")
    print("策略分區: 技術面 | 基本面 | 混合策略 | 特定主題")
    print("=" * 70)
    
    # 檢查是否為交易日
    checker = TradingDayChecker()
    if not checker.is_trading_day(datetime.now().strftime('%Y-%m-%d')):
        print(f"\n❌ 今日 ({datetime.now().strftime('%Y-%m-%d')}) 非台灣股市交易日")
        print("系統將跳過今日分析。")
        print("=" * 70)
        
        # 發送非交易日通知
        notifier = DiscordNotifier()
        notifier.send_non_trading_day_notification(datetime.now().strftime('%Y-%m-%d'))
        
        return True
    
    try:
        # 1. 執行四策略分析
        print("\n[1/4] 執行四策略投資分析...")
        analyzer = FourStrategyAnalyzer()
        analysis_result = analyzer.analyze_all_strategies()
        
        # 2. 生成整合HTML報告（包含交易建議）
        print("\n[2/4] 生成四策略HTML報告（含完整交易建議）...")
        generator = FourStrategyReportGeneratorIntegrated()
        html_path = generator.save_report(analysis_result)
        
        # 3. 發送Discord通知
        print("\n[3/4] 發送Discord通知...")
        notifier = DiscordNotifier()
        notification_sent = notifier.send_daily_report(analysis_result, html_path)
        
        # 4. 保存JSON報告
        json_path = os.path.join("/home/admin/.openclaw/workspace/investment/reports", f"four_strategy_report_{analysis_result['date']}.json")
        import json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ 四策略投資分析完成！")
        print(f"   報告網址: http://aiothome.top/investment/four_strategy_report_{analysis_result['date']}.html")
        print(f"   生成時間: {analysis_result['report_time']}")
        print(f"   分析股票: {analysis_result['total_stocks_analyzed']}支")
        print(f"   技術面策略: {len(analysis_result['technical_strategy'])}支推薦")
        print(f"   基本面策略: {len(analysis_result['fundamental_strategy'])}支推薦")
        print(f"   混合策略: {len(analysis_result['hybrid_strategy'])}支推薦")
        print(f"   主題策略: 高股息({len(analysis_result['thematic_strategy']['high_dividend'])}) + 成長股({len(analysis_result['thematic_strategy']['growth_stocks'])}) + 價值股({len(analysis_result['thematic_strategy']['value_stocks'])})")
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
        
        # 發送錯誤通知
        notifier = DiscordNotifier()
        notifier.send_error_notification(f"四策略投資分析系統執行失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)