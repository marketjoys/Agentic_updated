import React, { useState, useEffect } from 'react';
import { Upload, Plus, Search, Users, Mail, Building, Phone, Download, RefreshCw, UserCheck, AlertCircle, X, Sparkles } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import AIProspectorModal from '../components/AIProspectorModal';
import useEscapeKey from '../hooks/useEscapeKey';

const Prospects = () => {
  const [prospects, setProspects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showAIProspector, setShowAIProspector] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadProspects();
  }, []);

  const loadProspects = async () => {
    try {
      const response = await apiService.getProspects();
      setProspects(response.data);
    } catch (error) {
      toast.error('Failed to load prospects');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const response = await apiService.uploadProspects(file);
      toast.success(response.data.message);
      loadProspects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload prospects');
    } finally {
      setUploading(false);
    }
  };

  const handleAddProspect = async (prospectData) => {
    try {
      await apiService.createProspect(prospectData);
      toast.success('Prospect added successfully');
      setShowAddModal(false);
      loadProspects();
    } catch (error) {
      toast.error('Failed to add prospect');
    }
  };

  const downloadSampleCSV = async () => {
    try {
      const response = await apiService.api.get('/api/sample-csv');
      const csvContent = response.data.content;
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      // Fallback to hardcoded CSV if API fails
      const csvContent = `email,first_name,last_name,company,phone,linkedin_url,company_domain,industry,company_linkedin_url,job_title,location,company_size,annual_revenue,lead_source
john.doe@example.com,John,Doe,Example Corp,+1-555-0123,https://linkedin.com/in/john-doe,example.com,Technology,https://linkedin.com/company/example-corp,CEO,San Francisco CA,100-500,$10M-$50M,Website
jane.smith@test.com,Jane,Smith,Test Inc,+1-555-0456,https://linkedin.com/in/jane-smith,test.com,Software,https://linkedin.com/company/test-inc,CTO,New York NY,50-100,$5M-$10M,LinkedIn
mark.wilson@demo.org,Mark,Wilson,Demo Solutions,+1-555-0789,https://linkedin.com/in/mark-wilson,demo.org,Consulting,https://linkedin.com/company/demo-solutions,VP Sales,Austin TX,200-500,$25M-$50M,Referral`;
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'prospects_sample.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    }
  };

  const handleAIProspectsAdded = (count) => {
    // Refresh prospects list after AI prospecting
    loadProspects();
    toast.success(`${count} prospects added via AI prospecting!`);
  };

  const filteredProspects = prospects.filter(prospect =>
    prospect.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    prospect.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    prospect.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    prospect.company.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading prospects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text">Prospects</h1>
          <p className="text-gray-600 mt-2">Manage your email prospects and leads</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowAIProspector(true)}
            className="btn btn-gradient flex items-center space-x-2"
          >
            <Sparkles className="h-4 w-4" />
            <span>AI Prospector</span>
          </button>
          <button
            onClick={downloadSampleCSV}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Sample CSV</span>
          </button>
          <label className="btn btn-secondary cursor-pointer flex items-center space-x-2">
            {uploading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                <span>Upload CSV</span>
              </>
            )}
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add Prospect</span>
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
                <UserCheck className="h-5 w-5 text-white" />
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
                <p className="text-sm font-medium text-gray-600">Recently Added</p>
                <p className="text-2xl font-bold text-orange-600">
                  {prospects.filter(p => {
                    const created = new Date(p.created_at);
                    const today = new Date();
                    const diffTime = Math.abs(today - created);
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    return diffDays <= 7;
                  }).length}
                </p>
              </div>
              <div className="icon-wrapper bg-gradient-to-r from-orange-500 to-orange-600">
                <AlertCircle className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <div className="card-body">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search prospects by name, email, or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
      </div>

      {/* Upload Instructions */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Upload className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">CSV Upload Instructions</h3>
              <p className="text-gray-600 mb-3">
                Upload a CSV file with the following required columns: <strong>email</strong>, <strong>first_name</strong>, <strong>last_name</strong>
              </p>
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Optional columns:</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-sm text-gray-600">
                  <span>• company</span>
                  <span>• phone</span>
                  <span>• linkedin_url</span>
                  <span>• company_domain</span>
                  <span>• industry</span>
                  <span>• company_linkedin_url</span>
                  <span>• job_title</span>
                  <span>• location</span>
                  <span>• company_size</span>
                  <span>• annual_revenue</span>
                  <span>• lead_source</span>
                  <span>• + custom fields</span>
                </div>
              </div>
              <p className="text-sm text-gray-500 mb-4">
                <strong>Note:</strong> You can include any additional custom fields in your CSV - they will be stored as additional fields for each prospect.
              </p>
              <div className="flex items-center space-x-4">
                <button
                  onClick={downloadSampleCSV}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Download Sample CSV
                </button>
                <span className="text-gray-300">|</span>
                <a
                  href="/sample_prospects.csv"
                  download
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Download Pre-filled Sample
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Prospects Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-xl font-bold text-gray-900">
            All Prospects ({filteredProspects.length})
          </h3>
        </div>
        <div className="card-body p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="table-header">Name</th>
                  <th className="table-header">Email</th>
                  <th className="table-header">Company</th>
                  <th className="table-header">Phone</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Added</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredProspects.map((prospect) => (
                  <tr key={prospect.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="table-cell">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg">
                          <Users className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">
                            {prospect.first_name} {prospect.last_name}
                          </div>
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
                          : 'badge-danger'
                      }`}>
                        {prospect.status}
                      </span>
                    </td>
                    <td className="table-cell text-gray-500">
                      {new Date(prospect.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Add Prospect Modal */}
      {showAddModal && (
        <AddProspectModal
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddProspect}
        />
      )}

      {/* AI Prospector Modal */}
      <AIProspectorModal
        isOpen={showAIProspector}
        onClose={() => setShowAIProspector(false)}
        onProspectsAdded={handleAIProspectsAdded}
      />
    </div>
  );
};

const AddProspectModal = ({ onClose, onSubmit }) => {
  // Add escape key functionality
  useEscapeKey(onClose, true);
  
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    company: '',
    phone: '',
    linkedin_url: '',
    company_domain: '',
    industry: '',
    company_linkedin_url: '',
    job_title: '',
    location: '',
    company_size: '',
    annual_revenue: '',
    lead_source: ''
  });

  const [additionalFields, setAdditionalFields] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Add additional fields to the form data
    const additional_fields = {};
    additionalFields.forEach(field => {
      if (field.key && field.value) {
        additional_fields[field.key] = field.value;
      }
    });
    
    const finalData = {
      ...formData,
      additional_fields: additional_fields
    };
    
    onSubmit(finalData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const addAdditionalField = () => {
    setAdditionalFields([...additionalFields, { key: '', value: '' }]);
  };

  const removeAdditionalField = (index) => {
    setAdditionalFields(additionalFields.filter((_, i) => i !== index));
  };

  const handleAdditionalFieldChange = (index, field, value) => {
    const updated = [...additionalFields];
    updated[index][field] = value;
    setAdditionalFields(updated);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-4xl">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-xl font-bold text-gray-900">Add New Prospect</h3>
          <p className="text-gray-600 mt-1">Add a new prospect to your database</p>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="input"
                  required
                  placeholder="john.doe@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="input"
                  placeholder="+1-555-0123"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="input"
                  required
                  placeholder="John"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="input"
                  required
                  placeholder="Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title
                </label>
                <input
                  type="text"
                  name="job_title"
                  value={formData.job_title}
                  onChange={handleChange}
                  className="input"
                  placeholder="CEO"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  className="input"
                  placeholder="San Francisco, CA"
                />
              </div>
            </div>
          </div>

          {/* Company Information */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-4">Company Information</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company
                </label>
                <input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  className="input"
                  placeholder="Example Corp"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Domain
                </label>
                <input
                  type="text"
                  name="company_domain"
                  value={formData.company_domain}
                  onChange={handleChange}
                  className="input"
                  placeholder="example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <input
                  type="text"
                  name="industry"
                  value={formData.industry}
                  onChange={handleChange}
                  className="input"
                  placeholder="Technology"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Size
                </label>
                <select
                  name="company_size"
                  value={formData.company_size}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select size...</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-100">51-100 employees</option>
                  <option value="101-500">101-500 employees</option>
                  <option value="501-1000">501-1000 employees</option>
                  <option value="1000+">1000+ employees</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Annual Revenue
                </label>
                <select
                  name="annual_revenue"
                  value={formData.annual_revenue}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select range...</option>
                  <option value="$0-$1M">$0-$1M</option>
                  <option value="$1M-$5M">$1M-$5M</option>
                  <option value="$5M-$10M">$5M-$10M</option>
                  <option value="$10M-$50M">$10M-$50M</option>
                  <option value="$50M-$100M">$50M-$100M</option>
                  <option value="$100M+">$100M+</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lead Source
                </label>
                <select
                  name="lead_source"
                  value={formData.lead_source}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select source...</option>
                  <option value="Website">Website</option>
                  <option value="LinkedIn">LinkedIn</option>
                  <option value="Referral">Referral</option>
                  <option value="Conference">Conference</option>
                  <option value="Social Media">Social Media</option>
                  <option value="Cold Email">Cold Email</option>
                  <option value="Partnership">Partnership</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* LinkedIn URLs */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-4">LinkedIn Information</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  LinkedIn URL
                </label>
                <input
                  type="url"
                  name="linkedin_url"
                  value={formData.linkedin_url}
                  onChange={handleChange}
                  className="input"
                  placeholder="https://linkedin.com/in/john-doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company LinkedIn URL
                </label>
                <input
                  type="url"
                  name="company_linkedin_url"
                  value={formData.company_linkedin_url}
                  onChange={handleChange}
                  className="input"
                  placeholder="https://linkedin.com/company/example-corp"
                />
              </div>
            </div>
          </div>

          {/* Additional Fields */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium text-gray-900">Additional Fields</h4>
              <button
                type="button"
                onClick={addAdditionalField}
                className="btn btn-secondary text-sm"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add Field
              </button>
            </div>
            {additionalFields.map((field, index) => (
              <div key={index} className="flex items-center space-x-3 mb-3">
                <input
                  type="text"
                  placeholder="Field name"
                  value={field.key}
                  onChange={(e) => handleAdditionalFieldChange(index, 'key', e.target.value)}
                  className="input flex-1"
                />
                <input
                  type="text"
                  placeholder="Field value"
                  value={field.value}
                  onChange={(e) => handleAdditionalFieldChange(index, 'value', e.target.value)}
                  className="input flex-1"
                />
                <button
                  type="button"
                  onClick={() => removeAdditionalField(index)}
                  className="p-2 text-red-500 hover:text-red-700"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
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
              Add Prospect
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Prospects;