"""
Quick feedback route for ML analysis suggestions
Separate file for better organization of analysis-specific feedback
"""

from flask import request, jsonify
from app import app, db
from models import AnalysisFeedback
import json
import logging
from datetime import datetime

@app.route('/api/rate-suggestion', methods=['POST'])
def rate_suggestion():
    """Quick rating endpoint for individual suggestions"""
    try:
        data = request.get_json()
        
        suggestion_index = data.get('suggestion_index')
        rating = data.get('rating')  # 'helpful' or 'not_helpful'
        problem_description = data.get('problem_description', '')
        detected_system = data.get('detected_system', '')
        
        if suggestion_index is None or not rating:
            return jsonify({
                'success': False,
                'message': 'Índice da sugestão e avaliação são obrigatórios'
            }), 400
        
        if rating not in ['helpful', 'not_helpful']:
            return jsonify({
                'success': False,
                'message': 'Avaliação deve ser "helpful" ou "not_helpful"'
            }), 400
        
        # Create suggestion ratings object
        suggestion_ratings = {str(suggestion_index): rating}
        
        # Determine overall score based on rating
        overall_score = 5 if rating == 'helpful' else 1
        
        # Create new analysis feedback record
        feedback = AnalysisFeedback()
        feedback.problem_description = problem_description[:500]  # Limit length
        feedback.overall_score = overall_score
        feedback.suggestion_ratings = json.dumps(suggestion_ratings)
        feedback.detected_system = detected_system
        feedback.good_aspects = json.dumps(['relevant'] if rating == 'helpful' else [])
        feedback.improvements = json.dumps([] if rating == 'helpful' else ['accuracy'])
        feedback.comments = f"Quick rating: {rating} for suggestion {suggestion_index}"
        feedback.created_at = datetime.now()
        
        db.session.add(feedback)
        db.session.commit()
        
        # Process feedback for ML learning
        from ml_service import MLService
        ml_service = MLService()
        ml_service.process_analysis_feedback(feedback)
        
        logging.info(f"Quick feedback: suggestion {suggestion_index} rated as {rating}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback registrado com sucesso!',
            'rating': rating,
            'suggestion_index': suggestion_index
        })
        
    except Exception as e:
        logging.error(f"Error in rate_suggestion: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500