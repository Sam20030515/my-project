from getStockInfo import getStockInfo
from datetime import datetime, timedelta
from pymongo import MongoClient
import json

# MongoDB 連線設定 - 用來儲存投資記錄
target_client = MongoClient("mongodb://localhost:27017/")
target_db = target_client["investment_db"]
target_collection = target_db["investment_records"]
target_collection1 = target_db["rank_records"]

def get_rules():
    """從 MongoDB 獲取 PE 策略的解釋規則"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client["myDatabase"]  # 替換為你的資料庫名稱
    collection = db["rules"]  # 替換為你的集合名稱

    query = {"strategy": "PE"}
    results = collection.find(query)

    rules = []
    for result in results:
        value = result.get("value", None)
        if value:
            rules.append({
                "id": result.get("id"),
                "strategy": result.get("strategy"),
                "stock_code": result.get("stock_code"),
                "pe_ratio": float(value)  # 合理股價系數
            })
    return rules

def calculate_fair_price(eps_data, pe_ratio, month):
    """根據月份和 EPS 計算合理股價"""
    if 1 <= month <= 3:
        return eps_data["q1"] * pe_ratio
    elif 4 <= month <= 6:
        return eps_data["q2"] * 4 * pe_ratio
    elif 7 <= month <= 9:
        return eps_data["q3"] * 2 * pe_ratio
    elif 10 <= month <= 12:
        return (eps_data["q4"] / 3) * 4 * pe_ratio
    return 0

def get_user_data():
    """讀取用戶資金資訊"""
    with open(r"C:\Users\user\invest\local_data\user.json", "r", encoding="utf-8") as f:
        user_data = json.load(f)
    return float(user_data.get("total_assets", 0))

def PE_strategy(start, end, rule_id, stock_code, pe_ratio, remaining_funds):
    current_date = start
    total_shares = 0
    total_cost = 0
    return_rate = 0  # 初始化 return_rate
    all_investment = 0

    while current_date <= end:
        stock_info_json = getStockInfo("PE", current_date.strftime("%Y/%m/%d"), stock_code)

        if isinstance(stock_info_json, dict):
            stock_info = stock_info_json
        else:
            try:
                stock_info = json.loads(stock_info_json)
            except json.JSONDecodeError:
                print(f"Failed to parse stock info: {stock_info_json}")
                current_date += timedelta(days=1)
                continue

        if "closing_price" in stock_info and "eps_records" in stock_info:
            closing_price = float(stock_info["closing_price"])
            eps_records = stock_info["eps_records"]
            fair_price = calculate_fair_price(eps_records, pe_ratio, current_date.month)

            if closing_price < fair_price and remaining_funds > closing_price:
                shares = int(remaining_funds // closing_price)
                investment = shares * closing_price
                remaining_funds -= investment
                total_shares += shares
                total_cost += investment
                all_investment += investment

                print(f"{current_date.strftime('%Y/%m/%d')}: Buy {shares} shares at {closing_price}, fair price: {fair_price}")
                target_collection.insert_one({
                    "id": rule_id,
                    "stock_code": stock_code,
                    "action": "buy",
                    "shares": shares,
                    "price_per_share": closing_price,
                    "total_investment": investment,
                    "transaction_value":all_investment,
                    "date": current_date.strftime('%Y/%m/%d'),
                    "remaining_funds": remaining_funds
                })

            elif closing_price > fair_price and total_shares > 0:
                total_value = total_shares * closing_price
                remaining_funds += total_value
                return_rate = (closing_price - (total_cost / total_shares)) / (total_cost / total_shares) * 100

                print(f"{current_date.strftime('%Y/%m/%d')}: Sell all shares at {closing_price}, fair price: {fair_price}")
                target_collection.insert_one({
                    "id": rule_id,
                    "stock_code": stock_code,
                    "action": "sell",
                    "shares": total_shares,
                    "price_per_share": closing_price,
                    "transaction_value":all_investment,
                    "total_value": total_value,
                    "return_rate": return_rate,
                    "date": current_date.strftime('%Y/%m/%d'),
                    "remaining_funds": remaining_funds
                })

                total_shares = 0
                total_cost = 0

        current_date += timedelta(days=1)

    if total_shares > 0:
        total_value = total_shares * closing_price
        return_rate = (total_value - total_cost) / total_cost * 100

        print(f"End of simulation: Holding {total_shares} shares worth {total_value}")
        target_collection.insert_one({
            "rule_id": rule_id,
            "stock_code": stock_code,
            "action": "hold",
            "shares": total_shares,
            "current_value": total_value,
            "transaction_value":all_investment,
            "return_rate": return_rate,
            "date": current_date.strftime('%Y/%m/%d'),
            "remaining_funds": remaining_funds
        })

    return remaining_funds, rule_id, return_rate

def main():
    all_rules = get_rules()
    total_funds = get_user_data()  # 讀取用戶初始資金

    investment_start = datetime(2022, 12, 31)
    investment_end = datetime(2023, 12, 31)

    remaining_funds = total_funds

    for rule in all_rules:
        rule_id = rule["id"]
        stock_code = rule["stock_code"]
        pe_ratio = rule["pe_ratio"]

        # 執行單條規則
        remaining_funds, _, return_rate = PE_strategy(
            investment_start, investment_end, rule_id, stock_code, pe_ratio, remaining_funds
        )

        # 插入該規則的最終資金與回報率
        target_collection1.insert_one({
            "id": rule_id,
            "record_type": "final_funds",
            "remaining_funds": remaining_funds,
            "return_rate": return_rate,
            "date": datetime.now().strftime('%Y/%m/%d')
        })
        print(f"Final remaining funds: {remaining_funds}, Rule ID: {rule_id}, Return rate: {return_rate}%")

if __name__ == "__main__":
    main()