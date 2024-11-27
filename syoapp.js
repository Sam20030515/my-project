import React, { useState, useEffect } from 'react';
import './App.css';

function RuleForm() {
    const [selectedStrategy, setSelectedStrategy] = useState('DCA'); // 選擇的策略類型
    const [selectedDay, setSelectedDay] = useState(''); // 選擇的日期 (1-31) 適用於定期定額
    const [inputType, setInputType] = useState('count'); // 定期定額輸入類型：股數或價格
    const [stockCode, setStockCode] = useState(''); // 股票代碼輸入
    const [inputValue, setInputValue] = useState(''); // 通用輸入值
    const [stopLoss, setStopLoss] = useState(''); // 停損值適用於停損停利
    const [takeProfit, setTakeProfit] = useState(''); // 停利值適用於停損停利
    const [peRatio, setPeRatio] = useState(''); // 本益比適用於合理本益比
    const [targetPrice, setTargetPrice] = useState(''); // 目標價格適用於目標價格策略
    const [rules, setRules] = useState([]); // 用於存儲從數據庫獲取的規則

    const daysOfMonth = Array.from({ length: 31 }, (_, i) => i + 1); // 生成日期陣列 [1, 2, ..., 31]

    // 從 Flask API 獲取現有的規則
    useEffect(() => {
        const fetchRules = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/rules');
                const result = await response.json();
                if (response.ok) {
                    setRules(result); // 將規則儲存在狀態中
                } else {
                    console.error('Error fetching rules:', response.statusText);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        };

        fetchRules();
    }, []);

    // 提交新規則到數據庫
    const handleSubmit = async (event) => {
        event.preventDefault();

        const data = {
            strategy: selectedStrategy,
            date: selectedDay,
            input_type: inputType,
            stock_code: stockCode,
            value: selectedStrategy === 'DCA' ? inputValue :
                selectedStrategy === 'StopLossTakeProfit' ? { stopLoss, takeProfit } :
                    selectedStrategy === 'PE' ? peRatio :
                        targetPrice,
        };

        try {
            const response = await fetch('http://127.0.0.1:5000/rule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                window.alert('成功提交規則數據！');
                setRules([...rules, result]); // 用新規則更新規則列表
            } else {
                console.error('Non-OK response:', response.status, response.statusText);
                window.alert(`提交規則時出錯：${response.statusText}`);
            }
        } catch (error) {
            console.error('Error:', error);
            window.alert('發生錯誤，請稍後再試。');
        }
    };

    // 刪除規則
    const handleDelete = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/rules/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                window.alert('成功刪除規則！');
                setRules(rules.filter((rule) => rule.id !== id)); // 從狀態中移除刪除的規則
            } else {
                console.error('Non-OK response:', response.status, response.statusText);
                window.alert(`刪除規則時出錯：${response.statusText}`);
            }
        } catch (error) {
            console.error('Error:', error);
            window.alert('刪除規則時發生錯誤。');
        }
    };

    return (
        <div>
            <h1>設定投資策略</h1>
            <form onSubmit={handleSubmit}>
                {/* 策略選擇器 */}
                <label>策略:</label>
                <select value={selectedStrategy} onChange={(e) => setSelectedStrategy(e.target.value)}>
                    <option value="DCA">定期定額 (DCA)</option>
                    <option value="StopLossTakeProfit">停損停利</option>
                    <option value="PE">合理本益比</option>
                    <option value="TargetPrice">目標價格</option>
                </select>

                {/* 定期定額的日期選擇器 */}
                {selectedStrategy === 'DCA' && (
                    <>
                        <label>日期:</label>
                        <select value={selectedDay} onChange={(e) => setSelectedDay(e.target.value)}>
                            <option value="">選擇日期</option>
                            {daysOfMonth.map((day) => (
                                <option key={day} value={day}>
                                    {day}
                                </option>
                            ))}
                        </select>
                    </>
                )}

                {/* 定期定額的輸入類型選擇器 */}
                {selectedStrategy === 'DCA' && (
                    <>
                        <label>輸入類型:</label>
                        <select value={inputType} onChange={(e) => setInputType(e.target.value)}>
                            <option value="count">股票數量</option>
                            <option value="price">股票價格</option>
                        </select>
                    </>
                )}

                {/* 股票代碼輸入 */}
                <label>股票代碼:</label>
                <input
                    type="text"
                    value={stockCode}
                    onChange={(e) => setStockCode(e.target.value)}
                    placeholder="輸入股票代碼"
                />

                {/* 基於策略的條件輸入 */}
                {selectedStrategy === 'DCA' && (
                    <input
                        type="number"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder={inputType === 'count' ? "輸入股票數量" : "輸入股票價格"}
                    />
                )}
                {selectedStrategy === 'StopLossTakeProfit' && (
                    <>
                        <label>停損值:</label>
                        <input
                            type="number"
                            value={stopLoss}
                            onChange={(e) => setStopLoss(e.target.value)}
                            placeholder="輸入停損百分比"
                        />
                        <label>停利值:</label>
                        <input
                            type="number"
                            value={takeProfit}
                            onChange={(e) => setTakeProfit(e.target.value)}
                            placeholder="輸入停利百分比"
                        />
                    </>
                )}
                {selectedStrategy === 'PE' && (
                    <input
                        type="number"
                        value={peRatio}
                        onChange={(e) => setPeRatio(e.target.value)}
                        placeholder="輸入本益比"
                    />
                )}
                {selectedStrategy === 'TargetPrice' && (
                    <input
                        type="number"
                        value={targetPrice}
                        onChange={(e) => setTargetPrice(e.target.value)}
                        placeholder="輸入目標價格"
                    />
                )}

                <button type="submit">提交規則</button>
            </form>

            <h2>現有規則</h2>
            <ul>
                {rules.length > 0 ? (
                    rules.map((rule, index) => (
                        <li key={index}>
                            策略: {rule.strategy}, 股票代碼: {rule.stock_code},
                            {rule.strategy === 'DCA' ? `日期 : ${rule.date}, ${rule.input_type === 'count' ? '股票數量' : '股票價格'}: ${rule.value}` :
                            rule.strategy === 'StopLossTakeProfit' ? `停損值: ${rule.value.stopLoss}%, 停利值: ${rule.value.takeProfit}% `:
                            rule.strategy === 'PE' ? `本益比: ${rule.value} `:
                            `目標價格: ${rule.value}`}
                            <button onClick={() => handleDelete(rule.id)}>刪除</button>
                        </li>
                    ))
                ) : (
                    <p>未找到任何規則。</p>
                )}
            </ul>
        </div>
    );
}

export default RuleForm;