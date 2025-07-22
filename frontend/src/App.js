import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthForm from './components/AuthForm';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import RealTimeDashboard from './components/RealTimeDashboard';
import Campaigns from './pages/Campaigns';
import Prospects from './pages/Prospects';
import Lists from './pages/Lists';
import ListsDetail from './pages/ListsDetail';
import Templates from './pages/Templates';
import Intents from './pages/Intents';
import Analytics from './pages/Analytics';
import EmailProcessing from './pages/EmailProcessing';
import EmailProviders from './pages/EmailProviders';
import KnowledgeBase from './pages/KnowledgeBase';
import SystemPrompts from './pages/SystemPrompts';
import ResponseVerification from './pages/ResponseVerification';

// Protected Routes Component
const ProtectedRoutes = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthForm />;
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/real-time" element={<RealTimeDashboard />} />
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
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <ProtectedRoutes />
          <Toaster position="top-right" />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;