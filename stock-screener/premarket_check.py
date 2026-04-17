#!/usr/bin/env python3
"""
盤前準備腳本
每日 08:30 執行（平日）
產出: /tmp/premarket_status.json
"""
import sys
import json
import os
sys.path.insert(0, '/home/admin/.openclaw/workspace/fubon_sdk_complete')
from fubon_complete import FubonComplete
from datetime import datetime

OUTPUT = '/tmp/premarket_status.json'

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 盤前準備啟動")
    
    fc = FubonComplete()
    
    # 登入
    if not fc.login():
        print("[錯誤] 富邦登入失敗")
        return
    print(f"[登入] 成功: {fc.account.name} ({fc.account.branch_no}/{fc.account.account})")
    
    # 1. 查詢帳戶可用餘額
    try:
        r = fc.sdk.accounting.bank_remain(account=fc.account)
        if r.is_success:
            avail = r.data.available_balance
        else:
            avail = 0
        print(f"[帳戶] 可用餘額: {avail:,.0f} TWD")
    except Exception as e:
        print(f"[錯誤] 查詢帳戶失敗: {e}")
        avail = 0
    
    # 2. 查詢持倉
    holdings = []
    try:
        result = fc.sdk.accounting.unrealized_gains_and_loses(account=fc.account)
        if result.is_success and result.data:
            for h in result.data:
                code = str(h.stock_no).strip()
                qty = int(h.tradable_qty)
                entry = float(h.cost_price)
                if qty > 0 and entry > 0:
                    stop = round(entry * 0.95, 2)
                    target = round(entry * 1.10, 2)
                    unreal = float(getattr(h, 'unrealized_profit', 0) or getattr(h, 'unrealized_loss', 0) or 0)
                    last = entry + unreal / qty if qty > 0 else entry
                    pnl = (last - entry) / entry * 100 if entry > 0 else 0
                    holdings.append({
                        'code': code,
                        'name': getattr(h, 'stock_name', code),
                        'qty': qty,
                        'entry_price': entry,
                        'last_price': round(last, 2),
                        'pnl': round(pnl, 2),
                        'stop_loss': stop,
                        'target': target,
                        'status': 'HOLDING'
                    })
        print(f"[持倉] {len(holdings)} 檔")
    except Exception as e:
        print(f"[錯誤] 查詢持倉失敗: {e}")
    
    # 3. 讀取追蹤清單
    watchlist = []
    try:
        tracking_file = '/home/admin/pCloudDrive/openclaw/stock-screener/data/tracking_list.json'
        if os.path.exists(tracking_file):
            with open(tracking_file) as f:
                data = json.load(f)
                watchlist = data.get('watchlist', [])[:10]  # 取前10檔
        print(f"[追蹤] {len(watchlist)} 檔")
    except Exception as e:
        print(f"[錯誤] 讀取追蹤清單失敗: {e}")
    
    # 4. 產出狀態檔
    status = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'account': {
            'broker': '富邦',
            'account': f"{fc.account.branch_no}/{fc.account.account}",
            'available_balance': round(avail, 0),
            'currency': 'TWD'
        },
        'holdings': holdings,
        'watchlist': watchlist,
        'notes': f'Market opens 09:00. Balance: {avail:,.0f} TWD. Holdings: {len(holdings)} lots.'
    }
    
    with open(OUTPUT, 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    
    print(f"[完成] 狀態檔已寫入: {OUTPUT}")
    print(f"[摘要] 持倉: {len(holdings)} 檔 | 追蹤: {len(watchlist)} 檔 | 餘額: {avail:,.0f}")
    
    fc.logout()

if __name__ == '__main__':
    main()
