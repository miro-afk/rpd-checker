// FileUploader.jsx
import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './FileUploader.css';

const FileUploader = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const navigate = useNavigate();

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const validateFile = (file) => {
    if (file.type !== 'application/pdf') {
      setMessage({ text: 'Пожалуйста, загрузите файл в формате PDF', type: 'error' });
      return false;
    }
    if (file.size > 10 * 1024 * 1024) {
      setMessage({ text: 'Файл слишком большой. Максимальный размер: 10MB', type: 'error' });
      return false;
    }
    return true;
  };

  const handleFile = (file) => {
    if (validateFile(file)) {
      setFile(file);
      setMessage({ text: `Выбран файл: ${file.name}`, type: 'success' });
    } else {
      setFile(null);
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFile(droppedFile);
    }
  }, []);

  const handleChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ text: 'Пожалуйста, выберите файл', type: 'error' });
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        if (data.result === 'success' && data.file_id) {
          // Переходим на страницу результатов с file_id
          navigate(`/result/${data.file_id}`);
        } else {
          console.log(data.result,data.file_id)
          throw new Error('Неверный ответ от сервера');
        }
      } else {
        throw new Error('Ошибка при загрузке');
      }
    } catch (error) {
      setMessage({ text: 'Ошибка при загрузке файла на сервер', type: 'error' });
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
    <header className="app-header">
        <div className="app-header-content">
          <h1 className="app-title">Анализатор РПД</h1>
          <p className="app-subtitle">Анализ рабочих программ дисциплин на соответствие шаблону</p>
        </div>
      </header>
    <div className="upload-container">
      
      <div className="upload-card">
        <h2>Загрузка PDF файла</h2>
        
        <div
          className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="drop-zone-content">
            <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="drop-text">
              {dragActive ? 'Отпустите файл для загрузки' : 'Перетащите PDF файл сюда'}
            </p>
            <p className="drop-subtext">или</p>
            <label htmlFor="file-input" className="file-input-label">
              Выберите файл на компьютере
            </label>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={handleChange}
              disabled={uploading}
              className="file-input"
            />
            <p className="file-info">Поддерживаются только PDF файлы (макс. 10MB)</p>
          </div>
        </div>

        {file && (
          <div className="file-info-section">
            <div className="file-details">
              <svg className="file-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
                />
              </svg>
              <div>
                <p className="file-name">{file.name}</p>
                <p className="file-size">
                  Размер: {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button 
              onClick={handleUpload} 
              disabled={uploading}
              className="upload-button"
            >
              {uploading ? 'Загрузка...' : 'Начать проверку'}
            </button>
          </div>
        )}

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
      </div>
    </div>
    </>
  );
};

export default FileUploader;