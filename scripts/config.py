#!/usr/bin/env python3
# 投資系統配置 (FinMind 主要數據源)

import os
from datetime import datetime

# 基本配置
CONFIG = {
    # 時間配置
    "update_time": "08:30",  # 台灣時間早上8:30更新 (市場開盤後)
    "timezone": "Asia/Taipei",
    
    # 資料來源配置
    "data_source_priority": "yfinance",  # 主要數據源: yfinance, 備用: finmind
    "data_sources": {
        # 主要數據源: FinMind (台灣本地數據，600次/小時限制)
        "finmind": {
            "api_url": "https://api.finmindtrade.com/api/v4/data",
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMi0wNiAxNDo0Mjo0NiIsInVzZXJfaWQiOiJub295YSIsImVtYWlsIjoiamFjay5zYy55YW5nQGdtYWlsLmNvbSIsImlwIjoiMjExLjIxLjkyLjIxMCJ9.PXqVAirKjOixGflicKyBneRQduIhpxlaB0VJTDaHHLE",
            "rate_limit": 600,  # 次/小時 (登入模式)
            "enabled": True,
        },
        # 備用數據源: Yahoo Finance (國際數據源)
        "yfinance": {
            "enabled": True,
            "fallback_only": True,  # 僅作為備用
        },
        # 其他數據源
        "twse_openapi": "https://openapi.twse.com.tw/",  # 台灣證交所開放資料
        "fugle_mcp": "https://api.fugle.tw/marketdata/v1.0/",  # Fugle即時數據
        "twse_holiday": "https://www.twse.com.tw/holidaySchedule/holidaySchedule",  # 休市日
        "twse_etf": "https://www.twse.com.tw/zh/ETF/",  # ETF資訊
    },
    
    # API金鑰
    "api_keys": {
        "fugle": "ZWI5Nzg0NmYtZDZiOC00Yjk4LWFhOTgtYmM5N2MxMmQyOTYyIDJiMjM4Y2MxLWVlYzctNGJmOS04NDUwLWQwZDY0MDE2MjM0Nw=="
    },
    
    # 篩選條件
    "screening_criteria": {
        "min_volume": 1000,  # 最小成交量(張)
        "max_pe_ratio": 30,  # 最大本益比
        "min_price": 10,     # 最低股價
        "max_price": 500,    # 最高股價
        "min_market_cap": 10_000_000_000,  # 最小市值(10億)
    },
    
    # 關注的ETF列表
    "etf_watchlist": [
        "006205",  # FB台50
        "006208",  # 元大台灣50
        "00646",   # 元大S&P500
        "006207",  # 富邦台50
        "006203",  # 元大MSCI台灣
        "006204",  # 永豐台灣加權
        "00690",   # 兆豐藍籌30
        "00692",   # 富邦公司治理
        "00850",   # 元大台灣ESG永續
        "00878",   # 國泰永續高股息
        # 大陸ETF
        "00636",   # 國泰中國A50
        "00639",   # 富邦深証100
        "00643",   # 群益深証中小
        "0061",    # 寶滬深
        "00752",   # 中信中國50
    ],
    
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
    "discord_channel_id": "1467419982240420014",  # 當前頻道ID
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
    """獲取HTML報告路徑"""
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
    primary = CONFIG.get("data_source_priority", "finmind")
    config = get_data_source_config(primary)
    
    if config and config.get("enabled", True):
        return primary, config
    return None, None

def get_fallback_data_sources():
    """獲取備用數據源列表"""
    fallbacks = []
    for source_name, config in CONFIG["data_sources"].items():
        if source_name == CONFIG.get("data_source_priority", "finmind"):
            continue
            
        if isinstance(config, dict):
            if config.get("enabled", True) and not config.get("fallback_only", False):
                fallbacks.append((source_name, config))
        else:
            fallbacks.append((source_name, {"api_url": config, "enabled": True}))
    
    return fallbacks

def get_finmind_token():
    """獲取FinMind token"""
    finmind_config = get_data_source_config("finmind")
    if finmind_config and isinstance(finmind_config, dict):
        return finmind_config.get("token")
    return None

def is_finmind_enabled():
    """檢查FinMind是否啟用"""
    finmind_config = get_data_source_config("finmind")
    return finmind_config and finmind_config.get("enabled", True)