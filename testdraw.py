import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import random
import os
from datetime import datetime, timedelta

# 定義 JSON 模擬資料
mock_data_json = []

# 模擬 3 個策略，每個策略 10 天的數據
for strategy_id in range(1, 4):
    for i in range(10):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        return_rate = round(random.uniform(-10, 20), 2)  # 隨機回報率 (-10% ~ 20%)
        stock_code = f"STOCK{strategy_id}"  # 模擬股票代碼
        shares = random.randint(10, 100)  # 隨機股票數量
        stock_price = round(random.uniform(50, 150), 2)  # 隨機股票價格
        total_investment = round(stock_price * shares, 2)  # 計算總投資
        action = random.choice(["buy", "sell"])  # 隨機買賣行為
        transaction_price = round(stock_price * random.uniform(0.9, 1.1), 2)  # 當下股價波動

        mock_data_json.append({
            "id": strategy_id,
            "date": date,
            "return_rate": return_rate,
            "stock_code": stock_code,
            "shares": shares,
            "total_investment": total_investment,
            "stock_price": stock_price,
            "action": action,
            "transaction_price": transaction_price
        })

# 將 JSON 轉換為 DataFrame
data = pd.DataFrame(mock_data_json)
data['date'] = pd.to_datetime(data['date'])

# 確保 static 資料夾存在
static_folder = 'static'
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

# 繪製每個策略的 total_investment 和 shares 圖表
fig, ax = plt.subplots(3, 1, figsize=(12, 15), sharex=True)

for i, strategy_id in enumerate(data['id'].unique()):
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
    
    # 添加圖例
    ax[i].legend(loc='upper left')
    ax2.legend(loc='upper right')

# 保存 total_investment 圖表
investment_image_path = os.path.join(static_folder, 'investment_and_shares.png')
plt.savefig(investment_image_path, dpi=300)

# 繪製 stock_price 和 current_price 的圖表
fig, ax1 = plt.subplots(figsize=(12, 6))

for strategy_id in data['id'].unique():
    strategy_data = data[data['id'] == strategy_id]
    
    # 繪製 stock_price
    ax1.plot(strategy_data['date'], strategy_data['stock_price'], marker='o', linestyle='-', label=f'Strategy {strategy_id} - Stock Price')
    
    # 繪製 transaction_price
    ax1.plot(strategy_data['date'], strategy_data['transaction_price'], marker='x', linestyle='--', label=f'Strategy {strategy_id} - transaction Price')

    # 標記買賣行為
    for j, row in strategy_data.iterrows():
        if row['action'] == 'buy':
            ax1.scatter(row['date'], row['stock_price'], color='green', s=50, label='Buy' if j == 0 else "")
        else:
            ax1.scatter(row['date'], row['stock_price'], color='red', s=50, label='Sell' if j == 0 else "")

# 添加標籤和標題
ax1.set_title('Stock Price and Transaction Price with Buy/Sell Actions')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (NTD)')
ax1.legend()

# 格式化 x 軸日期
plt.xticks(rotation=45)
plt.grid(True)

# 保存 stock_price 圖表
price_image_path = os.path.join(static_folder, 'stock_and_transaction_price.png')
plt.savefig(price_image_path, dpi=300)

print(f"投資圖表已儲存至 {investment_image_path}")
print(f"股價圖表已儲存至 {price_image_path}")
