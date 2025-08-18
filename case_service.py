import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from flask import current_app
from models import Case, CaseFeedback
from app import db
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class CaseService:
    """Service for managing cases and performing similarity searches"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self._fitted = False
    
    def get_all_cases(self) -> List[Case]:
        """Get all cases from database with fallback"""
        try:
            return Case.query.all()
        except Exception as e:
            logging.error(f"Error getting cases from database: {str(e)}")
            # Fallback to in-memory storage
            return current_app.config.get('CASES_STORAGE', [])
    
    def get_case_by_id(self, case_id: int) -> Optional[Case]:
        """Get a specific case by ID from PostgreSQL"""
        try:
            return Case.query.get(case_id)
        except Exception as e:
            logging.error(f"Error getting case {case_id} from database: {str(e)}")
            # Fallback to in-memory storage
            cases = current_app.config.get('CASES_STORAGE', [])
            for case in cases:
                if case.id == case_id:
                    return case
            return None
    
    def add_case(self, problem_description: str, solution: str, system_type: str = "Unknown") -> Optional[Case]:
        """Add a new case to the database with robust error handling"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Create new case
                case = Case()
                case.problem_description = problem_description
                case.solution = solution
                case.system_type = system_type
                
                # Add to database
                db.session.add(case)
                db.session.commit()
                
                # Refit vectorizer when new cases are added
                self._fitted = False
                
                logging.info(f"Added new case #{case.id} to database")
                return case
                
            except Exception as e:
                retry_count += 1
                try:
                    db.session.rollback()
                except:
                    pass
                    
                if retry_count < max_retries:
                    logging.warning(f"Database error on attempt {retry_count}, retrying: {str(e)}")
                    continue
                else:
                    logging.error(f"Failed to add case to database after {max_retries} attempts: {str(e)}")
                    return None
    
    def update_case(self, case_id: int, problem_description: str, solution: str, system_type: str) -> bool:
        """Update an existing case in PostgreSQL"""
        try:
            case = Case.query.get(case_id)
            if case:
                case.problem_description = problem_description
                case.solution = solution
                case.system_type = system_type
                
                db.session.commit()
                
                # Refit vectorizer when cases are updated
                self._fitted = False
                
                logging.info(f"Updated case #{case_id} in database")
                return True
            
            return False  # Case not found
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating case {case_id} in database: {str(e)}")
            return False
    
    def delete_case(self, case_id: int) -> bool:
        """Delete a case from PostgreSQL database"""
        try:
            case = Case.query.get(case_id)
            if case:
                db.session.delete(case)
                db.session.commit()
                
                # Refit vectorizer when cases are deleted
                self._fitted = False
                
                logging.info(f"Deleted case #{case_id} from database")
                return True
            
            return False  # Case not found
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting case {case_id} from database: {str(e)}")
            return False
            
    def add_case_feedback(self, case_id: int, effectiveness_score: int, 
                         resolution_method: str = "", custom_solution: str = "") -> bool:
        """Add feedback to a case"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return False
                
            # Add feedback using the model method
            case.add_feedback(effectiveness_score, resolution_method, custom_solution)
            db.session.commit()
            
            logging.info(f"Added feedback to case #{case_id}: {resolution_method} (score: {effectiveness_score})")
            return True
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding feedback to case {case_id}: {str(e)}")
            return False
    
    def get_case_feedbacks(self, case_id: int) -> List[CaseFeedback]:
        """Get all feedback for a specific case"""
        try:
            return CaseFeedback.query.filter_by(case_id=case_id).order_by(CaseFeedback.created_at.desc()).all()
        except Exception as e:
            logging.error(f"Error getting feedbacks for case {case_id}: {str(e)}")
            return []
    
    def find_similar_cases(self, problem_description: str, limit: int = 5) -> List[Case]:
        """Find cases similar to the given problem description using enhanced semantic matching"""
        try:
            cases = self.get_all_cases()
            
            if not cases:
                return []
            
            # Use ML service for enhanced semantic similarity
            from ml_service import MLService
            ml_service = MLService()
            
            # Prepare text corpus with semantic preprocessing
            case_descriptions = [case.problem_description for case in cases]
            all_descriptions = case_descriptions + [problem_description]
            
            # Use semantic vectorizer for better matching
            try:
                semantic_matrix = ml_service.semantic_vectorizer.fit_transform(all_descriptions)
                self._fitted = True
            except Exception as e:
                logging.error(f"Error with semantic vectorizer: {str(e)}")
                # Fallback to standard vectorizer
                try:
                    semantic_matrix = self.vectorizer.fit_transform(all_descriptions)
                    self._fitted = True
                except Exception as e2:
                    logging.error(f"Error fitting fallback vectorizer: {str(e2)}")
                    return []
            
            # Calculate semantic similarities
            query_vector = semantic_matrix[-1]  # Last item is the query
            case_vectors = semantic_matrix[:-1]  # All except the last
            
            similarities = cosine_similarity(query_vector, case_vectors).flatten()
            
            # Enhanced similarity scoring with semantic boost
            enhanced_similarities = []
            query_normalized = ml_service._preprocess_text(problem_description)
            query_tokens = set(ml_service._semantic_tokenizer(query_normalized))
            
            for idx, case in enumerate(cases):
                base_similarity = similarities[idx]
                
                # Calculate semantic boost
                case_normalized = ml_service._preprocess_text(case.problem_description)
                case_tokens = set(ml_service._semantic_tokenizer(case_normalized))
                
                # Boost for semantic equivalents
                semantic_boost = 0.0
                for token in query_tokens:
                    if token in ml_service.semantic_equivalents:
                        for equiv in ml_service.semantic_equivalents[token]:
                            if equiv in case_tokens:
                                semantic_boost += 0.1
                
                # Boost for system type match
                system_boost = 0.0
                detected_system = ml_service._detect_system_type(problem_description)
                if detected_system == case.system_type:
                    system_boost = 0.2
                
                enhanced_similarity = base_similarity + semantic_boost + system_boost
                enhanced_similarities.append((idx, enhanced_similarity))
            
            # Sort by enhanced similarity
            enhanced_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top similar cases with minimum threshold
            similar_cases = []
            for idx, similarity in enhanced_similarities[:limit]:
                if similarity > 0.05:  # Lower threshold due to enhanced scoring
                    similar_cases.append(cases[idx])
            
            return similar_cases
            
        except Exception as e:
            logging.error(f"Error finding similar cases: {str(e)}")
            return []
    
    def search_cases(self, query: str, system_filter: str = "") -> List[Case]:
        """Enhanced semantic search with aggressive accent normalization and fuzzy matching"""
        try:
            cases = self.get_all_cases()
            
            if not query and not system_filter:
                return cases
            
            # Use ML service for enhanced search
            from ml_service import MLService
            ml_service = MLService()
            
            filtered_cases = []
            
            if query:
                # Advanced query preprocessing
                query_normalized = ml_service._preprocess_text(query)
                query_tokens = set(ml_service._semantic_tokenizer(query_normalized))
                
                # Create expanded search terms with variations
                expanded_query_tokens = query_tokens.copy()
                for token in query_tokens:
                    if token in ml_service.semantic_equivalents:
                        expanded_query_tokens.update(ml_service.semantic_equivalents[token][:5])
                    
                    # Add common variations for Portuguese
                    if len(token) > 3:
                        # Add plural/singular variations
                        if token.endswith('s'):
                            expanded_query_tokens.add(token[:-1])  # Remove 's'
                        else:
                            expanded_query_tokens.add(token + 's')  # Add 's'
                        
                        # Add verb variations
                        if token.endswith('ar'):
                            expanded_query_tokens.add(token[:-2] + 'ou')  # -ar to -ou
                            expanded_query_tokens.add(token[:-2] + 'ando')  # -ar to -ando
                
                for case in cases:
                    # Apply system filter first
                    if system_filter and case.system_type.lower() != system_filter.lower():
                        continue
                    
                    # Enhanced semantic matching with fuzzy logic
                    case_description_norm = ml_service._preprocess_text(case.problem_description)
                    case_solution_norm = ml_service._preprocess_text(case.solution)
                    
                    case_desc_tokens = set(ml_service._semantic_tokenizer(case_description_norm))
                    case_sol_tokens = set(ml_service._semantic_tokenizer(case_solution_norm))
                    case_all_tokens = case_desc_tokens.union(case_sol_tokens)
                    
                    # Calculate enhanced match score
                    match_score = 0.0
                    
                    # Direct token matches (highest weight)
                    direct_matches = len(query_tokens.intersection(case_all_tokens))
                    match_score += direct_matches * 5.0
                    
                    # Semantic equivalent matches (high weight)
                    semantic_matches = len(expanded_query_tokens.intersection(case_all_tokens))
                    match_score += semantic_matches * 2.0
                    
                    # Fuzzy substring matching (medium weight)
                    for query_token in query_tokens:
                        if len(query_token) > 3:
                            for case_token in case_all_tokens:
                                if len(case_token) > 3:
                                    # Check if tokens are similar (levenshtein-like)
                                    if (query_token in case_token or case_token in query_token or
                                        self._tokens_similar(query_token, case_token)):
                                        match_score += 1.0
                    
                    # Raw text substring matching (lower weight but important for phrases)
                    query_parts = query_normalized.split()
                    case_full_text = (case_description_norm + ' ' + case_solution_norm).lower()
                    for part in query_parts:
                        if len(part) > 2 and part in case_full_text:
                            match_score += 0.8
                    
                    # Include case if there's any meaningful match (lowered threshold)
                    if match_score > 0.5:
                        filtered_cases.append((case, match_score))
                
                # Sort by match score (highest first)
                filtered_cases.sort(key=lambda x: x[1], reverse=True)
                filtered_cases = [case for case, score in filtered_cases]
                
            else:
                # Only system filter, no text query
                for case in cases:
                    if system_filter and case.system_type.lower() != system_filter.lower():
                        continue
                    filtered_cases.append(case)
            
            return filtered_cases
            
        except Exception as e:
            logging.error(f"Error in enhanced search: {str(e)}")
            # Fallback to simple search
            return self._simple_search_fallback(query, system_filter, cases)
    
    def _tokens_similar(self, token1: str, token2: str) -> bool:
        """Check if two tokens are similar using simple fuzzy logic"""
        if len(token1) < 3 or len(token2) < 3:
            return False
        
        # Check if one token is contained in another with some flexibility
        longer = max(token1, token2, key=len)
        shorter = min(token1, token2, key=len)
        
        if len(shorter) / len(longer) < 0.6:  # Too different in length
            return False
        
        # Simple similarity check
        common_chars = sum(1 for i, char in enumerate(shorter) 
                          if i < len(longer) and char == longer[i])
        
        return common_chars / len(shorter) > 0.7
    
    def _simple_search_fallback(self, query: str, system_filter: str, cases: List[Case]) -> List[Case]:
        """Fallback simple search if enhanced search fails"""
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
                    'systems': [],
                    'systems_dict': {},
                    'avg_effectiveness': 0,
                    'cases_with_feedback': 0,
                    'total_feedback': 0,
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
            
            # Convert systems dict to sorted list for template
            systems_list = sorted(systems.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'total_cases': len(cases),
                'systems': systems_list,
                'systems_dict': systems,
                'avg_effectiveness': round(avg_effectiveness, 2),
                'cases_with_feedback': cases_with_feedback,
                'total_feedback': cases_with_feedback,
                'recent_activity': recent_cases
            }
            
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {
                'total_cases': 0,
                'systems': [],
                'systems_dict': {},
                'avg_effectiveness': 0,
                'cases_with_feedback': 0,
                'total_feedback': 0,
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
    
    def delete_all_cases(self) -> int:
        """Delete ALL cases from the database - DESTRUCTIVE OPERATION"""
        try:
            cases = self.get_all_cases()
            if not cases:
                return 0
            
            deleted_count = 0
            
            # Try to delete from database first
            try:
                deleted_count = Case.query.count()
                Case.query.delete()
                db.session.commit()
                
                # Reset vectorizer since all data is gone
                self._fitted = False
                
                logging.warning(f"BULK DELETE: Removed {deleted_count} cases from database")
                
            except Exception as db_error:
                logging.error(f"Database bulk delete failed: {str(db_error)}")
                try:
                    db.session.rollback()
                except:
                    pass
                
                # Fallback: clear in-memory storage
                current_app.config['CASES_STORAGE'] = []
                current_app.config['NEXT_CASE_ID'] = 1
                deleted_count = len(cases)
                logging.warning(f"Fallback: Cleared {deleted_count} cases from memory")
            
            return deleted_count
            
        except Exception as e:
            logging.error(f"Critical error in bulk delete: {str(e)}")
            return 0
