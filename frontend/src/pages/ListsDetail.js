import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Users, Edit, Trash2, UserPlus, UserMinus, Search, 
  Mail, Building, Phone, Calendar, Filter, Download, MoreHorizontal,
  CheckCircle, XCircle, Eye, AlertCircle 
} from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const ListsDetail = () => {
  const { listId } = useParams();
  const navigate = useNavigate();
  const [list, setList] = useState(null);
  const [prospects, setProspects] = useState([]);
  const [allProspects, setAllProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddProspectsModal, setShowAddProspectsModal] = useState(false);
  const [showEditListModal, setShowEditListModal] = useState(false);
  const [selectedProspects, setSelectedProspects] = useState([]);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadListDetails();
    loadAllProspects();
  }, [listId]);

  const loadListDetails = async () => {
    try {
      const response = await apiService.getList(listId);
      setList(response.data);
      setProspects(response.data.prospects || []);
    } catch (error) {
      toast.error('Failed to load list details');
      navigate('/lists');
    } finally {
      setLoading(false);
    }
  };

  const loadAllProspects = async () => {
    try {
      const response = await apiService.getProspects();
      setAllProspects(response.data);
    } catch (error) {
      console.error('Failed to load prospects:', error);
    }
  };

  const handleUpdateList = async (listData) => {
    try {
      await apiService.updateList(listId, listData);
      toast.success('List updated successfully');
      setShowEditListModal(false);
      loadListDetails();
    } catch (error) {
      toast.error('Failed to update list');
    }
  };

  const handleDeleteList = async () => {
    if (!window.confirm(`Are you sure you want to delete "${list.name}"?`)) return;
    
    try {
      await apiService.deleteList(listId);
      toast.success('List deleted successfully');
      navigate('/lists');
    } catch (error) {
      toast.error('Failed to delete list');
    }
  };

  const handleAddProspectsToList = async (prospectIds) => {
    try {
      await apiService.addProspectsToList(listId, prospectIds);
      toast.success(`Added ${prospectIds.length} prospects to list`);
      setShowAddProspectsModal(false);
      loadListDetails();
    } catch (error) {
      toast.error('Failed to add prospects to list');
    }
  };

  const handleRemoveProspectsFromList = async (prospectIds) => {
    if (!window.confirm(`Remove ${prospectIds.length} prospect(s) from this list?`)) return;
    
    try {
      await apiService.removeProspectsFromList(listId, prospectIds);
      toast.success(`Removed ${prospectIds.length} prospects from list`);
      setSelectedProspects([]);
      loadListDetails();
    } catch (error) {
      toast.error('Failed to remove prospects from list');
    }
  };

  const handleProspectToggle = (prospectId) => {
    setSelectedProspects(prev => 
      prev.includes(prospectId) 
        ? prev.filter(id => id !== prospectId)
        : [...prev, prospectId]
    );
  };

  const handleSelectAll = () => {
    const filteredProspectIds = filteredProspects.map(p => p.id);
    const allSelected = filteredProspectIds.every(id => selectedProspects.includes(id));
    
    if (allSelected) {
      // Remove all filtered prospects from selection
      setSelectedProspects(prev => prev.filter(id => !filteredProspectIds.includes(id)));
    } else {
      // Add all filtered prospects to selection (merge with existing)
      setSelectedProspects(prev => {
        const newSelected = [...prev];
        filteredProspectIds.forEach(id => {
          if (!newSelected.includes(id)) {
            newSelected.push(id);
          }
        });
        return newSelected;
      });
    }
  };

  const exportProspects = () => {
    const csvContent = [
      ['first_name', 'last_name', 'email', 'company', 'phone', 'job_title', 'status', 'created_at'].join(','),
      ...filteredProspects.map(prospect => [
        prospect.first_name || '',
        prospect.last_name || '',
        prospect.email || '',
        prospect.company || '',
        prospect.phone || '',
        prospect.job_title || '',
        prospect.status || '',
        new Date(prospect.created_at).toLocaleDateString()
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${list?.name || 'prospects'}_export.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const filteredProspects = prospects.filter(prospect => {
    const matchesSearch = 
      prospect.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prospect.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prospect.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prospect.company?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter = filterStatus === 'all' || prospect.status === filterStatus;

    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading list details...</p>
        </div>
      </div>
    );
  }

  if (!list) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">List Not Found</h2>
          <p className="text-gray-600 mb-4">The list you're looking for doesn't exist.</p>
          <button
            onClick={() => navigate('/lists')}
            className="btn btn-primary"
          >
            Back to Lists
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/lists')}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600" />
          </button>
          <div className="flex items-center space-x-3">
            <div 
              className="w-4 h-4 rounded-full" 
              style={{ backgroundColor: list.color }}
            ></div>
            <div>
              <h1 className="text-4xl font-bold gradient-text">{list.name}</h1>
              <p className="text-gray-600 mt-1">{list.description}</p>
            </div>
          </div>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowAddProspectsModal(true)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <UserPlus className="h-4 w-4" />
            <span>Add Prospects</span>
          </button>
          <button
            onClick={() => setShowEditListModal(true)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Edit className="h-4 w-4" />
            <span>Edit List</span>
          </button>
          <button
            onClick={handleDeleteList}
            className="btn btn-danger flex items-center space-x-2"
          >
            <Trash2 className="h-4 w-4" />
            <span>Delete List</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Prospects</p>
                <p className="text-2xl font-bold text-gray-900">{prospects.length}</p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-blue-500 to-blue-600">
                <Users className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-emerald-600">
                  {prospects.filter(p => p.status === 'active').length}
                </p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-emerald-500 to-emerald-600">
                <CheckCircle className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">With Companies</p>
                <p className="text-2xl font-bold text-purple-600">
                  {prospects.filter(p => p.company && p.company.length > 0).length}
                </p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-purple-500 to-purple-600">
                <Building className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Created</p>
                <p className="text-2xl font-bold text-orange-600">
                  {new Date(list.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-orange-500 to-orange-600">
                <Calendar className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search prospects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10 w-64"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input w-32"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="bounced">Bounced</option>
            </select>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {selectedProspects.length > 0 && (
            <button
              onClick={() => handleRemoveProspectsFromList(selectedProspects)}
              className="btn btn-danger flex items-center space-x-2"
            >
              <UserMinus className="h-4 w-4" />
              <span>Remove Selected ({selectedProspects.length})</span>
            </button>
          )}
          <button
            onClick={exportProspects}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Tags */}
      {list.tags && list.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {list.tags.map((tag, index) => (
            <span key={index} className="badge badge-info">
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Prospects Table */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Prospects in {list.name} ({filteredProspects.length})
            </h3>
            <button
              onClick={handleSelectAll}
              className="btn btn-secondary btn-sm"
            >
              {selectedProspects.length === filteredProspects.length ? 'Deselect All' : 'Select All'}
            </button>
          </div>

          {filteredProspects.length === 0 ? (
            <div className="text-center py-12">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No prospects found</h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || filterStatus !== 'all' 
                  ? 'Try adjusting your search or filter criteria'
                  : 'Start by adding some prospects to this list'
                }
              </p>
              {!searchTerm && filterStatus === 'all' && (
                <button
                  onClick={() => setShowAddProspectsModal(true)}
                  className="btn btn-primary"
                >
                  Add Prospects
                </button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th className="table-header">
                      <input
                        type="checkbox"
                        checked={filteredProspects.map(p => p.id).every(id => selectedProspects.includes(id)) && filteredProspects.length > 0}
                        onChange={handleSelectAll}
                        className="h-4 w-4 text-blue-600 rounded"
                      />
                    </th>
                    <th className="table-header">Name</th>
                    <th className="table-header">Email</th>
                    <th className="table-header">Company</th>
                    <th className="table-header">Phone</th>
                    <th className="table-header">Status</th>
                    <th className="table-header">Added</th>
                    <th className="table-header">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProspects.map((prospect) => (
                    <tr key={prospect.id} className="table-row">
                      <td className="table-cell">
                        <input
                          type="checkbox"
                          checked={selectedProspects.includes(prospect.id)}
                          onChange={() => handleProspectToggle(prospect.id)}
                          className="h-4 w-4 text-blue-600 rounded"
                        />
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                            {prospect.first_name?.[0] || prospect.email?.[0] || '?'}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">
                              {prospect.first_name} {prospect.last_name}
                            </div>
                            <div className="text-sm text-gray-500">{prospect.job_title}</div>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center space-x-2">
                          <Mail className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-900">{prospect.email}</span>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center space-x-2">
                          <Building className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-900">{prospect.company || 'N/A'}</span>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center space-x-2">
                          <Phone className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-900">{prospect.phone || 'N/A'}</span>
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className={`badge ${
                          prospect.status === 'active' 
                            ? 'badge-success' 
                            : prospect.status === 'bounced' 
                              ? 'badge-danger'
                              : 'badge-secondary'
                        }`}>
                          {prospect.status || 'active'}
                        </span>
                      </td>
                      <td className="table-cell text-gray-500">
                        {new Date(prospect.created_at).toLocaleDateString()}
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleRemoveProspectsFromList([prospect.id])}
                            className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                            title="Remove from list"
                          >
                            <UserMinus className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Add Prospects Modal */}
      {showAddProspectsModal && (
        <AddProspectsToListModal
          list={list}
          prospects={allProspects}
          onClose={() => setShowAddProspectsModal(false)}
          onSubmit={handleAddProspectsToList}
        />
      )}

      {/* Edit List Modal */}
      {showEditListModal && (
        <EditListModal
          list={list}
          onClose={() => setShowEditListModal(false)}
          onSubmit={handleUpdateList}
        />
      )}
    </div>
  );
};

// Add Prospects Modal Component
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
    (prospect.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
     prospect.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
     prospect.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
     prospect.company?.toLowerCase().includes(searchTerm.toLowerCase()))
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
                    className={`p-4 border rounded-lg transition-colors cursor-pointer ${
                      selectedProspects.includes(prospect.id) 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleProspectToggle(prospect.id)}
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

// Edit List Modal Component
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
                      <XCircle className="h-3 w-3" />
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

export default ListsDetail;