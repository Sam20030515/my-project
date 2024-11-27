from getStockInfo import getStockInfo
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
# MongoDB 連線設定 - 用來儲存投資記錄
target_client = MongoClient("mongodb://localhost:27017/")
target_db = target_client["investment_records"]
target_collection = target_db["trade_records"]

def StopLossTakeProfit(start, end, stock_code, buy_value, stop_loss_percent, take_profit_percent):
    current_date = start
    total_shares = 0  # Total shares
    total_investment = 0  # Total investment amount
    buy_price = 0  # Buy price
    total_value = 0  # Total value of the stocks

    while current_date <= end:
        stock_info_json = getStockInfo(current_date.strftime("%Y/%m/%d"), stock_code)
        stock_info = json.loads(stock_info_json)

        if "收盤價(元)" in stock_info:
            current_stock_price = float(stock_info["收盤價(元)"])
        else:
            current_date += timedelta(days=1)
            continue

        if total_shares == 0:
            # Buy shares only if no stocks are currently owned
            shares = int(buy_value / current_stock_price)
            if shares > 0:
                total_shares += shares
                total_investment += buy_value
                buy_price = current_stock_price
                print(f"在 {current_date.strftime('%Y/%m/%d')} 買入 {shares} 股，買入價格: {buy_price} 元")
                trade_record = {
                    "stock_code": stock_code,
                    "action": "buy",
                    "shares": shares,
                    "price_per_share": buy_price,
                    "total_investment": buy_value,
                    "date": current_date.strftime('%Y/%m/%d'),
                }
                target_collection.insert_one(trade_record)
            else:
                print(f"資金不足以買入任何股票，跳過此日期：{current_date.strftime('%Y/%m/%d')}")
                current_date += timedelta(days=1)
                continue

        # Calculate total value of stocks, stop loss and take profit prices
        total_value = total_shares * current_stock_price
        stop_loss_price = buy_price * (1 - stop_loss_percent / 100)
        take_profit_price = buy_price * (1 + take_profit_percent / 100)

        # Trigger stop loss or take profit
        if current_stock_price <= stop_loss_price:
            print(f"停損觸發: 在 {current_date.strftime('%Y/%m/%d')} 賣出所有 {total_shares} 股，價格: {current_stock_price} 元")
            return_rate = (current_stock_price - buy_price) / buy_price * 100
            print(f"總回報率: {return_rate}%")
            trade_record = {
                "stock_code": stock_code,
                "action": "sell",
                "shares": total_shares,
                "price_per_share": current_stock_price,
                "total_value": total_value,
                "return_rate": return_rate,
                "date": current_date.strftime('%Y/%m/%d'),
            }
            target_collection.insert_one(trade_record)

            # Reset variables and prepare for next round
            total_shares = 0
            total_investment = 0
            buy_price = 0
            current_date += timedelta(days=1)
            print(f"準備開始下一輪交易\n")

        elif current_stock_price >= take_profit_price:
            print(f"停利觸發: 在 {current_date.strftime('%Y/%m/%d')} 賣出所有 {total_shares} 股，價格: {current_stock_price} 元")
            return_rate = (current_stock_price - buy_price) / buy_price * 100
            print(f"總回報率: {return_rate}%")
            trade_record = {
                "stock_code": stock_code,
                "action": "sell",
                "shares": total_shares,
                "price_per_share": current_stock_price,
                "total_value": total_value,
                "return_rate": return_rate,
                "date": current_date.strftime('%Y/%m/%d'),
            }
            target_collection.insert_one(trade_record)

            # Reset variables and prepare for next round
            total_shares = 0
            total_investment = 0
            buy_price = 0
            current_date += timedelta(days=1)
            print(f"準備開始下一輪交易\n")

        current_date += timedelta(days=1)

    # If the position is still open at the end of the period, return the final value and rate of return
    if total_shares > 0:
        return_rate = (total_value - total_investment) / total_investment * 100
        print(f"在 {current_date.strftime('%Y/%m/%d')} 最終回報率: {return_rate}%")
        trade_record = {
            "stock_code": stock_code,
            "action": "hold",
            "shares": total_shares,
            "current_value": total_value,
            "return_rate": return_rate,
            "date": current_date.strftime('%Y/%m/%d'),
        }
        target_collection.insert_one(trade_record)

    return None

# 示範使用停損停利策略
def main():
    stock_code = "2330"  # 台積電
    investment_start = datetime(2022, 12, 31)  # 開始投資日期
    investment_end = datetime(2023, 12, 31)  # 結束投資日期
    buy_value = 100000  # 每次投資金額
    stop_loss_percent = 5  # 停損 5%
    take_profit_percent = 10  # 停利 10%

    StopLossTakeProfit(investment_start, investment_end, stock_code, buy_value, stop_loss_percent, take_profit_percent)

if __name__ == "__main__":
    main()