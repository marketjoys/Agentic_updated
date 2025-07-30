import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Code, Mail, Palette, Save, X } from 'lucide-react';
import { toast } from 'react-hot-toast';
import useEscapeKey from '../hooks/useEscapeKey';
import RichTextEditor from './RichTextEditor';

const HTMLTemplateEditor = ({ isOpen, onClose, template, onSave }) => {
  // Add escape key functionality
  useEscapeKey(onClose, isOpen);
  
  const [activeTab, setActiveTab] = useState('edit');
  const [showPreview, setShowPreview] = useState(true);
  const [templateData, setTemplateData] = useState({
    name: '',
    subject: '',
    content: '',
    html_content: '',
    type: 'email',
    is_html_enabled: true,
    style_settings: {
      primaryColor: '#3B82F6',
      backgroundColor: '#FFFFFF',
      textColor: '#1F2937',
      font: 'Arial, sans-serif',
      borderRadius: '8px'
    }
  });

  const [htmlPreview, setHtmlPreview] = useState('');

  useEffect(() => {
    if (template) {
      setTemplateData({
        name: template.name || '',
        subject: template.subject || '',
        content: template.content || '',
        html_content: template.html_content || generateHTMLFromText(template.content || ''),
        type: template.type || 'email',
        is_html_enabled: template.is_html_enabled !== false,
        style_settings: {
          primaryColor: template.style_settings?.primaryColor || '#3B82F6',
          backgroundColor: template.style_settings?.backgroundColor || '#FFFFFF',
          textColor: template.style_settings?.textColor || '#1F2937',
          font: template.style_settings?.font || 'Arial, sans-serif',
          borderRadius: template.style_settings?.borderRadius || '8px'
        }
      });
    } else {
      // Reset for new template
      setTemplateData({
        name: '',
        subject: '',
        content: '',
        html_content: getDefaultHTMLTemplate(),
        type: 'email',
        is_html_enabled: true,
        style_settings: {
          primaryColor: '#3B82F6',
          backgroundColor: '#FFFFFF',
          textColor: '#1F2937',
          font: 'Arial, sans-serif',
          borderRadius: '8px'
        }
      });
    }
  }, [template, isOpen]);

  useEffect(() => {
    if (templateData.is_html_enabled) {
      setHtmlPreview(templateData.html_content);
    }
  }, [templateData.html_content, templateData.is_html_enabled]);

  const getDefaultHTMLTemplate = () => {
    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{subject}}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #1F2937;
            background-color: #f9fafb;
            margin: 0;
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background-color: #3B82F6;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            padding: 30px;
        }
        .footer {
            background-color: #F3F4F6;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6B7280;
        }
        .button {
            display: inline-block;
            background-color: #3B82F6;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        h1, h2, h3 { color: #1F2937; }
        p { margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>Hello {{first_name}}!</h1>
        </div>
        <div class="content">
            <p>Write your email content here...</p>
            <p>You can use personalization like:</p>
            <ul>
                <li>{{first_name}} - First name</li>
                <li>{{last_name}} - Last name</li>
                <li>{{company}} - Company name</li>
                <li>{{job_title}} - Job title</li>
                <li>{{industry}} - Industry</li>
            </ul>
        </div>
        <div class="footer">
            <p>This email was sent to {{email}}</p>
        </div>
    </div>
</body>
</html>`;
  };

  const generateHTMLFromText = (textContent) => {
    if (!textContent) return getDefaultHTMLTemplate();
    
    const paragraphs = textContent.split('\n').filter(p => p.trim());
    const htmlContent = paragraphs.map(p => `            <p>${p}</p>`).join('\n');
    
    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{subject}}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #1F2937;
            background-color: #f9fafb;
            margin: 0;
            padding: 20px;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        h1, h2, h3 { color: #1F2937; }
        p { margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="email-container">
${htmlContent}
    </div>
</body>
</html>`;
  };

  const handleInputChange = (field, value) => {
    setTemplateData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleStyleChange = (field, value) => {
    setTemplateData(prev => ({
      ...prev,
      style_settings: {
        ...prev.style_settings,
        [field]: value
      }
    }));
    
    // Update HTML content with new styles
    updateHTMLWithStyles();
  };

  const updateHTMLWithStyles = () => {
    const { primaryColor, backgroundColor, textColor, font, borderRadius } = templateData.style_settings;
    
    // Update the HTML content with new styles
    let updatedHTML = templateData.html_content;
    
    // Replace style values in the HTML
    updatedHTML = updatedHTML.replace(/color: #[0-9A-Fa-f]{6}/g, `color: ${textColor}`);
    updatedHTML = updatedHTML.replace(/background-color: #[0-9A-Fa-f]{6}/g, `background-color: ${backgroundColor}`);
    updatedHTML = updatedHTML.replace(/font-family: [^;]*/g, `font-family: ${font}`);
    updatedHTML = updatedHTML.replace(/border-radius: [^;]*/g, `border-radius: ${borderRadius}`);
    
    setTemplateData(prev => ({
      ...prev,
      html_content: updatedHTML
    }));
  };

  const convertTextToHTML = () => {
    const htmlContent = generateHTMLFromText(templateData.content);
    setTemplateData(prev => ({
      ...prev,
      html_content: htmlContent,
      is_html_enabled: true
    }));
    toast.success('Text converted to HTML template');
  };

  const handleSave = async () => {
    try {
      if (!templateData.name.trim()) {
        toast.error('Please enter a template name');
        return;
      }
      
      if (!templateData.subject.trim()) {
        toast.error('Please enter a subject line');
        return;
      }

      const saveData = {
        ...templateData,
        content: templateData.content || extractTextFromHTML(templateData.html_content)
      };

      await onSave(saveData);
      toast.success(`Template ${template ? 'updated' : 'created'} successfully`);
      onClose();
    } catch (error) {
      console.error('Error saving template:', error);
      toast.error('Failed to save template');
    }
  };

  const extractTextFromHTML = (html) => {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    return tempDiv.textContent || tempDiv.innerText || '';
  };

  const insertPersonalizationTag = (tag) => {
    const textarea = document.querySelector(`textarea[data-field="html_content"]`);
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = textarea.value;
      const before = text.substring(0, start);
      const after = text.substring(end);
      
      const newText = before + `{{${tag}}}` + after;
      setTemplateData(prev => ({
        ...prev,
        html_content: newText
      }));
      
      // Set cursor position after inserted tag
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + tag.length + 4, start + tag.length + 4);
      }, 0);
    }
  };

  if (!isOpen) return null;

  const personalizationTags = [
    'first_name', 'last_name', 'company', 'job_title', 'industry', 'email'
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-7xl h-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <Mail className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold">
              {template ? 'Edit Template' : 'Create HTML Email Template'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Left Panel - Form */}
          <div className="w-1/2 p-6 border-r overflow-y-auto">
            {/* Basic Information */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Template Name *
                </label>
                <input
                  type="text"
                  value={templateData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter template name..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject Line *
                </label>
                <input
                  type="text"
                  value={templateData.subject}
                  onChange={(e) => handleInputChange('subject', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter subject line..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Template Type
                </label>
                <select
                  value={templateData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="email">Email Campaign</option>
                  <option value="follow-up">Follow-up</option>
                  <option value="auto-response">Auto Response</option>
                </select>
              </div>
            </div>

            {/* HTML Toggle */}
            <div className="flex items-center space-x-3 mb-4">
              <input
                type="checkbox"
                checked={templateData.is_html_enabled}
                onChange={(e) => handleInputChange('is_html_enabled', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label className="text-sm font-medium text-gray-700">
                Enable HTML Editor
              </label>
              {!templateData.is_html_enabled && templateData.content && (
                <button
                  onClick={convertTextToHTML}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Convert to HTML
                </button>
              )}
            </div>

            {/* Content Editor */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  {templateData.is_html_enabled ? 'Template Content' : 'Text Content'}
                </label>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setActiveTab('edit')}
                    className={`px-3 py-1 text-sm rounded ${
                      activeTab === 'edit'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    <Code className="w-4 h-4 inline mr-1" />
                    Edit
                  </button>
                  {templateData.is_html_enabled && (
                    <button
                      onClick={() => setShowPreview(!showPreview)}
                      className="px-3 py-1 text-sm bg-gray-200 text-gray-700 hover:bg-gray-300 rounded"
                    >
                      {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  )}
                </div>
              </div>

              {templateData.is_html_enabled ? (
                <RichTextEditor
                  value={templateData.html_content}
                  onChange={(value) => {
                    handleInputChange('html_content', value);
                    // Auto-convert rich text to HTML
                    updateHTMLWithStyles();
                  }}
                  onKeyDown={(e) => {
                    // Allow typing and prevent modal close on Escape when editing
                    if (e.key === 'Escape') {
                      e.stopPropagation();
                    }
                  }}
                  placeholder="Create your email template here. Use the toolbar above to format your content..."
                  className="border border-gray-300 rounded-lg min-h-[300px]"
                />
              ) : (
                <RichTextEditor
                  value={templateData.content}
                  onChange={(value) => handleInputChange('content', value)}
                  onKeyDown={(e) => {
                    // Allow typing and prevent modal close on Escape when editing
                    if (e.key === 'Escape') {
                      e.stopPropagation();
                    }
                  }}
                  placeholder="Enter your email content here. Use the toolbar above to format your text..."
                  className="border border-gray-300 rounded-lg"
                />
              )}
            </div>

            {/* Personalization Tags */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Personalization Tags
              </label>
              <div className="grid grid-cols-3 gap-2">
                {personalizationTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => insertPersonalizationTag(tag)}
                    className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded border"
                  >
                    {`{{${tag}}}`}
                  </button>
                ))}
              </div>
            </div>

            {/* Style Settings (for HTML templates) */}
            {templateData.is_html_enabled && (
              <div className="mb-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Palette className="w-5 h-5 text-gray-600" />
                  <h3 className="text-lg font-medium text-gray-800">Style Settings</h3>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Primary Color</label>
                    <input
                      type="color"
                      value={templateData.style_settings.primaryColor}
                      onChange={(e) => handleStyleChange('primaryColor', e.target.value)}
                      className="w-full h-10 border border-gray-300 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Background Color</label>
                    <input
                      type="color"
                      value={templateData.style_settings.backgroundColor}
                      onChange={(e) => handleStyleChange('backgroundColor', e.target.value)}
                      className="w-full h-10 border border-gray-300 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Text Color</label>
                    <input
                      type="color"
                      value={templateData.style_settings.textColor}
                      onChange={(e) => handleStyleChange('textColor', e.target.value)}
                      className="w-full h-10 border border-gray-300 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Font Family</label>
                    <select
                      value={templateData.style_settings.font}
                      onChange={(e) => handleStyleChange('font', e.target.value)}
                      className="w-full px-2 py-2 border border-gray-300 rounded text-sm"
                    >
                      <option value="Arial, sans-serif">Arial</option>
                      <option value="Helvetica, sans-serif">Helvetica</option>
                      <option value="Georgia, serif">Georgia</option>
                      <option value="Times New Roman, serif">Times New Roman</option>
                      <option value="Verdana, sans-serif">Verdana</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Preview */}
          <div className="w-1/2 p-6 bg-gray-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">Preview</h3>
              <div className="text-sm text-gray-600">
                {templateData.is_html_enabled ? 'HTML Preview' : 'Text Preview'}
              </div>
            </div>
            
            <div className="bg-white border border-gray-300 rounded-lg h-full overflow-auto">
              {templateData.is_html_enabled && showPreview ? (
                <iframe
                  srcDoc={htmlPreview}
                  className="w-full h-full"
                  title="Email Preview"
                />
              ) : (
                <div className="p-4">
                  <div className="mb-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                    <strong>Subject:</strong> {templateData.subject || 'No subject'}
                  </div>
                  <div className="whitespace-pre-wrap text-sm text-gray-800">
                    {templateData.is_html_enabled 
                      ? extractTextFromHTML(templateData.html_content)
                      : templateData.content || 'No content'
                    }
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t">
          <div className="text-sm text-gray-600">
            {templateData.is_html_enabled ? 
              'HTML template with rich formatting' : 
              'Plain text template'
            }
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>Save Template</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HTMLTemplateEditor;