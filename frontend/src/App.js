import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Import pages
import Home from './pages/Home';
import Devices from './pages/Devices';
import Alerts from './pages/Alerts';
import Research from './pages/Research';
import Vulnerabilities from './pages/Vulnerabilities';

// Import components
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <nav className="navbar">
            <div className="nav-brand">
              <h1>IoT Security Dashboard</h1>
            </div>
            <div className="nav-links">
              <a href="/">Dashboard</a>
              <a href="/devices">Devices</a>
              <a href="/alerts">Alerts</a>
              <a href="/vulnerabilities">Vulnerabilities</a>
              <a href="/research">Research</a>
            </div>
          </nav>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/devices" element={<Devices />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/vulnerabilities" element={<Vulnerabilities />} />
            <Route path="/research" element={<Research />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;