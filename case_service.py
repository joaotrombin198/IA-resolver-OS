import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from flask import current_app
from models import Case
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class CaseService:
    """Service for managing cases and performing similarity searches"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self._fitted = False
    
    def get_all_cases(self) -> List[Case]:
        """Get all cases from storage"""
        return current_app.config.get('CASES_STORAGE', [])
    
    def get_case_by_id(self, case_id: int) -> Optional[Case]:
        """Get a specific case by ID"""
        cases = self.get_all_cases()
        for case in cases:
            if case.id == case_id:
                return case
        return None
    
    def add_case(self, problem_description: str, solution: str, system_type: str = "Unknown") -> Case:
        """Add a new case to the knowledge base"""
        try:
            # Get next ID
            next_id = current_app.config.get('NEXT_CASE_ID', 1)
            current_app.config['NEXT_CASE_ID'] = next_id + 1
            
            # Create new case
            case = Case(
                problem_description=problem_description,
                solution=solution,
                system_type=system_type,
                case_id=next_id
            )
            
            # Add to storage
            cases = current_app.config.get('CASES_STORAGE', [])
            cases.append(case)
            current_app.config['CASES_STORAGE'] = cases
            
            # Refit vectorizer when new cases are added
            self._fitted = False
            
            logging.info(f"Added new case #{case.id}")
            return case
            
        except Exception as e:
            logging.error(f"Error adding case: {str(e)}")
            raise
    
    def update_case(self, case_id: int, problem_description: str, solution: str, system_type: str) -> bool:
        """Update an existing case"""
        try:
            cases = self.get_all_cases()
            for case in cases:
                if case.id == case_id:
                    case.problem_description = problem_description
                    case.solution = solution
                    case.system_type = system_type
                    
                    # Update storage
                    current_app.config['CASES_STORAGE'] = cases
                    
                    # Refit vectorizer when cases are updated
                    self._fitted = False
                    
                    logging.info(f"Updated case #{case_id}")
                    return True
            
            return False  # Case not found
            
        except Exception as e:
            logging.error(f"Error updating case {case_id}: {str(e)}")
            raise
    
    def delete_case(self, case_id: int) -> bool:
        """Delete a case from the knowledge base"""
        try:
            cases = self.get_all_cases()
            original_count = len(cases)
            
            # Filter out the case to delete
            updated_cases = [case for case in cases if case.id != case_id]
            
            if len(updated_cases) < original_count:
                current_app.config['CASES_STORAGE'] = updated_cases
                
                # Refit vectorizer when cases are deleted
                self._fitted = False
                
                logging.info(f"Deleted case #{case_id}")
                return True
            
            return False  # Case not found
            
        except Exception as e:
            logging.error(f"Error deleting case {case_id}: {str(e)}")
            raise
    
    def find_similar_cases(self, problem_description: str, limit: int = 5) -> List[Case]:
        """Find cases similar to the given problem description"""
        try:
            cases = self.get_all_cases()
            
            if not cases:
                return []
            
            # Prepare text corpus
            case_descriptions = [case.problem_description for case in cases]
            all_descriptions = case_descriptions + [problem_description]
            
            # Fit or refit vectorizer if needed
            if not self._fitted or len(case_descriptions) > 0:
                try:
                    tfidf_matrix = self.vectorizer.fit_transform(all_descriptions)
                    self._fitted = True
                except Exception as e:
                    logging.error(f"Error fitting vectorizer: {str(e)}")
                    return []
            else:
                return []
            
            # Calculate similarities
            query_vector = tfidf_matrix[-1]  # Last item is the query
            case_vectors = tfidf_matrix[:-1]  # All except the last
            
            similarities = cosine_similarity(query_vector, case_vectors).flatten()
            
            # Get top similar cases
            similar_indices = np.argsort(similarities)[::-1][:limit]
            similar_cases = []
            
            for idx in similar_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    similar_cases.append(cases[idx])
            
            return similar_cases
            
        except Exception as e:
            logging.error(f"Error finding similar cases: {str(e)}")
            return []
    
    def search_cases(self, query: str, system_filter: str = "") -> List[Case]:
        """Search cases by query and optional system filter"""
        try:
            cases = self.get_all_cases()
            
            if not query and not system_filter:
                return cases
            
            filtered_cases = []
            
            for case in cases:
                # Apply system filter
                if system_filter and case.system_type.lower() != system_filter.lower():
                    continue
                
                # Apply text search
                if query:
                    query_lower = query.lower()
                    if (query_lower in case.problem_description.lower() or 
                        query_lower in case.solution.lower()):
                        filtered_cases.append(case)
                else:
                    filtered_cases.append(case)
            
            return filtered_cases
            
        except Exception as e:
            logging.error(f"Error searching cases: {str(e)}")
            return []
    
    def get_recent_cases(self, limit: int = 10) -> List[Case]:
        """Get most recently added cases"""
        try:
            cases = self.get_all_cases()
            # Sort by creation date (most recent first)
            sorted_cases = sorted(cases, key=lambda x: x.created_at, reverse=True)
            return sorted_cases[:limit]
            
        except Exception as e:
            logging.error(f"Error getting recent cases: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        try:
            cases = self.get_all_cases()
            
            if not cases:
                return {
                    'total_cases': 0,
                    'systems': {},
                    'avg_effectiveness': 0,
                    'cases_with_feedback': 0,
                    'recent_activity': 0
                }
            
            # Count by system type
            systems = {}
            total_effectiveness = 0
            cases_with_feedback = 0
            recent_cases = 0
            
            week_ago = datetime.now() - timedelta(days=7)
            
            for case in cases:
                # System type counts
                systems[case.system_type] = systems.get(case.system_type, 0) + 1
                
                # Effectiveness tracking
                if case.effectiveness_score is not None:
                    total_effectiveness += case.effectiveness_score
                    cases_with_feedback += 1
                
                # Recent activity
                if case.created_at > week_ago:
                    recent_cases += 1
            
            avg_effectiveness = (total_effectiveness / cases_with_feedback) if cases_with_feedback > 0 else 0
            
            return {
                'total_cases': len(cases),
                'systems': systems,
                'avg_effectiveness': round(avg_effectiveness, 2),
                'cases_with_feedback': cases_with_feedback,
                'recent_activity': recent_cases
            }
            
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {
                'total_cases': 0,
                'systems': {},
                'avg_effectiveness': 0,
                'cases_with_feedback': 0,
                'recent_activity': 0
            }
    
    def get_unique_systems(self) -> List[str]:
        """Get list of unique system types"""
        try:
            cases = self.get_all_cases()
            systems = set(case.system_type for case in cases)
            return sorted(list(systems))
            
        except Exception as e:
            logging.error(f"Error getting unique systems: {str(e)}")
            return []
    
    def add_feedback(self, case_id: int, effectiveness: int) -> bool:
        """Add effectiveness feedback to a case"""
        try:
            case = self.get_case_by_id(case_id)
            if case:
                case.add_feedback(effectiveness)
                logging.info(f"Added feedback to case #{case_id}: {effectiveness}")
                return True
            return False
            
        except Exception as e:
            logging.error(f"Error adding feedback: {str(e)}")
            return False
