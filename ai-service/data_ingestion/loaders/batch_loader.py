"""
Batch Loader

Handles batch processing of multiple CV files.
"""

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .file_loader import FileLoader
from ..config.ingestion_config import IngestionConfig


class BatchLoader:
    """Batch loader for processing multiple CV files"""
    
    def __init__(self, config: Optional[IngestionConfig] = None):
        """
        Initialize the batch loader
        
        Args:
            config: Optional configuration instance
        """
        self.config = config or IngestionConfig()
        self.file_loader = FileLoader(config)
        self.batch_size = self.config.batch_size
        self.enable_multiprocessing = self.config.enable_multiprocessing
        self.max_workers = self.config.max_workers
    
    def load_directory(
        self,
        directory_path: str,
        recursive: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Load all CV files from a directory
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to search recursively
            progress_callback: Optional callback function(current, total) for progress updates
            
        Returns:
            List of loaded file data dictionaries
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        # Find all CV files
        cv_files = self._find_cv_files(directory, recursive)
        
        if not cv_files:
            return []
        
        # Load files
        return self.load_files(cv_files, progress_callback)
    
    def load_files(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Load multiple CV files
        
        Args:
            file_paths: List of file paths to load
            progress_callback: Optional callback function(current, total) for progress updates
            
        Returns:
            List of loaded file data dictionaries
        """
        total_files = len(file_paths)
        loaded_files = []
        
        if self.enable_multiprocessing and total_files > 1:
            # Use multiprocessing for better performance
            loaded_files = self._load_files_parallel(file_paths, progress_callback)
        else:
            # Sequential loading
            loaded_files = self._load_files_sequential(file_paths, progress_callback)
        
        return loaded_files
    
    def load_batch(
        self,
        file_paths: List[str],
        start_index: int = 0,
        batch_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load a batch of CV files
        
        Args:
            file_paths: List of file paths
            start_index: Starting index for the batch
            batch_size: Size of the batch (uses config batch_size if not provided)
            
        Returns:
            List of loaded file data dictionaries
        """
        batch_size = batch_size or self.batch_size
        end_index = min(start_index + batch_size, len(file_paths))
        batch_files = file_paths[start_index:end_index]
        
        return self.load_files(batch_files)
    
    def _load_files_sequential(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """Load files sequentially"""
        loaded_files = []
        total_files = len(file_paths)
        
        for idx, file_path in enumerate(file_paths, 1):
            try:
                file_data = self.file_loader.load_file(file_path)
                loaded_files.append({
                    'success': True,
                    'data': file_data,
                    'error': None
                })
            except Exception as e:
                loaded_files.append({
                    'success': False,
                    'data': None,
                    'error': str(e),
                    'file_path': file_path
                })
            
            # Call progress callback
            if progress_callback:
                progress_callback(idx, total_files)
        
        return loaded_files
    
    def _load_files_parallel(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """Load files in parallel using ThreadPoolExecutor"""
        loaded_files = []
        total_files = len(file_paths)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._load_single_file, path): path
                for path in file_paths
            }
            
            # Process completed tasks
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                try:
                    result = future.result()
                    loaded_files.append(result)
                except Exception as e:
                    loaded_files.append({
                        'success': False,
                        'data': None,
                        'error': str(e),
                        'file_path': file_path
                    })
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total_files)
        
        return loaded_files
    
    def _load_single_file(self, file_path: str) -> Dict[str, Any]:
        """Load a single file (used for parallel processing)"""
        try:
            file_data = self.file_loader.load_file(file_path)
            return {
                'success': True,
                'data': file_data,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e),
                'file_path': file_path
            }
    
    def _find_cv_files(self, directory: Path, recursive: bool) -> List[str]:
        """Find all CV files in a directory"""
        cv_files = []
        
        if recursive:
            # Recursive search
            for ext in self.config.supported_formats:
                pattern = f"**/*{ext}"
                cv_files.extend([str(f) for f in directory.glob(pattern)])
        else:
            # Top-level search only
            for ext in self.config.supported_formats:
                pattern = f"*{ext}"
                cv_files.extend([str(f) for f in directory.glob(pattern)])
        
        return sorted(cv_files)
    
    def get_batch_info(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Get information about a batch of files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dictionary with batch information
        """
        total_files = len(file_paths)
        batch_count = (total_files + self.batch_size - 1) // self.batch_size
        
        # Estimate total size
        total_size = 0
        valid_files = 0
        invalid_files = []
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.exists():
                    total_size += path.stat().st_size
                    valid_files += 1
                else:
                    invalid_files.append(file_path)
            except Exception as e:
                invalid_files.append(file_path)
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': len(invalid_files),
            'invalid_file_paths': invalid_files,
            'batch_count': batch_count,
            'batch_size': self.batch_size,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / 1024 / 1024,
            'multiprocessing_enabled': self.enable_multiprocessing,
            'max_workers': self.max_workers if self.enable_multiprocessing else 1
        }
    
    def validate_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Validate a batch of files without loading them
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'total': len(file_paths),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
        
        for file_path in file_paths:
            is_valid, error_msg = self.file_loader.validate_file(file_path)
            if is_valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['errors'].append({
                    'file_path': file_path,
                    'error': error_msg
                })
        
        return results
