from app import db
from datetime import datetime
from typing import List, Dict, Optional
from flask_sqlalchemy import SQLAlchemy


class Case(db.Model):
    """Model for storing work order cases"""
    
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    problem_description = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    system_type = db.Column(db.String(100), default="Unknown")
    created_at = db.Column(db.DateTime, default=datetime.now)
    effectiveness_score = db.Column(db.Float, nullable=True)
    feedback_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(500), default="")  # Stored as comma-separated string
    
    # Relationship to feedback entries
    feedbacks = db.relationship("CaseFeedback", backref="case", cascade="all, delete-orphan")
    
    def get_tags_list(self) -> List[str]:
        """Get tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []
    
    def set_tags_list(self, tags: List[str]):
        """Set tags from a list"""
        self.tags = ','.join(tags) if tags else ""
        
    def to_dict(self) -> Dict:
        """Convert case to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'problem_description': self.problem_description,
            'solution': self.solution,
            'system_type': self.system_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'effectiveness_score': self.effectiveness_score,
            'feedback_count': self.feedback_count,
            'tags': self.get_tags_list()
        }
    
    def add_feedback(self, effectiveness: int, resolution_method: str = "", 
                    custom_solution: str = ""):
        """Add effectiveness feedback (1-5 scale)"""
        if self.effectiveness_score is None:
            self.effectiveness_score = effectiveness
        else:
            # Calculate running average
            total_score = self.effectiveness_score * self.feedback_count + effectiveness
            self.effectiveness_score = total_score / (self.feedback_count + 1)
        
        self.feedback_count += 1
        
        # Create feedback record
        feedback = CaseFeedback()
        feedback.case_id = self.id
        feedback.effectiveness_score = effectiveness
        feedback.resolution_method = resolution_method
        feedback.custom_solution = custom_solution
        db.session.add(feedback)
        db.session.commit()


class CaseFeedback(db.Model):
    """Model for storing detailed feedback on case resolutions"""
    
    __tablename__ = 'case_feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    effectiveness_score = db.Column(db.Integer, nullable=False)  # 1-5 scale
    resolution_method = db.Column(db.String(50), default="")  # "first_suggestion", "custom", "not_resolved"
    custom_solution = db.Column(db.Text, default="")  # What actually worked
    created_at = db.Column(db.DateTime, default=datetime.now)


class AnalysisFeedback(db.Model):
    """Model for storing feedback on AI analysis and suggestions"""
    
    __tablename__ = 'analysis_feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    problem_description = db.Column(db.Text, nullable=False)  # The analyzed problem
    overall_score = db.Column(db.Integer, nullable=False)  # 1-5 scale
    suggestion_ratings = db.Column(db.Text, default="{}")  # JSON: {"0": "helpful", "1": "not_helpful"}
    good_aspects = db.Column(db.Text, default="[]")  # JSON: ["relevant", "clear"]
    improvements = db.Column(db.Text, default="[]")  # JSON: ["speed", "detail"]
    comments = db.Column(db.Text, default="")
    detected_system = db.Column(db.String(100), default="")  # What system was detected
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert analysis feedback to dictionary"""
        import json
        return {
            'id': self.id,
            'problem_description': self.problem_description,
            'overall_score': self.overall_score,
            'suggestion_ratings': json.loads(self.suggestion_ratings or "{}"),
            'good_aspects': json.loads(self.good_aspects or "[]"),
            'improvements': json.loads(self.improvements or "[]"),
            'comments': self.comments,
            'detected_system': self.detected_system,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        """Convert feedback to dictionary"""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'effectiveness_score': self.effectiveness_score,
            'resolution_method': self.resolution_method,
            'custom_solution': self.custom_solution,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SolutionSuggestion:
    """Model for ML-generated solution suggestions"""
    
    def __init__(self, problem_description: str, suggested_solutions: List[str],
                 confidence: float, system_type: str, similar_cases: Optional[List[Case]] = None):
        self.problem_description = problem_description
        self.suggested_solutions = suggested_solutions
        self.confidence = confidence
        self.system_type = system_type
        self.similar_cases = similar_cases or []
        self.generated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert suggestion to dictionary"""
        return {
            'problem_description': self.problem_description,
            'suggested_solutions': self.suggested_solutions,
            'confidence': self.confidence,
            'system_type': self.system_type,
            'similar_cases': [case.to_dict() for case in self.similar_cases],
            'generated_at': self.generated_at.isoformat()
        }