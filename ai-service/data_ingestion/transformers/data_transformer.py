"""
Data Transformer

Transforms and normalizes parsed CV data into standardized formats.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from ..models.cv_schema import (
    CVSchema, PersonalInfo, Experience, Education, Skill,
    Certification, Project, Language, SkillCategory, DegreeLevel
)


class DataTransformer:
    """Transforms parsed CV data into standardized schema"""
    
    def __init__(self):
        """Initialize the data transformer"""
        self.skill_category_mapping = self._build_skill_category_mapping()
        self.degree_level_mapping = self._build_degree_level_mapping()
    
    def transform(self, parsed_data: Dict[str, Any]) -> CVSchema:
        """
        Transform parsed data into CVSchema
        
        Args:
            parsed_data: Raw parsed CV data
            
        Returns:
            CVSchema instance
        """
        # Transform personal info
        personal_info = self._transform_personal_info(parsed_data)
        
        # Transform skills
        skills = self._transform_skills(parsed_data.get('skills', []))
        
        # Transform experience
        experience = self._transform_experience(parsed_data.get('experience', []))
        
        # Transform education
        education = self._transform_education(parsed_data.get('education', []))
        
        # Transform certifications
        certifications = self._transform_certifications(parsed_data.get('certifications', []))
        
        # Transform projects
        projects = self._transform_projects(parsed_data.get('projects', []))
        
        # Transform languages
        languages = self._transform_languages(parsed_data.get('languages', []))
        
        # Create CVSchema
        cv_schema = CVSchema(
            personal_info=personal_info,
            skills=skills,
            experience=experience,
            education=education,
            certifications=certifications,
            projects=projects,
            languages=languages,
            years_of_experience=float(parsed_data.get('years_of_experience', 0)),
            raw_text=parsed_data.get('raw_text'),
            parser_version=parsed_data.get('parser_version', '1.0.0')
        )
        
        return cv_schema
    
    def _transform_personal_info(self, parsed_data: Dict[str, Any]) -> PersonalInfo:
        """Transform personal information"""
        return PersonalInfo(
            full_name=parsed_data.get('full_name'),
            email=self._normalize_email(parsed_data.get('email')),
            phone=self._normalize_phone(parsed_data.get('phone')),
            location=parsed_data.get('location'),
            linkedin=parsed_data.get('linkedin'),
            github=parsed_data.get('github'),
            website=parsed_data.get('website'),
            summary=parsed_data.get('summary')
        )
    
    def _transform_skills(self, skills_data: List) -> List[Skill]:
        """Transform skills"""
        skills = []
        
        for skill_item in skills_data:
            if isinstance(skill_item, str):
                # Simple string skill
                skill = Skill(
                    name=skill_item.strip(),
                    category=self._categorize_skill(skill_item),
                    proficiency=None,
                    years_experience=None
                )
            elif isinstance(skill_item, dict):
                # Dictionary with metadata
                skill = Skill(
                    name=skill_item.get('name', '').strip(),
                    category=self._categorize_skill(skill_item.get('name', '')),
                    proficiency=skill_item.get('proficiency'),
                    years_experience=skill_item.get('years_experience')
                )
            else:
                continue
            
            if skill.name:
                skills.append(skill)
        
        return skills
    
    def _transform_experience(self, experience_data: List) -> List[Experience]:
        """Transform work experience"""
        experiences = []
        
        for exp_item in experience_data:
            if not isinstance(exp_item, dict):
                continue
            
            experience = Experience(
                title=exp_item.get('title', ''),
                company=exp_item.get('company', ''),
                start_date=self._normalize_date(exp_item.get('startDate', '')),
                end_date=self._normalize_date(exp_item.get('endDate', '')),
                description=exp_item.get('description', ''),
                responsibilities=exp_item.get('responsibilities', []),
                location=exp_item.get('location'),
                is_current='present' in str(exp_item.get('endDate', '')).lower(),
                duration_months=None
            )
            
            # Calculate duration
            experience.calculate_duration()
            
            experiences.append(experience)
        
        return experiences
    
    def _transform_education(self, education_data: List) -> List[Education]:
        """Transform education"""
        educations = []
        
        for edu_item in education_data:
            if not isinstance(edu_item, dict):
                continue
            
            degree = edu_item.get('degree', '')
            
            education = Education(
                degree=degree,
                institution=edu_item.get('institution', ''),
                start_date=self._normalize_date(edu_item.get('startDate', '')),
                end_date=self._normalize_date(edu_item.get('endDate', '')),
                field_of_study=edu_item.get('fieldOfStudy'),
                gpa=edu_item.get('gpa'),
                honors=edu_item.get('honors'),
                location=edu_item.get('location'),
                degree_level=self._determine_degree_level(degree)
            )
            
            educations.append(education)
        
        return educations
    
    def _transform_certifications(self, certifications_data: List) -> List[Certification]:
        """Transform certifications"""
        certifications = []
        
        for cert_item in certifications_data:
            if not isinstance(cert_item, dict):
                continue
            
            certification = Certification(
                name=cert_item.get('name', ''),
                issuer=cert_item.get('issuer', ''),
                issue_date=self._normalize_date(cert_item.get('issue_date', '')),
                expiry_date=self._normalize_date(cert_item.get('expiry_date', '')),
                credential_id=cert_item.get('credential_id'),
                url=cert_item.get('url')
            )
            
            certifications.append(certification)
        
        return certifications
    
    def _transform_projects(self, projects_data: List) -> List[Project]:
        """Transform projects"""
        projects = []
        
        for proj_item in projects_data:
            if not isinstance(proj_item, dict):
                continue
            
            project = Project(
                name=proj_item.get('name', ''),
                description=proj_item.get('description', ''),
                technologies=proj_item.get('technologies', []),
                url=proj_item.get('url'),
                start_date=self._normalize_date(proj_item.get('start_date', '')),
                end_date=self._normalize_date(proj_item.get('end_date', '')),
                role=proj_item.get('role')
            )
            
            projects.append(project)
        
        return projects
    
    def _transform_languages(self, languages_data: List) -> List[Language]:
        """Transform languages"""
        languages = []
        
        for lang_item in languages_data:
            if isinstance(lang_item, str):
                language = Language(
                    language=lang_item,
                    proficiency='Unknown'
                )
            elif isinstance(lang_item, dict):
                language = Language(
                    language=lang_item.get('language', ''),
                    proficiency=lang_item.get('proficiency', 'Unknown')
                )
            else:
                continue
            
            languages.append(language)
        
        return languages
    
    def _categorize_skill(self, skill_name: str) -> SkillCategory:
        """Categorize a skill based on its name"""
        skill_lower = skill_name.lower()
        
        for category, keywords in self.skill_category_mapping.items():
            if skill_lower in keywords:
                return category
        
        return SkillCategory.OTHER
    
    def _determine_degree_level(self, degree: str) -> DegreeLevel:
        """Determine degree level from degree string"""
        degree_lower = degree.lower()
        
        for level, keywords in self.degree_level_mapping.items():
            for keyword in keywords:
                if keyword in degree_lower:
                    return level
        
        return DegreeLevel.OTHER
    
    def _normalize_email(self, email: Optional[str]) -> Optional[str]:
        """Normalize email address"""
        if not email:
            return None
        
        email = email.strip().lower()
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return email
        
        return None
    
    def _normalize_phone(self, phone: Optional[str]) -> Optional[str]:
        """Normalize phone number"""
        if not phone:
            return None
        
        # Remove common formatting characters
        phone = re.sub(r'[\s\-\(\)\.]', '', phone.strip())
        
        # Keep only digits and leading +
        phone = re.sub(r'[^\d+]', '', phone)
        
        return phone if phone else None
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string"""
        if not date_str:
            return ''
        
        date_str = str(date_str).strip()
        
        # Handle "Present"
        if 'present' in date_str.lower():
            return 'Present'
        
        # Extract year if present
        year_match = re.search(r'(19|20)\d{2}', date_str)
        if year_match:
            year = year_match.group(0)
            
            # Try to extract month
            month_match = re.search(
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*',
                date_str,
                re.IGNORECASE
            )
            
            if month_match:
                month = month_match.group(0)[:3].capitalize()
                return f"{month} {year}"
            
            return year
        
        return date_str
    
    def _build_skill_category_mapping(self) -> Dict[SkillCategory, List[str]]:
        """Build skill category mapping"""
        return {
            SkillCategory.PROGRAMMING: [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
                'php', 'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab'
            ],
            SkillCategory.WEB: [
                'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
                'express', 'next.js', 'nuxt', 'svelte', 'fastapi', 'asp.net', 'html',
                'css', 'sass', 'less', 'webpack', 'vite'
            ],
            SkillCategory.MOBILE: [
                'ios', 'android', 'react native', 'flutter', 'swift', 'kotlin',
                'objective-c', 'xamarin', 'ionic'
            ],
            SkillCategory.DATABASE: [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'cassandra', 'dynamodb', 'neo4j', 'sqlite'
            ],
            SkillCategory.CLOUD: [
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
                'terraform', 'cloudformation', 'openshift', 'heroku'
            ],
            SkillCategory.AI_ML: [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch',
                'scikit-learn', 'nlp', 'computer vision', 'keras', 'pandas', 'numpy'
            ],
            SkillCategory.TOOLS: [
                'git', 'jenkins', 'jira', 'agile', 'scrum', 'ci/cd', 'github',
                'gitlab', 'bitbucket', 'confluence', 'slack'
            ],
            SkillCategory.TESTING: [
                'junit', 'pytest', 'selenium', 'jest', 'mocha', 'cypress', 'testng',
                'unit testing', 'integration testing'
            ],
            SkillCategory.DEVOPS: [
                'linux', 'bash', 'ansible', 'puppet', 'chef', 'nginx', 'apache',
                'monitoring', 'logging'
            ]
        }
    
    def _build_degree_level_mapping(self) -> Dict[DegreeLevel, List[str]]:
        """Build degree level mapping"""
        return {
            DegreeLevel.PHD: ['phd', 'ph.d', 'doctorate', 'doctoral'],
            DegreeLevel.MASTERS: ['master', 'm.s', 'msc', 'm.sc', 'mba', 'm.b.a'],
            DegreeLevel.BACHELORS: ['bachelor', 'b.s', 'bsc', 'b.sc', 'b.a', 'ba', 'b.tech', 'b.e'],
            DegreeLevel.ASSOCIATE: ['associate', 'a.s', 'a.a'],
            DegreeLevel.DIPLOMA: ['diploma'],
            DegreeLevel.CERTIFICATE: ['certificate']
        }
    
    def to_dict(self, cv_schema: CVSchema) -> Dict[str, Any]:
        """
        Convert CVSchema to dictionary
        
        Args:
            cv_schema: CVSchema instance
            
        Returns:
            Dictionary representation
        """
        return cv_schema.to_dict()
    
    def to_json_compatible(self, cv_schema: CVSchema) -> Dict[str, Any]:
        """
        Convert CVSchema to JSON-compatible dictionary
        
        Args:
            cv_schema: CVSchema instance
            
        Returns:
            JSON-compatible dictionary
        """
        data = cv_schema.to_dict()
        
        # Ensure all values are JSON-serializable
        return self._make_json_compatible(data)
    
    def _make_json_compatible(self, obj: Any) -> Any:
        """Make object JSON-compatible"""
        if isinstance(obj, dict):
            return {key: self._make_json_compatible(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_compatible(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        else:
            return str(obj)
