from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# 建立 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")
db = client["investment_db"]
collection = db["investment_records"]

# 執行查詢
query = {}
results = collection.find(query, {"_id": 0, "date": 1, "total_investment": 1})

# 將查詢結果轉換為 Pandas DataFrame
data = pd.DataFrame(results)

# 將 'date' 欄位轉換為 datetime 格式
data['date'] = pd.to_datetime(data['date'])

# 按日期分組並計算每個日期的 total_investment 平均值
grouped_data = data.groupby('date', as_index=False).mean()

# 選取用於繪圖的欄位
x_data = grouped_data['date']
y_data = grouped_data['total_investment']

# 繪製折線圖，線段連接各點
plt.figure(figsize=(10, 6))
plt.plot(x_data, y_data, marker='o', linestyle='-', color='blue')  # 折線圖，藍色，連接點
plt.xlabel('Date')
plt.ylabel('Total Investment (NTD)')  # 假設單位為台幣

# 設定 y 軸範圍和格式
plt.ylim(min(y_data), max(y_data))
formatter = ticker.StrMethodFormatter('{x:,.2f}')
plt.gca().yaxis.set_major_formatter(formatter)

# 設定標題和顯示
plt.title('Fluctuation of Investment')
plt.grid(True)
plt.xticks(rotation=45)

# 確保 static 資料夾存在
static_folder = 'static'
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

# 儲存圖表到 static 資料夾
image_path = os.path.join(static_folder, 'investment_chart.png')
plt.savefig(image_path)

# 關閉圖表
plt.close()

print(f"圖表已儲存至 {image_path}")
