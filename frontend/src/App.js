import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthForm from './components/AuthForm';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import { LoadingSpinner } from './components/LazyLoadWrapper';

// Lazy load components for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const RealTimeDashboard = lazy(() => import('./components/RealTimeDashboard'));
const Campaigns = lazy(() => import('./pages/Campaigns'));
const Prospects = lazy(() => import('./pages/Prospects'));
const Lists = lazy(() => import('./pages/Lists'));
const ListsDetail = lazy(() => import('./pages/ListsDetail'));
const Templates = lazy(() => import('./pages/Templates'));
const Intents = lazy(() => import('./pages/Intents'));
const Analytics = lazy(() => import('./pages/Analytics'));
const EmailProcessing = lazy(() => import('./pages/EmailProcessing'));
const EmailProviders = lazy(() => import('./pages/EmailProviders'));
const KnowledgeBase = lazy(() => import('./pages/KnowledgeBase'));
const SystemPrompts = lazy(() => import('./pages/SystemPrompts'));
const ResponseVerification = lazy(() => import('./pages/ResponseVerification'));
const AIAgentChat = lazy(() => import('./components/AIAgentChat'));
const EnhancedAIAgentChat = lazy(() => import('./components/EnhancedAIAgentChat'));

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
        <Route path="/lists/:listId" element={<ListsDetail />} />
        <Route path="/templates" element={<Templates />} />
        <Route path="/intents" element={<Intents />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/email-processing" element={<EmailProcessing />} />
        <Route path="/email-providers" element={<EmailProviders />} />
        <Route path="/knowledge-base" element={<KnowledgeBase />} />
        <Route path="/system-prompts" element={<SystemPrompts />} />
        <Route path="/response-verification" element={<ResponseVerification />} />
        <Route path="/ai-agent" element={<AIAgentChat />} />
        <Route path="/ai-agent-enhanced" element={<EnhancedAIAgentChat />} />
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