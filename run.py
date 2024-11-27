import subprocess
from pymongo import MongoClient

# MongoDB 連線設定
client = MongoClient("mongodb://localhost:27017/")
db = client["myDatabase"]
rules_collection = db["rules"]

# 從資料庫獲取所有規則
def get_rules():
    return list(rules_collection.find())

# 執行外部策略檔案（直接在主目錄）
def execute_strategy(strategy_name, rule):
    try:
        # 將規則內容傳遞給策略腳本
        subprocess.run(["python", f"{strategy_name}.py", str(rule)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"執行策略 '{strategy_name}' 時發生錯誤: {e}")
    except FileNotFoundError:
        print(f"策略檔案 '{strategy_name}.py' 不存在！")

# 主程式
def main():
    rules = get_rules()  # 取得所有規則
    valid_strategies = ["DCA", "StopLossTakeProfit", "strategy3"]  # 合法策略清單
    
    for rule in rules:
        strategy_name = rule.get("strategy")
        if strategy_name in valid_strategies:
            print(f"執行策略: {strategy_name}")
            execute_strategy(strategy_name, rule)
        else:
            print(f"未知或未支援的策略: {strategy_name}")

if __name__ == "__main__":
    main()