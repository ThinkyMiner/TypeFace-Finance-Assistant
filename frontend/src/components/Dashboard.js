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
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    kind: '',
  });
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 5,
    total: 0
  });
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importPreview, setImportPreview] = useState(null);
  const [importLoading, setImportLoading] = useState(false);

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');

    if (!token) {
      navigate('/login');
      return;
    }

    try {
      // Build query params for filters
      const filterParams = new URLSearchParams();
      if (filters.startDate) filterParams.append('start_date', filters.startDate);
      if (filters.endDate) filterParams.append('end_date', filters.endDate);
      if (filters.kind) filterParams.append('kind', filters.kind);

      // Fetch stats (all transactions with filters, no pagination)
      const statsParams = new URLSearchParams(filterParams);
      statsParams.append('limit', 10000); // Large number to get all
      statsParams.append('offset', 0);

      const statsResponse = await fetch(`${API_BASE}/transactions?${statsParams.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (statsResponse.ok) {
        const allData = await statsResponse.json();
        calculateStats(allData);
      }

      // Fetch paginated transactions
      const pageParams = new URLSearchParams(filterParams);
      pageParams.append('limit', pagination.limit);
      pageParams.append('offset', (pagination.page - 1) * pagination.limit);

      const response = await fetch(`${API_BASE}/transactions?${pageParams.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }

      if (!response.ok) throw new Error('Failed to fetch transactions');

      // Get total count from header
      const totalCount = parseInt(response.headers.get('X-Total-Count') || '0');

      console.log('API Response Headers:', {
        totalCountHeader: response.headers.get('X-Total-Count'),
        parsedTotal: totalCount,
        allHeaders: Array.from(response.headers.entries())
      });

      const data = await response.json();
      console.log('Fetched transactions:', data.length, 'Total from header:', totalCount);

      setTransactions(data);
      setPagination(prev => ({ ...prev, total: totalCount }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [navigate, filters, pagination.page, pagination.limit]);

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

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const clearFilters = () => {
    setFilters({
      startDate: '',
      endDate: '',
      kind: '',
    });
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    console.log('Page change clicked:', newPage);
    setPagination(prev => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleExportPDF = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);

      // Build query params (same filters as current view)
      const params = new URLSearchParams();
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      if (filters.kind) params.append('kind', filters.kind);

      const response = await fetch(`${API_BASE}/transactions/export/pdf?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to export PDF');

      // Download the PDF
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transactions_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to export PDF: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleImportFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setImportFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setImportFile(null);
    }
  };

  const handleUploadStatement = async () => {
    if (!importFile) return;

    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    setImportLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', importFile);

      const response = await fetch(`${API_BASE}/imports/bank-statement`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to parse statement');
      }

      const data = await response.json();
      setImportPreview(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setImportLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    setImportLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/imports/confirm`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const imported = await response.json();
      setError(''); // Clear any errors
      alert(`Successfully imported ${imported.length} transactions!`);

      // Close modal and refresh
      setShowImportModal(false);
      setImportFile(null);
      setImportPreview(null);
      fetchTransactions();
    } catch (err) {
      console.error('Import error:', err);
      setError(err.message);
    } finally {
      setImportLoading(false);
    }
  };

  const handleCloseImportModal = () => {
    setShowImportModal(false);
    setImportFile(null);
    setImportPreview(null);
    setError('');
  };

  const totalPages = Math.ceil(pagination.total / pagination.limit);

  // Debug logging
  console.log('Pagination Debug:', {
    total: pagination.total,
    limit: pagination.limit,
    page: pagination.page,
    totalPages,
    shouldShowPagination: pagination.total > pagination.limit,
    transactionsLength: transactions.length
  });

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
        <h2>Transactions</h2>

        <div className="filters-container">
          <div className="filters">
            <div className="filter-group">
              <label>From Date</label>
              <input
                type="date"
                name="startDate"
                value={filters.startDate}
                onChange={handleFilterChange}
              />
            </div>
            <div className="filter-group">
              <label>To Date</label>
              <input
                type="date"
                name="endDate"
                value={filters.endDate}
                onChange={handleFilterChange}
              />
            </div>
            <div className="filter-group">
              <label>Type</label>
              <select
                name="kind"
                value={filters.kind}
                onChange={handleFilterChange}
              >
                <option value="">All</option>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            <button onClick={clearFilters} className="btn btn-secondary">Clear Filters</button>
            <button onClick={() => setShowImportModal(true)} className="btn btn-import">
              📥 Import PDF
            </button>
            <button onClick={handleExportPDF} className="btn btn-export" disabled={loading}>
              📄 Export PDF
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading...</div>
        ) : transactions.length === 0 ? (
          <div className="empty-state">
            {filters.startDate || filters.endDate || filters.kind
              ? 'No transactions found for the selected filters.'
              : 'No transactions yet. Add your first transaction above!'}
          </div>
        ) : (
          <>
            {pagination.total > 0 && (
              <div className="transaction-summary">
                Showing {((pagination.page - 1) * pagination.limit) + 1} - {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} transaction{pagination.total !== 1 ? 's' : ''}
              </div>
            )}
            <div className="transactions-list">
              {transactions.map(txn => (
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
              ))}
            </div>

            {/* Always show pagination if there are any transactions for debugging */}
            {transactions.length > 0 && (
              <div className="pagination">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page === 1}
                  className="pagination-btn"
                >
                  ← Previous
                </button>

                <div className="pagination-pages">
                  {totalPages > 0 && Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNum => (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`pagination-page ${pagination.page === pageNum ? 'active' : ''}`}
                    >
                      {pageNum}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page === totalPages || totalPages <= 1}
                  className="pagination-btn"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <div className="modal-overlay" onClick={handleCloseImportModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📥 Import Bank Statement</h2>
              <button className="modal-close" onClick={handleCloseImportModal}>×</button>
            </div>

            <div className="modal-body">
              {error && <div className="error">{error}</div>}

              {!importPreview ? (
                <>
                  <p>Upload a PDF bank statement to automatically import transactions</p>

                  <div className="import-file-section">
                    <input
                      type="file"
                      id="import-file"
                      accept="application/pdf"
                      onChange={handleImportFileChange}
                      style={{ display: 'none' }}
                    />
                    <label htmlFor="import-file" className="file-upload-btn">
                      {importFile ? `📄 ${importFile.name}` : '📁 Choose PDF File'}
                    </label>
                  </div>

                  <button
                    onClick={handleUploadStatement}
                    disabled={!importFile || importLoading}
                    className="btn btn-primary"
                  >
                    {importLoading ? 'Parsing...' : 'Parse Statement'}
                  </button>
                </>
              ) : (
                <>
                  <div className="import-preview-info">
                    <h3>Found {importPreview.total_count} transactions</h3>
                    <p className="preview-method">Method: {importPreview.method}</p>
                  </div>

                  <div className="preview-table-container">
                    <table className="preview-table-modal">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Type</th>
                          <th>Merchant</th>
                          <th>Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {importPreview.preview.map((txn, idx) => (
                          <tr key={idx}>
                            <td>{txn.occurred_on}</td>
                            <td>
                              <span className={`badge ${txn.kind}`}>
                                {txn.kind}
                              </span>
                            </td>
                            <td>{txn.merchant}</td>
                            <td className={`amount ${txn.kind}`}>
                              ₹{txn.amount.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="modal-actions">
                    <button
                      onClick={handleConfirmImport}
                      disabled={importLoading}
                      className="btn btn-success"
                    >
                      {importLoading ? 'Importing...' : `Import All ${importPreview.total_count}`}
                    </button>
                    <button onClick={handleCloseImportModal} className="btn btn-secondary">
                      Cancel
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
