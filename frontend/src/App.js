import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Campaigns from './pages/Campaigns';
import Prospects from './pages/Prospects';
import Lists from './pages/Lists';
import Templates from './pages/Templates';
import Intents from './pages/Intents';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/prospects" element={<Prospects />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/intents" element={<Intents />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </Layout>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;