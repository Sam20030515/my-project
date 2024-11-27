from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# 建立 MongoDB 連線
client = MongoClient("mongodb://localhost:27017/")
db = client["investment_db"]
collection = db["investment_records"]

try:
    # 執行查詢並轉換為 DataFrame
    query = {}
    results = collection.find(query, {"_id": 0, "id": 1, "date": 1, "action": 1, "shares": 1, "total_investment": 1, "return_rate": 1, "stock_price": 1, "transaction_value": 1})
    
    # 將查詢結果轉換為 DataFrame
    data = pd.DataFrame(results)
    
    # 檢查資料是否為空
    if data.empty:
        raise ValueError("查詢結果為空，請確認資料庫中是否有數據。")

    # 將 date 轉換為 datetime 格式
    data['date'] = pd.to_datetime(data['date'])

    # 確保 static 資料夾存在
    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

    # 獲取唯一策略數量
    strategy_ids = data['id'].unique()

    # 動態生成子圖數量
    fig, ax = plt.subplots(len(strategy_ids), 1, figsize=(12, 15), sharex=True)

    for i, strategy_id in enumerate(strategy_ids):
        strategy_data = data[data['id'] == strategy_id]
        
        # 繪製 total_investment
        ax[i].plot(strategy_data['date'], strategy_data['total_investment'], marker='o', linestyle='-', color='blue', label='Total Investment')
        
        # 繪製 shares
        ax2 = ax[i].twinx()
        ax2.plot(strategy_data['date'], strategy_data['shares'], marker='x', linestyle='--', color='green', label='Shares')
        
        # 添加標籤和標題
        ax[i].set_title(f'Strategy {strategy_id}: Total Investment and Shares')
        ax[i].set_ylabel('Total Investment (NTD)', color='blue')
        ax2.set_ylabel('Shares', color='green')
        ax[i].tick_params(axis='y', labelcolor='blue')
        ax2.tick_params(axis='y', labelcolor='green')
        
        # 格式化 y 軸數字，將 total_investment 顯示為千分位
        ax[i].yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))  # 千分位格式

        # 添加圖例
        ax[i].legend(loc='upper left')
        ax2.legend(loc='upper right')

    # 保存圖表
    plt.tight_layout()
    output_path = os.path.join(static_folder, "investment_and_shares.png")
    plt.savefig(output_path, dpi=300)
    plt.close(fig)  # 關閉圖表以釋放記憶體

    ### 繪製 action + transaction_value 的柱狀圖（不同策略不同顏色） ###
    fig, ax = plt.subplots(figsize=(12, 6))

    # 定義顏色列表，每個策略分配一個顏色
    color_map = plt.cm.get_cmap('tab10')  # 使用 matplotlib 的顏色映射
    strategy_colors = {strategy_id: color_map(i) for i, strategy_id in enumerate(data['id'].unique())}

    # 按 id 分組，為每個策略繪製柱狀圖
    for strategy_id, color in strategy_colors.items():
        strategy_data = data[data['id'] == strategy_id]

        # 繪製柱狀圖：買入為深色，賣出為淺色
        colors = strategy_data['action'].apply(lambda x: color if x == 'buy' else (color[0], color[1], color[2], 0.4))  # 淺化顏色
        ax.bar(strategy_data['date'], strategy_data['transaction_value'], color=colors, width=1, label=f'Strategy {strategy_id}')

    # 添加標籤和標題
    ax.set_title('Transaction Price by Action and Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Transaction Price (NTD)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))  # 格式化日期
    plt.xticks(rotation=45)
    plt.grid(True)

    # 添加圖例
    plt.legend(loc='upper left', title='Strategies')

    # 保存柱狀圖
    transaction_image_path = os.path.join(static_folder, 'action_transaction_price.png')
    plt.tight_layout()
    plt.savefig(transaction_image_path, dpi=300)
    plt.close(fig)

    print(f"交易價格柱狀圖已儲存至 {transaction_image_path}")

    ### 繪製 stock_price 折線圖 ###
    fig, ax = plt.subplots(figsize=(12, 6))

    for strategy_id in data['id'].unique():
        strategy_data = data[data['id'] == strategy_id]

        # 繪製 stock_price 折線圖
        ax.plot(strategy_data['date'], strategy_data['stock_price'], marker='o', linestyle='-', 
                label=f'Strategy {strategy_id} - Stock Price')

    # 添加標籤和標題
    ax.set_title('Stock Price by Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price (NTD)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))  # 格式化日期
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.grid(True)

    # 保存折線圖
    stock_price_image_path = os.path.join(static_folder, 'stock_price.png')
    plt.tight_layout()
    plt.savefig(stock_price_image_path, dpi=300)
    plt.close(fig)

    # print(f"投資圖表已儲存至 {investment_image_path}")
    print(f"交易價格柱狀圖已儲存至 {transaction_image_path}")
    print(f"股價折線圖已儲存至 {stock_price_image_path}")

    ### 繪製報酬率折線圖 ###
    fig, ax = plt.subplots(figsize=(12, 6))

    for strategy_id in data['id'].unique():
        strategy_data = data[data['id'] == strategy_id]

        # 繪製報酬率折線圖
        ax.plot(strategy_data['date'], strategy_data['return_rate'], marker='o', linestyle='-', 
                label=f'Strategy {strategy_id} - Return Rate')

    # 添加標籤和標題
    ax.set_title('Return Rate by Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Return Rate (%)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))  # 格式化日期
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.grid(True)

    # 保存報酬率折線圖
    return_rate_image_path = os.path.join(static_folder, 'return_rate.png')
    plt.tight_layout()
    plt.savefig(return_rate_image_path, dpi=300)
    plt.close(fig)

    print(f"報酬率折線圖已儲存至 {return_rate_image_path}")

finally:
    # 注意：清空資料庫操作應謹慎，通常在測試時使用！
    delete_result = collection.delete_many({})
    print(f"已刪除 {delete_result.deleted_count} 筆資料")
