#!/usr/bin/env python3
# 完整交易建議系統 - 單一整合版本
# 包含: 繁體中文 | 買賣點 | 獲利目標 | 停損點 | 正確日期

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

from complete_trading_advisor import CompleteTradingAdvisor
from integrated_report_generator import IntegratedReportGenerator
from notifier import DiscordNotifier
from trading_day_checker import TradingDayChecker

def main():
    """主執行函數"""
    print("=" * 70)
    print("🎯 完整交易建議系統 - 單一整合版本")
    print("包含: 繁體中文 | 買賣點 | 獲利目標 | 停損點 | 正確日期")
    print("=" * 70)
    
    # 檢查是否為交易日
    checker = TradingDayChecker()
    today_date = datetime.now().date()
    if not checker.is_trading_day(today_date):
        print(f"\n❌ 今日 ({today_date}) 非台灣股市交易日")
        print("系統將跳過今日分析。")
        print("=" * 70)
        
        # 發送非交易日通知
        notifier = DiscordNotifier()
        notifier.send_non_trading_day_notification(str(today_date))
        
        return True
    
    try:
        # 1. 收集股票數據
        print("\n[1/3] 收集股票數據...")
        from four_strategy_analyzer import FourStrategyAnalyzer
        analyzer = FourStrategyAnalyzer()
        analysis_result = analyzer.analyze_all_strategies()
        
        # 2. 生成完整交易建議
        print("\n[2/3] 生成完整交易建議...")
        advisor = CompleteTradingAdvisor()
        trading_report = advisor.generate_complete_report(analysis_result)
        
        # 3. 生成整合HTML報告
        print("\n[3/3] 生成整合HTML報告...")
        generator = IntegratedReportGenerator()
        html_path = generator.save_report(trading_report)
        
        # 4. 發送Discord通知
        print("\n[4/4] 發送Discord通知...")
        notifier = DiscordNotifier()
        notification_sent = notifier.send_daily_report(trading_report, html_path)
        
        print("\n" + "=" * 70)
        print("✅ 完整交易建議系統執行成功！")
        print(f"   報告網址: http://aiothome.top/investment/complete_trading_report_{trading_report['date']}.html")
        print(f"   生成時間: {trading_report['report_time']}")
        print(f"   技術面策略: {len(trading_report['strategies']['technical'])}支股票")
        print(f"   基本面策略: {len(trading_report['strategies']['fundamental'])}支股票")
        print(f"   混合策略: {len(trading_report['strategies']['hybrid'])}支股票")
        print(f"   主題策略: 高股息({len(trading_report['strategies']['thematic'].get('high_dividend', []))}) + 成長股({len(trading_report['strategies']['thematic'].get('growth_stocks', []))})")
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
        notifier.send_error_notification(f"完整交易建議系統執行失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)