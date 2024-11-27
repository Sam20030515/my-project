from getStockInfo import getStockInfo
import json
import pymongo
from datetime import datetime, timedelta
from pymongo import MongoClient
import subprocess

# MongoDB 連線設定 - 用來儲存投資記錄
target_client = MongoClient("mongodb://localhost:27017/")
target_db = target_client["investment_db"]
target_collection = target_db["investment_records"]

# MongoDB 連線設定 - 用來獲取股市資料
stock_client = MongoClient("mongodb://localhost:27017/")
db = stock_client["stock"]
collection = db["stock_record"]

# 獲取規則
# 獲取規則
def get_rules(id_filter=None):
    """從 MongoDB 獲取指定策略名稱為 DCA 的規則"""
    source_client = MongoClient("mongodb://localhost:27017/")
    source_db = source_client["myDatabase"]  # 請替換為您的資料庫名稱
    source_collection = source_db["rules"]  # 請替換為您的集合名稱

    # 增加條件，只選取 DCA 策略的資料
    query = {"strategy": "DCA"}
    if id_filter:
        query["id"] = id_filter  # 如果需要指定 id，可以添加此條件

    results = source_collection.find(query)

    rules = []
    for result in results:
        # 檢查是否存在 "date" 欄位
        if "date" not in result:
            continue  # 跳過沒有 "date" 欄位的資料

        rule = {
            "id": result.get("id", ""),  # 取得 id
            "strategy": result.get("strategy", ""),  # 取得策略名稱
            "stock_code": result.get("stock_code", ""),  # 取得股票代碼
            "date": result["date"],  # 取得投資日期
            "input_type": result.get("input_type", ""),  # 取得輸入類型（price 或 count）
            "value": result.get("value", 0)  # 取得投資金額或股數
        }
        rules.append(rule)

    return rules



# 獲取最接近的收盤價
def get_closest_stock_price(current_date, stock_code):
    """根據指定的日期，尋找最接近的收盤價資料"""
    for delta in range(0, 30):
        # 向前查找
        prev_date = current_date - timedelta(days=delta)
        stock_info_json = getStockInfo("DCA", prev_date.strftime("%Y/%m/%d"), stock_code)
        stock_info = json.loads(stock_info_json)

        if "收盤價(元)" in stock_info:
            return float(stock_info["收盤價(元)"])

        # 向後查找
        if delta > 0:
            next_date = current_date + timedelta(days=delta)
            stock_info_json = getStockInfo("DCA", next_date.strftime("%Y/%m/%d"), stock_code)
            stock_info = json.loads(stock_info_json)

            if "收盤價(元)" in stock_info:
                return float(stock_info["收盤價(元)"])

    return None  # 如果完全找不到資料，返回 None



# 定期定額投資策略
def dca(start, end, day, input_type, value, stock_code, rule_id, remaining_funds):
    current_date = start
    total_shares = 0
    total_investment = 0

    while current_date <= end:
        if current_date.day == day:
            stock_info_json = getStockInfo("DCA",current_date.strftime("%Y/%m/%d"), stock_code)
            stock_info = json.loads(stock_info_json)

            # 若當天沒有收盤價，找其餘近的收盤價
            if "收盤價(元)" in stock_info:
                current_stock_price = float(stock_info["收盤價(元)"])
            else:
                current_stock_price = get_closest_stock_price(current_date, stock_code)
                if current_stock_price is None:
                    # 如果找不到接近的收盤價，跳過這一天
                    current_date = current_date.replace(month=current_date.month % 12 + 1, year=current_date.year + (current_date.month // 12))
                    continue  # 跳到下一月

            # 根據交易模式計算實際投資金額
            if input_type == "price":
                investment_cost = value
                action = "buy"
            elif input_type == "count":
                investment_cost = value * 1000 * current_stock_price
                action = "buy"
            else:
                break

            # 資金檢查：如果剩餘資金不足以進行此次交易，跳過
            if investment_cost > remaining_funds:
                # 更新日期至下個月
                next_month = current_date.month % 12 + 1
                next_year = current_date.year + (current_date.month // 12)
                current_date = current_date.replace(year=next_year, month=next_month, day=day)
                continue

            # 計算購買的股數
            shares = value * 1000 if input_type == "count" else int(value / current_stock_price)

            # 更新交易後的總數據與剩餘資金
            total_shares += shares
            total_investment += investment_cost
            remaining_funds -= investment_cost  # **扣除本次交易的金額**
            market_value = total_shares * current_stock_price
            return_rate = (market_value - total_investment) / total_investment * 100

            # 建立交易記錄
            transaction = {
                "id": rule_id,
                "date": current_date.strftime("%Y-%m-%d"),
                "stock_code": stock_code,
                "action": action,  # 增加 action（buy 或 sell）
                "shares": total_shares,
                "total_investment": total_investment,
                "market_value": market_value,
                "return_rate": return_rate,
                "remaining_funds": remaining_funds,
                "stock_price": current_stock_price,  # 加入當日股價
                "transaction_value": investment_cost  # 改為 transaction_value
            }

            # 插入交易記錄到 MongoDB
            try:
                # 印出即將插入的交易記錄
                print("即將插入的交易記錄:", transaction)
                target_collection.insert_one(transaction)
                print("插入成功")
            except pymongo.errors.PyMongoError as e:
                print(f"MongoDB 錯誤: {e}")
            except Exception as e:
                print(f"其他錯誤: {e}")


        # 更新至下個月相同日期
        next_month = current_date.month % 12 + 1
        next_year = current_date.year + (current_date.month // 12)
        try:
            current_date = current_date.replace(year=next_year, month=next_month, day=day)
        except ValueError:
            current_date = current_date.replace(year=next_year, month=next_month) + timedelta(days=31 - day)

    return remaining_funds


# 讀取 user.json 中的 total_assets
def load_initial_funds(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return int(data["total_assets"])  # 轉換為整數
    except (FileNotFoundError, KeyError, ValueError) as e:
        return 0  # 無法讀取時返回 0

def main():
    # 讀取初始資金設定
    user_json_path = r"C:\Users\user\invest\local_data\user.json"
    total_funds = load_initial_funds(user_json_path)
    if total_funds <= 0:
        return

    # 取得所有規則
    all_rules = get_rules()

    # 設定投資期間
    investment_start = datetime(2022, 12, 31)
    investment_end = datetime(2023, 12, 31)

    # 處理每條規則
    for rule in all_rules:
        stock_code = rule["stock_code"]
        investment_day = int(rule["date"])
        input_type = rule["input_type"]
        investment_value = int(rule["value"])
        rule_id = rule["id"]

        # 每個策略執行前重置初始資金
        remaining_funds = total_funds

        # 執行投資策略，並更新剩餘資金
        if rule["strategy"] == "DCA":
            remaining_funds = dca(
                investment_start,
                investment_end,
                investment_day,
                input_type,
                investment_value,
                stock_code,
                rule_id,
                remaining_funds
            )

    # 繪製圖表（若需要）
    #subprocess.Popen(["python", "draw.py"])

if __name__ == "__main__":
    main()