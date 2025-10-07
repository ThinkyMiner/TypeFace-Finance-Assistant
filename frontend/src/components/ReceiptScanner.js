import { useState } from 'react';
import '../App.css';

const API_BASE = 'http://localhost:8000/api/v1';

function ReceiptScanner({ onExtractComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload an image (JPG, PNG) or PDF file');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setError('');
    setExtractedData(null);

    // Create preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError('');
    const token = localStorage.getItem('token');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_BASE}/receipts/extract`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to extract receipt data');
      }

      const data = await response.json();
      setExtractedData(data.extracted);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTransaction = () => {
    if (extractedData && onExtractComplete) {
      onExtractComplete(extractedData);
      // Reset the form
      setSelectedFile(null);
      setPreview(null);
      setExtractedData(null);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
    setExtractedData(null);
    setError('');
  };

  return (
    <div className="receipt-scanner">
      <div className="scanner-header">
        <h2>📸 Receipt Scanner</h2>
        <p>Upload a receipt image or PDF to automatically extract transaction details</p>
      </div>

      <div className="upload-section">
        <div className="file-input-wrapper">
          <input
            type="file"
            id="receipt-file"
            accept="image/*,application/pdf"
            onChange={handleFileSelect}
            className="file-input"
          />
          <label htmlFor="receipt-file" className="file-input-label">
            {selectedFile ? selectedFile.name : 'Choose File'}
          </label>
          {selectedFile && (
            <button onClick={handleClear} className="btn-clear">Clear</button>
          )}
        </div>

        {preview && (
          <div className="image-preview">
            <img src={preview} alt="Receipt preview" />
          </div>
        )}

        {selectedFile && !extractedData && (
          <button
            onClick={handleUpload}
            className="btn btn-scan"
            disabled={loading}
          >
            {loading ? 'Scanning Receipt...' : '🔍 Scan Receipt'}
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {extractedData && (
        <div className="extracted-data">
          <h3>✅ Extracted Information</h3>
          <div className="data-grid">
            <div className="data-item">
              <label>Merchant:</label>
              <span>{extractedData.merchant || 'N/A'}</span>
            </div>
            <div className="data-item">
              <label>Amount:</label>
              <span className="amount">${extractedData.amount?.toFixed(2) || '0.00'}</span>
            </div>
            <div className="data-item">
              <label>Date:</label>
              <span>{extractedData.date || 'N/A'}</span>
            </div>
            <div className="data-item">
              <label>Payment Method:</label>
              <span>{extractedData.payment_method || 'N/A'}</span>
            </div>
            {extractedData.items && extractedData.items.length > 0 && (
              <div className="data-item full-width">
                <label>Items:</label>
                <ul className="items-list">
                  {extractedData.items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            {extractedData.note && (
              <div className="data-item full-width">
                <label>Note:</label>
                <span>{extractedData.note}</span>
              </div>
            )}
            <div className="data-item">
              <label>Confidence:</label>
              <span className="confidence">
                {(extractedData.confidence * 100).toFixed(0)}%
              </span>
            </div>
            {extractedData.extraction_method && (
              <div className="data-item">
                <label>Method:</label>
                <span className="badge">
                  {extractedData.extraction_method === 'gemini_vision' ? '✨ AI-Powered' : 'OCR'}
                </span>
              </div>
            )}
          </div>

          <button onClick={handleCreateTransaction} className="btn">
            ➕ Add as Transaction
          </button>
        </div>
      )}

      <div className="scanner-tips">
        <h4>💡 Tips for best results:</h4>
        <ul>
          <li>Take a clear, well-lit photo of the receipt</li>
          <li>Ensure all text is readable and in focus</li>
          <li>Include the entire receipt in the image</li>
          <li>Supported formats: JPG, PNG, PDF (max 10MB)</li>
        </ul>
      </div>
    </div>
  );
}

export default ReceiptScanner;
