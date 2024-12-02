
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
import pymongo

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

