import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, AlertCircle, Eye, Edit, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ResponseVerification = () => {
  const [verifications, setVerifications] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending');
  const [showViewModal, setShowViewModal] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [selectedVerification, setSelectedVerification] = useState(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [suggestedChanges, setSuggestedChanges] = useState('');
  const [editedContent, setEditedContent] = useState('');

  useEffect(() => {
    fetchVerifications();
    fetchStatistics();
  }, [filter]);

  const fetchVerifications = async () => {
    try {
      const endpoint = filter === 'pending' 
        ? `${BACKEND_URL}/api/response-verification/pending`
        : `${BACKEND_URL}/api/response-verification`;
      
      const response = await axios.get(endpoint);
      setVerifications(response.data);
    } catch (error) {
      console.error('Error fetching verifications:', error);
      toast.error('Failed to load verifications');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/response-verification/statistics`);
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleApprove = async (verificationId) => {
    try {
      await axios.post(`${BACKEND_URL}/api/response-verification/${verificationId}/approve`, {
        reviewer: 'Manual Review',
        notes: reviewNotes
      });
      toast.success('Response approved successfully');
      setShowReviewModal(false);
      fetchVerifications();
      fetchStatistics();
    } catch (error) {
      console.error('Error approving verification:', error);
      toast.error('Failed to approve response');
    }
  };

  const handleReject = async (verificationId) => {
    try {
      await axios.post(`${BACKEND_URL}/api/response-verification/${verificationId}/reject`, {
        reviewer: 'Manual Review',
        notes: reviewNotes,
        suggested_changes: suggestedChanges
      });
      toast.success('Response rejected successfully');
      setShowReviewModal(false);
      fetchVerifications();
      fetchStatistics();
    } catch (error) {
      console.error('Error rejecting verification:', error);
      toast.error('Failed to reject response');
    }
  };

  const handleUpdateContent = async (verificationId) => {
    try {
      await axios.put(`${BACKEND_URL}/api/response-verification/${verificationId}/content`, {
        content: editedContent
      });
      toast.success('Response content updated successfully');
      setShowReviewModal(false);
      fetchVerifications();
    } catch (error) {
      console.error('Error updating content:', error);
      toast.error('Failed to update content');
    }
  };

  const openViewModal = (verification) => {
    setSelectedVerification(verification);
    setShowViewModal(true);
  };

  const openReviewModal = (verification) => {
    setSelectedVerification(verification);
    setReviewNotes('');
    setSuggestedChanges('');
    setEditedContent(verification.verified_content || verification.original_content);
    setShowReviewModal(true);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'needs_review':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'needs_review':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const ViewModal = ({ show, onClose, verification }) => {
    if (!show || !verification) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Response Verification Details</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Status</h3>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(verification.status)}
                  <span className={`px-2 py-1 text-sm rounded ${getStatusColor(verification.status)}`}>
                    {verification.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Overall Score</h3>
                <span className={`text-2xl font-bold ${getScoreColor(verification.overall_score)}`}>
                  {(verification.overall_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Verification Scores</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Context Alignment:</span>
                    <span className={getScoreColor(verification.context_score)}>
                      {(verification.context_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Intent Accuracy:</span>
                    <span className={getScoreColor(verification.intent_alignment_score)}>
                      {(verification.intent_alignment_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Content Quality:</span>
                    <span className={getScoreColor(verification.content_quality_score)}>
                      {(verification.content_quality_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Personalization:</span>
                    <span className={getScoreColor(verification.personalization_score)}>
                      {(verification.personalization_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Professional Tone:</span>
                    <span className={getScoreColor(verification.tone_score)}>
                      {(verification.tone_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Verification Notes</h3>
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-sm text-gray-700">
                    {verification.verification_notes || 'No notes available'}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Original Content</h3>
              <div className="bg-gray-50 p-4 rounded-md">
                <pre className="whitespace-pre-wrap text-sm text-gray-700">
                  {verification.original_content}
                </pre>
              </div>
            </div>

            {verification.verified_content !== verification.original_content && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Verified Content</h3>
                <div className="bg-blue-50 p-4 rounded-md">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {verification.verified_content}
                  </pre>
                </div>
              </div>
            )}

            {verification.suggested_changes && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Suggested Changes</h3>
                <div className="bg-yellow-50 p-4 rounded-md">
                  <p className="text-sm text-gray-700">{verification.suggested_changes}</p>
                </div>
              </div>
            )}

            {verification.manual_review_notes && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Manual Review Notes</h3>
                <div className="bg-green-50 p-4 rounded-md">
                  <p className="text-sm text-gray-700">{verification.manual_review_notes}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Reviewed by: {verification.manual_reviewer}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const ReviewModal = ({ show, onClose, verification }) => {
    if (!show || !verification) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Manual Review</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Overall Score</h3>
                <span className={`text-2xl font-bold ${getScoreColor(verification.overall_score)}`}>
                  {(verification.overall_score * 100).toFixed(1)}%
                </span>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Verification Notes</h3>
                <p className="text-sm text-gray-700">{verification.verification_notes}</p>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Original Content</h3>
              <div className="bg-gray-50 p-4 rounded-md">
                <pre className="whitespace-pre-wrap text-sm text-gray-700">
                  {verification.original_content}
                </pre>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Edit Content (Optional)</h3>
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                rows={8}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Review Notes</h3>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="Add your review notes..."
              />
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Suggested Changes (if rejecting)</h3>
              <textarea
                value={suggestedChanges}
                onChange={(e) => setSuggestedChanges(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="Suggest specific improvements..."
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              
              {editedContent !== verification.original_content && (
                <button
                  onClick={() => handleUpdateContent(verification.id)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Update Content
                </button>
              )}
              
              <button
                onClick={() => handleReject(verification.id)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Reject
              </button>
              
              <button
                onClick={() => handleApprove(verification.id)}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Approve
              </button>
            </div>
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
          <h1 className="text-2xl font-bold text-gray-900">Response Verification</h1>
          <p className="text-gray-600">Review and approve AI-generated responses</p>
        </div>
        <div className="flex space-x-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="pending">Pending Review</option>
            <option value="needs_review">Needs Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Verifications</p>
              <p className="text-2xl font-bold text-gray-900">{statistics.total_verifications || 0}</p>
            </div>
            <MessageSquare className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{statistics.pending_verifications || 0}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-gray-900">{statistics.approved_verifications || 0}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-gray-900">{statistics.rejected_verifications || 0}</p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Verifications List */}
      <div className="space-y-4">
        {verifications.map((verification) => (
          <div key={verification.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center space-x-3">
                {getStatusIcon(verification.status)}
                <div>
                  <h3 className="font-semibold text-gray-900">
                    Verification #{verification.id.substring(0, 8)}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Created {new Date(verification.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded ${getStatusColor(verification.status)}`}>
                  {verification.status.replace('_', ' ').toUpperCase()}
                </span>
                <span className={`text-lg font-bold ${getScoreColor(verification.overall_score)}`}>
                  {(verification.overall_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Verification Scores</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Context:</span>
                    <span className={getScoreColor(verification.context_score)}>
                      {(verification.context_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Intent:</span>
                    <span className={getScoreColor(verification.intent_alignment_score)}>
                      {(verification.intent_alignment_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Quality:</span>
                    <span className={getScoreColor(verification.content_quality_score)}>
                      {(verification.content_quality_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Notes</h4>
                <p className="text-sm text-gray-700 line-clamp-3">
                  {verification.verification_notes || 'No notes available'}
                </p>
              </div>
            </div>

            <div className="bg-gray-50 p-3 rounded-md mb-4">
              <p className="text-sm text-gray-700 line-clamp-3">
                {verification.original_content}
              </p>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={() => openViewModal(verification)}
                className="flex-1 bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-4 h-4" />
                <span>View Details</span>
              </button>
              
              {(verification.status === 'pending' || verification.status === 'needs_review') && (
                <button
                  onClick={() => openReviewModal(verification)}
                  className="bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 flex items-center justify-center space-x-1"
                >
                  <Edit className="w-4 h-4" />
                  <span>Review</span>
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {verifications.length === 0 && (
        <div className="text-center py-12">
          <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No verifications found</h3>
          <p className="text-gray-600">
            {filter === 'pending' 
              ? 'No responses are currently pending verification'
              : 'No verifications match your current filter'
            }
          </p>
        </div>
      )}

      <ViewModal
        show={showViewModal}
        onClose={() => setShowViewModal(false)}
        verification={selectedVerification}
      />

      <ReviewModal
        show={showReviewModal}
        onClose={() => setShowReviewModal(false)}
        verification={selectedVerification}
      />
    </div>
  );
};

export default ResponseVerification;