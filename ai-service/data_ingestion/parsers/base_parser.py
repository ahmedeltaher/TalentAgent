"""
Base Parser Abstract Class

Defines the interface for all CV parsers in the ingestion layer.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class BaseParser(ABC):
    """Abstract base class for CV parsers"""
    
    def __init__(self):
        """Initialize the parser"""
        self.parser_name = self.__class__.__name__
        self.version = "1.0.0"
    
    @abstractmethod
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a PDF file and extract CV information
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed CV data
        """
        pass
    
    @abstractmethod
    def parse_docx(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a DOCX file and extract CV information
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Dictionary containing parsed CV data
        """
        pass
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a file based on its extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing parsed CV data
            
        Raises:
            ValueError: If file format is not supported
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.parse_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract raw text from a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text as string
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self._extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    @abstractmethod
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        pass
    
    @abstractmethod
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        pass
    
    def validate_output(self, parsed_data: Dict[str, Any]) -> bool:
        """
        Validate the parsed data structure
        
        Args:
            parsed_data: The parsed CV data
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['skills', 'experience', 'education', 'email', 'phone']
        return all(key in parsed_data for key in required_keys)
    
    def default_response(self) -> Dict[str, Any]:
        """
        Return default empty response structure
        
        Returns:
            Default empty CV data structure
        """
        return {
            "skills": [],
            "experience": [],
            "education": [],
            "phone": None,
            "email": None,
            "years_of_experience": 0,
            "certifications": [],
            "projects": [],
            "languages": [],
            "parser_name": self.parser_name,
            "parser_version": self.version
        }
    
    def get_parser_info(self) -> Dict[str, str]:
        """
        Get parser information
        
        Returns:
            Dictionary with parser name and version
        """
        return {
            "name": self.parser_name,
            "version": self.version
        }
