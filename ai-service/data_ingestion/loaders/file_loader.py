"""
File Loader

Handles loading and preprocessing of CV files before parsing.
"""

import os
import hashlib
import json
from typing import Dict, Any, Optional, BinaryIO
from pathlib import Path
from datetime import datetime

from ..config.ingestion_config import IngestionConfig


class FileLoader:
    """Loads and preprocesses CV files"""
    
    def __init__(self, config: Optional[IngestionConfig] = None):
        """
        Initialize the file loader
        
        Args:
            config: Optional configuration instance
        """
        self.config = config or IngestionConfig()
        self.cache_enabled = self.config.enable_caching
        self.cache_dir = self.config.get_cache_path()
        
        if self.cache_enabled:
            self.config.ensure_cache_directory()
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load a CV file
        
        Args:
            file_path: Path to the CV file
            
        Returns:
            Dictionary with file metadata and content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported or size exceeds limit
        """
        path = Path(file_path)
        
        # Validate file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file format
        if not self.config.is_supported_format(file_path):
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {self.config.supported_formats}"
            )
        
        # Validate file size
        file_size = path.stat().st_size
        if not self.config.is_file_size_valid(file_size):
            raise ValueError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.config.max_file_size_mb} MB)"
            )
        
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Generate file hash for caching
        file_hash = self._generate_file_hash(content)
        
        # Check cache if enabled
        if self.cache_enabled:
            cached_data = self._load_from_cache(file_hash)
            if cached_data:
                return cached_data
        
        # Prepare file metadata
        file_data = {
            'file_path': str(path.absolute()),
            'filename': path.name,
            'file_size': file_size,
            'file_extension': path.suffix,
            'file_hash': file_hash,
            'loaded_at': datetime.now().isoformat(),
            'content': content
        }
        
        return file_data
    
    def load_from_bytes(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Load CV from bytes content
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with file metadata and content
        """
        path = Path(filename)
        
        # Validate file format
        if not self.config.is_supported_format(filename):
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {self.config.supported_formats}"
            )
        
        # Validate file size
        file_size = len(content)
        if not self.config.is_file_size_valid(file_size):
            raise ValueError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.config.max_file_size_mb} MB)"
            )
        
        # Generate file hash
        file_hash = self._generate_file_hash(content)
        
        # Check cache if enabled
        if self.cache_enabled:
            cached_data = self._load_from_cache(file_hash)
            if cached_data:
                return cached_data
        
        # Prepare file metadata
        file_data = {
            'file_path': None,
            'filename': filename,
            'file_size': file_size,
            'file_extension': path.suffix,
            'file_hash': file_hash,
            'loaded_at': datetime.now().isoformat(),
            'content': content
        }
        
        return file_data
    
    def save_to_cache(self, file_hash: str, parsed_data: Dict[str, Any]) -> None:
        """
        Save parsed CV data to cache
        
        Args:
            file_hash: Hash of the original file
            parsed_data: Parsed CV data to cache
        """
        if not self.cache_enabled:
            return
        
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        # Add cache metadata
        cache_data = {
            'file_hash': file_hash,
            'cached_at': datetime.now().isoformat(),
            'data': parsed_data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save to cache: {e}")
    
    def _load_from_cache(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Load parsed data from cache
        
        Args:
            file_hash: Hash of the file to look up
            
        Returns:
            Cached data if found, None otherwise
        """
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Return the parsed data
            return cache_data.get('data')
        except Exception as e:
            print(f"Warning: Failed to load from cache: {e}")
            return None
    
    def _generate_file_hash(self, content: bytes) -> str:
        """
        Generate SHA-256 hash of file content
        
        Args:
            content: File content as bytes
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content).hexdigest()
    
    def clear_cache(self) -> int:
        """
        Clear all cached files
        
        Returns:
            Number of files deleted
        """
        if not self.cache_enabled or not self.cache_dir.exists():
            return 0
        
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                print(f"Warning: Failed to delete cache file {cache_file}: {e}")
        
        return count
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the cache
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_enabled:
            return {
                'enabled': False,
                'cache_dir': None,
                'file_count': 0,
                'total_size': 0
            }
        
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'enabled': True,
            'cache_dir': str(self.cache_dir),
            'file_count': len(cache_files),
            'total_size': total_size,
            'total_size_mb': total_size / 1024 / 1024
        }
    
    def validate_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate a file without loading it
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check existence
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # Check format
        if not self.config.is_supported_format(file_path):
            return False, (
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {self.config.supported_formats}"
            )
        
        # Check size
        file_size = path.stat().st_size
        if not self.config.is_file_size_valid(file_size):
            return False, (
                f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds "
                f"maximum allowed size ({self.config.max_file_size_mb} MB)"
            )
        
        return True, None
