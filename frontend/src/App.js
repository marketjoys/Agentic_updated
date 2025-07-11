import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import RealTimeDashboard from './components/RealTimeDashboard';
import Campaigns from './pages/Campaigns';
import Prospects from './pages/Prospects';
import Lists from './pages/Lists';
import Templates from './pages/Templates';
import Intents from './pages/Intents';
import Analytics from './pages/Analytics';
import EmailProcessing from './pages/EmailProcessing';
import EmailProviders from './pages/EmailProviders';
import KnowledgeBase from './pages/KnowledgeBase';
import SystemPrompts from './pages/SystemPrompts';
import ResponseVerification from './pages/ResponseVerification';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/prospects" element={<Prospects />} />
            <Route path="/lists" element={<Lists />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/intents" element={<Intents />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/email-processing" element={<EmailProcessing />} />
            <Route path="/email-providers" element={<EmailProviders />} />
            <Route path="/knowledge-base" element={<KnowledgeBase />} />
            <Route path="/system-prompts" element={<SystemPrompts />} />
            <Route path="/response-verification" element={<ResponseVerification />} />
          </Routes>
        </Layout>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;