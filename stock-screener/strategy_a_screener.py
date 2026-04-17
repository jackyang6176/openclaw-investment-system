#!/usr/bin/env python3
"""
策略A - 技術動能篩選
========================
【規格】/home/admin/.openclaw/workspace/stock-screener/STRATEGY_A_SPEC.md

執行時間：每日 14:30（收盤後）
產出：追蹤清單（最多20檔）

【進場條件】
1. MA5 斜率 > 0（最近3個交易日連續上升）
2. Gap < 2%（(MA20 - MA5) / MA20 < 2%）
3. Gap 三日縮小（MA5 逐漸逼近 MA20）
4. 成交量連四日放大（今日 > 昨日 > 前日 > 大前日）
5. K < 25 且 D < 25（最近3個交易日每天都滿足）
6. 日均成交張數 >= 1000（過去4天日平均）

【API】
- TWSE: 股票清單 + 今日收盤價（1次）
- Fubon SDK: sma(5) + sma(20) + kdj + candles（每檔4次）
- Rate Limit: 60次/分鐘（每呼叫間隔 1 秒）
"""
import sys
import json
import time
import os
from datetime import datetime, date, timedelta

# ====== 設定 ======
WORKSPACE = "/home/admin/.openclaw/workspace"
PDRIVE = "/home/admin/pCloudDrive/openclaw/stock-screener"
OUTPUT_FILE = f"{PDRIVE}/data/tracking_list.json"
STATE_FILE = f"{WORKSPACE}/tmp/strategy_a_state.json"
LOG_FILE = f"{PDRIVE}/logs/strategy_a_screener.log"
DELAY = 1  # 每呼叫間隔 1 秒（Rate limit: 60次/分鐘）
DATE_RANGE = 10  # 一次取10天日曆日

# ====== TWSE 下載 ======
def get_twse_today():
    """從 TWSE 取得今日收盤資料（股票清單+價格）"""
    import urllib.request
    today = date.today()
    date_str = today.strftime("%Y%m%d")
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date_str}&type=ALL&response=json"
    
    print(f"[TWSE] 下載資料: {date_str}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read().decode('utf-8'))
    
    tables = raw.get('tables', [])
    if not tables:
        print("[TWSE] 無表格資料")
        return {}
    
    # 找「每日收盤行情(全部)」表格
    target_table = None
    for t in tables:
        title = t.get('title', '')
        if '收盤行情' in title and '全部' in title:
            target_table = t
            break
    
    if not target_table:
        print("[TWSE] 找不到收盤行情表格")
        return {}
    
    result = {}
    skipped = 0
    for row in target_table.get('data', []):
        if len(row) < 9:
            continue
        code = row[0].strip()
        name = row[1].strip() if len(row) > 1 else code
        
        # 過濾：只留上市櫃股票 + ETF
        if not is_stock_or_etf(code):
            skipped += 1
            continue
        
        try:
            close = float(row[8].replace(',', ''))
            result[code] = {'name': name, 'close': close}
        except (ValueError, IndexError):
            continue
    
    print(f"[TWSE] 取得 {len(result)} 檔（已過濾 {skipped} 檔）")
    return result


def is_stock_or_etf(code):
    """過濾上市櫃股票 + ETF"""
    if code.startswith('00') or code.startswith('02'):
        return True
    if len(code) >= 4 and len(code) <= 6 and code.isdigit():
        first = int(code[0])
        if first in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return True
    return False


# ====== Fubon SDK ======
sys.path.insert(0, f"{WORKSPACE}/fubon_sdk_complete")
from fubon_complete import FubonComplete


def get_date_range():
    """計算 API 查詢的日期區間（取10天）"""
    today = date.today()
    start = today - timedelta(days=DATE_RANGE)
    return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')


def get_technical_data(fc, code):
    """
    取得技術指標資料（MA5, MA20, KDJ, 成交量）
    一次取10天日曆日，回傳最近3-4個交易日的資料
    """
    from_date, to_date = get_date_range()
    results = {
        'sma5': None,
        'sma20': None,
        'kdj': None,
        'candles': None
    }
    
    # 1. MA5（帶日期區間）
    try:
        sma5 = fc.get_sma(code, period=5, from_date=from_date, to_date=to_date)
        time.sleep(DELAY)
        if sma5 and len(sma5) >= 4:
            results['sma5'] = sma5[-4:]  # 取最後4筆（最近4個交易日）
    except Exception as e:
        print(f"  [WARN] {code} SMA5 錯誤: {e}")
        return results
    
    # 2. MA20（帶日期區間）
    try:
        sma20 = fc.get_sma(code, period=20, from_date=from_date, to_date=to_date)
        time.sleep(DELAY)
        if sma20 and len(sma20) >= 4:
            results['sma20'] = sma20[-4:]
    except Exception as e:
        print(f"  [WARN] {code} SMA20 錯誤: {e}")
        return results
    
    # 3. KDJ（帶日期區間，回傳陣列）
    try:
        kdj = fc.get_kdj(code, from_date=from_date, to_date=to_date)
        time.sleep(DELAY)
        if kdj and len(kdj) >= 3:
            results['kdj'] = kdj[-3:]  # 取最後3筆（最近3個交易日）
    except Exception as e:
        print(f"  [WARN] {code} KDJ 錯誤: {e}")
        return results
    
    # 4. 成交量（candles，帶日期區間）
    try:
        candles = fc.get_candles(code, from_date=from_date, to_date=to_date)
        time.sleep(DELAY)
        if candles and len(candles) >= 4:
            results['candles'] = candles[-4:]  # 取最後4筆
    except Exception as e:
        print(f"  [WARN] {code} Candles 錯誤: {e}")
        return results
    
    return results


def analyze_strategy_a(code, twse_data, tech_data):
    """
    策略A分析
    條件1: MA5 斜率 > 0（最近3個交易日連續上升）
    條件2: Gap < 2%
    條件3: Gap 三日縮小
    條件4: 成交量連四日放大
    條件5: K < 25 且 D < 25（最近3個交易日每天都滿足）
    條件6: 日均成交張數 >= 1000
    """
    today_data = twse_data.get(code)
    if not today_data:
        return None
    
    close = today_data.get('close')
    if not close or close <= 0:
        return None
    
    sma5 = tech_data.get('sma5')
    sma20 = tech_data.get('sma20')
    kdj = tech_data.get('kdj')
    candles = tech_data.get('candles')
    
    # 檢查基本資料
    if not all([sma5, sma20, kdj, candles]):
        return None
    
    if not (len(sma5) >= 3 and len(sma20) >= 3 and len(kdj) >= 3 and len(candles) >= 4):
        return None
    
    # ===== 條件1: MA5 斜率 > 0（最近3個交易日連續上升）=====
    # 取最近3個交易日的 MA5
    ma5_d1 = sma5[-3]['sma']  # 三天前
    ma5_d2 = sma5[-2]['sma']  # 兩天前
    ma5_d3 = sma5[-1]['sma']  # 今天
    cond1 = (ma5_d3 > ma5_d2 > ma5_d1)
    
    # ===== 條件2: Gap < 2% = (MA20 - MA5) / MA20 < 2% =====
    m5 = sma5[-1]['sma']
    m20 = sma20[-1]['sma']
    if m20 <= 0:
        return None
    gap = (m20 - m5) / m20 * 100
    cond2 = (gap < 2.0)
    
    # ===== 條件3: Gap 三日縮小 =====
    # 取最近3個交易日的 Gap
    gaps = []
    for i in range(-4, 1):
        idx = len(sma20) + i
        if 0 <= idx < len(sma5):
            m5i = sma5[idx]['sma']
            m20i = sma20[idx]['sma']
            if m20i > 0:
                gaps.append((m20i - m5i) / m20i * 100)
    
    if len(gaps) < 4:
        return None
    # gaps[-4], gaps[-3], gaps[-2], gaps[-1] = 4天前的gap, 3天前的gap, 2天前的gap, 今天gap
    # 條件: 今天 < 2天前 < 3天前 < 4天前（差距越來越小）
    cond3 = (gaps[-1] < gaps[-2] < gaps[-3] < gaps[-4])
    
    # ===== 條件4: 成交量連四日放大 =====
    # candles[-4], candles[-3], candles[-2], candles[-1] = 4天前, 3天前, 2天前, 今天
    vol_1 = candles[-4]['volume']  # 大前日
    vol_2 = candles[-3]['volume']  # 前日
    vol_3 = candles[-2]['volume']  # 昨日
    vol_4 = candles[-1]['volume']  # 今日
    cond4 = (vol_4 > vol_3 > vol_2 > vol_1)
    
    # ===== 條件5: K < 25 且 D < 25（最近3個交易日每天都滿足）=====
    cond5 = all(
        k['k'] < 25 and k['d'] < 25
        for k in kdj
    )
    
    # ===== 條件6: 日均成交張數 >= 1000 =====
    # candles volume 是股數，1張=1000股
    total_vol = sum(c['volume'] for c in candles)
    avg_vol_shares = total_vol / 4
    avg_vol_lots = avg_vol_shares / 1000
    cond6 = (avg_vol_lots >= 1000)
    
    # ===== 信心度 =====
    conditions_met = sum([cond1, cond2, cond3, cond4, cond5, cond6])
    confidence = conditions_met / 6 * 100
    
    return {
        'code': code,
        'name': today_data.get('name', code),
        'close': close,
        'ma5': round(m5, 2),
        'ma20': round(m20, 2),
        'gap': round(gap, 3),
        'avg_volume_lots': round(avg_vol_lots, 1),
        'cond1_ma5_slope': cond1,
        'cond2_gap_2pct': cond2,
        'cond3_gap_shrinking': cond3,
        'cond4_volume_up': cond4,
        'cond5_kd_below_25': cond5,
        'cond6_volume_1k': cond6,
        'conditions_met': conditions_met,
        'confidence': round(confidence, 1),
        'ok': conditions_met == 6
    }


# ====== 追蹤清單管理 ======
def load_tracking_list():
    """載入現有追蹤清單"""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            data = json.load(f)
            return data.get('holdings', []), data.get('watchlist', [])
    return [], []


def save_tracking_list(holdings, watchlist, new_filtered):
    """
    保存追蹤清單
    - 庫存股票自動保留
    - 新篩選結果按信心度排序加入
    - 總數最多20檔
    """
    # 庫存優先
    tracking = holdings.copy()
    
    # 加入新篩選結果（按信心度排序）
    for stock in sorted(new_filtered, key=lambda x: -x['confidence']):
        if len(tracking) >= 20:
            break
        # 避免重複
        if stock['code'] not in [t['code'] for t in tracking]:
            tracking.append(stock)
    
    today = str(date.today())
    output = {
        'date': today,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'holdings': holdings,
        'watchlist': [s for s in tracking if s['code'] not in [h['code'] for h in holdings]],
        'total': len(tracking)
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    return output


# ====== 主要流程 ======
def main():
    now = datetime.now()
    print(f"\n[{'='*60}]")
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 策略A篩選啟動")
    print(f"[{'='*60}]\n")
    
    # Step 1: 從 TWSE 取得今日資料
    twse_data = get_twse_today()
    if not twse_data:
        print("[ERROR] 無法取得 TWSE 資料，掃描終止")
        return
    
    # Step 2: 登入 Fubon SDK
    fc = FubonComplete()
    fc._load_config()
    fc.login()
    print()
    
    # Step 3: 載入現有追蹤清單
    holdings, current_watchlist = load_tracking_list()
    print(f"[追蹤] 庫存: {len(holdings)} 檔")
    
    # Step 4: 分析每檔股票
    results = []
    codes = list(twse_data.keys())
    total = len(codes)
    
    print(f"[INFO] 總共 {total} 檔待篩選")
    print(f"[INFO] 每呼叫間隔 {DELAY} 秒，預計耗時 {total * 4 * DELAY / 60:.0f} 分鐘\n")
    
    for i, code in enumerate(codes):
        tech_data = get_technical_data(fc, code)
        result = analyze_strategy_a(code, twse_data, tech_data)
        
        if result:
            results.append(result)
        
        # 進度報告
        if (i + 1) % 100 == 0 or (i + 1) == total:
            print(f"  進度: {i+1}/{total} ({(i+1)*100//total}%)")
    
    # Step 5: 分類結果
    passed = [r for r in results if r['ok']]
    near = sorted([r for r in results if not r['ok'] and r['confidence'] > 0],
                  key=lambda x: -x['confidence'])[:20]
    
    print(f"\n[{'='*60}]")
    print(f"[SUMMARY] 篩選完成！")
    print(f"[SUMMARY] 總掃描: {len(results)}/{total} 檔")
    print(f"[SUMMARY] 完全符合 (6/6): {len(passed)} 檔")
    print(f"[{'='*60}]\n")
    
    # 顯示完全符合的結果
    if passed:
        print(f"【完全符合 6/6 條件】({len(passed)}檔)")
        for p in sorted(passed, key=lambda x: -x['confidence'])[:10]:
            print(f"  ✅ {p['code']} {p.get('name','')}: "
                  f"收={p['close']} MA5={p['ma5']} MA20={p['ma20']} "
                  f"gap={p['gap']}% 量={p['avg_volume_lots']}張 信心={p['confidence']}%")
    
    # Step 6: 更新追蹤清單
    output = save_tracking_list(holdings, current_watchlist, passed)
    print(f"\n[追蹤] 清單已更新: {output['total']} 檔")
    print(f"[追蹤] 產出位置: {OUTPUT_FILE}")
    
    # Step 7: 保存詳細結果
    result_file = f"{PDRIVE}/data/strategy_a_results_{date.today()}.json"
    with open(result_file, 'w') as f:
        json.dump({
            'date': str(date.today()),
            'total': total,
            'scanned': len(results),
            'passed': passed,
            'near': near
        }, f, ensure_ascii=False, indent=2)
    print(f"[檔案] 詳細結果: {result_file}")
    
    # 登出
    fc.logout()
    
    print(f"\n[{'='*60}]")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 篩選完成")
    print(f"[{'='*60}]\n")


if __name__ == "__main__":
    main()
