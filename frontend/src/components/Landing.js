import { Link } from 'react-router-dom';
import '../App.css';

function Landing() {
  return (
    <div className="App">
      <div className="landing-container">
        <div className="landing-hero">
          <h1 className="landing-title">Personal Finance Tracker</h1>
          <p className="landing-subtitle">
            Take control of your finances. Track income, expenses, and manage your money with ease.
          </p>
          <div className="landing-buttons">
            <Link to="/login" className="btn btn-primary">Login</Link>
            <Link to="/register" className="btn btn-secondary">Register</Link>
          </div>
        </div>
        <div className="landing-features">
          <div className="feature-card">
            <h3>Track Transactions</h3>
            <p>Easily record income and expenses with detailed information</p>
          </div>
          <div className="feature-card">
            <h3>View Statistics</h3>
            <p>Get insights into your spending patterns and financial health</p>
          </div>
          <div className="feature-card">
            <h3>Stay Organized</h3>
            <p>Categorize transactions and keep your finances organized</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Landing;
