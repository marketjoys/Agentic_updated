import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Home, 
  Send, 
  Users, 
  FileText, 
  Brain, 
  BarChart3, 
  Menu, 
  X,
  Sparkles,
  FolderOpen,
  Mail,
  Settings,
  BookOpen,
  MessageSquare,
  CheckCircle,
  Server,
  Activity,
  LogOut,
  User,
  Bot
} from 'lucide-react';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home, color: 'from-blue-500 to-blue-600' },
    { name: 'AI Agent', href: '/ai-agent', icon: Bot, color: 'from-violet-500 to-violet-600' },
    { name: 'Real-Time', href: '/real-time', icon: Activity, color: 'from-red-500 to-red-600' },
    
    // Core Features
    { name: 'Email Processing', href: '/email-processing', icon: Mail, color: 'from-emerald-500 to-emerald-600' },
    { name: 'Campaigns', href: '/campaigns', icon: Send, color: 'from-purple-500 to-purple-600' },
    { name: 'Prospects', href: '/prospects', icon: Users, color: 'from-green-500 to-green-600' },
    { name: 'Lists', href: '/lists', icon: FolderOpen, color: 'from-indigo-500 to-indigo-600' },
    { name: 'Templates', href: '/templates', icon: FileText, color: 'from-orange-500 to-orange-600' },
    { name: 'Intents', href: '/intents', icon: Brain, color: 'from-pink-500 to-pink-600' },
    { name: 'Analytics', href: '/analytics', icon: BarChart3, color: 'from-indigo-500 to-indigo-600' },
    
    // Advanced Features
    { name: 'Email Providers', href: '/email-providers', icon: Server, color: 'from-cyan-500 to-cyan-600' },
    { name: 'Knowledge Base', href: '/knowledge-base', icon: BookOpen, color: 'from-teal-500 to-teal-600' },
    { name: 'System Prompts', href: '/system-prompts', icon: MessageSquare, color: 'from-amber-500 to-amber-600' },
    { name: 'Response Verification', href: '/response-verification', icon: CheckCircle, color: 'from-rose-500 to-rose-600' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      <div className="flex h-screen">
        {/* Mobile menu button */}
        <div className="lg:hidden fixed top-0 left-0 right-0 z-50">
          <div className="flex items-center justify-between p-4 bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-100">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-xl font-bold gradient-text">AI Email Responder</h1>
            </div>
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <Menu className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className={`
          fixed inset-y-0 left-0 z-50 w-72 bg-white/80 backdrop-blur-xl shadow-2xl transform transition-transform duration-300 ease-in-out border-r border-gray-100
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:relative lg:flex lg:flex-col overflow-hidden
        `}>
          <div className="flex items-center justify-between p-6 border-b border-gray-100">
            <div className="flex items-center space-x-3 min-w-0">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg flex-shrink-0">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="text-xl font-bold gradient-text truncate">AI Email Responder</h1>
                <p className="text-xs text-gray-500 truncate">Powered by AI</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors flex-shrink-0"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <nav className="p-4 space-y-2 flex-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium transition-all duration-200 rounded-xl group min-w-0
                    ${isActive(item.href)
                      ? 'bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700 shadow-sm border border-blue-100'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <div className={`
                    p-2 rounded-lg mr-3 transition-all duration-200 flex-shrink-0
                    ${isActive(item.href) 
                      ? `bg-gradient-to-r ${item.color} text-white shadow-md` 
                      : 'bg-gray-100 text-gray-500 group-hover:bg-gray-200'
                    }
                  `}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <span className="font-medium truncate flex-1">{item.name}</span>
                  {isActive(item.href) && (
                    <div className="ml-auto w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex-shrink-0"></div>
                  )}
                </Link>
              );
            })}
          </nav>
          
          {/* Sidebar Footer */}
          <div className="p-4 border-t border-gray-100 space-y-4">
            {/* User Profile */}
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-xl">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                <User className="h-4 w-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.full_name || user?.username || 'User'}
                </p>
                <p className="text-xs text-gray-600 truncate">
                  {user?.email || 'No email'}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>

            {/* AI Status */}
            <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">AI Powered</p>
                  <p className="text-xs text-gray-600">Groq Integration Active</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col lg:pt-0 pt-20">
          <main className="flex-1 p-6 overflow-y-auto">
            {children}
          </main>
        </div>

        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </div>
    </div>
  );
};

export default Layout;