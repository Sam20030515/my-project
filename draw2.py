from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os

# 連接 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["investment_records"]
collection = db["trade_records"]

# 查詢資料
data = pd.DataFrame(list(collection.find({}, {
    "_id": 0, "date": 1, "stock_code": 1, "action": 1, "shares": 1,
    "price_per_share": 1, "total_investment": 1, "return_rate": 1,
    "remaining_funds": 1, "remaining_shares": 1
})))

# 確認資料是否存在
if data.empty:
    print("查詢結果為空。")
else:
    data['date'] = pd.to_datetime(data['date'])

    # 繪製每股價格與投資趨勢
    unique_stocks = data['stock_code'].unique()
    for stock_code in unique_stocks:
        stock_data = data[data['stock_code'] == stock_code]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(stock_data['date'], stock_data['price_per_share'], marker='o', linestyle='-', label='Price per Share')

        # 標註買入（Buy）與賣出（Sell）點
        buy_data = stock_data[stock_data['action'] == 'buy']
        sell_data = stock_data[stock_data['action'] == 'sell']

        ax.scatter(buy_data['date'], buy_data['price_per_share'], color='green', label='Buy', zorder=5)
        ax.scatter(sell_data['date'], sell_data['price_per_share'], color='red', label='Sell', zorder=5)

        # 添加標題與圖例
        ax.set_title(f'Stock {stock_code} - Price Trend with Actions')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price per Share')
        ax.legend(loc='upper left')
        plt.grid(True)
        plt.tight_layout()

        # 保存圖表
        plt.savefig(f'static/price_trend_{stock_code}.png')
        plt.close()

    print("所有圖表已生成並儲存至 static 資料夾。")
