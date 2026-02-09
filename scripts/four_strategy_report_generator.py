#!/usr/bin/env python3
# 四策略投資報告生成器 (修正版)

import json
import os
from datetime import datetime

class FourStrategyReportGeneratorFixed:
    """四策略投資報告生成器 (修正版)"""
    
    def __init__(self, report_time=None):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.report_time = report_time or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_html(self, analysis_result):
        """生成HTML報告"""
        
        # 提取各策略結果
        technical_stocks = analysis_result.get('technical_strategy', [])
        fundamental_stocks = analysis_result.get('fundamental_strategy', [])
        hybrid_stocks = analysis_result.get('hybrid_strategy', [])
        thematic_data = analysis_result.get('thematic_strategy', {})
        high_dividend = thematic_data.get('high_dividend', [])
        growth_stocks = thematic_data.get('growth_stocks', [])
        value_stocks = thematic_data.get('value_stocks', [])
        
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>四策略投資分析 - {self.today}</title>
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
            padding: 30px;
        }}
        
        .strategy-section {{
            margin-bottom: 40px;
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
            font-size: 1rem;
            opacity: 0.9;
        }}
        
        .thematic-subsection {{
            margin-top: 25px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .thematic-title {{
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .stock-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .stock-table th {{
            background: #2c3e50;
            color: white;
            padding: 12px 10px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .stock-table td {{
            padding: 12px 10px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.9rem;
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
            border-radius: 4px;
            padding: 4px 8px;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            background: #f1f5f9;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }}
        
        .update-time {{
            margin-top: 10px;
            font-size: 0.9rem;
            color: #94a3b8;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                border-radius: 10px;
            }}
            
            header {{
                padding: 25px 20px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .strategies-container {{
                padding: 15px;
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
                padding: 8px 6px;
                font-size: 0.8rem;
            }}
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
    with open('/home/admin/.openclaw/workspace/investment/reports/four_strategy_report_2026-02-09.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    generator = FourStrategyReportGeneratorFixed()
    html_path = generator.save_report(test_data)
    
    print(f"測試報告生成完成: {html_path}")