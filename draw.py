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

    for i, strategy_id in enumerate(valid_strategy_ids):
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
        
        # 格式化 y 軸數字
        ax[i].yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

        # 添加圖例
        ax[i].legend(loc='upper left')
        ax2.legend(loc='upper right')

    # 保存圖表
    plt.tight_layout()
    output_path = os.path.join(static_folder, "investment_and_shares.png")
    plt.savefig(output_path, dpi=300)
    plt.close(fig)

    ### 繪製 action + transaction_value 的柱狀圖（不同策略不同顏色） ###
    fig, ax = plt.subplots(figsize=(12, 6))

    # 定義顏色映射，並為買賣操作分配不同顏色
    color_map = plt.colormaps['tab10']
    strategy_colors = {strategy_id: color_map(i) for i, strategy_id in enumerate(valid_strategy_ids)}

    # 按策略分組繪製柱狀圖
    for strategy_id in valid_strategy_ids:
        strategy_data = data[data['id'] == strategy_id]

        # 分離買入和賣出資料
        buy_data = strategy_data[strategy_data['action'] == 'buy']
        sell_data = strategy_data[strategy_data['action'] == 'sell']

        # 繪製買入柱狀圖（較深顏色）
        ax.bar(buy_data['date'], buy_data['transaction_value'], color=strategy_colors[strategy_id], alpha=0.9, label=f'{strategy_id} - Buy', width=0.8)

        # 繪製賣出柱狀圖（增加顏色變化）
        sell_color = tuple(c * 0.6 for c in strategy_colors[strategy_id][:3])  # 降低亮度
        ax.bar(sell_data['date'], sell_data['transaction_value'], color=sell_color, alpha=0.9, label=f'{strategy_id} - Sell', width=0.8)

    # 添加標籤和標題
    ax.set_title('Transaction Value by Action and Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Transaction Value (NTD)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.grid(True)

    # 處理圖例：避免重複
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', title='Strategies')

    # 保存柱狀圖
    transaction_image_path = os.path.join(static_folder, 'action_transaction_price.png')
    plt.tight_layout()
    plt.savefig(transaction_image_path, dpi=300)
    plt.close(fig)

    print(f"交易價格柱狀圖已儲存至 {transaction_image_path}")
    ### 繪製 stock_price 折線圖 ###
    fig, ax = plt.subplots(figsize=(12, 6))

    for strategy_id in valid_strategy_ids:
        strategy_data = data[data['id'] == strategy_id]
        # 繪製 stock_price 折線圖
        ax.plot(strategy_data['date'], strategy_data['stock_price'], marker='o', linestyle='-', 
                label=f'Strategy {strategy_id} - Stock Price')

    # 添加標籤和標題
    ax.set_title('Stock Price by Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price (NTD)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.grid(True)

    # 保存折線圖
    stock_price_image_path = os.path.join(static_folder, 'stock_price.png')
    plt.tight_layout()
    plt.savefig(stock_price_image_path, dpi=300)
    plt.close(fig)

    print(f"股價折線圖已儲存至 {stock_price_image_path}")

    ### 繪製報酬率折線圖 ###
    fig, ax = plt.subplots(figsize=(12, 6))

    for strategy_id in valid_strategy_ids:
        strategy_data = data[data['id'] == strategy_id]
        # 繪製報酬率折線圖
        ax.plot(strategy_data['date'], strategy_data['return_rate'], marker='o', linestyle='-', 
                label=f'Strategy {strategy_id} - Return Rate')

    # 添加標籤和標題
    ax.set_title('Return Rate by Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Return Rate (%)')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
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
    delete_result = collection.delete_many({})
    print(f"已刪除 {delete_result.deleted_count} 筆資料")
