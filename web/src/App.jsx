import React, { useState, useEffect, useCallback, useRef } from 'react';
import EmbeddedPDFViewer from './components/EmbeddedPDFViewer';
import './App.css';

const App = () => {
  // State management
  const [currentTheme, setCurrentTheme] = useState('light');
  const [pdfData, setPdfData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState({
    zoom: 100,
    rotation: 0,
    viewMode: 'fit-width',
    annotationsEnabled: true,
    darkMode: false
  });
  const [error, setError] = useState(null);
  
  // Refs
  const pdfViewerRef = useRef(null);
  const bridgeRef = useRef(null);

  // Global React App interface için
  useEffect(() => {
    window.ReactApp = {
      onBridgeReady: handleBridgeReady,
      onPdfDataChanged: handlePdfDataChanged,
      onThemeChanged: handleThemeChanged,
      onSettingsChanged: handleSettingsChanged,
      // PDF viewer methods
      getCurrentPage: () => pdfViewerRef.current?.getCurrentPage(),
      getTotalPages: () => pdfViewerRef.current?.getTotalPages(),
      zoomIn: () => pdfViewerRef.current?.zoomIn(),
      zoomOut: () => pdfViewerRef.current?.zoomOut(),
      resetZoom: () => pdfViewerRef.current?.resetZoom(),
      rotatePage: () => pdfViewerRef.current?.rotatePage(),
    };

    return () => {
      window.ReactApp = null;
    };
  }, []);

  // Bridge hazır olduğunda
  const handleBridgeReady = useCallback((bridge) => {
    console.log('Bridge ready in React App');
    bridgeRef.current = bridge;
    setError(null);
  }, []);

  // PDF data değiştiğinde
  const handlePdfDataChanged = useCallback((data) => {
    console.log('PDF data changed:', data);
    setIsLoading(true);
    setPdfData(data);
    setError(null);
    
    // Viewer'a PDF'i yükle
    if (pdfViewerRef.current && data.filePath) {
      pdfViewerRef.current.loadPDF(data.filePath)
        .then(() => {
          setIsLoading(false);
        })
        .catch((err) => {
          setError(`PDF yükleme hatası: ${err.message}`);
          setIsLoading(false);
        });
    }
  }, []);

  // Tema değiştiğinde
  const handleThemeChanged = useCallback((theme) => {
    console.log('Theme changed to:', theme);
    setCurrentTheme(theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, []);

  // Ayarlar değiştiğinde
  const handleSettingsChanged = useCallback((newSettings) => {
    console.log('Settings changed:', newSettings);
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  // Tool action handler
  const handleToolAction = useCallback(async (toolId, data) => {
    if (!window.pypdfTools.bridge) {
      console.error('Bridge not available for tool action');
      return;
    }

    try {
      const result = await window.pypdfTools.sendToolAction(toolId, {
        ...data,
        currentPage: pdfViewerRef.current?.getCurrentPage(),
        totalPages: pdfViewerRef.current?.getTotalPages(),
        zoom: settings.zoom,
        rotation: settings.rotation
      });
      
      const response = JSON.parse(result);
      if (response.success) {
        console.log(`Tool ${toolId} executed successfully:`, response.result);
        
        // Sonucu UI'da işle
        if (response.result) {
          if (response.result.zoom !== undefined) {
            setSettings(prev => ({ ...prev, zoom: response.result.zoom }));
            pdfViewerRef.current?.setZoom(response.result.zoom);
          }
          if (response.result.rotation !== undefined) {
            setSettings(prev => ({ ...prev, rotation: response.result.rotation }));
            pdfViewerRef.current?.setRotation(response.result.rotation);
          }
        }
      } else {
        setError(`Tool error: ${response.error}`);
      }
    } catch (err) {
      setError(`Tool action failed: ${err.message}`);
      console.error('Tool action error:', err);
    }
  }, [settings]);

  // Sayfa değişikliği handler
  const handlePageChange = useCallback((pageNumber) => {
    console.log('Page changed to:', pageNumber);
    
    // Python'a bildir
    if (window.pypdfTools.notifyPageChange) {
      window.pypdfTools.notifyPageChange(pageNumber);
    }
  }, []);

  // Annotation ekleme handler
  const handleAnnotationAdd = useCallback((annotation) => {
    console.log('Annotation added:', annotation);
    
    // Python'a bildir
    if (window.pypdfTools.notifyAnnotationAdd) {
      window.pypdfTools.notifyAnnotationAdd(annotation);
    }
  }, []);

  // Loading state
  if (isLoading && !pdfData) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>PDF yükleniyor...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="app-error">
        <div className="error-icon">⚠️</div>
        <h3>Hata Oluştu</h3>
        <p>{error}</p>
        <button 
          onClick={() => setError(null)}
          className="error-dismiss"
        >
          Kapat
        </button>
      </div>
    );
  }

  return (
    <div className={`app app-theme-${currentTheme}`}>
      {/* Header Toolbar */}
      <header className="app-header">
        <div className="app-header-left">
          <h1 className="app-title">
            {pdfData?.fileName || 'PyPDF-Tools'}
          </h1>
          {pdfData && (
            <div className="pdf-info">
              <span className="page-info">
                Sayfa {pdfViewerRef.current?.getCurrentPage() || 1} / {pdfData.totalPages || '?'}
              </span>
              <span className="file-size">
                {formatFileSize(pdfData.fileSize)}
              </span>
            </div>
          )}
        </div>
        
        <div className="app-header-right">
          {/* Quick action buttons */}
          <div className="quick-actions">
            <button
              onClick={() => handleToolAction('zoom-out')}
              className="tool-button"
              title="Uzaklaştır"
              disabled={!pdfData}
            >
              🔍-
            </button>
            <span className="zoom-level">{settings.zoom}%</span>
            <button
              onClick={() => handleToolAction('zoom-in')}
              className="tool-button"
              title="Yakınlaştır"
              disabled={!pdfData}
            >
              🔍+
            </button>
            <button
              onClick={() => handleToolAction('rotate')}
              className="tool-button"
              title="Döndür"
              disabled={!pdfData}
            >
              ↻
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {pdfData ? (
          <EmbeddedPDFViewer
            ref={pdfViewerRef}
            pdfData={pdfData}
            theme={currentTheme}
            settings={settings}
            onToolAction={handleToolAction}
            onPageChange={handlePageChange}
            onAnnotationAdd={handleAnnotationAdd}
            isLoading={isLoading}
          />
        ) : (
          <div className="app-welcome">
            <div className="welcome-content">
              <div className="welcome-icon">📄</div>
              <h2>PDF Yükleyin</h2>
              <p>Bir PDF dosyası açmak için PyQt menüsünden "Dosya → Aç" seçin</p>
              <div className="welcome-features">
                <div className="feature">
                  <span className="feature-icon">🔍</span>
                  <span>Görüntüleme ve Yakınlaştırma</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">✏️</span>
                  <span>Annotation ve Not Ekleme</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">⚡</span>
                  <span>Hızlı PDF İşlemleri</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer Status */}
      <footer className="app-footer">
        <div className="status-info">
          {bridgeRef.current ? (
            <span className="status-connected">🟢 Bağlı</span>
          ) : (
            <span className="status-disconnected">🔴 Bağlantı Yok</span>
          )}
          <span className="theme-info">Tema: {currentTheme}</span>
        </div>
        
        {pdfData && (
          <div className="pdf-metadata">
            <span>Son Değişiklik: {new Date(pdfData.lastModified * 1000).toLocaleDateString('tr-TR')}</span>
          </div>
        )}
      </footer>
    </div>
  );
};

// Utility functions
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export default App;
