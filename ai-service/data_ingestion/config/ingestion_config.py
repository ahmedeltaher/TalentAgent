"""
Ingestion Configuration Module

Manages configuration settings for the data ingestion layer.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IngestionConfig:
    """Configuration for data ingestion layer"""
    
    # File processing settings
    max_file_size_mb: int = 10
    supported_formats: list = field(default_factory=lambda: ['.pdf', '.docx', '.doc'])
    batch_size: int = 10
    
    # Parser settings
    default_parser: str = "AdvancedCVParser"
    parser_timeout: int = 30  # seconds
    enable_caching: bool = True
    cache_directory: str = "cv_cache"
    
    # Extraction settings
    extract_certifications: bool = True
    extract_projects: bool = True
    extract_languages: bool = True
    min_skill_confidence: float = 0.6
    
    # Validation settings
    require_email: bool = True
    require_phone: bool = False
    require_experience: bool = True
    require_education: bool = True
    min_skills_count: int = 1
    
    # Output settings
    output_format: str = "json"  # json, dict, schema
    include_raw_text: bool = True
    truncate_raw_text: int = 1000
    
    # Performance settings
    enable_multiprocessing: bool = False
    max_workers: int = 4
    
    # Logging settings
    log_level: str = "INFO"
    log_parsing_errors: bool = True
    
    @classmethod
    def from_env(cls) -> 'IngestionConfig':
        """Create configuration from environment variables"""
        return cls(
            max_file_size_mb=int(os.getenv('INGESTION_MAX_FILE_SIZE_MB', '10')),
            batch_size=int(os.getenv('INGESTION_BATCH_SIZE', '10')),
            default_parser=os.getenv('INGESTION_DEFAULT_PARSER', 'AdvancedCVParser'),
            parser_timeout=int(os.getenv('INGESTION_PARSER_TIMEOUT', '30')),
            enable_caching=os.getenv('INGESTION_ENABLE_CACHING', 'true').lower() == 'true',
            cache_directory=os.getenv('INGESTION_CACHE_DIR', 'cv_cache'),
            extract_certifications=os.getenv('INGESTION_EXTRACT_CERTS', 'true').lower() == 'true',
            extract_projects=os.getenv('INGESTION_EXTRACT_PROJECTS', 'true').lower() == 'true',
            extract_languages=os.getenv('INGESTION_EXTRACT_LANGUAGES', 'true').lower() == 'true',
            min_skill_confidence=float(os.getenv('INGESTION_MIN_SKILL_CONFIDENCE', '0.6')),
            require_email=os.getenv('INGESTION_REQUIRE_EMAIL', 'true').lower() == 'true',
            require_phone=os.getenv('INGESTION_REQUIRE_PHONE', 'false').lower() == 'true',
            require_experience=os.getenv('INGESTION_REQUIRE_EXPERIENCE', 'true').lower() == 'true',
            require_education=os.getenv('INGESTION_REQUIRE_EDUCATION', 'true').lower() == 'true',
            min_skills_count=int(os.getenv('INGESTION_MIN_SKILLS_COUNT', '1')),
            output_format=os.getenv('INGESTION_OUTPUT_FORMAT', 'json'),
            include_raw_text=os.getenv('INGESTION_INCLUDE_RAW_TEXT', 'true').lower() == 'true',
            truncate_raw_text=int(os.getenv('INGESTION_TRUNCATE_RAW_TEXT', '1000')),
            enable_multiprocessing=os.getenv('INGESTION_ENABLE_MULTIPROCESSING', 'false').lower() == 'true',
            max_workers=int(os.getenv('INGESTION_MAX_WORKERS', '4')),
            log_level=os.getenv('INGESTION_LOG_LEVEL', 'INFO'),
            log_parsing_errors=os.getenv('INGESTION_LOG_PARSING_ERRORS', 'true').lower() == 'true',
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'IngestionConfig':
        """Create configuration from dictionary"""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'max_file_size_mb': self.max_file_size_mb,
            'supported_formats': self.supported_formats,
            'batch_size': self.batch_size,
            'default_parser': self.default_parser,
            'parser_timeout': self.parser_timeout,
            'enable_caching': self.enable_caching,
            'cache_directory': self.cache_directory,
            'extract_certifications': self.extract_certifications,
            'extract_projects': self.extract_projects,
            'extract_languages': self.extract_languages,
            'min_skill_confidence': self.min_skill_confidence,
            'require_email': self.require_email,
            'require_phone': self.require_phone,
            'require_experience': self.require_experience,
            'require_education': self.require_education,
            'min_skills_count': self.min_skills_count,
            'output_format': self.output_format,
            'include_raw_text': self.include_raw_text,
            'truncate_raw_text': self.truncate_raw_text,
            'enable_multiprocessing': self.enable_multiprocessing,
            'max_workers': self.max_workers,
            'log_level': self.log_level,
            'log_parsing_errors': self.log_parsing_errors,
        }
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
        
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        
        if self.parser_timeout <= 0:
            raise ValueError("parser_timeout must be positive")
        
        if not 0 <= self.min_skill_confidence <= 1:
            raise ValueError("min_skill_confidence must be between 0 and 1")
        
        if self.min_skills_count < 0:
            raise ValueError("min_skills_count must be non-negative")
        
        if self.output_format not in ['json', 'dict', 'schema']:
            raise ValueError("output_format must be 'json', 'dict', or 'schema'")
        
        if self.max_workers <= 0:
            raise ValueError("max_workers must be positive")
        
        return True
    
    def get_cache_path(self) -> Path:
        """Get the cache directory path"""
        return Path(self.cache_directory)
    
    def ensure_cache_directory(self) -> Path:
        """Ensure cache directory exists and return path"""
        cache_path = self.get_cache_path()
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def is_file_size_valid(self, file_size_bytes: int) -> bool:
        """Check if file size is within limits"""
        max_size_bytes = self.max_file_size_mb * 1024 * 1024
        return file_size_bytes <= max_size_bytes


# Global configuration instance
_global_config: Optional[IngestionConfig] = None


def get_config() -> IngestionConfig:
    """Get the global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = IngestionConfig.from_env()
    return _global_config


def set_config(config: IngestionConfig) -> None:
    """Set the global configuration instance"""
    global _global_config
    _global_config = config


def reset_config() -> None:
    """Reset configuration to default"""
    global _global_config
    _global_config = None
