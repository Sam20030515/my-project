from pymongo import MongoClient
import json

# 設定 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 替換為您的 MongoDB 連線 URI
db = client["stock"]  # 替換為您的資料庫名稱
collection1 = db["stock_record"]  # 替換為您的股票資料集合名稱

# 定義函數：DCA 和 StopLossTakeProfit 策略
def get_stock_data(date, stock_code):
    stock_data = collection1.find_one({"年月日": date, "證券代碼": {"$regex": f"^{stock_code}"}})
    if stock_data:
        result = {
            "日期": stock_data.get("年月日"),
            "最高價(元)": stock_data.get("最高價(元)"),
            "最低價(元)": stock_data.get("最低價(元)"),
            "收盤價(元)": stock_data.get("收盤價(元)")
        }
        return json.dumps(result, ensure_ascii=False, indent=4)
    else:
        return json.dumps({"error": "No stock data found for the given date and stock ID."}, ensure_ascii=False, indent=4)

# 定義函數：PE 策略
def get_stock_and_eps_data(date, stock_code):
    """
    Fetch the stock closing price for a given date and stock ID, and merge it with EPS data.

    Args:
        date (str): The target date in the format 'YYYY/MM/DD'.
        stockID (str): The stock ID to query.

    Returns:
        dict: A JSON object combining the stock closing price and EPS data.
    """
    # Connect to MongoDB
    eps_collection = db["eps_record"]  # EPS 資料集合

    # 查詢股票資料
    stock_data = collection1.find_one(
        {"年月日": date, "證券代碼": {"$regex": f"^{stock_code}"}},
        {"_id": 0, "證券代碼": 1, "收盤價(元)": 1}
    )
    if not stock_data:
        return {"error": f"No stock data found for date: {date} and stock ID: {stock_code}"}

    # 查詢 EPS 資料
    eps_data = eps_collection.find_one(
        {"證券代碼": {"$regex": f"^{stock_code}"}},
        {"_id": 0, "證券代碼": 1, "q1": 1, "q2": 1, "q3": 1, "q4": 1}
    )
    if not eps_data:
        return {"error": f"No EPS data found for stock ID: {stock_code}"}

    # 整合股票與 EPS 資料
    result = {
        "date": date,
        "code": stock_data.get("證券代碼"),
        "closing_price": stock_data.get("收盤價(元)"),
        "eps_records": {
            "company_name": eps_data.get("證券代碼"),
            "q1": eps_data.get("q1"),
            "q2": eps_data.get("q2"),
            "q3": eps_data.get("q3"),
            "q4": eps_data.get("q4")
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=4)

# 整合主函數
def getStockInfo(strategy, date, stock_code):
    if strategy in ["DCA", "StopLossTakeProfit"]:
        return get_stock_data(date, stock_code)
    elif strategy == "PE":
        return get_stock_and_eps_data(date, stock_code)
    else:
        return json.dumps({"error": "Unsupported strategy."}, ensure_ascii=False, indent=4)

# 測試
# strategy = "DCA"
# date = "2023/01/03"
# stock_code = "2330"
# result = getStockInfo(strategy, date, stock_code)
# print(result)
