#!/usr/bin/env python3
# 投資系統配置
# 最後更新：2026-02-27 - 移除不可靠數據源 (yfinance, FinMind)
# 等待 Fubon 證券 API 開通

import os
from datetime import datetime

# 基本配置
CONFIG = {
    # 時間配置
    "update_time": "08:30",  # 台灣時間早上 8:30 更新 (市場開盤後)
    "timezone": "Asia/Taipei",
    
    # 資料來源配置 (2026-02-27 更新)
    # ⚠️ yfinance 和 FinMind 已移除（數據不可靠）
    # ✅ 等待 Fubon 證券 API 開通
    "data_source_priority": "fubon",  # 主要數據源：Fubon API (待開通)
    "data_sources": {
        # Fubon 證券 API (待開通)
        "fubon": {
            "enabled": False,  # ⏳ 等待帳號審批
            "status": "pending",
            "api_version": "v2.2.8",
            "note": "帳號申請中，預計 2026-02-28 開通",
        },
        
        # ❌ 已移除的數據源 (2026-02-27)
        # yfinance: 00887.TW 無法獲取 (404 錯誤)，但實際仍在交易
        # FinMind: 權限不足 (register → sponsor 需要升級)
    },
    
    # API 金鑰
    "api_keys": {
        # Fubon API 金鑰 (待配置)
        # "fubon_api_key": "待申請",
        # "fubon_secret_key": "待申請",
    },
    
    # 篩選條件
    "screening_criteria": {
        "min_volume": 1000,  # 最小成交量 (張)
        "max_pe_ratio": 30,  # 最大本益比
        "min_price": 10,     # 最低股價
        "max_price": 500,    # 最高股價
        "min_market_cap": 10_000_000_000,  # 最小市值 (10 億)
    },
    
    # 關注的 ETF 列表
    "etf_watchlist": [
        "0050",  # 元大台灣 50
        "0056",  # 元大高股息
        "006208",  # 元大台灣 50
        "00646",   # 元大 S&P500
        "006207",  # 富邦台 50
        "006203",  # 元大 MSCI 台灣
        "006204",  # 永豐台灣加權
        "00690",   # 兆豐藍籌 30
        "00692",   # 富邦公司治理
        "00850",   # 元大台灣 ESG 永續
        "00878",   # 國泰永續高股息
        # 大陸 ETF
        "00636",   # 國泰中國 A50
        "00639",   # 富邦深証 100
        "00643",   # 群益深証中小
        "0061",    # 寶滬深
        "00752",   # 中信中國 50
    ],
    
    # 用戶持倉 ETF (2026-02-27 驗證)
    "user_holdings": {
        "00655L": {"name": "國泰 A50 正 2", "type": "槓桿 ETF", "verified": True},
        "00882": {"name": "中信中國高股息", "type": "高股息 ETF", "verified": True},
        "00887": {"name": "永豐中國科技 50 大", "type": "科技主題 ETF", "verified": True, "last_price": 13.29, "date": "2026-02-26"},
    },
    
    # 重要股票列表（四策略分析使用）
    "important_stocks": [
        '2330', '2317', '2454', '2308', '2881', '2882',
        '1301', '1303', '2002', '2412', '1216', '2357',
        '2382', '3008', '3711', '2303', '2886', '5880',
        '2891', '2892'
    ],
    
    # 輸出配置
    "output_dir": os.path.join(os.path.dirname(__file__), "../reports"),
    "web_dir": os.path.join(os.path.dirname(__file__), "../../website/investment"),
    
    # Discord 通知配置
    "discord_webhook": "https://discord.com/api/webhooks/1470240479525212181/feekMInHeAIS-hMPuzthOTTIdeNcOuosYSJkqPT4etQgeRAXHs6QCIt7dm1BEuI6YkYi",
    "discord_channel_id": "1467419982240420014",  # 當前頻道 ID
}

def get_today_str():
    """獲取今日日期字串"""
    return datetime.now().strftime("%Y-%m-%d")

def get_report_path(date_str=None):
    """獲取報告文件路徑"""
    if date_str is None:
        date_str = get_today_str()
    return os.path.join(CONFIG["output_dir"], f"report_{date_str}.json")

def get_html_path(date_str=None):
    """獲取 HTML 報告路徑"""
    if date_str is None:
        date_str = get_today_str()
    return os.path.join(CONFIG["web_dir"], f"four_strategy_report_{date_str}.html")

# 數據源管理
def get_data_source_config(source_name):
    """獲取數據源配置"""
    if source_name in CONFIG["data_sources"]:
        config = CONFIG["data_sources"][source_name]
        if isinstance(config, dict):
            return config
        return {"api_url": config, "enabled": True}
    return None

def get_primary_data_source():
    """獲取主要數據源"""
    primary = CONFIG.get("data_source_priority", "fubon")
    config = get_data_source_config(primary)
    
    if config and config.get("enabled", True):
        return primary, config
    return None, None

def get_fallback_data_sources():
    """獲取備用數據源列表"""
    fallbacks = []
    for source_name, config in CONFIG["data_sources"].items():
        if source_name == CONFIG.get("data_source_priority", "fubon"):
            continue
            
        if isinstance(config, dict):
            if config.get("enabled", True) and not config.get("fallback_only", False):
                fallbacks.append((source_name, config))
        else:
            fallbacks.append((source_name, {"api_url": config, "enabled": True}))
    
    return fallbacks

def get_fubon_api_key():
    """獲取 Fubon API 金鑰"""
    return CONFIG["api_keys"].get("fubon_api_key")

def is_fubon_enabled():
    """檢查 Fubon API 是否啟用"""
    fubon_config = get_data_source_config("fubon")
    return fubon_config and fubon_config.get("enabled", False)

def verify_symbol(symbol, source="fubon"):
    """驗證代碼是否可用"""
    # 等待 Fubon API 開通後實現
    return True
