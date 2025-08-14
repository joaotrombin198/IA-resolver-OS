from datetime import datetime
from typing import List, Dict, Optional

class Case:
    """Model for storing work order cases"""
    
    def __init__(self, problem_description: str, solution: str, 
                 system_type: str = "Unknown", case_id: Optional[int] = None):
        self.id = case_id
        self.problem_description = problem_description
        self.solution = solution
        self.system_type = system_type
        self.created_at = datetime.now()
        self.effectiveness_score: Optional[float] = None  # Will be set when feedback is provided
        self.feedback_count = 0
        self.tags: List[str] = []
        
    def to_dict(self) -> Dict:
        """Convert case to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'problem_description': self.problem_description,
            'solution': self.solution,
            'system_type': self.system_type,
            'created_at': self.created_at.isoformat(),
            'effectiveness_score': self.effectiveness_score,
            'feedback_count': self.feedback_count,
            'tags': self.tags
        }
    
    def add_feedback(self, effectiveness: int):
        """Add effectiveness feedback (1-5 scale)"""
        if self.effectiveness_score is None:
            self.effectiveness_score = effectiveness
        else:
            # Calculate running average
            total_score = self.effectiveness_score * self.feedback_count + effectiveness
            self.effectiveness_score = total_score / (self.feedback_count + 1)
        
        self.feedback_count += 1

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
