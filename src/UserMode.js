import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // 引入 useNavigate
import './UserMode.css';

function UserForm() {
    const [username, setUsername] = useState('');
    const [totalAssets, setTotalAssets] = useState('');
    const [monthlyInvestment, setMonthlyInvestment] = useState('');
    const [users, setUsers] = useState([]);
    const [editingUser, setEditingUser] = useState(null);
    const [selectedUser, setSelectedUser] = useState(null); // 新增選擇的使用者
    const navigate = useNavigate(); // 初始化 useNavigate

    // Fetch users from the database
    const fetchUsers = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/users');
            const result = await response.json();
            if (response.ok) {
                setUsers(result);
            } else {
                console.error('Error fetching users:', response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Load users on component mount
    useEffect(() => {
        fetchUsers();
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();

        const data = {
            username,
            total_assets: totalAssets,
            monthly_investment: monthlyInvestment,
        };

        try {
            let response;
            if (editingUser) {
                response = await fetch(`http://127.0.0.1:5000/users/${editingUser.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
            } else {
                response = await fetch('http://127.0.0.1:5000/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
            }

            if (response.ok) {
                window.alert(editingUser ? '使用者資料已更新！' : '成功提交使用者數據！');
                setEditingUser(null);
                setUsername('');
                setTotalAssets('');
                setMonthlyInvestment('');
                fetchUsers();
            } else {
                const result = await response.json();
                console.error('Non-OK response:', response.status, response.statusText);
                window.alert(`提交使用者數據時出錯：${response.statusText}`);
            }
        } catch (error) {
            console.error('Error:', error);
            window.alert('發生錯誤，請稍後再試。');
        }
    };

    const handleEdit = (user) => {
        setEditingUser(user);
        setUsername(user.username);
        setTotalAssets(user.total_assets);
        setMonthlyInvestment(user.monthly_investment);
    };

    const handleDelete = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/users/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                window.alert('成功刪除使用者！');
                fetchUsers();
            } else {
                console.error('Non-OK response:', response.status, response.statusText);
                window.alert(`刪除使用者時出錯：${response.statusText}`);
            }
        } catch (error) {
            console.error('Error:', error);
            window.alert('刪除使用者時發生錯誤。');
        }
    };

    const handleSelect = async (user) => {
        setSelectedUser(user); // 儲存選擇的使用者到狀態
        try {
            // 發送請求到後端保存選擇的使用者
            const response = await fetch('http://127.0.0.1:5000/save_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user),
            });

            if (response.ok) {
                const result = await response.json();
                window.alert(result.message);
                navigate('/ruleform'); // 跳轉至 ruleform 頁面，並攜帶使用者資料
            } else {
                const errorResult = await response.json();
                window.alert(`儲存使用者資料失敗：${errorResult.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            window.alert('無法儲存使用者資料，請稍後再試。');
        }
    };


    return (
        <div className="user-form-page">
            <div className="layout-container">
                {/* 左側表單 */}
                <div className="form-container">
                    <h1>情境輸入</h1>
                    <form onSubmit={handleSubmit}>
                        <label>使用者名稱:</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="輸入使用者名稱"
                            required
                        />

                        <label>總資產:</label>
                        <input
                            type="number"
                            value={totalAssets}
                            onChange={(e) => setTotalAssets(e.target.value)}
                            placeholder="輸入總資產"
                            required
                        />

                        <label>每月投入資金:</label>
                        <input
                            type="number"
                            value={monthlyInvestment}
                            onChange={(e) => setMonthlyInvestment(e.target.value)}
                            placeholder="輸入每月投入資金"
                            required
                        />

                        <button type="submit">{editingUser ? '更新使用者' : '提交使用者'}</button>
                    </form>
                </div>

                {/* 右側使用者列表 */}
                <div className="users-container">
                    <h2>使用者列表</h2>
                    {users.length === 0 ? (
                        <div className="no-users">
                            <p>目前沒有使用者，請新增一個！</p>
                        </div>
                    ) : (
                        <ul>
                            {users.map((user) => (
                                <li key={user.id}>
                                    <span>
                                        名稱: {user.username}, 總資產: {user.total_assets}, 每月投入資金: {user.monthly_investment}
                                    </span>
                                    <div className="button-group">
                                        <button className="action-edit" onClick={() => handleEdit(user)}>編輯</button>
                                        <button className="action-delete" onClick={() => handleDelete(user.id)}>刪除</button>
                                        <button className="action-select" onClick={() => handleSelect(user)}>選擇</button>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
}

export default UserForm;
