import React, { useState, useEffect } from 'react';
import { Plus, Search, BookOpen, Tag, Edit, Trash2, Eye, Upload, Download, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const KnowledgeBase = () => {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [statistics, setStatistics] = useState({});
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'general',
    tags: [],
    keywords: [],
    is_active: true
  });

  useEffect(() => {
    fetchArticles();
    fetchStatistics();
  }, []);

  const fetchArticles = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/knowledge-base`);
      setArticles(response.data);
      
      // Extract unique categories
      const uniqueCategories = [...new Set(response.data.map(article => article.category))];
      setCategories(uniqueCategories);
    } catch (error) {
      console.error('Error fetching articles:', error);
      toast.error('Failed to load knowledge base articles');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/knowledge-base/statistics/overview`);
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleAddArticle = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${BACKEND_URL}/api/knowledge-base`, {
        ...formData,
        tags: formData.tags.filter(tag => tag.trim() !== ''),
        keywords: formData.keywords.filter(keyword => keyword.trim() !== '')
      });
      toast.success('Knowledge article added successfully');
      setShowAddModal(false);
      resetForm();
      fetchArticles();
      fetchStatistics();
    } catch (error) {
      console.error('Error adding article:', error);
      toast.error('Failed to add knowledge article');
    }
  };

  const handleEditArticle = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${BACKEND_URL}/api/knowledge-base/${selectedArticle.id}`, {
        ...formData,
        tags: formData.tags.filter(tag => tag.trim() !== ''),
        keywords: formData.keywords.filter(keyword => keyword.trim() !== '')
      });
      toast.success('Knowledge article updated successfully');
      setShowEditModal(false);
      setSelectedArticle(null);
      resetForm();
      fetchArticles();
    } catch (error) {
      console.error('Error updating article:', error);
      toast.error('Failed to update knowledge article');
    }
  };

  const handleDeleteArticle = async (articleId) => {
    if (window.confirm('Are you sure you want to delete this knowledge article?')) {
      try {
        await axios.delete(`${BACKEND_URL}/api/knowledge-base/${articleId}`);
        toast.success('Knowledge article deleted successfully');
        fetchArticles();
        fetchStatistics();
      } catch (error) {
        console.error('Error deleting article:', error);
        toast.error('Failed to delete knowledge article');
      }
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      fetchArticles();
      return;
    }

    try {
      const response = await axios.get(`${BACKEND_URL}/api/knowledge-base/search`, {
        params: { 
          query: searchTerm,
          category: selectedCategory || undefined
        }
      });
      setArticles(response.data);
    } catch (error) {
      console.error('Error searching articles:', error);
      toast.error('Failed to search articles');
    }
  };

  const handleBulkImport = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${BACKEND_URL}/api/knowledge-base/bulk-import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      toast.success('Articles imported successfully');
      fetchArticles();
      fetchStatistics();
    } catch (error) {
      console.error('Error importing articles:', error);
      toast.error('Failed to import articles');
    }
    
    event.target.value = '';
  };

  const handleBulkExport = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/knowledge-base/bulk-export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'knowledge-base-export.json');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Articles exported successfully');
    } catch (error) {
      console.error('Error exporting articles:', error);
      toast.error('Failed to export articles');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      category: 'general',
      tags: [],
      keywords: [],
      is_active: true
    });
  };

  const openEditModal = (article) => {
    setSelectedArticle(article);
    setFormData({
      title: article.title,
      content: article.content,
      category: article.category,
      tags: article.tags || [],
      keywords: article.keywords || [],
      is_active: article.is_active
    });
    setShowEditModal(true);
  };

  const openViewModal = (article) => {
    setSelectedArticle(article);
    setShowViewModal(true);
  };

  const handleTagsChange = (value) => {
    const tags = value.split(',').map(tag => tag.trim());
    setFormData({...formData, tags});
  };

  const handleKeywordsChange = (value) => {
    const keywords = value.split(',').map(keyword => keyword.trim());
    setFormData({...formData, keywords});
  };

  const filteredArticles = articles.filter(article => {
    const matchesSearch = !searchTerm || 
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.content.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = !selectedCategory || article.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const ArticleModal = ({ show, onClose, onSubmit, title, isEdit = false }) => {
    if (!show) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="general">General</option>
                  <option value="product">Product</option>
                  <option value="pricing">Pricing</option>
                  <option value="support">Support</option>
                  <option value="sales">Sales</option>
                  <option value="technical">Technical</option>
                  <option value="industry">Industry</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Content</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
                rows={10}
                className="w-full px-3 py-2 border rounded-md"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Tags (comma-separated)</label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={(e) => handleTagsChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="tag1, tag2, tag3"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Keywords (comma-separated)</label>
                <input
                  type="text"
                  value={formData.keywords.join(', ')}
                  onChange={(e) => handleKeywordsChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="keyword1, keyword2, keyword3"
                />
              </div>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  className="mr-2"
                />
                Active
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {isEdit ? 'Update' : 'Add'} Article
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const ViewModal = ({ show, onClose, article }) => {
    if (!show || !article) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">{article.title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                {article.category}
              </span>
              <span>Used {article.usage_count || 0} times</span>
              <span>Created {new Date(article.created_at).toLocaleDateString()}</span>
            </div>

            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap">{article.content}</div>
            </div>

            {article.tags && article.tags.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Tags:</h3>
                <div className="flex flex-wrap gap-2">
                  {article.tags.map((tag, index) => (
                    <span key={index} className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {article.keywords && article.keywords.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Keywords:</h3>
                <div className="flex flex-wrap gap-2">
                  {article.keywords.map((keyword, index) => (
                    <span key={index} className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
          <p className="text-gray-600">Manage your AI knowledge articles and documentation</p>
        </div>
        <div className="flex space-x-3">
          <input
            type="file"
            accept=".json,.csv"
            onChange={handleBulkImport}
            className="hidden"
            id="bulk-import"
          />
          <button
            onClick={() => document.getElementById('bulk-import').click()}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
          >
            <Upload className="w-4 h-4" />
            <span>Import</span>
          </button>
          <button
            onClick={handleBulkExport}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Article</span>
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Articles</p>
              <p className="text-2xl font-bold text-gray-900">{statistics.total_articles || 0}</p>
            </div>
            <BookOpen className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Articles</p>
              <p className="text-2xl font-bold text-gray-900">{statistics.active_articles || 0}</p>
            </div>
            <Eye className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Categories</p>
              <p className="text-2xl font-bold text-gray-900">{statistics.categories?.length || 0}</p>
            </div>
            <Tag className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="flex space-x-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search articles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg"
            />
          </div>
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Search className="w-4 h-4" />
            <span>Search</span>
          </button>
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredArticles.map((article) => (
          <div key={article.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-gray-900 line-clamp-2">{article.title}</h3>
              <span className={`px-2 py-1 text-xs rounded ${
                article.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {article.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            
            <p className="text-gray-600 text-sm mb-3 line-clamp-3">
              {article.content.substring(0, 150)}...
            </p>
            
            <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                {article.category}
              </span>
              <span>Used {article.usage_count || 0} times</span>
            </div>
            
            {article.tags && article.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {article.tags.slice(0, 3).map((tag, index) => (
                  <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                    {tag}
                  </span>
                ))}
                {article.tags.length > 3 && (
                  <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                    +{article.tags.length - 3} more
                  </span>
                )}
              </div>
            )}
            
            <div className="flex space-x-2">
              <button
                onClick={() => openViewModal(article)}
                className="flex-1 bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-4 h-4" />
                <span>View</span>
              </button>
              
              <button
                onClick={() => openEditModal(article)}
                className="bg-yellow-600 text-white py-2 px-3 rounded-md hover:bg-yellow-700 flex items-center justify-center"
              >
                <Edit className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => handleDeleteArticle(article.id)}
                className="bg-red-600 text-white py-2 px-3 rounded-md hover:bg-red-700 flex items-center justify-center"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredArticles.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || selectedCategory 
              ? 'Try adjusting your search or filter criteria'
              : 'Add your first knowledge article to get started'
            }
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Add Article
          </button>
        </div>
      )}

      <ArticleModal
        show={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddArticle}
        title="Add Knowledge Article"
      />

      <ArticleModal
        show={showEditModal}
        onClose={() => setShowEditModal(false)}
        onSubmit={handleEditArticle}
        title="Edit Knowledge Article"
        isEdit={true}
      />

      <ViewModal
        show={showViewModal}
        onClose={() => setShowViewModal(false)}
        article={selectedArticle}
      />
    </div>
  );
};

export default KnowledgeBase;