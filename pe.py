import datetime
from pymongo import MongoClient
import json

# 連接 MongoDB，並獲取 PE 規則值
def get_user_pe():
    source_client = MongoClient("mongodb://localhost:27017/")
    source_db = source_client["myDatabase"]
    source_collection = source_db["rules"]
    
    query = {"strategy": "PE"}
    result = source_collection.find_one(query)
    
    if result and "value" in result:
        return float(result["value"])
    else:
        raise ValueError("未找到有效的 PE 策略或 PE 值缺失")


# 假設 EPS 資料 (按年度與季度)
eps_data = {
    2023: {  
        1: 2.5,  # 第一季
        4: 2.5,  # 第二季
        7: 3.0,  # 第三季
        10: 3.2  # 第四季
    },
    2024: {  
        1: 3.3,  # 第一季
        4: 3.5,  # 第二季
        7: 3.8,  # 第三季
        10: 4.0  # 第四季
    }
}

# 假市場股價資料
market_prices = {
    "2023-04-15": 140, 
    "2023-07-20": 95,   
    "2023-10-10": 125,
    "2024-01-05": 155
}

# 計算合理股價
def calculate_fair_price(eps, pe, current_date):
    month = current_date.month
    if 4 <= month <= 6:
        return eps * 4 * pe
    elif 7 <= month <= 9:
        return eps * 2 * pe
    elif 10 <= month <= 12:
        return (eps / 4) * 3 * pe
    else:
        return eps * pe

# 讀取初始資金和月投入金額
def load_initial_funds(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            total_assets = float(data.get("total_assets", 0))
            monthly_investment = float(data.get("monthly_investment", 0))
            return total_assets, monthly_investment
    except (FileNotFoundError, KeyError, ValueError) as e:
        raise ValueError("資金資料讀取錯誤或格式不正確")

# 模擬交易邏輯
def simulate_trading(market_prices, eps_data, json_path):
    total_assets, monthly_investment = load_initial_funds(json_path)
    shares_owned = 0
    
    user_pe = get_user_pe()
    
    for date, price in sorted(market_prices.items()):
        current_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        year, month = current_date.year, current_date.month
        
        # 根據月份選擇 EPS
        if month in [1, 2, 3]:  # 1 月到 3 月使用前一年 Q4 EPS
            eps = eps_data[year - 1][10]
        elif 4 <= month <= 6:
            eps = eps_data[year][1]  # Q1 EPS
        elif 7 <= month <= 9:
            eps = eps_data[year][4]  # Q2 EPS
        else:
            eps = eps_data[year][7]  # Q3 EPS
        
        # 每月投入資金邏輯
        if month == 1:
            total_assets += monthly_investment
        
        # 計算合理價
        fair_price = calculate_fair_price(eps, user_pe, current_date)
        
        # 買賣邏輯
        if price < fair_price and total_assets >= price:
            shares_bought = total_assets // price  # 買入整股數
            if shares_bought > 0:
                total_assets -= shares_bought * price
                shares_owned += shares_bought
                action = f"買入 {shares_bought} 股"
            else:
                action = "資金不足，未買入"
        elif price > fair_price and shares_owned > 0:
            total_assets += shares_owned * price  # 全部賣出
            action = f"賣出 {shares_owned} 股"
            shares_owned = 0
        else:
            action = "持有"
        
        # 打印當前狀態
        print(f"{date}: 市場價: {price}, 合理價: {fair_price:.2f}, 動作: {action}, 剩餘資金: {total_assets:.2f}, 持股: {shares_owned}")

# 執行模擬
simulate_trading(market_prices, eps_data, r"C:\Users\user\invest\local_data\user.json")