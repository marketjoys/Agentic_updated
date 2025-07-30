import React, { useEffect, useRef, forwardRef } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

const RichTextEditor = forwardRef(({ value, onChange, placeholder, onKeyDown, className, ...props }, ref) => {
  const quillRef = useRef(null);

  // Custom toolbar configuration
  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'align': [] }],
      ['link', 'image'],
      ['blockquote', 'code-block'],
      ['clean']
    ],
  };

  const formats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'color', 'background', 'list', 'bullet', 'indent',
    'align', 'link', 'image', 'blockquote', 'code-block'
  ];

  // Handle key events (like Escape)
  useEffect(() => {
    if (quillRef.current && onKeyDown) {
      const editor = quillRef.current.getEditor();
      const handleKeyDown = (event) => {
        onKeyDown(event);
      };
      editor.root.addEventListener('keydown', handleKeyDown);
      
      return () => {
        if (editor && editor.root) {
          editor.root.removeEventListener('keydown', handleKeyDown);
        }
      };
    }
  }, [onKeyDown]);

  return (
    <div className={className}>
      <ReactQuill
        ref={(el) => {
          quillRef.current = el;
          if (ref) {
            if (typeof ref === 'function') {
              ref(el);
            } else {
              ref.current = el;
            }
          }
        }}
        theme="snow"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        modules={modules}
        formats={formats}
        style={{
          height: '300px',
          marginBottom: '50px' // Space for toolbar
        }}
        {...props}
      />
    </div>
  );
});

RichTextEditor.displayName = 'RichTextEditor';

export default RichTextEditor;