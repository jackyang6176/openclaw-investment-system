#!/usr/bin/env python3
# 交易日判斷模組 - 檢查是否為台灣股市交易日
# 使用台灣證交所官方休市日數據：https://www.twse.com.tw/zh/trading/holiday.html

import requests
import json
from datetime import datetime, date, timedelta

class TradingDayChecker:
    def __init__(self):
        self.twse_holidays = self._load_twse_holiday_data()
        self.cache = {}  # 緩存交易日判斷結果
    
    def _load_twse_holiday_data(self):
        """從台灣證交所API載入休市日數據"""
        print("從台灣證交所載入休市日數據...")
        
        try:
            # 台灣證交所休市日API
            url = "https://www.twse.com.tw/holidaySchedule/holidaySchedule"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('stat') == 'ok':
                    holidays_set = set()
                    holiday_data = data.get('data', [])
                    
                    for item in holiday_data:
                        date_str = item[0]  # 日期
                        name = item[1]      # 名稱
                        description = item[2]  # 說明
                        
                        # 判斷是否為休市日
                        is_holiday = self._is_holiday_by_name(name)
                        
                        if is_holiday:
                            holidays_set.add(date_str)
                            print(f"  休市日: {date_str} - {name}")
                    
                    print(f"✅ 成功載入 {len(holidays_set)} 個休市日")
                    return holidays_set
                else:
                    print(f"⚠️  API返回狀態錯誤: {data.get('stat')}")
            else:
                print(f"⚠️  無法連接台灣證交所API: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  載入台灣證交所數據失敗: {str(e)}")
        
        # 如果API失敗，使用備用數據
        print("使用備用休市日數據...")
        return self._load_backup_holiday_data()
    
    def _is_holiday_by_name(self, name):
        """根據名稱判斷是否為休市日"""
        # 明確是交易日的
        if "開始交易日" in name or "最後交易日" in name:
            return False
        
        # 明確是休市日的關鍵字
        holiday_keywords = [
            "市場無交易",
            "放假",
            "紀念日",
            "國慶日",
            "勞動節",
            "除夕",
            "春節",
            "兒童節",
            "清明節",
            "端午節",
            "中秋節",
            "教師節",
            "光復",
            "行憲"
        ]
        
        # 檢查是否包含休市關鍵字
        for keyword in holiday_keywords:
            if keyword in name:
                return True
        
        # 檢查「節」字，但要排除「最後交易日」等
        if "節" in name and "交易日" not in name:
            return True
        
        # 其他情況預設為交易日（保守估計）
        return False
    
    def _load_backup_holiday_data(self):
        """載入備用休市日數據（當API失敗時使用）"""
        # 2026年台灣證交所休市日（根據官方資料，修正版）
        backup_holidays = {
            '2026-01-01',  # 中華民國開國紀念日
            '2026-02-12',  # 市場無交易，僅辦理結算交割作業
            '2026-02-13',  # 市場無交易，僅辦理結算交割作業
            '2026-02-15',  # 農曆除夕及春節
            '2026-02-16',  # 農曆除夕及春節
            '2026-02-17',  # 農曆除夕及春節
            '2026-02-18',  # 農曆除夕及春節
            '2026-02-19',  # 農曆除夕及春節
            '2026-02-20',  # 農曆除夕及春節（補假）
            '2026-02-27',  # 和平紀念日（補假）
            '2026-02-28',  # 和平紀念日
            '2026-04-03',  # 兒童節及民族掃墓節（補假）
            '2026-04-04',  # 兒童節及民族掃墓節
            '2026-04-05',  # 兒童節及民族掃墓節
            '2026-04-06',  # 兒童節及民族掃墓節（補假）
            '2026-05-01',  # 勞動節
            '2026-06-19',  # 端午節
            '2026-09-25',  # 中秋節
            '2026-09-28',  # 孔子誕辰紀念日/教師節
            '2026-10-09',  # 國慶日（補假）
            '2026-10-10',  # 國慶日
            '2026-10-25',  # 臺灣光復暨金門古寧頭大捷紀念日
            '2026-10-26',  # 臺灣光復暨金門古寧頭大捷紀念日（補假）
            '2026-12-25',  # 行憲紀念日
        }
        
        print(f"使用備用數據: {len(backup_holidays)} 個休市日")
        return backup_holidays
    
    def is_trading_day(self, check_date=None):
        """檢查指定日期是否為交易日"""
        if check_date is None:
            check_date = date.today()
        
        # 檢查緩存
        date_str = check_date.strftime('%Y-%m-%d')
        if date_str in self.cache:
            return self.cache[date_str]
        
        # 1. 檢查是否為週末（台灣股市週六、週日休市）
        weekday = check_date.weekday()  # 0=周一, 1=周二, ..., 6=周日
        
        # 台灣股市週六、週日休市
        if weekday >= 5:  # 5=周六, 6=周日
            self.cache[date_str] = False
            return False
        
        # 2. 檢查是否為台灣證交所公告的休市日
        if date_str in self.twse_holidays:
            self.cache[date_str] = False
            return False
        
        # 3. 檢查特殊情況（如颱風假等）
        # 這裡可以接入政府公告API，暫時先跳過
        
        # 4. 檢查是否為補班日（週六開市）
        # 台灣有時週六補班開市，但證交所會特別公告
        # 目前假設週六都休市，除非特別公告
        
        self.cache[date_str] = True
        return True
    
    def get_next_trading_day(self, from_date=None):
        """獲取下一個交易日"""
        if from_date is None:
            from_date = date.today()
        
        next_day = from_date + timedelta(days=1)
        while not self.is_trading_day(next_day):
            next_day += timedelta(days=1)
        
        return next_day
    
    def get_previous_trading_day(self, from_date=None):
        """獲取上一個交易日"""
        if from_date is None:
            from_date = date.today()
        
        prev_day = from_date - timedelta(days=1)
        while not self.is_trading_day(prev_day):
            prev_day -= timedelta(days=1)
        
        return prev_day
    
    def get_trading_days_in_range(self, start_date, end_date):
        """獲取指定日期範圍內的所有交易日"""
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def check_market_hours(self):
        """檢查當前是否在交易時間內"""
        now = datetime.now()
        current_time = now.time()
        
        # 台灣股市交易時間：
        # 一般交易：09:00-13:30
        # 盤後交易：14:00-14:30
        # 零股交易：13:40-14:30
        
        # 檢查是否在一般交易時間
        morning_start = datetime.strptime('09:00', '%H:%M').time()
        morning_end = datetime.strptime('13:30', '%H:%M').time()
        
        if morning_start <= current_time <= morning_end:
            return 'regular_trading'
        
        # 檢查是否在盤後交易時間
        after_start = datetime.strptime('14:00', '%H:%M').time()
        after_end = datetime.strptime('14:30', '%H:%M').time()
        
        if after_start <= current_time <= after_end:
            return 'after_hours_trading'
        
        return 'market_closed'
    
    def get_holiday_info(self, check_date=None):
        """獲取休市日資訊"""
        if check_date is None:
            check_date = date.today()
        
        date_str = check_date.strftime('%Y-%m-%d')
        
        if date_str in self.twse_holidays:
            return {
                'is_holiday': True,
                'date': date_str,
                'reason': '台灣證交所公告休市日'
            }
        
        weekday = check_date.weekday()
        if weekday >= 5:
            return {
                'is_holiday': True,
                'date': date_str,
                'reason': '週末休市'
            }
        
        return {
            'is_holiday': False,
            'date': date_str,
            'reason': '正常交易日'
        }

if __name__ == "__main__":
    # 測試交易日判斷
    checker = TradingDayChecker()
    
    print("交易日判斷測試 (使用台灣證交所官方數據):")
    print("-" * 60)
    
    today = date.today()
    today_status = checker.is_trading_day(today)
    print(f"今天 ({today}): {'✅ 交易日' if today_status else '❌ 非交易日'}")
    
    # 顯示休市日資訊
    holiday_info = checker.get_holiday_info(today)
    if holiday_info['is_holiday']:
        print(f"休市原因: {holiday_info['reason']}")
    
    print("\n未來7天交易日狀態:")
    print("-" * 40)
    
    for i in range(1, 8):
        test_date = today + timedelta(days=i)
        is_trading = checker.is_trading_day(test_date)
        weekday_str = ['一', '二', '三', '四', '五', '六', '日'][test_date.weekday()]
        
        if is_trading:
            print(f"{test_date} (星期{weekday_str}): ✅ 交易日")
        else:
            holiday_info = checker.get_holiday_info(test_date)
            print(f"{test_date} (星期{weekday_str}): ❌ 非交易日 - {holiday_info['reason']}")
    
    print("-" * 40)
    print(f"下一個交易日: {checker.get_next_trading_day()}")
    print(f"上一個交易日: {checker.get_previous_trading_day()}")
    
    # 檢查當前交易時間
    market_status = checker.check_market_hours()
    status_map = {
        'regular_trading': '一般交易時間 (09:00-13:30)',
        'after_hours_trading': '盤後交易時間 (14:00-14:30)',
        'market_closed': '市場休市'
    }
    print(f"當前市場狀態: {status_map.get(market_status, '未知')}")
    
    # 顯示載入的休市日數量
    print(f"\n已載入休市日數量: {len(checker.twse_holidays)}")
    print("=" * 60)