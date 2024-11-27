import React from 'react';
import './InvestmentChart.css'; // 假設 CSS 檔與此檔案同路徑

const InvestmentChart = () => {
    const imagePath = 'http://localhost:5000/static/investment_chart.png'; // 假設圖片在這個路徑

    return (
        <div className="investment-chart-page">
            <div className="investment-chart-container">
                <h1>投資金額波動圖</h1>
                <img
                    src={imagePath}
                    alt="Investment chart"
                />
                <p>此圖展示了不同時期的投資金額波動情況。</p>
            </div>
        </div>
    );
};

export default InvestmentChart;
