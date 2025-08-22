[tool:pytest]
# PyPDF-Tools Pytest Configuration

# Test discovery
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test* *Tests
python_functions = test_*

# Minimum version
minversion = 7.0

# Additional options
addopts = 
    # Output formatting
    -ra
    --strict-markers
    --strict-config
    --tb=short
    --showlocals
    
    # Coverage options
    --cov=src/pypdf_tools
    --cov-branch
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
    
    # Performance
    --durations=10
    
    # Warnings
    --disable-warnings
    
    # Parallel execution
    -n auto

# Environment variables
env = 
    QT_QPA_PLATFORM = offscreen
    PYPDF_TEST_MODE = 1
    PYTHONPATH = src

# Markers for test categorization
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, multiple components)
    e2e: End-to-end tests (slowest, full application)
    gui: Tests that require GUI components
    cli: Command-line interface tests
    pdf: Tests that work with PDF files
    slow: Slow running tests
    network: Tests that require network access
    ai: AI feature tests
    security: Security-related tests
    performance: Performance/benchmark tests
    smoke: Smoke tests for basic functionality
    regression: Regression tests for known issues
    
# Test filtering
filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning:PyQt6.*
    ignore::PendingDeprecationWarning
    ignore:.*distutils.*:DeprecationWarning
    ignore:.*imp module.*:DeprecationWarning

# Logging configuration
log_cli = false
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S

# Test timeout (seconds)
timeout = 300
timeout_method = thread

# Collect ignore patterns
collect_ignore = [
    "setup.py",
    "docs/",
    "build/",
    "dist/",
    "web/node_modules/",
    "web/build/"
]

# Qt specific settings for GUI tests
qt_api = pyqt6
qt_no_exception_capture = 1

# Benchmark settings
benchmark_min_rounds = 3
benchmark_max_time = 10.0
benchmark_min_time = 0.000005
benchmark_timer = time.perf_counter
benchmark_disable_gc = false
benchmark_warmup = true
