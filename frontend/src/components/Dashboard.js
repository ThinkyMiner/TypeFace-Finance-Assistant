import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import AIAssistant from './AIAssistant';
import ReceiptScanner from './ReceiptScanner';
import '../App.css';

const API_BASE = 'http://localhost:8000/api/v1';

function Dashboard() {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState({ totalIncome: 0, totalExpense: 0, balance: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    kind: 'expense',
    amount: '',
    occurred_on: new Date().toISOString().split('T')[0],
    merchant: '',
    note: '',
    payment_method: ''
  });

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');

    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/transactions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }

      if (!response.ok) throw new Error('Failed to fetch transactions');
      const data = await response.json();
      setTransactions(data);
      calculateStats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const calculateStats = (txns) => {
    const income = txns.filter(t => t.kind === 'income').reduce((sum, t) => sum + t.amount, 0);
    const expense = txns.filter(t => t.kind === 'expense').reduce((sum, t) => sum + t.amount, 0);
    setStats({
      totalIncome: income,
      totalExpense: expense,
      balance: income - expense
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_BASE}/transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          amount: parseFloat(formData.amount)
        })
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }

      if (!response.ok) throw new Error('Failed to create transaction');
      setFormData({
        kind: 'expense',
        amount: '',
        occurred_on: new Date().toISOString().split('T')[0],
        merchant: '',
        note: '',
        payment_method: ''
      });
      fetchTransactions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const handleReceiptExtract = (extractedData) => {
    // Pre-fill the form with extracted data
    setFormData({
      kind: 'expense',
      amount: extractedData.amount || '',
      occurred_on: extractedData.date || new Date().toISOString().split('T')[0],
      merchant: extractedData.merchant || '',
      note: extractedData.note || '',
      payment_method: extractedData.payment_method || ''
    });
    // Scroll to the form
    document.querySelector('.transaction-form')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="App">
      <header className="header">
        <div>
          <h1>Personal Finance Tracker</h1>
          <p>Track your income and expenses</p>
        </div>
        <button onClick={handleLogout} className="btn btn-logout">Logout</button>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="stats-container">
        <div className="stat-card">
          <h3>Total Income</h3>
          <div className="value">${stats.totalIncome.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <h3>Total Expense</h3>
          <div className="value">${stats.totalExpense.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <h3>Balance</h3>
          <div className="value">${stats.balance.toFixed(2)}</div>
        </div>
      </div>

      <AIAssistant />

      <ReceiptScanner onExtractComplete={handleReceiptExtract} />

      <div className="transaction-form">
        <h2>Add Transaction</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Type</label>
              <select name="kind" value={formData.kind} onChange={handleChange} required>
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>
            <div className="form-group">
              <label>Amount</label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                step="0.01"
                placeholder="0.00"
                required
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Date</label>
              <input
                type="date"
                name="occurred_on"
                value={formData.occurred_on}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Merchant</label>
              <input
                type="text"
                name="merchant"
                value={formData.merchant}
                onChange={handleChange}
                placeholder="Store or person name"
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Payment Method</label>
              <input
                type="text"
                name="payment_method"
                value={formData.payment_method}
                onChange={handleChange}
                placeholder="Cash, Card, etc."
              />
            </div>
            <div className="form-group full-width">
              <label>Note</label>
              <input
                type="text"
                name="note"
                value={formData.note}
                onChange={handleChange}
                placeholder="Optional note"
              />
            </div>
          </div>
          <button type="submit" className="btn">Add Transaction</button>
        </form>
      </div>

      <div className="transactions-section">
        <h2>Recent Transactions</h2>
        {loading ? (
          <div className="loading">Loading...</div>
        ) : transactions.length === 0 ? (
          <div className="empty-state">No transactions yet. Add your first transaction above!</div>
        ) : (
          transactions.map(txn => (
            <div key={txn.id} className="transaction-item">
              <div className="transaction-info">
                <div className="transaction-merchant">
                  {txn.merchant || 'Unnamed Transaction'}
                </div>
                <div className="transaction-details">
                  {txn.occurred_on} {txn.payment_method && `• ${txn.payment_method}`}
                  {txn.note && ` • ${txn.note}`}
                </div>
              </div>
              <div className={`transaction-amount ${txn.kind}`}>
                {txn.kind === 'income' ? '+' : '-'}${txn.amount.toFixed(2)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Dashboard;
