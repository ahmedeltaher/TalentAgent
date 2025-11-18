"""
CV Data Validator

Validates parsed CV data against quality and completeness requirements.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime


class CVValidator:
    """Validates CV data for completeness and quality"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the validator
        
        Args:
            config: Optional validation configuration
        """
        self.config = config or {}
        self.require_email = self.config.get('require_email', True)
        self.require_phone = self.config.get('require_phone', False)
        self.require_experience = self.config.get('require_experience', True)
        self.require_education = self.config.get('require_education', True)
        self.min_skills_count = self.config.get('min_skills_count', 1)
    
    def validate(self, cv_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate CV data
        
        Args:
            cv_data: Parsed CV data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate personal information
        errors.extend(self._validate_personal_info(cv_data))
        
        # Validate skills
        errors.extend(self._validate_skills(cv_data))
        
        # Validate experience
        errors.extend(self._validate_experience(cv_data))
        
        # Validate education
        errors.extend(self._validate_education(cv_data))
        
        # Validate data quality
        errors.extend(self._validate_data_quality(cv_data))
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _validate_personal_info(self, cv_data: Dict[str, Any]) -> List[str]:
        """Validate personal information"""
        errors = []
        
        email = cv_data.get('email')
        phone = cv_data.get('phone')
        
        # Email validation
        if self.require_email:
            if not email:
                errors.append("Email is required but not found")
            elif not self._is_valid_email(email):
                errors.append(f"Invalid email format: {email}")
        
        # Phone validation
        if self.require_phone:
            if not phone:
                errors.append("Phone number is required but not found")
            elif not self._is_valid_phone(phone):
                errors.append(f"Invalid phone format: {phone}")
        
        # At least one contact method
        if not email and not phone:
            errors.append("At least one contact method (email or phone) is required")
        
        return errors
    
    def _validate_skills(self, cv_data: Dict[str, Any]) -> List[str]:
        """Validate skills"""
        errors = []
        
        skills = cv_data.get('skills', [])
        
        if not isinstance(skills, list):
            errors.append("Skills must be a list")
            return errors
        
        if len(skills) < self.min_skills_count:
            errors.append(f"At least {self.min_skills_count} skill(s) required, found {len(skills)}")
        
        # Check for duplicate skills
        if len(skills) != len(set(skills)):
            errors.append("Duplicate skills found")
        
        # Check for empty or invalid skills
        for skill in skills:
            if not skill or not isinstance(skill, str):
                errors.append("Invalid skill entry found")
            elif len(skill.strip()) < 2:
                errors.append(f"Skill name too short: '{skill}'")
        
        return errors
    
    def _validate_experience(self, cv_data: Dict[str, Any]) -> List[str]:
        """Validate work experience"""
        errors = []
        
        experience = cv_data.get('experience', [])
        
        if not isinstance(experience, list):
            errors.append("Experience must be a list")
            return errors
        
        if self.require_experience and len(experience) == 0:
            errors.append("At least one work experience entry is required")
        
        # Validate each experience entry
        for idx, exp in enumerate(experience):
            if not isinstance(exp, dict):
                errors.append(f"Experience entry {idx} is not a valid dictionary")
                continue
            
            # Check required fields
            required_fields = ['title', 'company', 'startDate', 'endDate']
            for field in required_fields:
                if not exp.get(field):
                    errors.append(f"Experience entry {idx}: Missing required field '{field}'")
            
            # Validate dates
            if exp.get('startDate') and exp.get('endDate'):
                if not self._is_valid_date_range(exp['startDate'], exp['endDate']):
                    errors.append(f"Experience entry {idx}: Invalid date range")
        
        return errors
    
    def _validate_education(self, cv_data: Dict[str, Any]) -> List[str]:
        """Validate education"""
        errors = []
        
        education = cv_data.get('education', [])
        
        if not isinstance(education, list):
            errors.append("Education must be a list")
            return errors
        
        if self.require_education and len(education) == 0:
            errors.append("At least one education entry is required")
        
        # Validate each education entry
        for idx, edu in enumerate(education):
            if not isinstance(edu, dict):
                errors.append(f"Education entry {idx} is not a valid dictionary")
                continue
            
            # Check required fields
            required_fields = ['degree', 'institution']
            for field in required_fields:
                if not edu.get(field):
                    errors.append(f"Education entry {idx}: Missing required field '{field}'")
            
            # Validate dates if present
            if edu.get('startDate') and edu.get('endDate'):
                if not self._is_valid_date_range(edu['startDate'], edu['endDate']):
                    errors.append(f"Education entry {idx}: Invalid date range")
        
        return errors
    
    def _validate_data_quality(self, cv_data: Dict[str, Any]) -> List[str]:
        """Validate overall data quality"""
        errors = []
        
        # Check years of experience
        years_exp = cv_data.get('years_of_experience', 0)
        if years_exp < 0:
            errors.append("Years of experience cannot be negative")
        elif years_exp > 70:
            errors.append(f"Years of experience seems unrealistic: {years_exp}")
        
        # Check if experience years match with actual experience entries
        experience = cv_data.get('experience', [])
        if years_exp > 0 and len(experience) == 0:
            errors.append("Years of experience specified but no experience entries found")
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone format"""
        if not phone:
            return False
        
        # Remove common separators and check if we have enough digits
        digits = re.sub(r'[\s\-\(\)\.]', '', phone)
        return len(digits) >= 10 and digits.isdigit()
    
    def _is_valid_date_range(self, start_date: str, end_date: str) -> bool:
        """Validate date range"""
        try:
            # Extract years from dates
            start_year = self._extract_year(start_date)
            end_year = self._extract_year(end_date)
            
            if not start_year:
                return True  # Skip validation if we can't parse
            
            # Check if end date is "Present"
            if "present" in end_date.lower():
                end_year = datetime.now().year
            
            if not end_year:
                return True
            
            # Start year should not be after end year
            if start_year > end_year:
                return False
            
            # Date range should be reasonable (not more than 50 years)
            if end_year - start_year > 50:
                return False
            
            return True
        except:
            return True  # Skip validation on error
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        
        # Look for 4-digit year
        year_match = re.search(r'(19|20)\d{2}', date_str)
        if year_match:
            return int(year_match.group(0))
        
        return None
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a specific field
        
        Args:
            field_name: Name of the field to validate
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if field_name == 'email':
            if not self._is_valid_email(value):
                return False, f"Invalid email format: {value}"
        
        elif field_name == 'phone':
            if not self._is_valid_phone(value):
                return False, f"Invalid phone format: {value}"
        
        elif field_name == 'skills':
            if not isinstance(value, list) or len(value) < self.min_skills_count:
                return False, f"Skills must be a list with at least {self.min_skills_count} item(s)"
        
        elif field_name == 'experience':
            if not isinstance(value, list):
                return False, "Experience must be a list"
        
        elif field_name == 'education':
            if not isinstance(value, list):
                return False, "Education must be a list"
        
        return True, None
    
    def get_data_completeness_score(self, cv_data: Dict[str, Any]) -> float:
        """
        Calculate data completeness score (0.0 to 1.0)
        
        Args:
            cv_data: Parsed CV data
            
        Returns:
            Completeness score between 0 and 1
        """
        score = 0.0
        max_score = 0.0
        
        # Email (15 points)
        max_score += 15
        if cv_data.get('email') and self._is_valid_email(cv_data['email']):
            score += 15
        
        # Phone (10 points)
        max_score += 10
        if cv_data.get('phone') and self._is_valid_phone(cv_data['phone']):
            score += 10
        
        # Skills (20 points)
        max_score += 20
        skills = cv_data.get('skills', [])
        if len(skills) >= 5:
            score += 20
        elif len(skills) > 0:
            score += (len(skills) / 5) * 20
        
        # Experience (25 points)
        max_score += 25
        experience = cv_data.get('experience', [])
        if len(experience) >= 3:
            score += 25
        elif len(experience) > 0:
            score += (len(experience) / 3) * 25
        
        # Education (20 points)
        max_score += 20
        education = cv_data.get('education', [])
        if len(education) >= 2:
            score += 20
        elif len(education) > 0:
            score += (len(education) / 2) * 20
        
        # Years of experience (10 points)
        max_score += 10
        years = cv_data.get('years_of_experience', 0)
        if years > 0:
            score += min(10, years)
        
        return score / max_score if max_score > 0 else 0.0
