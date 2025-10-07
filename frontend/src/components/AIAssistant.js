import { useState } from 'react';
import ChartRenderer from './ChartRenderer';
import '../App.css';

const API_BASE = 'http://localhost:8000/api/v1';

function AIAssistant() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [suggestions] = useState([
    { text: "How am I doing financially?", preset: "overview" },
    { text: "Where am I spending the most?", preset: "spending" },
    { text: "Show me my spending trends", preset: "trends" },
  ]);

  const handleQuery = async (queryText, preset = null) => {
    setLoading(true);
    setResponse(null);
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_BASE}/ai/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: queryText,
          preset: preset
        })
      });

      if (!response.ok) throw new Error('Failed to get AI response');
      const data = await response.json();
      setResponse(data);
      setQuery('');
    } catch (err) {
      setResponse({
        insight: 'Sorry, I encountered an error. Please try again.',
        chart: null,
        recommendations: []
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      handleQuery(query);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleQuery(suggestion.text, suggestion.preset);
  };

  return (
    <div className="ai-assistant">
      <div className="ai-header">
        <h2>AI Financial Assistant</h2>
        <p>Ask me anything about your finances!</p>
      </div>

      <div className="ai-suggestions">
        <p className="suggestions-label">Try asking:</p>
        <div className="suggestion-buttons">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="suggestion-btn"
              disabled={loading}
            >
              {suggestion.text}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="ai-input-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Or type your own question..."
          className="ai-input"
          disabled={loading}
        />
        <button type="submit" className="btn" disabled={loading || !query.trim()}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </form>

      {loading && (
        <div className="ai-response">
          <div className="loading">Analyzing your finances...</div>
        </div>
      )}

      {response && !loading && (
        <div className="ai-response">
          <div className="ai-insight">
            <h3>Insight</h3>
            <p>{response.insight}</p>
          </div>

          {response.chart && (
            <div className="ai-chart">
              <div className="chart-container">
                <ChartRenderer chartConfig={response.chart} />
              </div>
            </div>
          )}

          {response.recommendations && response.recommendations.length > 0 && (
            <div className="ai-recommendations">
              <h3>Recommendations</h3>
              <ul>
                {response.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AIAssistant;
