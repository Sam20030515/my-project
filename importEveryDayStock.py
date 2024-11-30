import pandas as pd
from pymongo import MongoClient

# 設定 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")  # 替換為您的 MongoDB 連線 URI
db = client["stock"]  # 替換為您的資料庫名稱
collection = db["stock_record"]  # 替換為您的集合名稱

# 指定三個 Excel 檔案的路徑
excel_files = [
    r"C:\Users\allen\first-react\2023一月.xlsx",  # 檔案1
    r"C:\Users\allen\first-react\2023二月.xlsx",
    r"C:\Users\allen\first-react\2023三月.xlsx",
    r"C:\Users\allen\first-react\2023四月.xlsx",
    r"C:\Users\allen\first-react\2023五月.xlsx",
    r"C:\Users\allen\first-react\2023六月.xlsx",
    r"C:\Users\allen\first-react\2023七月.xlsx",
    r"C:\Users\allen\first-react\2023八月.xlsx",
    r"C:\Users\allen\first-react\2023九月.xlsx",
    r"C:\Users\allen\first-react\2023十月.xlsx",
    r"C:\Users\allen\first-react\2023十一月.xlsx",
    r"C:\Users\allen\first-react\2023十二月.xlsx"
]

# 定義欄位名稱對應字典
column_mapping = {
    'Unnamed: 0': '證券代碼',
    'Unnamed: 1': '年月日',
    'Unnamed: 2': '開盤價(元)',
    'Unnamed: 3': '最高價(元)',
    'Unnamed: 4': '最低價(元)',
    'Unnamed: 5': '收盤價(元)',
    'Unnamed: 6': '成交量(千股)',
    'Unnamed: 7': '成交值(千元)',
    'Unnamed: 8': '報酬率％',
    'Unnamed: 9': '週轉率％',
    'Unnamed: 10': '流通在外股數(千股)',
    'Unnamed: 11': '市值(百萬元)',
    'Unnamed: 12': '最後揭示買價',
    'Unnamed: 13': '最後揭示賣價',
    'Unnamed: 14': '報酬率-Ln',
    'Unnamed: 15': '市值比重％',
    'Unnamed: 16': '成交值比重％',
    'Unnamed: 17': '成交筆數(筆)',
    'Unnamed: 18': '本益比-TSE',
    'Unnamed: 19': '本益比-TEJ',
    'Unnamed: 20': '股價淨值比-TSE',
    'Unnamed: 21': '股價淨值比-TEJ'
}

# 處理每個 Excel 檔案
for excel_file in excel_files:
    # 讀取 Excel 檔案
    df = pd.read_excel(excel_file)
    
    # 使用 rename 方法替換欄位名稱
    df.rename(columns=column_mapping, inplace=True)
    
    # 將資料轉換為字典格式並插入 MongoDB
    data = df.to_dict(orient="records")
    collection.insert_many(data)
    
    print(f"{excel_file} 資料匯入完成")

print("所有檔案匯入完成")