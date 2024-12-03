import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

function HomePage() {
    const [slideUp, setSlideUp] = useState(false);
    const [rankList, setRankList] = useState([]); // 新增排行榜狀態
    const navigate = useNavigate();
    const imagePath1 = "/logo192.png";

    const handleStartClick = () => {
        setSlideUp(true);
        setTimeout(() => {
            navigate('/usermode');
        }, 500);
    };

    // 獲取排行榜資料
    useEffect(() => {
        fetch('http://localhost:5000/rank_records') // 更新為後端 API 地址
            .then(response => response.json())
            .then(data => {
                setRankList(data); // 設定排行榜數據
            })
            .catch(error => console.error('獲取排行榜失敗:', error));
    }, []);

    return (
        <div className={`home-page ${slideUp ? 'slide-up' : ''}`}>
            <div className={`welcome-container ${slideUp ? 'hidden' : ''}`}>
                <img src={imagePath1} alt="Action Transaction Price Chart" />
                <h1 className="welcome-title">歡迎使用股神孵化器</h1>
                <p className="welcome-subtitle">在這裡，您可以設計並測試您的投資策略</p>
                <button className="start-button" onClick={handleStartClick}>
                    開始使用
                </button>

                {/* 排行榜表格 */}
                <div className="rank-table">
                    <h2>排行榜</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>名次</th>
                                <th>ID</th>
                                <th>回報率 (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rankList.length > 0 ? (
                                rankList.map((record, index) => (
                                    <tr key={index}>
                                        <td>{index + 1}</td>
                                        <td>{record.rule_id}</td>
                                        <td>{record.return_rate.toFixed(2)}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3">暫無排行榜數據</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default HomePage;