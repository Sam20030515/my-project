import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import UserMode from './UserMode';
import RuleForm from './RuleForm';
import InvestmentChart from './InvestmentChart';  

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/usermode" element={<UserMode />} />
                <Route path="/ruleform" element={<RuleForm />} />
                <Route path="/investment-chart" element={<InvestmentChart />} /> 
            </Routes>
        </Router>
    );
}

export default App;
