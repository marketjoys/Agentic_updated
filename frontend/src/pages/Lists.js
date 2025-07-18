import React, { useState, useEffect } from 'react';
import { Plus, Search, Users, Tag, Edit, Trash2, FolderPlus, UserPlus, X } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Lists = () => {
  const [lists, setLists] = useState([]);
  const [prospects, setProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedList, setSelectedList] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAddProspectsModal, setShowAddProspectsModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [listsResponse, prospectsResponse] = await Promise.all([
        apiService.getLists(),
        apiService.getProspects()
      ]);
      setLists(listsResponse.data);
      setProspects(prospectsResponse.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateList = async (listData) => {
    try {
      await apiService.createList(listData);
      toast.success('List created successfully');
      setShowCreateModal(false);
      loadData();
    } catch (error) {
      toast.error('Failed to create list');
    }
  };

  const handleUpdateList = async (listData) => {
    try {
      await apiService.updateList(selectedList.id, listData);
      toast.success('List updated successfully');
      setShowEditModal(false);
      setSelectedList(null);
      loadData();
    } catch (error) {
      toast.error('Failed to update list');
    }
  };

  const handleDeleteList = async (listId) => {
    if (!window.confirm('Are you sure you want to delete this list?')) return;
    
    try {
      await apiService.deleteList(listId);
      toast.success('List deleted successfully');
      loadData();
    } catch (error) {
      toast.error('Failed to delete list');
    }
  };

  const handleAddProspectsToList = async (listId, prospectIds) => {
    try {
      await apiService.addProspectsToList(listId, prospectIds);
      toast.success('Prospects added to list successfully');
      loadData();
      setShowAddProspectsModal(false);
      setSelectedList(null);
    } catch (error) {
      toast.error('Failed to add prospects to list');
    }
  };

  const handleShowAddProspects = (list) => {
    setSelectedList(list);
    setShowAddProspectsModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading lists...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text">Prospect Lists</h1>
          <p className="text-gray-600 mt-2">Organize prospects into targeted lists</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create List</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Lists</p>
                <p className="text-2xl font-bold text-gray-900">{lists.length}</p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-blue-500 to-blue-600">
                <FolderPlus className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Prospects</p>
                <p className="text-2xl font-bold text-emerald-600">{prospects.length}</p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-emerald-500 to-emerald-600">
                <Users className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. List Size</p>
                <p className="text-2xl font-bold text-purple-600">
                  {lists.length > 0 ? Math.round(lists.reduce((sum, list) => sum + list.prospect_count, 0) / lists.length) : 0}
                </p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-purple-500 to-purple-600">
                <UserPlus className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Tags</p>
                <p className="text-2xl font-bold text-orange-600">
                  {new Set(lists.flatMap(list => list.tags || [])).size}
                </p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-orange-500 to-orange-600">
                <Tag className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lists Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {lists.map((list) => (
          <div key={list.id} className="card card-hover">
            <div className="card-body">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full" 
                    style={{ backgroundColor: list.color }}
                  ></div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{list.name}</h3>
                    <p className="text-sm text-gray-600">{list.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleShowAddProspects(list)}
                    className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                    title="Add Prospects"
                  >
                    <UserPlus className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      setSelectedList(list);
                      setShowEditModal(true);
                    }}
                    className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteList(list.id)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">{list.prospect_count} prospects</span>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(list.created_at).toLocaleDateString()}
                </div>
              </div>

              {list.tags && list.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {list.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="badge badge-info text-xs">
                      {tag}
                    </span>
                  ))}
                  {list.tags.length > 3 && (
                    <span className="text-xs text-gray-500">+{list.tags.length - 3}</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create List Modal */}
      {showCreateModal && (
        <CreateListModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateList}
        />
      )}

      {/* Edit List Modal */}
      {showEditModal && selectedList && (
        <EditListModal
          list={selectedList}
          onClose={() => {
            setShowEditModal(false);
            setSelectedList(null);
          }}
          onSubmit={handleUpdateList}
        />
      )}

      {/* Add Prospects to List Modal */}
      {showAddProspectsModal && selectedList && (
        <AddProspectsToListModal
          list={selectedList}
          prospects={prospects}
          onClose={() => {
            setShowAddProspectsModal(false);
            setSelectedList(null);
          }}
          onSubmit={(prospectIds) => handleAddProspectsToList(selectedList.id, prospectIds)}
        />
      )}
    </div>
  );
};

const CreateListModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#3B82F6',
    tags: []
  });
  const [tagInput, setTagInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
  ];

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-xl font-bold text-gray-900">Create New List</h3>
          <p className="text-gray-600 mt-1">Create a new prospect list</p>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              List Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              required
              placeholder="Technology Companies"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input h-20 resize-none"
              placeholder="Description of this prospect list..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Color
            </label>
            <div className="flex space-x-2">
              {colors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData({ ...formData, color })}
                  className={`w-8 h-8 rounded-full border-2 ${
                    formData.color === color ? 'border-gray-400' : 'border-gray-200'
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <div className="flex items-center space-x-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                className="input flex-1"
                placeholder="Add a tag..."
              />
              <button
                type="button"
                onClick={addTag}
                className="btn btn-secondary"
              >
                Add
              </button>
            </div>
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag, index) => (
                  <span key={index} className="badge badge-info flex items-center space-x-1">
                    <span>{tag}</span>
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-6">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
            >
              Create List
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const EditListModal = ({ list, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: list.name,
    description: list.description || '',
    color: list.color,
    tags: list.tags || []
  });
  const [tagInput, setTagInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
  ];

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-xl font-bold text-gray-900">Edit List</h3>
          <p className="text-gray-600 mt-1">Update list information</p>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              List Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input h-20 resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Color
            </label>
            <div className="flex space-x-2">
              {colors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData({ ...formData, color })}
                  className={`w-8 h-8 rounded-full border-2 ${
                    formData.color === color ? 'border-gray-400' : 'border-gray-200'
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <div className="flex items-center space-x-2 mb-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                className="input flex-1"
                placeholder="Add a tag..."
              />
              <button
                type="button"
                onClick={addTag}
                className="btn btn-secondary"
              >
                Add
              </button>
            </div>
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag, index) => (
                  <span key={index} className="badge badge-info flex items-center space-x-1">
                    <span>{tag}</span>
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-6">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
            >
              Update List
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const AddProspectsToListModal = ({ list, prospects, onClose, onSubmit }) => {
  const [selectedProspects, setSelectedProspects] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedProspects.length === 0) {
      toast.error('Please select at least one prospect');
      return;
    }
    onSubmit(selectedProspects);
  };

  const handleProspectToggle = (prospectId) => {
    setSelectedProspects(prev => 
      prev.includes(prospectId) 
        ? prev.filter(id => id !== prospectId)
        : [...prev, prospectId]
    );
  };

  const filteredProspects = prospects.filter(prospect => 
    !prospect.list_ids?.includes(list.id) && // Don't show prospects already in this list
    (prospect.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
     prospect.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
     prospect.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
     prospect.company.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-4xl">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-xl font-bold text-gray-900">Add Prospects to {list.name}</h3>
          <p className="text-gray-600 mt-1">Select prospects to add to this list</p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search prospects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>

          {/* Prospects List */}
          <div className="max-h-96 overflow-y-auto mb-6">
            {filteredProspects.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No prospects available to add to this list
              </div>
            ) : (
              <div className="space-y-2">
                {filteredProspects.map((prospect) => (
                  <div
                    key={prospect.id}
                    className={`p-4 border rounded-lg transition-colors ${
                      selectedProspects.includes(prospect.id) 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedProspects.includes(prospect.id)}
                          onChange={(e) => {
                            e.stopPropagation();
                            handleProspectToggle(prospect.id);
                          }}
                          className="h-4 w-4 text-blue-600 rounded"
                        />
                        <div>
                          <div className="font-medium text-gray-900">
                            {prospect.first_name} {prospect.last_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {prospect.email} • {prospect.company || 'No company'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Selected Count */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <div className="text-sm text-blue-800">
              {selectedProspects.length} prospect(s) selected
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={selectedProspects.length === 0}
            >
              Add {selectedProspects.length} Prospect(s)
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Lists;