"""
Data Models and Schemas for CV/Resume Data

Defines the structured data models for parsed CV information.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class SkillCategory(Enum):
    """Skill category enumeration"""
    PROGRAMMING = "programming"
    WEB = "web"
    MOBILE = "mobile"
    DATABASE = "database"
    CLOUD = "cloud"
    AI_ML = "ai_ml"
    TOOLS = "tools"
    TESTING = "testing"
    DEVOPS = "devops"
    SOFT_SKILLS = "soft_skills"
    OTHER = "other"


class DegreeLevel(Enum):
    """Education degree level enumeration"""
    PHD = "PhD"
    MASTERS = "Master's"
    BACHELORS = "Bachelor's"
    ASSOCIATE = "Associate"
    DIPLOMA = "Diploma"
    CERTIFICATE = "Certificate"
    OTHER = "Other"


@dataclass
class Skill:
    """Skill data model"""
    name: str
    category: Optional[SkillCategory] = None
    proficiency: Optional[str] = None  # Beginner, Intermediate, Advanced, Expert
    years_experience: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.category:
            data['category'] = self.category.value
        return data


@dataclass
class Experience:
    """Work experience data model"""
    title: str
    company: str
    start_date: str
    end_date: str
    description: Optional[str] = ""
    responsibilities: List[str] = field(default_factory=list)
    location: Optional[str] = None
    is_current: bool = False
    duration_months: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def calculate_duration(self) -> int:
        """Calculate duration in months"""
        try:
            # Parse dates and calculate duration
            # This is a simplified calculation
            if "present" in self.end_date.lower():
                end_year = datetime.now().year
            else:
                end_year = int(self.end_date.split()[-1]) if self.end_date else datetime.now().year
            
            start_year = int(self.start_date.split()[-1]) if self.start_date else end_year
            
            duration = (end_year - start_year) * 12
            self.duration_months = max(0, duration)
            return self.duration_months
        except:
            self.duration_months = 0
            return 0


@dataclass
class Education:
    """Education data model"""
    degree: str
    institution: str
    start_date: str
    end_date: str
    field_of_study: Optional[str] = None
    gpa: Optional[float] = None
    honors: Optional[str] = None
    location: Optional[str] = None
    degree_level: Optional[DegreeLevel] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.degree_level:
            data['degree_level'] = self.degree_level.value
        return data


@dataclass
class PersonalInfo:
    """Personal information data model"""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Certification:
    """Certification data model"""
    name: str
    issuer: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Project:
    """Project data model"""
    name: str
    description: str
    technologies: List[str] = field(default_factory=list)
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    role: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Language:
    """Language proficiency data model"""
    language: str
    proficiency: str  # Native, Fluent, Professional, Limited
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CVSchema:
    """Complete CV data schema"""
    personal_info: PersonalInfo
    skills: List[Skill] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    languages: List[Language] = field(default_factory=list)
    years_of_experience: float = 0.0
    raw_text: Optional[str] = None
    parsed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    parser_version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complete CV schema to dictionary"""
        return {
            "personal_info": self.personal_info.to_dict(),
            "skills": [skill.to_dict() for skill in self.skills],
            "experience": [exp.to_dict() for exp in self.experience],
            "education": [edu.to_dict() for edu in self.education],
            "certifications": [cert.to_dict() for cert in self.certifications],
            "projects": [proj.to_dict() for proj in self.projects],
            "languages": [lang.to_dict() for lang in self.languages],
            "years_of_experience": self.years_of_experience,
            "raw_text": self.raw_text[:500] if self.raw_text else None,  # Truncate for storage
            "parsed_at": self.parsed_at,
            "parser_version": self.parser_version
        }
    
    def validate(self) -> List[str]:
        """Validate the CV schema and return list of validation errors"""
        errors = []
        
        # Validate personal info
        if not self.personal_info.email and not self.personal_info.phone:
            errors.append("At least one contact method (email or phone) is required")
        
        # Validate email format if present
        if self.personal_info.email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.personal_info.email):
                errors.append(f"Invalid email format: {self.personal_info.email}")
        
        # Validate experience
        if not self.experience:
            errors.append("At least one work experience entry is recommended")
        
        # Validate education
        if not self.education:
            errors.append("At least one education entry is recommended")
        
        # Validate skills
        if not self.skills:
            errors.append("At least one skill is required")
        
        return errors
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CVSchema':
        """Create CVSchema from dictionary"""
        return cls(
            personal_info=PersonalInfo(**data.get('personal_info', {})),
            skills=[Skill(**skill) for skill in data.get('skills', [])],
            experience=[Experience(**exp) for exp in data.get('experience', [])],
            education=[Education(**edu) for edu in data.get('education', [])],
            certifications=[Certification(**cert) for cert in data.get('certifications', [])],
            projects=[Project(**proj) for proj in data.get('projects', [])],
            languages=[Language(**lang) for lang in data.get('languages', [])],
            years_of_experience=data.get('years_of_experience', 0.0),
            raw_text=data.get('raw_text'),
            parsed_at=data.get('parsed_at', datetime.now().isoformat()),
            parser_version=data.get('parser_version', '1.0.0')
        )
