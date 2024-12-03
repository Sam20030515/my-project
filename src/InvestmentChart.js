import React from 'react';
import './InvestmentChart.css';

const InvestmentChart = () => {
    const imagePath1 = 'http://localhost:5000/static/action_transaction_price.png'; // 第一張圖
    const imagePath2 = 'http://localhost:5000/static/stock_price.png'; // 第二張圖
    //const imagePath3 = 'http://localhost:5000/static/investment_and_shares.png'; // 第三張圖
    const imagePath4 = 'http://localhost:5000/static/return_rate.png'; // 第三張圖，放在下面


    return (
        <div className="investment-chart-page">
            <div className="investment-chart-container">
                <h1>投資金額波動圖</h1>
                <div className="investment-chart-images">
                    <img src={imagePath1} alt="Action Transaction Price Chart" />
                    <img src={imagePath2} alt="Stock Price Chart" />
                    {/*<img src={imagePath3} alt="Investment and Shares Chart" />*/}
                    <img src={imagePath4} alt="Return Rate Chart" />
                </div>
                <p>此圖展示了不同時期的投資金額波動情況。</p>
            </div>
        </div>
    );
};

export default InvestmentChart;
