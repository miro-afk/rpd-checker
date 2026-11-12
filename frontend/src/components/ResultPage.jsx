// ResultPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ResultPage.css';

const ResultPage = () => {
  const { file_id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [isDeleted, setIsDeleted] = useState(false);

  // Функция для удаления файла с сервера
  const deleteFileFromServer = async () => {
    if (isDeleted) return;
    
    setDeleting(true);
    try {
      const response = await fetch(`http://localhost:8000/delete/${file_id}`, {
        method: 'DELETE', 
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        console.log('Файл успешно удален с сервера');
        setIsDeleted(true);
      } else {
        console.warn('Не удалось удалить файл с сервера:', response.status);
      }
    } catch (error) {
      console.error('Ошибка при удалении файла:', error);
    } finally {
      setDeleting(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Запрашиваем данные анализа
        const response = await fetch(`http://localhost:8000/check/${file_id}`);
        
        if (!response.ok) {
          throw new Error('Ошибка при получении данных анализа');
        }
        
        const data = await response.json();

        // Нормализуем данные: преобразуем строки в массивы
        const normalizeField = (field) => {
          if (!field) return [];
          if (Array.isArray(field)) return field;
          if (typeof field === 'string') {
            // Если строка содержит переносы строк, разделяем
            if (field.includes('\n')) {
              return field.split('\n').filter(line => line.trim());
            }
            return [field];
          }
          return [String(field)];
        };
    
    // Применяем нормализацию к каждому полю с контентом
    data.hourtables_content = normalizeField(data.hourtables_content);
    data.headers_content = normalizeField(data.headers_content);
    data.comp_content = normalizeField(data.comp_content);
    data.themes_content = normalizeField(data.themes_content);
    data.literature_content = normalizeField(data.literature_content);
        setReportData(data);
        
        // Запрашиваем PDF файл для превью
        const pdfResponse = await fetch(`http://localhost:8000/pdf/${file_id}`);
        if (pdfResponse.ok) {
          const blob = await pdfResponse.blob();
          const url = URL.createObjectURL(blob);
          setPdfUrl(url);
        } else {
          console.error('Не удалось загрузить PDF');
        }
        
        setLoading(false);
        deleteFileFromServer();
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();

    // Cleanup URL object
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [file_id]);

  const getStatusIcon = (isSuccess) => {
    return isSuccess ? '✅' : '❌';
  };

  const getStatusClass = (isSuccess) => {
    return isSuccess ? 'success' : 'error';
  };

  // Функция для получения динамического заголовка
  const getSectionTitle = (type, isSuccess) => {
    if (isSuccess) {
      // Если проверка пройдена успешно
      switch(type) {
        case 'hourtables':
          return 'Проверка часов в таблицах';
        case 'headers':
          return 'Проверка заголовков';
        case 'comp':
          return 'Проверка компетенций';
        case 'themes':
          return 'Проверка тем';
        case 'literature':
          return 'Проверка литературы';
        default:
          return '';
      }
    } else {
      // Если есть ошибки - показываем проблемные названия
      switch(type) {
        case 'hourtables':
          return 'Несовпадающие часы';
        case 'headers':
          return 'Ненайденные заголовки';
        case 'comp':
          return 'Несовпадающие компетенции';
        case 'themes':
          return 'Ненайденные описания тем';
        case 'literature':
          return 'ошибки в оформлении литературы';
        default:
          return '';
      }
    }
  };

  // Функция для отображения списка ошибок
  const renderErrorList = (errors) => {
    if (!errors || errors.length === 0) return null;
    
    return (
      <div className="error-list">
        {errors.map((error, index) => (
          <div key={index} className="error-item">
            • {error}
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="result-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Загрузка данных анализа...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="result-container">
        <div className="error-container">
          <h2>Ошибка</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} className="back-button">
            Вернуться к загрузке
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="result-container">
      <div className="result-header">
        <div className="header-left">
          <button onClick={() => navigate('/')} className="back-button">
            ← Загрузить новый файл
          </button>
        </div>
        <div className="header-center">
          <h1 className="app-title">Анализатор РПД</h1>
        </div>
        <div className="header-right"></div>
      </div>
      
      <div className="result-content">
        {/* Левая колонка - превью PDF */}
        <div className="pdf-preview">
          <h2>Превью документа</h2>
          {pdfUrl ? (
            <iframe
              src={pdfUrl}
              title="PDF Preview"
              className="pdf-iframe"
              frameBorder="0"
            >
              Ваш браузер не поддерживает просмотр PDF
            </iframe>
          ) : (
            <div className="no-pdf">
              <p>Не удалось загрузить превью PDF</p>
            </div>
          )}
        </div>

        {/* Правая колонка - отчет об анализе */}
        <div className="analysis-report">
          <h2>Отчет об анализе</h2>
          
          <div className="report-sections">
            {/* Секция проверки часов */}
            <div className="report-section">
              <div className="section-header">
                <span className={`status-icon ${getStatusClass(reportData.result_hourtables)}`}>
                  {getStatusIcon(reportData.result_hourtables)}
                </span>
                <h3>{getSectionTitle('hourtables', reportData.result_hourtables)}</h3>
              </div>
              {!reportData.result_hourtables && reportData.hourtables_content && (
                <div className="section-content error-content">
                  {renderErrorList(reportData.hourtables_content)}
                </div>
              )}
              {reportData.result_hourtables && (
                <div className="section-content success-content">
                  <p>✓ Часы в документе совпадают</p>
                </div>
              )}
            </div>

            {/* Секция заголовков */}
            <div className="report-section">
              <div className="section-header">
                <span className={`status-icon ${getStatusClass(reportData.result_headers)}`}>
                  {getStatusIcon(reportData.result_headers)}
                </span>
                <h3>{getSectionTitle('headers', reportData.result_headers)}</h3>
              </div>
              {!reportData.result_headers && reportData.headers_content && (
                <div className="section-content error-content">
                  {renderErrorList(reportData.headers_content)}
                </div>
              )}
              {reportData.result_headers && (
                <div className="section-content success-content">
                  <p>✓ Все заголовки в документе корректны</p>
                </div>
              )}
            </div>

            {/* Проверка компетенций */}
            <div className="report-section">
              <div className="section-header">
                <span className={`status-icon ${getStatusClass(reportData.result_comp)}`}>
                  {getStatusIcon(reportData.result_comp)}
                </span>
                <h3>{getSectionTitle('comp', reportData.result_comp)}</h3>
              </div>
              {!reportData.result_comp && reportData.comp_content && (
                <div className="section-content error-content">
                  {renderErrorList(reportData.comp_content)}
                </div>
              )}
              {reportData.result_comp && (
                <div className="section-content success-content">
                  <p>✓ Проверка компетенций пройдена успешно</p>
                </div>
              )}
            </div>

            {/* Секция проверки тем */}
            <div className="report-section">
              <div className="section-header">
                <span className={`status-icon ${getStatusClass(reportData.result_themes)}`}>
                  {getStatusIcon(reportData.result_themes)}
                </span>
                <h3>{getSectionTitle('themes', reportData.result_themes)}</h3>
              </div>
              {!reportData.result_themes && reportData.themes_content && (
                <div className="section-content error-content">
                  {renderErrorList(reportData.themes_content)}
                </div>
              )}
              {reportData.result_themes && (
                <div className="section-content success-content">
                  <p>✓ Все темы в документе корректны</p>
                </div>
              )}
            </div>

            {/* Секция проверки литературы */}
            <div className="report-section">
              <div className="section-header">
                <span className={`status-icon ${getStatusClass(reportData.result_literature)}`}>
                  {getStatusIcon(reportData.result_literature)}
                </span>
                <h3>{getSectionTitle('literature', reportData.result_literature)}</h3>
              </div>
              {!reportData.result_literature && reportData.literature_content && (
                <div className="section-content error-content">
                  {renderErrorList(reportData.literature_content)}
                </div>
              )}
              {reportData.result_literature && (
                <div className="section-content success-content">
                  <p>✓ Оформление литературы корректно</p>
                </div>
              )}
            </div>
          </div>

          {/* Общий итог*/}
          <div className="summary">
            <h3>Общий итог проверки</h3>
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-label">Часы:</span>
                <span className={`stat-value ${getStatusClass(reportData.result_hourtables)}`}>
                  {reportData.result_hourtables ? 'Пройдено' : 'Ошибка'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Заголовки:</span>
                <span className={`stat-value ${getStatusClass(reportData.result_headers)}`}>
                  {reportData.result_headers ? 'Пройдено' : 'Ошибка'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Компетенции:</span>
                <span className={`stat-value ${getStatusClass(reportData.result_comp)}`}>
                  {reportData.result_comp ? 'Пройдено' : 'Ошибка'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Темы:</span>
                <span className={`stat-value ${getStatusClass(reportData.result_themes)}`}>
                  {reportData.result_themes ? 'Пройдено' : 'Ошибка'}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Литература:</span>
                <span className={`stat-value ${getStatusClass(reportData.result_literature)}`}>
                  {reportData.result_literature ? 'Пройдено' : 'Ошибка'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultPage;