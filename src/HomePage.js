import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 引入 useNavigate
import './HomePage.css';

function HomePage() {
    const [slideUp, setSlideUp] = useState(false);
    const navigate = useNavigate(); // 初始化 useNavigate
    const imagePath1 = "/logo192.png";

    const handleStartClick = () => {
        setSlideUp(true);
        setTimeout(() => {
            navigate('/usermode'); // 修改目標路徑為 /usermode
        }, 500);
    };


    return (
        <div className={`home-page ${slideUp ? 'slide-up' : ''}`}>
            <div className={`welcome-container ${slideUp ? 'hidden' : ''}`}>
                <img src={imagePath1} alt="Action Transaction Price Chart" />
                <h1 className="welcome-title">歡迎使用股神孵化器</h1>
                <p className="welcome-subtitle">在這裡，您可以設計並測試您的投資策略</p>
                <button className="start-button" onClick={handleStartClick}>
                    開始使用
                </button>
            </div>
        </div>
    );
}

export default HomePage;
