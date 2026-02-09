#!/usr/bin/env python3
# 通知模組 - Discord通知

import requests
import json
from datetime import datetime
from config import CONFIG, get_today_str

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = CONFIG.get('discord_webhook', '')
        self.channel_id = CONFIG.get('discord_channel_id', '')
    
    def send_discord_message(self, message, embed=None):
        """發送Discord訊息"""
        if not self.webhook_url:
            print("警告: Discord webhook未配置，跳過通知")
            return False
        
        payload = {
            'content': message,
            'username': 'OpenClaw投資助手',
            'avatar_url': 'https://cdn-icons-png.flaticon.com/512/4712/4712035.png'
        }
        
        if embed:
            payload['embeds'] = [embed]
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 204]:
                print(f"Discord通知發送成功")
                return True
            else:
                print(f"Discord通知發送失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Discord通知錯誤: {str(e)}")
            return False
    
    def create_report_embed(self, analysis_result, report_url):
        """創建Discord嵌入訊息"""
        today = get_today_str()
        
        # 獲取市場指數
        indices = analysis_result.get('market_summary', {})
        market_summary = ""
        for key, index in indices.items():
            change_sign = "+" if index.get('change', 0) >= 0 else ""
            market_summary += f"**{index.get('name', key)}**: {index.get('value', 0):,.2f} ({change_sign}{index.get('change_percent', 0):.2f}%)\n"
        
        # 獲取Top 3推薦
        recommendations = analysis_result.get('top_10_recommendations', [])[:3]
        top_recommendations = ""
        for i, item in enumerate(recommendations, 1):
            item_type = "📈" if 'dividend_yield' in item else "🏦"
            change_sign = "+" if item.get('change', 0) >= 0 else ""
            top_recommendations += f"{i}. **{item.get('code', '')}** {item.get('name', '')} {item_type}\n"
            top_recommendations += f"   價格: {item.get('price', 0):.2f} ({change_sign}{item.get('change_percent', 0):.2f}%) | 評分: {item.get('score', 0):.1f}\n"
        
        embed = {
            'title': f'📊 每日投資報告 - {today}',
            'description': '今日最值得關注的投資標的已更新！',
            'color': 0x4CA1AF,
            'fields': [
                {
                    'name': '📈 市場指數',
                    'value': market_summary or '暫無數據',
                    'inline': False
                },
                {
                    'name': '🏆 Top 3推薦',
                    'value': top_recommendations or '暫無推薦',
                    'inline': False
                },
                {
                    'name': '📊 分析統計',
                    'value': f"分析股票: {analysis_result.get('total_analyzed', {}).get('stocks', 0)}\n分析ETF: {analysis_result.get('total_analyzed', {}).get('etfs', 0)}\n推薦標的: {len(analysis_result.get('top_10_recommendations', []))}",
                    'inline': True
                }
            ],
            'footer': {
                'text': 'OpenClaw投資分析系統 • 自動生成'
            },
            'timestamp': datetime.now().isoformat(),
            'url': report_url
        }
        
        return embed
    
    def send_daily_report(self, analysis_result, html_path):
        """發送每日報告通知"""
        today = get_today_str()
        report_url = f"http://aiothome.top/investment/report_{today}.html"
        
        # 創建嵌入訊息
        embed = self.create_report_embed(analysis_result, report_url)
        
        # 發送訊息
        message = f"⏰ **台灣時間早上8點投資報告**\n今日推薦已更新！點擊查看完整報告：{report_url}"
        
        return self.send_discord_message(message, embed)
    
    def send_error_notification(self, error_message):
        """發送錯誤通知"""
        embed = {
            'title': '❌ 投資分析系統錯誤',
            'description': error_message,
            'color': 0xFF0000,
            'timestamp': datetime.now().isoformat()
        }
        
        message = "⚠️ 投資分析系統執行失敗，請檢查系統狀態！"
        return self.send_discord_message(message, embed)
    
    def send_non_trading_day_notification(self, date_str):
        """發送非交易日通知"""
        embed = {
            'title': '📅 非交易日通知',
            'description': f'{date_str} 為台灣股市非交易日，今日無投資分析報告。',
            'color': 0x64748b,  # 灰色
            'timestamp': datetime.now().isoformat(),
            'footer': {
                'text': 'OpenClaw投資分析系統'
            }
        }
        
        message = f"📅 **非交易日通知**\n今日 ({date_str}) 為台灣股市非交易日，無投資分析報告。"
        return self.send_discord_message(message, embed)

if __name__ == "__main__":
    # 測試通知
    notifier = DiscordNotifier()
    
    # 測試訊息
    test_result = {
        'market_summary': {
            'TWSE': {'name': '台灣加權指數', 'value': 17500.50, 'change': 50.25, 'change_percent': 0.29},
            'A50': {'name': '富時中國A50', 'value': 12500.75, 'change': -25.50, 'change_percent': -0.20}
        },
        'top_10_recommendations': [
            {'code': '2330', 'name': '台積電', 'price': 580.0, 'change': 5.0, 'change_percent': 0.87, 'score': 85.5},
            {'code': '006208', 'name': '元大台灣50', 'price': 135.25, 'change': 0.75, 'change_percent': 0.56, 'score': 82.3},
            {'code': '00636', 'name': '國泰中國A50', 'price': 42.80, 'change': -0.20, 'change_percent': -0.47, 'score': 78.9}
        ],
        'total_analyzed': {'stocks': 50, 'etfs': 15}
    }
    
    success = notifier.send_daily_report(test_result, "http://aiothome.top/investment/report_test.html")
    print(f"測試通知發送: {'成功' if success else '失敗'}")