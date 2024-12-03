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
    results = collection.find(query, {
        "_id": 0, "id": 1, "date": 1, "action": 1, "shares": 1,
        "total_investment": 1, "return_rate": 1, "stock_price": 1, "transaction_value": 1
    })
    
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

    # 獲取唯一策略數量，過濾無效策略
    strategy_ids = data['id'].unique()
    valid_strategy_ids = [strategy_id for strategy_id in strategy_ids if not data[data['id'] == strategy_id].empty]

    # 動態生成子圖數量（僅繪製有效策略）
    fig, ax = plt.subplots(len(valid_strategy_ids), 1, figsize=(12, 5 * len(valid_strategy_ids)), sharex=True)

    # 如果只有一個策略，將 ax 轉換為列表
    if len(valid_strategy_ids) == 1:
        ax = [ax]

    # 繪製每個策略的柱狀圖
    bar_width = 0.6  # 減小柱狀圖的寬度
    for i, strategy_id in enumerate(valid_strategy_ids):
        strategy_data = data[data['id'] == strategy_id]
        
        # 分離買入和賣出資料
        buy_data = strategy_data[strategy_data['action'] == 'buy']
        sell_data = strategy_data[strategy_data['action'] == 'sell']

        # 繪製買入柱狀圖
        ax[i].bar(buy_data['date'] - pd.Timedelta(days=1), buy_data['transaction_value'], color='blue', alpha=0.9, label='Buy', width=bar_width)
        
        # 繪製賣出柱狀圖
        ax[i].bar(sell_data['date'] + pd.Timedelta(days=1), sell_data['transaction_value'], color='red', alpha=0.9, label='Sell', width=bar_width)

        # 添加標籤（在每個柱狀圖上方顯示數值）
        for bar in ax[i].patches:
            height = bar.get_height()
            if height > 0:
                ax[i].annotate(f'{height:,.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 5),  # 垂直偏移值，避免與柱子重疊
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)

        # 設置標題和軸標籤
        ax[i].set_title(f'Transaction Value by Action - Strategy {strategy_id}')
        ax[i].set_xlabel('Date')
        ax[i].set_ylabel('Transaction Value (NTD)')
        ax[i].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        ax[i].tick_params(axis='x', rotation=45)
        ax[i].grid(True)
        ax[i].legend(loc='upper left')

    # 儲存整個策略的交易價值柱狀圖
    transaction_image_path = os.path.join(static_folder, 'action_transaction_price.png')
    plt.tight_layout()
    plt.savefig(transaction_image_path, dpi=300)
    plt.close(fig)

    print(f"交易價格柱狀圖已儲存至 {transaction_image_path}")

    # 其他圖表繪製 (保留原有邏輯)
    # 繪製股價折線圖  
    fig, ax = plt.subplots(figsize=(12, 6))
    for strategy_id in valid_strategy_ids:
        strategy_data = data[data['id'] == strategy_id]
        ax.plot(strategy_data['date'], strategy_data['stock_price'], marker='o', linestyle='-', 
                label=f'Strategy {strategy_id} - Stock Price')

    ax.set_title('Stock Price by Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price (NTD)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.grid(True)

    stock_price_image_path = os.path.join(static_folder, 'stock_price.png')
    plt.tight_layout()
    plt.savefig(stock_price_image_path, dpi=300)
    plt.close(fig)
    print(f"股價折線圖已儲存至 {stock_price_image_path}")

    # 繪製報酬率折線圖  
    fig, ax = plt.subplots(figsize=(12, 6))
    for strategy_id in valid_strategy_ids:
        strategy_data = data[data['id'] == strategy_id]
        ax.plot(strategy_data['date'], strategy_data['return_rate'], marker='o', linestyle='-', 
                label=f'Strategy {strategy_id} - Return Rate')

    ax.set_title('Return Rate by Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Return Rate (%)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.grid(True)

    return_rate_image_path = os.path.join(static_folder, 'return_rate.png')
    plt.tight_layout()
    plt.savefig(return_rate_image_path, dpi=300)
    plt.close(fig)
    print(f"報酬率折線圖已儲存至 {return_rate_image_path}")

finally:
    delete_result = collection.delete_many({})
    print(f"已刪除 {delete_result.deleted_count} 筆資料")
