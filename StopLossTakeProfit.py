from getStockInfo import getStockInfo
import json
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB 連線設定 - 用來儲存投資記錄
target_client = MongoClient("mongodb://localhost:27017/")
target_db = target_client["investment_records"]
target_collection = target_db["trade_records"]

def get_rules(greater_than_zero=True):
    """從 MongoDB 獲取所有指定策略的規則"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client["myDatabase"]  # 替換為你的資料庫名稱
    collection = db["rules"]  # 替換為你的集合名稱

    # 增加條件，只選取 StopLossTakeProfit 策略的資料
    query = {"strategy": "StopLossTakeProfit"}
    if greater_than_zero:
        query["id"] = {"$gt": 0}

    results = collection.find(query)

    rules = []
    for result in results:
        value_data = result.get("value", {})
        if not isinstance(value_data, dict):  # 確保 value 是字典
            continue
        
        rule = {
            "id": result.get("id", None),
            "strategy": result.get("strategy", None),
            "stock_code": result.get("stock_code", None),
            "value": {
                "stopLoss": float(value_data.get("stopLoss", 0)),
                "takeProfit": float(value_data.get("takeProfit", 0)),
                "everyBuy": float(value_data.get("everyBuy", 0))
            }
        }
        rules.append(rule)

    return rules

def StopLossTakeProfit(start, end, stock_code, every_buy, stop_loss_percent, take_profit_percent, remaining_funds):
    current_date = start
    total_shares = 0  # 持有的總股數
    total_cost = 0    # 總成本（用於計算動態成本價）

    while current_date <= end:
        # 使用 getStockInfo.py 提供的接口獲取股票資訊
        stock_info_json = getStockInfo("StopLossTakeProfit", current_date.strftime("%Y/%m/%d"), stock_code)
        try:
            stock_info = json.loads(stock_info_json)
        except json.JSONDecodeError:
            print(f"無法解析股票資訊：{stock_info_json}")
            current_date += timedelta(days=1)
            continue

        if "收盤價(元)" in stock_info:
            current_stock_price = float(stock_info["收盤價(元)"])
        else:
            current_date += timedelta(days=1)
            continue

        # 動態計算停損與停利價格
        if total_shares > 0:
            average_cost_price = total_cost / total_shares  # 平均成本價
            stop_loss_price = average_cost_price * (1 - stop_loss_percent / 100)
            take_profit_price = average_cost_price * (1 + take_profit_percent / 100)
        else:
            stop_loss_price = take_profit_price = 0  # 無持倉時無需計算

        # 全額買入（首次或在有剩餘資金時執行）
        if total_shares == 0 and remaining_funds > 0:
            shares = int(remaining_funds // current_stock_price)  # 計算可買入的股數
            if shares > 0:
                investment = shares * current_stock_price  # 實際投入金額
                remaining_funds -= investment  # 更新剩餘資金
                total_shares += shares
                total_cost += investment  # 更新總成本

                print(f"在 {current_date.strftime('%Y/%m/%d')} 全額買入 {shares} 股，買入價格: {current_stock_price} 元")
                trade_record = {
                    "stock_code": stock_code,
                    "action": "buy",
                    "shares": shares,
                    "price_per_share": current_stock_price,
                    "total_investment": investment,
                    "date": current_date.strftime('%Y/%m/%d'),
                    "remaining_funds": remaining_funds
                }
                target_collection.insert_one(trade_record)

        # 停損或停利條件觸發
        if total_shares > 0 and (current_stock_price <= stop_loss_price or current_stock_price >= take_profit_price):
            sell_shares = int(every_buy // current_stock_price)  # 計算每次可賣出的股數
            if sell_shares > total_shares:
                sell_shares = total_shares  # 如果剩餘股數不足，全部賣出

            if sell_shares > 0:
                total_value = sell_shares * current_stock_price  # 賣出總值
                remaining_funds += total_value  # 更新剩餘資金
                total_shares -= sell_shares  # 更新剩餘股數
                total_cost -= sell_shares * (total_cost / total_shares)  # 更新總成本
                return_rate = (current_stock_price - (total_cost / total_shares)) / (total_cost / total_shares) * 100

                print(f"在 {current_date.strftime('%Y/%m/%d')} 達成條件，賣出 {sell_shares} 股，價格: {current_stock_price} 元")
                trade_record = {
                    "stock_code": stock_code,
                    "action": "sell",
                    "shares": sell_shares,
                    "price_per_share": current_stock_price,
                    "total_value": total_value,
                    "return_rate": return_rate,
                    "date": current_date.strftime('%Y/%m/%d'),
                    "remaining_shares": total_shares,
                    "remaining_funds": remaining_funds
                }
                target_collection.insert_one(trade_record)

        # 前進到下一天
        current_date += timedelta(days=1)

    # 持有情況記錄
    if total_shares > 0:
        total_value = total_shares * current_stock_price  # 現值
        return_rate = (total_value - total_cost) / total_cost * 100

        print(f"持有結束: 在 {current_date.strftime('%Y/%m/%d')} 持有 {total_shares} 股，現值: {total_value} 元")
        trade_record = {
            "stock_code": stock_code,
            "action": "hold",
            "shares": total_shares,
            "current_value": total_value,
            "return_rate": return_rate,
            "date": current_date.strftime('%Y/%m/%d'),
            "remaining_funds": remaining_funds
        }
        target_collection.insert_one(trade_record)

    return remaining_funds


def load_initial_funds(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return int(data["total_assets"])  # 轉換為整數
    except (FileNotFoundError, KeyError, ValueError) as e:
        return 0  # 無法讀取時返回 0

def main():
    all_rules = get_rules()
    user_json_path = r"C:\Users\allen\TopicCode\local_data\user.json"
    total_funds = load_initial_funds(user_json_path)
    if total_funds <= 0:
        print("初始資金無效或無法讀取，程序終止。")
        return

    investment_start = datetime(2022, 12, 31)
    investment_end = datetime(2023, 12, 31)

    remaining_funds = total_funds  # 初始化剩餘資金
    for rule in all_rules:
        stock_code = rule["stock_code"]
        buy_value = rule["value"]["everyBuy"]
        stop_loss_percent = rule["value"]["stopLoss"]
        take_profit_percent = rule["value"]["takeProfit"]

        remaining_funds = StopLossTakeProfit(
            investment_start, investment_end, stock_code, buy_value, stop_loss_percent, take_profit_percent, remaining_funds
        )

    # 最終記錄總剩餘資金
    target_collection.insert_one({
        "record_type": "final_funds",
        "remaining_funds": remaining_funds,
        "date": datetime.now().strftime('%Y/%m/%d'),
    })
    print(f"最終剩餘資金: {remaining_funds} 元")

if __name__ == "__main__":
    main()
