from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
import subprocess
import os
import json

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

# 初始化 n 變數，用來追蹤手動生成的 'id' 值
def initialize_n():
    global n
    last_rule = mongo.db.rules.find().sort("id", -1).limit(1)
    last_rule_list = list(last_rule)
    n = last_rule_list[0]['id'] if last_rule_list else 0

initialize_n()

# 路由：獲取所有規則
@app.route('/rules', methods=['GET'])
def get_rules():
    try:
        rules_cursor = mongo.db.rules.find()
        result = []
        for rule in rules_cursor:
            result.append({
                '_id': str(rule['_id']),
                'id': rule['id'],
                'strategy': rule['strategy'],
                'date': rule.get('date'),
                'input_type': rule.get('input_type'),
                'stock_code': rule['stock_code'],
                'value': rule['value']
})

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 路由：新增規則
@app.route('/rule', methods=['POST'])
def add_rule():
    global n
    strategy = request.json.get('strategy')
    stock_code = request.json.get('stock_code')
    date = request.json.get('date')
    input_type = request.json.get('input_type')
    value = request.json.get('value')
    
    # 每次新增規則時增加 n 的值
    n += 1

    # 根據策略決定資料格式
    rule = {
        'id': n,
        'strategy': strategy,
        'stock_code': stock_code
    }
    if strategy == "DCA":
        rule.update({
            'date': date,
            'input_type': input_type,
            'value': value
        })
    elif strategy == "StopLossTakeProfit":
        rule['value'] = {
        'stopLoss': value.get('stopLoss'),
        'takeProfit': value.get('takeProfit'),
        'everyBuy': value.get('everyBuy')  # 新增處理每次買入金額
    }

    elif strategy in ["PE", "TargetPrice"]:
        rule['value'] = value

    try:
        rule_id = mongo.db.rules.insert_one(rule).inserted_id
        return jsonify({
            '_id': str(rule_id),
            'id': n,
            'strategy': strategy,
            'date': date,
            'input_type': input_type,
            'stock_code': stock_code,
            'value': rule['value']
        }), 201
    except Exception as e:
        return jsonify({'error': f'新增規則失敗: {str(e)}'}), 500

# 路由：更新規則
@app.route('/rules/<int:id>', methods=['PUT'])
def update_rule(id):
    strategy = request.json.get('strategy')
    stock_code = request.json.get('stock_code')
    date = request.json.get('date')
    input_type = request.json.get('input_type')
    value = request.json.get('value')

    # 根據策略設定更新資料
    update_data = {
        'strategy': strategy,
        'stock_code': stock_code
    }

    if strategy == "DCA":
        update_data.update({
            'date': date,
            'input_type': input_type,
            'value': value
        })
    elif strategy == "StopLossTakeProfit":
        update_data['value'] = {
        'stopLoss': value.get('stopLoss'),
        'takeProfit': value.get('takeProfit'),
        'everyBuy': value.get('everyBuy')  # 新增處理每次買入金額
    }

    elif strategy in ["PE", "TargetPrice"]:
        update_data['value'] = value

    try:
        result = mongo.db.rules.update_one({'id': id}, {'$set': update_data})
        if result.modified_count > 0:
            return jsonify({'message': '規則已更新'})
        else:
            return jsonify({'error': '找不到規則或無變更'}), 404
    except Exception as e:
        return jsonify({'error': f'更新規則失敗: {str(e)}'}), 500

# 路由：刪除規則
@app.route('/rules/<int:id>', methods=['DELETE'])
def delete_rule(id):
    result = mongo.db.rules.delete_one({'id': id})
    if result.deleted_count > 0:
        return jsonify({'message': '規則已刪除'})
    else:
        return jsonify({'error': '找不到規則'}), 404

# 初始化使用者的 id
def initialize_user_id():
    global user_id
    last_user = mongo.db.users.find().sort("id", -1).limit(1)
    last_user_list = list(last_user)
    user_id = last_user_list[0]['id'] if last_user_list else 0

initialize_user_id()

# 路由：獲取所有使用者
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users_cursor = mongo.db.users.find()
        result = []
        for user in users_cursor:
            result.append({
                '_id': str(user['_id']),
                'id': user['id'],
                'username': user['username'],
                'total_assets': user['total_assets'],
                'monthly_investment': user['monthly_investment']
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 路由：新增使用者
@app.route('/users', methods=['POST'])
def add_user():
    global user_id
    username = request.json.get('username')
    total_assets = request.json.get('total_assets')
    monthly_investment = request.json.get('monthly_investment')

    # 每次新增使用者時增加 user_id 的值
    user_id += 1

    user = {
        'id': user_id,
        'username': username,
        'total_assets': total_assets,
        'monthly_investment': monthly_investment
    }

    try:
        user_id_inserted = mongo.db.users.insert_one(user).inserted_id
        return jsonify({
            '_id': str(user_id_inserted),
            'id': user_id,
            'username': username,
            'total_assets': total_assets,
            'monthly_investment': monthly_investment
        }), 201
    except Exception as e:
        return jsonify({'error': f'新增使用者失敗: {str(e)}'}), 500

# 路由：更新使用者
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    username = request.json.get('username')
    total_assets = request.json.get('total_assets')
    monthly_investment = request.json.get('monthly_investment')

    update_data = {
        'username': username,
        'total_assets': total_assets,
        'monthly_investment': monthly_investment
    }

    try:
        result = mongo.db.users.update_one({'id': id}, {'$set': update_data})
        if result.modified_count > 0:
            return jsonify({'message': '使用者已更新'})
        else:
            return jsonify({'error': '找不到使用者或無變更'}), 404
    except Exception as e:
        return jsonify({'error': f'更新使用者失敗: {str(e)}'}), 500

# 路由：刪除使用者
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    result = mongo.db.users.delete_one({'id': id})
    if result.deleted_count > 0:
        return jsonify({'message': '使用者已刪除'})
    else:
        return jsonify({'error': '找不到使用者'}), 404


# 路由：將選擇的使用者存入本地檔案
@app.route('/save_user', methods=['POST'])
def save_user():
    user_data = request.json  # 從請求中獲取使用者資料
    try:
        # 定義本地檔案路徑
        file_path = os.path.join("local_data", f"user.json")

        # 確保資料夾存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 將資料寫入 JSON 檔案
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)

        return jsonify({'message': f"使用者資料已儲存至 {file_path}"}), 200
    except Exception as e:
        return jsonify({'error': f'儲存使用者資料失敗: {str(e)}'}), 500

@app.route('/run_script', methods=['POST'])
def run_script():
    try:
        # 執行 run.py 腳本
        subprocess.run(['python', 'run.py'], check=True)
        return jsonify({'message': '腳本執行成功！'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'腳本執行失敗: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'發生未知錯誤: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(debug=True)
