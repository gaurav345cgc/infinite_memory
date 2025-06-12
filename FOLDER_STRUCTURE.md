# Project Folder Structure

## Current Structure
```
📁 infinite/
├── 📁 .git/                          # Git repository
├── 📁 src/                           # Source code directory
│   └── 📁 core/                      # Core modules (empty)
├── 📁 chroma_persist/                # ChromaDB persistence (excluded)
├── 📁 venv/                          # Virtual environment (excluded)
├── 📁 logs/                          # Log files (excluded)
├── 📁 chroma_perf_test/              # ChromaDB performance tests (excluded)
├── 📁 __pycache__/                   # Python cache (excluded)
├── 📄 .gitattributes                 # Git attributes
├── 📄 embedding.py                   # Embedding functionality
├── 📄 db.py                         # Database operations
├── 📄 app.py                        # Main application
├── 📄 logging_config.py             # Logging configuration
├── 📄 utils.py                      # Utility functions
├── 📄 latency_report_1749046092.csv # Performance report
├── 📄 testing.py                    # Testing scripts
├── 📄 models.py                     # Data models
├── 📄 transfer.py                   # Transfer operations
└── 📄 onnx.tar.gz                   # ONNX model archive
```

## Suggested Organized Structure
```
📁 infinite/
├── 📁 src/                           # Source code
│   ├── 📁 core/                      # Core application logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 app.py                 # Main application
│   │   └── 📄 models.py              # Data models
│   ├── 📁 database/                  # Database layer
│   │   ├── 📄 __init__.py
│   │   └── 📄 db.py                  # Database operations
│   ├── 📁 utils/                     # Utility functions
│   │   ├── 📄 __init__.py
│   │   ├── 📄 utils.py               # General utilities
│   │   ├── 📄 embedding.py           # Embedding utilities
│   │   └── 📄 transfer.py            # Transfer utilities
│   ├── 📁 automation/                # Automation tools
│   │   ├── 📄 __init__.py
│   │   └── 📄 autoclicker.py         # Auto-clicker
│   ├── 📁 config/                    # Configuration
│   │   ├── 📄 __init__.py
│   │   └── 📄 logging_config.py      # Logging configuration
│   └── 📁 tests/                     # Test files
│       ├── 📄 __init__.py
│       └── 📄 testing.py             # Test scripts
├── 📁 data/                          # Data files
│   └── 📄 latency_report_1749046092.csv
├── 📁 models/                        # Model files
│   └── 📄 onnx.tar.gz
├── 📁 docs/                          # Documentation
│   └── 📄 FOLDER_STRUCTURE.md
├── 📄 .gitattributes                 # Git attributes
├── 📄 requirements.txt               # Python dependencies
├── 📄 README.md                      # Project documentation
└── 📄 .gitignore                     # Git ignore rules

# Excluded Directories (as requested):
# 📁 venv/                           # Virtual environment
# 📁 logs/                           # Log files
# 📁 chroma_persist/                 # ChromaDB persistence
# 📁 chroma_perf_test/               # ChromaDB performance tests
# 📁 __pycache__/                    # Python cache
```

## Key Directories Explained

### 📁 src/
- **core/**: Main application logic and core functionality
- **database/**: Database operations and data access layer
- **utils/**: Utility functions and helper modules
- **automation/**: Automation tools and scripts
- **config/**: Configuration files and settings
- **tests/**: Test files and testing utilities

### 📁 data/
- Contains data files, reports, and datasets

### 📁 models/
- Contains model files, weights, and archives

### 📁 docs/
- Project documentation and guides

## Benefits of This Structure
1. **Separation of Concerns**: Each directory has a specific purpose
2. **Scalability**: Easy to add new modules and features
3. **Maintainability**: Clear organization makes code easier to find and maintain
4. **Testing**: Dedicated test directory for all test files
5. **Configuration**: Centralized configuration management
6. **Documentation**: Dedicated space for project docs

## Next Steps
To implement this structure:
1. Create the suggested directories
2. Move existing files to their appropriate locations
3. Update import statements in Python files
4. Create missing configuration files (requirements.txt, README.md, .gitignore) 