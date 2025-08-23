import React, { useState, useRef, useCallback, useEffect, forwardRef, useImperativeHandle } from 'react';
import {
  ChevronLeft, ChevronRight, ZoomIn, ZoomOut, RotateCw, Search,
  Edit3, Type, Highlighter, MessageSquare, Square, ArrowRight, Trash2,
  Split, Merge, Copy, Scissors, Plus, Minus, Download, Upload,
  Eye, EyeOff, Lock, Unlock, Award, ScanText, Brain, BarChart3,
  Layers, Grid3X3, Bookmark, Share2, Settings, RefreshCw,
  FileText, Save, Printer, Mail, Cloud, Users, Target, Wand2
} from 'lucide-react';

// PyPDF-Tools'a entegre PDF Viewer Component
const EmbeddedPDFViewer = forwardRef(({
  pdfData,
  onToolAction,
  onPageChange,
  onAnnotationAdd,
  theme = 'light',
  settings = {},
  isLoading = false,
  className = ''
}, ref) => {
  // Core States
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(pdfData?.totalPages || 0);
  const [zoom, setZoom] = useState(settings.zoom || 100);
  const [rotation, setRotation] = useState(settings.rotation || 0);
  const [viewMode, setViewMode] = useState(settings.viewMode || 'single');

  // Tool States
  const [activeTool, setActiveTool] = useState(null);
  const [annotations, setAnnotations] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedText, setSelectedText] = useState('');
  const [bookmarks, setBookmarks] = useState([]);

  // UI States
  const [showThumbnails, setShowThumbnails] = useState(true);
  const [sidebarTab, setSidebarTab] = useState('thumbnails');
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false);
  const [toolbarExpanded, setToolbarExpanded] = useState(false);

  // AI States
  const [aiMode, setAiMode] = useState(false);
  const [aiSummary, setAiSummary] = useState('');
  const [aiQuestions, setAiQuestions] = useState([]);

  // Drawing States
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingPath, setDrawingPath] = useState([]);
  const [currentColor, setCurrentColor] = useState('#ffff00');

  // Refs
  const canvasRef = useRef(null);
  const viewerRef = useRef(null);

  // Imperative handle for parent component
  useImperativeHandle(ref, () => ({
    getCurrentPage: () => currentPage,
    getTotalPages: () => totalPages,
    getZoom: () => zoom,
    getRotation: () => rotation,
    setZoom: (newZoom) => setZoom(Math.max(25, Math.min(500, newZoom))),
    setRotation: (newRotation) => setRotation(newRotation % 360),
    zoomIn: handleZoomIn,
    zoomOut: handleZoomOut,
    resetZoom: () => setZoom(100),
    rotatePage: () => setRotation(prev => (prev + 90) % 360),
    goToPage: (page) => goToPage(page),
    loadPDF: async (filePath) => {
      // Mock PDF loading - gerçek implementasyon PDF.js kullanmalı
      console.log('Loading PDF:', filePath);
      return Promise.resolve();
    }
  }));

  // Effect: Update from settings prop
  useEffect(() => {
    if (settings.zoom !== undefined) setZoom(settings.zoom);
    if (settings.rotation !== undefined) setRotation(settings.rotation);
    if (settings.viewMode !== undefined) setViewMode(settings.viewMode);
  }, [settings]);

  // Effect: Update total pages from pdfData
  useEffect(() => {
    if (pdfData?.totalPages) {
      setTotalPages(pdfData.totalPages);
    }
  }, [pdfData]);

  // Effect: Notify parent of page changes
  useEffect(() => {
    if (onPageChange) {
      onPageChange(currentPage);
    }
  }, [currentPage, onPageChange]);

  // Theme configuration
  const getThemeClasses = () => {
    const themes = {
      light: {
        bg: 'bg-white',
        sidebar: 'bg-gray-50',
        toolbar: 'bg-white border-gray-200',
        text: 'text-gray-900',
        border: 'border-gray-200',
        button: 'bg-white hover:bg-gray-50 border-gray-200',
        accent: 'bg-blue-500 text-white hover:bg-blue-600'
      },
      dark: {
        bg: 'bg-gray-900',
        sidebar: 'bg-gray-800',
        toolbar: 'bg-gray-800 border-gray-700',
        text: 'text-white',
        border: 'border-purple-600',
        button: 'bg-purple-700 hover:bg-purple-600 border-purple-600',
        accent: 'bg-cyan-500 text-white hover:bg-cyan-600'
      },
      midnight: {
        bg: 'bg-slate-900',
        sidebar: 'bg-slate-800',
        toolbar: 'bg-slate-800 border-slate-700',
        text: 'text-white',
        border: 'border-slate-700',
        button: 'bg-slate-700 hover:bg-slate-600 border-slate-600',
        accent: 'bg-blue-400 text-white hover:bg-blue-500'
      }
    };
    return themes[theme] || themes.light;
  };

  const themeClasses = getThemeClasses();

  // Tool categories configuration
  const toolCategories = [
    {
      id: 'view',
      title: 'Görünüm',
      icon: Eye,
      tools: [
        { id: 'zoom-in', icon: ZoomIn, tooltip: 'Yakınlaştır' },
        { id: 'zoom-out', icon: ZoomOut, tooltip: 'Uzaklaştır' },
        { id: 'rotate', icon: RotateCw, tooltip: 'Döndür' },
        { id: 'fit-width', icon: ArrowRight, tooltip: 'Genişliğe Sığdır' },
        { id: 'fit-page', icon: Square, tooltip: 'Sayfaya Sığdır' }
      ]
    },
    {
      id: 'annotate',
      title: 'Açıklama',
      icon: Edit3,
      tools: [
        { id: 'highlight', icon: Highlighter, tooltip: 'Vurgu', color: '#ffff00' },
        { id: 'text-note', icon: Type, tooltip: 'Metin Notu' },
        { id: 'sticky-note', icon: MessageSquare, tooltip: 'Yapışkan Not' },
        { id: 'draw', icon: Edit3, tooltip: 'Çizim' },
        { id: 'shape', icon: Square, tooltip: 'Şekil' },
        { id: 'arrow', icon: ArrowRight, tooltip: 'Ok' }
      ]
    },
    {
      id: 'edit',
      title: 'Düzenle',
      icon: Scissors,
      tools: [
        { id: 'split', icon: Split, tooltip: 'Böl' },
        { id: 'merge', icon: Merge, tooltip: 'Birleştir' },
        { id: 'add-page', icon: Plus, tooltip: 'Sayfa Ekle' },
        { id: 'delete-page', icon: Minus, tooltip: 'Sayfa Sil' },
        { id: 'copy-page', icon: Copy, tooltip: 'Sayfa Kopyala' }
      ]
    },
    {
      id: 'security',
      title: 'Güvenlik',
      icon: Lock,
      tools: [
        { id: 'encrypt', icon: Lock, tooltip: 'Şifrele' },
        { id: 'decrypt', icon: Unlock, tooltip: 'Şifre Kaldır' },
        { id: 'sign', icon: Award, tooltip: 'Dijital İmza' },
        { id: 'redact', icon: EyeOff, tooltip: 'Redaksiyon' }
      ]
    },
    {
      id: 'ai',
      title: 'AI Araçları',
      icon: Brain,
      tools: [
        { id: 'summarize', icon: BarChart3, tooltip: 'Özetleme' },
        { id: 'extract', icon: ScanText, tooltip: 'Metin Çıkarma' },
        { id: 'translate', icon: RefreshCw, tooltip: 'Çeviri' },
        { id: 'analyze', icon: Target, tooltip: 'Analiz' }
      ]
    }
  ];

  // Tool action handler
  const handleToolAction = useCallback((toolId, data = {}) => {
    if (onToolAction) {
      onToolAction(toolId, {
        ...data,
        currentPage,
        totalPages,
        selectedText,
        annotations,
        zoom,
        rotation
      });
    }
    setActiveTool(toolId);
  }, [onToolAction, currentPage, totalPages, selectedText, annotations, zoom, rotation]);

  // Annotation functions
  const addAnnotation = useCallback((type, position, content = '') => {
    const annotation = {
      id: Date.now(),
      type,
      page: currentPage,
      position,
      content,
      color: currentColor,
      timestamp: new Date().toISOString()
    };
    setAnnotations(prev => [...prev, annotation]);
    
    if (onAnnotationAdd) {
      onAnnotationAdd(annotation);
    }
  }, [currentPage, currentColor, onAnnotationAdd]);

  // Navigation functions
  const goToPage = (page) => {
    const newPage = Math.max(1, Math.min(totalPages, page));
    setCurrentPage(newPage);
  };

  // Zoom functions
  const handleZoomIn = () => setZoom(prev => Math.min(500, prev + 25));
  const handleZoomOut = () => setZoom(prev => Math.max(25, prev - 25));

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (!pdfData) return;

      switch(e.key) {
        case 'ArrowLeft':
          e.ctrlKey ? setCurrentPage(1) : goToPage(currentPage - 1);
          break;
        case 'ArrowRight':
          e.ctrlKey ? setCurrentPage(totalPages) : goToPage(currentPage + 1);
          break;
        case '+':
          if (e.ctrlKey) { e.preventDefault(); handleZoomIn(); }
          break;
        case '-':
          if (e.ctrlKey) { e.preventDefault(); handleZoomOut(); }
          break;
        case '0':
          if (e.ctrlKey) { e.preventDefault(); setZoom(100); }
          break;
        case 'f':
          if (e.ctrlKey) { e.preventDefault(); document.getElementById('search-input')?.focus(); }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentPage, totalPages, pdfData]);

  // Loading state
  if (isLoading) {
    return (
      <div className={`${className} ${themeClasses.bg} ${themeClasses.text} h-full flex items-center justify-center`}>
        <div className="text-center p-8">
          <div className="loading-spinner mx-auto mb-4"></div>
          <h3 className="text-lg font-medium mb-2">PDF Yükleniyor...</h3>
          <p className="text-sm opacity-70">Lütfen bekleyin</p>
        </div>
      </div>
    );
  }

  // No PDF state
  if (!pdfData) {
    return (
      <div className={`${className} ${themeClasses.bg} ${themeClasses.text} h-full flex items-center justify-center`}>
        <div className="text-center p-8">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium mb-2">PDF Yükleyin</h3>
          <p className="text-sm opacity-70">PDF dosyanızı ana uygulamadan yükleyin</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className} ${themeClasses.bg} ${themeClasses.text} flex h-full embedded-pdf-viewer`}>
      {/* Sol Sidebar */}
      <div className={`w-64 ${themeClasses.sidebar} ${themeClasses.border} border-r flex flex-col`}>
        {/* Sidebar Tabs */}
        <div className={`flex ${themeClasses.toolbar} border-b ${themeClasses.border}`}>
          {[
            { id: 'thumbnails', icon: Grid3X3, label: 'Sayfalar' },
            { id: 'bookmarks', icon: Bookmark, label: 'Yer İşaretleri' },
            { id: 'annotations', icon: MessageSquare, label: 'Notlar' },
            { id: 'search', icon: Search, label: 'Arama' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setSidebarTab(tab.id)}
              className={`flex-1 p-2 text-xs transition-colors ${
                sidebarTab === tab.id
                  ? themeClasses.accent
                  : `${themeClasses.button} hover:bg-opacity-80`
              }`}
              title={tab.label}
            >
              <tab.icon className="w-4 h-4 mx-auto" />
            </button>
          ))}
        </div>

        {/* Sidebar Content */}
        <div className="flex-1 overflow-y-auto p-2">
          {sidebarTab === 'thumbnails' && (
            <div className="space-y-2">
              <div className="text-sm font-medium mb-2">Sayfa Küçük Resimleri</div>
              {Array.from({ length: totalPages }, (_, i) => (
                <div
                  key={i + 1}
                  onClick={() => setCurrentPage(i + 1)}
                  className={`relative p-2 border rounded cursor-pointer transition-all ${
                    currentPage === i + 1
                      ? `${themeClasses.accent} border-blue-500`
                      : `${themeClasses.button} ${themeClasses.border}`
                  }`}
                >
                  <div className="aspect-[3/4] bg-gray-200 rounded mb-1 flex items-center justify-center text-xs">
                    {i + 1}
                  </div>
                  <div className="text-xs text-center">Sayfa {i + 1}</div>
                </div>
              ))}
            </div>
          )}

          {sidebarTab === 'bookmarks' && (
            <div className="space-y-2">
              <div className="text-sm font-medium mb-2">Yer İşaretleri</div>
              {bookmarks.length === 0 ? (
                <div className="text-xs opacity-70 text-center py-4">
                  Henüz yer işareti eklenmedi
                </div>
              ) : (
                bookmarks.map(bookmark => (
                  <div
                    key={bookmark.id}
                    onClick={() => setCurrentPage(bookmark.page)}
                    className={`p-2 rounded cursor-pointer ${themeClasses.button}`}
                  >
                    <div className="text-sm font-medium">{bookmark.title}</div>
                    <div className="text-xs opacity-70">Sayfa {bookmark.page}</div>
                  </div>
                ))
              )}
            </div>
          )}

          {sidebarTab === 'annotations' && (
            <div className="space-y-2">
              <div className="text-sm font-medium mb-2">Açıklamalar</div>
              {annotations.map(annotation => (
                <div
                  key={annotation.id}
                  className={`p-2 border-l-4 ${themeClasses.button} cursor-pointer`}
                  style={{ borderLeftColor: annotation.color }}
                  onClick={() => setCurrentPage(annotation.page)}
                >
                  <div className="text-sm font-medium capitalize">{annotation.type}</div>
                  <div className="text-xs opacity-70">Sayfa {annotation.page}</div>
                  {annotation.content && (
                    <div className="text-xs mt-1">{annotation.content.slice(0, 50)}...</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {sidebarTab === 'search' && (
            <div className="space-y-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 w-4 h-4 opacity-50" />
                <input
                  id="search-input"
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="PDF'de ara..."
                  className={`w-full pl-8 pr-3 py-2 text-sm border rounded ${themeClasses.button} ${themeClasses.border} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                />
              </div>
              {searchResults.map((result, index) => (
                <div
                  key={index}
                  onClick={() => setCurrentPage(result.page)}
                  className={`p-2 cursor-pointer rounded ${themeClasses.button}`}
                >
                  <div className="text-sm font-medium">Sayfa {result.page}</div>
                  <div className="text-xs opacity-70">{result.context}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Ana İçerik */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className={`${themeClasses.toolbar} border-b ${themeClasses.border} p-2`}>
          <div className="flex items-center justify-between">
            {/* Sol Toolbar */}
            <div className="flex items-center space-x-1">
              {/* Sayfa Navigasyon */}
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage <= 1}
                  className={`p-1.5 rounded ${themeClasses.button} disabled:opacity-50 transition-colors`}
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <div className="flex items-center space-x-1 text-sm">
                  <input
                    type="number"
                    value={currentPage}
                    onChange={(e) => goToPage(parseInt(e.target.value) || 1)}
                    className={`w-12 px-1 py-1 text-center text-xs border rounded ${themeClasses.button} ${themeClasses.border} focus:outline-none focus:ring-1 focus:ring-blue-500`}
                    min="1"
                    max={totalPages}
                  />
                  <span className="text-xs">/ {totalPages}</span>
                </div>
                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage >= totalPages}
                  className={`p-1.5 rounded ${themeClasses.button} disabled:opacity-50 transition-colors`}
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              {/* Zoom Kontrolleri */}
              <div className="flex items-center space-x-1 ml-4">
                <button
                  onClick={handleZoomOut}
                  className={`p-1.5 rounded ${themeClasses.button} transition-colors`}
                  title="Uzaklaştır"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <div className={`px-2 py-1 text-xs ${themeClasses.button} rounded min-w-[50px] text-center`}>
                  {zoom}%
                </div>
                <button
                  onClick={handleZoomIn}
                  className={`p-1.5 rounded ${themeClasses.button} transition-colors`}
                  title="Yakınlaştır"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Sağ Toolbar - Araçlar */}
            <div className="flex items-center space-x-1">
              {toolCategories.map(category => (
                <div key={category.id} className="relative">
                  <button
                    onClick={() => setToolbarExpanded(toolbarExpanded === category.id ? null : category.id)}
                    className={`p-1.5 rounded transition-colors ${
                      toolbarExpanded === category.id ? themeClasses.accent : themeClasses.button
                    }`}
                    title={category.title}
                  >
                    <category.icon className="w-4 h-4" />
                  </button>
                  {toolbarExpanded === category.id && (
                    <div className={`absolute top-full right-0 mt-1 ${themeClasses.sidebar} ${themeClasses.border} border rounded-lg shadow-lg p-2 z-10`}>
                      <div className="grid grid-cols-3 gap-1">
                        {category.tools.map(tool => (
                          <button
                            key={tool.id}
                            onClick={() => {
                              handleToolAction(tool.id);
                              setToolbarExpanded(null);
                            }}
                            className={`p-2 rounded transition-colors ${
                              activeTool === tool.id ? themeClasses.accent : themeClasses.button
                            }`}
                            title={tool.tooltip}
                          >
                            <tool.icon className="w-4 h-4" />
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* PDF Viewer Ana Alanı */}
        <div className="flex-1 overflow-auto p-4 bg-gray-100 dark:bg-gray-900">
          <div className="flex justify-center">
            <div
              ref={viewerRef}
              className="relative bg-white shadow-lg transition-transform"
              style={{
                transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                transformOrigin: 'center center'
              }}
            >
              {/* Simulated PDF Page */}
              <div className="w-[595px] h-[842px] bg-white border p-8 relative">
                {/* Canvas for annotations */}
                <canvas
                  ref={canvasRef}
                  className="absolute inset-0 w-full h-full pointer-events-none"
                  width={595}
                  height={842}
                />

                {/* PDF Content */}
                <div className="h-full">
                  <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">
                      {pdfData?.fileName || 'PDF Dökümanı'}
                    </h1>
                    <div className="text-sm text-gray-500">
                      Sayfa {currentPage} / {totalPages}
                    </div>
                  </div>
                  <div className="space-y-4 text-gray-700">
                    <div className="h-3 bg-gray-300 rounded animate-pulse"></div>
                    <div className="h-3 bg-gray-300 rounded w-3/4 animate-pulse"></div>
                    <div className="h-3 bg-gray-300 rounded w-1/2 animate-pulse"></div>
                    <div className="h-32 bg-gray-200 rounded-lg animate-pulse"></div>
                    <div className="h-3 bg-gray-300 rounded animate-pulse"></div>
                    <div className="h-3 bg-gray-300 rounded w-2/3 animate-pulse"></div>
                    
                    {/* Render annotations */}
                    {annotations
                      .filter(ann => ann.page === currentPage)
                      .map(annotation => (
                        <div
                          key={annotation.id}
                          className="absolute rounded transition-all hover:shadow-md"
                          style={{
                            left: annotation.position?.x || 100,
                            top: annotation.position?.y || 100,
                            backgroundColor: annotation.color,
                            padding: annotation.type === 'highlight' ? '2px 4px' : '4px 8px',
                          }}
                        >
                          {annotation.type === 'text-note' && (
                            <div className="text-sm text-black">{annotation.content}</div>
                          )}
                          {annotation.type === 'sticky-note' && (
                            <MessageSquare className="w-4 h-4" />
                          )}
                        </div>
                      ))}
                  </div>
                </div>

                {/* Sayfa numarası */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-sm text-gray-500">
                  {currentPage}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Alt Status Bar */}
        <div className={`${themeClasses.toolbar} border-t ${themeClasses.border} px-4 py-2 flex justify-between items-center text-sm`}>
          <div className="flex items-center space-x-4">
            <span>Sayfa {currentPage} / {totalPages}</span>
            <span>Zoom: {zoom}%</span>
            {activeTool && <span>Aktif araç: {activeTool}</span>}
            {rotation !== 0 && <span>Döndürme: {rotation}°</span>}
          </div>
          <div className="flex items-center space-x-2">
            <span>{annotations.length} açıklama</span>
            <span>•</span>
            <span>{bookmarks.length} yer işareti</span>
            {pdfData?.fileSize && (
              <>
                <span>•</span>
                <span>{formatFileSize(pdfData.fileSize)}</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

// Utility function
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

EmbeddedPDFViewer.displayName = 'EmbeddedPDFViewer';

export default EmbeddedPDFViewer;
        border: 'border-gray-700',
        button: 'bg-gray-700 hover:bg-gray-600 border-gray-600',
        accent: 'bg-blue-600 text-white hover:bg-blue-700'
      },
      neon: {
        bg: 'bg-purple-900',
        sidebar: 'bg-purple-800',
        toolbar: 'bg-purple-800 border-purple-600',
        text: 'text-white',
