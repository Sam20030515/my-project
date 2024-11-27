from pymongo import MongoClient
import json

# 設定 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 替換為您的 MongoDB 連線 URI
db = client["stock"]  # 替換為您的資料庫名稱
collection = db["stock_record"]  # 替換為您的集合名稱

# 定義函數以從資料庫中提取當日股票資訊
def getStockInfo(date,stockID):
    
    # 查詢資料庫中符合日期和股票代號的文件
    stock_data = collection.find_one({"年月日": date, "證券代碼": {"$regex": f"^{stockID}"}})
    
    # 如果資料存在，格式化為 JSON；否則回傳 None
    if stock_data:
        result = {
            "日期": stock_data.get("年月日"),
            "最高價(元)": stock_data.get("最高價(元)"),
            "最低價(元)": stock_data.get("最低價(元)"),
            "收盤價(元)": stock_data.get("收盤價(元)")
        }
        return json.dumps(result, ensure_ascii=False, indent=4)
    else:
        return json.dumps({"error": "No data found for today."}, ensure_ascii=False, indent=4)

# 範例：取得指定股票代號的當日資訊
stock_info_json = getStockInfo("2024/04/01","2330")
print(stock_info_json)
