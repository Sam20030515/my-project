from getStockInfo import getStockInfo
import json
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB 連線設定 - 用來儲存投資記錄
target_client = MongoClient("mongodb://localhost:27017/")
target_db = target_client["investment_db"]
target_collection = target_db["investment_records"]

# MongoDB 連線設定 - 用來獲取股市資料
stock_client = MongoClient("mongodb://localhost:27017/")
db = stock_client["stock"]
collection = db["stock_record"]

# 獲取規則
def get_rules(id_filter=None):
    """從 MongoDB 獲取指定 id 的規則"""
    source_client = MongoClient("mongodb://localhost:27017/")
    source_db = source_client["myDatabase"]
    source_collection = source_db["rules"]

    # 根據 id 進行查詢，若 id_filter 為 None 則查詢所有
    query = {"id": id_filter} if id_filter else {}
    results = source_collection.find(query)

    rules = []
    for result in results:
        # 檢查是否存在 "date" 欄位
        if "date" not in result:
            print(f"跳過缺少 'date' 欄位的規則: {result}")
            continue  # 跳過此筆資料

        rule = {
            "id": result.get("id", ""),  # 加入 id 欄位
            "strategy": result.get("strategy", ""),  # 使用 get() 防止 KeyError
            "stock_code": result.get("stock_code", ""),
            "date": result["date"],
            "input_type": result.get("input_type", ""),
            "value": result.get("value", 0)
        }
        rules.append(rule)

    return rules


# 獲取最接近的收盤價
def get_closest_stock_price(current_date, stock_code):
    """根據指定的日期，尋找最接近的收盤價資料"""
    for delta in range(0, 30):  # 你可以調整這個範圍來查找多長時間的資料
        # 向前查找
        prev_date = current_date - timedelta(days=delta)
        stock_info_json = getStockInfo(prev_date.strftime("%Y/%m/%d"), stock_code)
        stock_info = json.loads(stock_info_json)

        # 若取得收盤價則返回
        if "收盤價(元)" in stock_info:
            print(f"取得 {stock_code} 在 {prev_date.strftime('%Y/%m/%d')} 的收盤價資料: {stock_info['收盤價(元)']} 元")
            return float(stock_info["收盤價(元)"])

        # 若未找到，繼續查找下一天
        if delta > 0:
            next_date = current_date + timedelta(days=delta)
            stock_info_json = getStockInfo(next_date.strftime("%Y/%m/%d"), stock_code)
            stock_info = json.loads(stock_info_json)

            if "收盤價(元)" in stock_info:
                print(f"取得 {stock_code} 在 {next_date.strftime('%Y/%m/%d')} 的收盤價資料: {stock_info['收盤價(元)']} 元")
                return float(stock_info["收盤價(元)"])

    print(f"無法在 {current_date.strftime('%Y/%m/%d')} 附近取得 {stock_code} 的收盤價資料")
    return None  # 如果完全找不到資料，返回 None


# 定期定額投資策略
def periodic_investment_to_db(start, end, day, input_type, value, stock_code, rule_id):
    current_date = start
    total_shares = 0
    total_investment = 0

    while current_date <= end:
        if current_date.day == day:
            stock_info_json = getStockInfo(current_date.strftime("%Y/%m/%d"), stock_code)
            stock_info = json.loads(stock_info_json)

            if "收盤價(元)" in stock_info:
                current_stock_price = float(stock_info["收盤價(元)"])
                print(f"在 {current_date.strftime('%Y/%m/%d')} 取得收盤價資料: {current_stock_price} 元")
            else:
                print(f"無法取得 {stock_code} 在 {current_date.strftime('%Y/%m/%d')} 的收盤價資料")
                current_stock_price = get_closest_stock_price(current_date, stock_code)
                if current_stock_price is None:
                    # 如果找不到接近的收盤價，跳過這一天
                    current_date = current_date.replace(month=current_date.month % 12 + 1, year=current_date.year + (current_date.month // 12))
                    continue  # 跳到下一月

            shares = value * 1000 if input_type == "count" else int(value / current_stock_price)
            total_shares += shares
            total_investment += value if input_type == "price" else current_stock_price * shares
            market_value = total_shares * current_stock_price
            return_rate = (market_value - total_investment) / total_investment * 100

            # 檢查是否已經存在這筆資料
            existing_record = target_collection.find_one({
                "date": current_date.strftime("%Y-%m-%d"),
                "stock_code": stock_code
            })

            if existing_record is None:
                # 如果不存在該記錄，插入資料
                record = {
                    "id": rule_id,  # 新增 rule_id
                    "date": current_date.strftime("%Y-%m-%d"),
                    "stock_code": stock_code,
                    "shares": total_shares,
                    "total_investment": total_investment,
                    "market_value": market_value,
                    "return_rate": return_rate
                }

                try:
                    target_collection.insert_one(record)
                    print("成功將記錄插入 MongoDB")
                except Exception as e:
                    print("將記錄插入 MongoDB 時發生錯誤:", e)
            else:
                print(f"已經存在 {current_date.strftime('%Y-%m-%d')} 的記錄，跳過插入。")

        # 更新至下個月相同日期
        next_month = current_date.month % 12 + 1
        next_year = current_date.year + (current_date.month // 12)

        try:
            current_date = current_date.replace(year=next_year, month=next_month, day=day)
        except ValueError:
            current_date = current_date.replace(year=next_year, month=next_month) + timedelta(days=31 - day)

    print("總持有股數:", total_shares)
    print("總投資金額:", total_investment)


# 其他策略 1
def strategy_1(start, end, stock_code):
    # 這裡可以寫自定義的投資策略邏輯
    print("執行策略 1")
    pass

# 其他策略 2
def strategy_2(start, end, stock_code):
    # 這裡可以寫自定義的投資策略邏輯
    print("執行策略 2")
    pass

# 主程式
def main():
    # 初始資金設定
    total_funds = 1000000  # 假設初始資金為 1,000,000 元

    # 取得所有規則
    all_rules = get_rules()
    print(f"獲取到的規則: {all_rules}")  # 查看是否獲得了規則

    # 假設我們設定了投資策略的執行範圍
    investment_start = datetime(2022, 12, 31)
    investment_end = datetime(2023, 12, 31)

    # 迴圈遍歷每個規則
    for rule in all_rules:
        print(f"處理規則: {rule}")  # 查看當前正在處理的規則
        # 獲取每個規則的相關參數
        stock_code = rule["stock_code"]
        investment_day = int(rule["date"])  # 投資日期
        input_type = rule["input_type"]
        investment_value = int(rule["value"])
        rule_id = rule["id"]  # 獲取規則的 id

        # 資金檢查
        if input_type == "price" and investment_value > total_funds:
            print(f"資金不足以執行規則 (股票代碼: {stock_code}, 投資金額: {investment_value} 元, 剩餘資金: {total_funds} 元)。跳過此規則。")
            continue
        elif input_type == "count":
            # 假設股票每股價格暫定為 100 元 (需要從資料庫獲取)
            approx_price_per_share = 100  
            estimated_cost = investment_value * 1000 * approx_price_per_share
            if estimated_cost > total_funds:
                print(f"資金不足以執行規則 (股票代碼: {stock_code}, 預估成本: {estimated_cost} 元, 剩餘資金: {total_funds} 元)。跳過此規則。")
                continue

        # 根據規則決定執行哪個策略
        if rule["strategy"] == "DCA":  # 假設這是你定期定額策略
            periodic_investment_to_db(investment_start, investment_end, investment_day, input_type, investment_value, stock_code, rule_id)
            if input_type == "price":
                total_funds -= investment_value
            else:
                total_funds -= estimated_cost
        elif rule["strategy"] == "strategy_1":
            strategy_1(investment_start, investment_end, stock_code)
        elif rule["strategy"] == "strategy_2":
            strategy_2(investment_start, investment_end, stock_code)

        print(f"執行完成後的剩餘資金: {total_funds} 元")


if __name__ == "__main__":
    main()
