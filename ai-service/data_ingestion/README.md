# Data Loading & Ingestion Layer

A comprehensive, modular data ingestion system for processing CV/Resume documents in the Agentic AI Recruitment System.

## Overview

The Data Loading & Ingestion Layer provides a complete pipeline for loading, parsing, validating, and transforming CV/Resume data into standardized formats. It is designed with modularity, extensibility, and performance in mind.

## Architecture

```
data_ingestion/
├── config/              # Configuration management
│   ├── ingestion_config.py
│   └── __init__.py
├── loaders/             # File loading and batch processing
│   ├── file_loader.py
│   ├── batch_loader.py
│   └── __init__.py
├── parsers/             # CV parsing implementations
│   ├── base_parser.py
│   ├── advanced_cv_parser.py
│   └── __init__.py
├── models/              # Data models and schemas
│   ├── cv_schema.py
│   └── __init__.py
├── validators/          # Data validation
│   ├── cv_validator.py
│   └── __init__.py
├── transformers/        # Data transformation
│   ├── data_transformer.py
│   └── __init__.py
└── __init__.py
```

## Features

### 1. **File Loading**
- Support for PDF and DOCX formats
- File size validation
- Content caching for performance
- Batch processing capabilities
- Parallel processing support

### 2. **CV Parsing**
- **Advanced CV Parser**: Regex-based extraction with comprehensive patterns
- **Base Parser**: Abstract class for custom parser implementations
- Extraction of:
  - Personal information (name, email, phone)
  - Skills with categorization
  - Work experience with dates
  - Education credentials
  - Certifications
  - Projects
  - Languages

### 3. **Data Validation**
- Email and phone format validation
- Required field checking
- Data quality scoring
- Date range validation
- Completeness assessment

### 4. **Data Transformation**
- Normalization of dates, emails, and phone numbers
- Skill categorization
- Degree level determination
- Schema-based data structuring
- JSON-compatible output

### 5. **Configuration Management**
- Environment variable support
- Flexible configuration options
- Cache management
- Performance tuning settings

## Quick Start

### Basic Usage

```python
from data_ingestion import AdvancedCVParser, FileLoader, DataTransformer, CVValidator

# Initialize components
file_loader = FileLoader()
parser = AdvancedCVParser()
transformer = DataTransformer()
validator = CVValidator()

# Load and parse a CV
file_data = file_loader.load_file("path/to/cv.pdf")
parsed_data = parser.parse_pdf("path/to/cv.pdf")

# Transform to structured schema
cv_schema = transformer.transform(parsed_data)

# Validate the data
is_valid, errors = validator.validate(parsed_data)

# Convert to dictionary
cv_dict = cv_schema.to_dict()
```

### Batch Processing

```python
from data_ingestion import BatchLoader, AdvancedCVParser

# Initialize batch loader
batch_loader = BatchLoader()
parser = AdvancedCVParser()

# Load all CVs from a directory
def progress_callback(current, total):
    print(f"Processing: {current}/{total}")

loaded_files = batch_loader.load_directory(
    "path/to/cv/directory",
    recursive=True,
    progress_callback=progress_callback
)

# Process each file
for file_result in loaded_files:
    if file_result['success']:
        file_data = file_result['data']
        parsed_data = parser.parse_file(file_data['file_path'])
        # Process parsed_data...
```

### Configuration

```python
from data_ingestion.config import IngestionConfig, set_config

# Create custom configuration
config = IngestionConfig(
    max_file_size_mb=15,
    batch_size=20,
    enable_caching=True,
    enable_multiprocessing=True,
    max_workers=8
)

# Set as global configuration
set_config(config)

# Or load from environment variables
config = IngestionConfig.from_env()
```

## Configuration Options

### Environment Variables

```bash
# File Processing
INGESTION_MAX_FILE_SIZE_MB=10
INGESTION_BATCH_SIZE=10

# Caching
INGESTION_ENABLE_CACHING=true
INGESTION_CACHE_DIR=cv_cache

# Validation
INGESTION_REQUIRE_EMAIL=true
INGESTION_REQUIRE_PHONE=false
INGESTION_MIN_SKILLS_COUNT=1

# Performance
INGESTION_ENABLE_MULTIPROCESSING=false
INGESTION_MAX_WORKERS=4
```

## Data Models

### CVSchema

The main data structure representing a parsed CV:

```python
@dataclass
class CVSchema:
    personal_info: PersonalInfo
    skills: List[Skill]
    experience: List[Experience]
    education: List[Education]
    certifications: List[Certification]
    projects: List[Project]
    languages: List[Language]
    years_of_experience: float
    raw_text: Optional[str]
    parsed_at: str
    parser_version: str
```

### Sub-Models

- **PersonalInfo**: Name, email, phone, location, social links
- **Skill**: Name, category, proficiency, years of experience
- **Experience**: Title, company, dates, description, responsibilities
- **Education**: Degree, institution, dates, field of study, GPA
- **Certification**: Name, issuer, dates, credential ID
- **Project**: Name, description, technologies, dates, role
- **Language**: Language name, proficiency level

## Advanced Features

### Custom Parser Implementation

```python
from data_ingestion.parsers import BaseParser

class CustomCVParser(BaseParser):
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        # Custom PDF parsing logic
        pass
    
    def parse_docx(self, file_path: str) -> Dict[str, Any]:
        # Custom DOCX parsing logic
        pass
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        # PDF text extraction
        pass
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        # DOCX text extraction
        pass
```

### Validation with Custom Rules

```python
from data_ingestion import CVValidator

# Create validator with custom config
validator = CVValidator({
    'require_email': True,
    'require_phone': True,
    'require_experience': True,
    'require_education': True,
    'min_skills_count': 3
})

# Validate
is_valid, errors = validator.validate(parsed_data)

# Get completeness score
score = validator.get_data_completeness_score(parsed_data)
print(f"Completeness: {score * 100:.1f}%")
```

### Cache Management

```python
from data_ingestion import FileLoader

file_loader = FileLoader()

# Get cache information
cache_info = file_loader.get_cache_info()
print(f"Cached files: {cache_info['file_count']}")
print(f"Cache size: {cache_info['total_size_mb']:.2f} MB")

# Clear cache
deleted_count = file_loader.clear_cache()
print(f"Deleted {deleted_count} cached files")
```

## Performance Considerations

### Caching
- Enabled by default
- Uses SHA-256 file hashing
- Stores parsed results in JSON format
- Automatic cache lookup on subsequent loads

### Parallel Processing
- Optional multiprocessing support
- Configurable worker count
- Best for batch operations with multiple files
- Thread-safe implementation

### Memory Management
- Raw text truncation (configurable)
- Streaming file processing
- Batch size control
- Efficient data structures

## Error Handling

The module provides comprehensive error handling:

```python
from data_ingestion import FileLoader

try:
    file_data = file_loader.load_file("cv.pdf")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid file: {e}")
```

## Integration with Existing Services

The data ingestion layer can be integrated with the existing `enhanced_cv_service.py`:

```python
from data_ingestion import (
    AdvancedCVParser,
    DataTransformer,
    CVValidator,
    FileLoader
)

class EnhancedCVService:
    def __init__(self):
        self.parser = AdvancedCVParser()
        self.transformer = DataTransformer()
        self.validator = CVValidator()
        self.file_loader = FileLoader()
    
    def process_cv(self, file_path: str):
        # Load file
        file_data = self.file_loader.load_file(file_path)
        
        # Parse
        parsed_data = self.parser.parse_file(file_path)
        
        # Validate
        is_valid, errors = self.validator.validate(parsed_data)
        
        # Transform
        cv_schema = self.transformer.transform(parsed_data)
        
        return cv_schema.to_dict()
```

## Testing

```python
# Example test
from data_ingestion import AdvancedCVParser

def test_parser():
    parser = AdvancedCVParser()
    result = parser.parse_pdf("test_cv.pdf")
    
    assert result['email'] is not None
    assert len(result['skills']) > 0
    assert len(result['experience']) > 0
```

## Dependencies

- PyPDF2: PDF text extraction
- python-docx: DOCX document processing
- Standard library: re, pathlib, hashlib, json, datetime

## Future Enhancements

- [ ] Support for more file formats (TXT, RTF)
- [ ] AI/LLM-based parsing integration
- [ ] Advanced skill matching and normalization
- [ ] Resume quality scoring
- [ ] Multi-language support
- [ ] OCR for scanned documents
- [ ] Real-time processing API

## License

Part of the Agentic AI Recruitment System

## Contributing

To contribute to the data ingestion layer:
1. Follow the existing architecture patterns
2. Add comprehensive documentation
3. Include unit tests
4. Update this README with new features
