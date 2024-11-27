from pymongo import MongoClient

# MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 替換為您的 MongoDB 連線 URI
db = client["stock"]  # 替換為您的資料庫名稱
source_collection = db["eps_recordd"]  # 原始集合
target_collection = db["eps_record"]  # 整理後的集合名稱

# 聚合管道
pipeline = [
    {
        "$group": {
            "_id": "$證券代碼",  # 按公司名稱分組
            "data": {
                "$mergeObjects": "$$ROOT"  # 將每一筆資料合併
            }
        }
    },
    {
        "$replaceRoot": {
            "newRoot": {
                "$mergeObjects": ["$data", {"證券代碼": "$_id"}]  # 更新結構並保留公司名稱
            }
        }
    },
    {
        "$project": {
            "_id": 0  # 去除 _id 欄位
        }
    }
]

# 執行聚合
result = list(source_collection.aggregate(pipeline))

# 將結果插入新的集合
if result:
    target_collection.delete_many({})  # 清空目標集合（可選）
    target_collection.insert_many(result)
    print(f"已成功插入 {len(result)} 筆整合資料到集合 'eps_consolidated'")
else:
    print("沒有找到可以整合的資料。")
