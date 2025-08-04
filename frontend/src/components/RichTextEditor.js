import React, { useEffect, useRef, forwardRef, useState } from 'react';
import { Bold, Italic, Underline, List, Link, Type, AlignLeft, AlignCenter, AlignRight, Code } from 'lucide-react';

const RichTextEditor = forwardRef(({ value, onChange, placeholder, onKeyDown, className, ...props }, ref) => {
  const textareaRef = useRef(null);
  const [isHtmlMode, setIsHtmlMode] = useState(false);

  // Handle key events (like Escape)
  useEffect(() => {
    if (textareaRef.current && onKeyDown) {
      const handleKeyDown = (event) => {
        onKeyDown(event);
      };
      textareaRef.current.addEventListener('keydown', handleKeyDown);
      
      return () => {
        if (textareaRef.current) {
          textareaRef.current.removeEventListener('keydown', handleKeyDown);
        }
      };
    }
  }, [onKeyDown]);

  // Forward ref to textarea
  useEffect(() => {
    if (ref) {
      if (typeof ref === 'function') {
        ref(textareaRef.current);
      } else {
        ref.current = textareaRef.current;
      }
    }
  }, [ref]);

  const insertText = (before, after = '') => {
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    const newText = textarea.value.substring(0, start) + before + selectedText + after + textarea.value.substring(end);
    
    onChange(newText);
    
    // Set cursor position
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length);
    }, 0);
  };

  const formatButtons = [
    { icon: Bold, action: () => insertText('<strong>', '</strong>'), title: 'Bold' },
    { icon: Italic, action: () => insertText('<em>', '</em>'), title: 'Italic' },
    { icon: Underline, action: () => insertText('<u>', '</u>'), title: 'Underline' },
    { icon: Type, action: () => insertText('<h2>', '</h2>'), title: 'Heading' },
    { icon: List, action: () => insertText('<ul><li>', '</li></ul>'), title: 'List' },
    { icon: Link, action: () => insertText('<a href="https://example.com">', '</a>'), title: 'Link' },
    { icon: AlignCenter, action: () => insertText('<div style="text-align: center;">', '</div>'), title: 'Center' },
    { icon: Code, action: () => setIsHtmlMode(!isHtmlMode), title: 'HTML Mode' },
  ];

  return (
    <div className={className}>
      {/* Toolbar */}
      <div className="border border-gray-300 rounded-t-lg bg-gray-50 px-3 py-2 flex flex-wrap gap-1">
        {formatButtons.map((button, index) => (
          <button
            key={index}
            type="button"
            onClick={button.action}
            title={button.title}
            className={`p-2 rounded hover:bg-gray-200 ${isHtmlMode && button.icon === Code ? 'bg-blue-100' : ''}`}
          >
            <button.icon className="w-4 h-4" />
          </button>
        ))}
      </div>

      {/* Editor */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || 'Enter your email content here...'}
          className={`w-full border-x border-b border-gray-300 rounded-b-lg p-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none ${isHtmlMode ? 'font-mono text-sm' : ''}`}
          style={{
            height: '300px',
            fontFamily: isHtmlMode ? 'monospace' : 'inherit'
          }}
          {...props}
        />
        
        {isHtmlMode && (
          <div className="absolute top-2 right-2 bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
            HTML Mode
          </div>
        )}
      </div>

      {/* Helper text */}
      <div className="text-sm text-gray-600 mt-2">
        Use the toolbar buttons to add formatting, or switch to HTML mode for advanced editing.
      </div>
    </div>
  );
});

RichTextEditor.displayName = 'RichTextEditor';

export default RichTextEditor;