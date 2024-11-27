import pandas as pd
from pymongo import MongoClient

# 設定 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 替換為您的 MongoDB 連線 URI
db = client["stock"]  # 替換為您的資料庫名稱
collection = db["eps_recordd"]  # 替換為您的集合名稱

# 指定三個 Excel 檔案的路徑
excel_files = [
    r"C:\Users\allen\OneDrive\文件\2022 Q4.xlsx",
    r"C:\Users\allen\OneDrive\文件\2023 Q1.xlsx",
    r"C:\Users\allen\OneDrive\文件\2023 Q2.xlsx",
    r"C:\Users\allen\OneDrive\文件\2023 Q3.xlsx"
]

# 定義欄位名稱對應字典
column_mapping = {
    'Unnamed: 0': '公司名稱',
    'Unnamed: 1': 'Q1',
    'Unnamed: 2': 'Q2',
    'Unnamed: 3': 'Q3',
    'Unnamed: 4': 'Q4'
}

# 處理每個 Excel 檔案
for excel_file in excel_files:
    # 讀取 Excel 檔案
    df = pd.read_excel(excel_file)
    
    # 使用 rename 方法替換欄位名稱
    # df.rename(columns=column_mapping, inplace=True)
    
    # 將資料轉換為字典格式並插入 MongoDB
    data = df.to_dict(orient="records")
    collection.insert_many(data)
    
    print(f"{excel_file} 資料匯入完成")

print("所有檔案匯入完成")