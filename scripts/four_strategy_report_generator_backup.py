#!/usr/bin/env python3
# 四策略投資報告生成器 (完全修正版 - 解決繁體中文和時間顯示問題)

import json
import os
from datetime import datetime

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

class FourStrategyReportGenerator:
    """四策略投資報告生成器 (完全修正版)"""
    
    def __init__(self, report_time=None):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.report_time = report_time or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_chinese_name(self, symbol, english_name):
        """獲取繁體中文股票名稱"""
        if symbol in CHINESE_STOCK_NAMES:
            return CHINESE_STOCK_NAMES[symbol]
        # 如果沒有映射，嘗試從英文名稱提取
        if 'Semiconductor' in english_name:
            return '台積電'
        elif 'Hon Hai' in english_name:
            return '鴻海'
        elif 'MediaTek' in english_name:
            return '聯發科'
        elif 'Cathay' in english_name:
            return '國泰金'
        elif 'Fubon' in english_name:
            return '富邦金'
        else:
            return english_name
    
    def generate_html(self, analysis_result):
        """生成HTML報告"""
        
        # 提取各策略結果並轉換為繁體中文
        technical_stocks = []
        for stock in analysis_result.get('technical_strategy', []):
            stock_copy = stock.copy()
            stock_copy['name'] = self.get_chinese_name(stock['symbol'], stock['name'])
            technical_stocks.append(stock_copy)
            
        fundamental_stocks = []
        for stock in analysis_result.get('fundamental_strategy', []):
            stock_copy = stock.copy()
            stock_copy['name'] = self.get_chinese_name(stock['symbol'], stock['name'])
            fundamental_stocks.append(stock_copy)
            
        hybrid_stocks = []
        for stock in analysis_result.get('hybrid_strategy', []):
            stock_copy = stock.copy()
            stock_copy['name'] = self.get_chinese_name(stock['symbol'], stock['name'])
            hybrid_stocks.append(stock_copy)
            
        thematic_results = analysis_result.get('thematic_strategy', {})
        high_dividend = []
        for stock in thematic_results.get('high_dividend', []):
            stock_copy = stock.copy()
            stock_copy['name'] = self.get_chinese_name(stock['symbol'], stock['name'])
            high_dividend.append(stock_copy)
            
        growth_stocks = []
        for stock in thematic_results.get('growth_stocks', []):
            stock_copy = stock.copy()
            stock_copy['name'] = self.get_chinese_name(stock['symbol'], stock['name'])
            growth_stocks.append(stock_copy)
            
        value_stocks = []
        for stock in thematic_results.get('value_stocks', []):
            stock_copy = stock.copy()
            stock_copy['name'] = self.get_chinese_name(stock['symbol'], stock['name'])
            value_stocks.append(stock_copy)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>四策略投資分析系統 - {self.today}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft JhengHei', sans-serif;
            background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.8rem;
            margin-bottom: 10px;
            font-weight: 800;
        }}
        
        .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .date-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.1rem;
            font-weight: 600;
        }}
        
        .strategies-container {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 30px;
            padding: 30px;
        }}
        
        .strategy-section {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        
        .strategy-header {{
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
        }}
        
        .strategy-title {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .strategy-description {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .stock-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .stock-table th {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95rem;
        }}
        
        .stock-table td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .stock-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .stock-table tr:hover {{
            background: #f8fafc;
        }}
        
        .change-positive {{
            color: #ef4444;
            font-weight: bold;
        }}
        
        .change-negative {{
            color: #10b981;
            font-weight: bold;
        }}
        
        .score-cell {{
            background: #dbeafe;
            color: #1d4ed8;
            font-weight: bold;
            text-align: center;
            border-radius: 5px;
            padding: 5px;
        }}
        
        .thematic-subsection {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
        }}
        
        .thematic-title {{
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 15px;
        }}
        
        footer {{
            background: #f1f5f9;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }}
        
        .update-time {{
            margin-top: 10px;
            font-size: 0.9rem;
            color: #64748b;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                border-radius: 10px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .strategy-section {{
                padding: 15px;
            }}
            
            .stock-table {{
                display: block;
                overflow-x: auto;
            }}
            
            .stock-table th,
            .stock-table td {{
                padding: 10px 8px;
                font-size: 0.85rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 四策略投資分析系統</h1>
            <div class="subtitle">AI智能篩選 · 多維度投資策略</div>
            <div class="date-badge">
                <i class="fas fa-calendar-alt"></i> {self.today} 報告
            </div>
        </header>
        
        <div class="strategies-container">
            
            <!-- 技術面主導策略 -->
            <div class="strategy-section">
                <div class="strategy-header" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);">
                    <div class="strategy-title">📈 技術面主導策略</div>
                    <div class="strategy-description">基於價格趨勢、成交量和技術指標的短期交易策略</div>
                </div>
                
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>股票</th>
                            <th>價格</th>
                            <th>漲跌幅</th>
                            <th>20日均線</th>
                            <th>RSI</th>
                            <th>成交量</th>
                            <th>策略分數</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 技術面股票列表
        for i, stock in enumerate(technical_stocks, 1):
            change_class = "change-positive" if stock.get('change_percent', 0) >= 0 else "change-negative"
            change_sign = "+" if stock.get('change_percent', 0) >= 0 else ""
            html += f"""
                        <tr>
                            <td><strong>{i}</strong></td>
                            <td><strong>{stock['name']}</strong><br><small>{stock['symbol']}</small></td>
                            <td>{stock['price']:.2f}</td>
                            <td class="{change_class}">{change_sign}{stock.get('change_percent', 0):.2f}%</td>
                            <td>{stock['ma20']:.2f}</td>
                            <td>{stock['rsi']:.1f}</td>
                            <td>{int(stock['volume']):,}</td>
                            <td class="score-cell">{stock.get('strategy_score', 0)}</td>
                        </tr>
"""
        
        if not technical_stocks:
            html += """
                        <tr>
                            <td colspan="8" style="text-align: center; color: #64748b;">今日無符合條件的股票</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <!-- 基本面主導策略 -->
            <div class="strategy-section">
                <div class="strategy-header" style="background: linear-gradient(135deg, #4ecdc4 0%, #556270 100%);">
                    <div class="strategy-title">📊 基本面主導策略</div>
                    <div class="strategy-description">基於財務指標、估值和股利的長期價值投資策略</div>
                </div>
                
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>股票</th>
                            <th>價格</th>
                            <th>本益比</th>
                            <th>股價淨值比</th>
                            <th>股利殖利率</th>
                            <th>ROE</th>
                            <th>市值</th>
                            <th>策略分數</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 基本面股票列表
        for i, stock in enumerate(fundamental_stocks, 1):
            market_cap_billion = stock['market_cap'] / 1_000_000_000 if stock['market_cap'] else 0
            html += f"""
                        <tr>
                            <td><strong>{i}</strong></td>
                            <td><strong>{stock['name']}</strong><br><small>{stock['symbol']}</small></td>
                            <td>{stock['price']:.2f}</td>
                            <td>{stock['pe_ratio']:.1f}</td>
                            <td>{stock['pb_ratio']:.2f}</td>
                            <td>{stock['dividend_yield']:.1f}%</td>
                            <td>{stock['roe']:.1f}%</td>
                            <td>{market_cap_billion:.1f}B</td>
                            <td class="score-cell">{stock.get('strategy_score', 0)}</td>
                        </tr>
"""
        
        if not fundamental_stocks:
            html += """
                        <tr>
                            <td colspan="9" style="text-align: center; color: #64748b;">今日無符合條件的股票</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <!-- 混合策略 -->
            <div class="strategy-section">
                <div class="strategy-header" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                    <div class="strategy-title">🔄 混合策略</div>
                    <div class="strategy-description">結合技術面趨勢與基本面價值的平衡投資策略</div>
                </div>
                
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>股票</th>
                            <th>價格</th>
                            <th>漲跌幅</th>
                            <th>本益比</th>
                            <th>20日均線</th>
                            <th>ROE</th>
                            <th>股利殖利率</th>
                            <th>策略分數</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 混合策略股票列表
        for i, stock in enumerate(hybrid_stocks, 1):
            change_class = "change-positive" if stock.get('change_percent', 0) >= 0 else "change-negative"
            change_sign = "+" if stock.get('change_percent', 0) >= 0 else ""
            html += f"""
                        <tr>
                            <td><strong>{i}</strong></td>
                            <td><strong>{stock['name']}</strong><br><small>{stock['symbol']}</small></td>
                            <td>{stock['price']:.2f}</td>
                            <td class="{change_class}">{change_sign}{stock.get('change_percent', 0):.2f}%</td>
                            <td>{stock['pe_ratio']:.1f}</td>
                            <td>{stock['ma20']:.2f}</td>
                            <td>{stock['roe']:.1f}%</td>
                            <td>{stock['dividend_yield']:.1f}%</td>
                            <td class="score-cell">{stock.get('strategy_score', 0)}</td>
                        </tr>
"""
        
        if not hybrid_stocks:
            html += """
                        <tr>
                            <td colspan="9" style="text-align: center; color: #64748b;">今日無符合條件的股票</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <!-- 特定主題策略 -->
            <div class="strategy-section">
                <div class="strategy-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="strategy-title">🎯 特定主題策略</div>
                    <div class="strategy-description">針對不同投資目標的專屬策略組合</div>
                </div>
"""
        
        # 高股息策略
        html += """
                <div class="thematic-subsection">
                    <div class="thematic-title" style="color: #ff6b6b;">
                        💰 高股息策略
                    </div>
                    <table class="stock-table">
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>股票</th>
                                <th>價格</th>
                                <th>股利殖利率</th>
                                <th>本益比</th>
                                <th>策略分數</th>
                            </tr>
                        </thead>
                        <tbody>
"""
        
        for i, stock in enumerate(high_dividend, 1):
            html += f"""
                            <tr>
                                <td><strong>{i}</strong></td>
                                <td><strong>{stock['name']}</strong><br><small>{stock['symbol']}</small></td>
                                <td>{stock['price']:.2f}</td>
                                <td>{stock['dividend_yield']:.1f}%</td>
                                <td>{stock['pe_ratio']:.1f}</td>
                                <td class="score-cell">{stock.get('strategy_score', 0)}</td>
                            </tr>
"""
        
        if not high_dividend:
            html += """
                            <tr>
                                <td colspan="6" style="text-align: center; color: #64748b;">今日無符合條件的高股息股票</td>
                            </tr>
"""
        
        html += """
                        </tbody>
                    </table>
                </div>
"""
        
        # 成長股策略
        html += """
                <div class="thematic-subsection">
                    <div class="thematic-title" style="color: #4ecdc4;">
                        📈 成長股策略
                    </div>
                    <table class="stock-table">
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>股票</th>
                                <th>價格</th>
                                <th>ROE</th>
                                <th>本益比</th>
                                <th>市值</th>
                                <th>策略分數</th>
                            </tr>
                        </thead>
                        <tbody>
"""
        
        for i, stock in enumerate(growth_stocks, 1):
            market_cap_billion = stock['market_cap'] / 1_000_000_000 if stock['market_cap'] else 0
            html += f"""
                            <tr>
                                <td><strong>{i}</strong></td>
                                <td><strong>{stock['name']}</strong><br><small>{stock['symbol']}</small></td>
                                <td>{stock['price']:.2f}</td>
                                <td>{stock['roe']:.1f}%</td>
                                <td>{stock['pe_ratio']:.1f}</td>
                                <td>{market_cap_billion:.1f}B</td>
                                <td class="score-cell">{stock.get('strategy_score', 0)}</td>
                            </tr>
"""
        
        if not growth_stocks:
            html += """
                            <tr>
                                <td colspan="7" style="text-align: center; color: #64748b;">今日無符合條件的成長股</td>
                            </tr>
"""
        
        html += """
                        </tbody>
                    </table>
                </div>
"""
        
        # 價值股策略
        html += """
                <div class="thematic-subsection">
                    <div class="thematic-title" style="color: #a8edea;">
                        🏦 價值股策略
                    </div>
                    <table class="stock-table">
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>股票</th>
                                <th>價格</th>
                                <th>本益比</th>
                                <th>股價淨值比</th>
                                <th>股利殖利率</th>
                                <th>策略分數</th>
                            </tr>
                        </thead>
                        <tbody>
"""
        
        for i, stock in enumerate(value_stocks, 1):
            html += f"""
                            <tr>
                                <td><strong>{i}</strong></td>
                                <td><strong>{stock['name']}</strong><br><small>{stock['symbol']}</small></td>
                                <td>{stock['price']:.2f}</td>
                                <td>{stock['pe_ratio']:.1f}</td>
                                <td>{stock['pb_ratio']:.2f}</td>
                                <td>{stock['dividend_yield']:.1f}%</td>
                                <td class="score-cell">{stock.get('strategy_score', 0)}</td>
                            </tr>
"""
        
        if not value_stocks:
            html += """
                            <tr>
                                <td colspan="7" style="text-align: center; color: #64748b;">今日無符合條件的價值股</td>
                            </tr>
"""
        
        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <footer>
            <p>OpenClaw 四策略投資分析系統 • AI智能篩選</p>
            <div class="update-time">
                最後更新: {self.report_time}
            </div>
            <p style="margin-top: 15px; font-size: 0.9rem;">
                <strong>免責聲明：</strong>本報告僅供參考，不構成投資建議。投資有風險，入市需謹慎。
            </p>
        </footer>
    </div>
</body>
</html>
"""
        
        # 修正時間顯示
        html = html.replace("{self.report_time}", self.report_time)
        html = html.replace("{self.today}", self.today)
        
        return html
    
    def save_report(self, analysis_result):
        """保存HTML報告"""
        html_content = self.generate_html(analysis_result)
        html_path = self.get_html_path()
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML報告已保存到: {html_path}")
        return html_path
    
    def get_html_path(self):
        """獲取HTML報告路徑"""
        return f"/home/admin/.openclaw/workspace/website/investment/four_strategy_report_{self.today}.html"

if __name__ == "__main__":
    # 測試報告生成
    import sys
    sys.path.append('.')
    
    # 載入測試數據
    with open('/home/admin/.openclaw/workspace/investment/reports/four_strategy_report_2026-02-10.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    generator = FourStrategyReportGenerator()
    html_path = generator.save_report(test_data)
    
    print(f"測試報告生成完成: {html_path}")