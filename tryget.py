from pymongo import MongoClient

# 設定 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 替換為您的 MongoDB 連線 URI
db = client["stock"]  # 替換為您的資料庫名稱
collection = db["eps_recordd"]  # 替換為您的集合名稱

# 定義查詢條件
company_name = "2059"  # 公司代碼
quarter = "q3"  # 欲查詢的季度欄位

# 使用正則表達式找到公司名稱以 "2313" 開頭的資料，且該筆記錄包含指定季度的欄位
query = {
    "公司名稱": {"$regex": f"^{company_name}"},  # 匹配公司名稱
    quarter: {"$exists": True}  # 該筆資料需包含指定季度的欄位
}

# 查詢資料
result = collection.find_one(query, {"_id": 0, "公司名稱": 1, quarter: 1})  # 投影只取公司名稱與指定季度

# 顯示結果
if result:
    print(f"{result['公司名稱']} 的 {quarter.upper()} EPS 值為: {result[quarter]}")
else:
    print(f"找不到 {company_name} 的 {quarter.upper()} EPS 資料")
