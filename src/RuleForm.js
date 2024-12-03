import React, { useState, useEffect } from 'react';
import './RuleForm.css';
import { useNavigate } from 'react-router-dom';

function RuleForm() {
  const [selectedStrategy, setSelectedStrategy] = useState('DCA');
  const [selectedDay, setSelectedDay] = useState('');
  const [inputType, setInputType] = useState('count');
  const [stockCode, setStockCode] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [peRatio, setPeRatio] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [rules, setRules] = useState([]);
  const [editingRule, setEditingRule] = useState(null);
  const [everyBuy, setEveryBuy] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('請稍後...');
  const navigate = useNavigate(); // 路由導航


  const daysOfMonth = Array.from({ length: 31 }, (_, i) => i + 1);

  // 定義抓取資料庫資料的函式
  const fetchRules = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/rules');
      const result = await response.json();
      if (response.ok) {
        setRules(result);
      } else {
        console.error('Error fetching rules:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // 初始加載數據
  useEffect(() => {
    fetchRules();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const data = {
      strategy: selectedStrategy,
      date: selectedDay,
      input_type: inputType,
      stock_code: stockCode,
      value:
        selectedStrategy === 'DCA'
          ? inputValue
          : selectedStrategy === 'StopLossTakeProfit'
            ? { stopLoss, takeProfit, everyBuy }
            : selectedStrategy === 'PE'
              ? peRatio
              : targetPrice,
    };


    try {
      let response;
      if (editingRule) {
        response = await fetch(`http://127.0.0.1:5000/rules/${editingRule.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
      } else {
        response = await fetch('http://127.0.0.1:5000/rule', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
      }

      if (response.ok) {
        window.alert(editingRule ? '規則已更新！' : '成功提交規則數據！');
        setEditingRule(null);
        fetchRules(); // 成功後重新抓取資料庫資料
      } else {
        const result = await response.json();
        console.error('Non-OK response:', response.status, response.statusText);
        window.alert(`提交規則時出錯：${response.statusText}`);
      }
    } catch (error) {
      console.error('Error:', error);
      window.alert('發生錯誤，請稍後再試。');
    }
  };

  const handleExecuteAndRedirect = async () => {
    setLoading(true); // 顯示請稍後彈窗
    setLoadingMessage('你先別急 我處理一下'); // 可自定義顯示文字

    try {
      const response = await fetch('http://127.0.0.1:5000/run_script', {
        method: 'POST',
      });
      if (response.ok) {
        window.alert('執行成功！');
        navigate('/investment-chart'); // 跳轉到 InvestmentChart 頁面
      } else {
        const result = await response.json();
        console.error('Error executing script:', result);
        window.alert('執行時出錯，請稍後再試。');
      }
    } catch (error) {
      console.error('Error:', error);
      window.alert('執行時發生錯誤。');
    } finally {
      setLoading(false); // 無論成功與否，都隱藏「請稍後」彈窗
    }
  };

  const handleEdit = (rule) => {
    setEditingRule(rule);
    setSelectedStrategy(rule.strategy);
    setSelectedDay(rule.date || '');
    setInputType(rule.input_type || 'count');
    setStockCode(rule.stock_code);
    if (rule.strategy === 'DCA') {
      setInputValue(rule.value);
    } else if (rule.strategy === 'StopLossTakeProfit') {
      setStopLoss(rule.value.stopLoss);
      setTakeProfit(rule.value.takeProfit);
      setEveryBuy(rule.value.everyBuy || '');
    } else if (rule.strategy === 'PE') {
      setPeRatio(rule.value);
    } else if (rule.strategy === 'TargetPrice') {
      setTargetPrice(rule.value);
    }
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/rules/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        window.alert('成功刪除規則！');
        fetchRules(); // 刪除成功後重新抓取資料庫資料
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
    <div className="rule-form-page">
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div className="layout-container">
          {/* 左側表單 */}
          <div className="form-container">
            <h1>設定投資策略</h1>
            <form onSubmit={handleSubmit}>
              {/* 表單內容 */}
              <label>策略:</label>
              <select value={selectedStrategy} onChange={(e) => setSelectedStrategy(e.target.value)}>
                <option value="DCA">定期定額 (DCA)</option>
                <option value="StopLossTakeProfit">停損停利</option>
                <option value="PE">合理本益比</option>
              </select>

              {/* 根據選擇顯示對應輸入框 */}
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

                  <label>類型:</label>
                  <select value={inputType} onChange={(e) => setInputType(e.target.value)}>
                    <option value="count">股票數量</option>
                    <option value="price">股票價格</option>
                  </select>


                  <label>股票代號:</label> {/* 新增股票代號輸入框 */}
                  <input
                    type="text"
                    value={stockCode}
                    onChange={(e) => setStockCode(e.target.value)}
                    placeholder="輸入股票代號"
                  />

                  <input
                    type="number"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder={inputType === 'count' ? '輸入股票數量' : '輸入股票價格'}
                  />
                </>
              )}

              {selectedStrategy === 'StopLossTakeProfit' && (
                <>
                  <label>股票代號:</label> {/* 新增股票代號輸入框 */}
                  <input
                    type="text"
                    value={stockCode}
                    onChange={(e) => setStockCode(e.target.value)}
                    placeholder="輸入股票代號"
                  />

                  <label>停損值(%):</label>
                  <input
                    type="number"
                    value={stopLoss}
                    onChange={(e) => setStopLoss(e.target.value)}
                    placeholder="輸入停損百分比"
                  />

                  <label>停利值(%):</label>
                  <input
                    type="number"
                    value={takeProfit}
                    onChange={(e) => setTakeProfit(e.target.value)}
                    placeholder="輸入停利百分比"
                  />

                  <label>每次賣出金額:</label> {/* 新增每次賣出金額輸入框 */}
                  <input
                    type="number"
                    value={everyBuy}
                    onChange={(e) => setEveryBuy(e.target.value)}
                    placeholder="輸入每次賣出金額"
                  />
                </>
              )}

              {selectedStrategy === 'PE' && (
                <>

                  <label>股票代號:</label> {/* 新增股票代號輸入框 */}
                  <input
                    type="text"
                    value={stockCode}
                    onChange={(e) => setStockCode(e.target.value)}
                    placeholder="輸入股票代號"
                  />


                  <label>本益比:</label>
                  <input
                    type="number"
                    value={peRatio}
                    onChange={(e) => setPeRatio(e.target.value)}
                    placeholder="輸入本益比"
                  />
                </>
              )}
              {selectedStrategy === 'TargetPrice' && (
                <>
                  <label>目標價格:</label>
                  <input
                    type="number"
                    value={targetPrice}
                    onChange={(e) => setTargetPrice(e.target.value)}
                    placeholder="輸入目標價格"
                  />
                </>
              )}

              <button type="submit">{editingRule ? '更新規則' : '提交規則'}</button>
              <button type="button" onClick={handleExecuteAndRedirect} disabled={loading}>
                {loading ? '請稍後...' : '執行結果'}
              </button>



            </form>
          </div>

          {/* 右側現有規則 */}
          <div className="rules-container">
            <h2>現有規則</h2>
            {rules.length === 0 ? (
              <div className="no-rules">
                <p>目前沒有規則，請新增一個！</p>
              </div>
            ) : (
              <ul>
                {rules.map((rule) => (
                  <li key={rule.id}>
                    <span>
                      策略: {rule.strategy}, 股票代碼: {rule.stock_code},
                      {rule.strategy === 'DCA'
                        ? `日期: ${rule.date}, ${rule.input_type === 'count' ? '股票數量' : '股票價格'
                        }: ${rule.value}`
                        : rule.strategy === 'StopLossTakeProfit'
                          ? `停損值: ${rule.value.stopLoss}%, 停利值: ${rule.value.takeProfit}%, 每次賣出金額: ${rule.value.everyBuy}`
                          : rule.strategy === 'PE'
                            ? `本益比: ${rule.value}`
                            : `目標價格: ${rule.value}`}
                    </span>
                    <div className="button-group">
                      <button onClick={() => handleEdit(rule)}>編輯</button>
                      <button onClick={() => handleDelete(rule.id)}>刪除</button>

                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
      {/* 彈窗顯示「請稍後...」 */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-popup">
            <p>{loadingMessage}</p>
          </div>
        </div>
      )}
    </div>

  );
}

export default RuleForm;
