import os
import pickle
import logging
import re
import unicodedata
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from models import SolutionSuggestion, Case

class MLService:
    """Machine Learning service for problem analysis and solution suggestions"""
    
    def __init__(self):
        self.system_classifier = None
        self.solution_generator = None
        
        # Initialize vectorizers without custom methods first
        self.vectorizer = None
        self.semantic_vectorizer = None
        
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
        # Multilingual stop words
        self.stop_words = {
            'portuguese': {'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das', 
                          'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
                          'e', 'ou', 'mas', 'que', 'se', 'quando', 'onde', 'como', 'porque', 'pois',
                          'ser', 'estar', 'ter', 'haver', 'fazer', 'ir', 'vir', 'dar', 'ver', 'dizer',
                          'muito', 'mais', 'menos', 'bem', 'mal', 'só', 'também', 'já', 'ainda', 'sempre'},
            'english': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                       'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
                       'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those',
                       'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                       'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must'}
        }
        
        # Enhanced semantic equivalents for better matching
        self.semantic_equivalents = {
            # Password related terms - expanded
            'senha': ['password', 'pass', 'pwd', 'login', 'credencial', 'acesso', 'autenticacao', 'logon', 'autenticar'],
            'password': ['senha', 'pass', 'pwd', 'login', 'credencial', 'acesso', 'autenticacao', 'logon', 'autenticar'],
            'recuperar': ['recover', 'reset', 'resetar', 'restaurar', 'redefinir', 'resgatar', 'recuperacao'],
            'esqueci': ['forgot', 'perdeu', 'perdi', 'esqueceu', 'nao lembro', 'nao sei'],
            'expirada': ['expired', 'vencida', 'bloqueada', 'blocked', 'invalid', 'invalida', 'venceu'],
            'expiry': ['expiracao', 'vencimento', 'validade'],
            'bloqueado': ['blocked', 'travado', 'locked', 'impedido', 'restrito'],
            'acesso': ['access', 'login', 'entrada', 'logon', 'conectar', 'acessar'],
            
            # Network terms
            'rede': ['network', 'net', 'conectividade', 'conexao', 'connection'],
            'network': ['rede', 'net', 'conectividade', 'conexao', 'connection'],
            'internet': ['web', 'online', 'conectividade'],
            'wifi': ['wireless', 'sem fio', 'wi-fi'],
            
            # System terms
            'sistema': ['system', 'aplicacao', 'application', 'app', 'software'],
            'system': ['sistema', 'aplicacao', 'application', 'app', 'software'],
            'erro': ['error', 'falha', 'failure', 'problema', 'problem', 'issue'],
            'error': ['erro', 'falha', 'failure', 'problema', 'problem', 'issue'],
            'lento': ['slow', 'devagar', 'performance', 'lag', 'delay'],
            'slow': ['lento', 'devagar', 'performance', 'lag', 'delay'],
            
            # Actions
            'reiniciar': ['restart', 'reboot', 'reset', 'resetar'],
            'restart': ['reiniciar', 'reboot', 'reset', 'resetar'],
            'instalar': ['install', 'setup', 'configurar', 'configure'],
            'install': ['instalar', 'setup', 'configurar', 'configure'],
            'atualizar': ['update', 'upgrade', 'refresh', 'sync'],
            'update': ['atualizar', 'upgrade', 'refresh', 'sync'],
            
            # Medical/Hospital terms
            'paciente': ['patient', 'cliente', 'user', 'usuario'],
            'medico': ['doctor', 'physician', 'clinician'],
            'consulta': ['appointment', 'visit', 'session'],
            'exame': ['exam', 'test', 'procedure', 'procedimento'],
            'prontuario': ['record', 'chart', 'file', 'history']
        }
        
        # Enhanced system keywords with semantic variations
        self.system_keywords = {
            'Tasy': ['tasy', 'hospitalar', 'hospital', 'prontuario', 'paciente', 'atendimento', 'medico',
                    'record', 'patient', 'medical', 'clinical', 'clinico', 'internacao', 'alta',
                    'prescricao', 'prescription', 'medication', 'medicamento'],
            'SGU': ['sgu', 'sistema gestao', 'gestao hospitalar', 'modulo sgu', 'management system',
                   'hospital management', 'sgu suite', 'suite sgu', 'gestao', 'management'],
            'SGU Card': ['sgu card', 'cartao', 'card', 'credenciamento', 'carteirinha', 'credential',
                        'badge', 'identification', 'id card', 'access card', 'cartao acesso'],
            'Autorizador': ['autorizador', 'autorizacao', 'autorizar', 'procedimento', 'guia',
                           'authorization', 'authorize', 'procedure', 'guide', 'approval',
                           'aprovacao', 'liberacao', 'release'],
            'AutSC': ['autsc', 'aut sc', 'autorizador sc', 'santa catarina', 'sc authorization'],
            'Contábil': ['contabil', 'accounting', 'financeiro', 'financial', 'contabilidade',
                        'fiscal', 'tax', 'imposto', 'lancamento', 'entry'],
            'ERP': ['erp', 'enterprise resource', 'gestao empresarial', 'business management',
                   'sistema integrado', 'integrated system'],
            'Exchange Online': ['exchange', 'email', 'outlook', 'mail', 'correio', 'office365',
                               'o365', 'microsoft exchange', 'webmail'],
            'Hardware': ['hardware', 'computador', 'computer', 'pc', 'notebook', 'laptop',
                        'impressora', 'printer', 'monitor', 'teclado', 'keyboard', 'mouse'],
            'Portal Interno': ['portal interno', 'internal portal', 'intranet', 'portal corporativo',
                              'corporate portal', 'employee portal', 'funcionario'],
            'Rede SMB': ['rede smb', 'smb network', 'file sharing', 'compartilhamento arquivo',
                        'shared folder', 'pasta compartilhada', 'network drive'],
            'SGUSuite': ['sgu suite', 'sgusuite', 'suite sgu', 'sgu sistema completo'],
            'VPN FortiClient': ['vpn', 'forticlient', 'forti client', 'remote access', 'acesso remoto',
                               'conexao remota', 'remote connection', 'trabalho remoto'],
            'Healthcare': ['saude', 'health', 'emr', 'ehr', 'clinico', 'diagnostico', 'exame',
                          'clinical', 'diagnosis', 'exam', 'teste', 'laboratorio', 'lab'],
            'Administrative': ['administrativo', 'admin', 'rh', 'financeiro', 'contabil', 'gestao',
                              'human resources', 'hr', 'payroll', 'folha pagamento'],
            'Network': ['rede', 'network', 'router', 'switch', 'firewall', 'ip', 'dns', 'dhcp',
                       'conectividade', 'connectivity', 'internet', 'wifi', 'wireless'],
            'Database': ['banco', 'database', 'sql', 'mysql', 'postgres', 'oracle', 'mongodb',
                        'dados', 'data', 'base dados', 'bd', 'db'],
            'Application Server': ['servidor', 'server', 'apache', 'nginx', 'tomcat', 'iis', 'aplicacao',
                                  'application', 'app server', 'web server', 'servico', 'service']
        }
        
        # Common solutions patterns
        self.solution_patterns = {
            'restart': ['Reiniciar o serviço', 'Verificar se o processo está rodando', 'Realizar restart do sistema'],
            'permissions': ['Verificar permissões de usuário', 'Checar grupos de acesso', 'Validar credenciais'],
            'network': ['Testar conectividade de rede', 'Verificar configurações de firewall', 'Validar DNS'],
            'database': ['Verificar conexão com banco de dados', 'Checar logs do banco', 'Validar consultas SQL'],
            'memory': ['Verificar uso de memória', 'Limpar cache', 'Reiniciar serviços que consomem muita RAM'],
            'disk': ['Verificar espaço em disco', 'Limpar arquivos temporários', 'Mover arquivos grandes']
        }
        
        # Initialize vectorizers after methods are defined
        self._initialize_vectorizers()
        
        # Load trained models if they exist
        self._load_models()
    
    def _initialize_vectorizers(self):
        """Initialize vectorizers after methods are defined"""
        # Enhanced vectorizer with multilingual support
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 3),  # Unigrams, bigrams, and trigrams
            min_df=1,
            max_df=0.95,
            analyzer='word',
            lowercase=True,
            stop_words=None,  # We'll handle stop words ourselves
            preprocessor=self._preprocess_text,
            tokenizer=self._enhanced_tokenizer
        )
        
        # Enhanced semantic vectorizer for similarity matching
        self.semantic_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 4),
            min_df=1,
            max_df=0.9,
            analyzer='word',
            lowercase=True,
            preprocessor=self._semantic_preprocess,
            tokenizer=self._semantic_tokenizer
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Enhanced text preprocessing with aggressive normalization"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents and normalize unicode more aggressively
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Enhanced accent handling - specific Portuguese replacements
        accent_map = {
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        for accented, plain in accent_map.items():
            text = text.replace(accented, plain)
        
        # Normalize common contractions and abbreviations
        contractions = {
            'nao': 'não', 'pq': 'porque', 'vc': 'voce', 'tb': 'tambem',
            'q': 'que', 'eh': 'e', 'soh': 'so', 'td': 'tudo'
        }
        for short, full in contractions.items():
            text = text.replace(short, full)
        
        # Remove punctuation but keep meaningful characters
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _enhanced_tokenizer(self, text: str) -> List[str]:
        """Enhanced tokenizer with semantic expansion"""
        if not text:
            return []
        
        # Basic tokenization
        tokens = text.split()
        
        # Filter out stop words
        filtered_tokens = []
        for token in tokens:
            if token not in self.stop_words['portuguese'] and token not in self.stop_words['english']:
                if len(token) > 1:  # Keep tokens with more than 1 character
                    filtered_tokens.append(token)
        
        # Add semantic equivalents
        expanded_tokens = filtered_tokens.copy()
        for token in filtered_tokens:
            if token in self.semantic_equivalents:
                expanded_tokens.extend(self.semantic_equivalents[token][:3])  # Add top 3 equivalents
        
        return expanded_tokens
    
    def _semantic_preprocess(self, text: str) -> str:
        """Semantic preprocessing for similarity matching"""
        if not text:
            return ""
        
        # Basic preprocessing
        text = self._preprocess_text(text)
        
        # Expand with semantic equivalents
        words = text.split()
        expanded_words = []
        
        for word in words:
            expanded_words.append(word)
            if word in self.semantic_equivalents:
                # Add semantic equivalents with lower weight
                for equiv in self.semantic_equivalents[word][:2]:
                    expanded_words.append(equiv)
        
        return ' '.join(expanded_words)
    
    def _semantic_tokenizer(self, text: str) -> List[str]:
        """Semantic tokenizer for enhanced similarity matching"""
        if not text:
            return []
        
        tokens = text.split()
        
        # Remove stop words and short tokens
        meaningful_tokens = []
        for token in tokens:
            if (token not in self.stop_words['portuguese'] and 
                token not in self.stop_words['english'] and 
                len(token) > 2):
                meaningful_tokens.append(token)
        
        return meaningful_tokens
    
    def analyze_problem(self, problem_description: str, similar_cases: list = None) -> SolutionSuggestion:
        """Analyze problem description and provide ML-based suggestions with priority for similar cases"""
        try:
            # Detect system type
            system_type = self._detect_system_type(problem_description)
            
            # Generate solution suggestions with similar cases priority
            suggestions = self._generate_solutions_with_similar_cases(problem_description, system_type, similar_cases)
            
            # Calculate confidence
            confidence = self._calculate_confidence(problem_description, system_type, suggestions)
            
            return SolutionSuggestion(
                problem_description=problem_description,
                suggested_solutions=suggestions,
                confidence=confidence,
                system_type=system_type
            )
            
        except Exception as e:
            logging.error(f"Error in ML analysis: {str(e)}")
            return SolutionSuggestion(
                problem_description=problem_description,
                suggested_solutions=["Erro na análise ML. Consulte a base de conhecimento manualmente."],
                confidence=0.1,
                system_type="Unknown"
            )
    
    def _detect_system_type(self, problem_description: str) -> str:
        """Detect system type using keyword matching and ML if available"""
        problem_lower = problem_description.lower()
        
        # Score each system type based on keywords
        scores = {}
        for system, keywords in self.system_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in problem_lower:
                    score += 1
            scores[system] = score
        
        # Get the system with highest score
        if scores and max(scores.values()) > 0:
            detected_system = max(scores.keys(), key=lambda k: scores[k])
            return detected_system
        
        # If no keywords matched, try ML classifier if trained
        if self.system_classifier and self.is_trained:
            try:
                prediction = self.system_classifier.predict([problem_description])
                return self.label_encoder.inverse_transform(prediction)[0]
            except Exception as e:
                logging.error(f"Error in ML system detection: {str(e)}")
        
        return "Unknown"
    
    def _generate_solutions(self, problem_description: str, system_type: str) -> List[str]:
        """Generate diverse solution suggestions based on enhanced problem analysis"""
        problem_normalized = self._preprocess_text(problem_description)
        problem_tokens = set(self._semantic_tokenizer(problem_normalized))
        suggestions = []
        
        # Enhanced pattern-based solution generation with more variety
        
        # Password/Authentication issues
        if any(token in problem_tokens for token in ['senha', 'password', 'login', 'acesso', 'autenticacao', 'esqueci']):
            auth_solutions = [
                "Verificar se o usuário está digitando a senha corretamente",
                "Resetar senha do usuário no sistema administrativo",
                "Verificar se a conta não está bloqueada por tentativas",
                "Checar configurações de política de senhas",
                "Validar sincronização com Active Directory se aplicável"
            ]
            suggestions.extend(auth_solutions[:3])  # Add variety by taking different amounts
        
        # Network/Connection issues
        if any(token in problem_tokens for token in ['conectar', 'conexao', 'rede', 'network', 'internet']):
            network_solutions = [
                "Testar conectividade com ping para o servidor",
                "Verificar configurações de proxy e firewall",
                "Reiniciar adaptador de rede no computador",
                "Checar cabos de rede e switches",
                "Verificar configurações DNS e DHCP",
                "Testar conectividade em outro computador"
            ]
            suggestions.extend(network_solutions[:2])  # Take fewer to keep variety
        
        # Database/Performance issues
        if any(token in problem_tokens for token in ['banco', 'database', 'sql', 'lento', 'slow', 'performance']):
            db_solutions = [
                "Verificar logs de erro do banco de dados",
                "Analisar queries lentas em execução",
                "Checar espaço disponível no servidor",
                "Reiniciar serviços do banco de dados",
                "Verificar índices e estatísticas do banco",
                "Monitorar uso de CPU e memória do servidor"
            ]
            suggestions.extend(db_solutions[:2])
        
        # System/Application errors
        if any(token in problem_tokens for token in ['erro', 'error', 'falha', 'exception', 'crash']):
            error_solutions = [
                "Consultar logs de aplicação para detalhes do erro",
                "Verificar se problema é reproduzível",
                "Checar atualizações pendentes do sistema",
                "Validar integridade dos arquivos de sistema",
                "Reiniciar serviços relacionados ao problema"
            ]
            suggestions.extend(error_solutions[:2])
        
        # Hardware/Infrastructure issues  
        if any(token in problem_tokens for token in ['hardware', 'impressora', 'printer', 'computador', 'pc']):
            hardware_solutions = [
                "Verificar conexões físicas dos equipamentos",
                "Testar em outro computador para isolar problema",
                "Verificar drivers de dispositivos",
                "Checar logs de eventos do Windows",
                "Reiniciar equipamentos envolvidos"
            ]
            suggestions.extend(hardware_solutions[:2])
        
        # Add system-specific solutions for variety
        system_specific = self._get_diversified_system_solutions(system_type, problem_tokens)
        suggestions.extend(system_specific)
        
        # If no specific patterns matched, add contextual generic solutions
        if not suggestions:
            generic_solutions = [
                "Verificar logs do sistema para identificar causa raiz",
                "Reproduzir problema com usuário de teste",
                "Documentar passos exatos que levaram ao problema",
                "Checar se problema afeta outros usuários",
                "Verificar últimas alterações no sistema"
            ]
            suggestions.extend(generic_solutions[:3])
        
        # Ensure variety by shuffling and limiting
        import random
        unique_suggestions = list(dict.fromkeys(suggestions))
        if len(unique_suggestions) > 5:
            # Keep some determinism but add variety
            priority_suggestions = unique_suggestions[:3]  # Keep top 3
            random_suggestions = random.sample(unique_suggestions[3:], min(2, len(unique_suggestions)-3))
            unique_suggestions = priority_suggestions + random_suggestions
        
        return unique_suggestions[:5] if unique_suggestions else [
            "Analisar logs detalhados do sistema",
            "Contatar suporte especializado",
            "Documentar cenário completo do problema"
        ]
    
    def _convert_to_infinitive(self, text: str) -> str:
        """Convert common past participle forms to infinitive"""
        # Common past participle to infinitive conversions for Portuguese
        conversions = {
            # Pattern: past participle -> infinitive
            'corrigida': 'corrigir',
            'corrigido': 'corrigir', 
            'analisada': 'analisar',
            'analisado': 'analisar',
            'ajustada': 'ajustar',
            'ajustado': 'ajustar',
            'verificada': 'verificar',
            'verificado': 'verificar',
            'checada': 'checar',
            'checado': 'checar',
            'configurada': 'configurar',
            'configurado': 'configurar',
            'resetada': 'resetar',
            'resetado': 'resetar',
            'reiniciada': 'reiniciar',
            'reiniciado': 'reiniciar',
            'atualizada': 'atualizar',
            'atualizado': 'atualizar',
            'validada': 'validar',
            'validado': 'validar',
            'testada': 'testar',
            'testado': 'testar',
            'consultada': 'consultar',
            'consultado': 'consultar',
            'documentada': 'documentar',
            'documentado': 'documentar',
            'monitorada': 'monitorar',
            'monitorado': 'monitorar'
        }
        
        # Apply conversions
        result = text.lower()
        for past_participle, infinitive in conversions.items():
            result = result.replace(past_participle, infinitive)
        
        # Capitalize first letter to maintain original format
        if result and result[0].islower() and text and text[0].isupper():
            result = result[0].upper() + result[1:]
            
        return result

    def _generate_solutions_with_similar_cases(self, problem_description: str, system_type: str, similar_cases: list = None) -> List[str]:
        """Generate solutions with INTELLIGENT RANKING based on feedback learning"""
        suggestions = []
        
        # PRIORITY 1: Solutions from similar cases with SMART SCORING
        if similar_cases:
            similar_solutions = []
            for case in similar_cases[:5]:  # Consider more cases for better learning
                if hasattr(case, 'solution') and case.solution:
                    solution = case.solution.strip()
                    solution = self._convert_to_infinitive(solution)
                    
                    if solution and solution not in [s['text'] for s in similar_solutions]:
                        # Calculate intelligent score based on feedback learning
                        effectiveness_score = self._calculate_solution_effectiveness_score(solution, problem_description)
                        similar_solutions.append({
                            'text': solution,
                            'score': effectiveness_score,
                            'case_id': getattr(case, 'id', None),
                            'source': 'similar_case'
                        })
            
            # Sort by intelligent score (highest first)
            similar_solutions.sort(key=lambda x: x['score'], reverse=True)
            suggestions.extend([s['text'] for s in similar_solutions[:3]])  # Top 3 by score
            logging.info(f"Added {len(similar_solutions)} intelligently ranked solutions from similar cases")
        
        # PRIORITY 2: Pattern-based solutions with SMART RANKING
        if len(suggestions) < 4:
            pattern_solutions = self._generate_solutions(problem_description, system_type)
            
            # Apply intelligent scoring to pattern solutions
            scored_pattern_solutions = []
            for solution in pattern_solutions:
                converted_solution = self._convert_to_infinitive(solution)
                if converted_solution not in suggestions:
                    effectiveness_score = self._calculate_solution_effectiveness_score(converted_solution, problem_description)
                    scored_pattern_solutions.append({
                        'text': converted_solution,
                        'score': effectiveness_score,
                        'source': 'pattern'
                    })
            
            # Sort by score and add the best ones
            scored_pattern_solutions.sort(key=lambda x: x['score'], reverse=True)
            for solution in scored_pattern_solutions:
                if len(suggestions) < 5:
                    suggestions.append(solution['text'])
        
        # INTELLIGENT FINAL RANKING: Re-rank all suggestions by combined score
        if hasattr(self, 'suggestion_ranking_weights'):
            suggestions = self._apply_intelligent_final_ranking(suggestions, problem_description)
        
        # FEEDBACK-BASED LEARNING: Apply feedback ranking for continuous improvement
        suggestions = self._rank_solutions_by_feedback(suggestions, problem_description)
        
        # Ensure we have suggestions with fallback
        if not suggestions:
            suggestions = [
                "Verificar logs detalhados do sistema para identificar a causa raiz",
                "Reproduzir o problema em ambiente de teste",
                "Consultar base de conhecimento interna",
                "Contatar suporte especializado se necessário",
                "Documentar cenário completo para análise"
            ]
        
        # Apply infinitive conversion to ALL suggestions
        final_suggestions = [self._convert_to_infinitive(solution) for solution in suggestions[:5]]
        
        logging.info(f"Generated {len(final_suggestions)} intelligently ranked solutions")
        return final_suggestions
    
    def _calculate_solution_effectiveness_score(self, solution_text: str, problem_description: str) -> float:
        """Calculate effectiveness score for a solution based on learned feedback patterns"""
        try:
            if not hasattr(self, 'solution_effectiveness'):
                return 1.0  # Default score
            
            # Extract tokens from both solution and problem
            solution_tokens = set(self._semantic_tokenizer(self._preprocess_text(solution_text)))
            problem_tokens = set(self._semantic_tokenizer(self._preprocess_text(problem_description)))
            
            # Calculate base score using solution effectiveness weights
            total_score = 0.0
            token_count = 0
            
            for token in solution_tokens.union(problem_tokens):
                # Look for helpful patterns
                helpful_pattern = f"{token}_helpful"
                not_helpful_pattern = f"{token}_not_helpful"
                
                if helpful_pattern in self.solution_effectiveness:
                    total_score += self.solution_effectiveness[helpful_pattern]['weight']
                    token_count += 1
                elif not_helpful_pattern in self.solution_effectiveness:
                    # Penalize tokens associated with not helpful feedback
                    total_score += (2.0 - self.solution_effectiveness[not_helpful_pattern]['weight'])
                    token_count += 1
                else:
                    total_score += 1.0  # Neutral score for unknown tokens
                    token_count += 1
            
            # Calculate average score
            if token_count > 0:
                average_score = total_score / token_count
            else:
                average_score = 1.0
            
            # Bonus for successful combination patterns
            if hasattr(self, 'feedback_patterns'):
                for combo in self.feedback_patterns.get('successful_combinations', []):
                    # Check if this solution matches successful patterns
                    matching_tokens = set(combo['problem_tokens']).intersection(solution_tokens.union(problem_tokens))
                    if len(matching_tokens) >= 2:  # At least 2 tokens match
                        # Apply success rate bonus
                        average_score *= (1 + combo['success_rate'] * 0.3)
            
            # Ensure score is within reasonable bounds
            return max(0.1, min(3.0, average_score))
            
        except Exception as e:
            logging.error(f"Error calculating solution effectiveness score: {str(e)}")
            return 1.0
    
    def _apply_intelligent_final_ranking(self, suggestions: List[str], problem_description: str) -> List[str]:
        """Apply final intelligent ranking to suggestions based on learned patterns"""
        try:
            # Score each suggestion
            scored_suggestions = []
            problem_tokens = set(self._semantic_tokenizer(self._preprocess_text(problem_description)))
            
            for suggestion in suggestions:
                # Calculate comprehensive score
                effectiveness_score = self._calculate_solution_effectiveness_score(suggestion, problem_description)
                
                # Apply ranking weights
                ranking_bonus = 0.0
                suggestion_tokens = set(self._semantic_tokenizer(self._preprocess_text(suggestion)))
                
                for token in suggestion_tokens.intersection(problem_tokens):
                    if hasattr(self, 'suggestion_ranking_weights') and token in self.suggestion_ranking_weights:
                        ranking_bonus += self.suggestion_ranking_weights[token]
                
                final_score = effectiveness_score + (ranking_bonus * 0.2)  # 20% bonus from ranking weights
                
                scored_suggestions.append({
                    'text': suggestion,
                    'score': final_score
                })
            
            # Sort by final score
            scored_suggestions.sort(key=lambda x: x['score'], reverse=True)
            
            # Return ranked suggestions
            return [s['text'] for s in scored_suggestions]
            
        except Exception as e:
            logging.error(f"Error applying intelligent final ranking: {str(e)}")
            return suggestions
    
    def _get_diversified_system_solutions(self, system_type: str, problem_tokens: set) -> List[str]:
        """Get diversified system-specific solutions based on context"""
        solutions = []
        
        if system_type == "Tasy":
            if 'login' in problem_tokens or 'senha' in problem_tokens:
                solutions.append("Verificar usuário no cadastro de funcionários do Tasy")
            elif 'impressao' in problem_tokens or 'relatorio' in problem_tokens:
                solutions.append("Checar configuração de impressoras no Tasy")
            elif 'lento' in problem_tokens or 'performance' in problem_tokens:
                solutions.append("Verificar performance de queries no banco Tasy")
            else:
                solutions.append("Consultar logs específicos do módulo Tasy afetado")
        
        elif system_type == "SGU":
            if 'autorizacao' in problem_tokens:
                solutions.append("Verificar regras de autorização no SGU")
            elif 'relatorio' in problem_tokens:
                solutions.append("Checar permissões de relatórios no SGU")
            else:
                solutions.append("Validar configurações de módulos SGU")
        
        elif system_type == "Autorizador":
            if 'guia' in problem_tokens or 'procedimento' in problem_tokens:
                solutions.append("Verificar fila de processamento de guias")
            elif 'operadora' in problem_tokens:
                solutions.append("Checar conectividade com webservices das operadoras")
            else:
                solutions.append("Analisar logs de autorização em tempo real")
        
        # Add escalation path
        solutions.append("Considerar abertura de chamado Nexdow se necessário")
        
        return solutions[:2]  # Limit to 2 for variety
    
    def _rank_solutions_by_feedback(self, solutions: List[str], problem_description: str) -> List[str]:
        """Rank solutions based on historical feedback effectiveness"""
        try:
            if not hasattr(self, 'solution_effectiveness') or not self.solution_effectiveness:
                # No feedback data yet, return original order
                return solutions
            
            # Get problem tokens for pattern matching
            problem_tokens = set(self._semantic_tokenizer(self._preprocess_text(problem_description)))
            
            # Score each solution based on feedback patterns
            scored_solutions = []
            for solution in solutions:
                solution_tokens = set(self._semantic_tokenizer(self._preprocess_text(solution)))
                effectiveness_score = 1.0  # Default neutral score
                
                # Calculate effectiveness based on feedback patterns
                total_feedback_weight = 0
                weighted_effectiveness = 0
                
                for token in problem_tokens.union(solution_tokens):
                    helpful_key = f"{token}_helpful"
                    not_helpful_key = f"{token}_not_helpful"
                    
                    if helpful_key in self.solution_effectiveness:
                        helpful_count = self.solution_effectiveness[helpful_key]['helpful']
                        not_helpful_count = self.solution_effectiveness[helpful_key]['not_helpful']
                        total_feedback = helpful_count + not_helpful_count
                        
                        if total_feedback > 0:
                            token_effectiveness = helpful_count / total_feedback
                            # Weight by frequency of feedback
                            feedback_weight = min(total_feedback, 10) / 10  # Cap at 10 for weight calculation
                            
                            weighted_effectiveness += token_effectiveness * feedback_weight
                            total_feedback_weight += feedback_weight
                
                if total_feedback_weight > 0:
                    effectiveness_score = weighted_effectiveness / total_feedback_weight
                    # Scale to range 0.2 to 2.0 for meaningful ranking differences
                    effectiveness_score = 0.2 + (effectiveness_score * 1.8)
                
                scored_solutions.append({
                    'text': solution,
                    'score': effectiveness_score
                })
            
            # Sort by effectiveness score (higher is better)
            scored_solutions.sort(key=lambda x: x['score'], reverse=True)
            
            # Log the reranking for debugging
            if scored_solutions[0]['score'] != scored_solutions[-1]['score']:
                logging.info(f"FEEDBACK LEARNING: Reranked solutions based on feedback patterns. "
                           f"Top solution score: {scored_solutions[0]['score']:.2f}, "
                           f"Lowest: {scored_solutions[-1]['score']:.2f}")
            
            return [s['text'] for s in scored_solutions]
            
        except Exception as e:
            logging.error(f"Error ranking solutions by feedback: {str(e)}")
            return solutions
    
    def _get_system_specific_solutions(self, system_type: str, problem_description: str) -> List[str]:
        """Get system-specific solution suggestions"""
        solutions = []
        
        if system_type == "Tasy":
            solutions = [
                "Verificar configurações do módulo Tasy específico",
                "Consultar logs do sistema Tasy",
                "Verificar integridade da base de dados Tasy",
                "Checar configurações de usuário no Tasy",
                "Verificar se problema requer chamado para Nexdow"
            ]
        elif system_type == "SGU":
            solutions = [
                "Verificar status dos serviços SGU",
                "Consultar logs de erro do SGU",
                "Checar conectividade com base de dados SGU",
                "Validar configurações de módulos SGU",
                "Considerar abertura de chamado Nexdow se necessário"
            ]
        elif system_type == "SGU Card":
            solutions = [
                "Verificar serviços de credenciamento",
                "Consultar logs do módulo Card",
                "Checar sincronização de dados de carteirinha",
                "Validar configurações de impressão de cartões",
                "Abrir chamado Nexdow se problema persistir"
            ]
        elif system_type == "Autorizador":
            solutions = [
                "Verificar fila de autorizações pendentes",
                "Consultar logs do sistema autorizador",
                "Checar conectividade com operadoras",
                "Validar regras de autorização",
                "Escalar para Nexdow casos complexos"
            ]
        elif system_type == "Healthcare":
            solutions = [
                "Verificar conectividade com sistemas de saúde",
                "Validar protocolos de comunicação HL7/FHIR",
                "Checar configurações de prontuário eletrônico"
            ]
        elif system_type == "Network":
            solutions = [
                "Verificar configurações de switch/router",
                "Testar conectividade ping/traceroute",
                "Analisar logs de firewall",
                "Verificar configurações VLAN"
            ]
        elif system_type == "Database":
            solutions = [
                "Verificar performance de queries",
                "Analisar locks e deadlocks",
                "Checar espaço em tablespaces",
                "Validar backup e recovery"
            ]
        
        # Add generic Nexdow escalation option
        solutions.append("Se problema não for resolvido, abrir chamado para Nexdow")
        
        return solutions
    
    def _calculate_confidence(self, problem_description: str, system_type: str, suggestions: List[str]) -> float:
        """Calculate confidence score based on various factors"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on description length and detail
        if len(problem_description) > 50:
            confidence += 0.1
        if len(problem_description) > 100:
            confidence += 0.1
        if len(problem_description) > 200:
            confidence += 0.1
        
        # Increase confidence if system type is detected
        if system_type != "Unknown":
            confidence += 0.2
        
        # Increase confidence based on number of relevant suggestions
        if len(suggestions) >= 3:
            confidence += 0.1
        
        # Check for technical keywords
        technical_keywords = ['erro', 'falha', 'exception', 'timeout', 'connection', 'database', 'server']
        keyword_count = sum(1 for keyword in technical_keywords if keyword in problem_description.lower())
        confidence += min(keyword_count * 0.05, 0.2)
        
        return min(confidence, 1.0)
    
    def train_models(self, cases: List[Case]) -> bool:
        """Train ML models with existing cases"""
        if len(cases) < 5:  # Need minimum cases to train
            logging.info("Not enough cases to train ML models")
            return False
        
        try:
            # Prepare training data
            descriptions = [case.problem_description for case in cases]
            system_types = [case.system_type for case in cases if case.system_type != "Unknown"]
            
            if len(system_types) < 3:  # Need minimum variety
                logging.info("Not enough system type variety to train classifier")
                return False
            
            # Train system type classifier
            filtered_descriptions = [cases[i].problem_description for i, case in enumerate(cases) 
                                   if case.system_type != "Unknown"]
            
            if len(filtered_descriptions) >= 3:
                # Encode labels
                encoded_labels = self.label_encoder.fit_transform(system_types)
                
                # Create and train pipeline
                self.system_classifier = Pipeline([
                    ('tfidf', TfidfVectorizer(stop_words='english', max_features=500)),
                    ('classifier', MultinomialNB())
                ])
                
                self.system_classifier.fit(filtered_descriptions, encoded_labels)
                self.is_trained = True
                
                # Save models
                self._save_models()
                
                logging.info(f"Trained ML models with {len(cases)} cases")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error training ML models: {str(e)}")
            return False
    
    def process_analysis_feedback(self, feedback):
        """Process feedback from analysis to improve future suggestions using advanced ML learning"""
        try:
            import json
            from app import db
            from models import AnalysisFeedback
            
            # Parse feedback data
            suggestion_ratings = json.loads(feedback.suggestion_ratings or "{}")
            good_aspects = json.loads(feedback.good_aspects or "[]")
            improvements = json.loads(feedback.improvements or "[]")
            
            # Analyze feedback patterns
            helpful_suggestions = sum(1 for rating in suggestion_ratings.values() if rating == "helpful")
            total_suggestions = len(suggestion_ratings)
            
            if total_suggestions > 0:
                success_rate = helpful_suggestions / total_suggestions
                
                # ADVANCED LEARNING: Update solution effectiveness weights
                self._update_solution_effectiveness_weights(feedback.problem_description, suggestion_ratings)
                
                # SMART PATTERN DETECTION: Learn from feedback patterns
                self._learn_from_feedback_patterns(feedback.problem_description, suggestion_ratings, 
                                                 feedback.detected_system, good_aspects, improvements)
                
                # Log comprehensive feedback analysis
                logging.info(f"Advanced ML Feedback: {success_rate:.1%} helpful, Score: {feedback.overall_score}/5, "
                           f"System: {feedback.detected_system}, Learning from patterns")
                
                # INTELLIGENT RETRAINING: Based on feedback quality and frequency
                feedback_count = db.session.query(AnalysisFeedback).count()
                
                # More frequent retraining for better learning
                if feedback_count % 5 == 0:  # Retrain every 5 feedback entries for faster learning
                    logging.info(f"Triggering intelligent ML retrain after {feedback_count} feedback entries")
                    case_service = self._get_case_service()
                    all_cases = case_service.get_all_cases()
                    if len(all_cases) >= 3:  # Lower threshold for more dynamic learning
                        self.train_models(all_cases)
                        self._update_suggestion_ranking_model()
                
        except Exception as e:
            logging.error(f"Error processing analysis feedback: {str(e)}")
    
    def _update_solution_effectiveness_weights(self, problem_description, suggestion_ratings):
        """Update effectiveness weights for solution patterns based on feedback"""
        try:
            # Initialize solution effectiveness tracking if not exists
            if not hasattr(self, 'solution_effectiveness'):
                self.solution_effectiveness = {}
            
            # Extract key terms from problem for pattern matching
            problem_tokens = set(self._semantic_tokenizer(self._preprocess_text(problem_description)))
            
            # Update weights for each rated suggestion
            for suggestion_index, rating in suggestion_ratings.items():
                # Create pattern key from problem tokens and rating
                for token in problem_tokens:
                    pattern_key = f"{token}_{rating}"
                    
                    if pattern_key not in self.solution_effectiveness:
                        self.solution_effectiveness[pattern_key] = {'helpful': 0, 'not_helpful': 0, 'weight': 1.0}
                    
                    # Update counters
                    self.solution_effectiveness[pattern_key][rating] += 1
                    
                    # Calculate new effectiveness weight (helpful vs not_helpful ratio)
                    helpful_count = self.solution_effectiveness[pattern_key]['helpful']
                    not_helpful_count = self.solution_effectiveness[pattern_key]['not_helpful']
                    
                    if helpful_count + not_helpful_count > 0:
                        # Weight between 0.1 and 2.0 based on success rate
                        success_rate = helpful_count / (helpful_count + not_helpful_count)
                        self.solution_effectiveness[pattern_key]['weight'] = 0.1 + (success_rate * 1.9)
            
            logging.info(f"Updated solution effectiveness weights for {len(problem_tokens)} tokens")
            
        except Exception as e:
            logging.error(f"Error updating solution effectiveness weights: {str(e)}")
    
    def _learn_from_feedback_patterns(self, problem_description, suggestion_ratings, detected_system, good_aspects, improvements):
        """Advanced pattern learning from comprehensive feedback data"""
        try:
            # Initialize pattern learning storage
            if not hasattr(self, 'feedback_patterns'):
                self.feedback_patterns = {
                    'system_accuracy': {},  # Track system detection accuracy
                    'solution_patterns': {},  # Track which solution patterns work best
                    'improvement_requests': {},  # Track what users want improved
                    'successful_combinations': []  # Track successful problem-solution combinations
                }
            
            # Learn system detection accuracy
            system_key = detected_system or 'Unknown'
            if system_key not in self.feedback_patterns['system_accuracy']:
                self.feedback_patterns['system_accuracy'][system_key] = {'correct': 0, 'total': 0}
            
            # Assume system detection is correct if overall feedback is positive
            helpful_count = sum(1 for rating in suggestion_ratings.values() if rating == "helpful")
            if helpful_count >= len(suggestion_ratings) / 2:  # If majority helpful, system detection likely correct
                self.feedback_patterns['system_accuracy'][system_key]['correct'] += 1
            self.feedback_patterns['system_accuracy'][system_key]['total'] += 1
            
            # Learn from improvement requests
            for improvement in improvements:
                if improvement not in self.feedback_patterns['improvement_requests']:
                    self.feedback_patterns['improvement_requests'][improvement] = 0
                self.feedback_patterns['improvement_requests'][improvement] += 1
            
            # Record successful combinations for future reference
            if helpful_count >= len(suggestion_ratings) / 2:
                self.feedback_patterns['successful_combinations'].append({
                    'problem_tokens': self._semantic_tokenizer(self._preprocess_text(problem_description)),
                    'system': detected_system,
                    'success_rate': helpful_count / len(suggestion_ratings),
                    'good_aspects': good_aspects
                })
                
                # Keep only the best 100 combinations to avoid memory issues
                if len(self.feedback_patterns['successful_combinations']) > 100:
                    # Sort by success rate and keep top 100
                    self.feedback_patterns['successful_combinations'].sort(
                        key=lambda x: x['success_rate'], reverse=True
                    )
                    self.feedback_patterns['successful_combinations'] = self.feedback_patterns['successful_combinations'][:100]
            
            logging.info(f"Advanced pattern learning: Updated patterns for {detected_system}, "
                        f"Success combinations: {len(self.feedback_patterns['successful_combinations'])}")
            
        except Exception as e:
            logging.error(f"Error in feedback pattern learning: {str(e)}")
    
    def _update_suggestion_ranking_model(self):
        """Update internal ranking model based on learned feedback patterns"""
        try:
            if not hasattr(self, 'feedback_patterns') or not hasattr(self, 'solution_effectiveness'):
                return
            
            # Create intelligent suggestion ranking weights
            self.suggestion_ranking_weights = {}
            
            # Weight based on solution effectiveness
            for pattern_key, effectiveness_data in self.solution_effectiveness.items():
                if '_helpful' in pattern_key:
                    token = pattern_key.replace('_helpful', '')
                    self.suggestion_ranking_weights[token] = effectiveness_data.get('weight', 1.0)
            
            # Weight successful combinations higher
            for combo in self.feedback_patterns.get('successful_combinations', []):
                for token in combo['problem_tokens']:
                    if token in self.suggestion_ranking_weights:
                        # Boost weight for tokens in successful combinations
                        self.suggestion_ranking_weights[token] *= (1 + combo['success_rate'] * 0.5)
                    else:
                        self.suggestion_ranking_weights[token] = 1 + combo['success_rate'] * 0.5
            
            logging.info(f"Updated suggestion ranking model with {len(self.suggestion_ranking_weights)} intelligent weights")
            
        except Exception as e:
            logging.error(f"Error updating suggestion ranking model: {str(e)}")
    
    def _get_case_service(self):
        """Get case service instance with import handling"""
        try:
            from case_service import CaseService
            return CaseService()
        except ImportError:
            # Fallback for circular import issues
            from app import current_app
            return current_app.config.get('case_service_instance')
    
    def _save_models(self):
        """Save trained models AND intelligent learning data to disk"""
        try:
            models_dir = "ml_models"
            os.makedirs(models_dir, exist_ok=True)
            
            if self.system_classifier:
                with open(f"{models_dir}/system_classifier.pkl", "wb") as f:
                    pickle.dump(self.system_classifier, f)
            
            if hasattr(self, 'label_encoder'):
                with open(f"{models_dir}/label_encoder.pkl", "wb") as f:
                    pickle.dump(self.label_encoder, f)
            
            # ADVANCED: Save intelligent learning data
            learning_data = {
                'solution_effectiveness': getattr(self, 'solution_effectiveness', {}),
                'feedback_patterns': getattr(self, 'feedback_patterns', {}),
                'suggestion_ranking_weights': getattr(self, 'suggestion_ranking_weights', {}),
                'learning_version': '2.0'  # Version for future compatibility
            }
            with open(f"{models_dir}/intelligent_learning.pkl", "wb") as f:
                pickle.dump(learning_data, f)
            
            # Save enhanced metadata
            metadata = {
                'trained_at': datetime.now().isoformat(),
                'is_trained': self.is_trained,
                'learning_data_saved': True,
                'solution_patterns_count': len(getattr(self, 'solution_effectiveness', {})),
                'successful_combinations_count': len(getattr(self, 'feedback_patterns', {}).get('successful_combinations', [])),
                'ranking_weights_count': len(getattr(self, 'suggestion_ranking_weights', {}))
            }
            with open(f"{models_dir}/metadata.pkl", "wb") as f:
                pickle.dump(metadata, f)
            
            logging.info(f"Saved ML models with intelligent learning data: "
                        f"{metadata['solution_patterns_count']} patterns, "
                        f"{metadata['successful_combinations_count']} successful combinations")
                
        except Exception as e:
            logging.error(f"Error saving ML models: {str(e)}")
    
    def _load_models(self):
        """Load trained models AND intelligent learning data from disk"""
        try:
            models_dir = "ml_models"
            
            # Load system classifier
            classifier_path = f"{models_dir}/system_classifier.pkl"
            if os.path.exists(classifier_path):
                with open(classifier_path, "rb") as f:
                    self.system_classifier = pickle.load(f)
            
            # Load label encoder
            encoder_path = f"{models_dir}/label_encoder.pkl"
            if os.path.exists(encoder_path):
                with open(encoder_path, "rb") as f:
                    self.label_encoder = pickle.load(f)
            
            # ADVANCED: Load intelligent learning data
            learning_path = f"{models_dir}/intelligent_learning.pkl"
            if os.path.exists(learning_path):
                with open(learning_path, "rb") as f:
                    learning_data = pickle.load(f)
                    
                    # Restore intelligent learning attributes
                    self.solution_effectiveness = learning_data.get('solution_effectiveness', {})
                    self.feedback_patterns = learning_data.get('feedback_patterns', {})
                    self.suggestion_ranking_weights = learning_data.get('suggestion_ranking_weights', {})
                    
                    logging.info(f"Loaded intelligent learning data: "
                               f"{len(self.solution_effectiveness)} solution patterns, "
                               f"{len(self.feedback_patterns.get('successful_combinations', []))} successful combinations, "
                               f"{len(self.suggestion_ranking_weights)} ranking weights")
            
            # Load metadata
            metadata_path = f"{models_dir}/metadata.pkl"
            if os.path.exists(metadata_path):
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)
                    self.is_trained = metadata.get('is_trained', False)
            
            if self.system_classifier and self.is_trained:
                learning_info = ""
                if hasattr(self, 'solution_effectiveness'):
                    learning_info = f" with {len(self.solution_effectiveness)} learned patterns"
                logging.info(f"Loaded trained ML models{learning_info}")
            
        except Exception as e:
            logging.error(f"Error loading ML models: {str(e)}")
            self.is_trained = False
    
    def get_model_info(self) -> Dict:
        """Get comprehensive information about trained models and learning progress"""
        # Calculate learning statistics
        solution_effectiveness_count = len(getattr(self, 'solution_effectiveness', {}))
        successful_combinations_count = len(getattr(self, 'feedback_patterns', {}).get('successful_combinations', []))
        ranking_weights_count = len(getattr(self, 'suggestion_ranking_weights', {}))
        
        # Calculate system detection accuracy if available
        system_accuracy = {}
        if hasattr(self, 'feedback_patterns') and 'system_accuracy' in self.feedback_patterns:
            for system, stats in self.feedback_patterns['system_accuracy'].items():
                if stats['total'] > 0:
                    accuracy = stats['correct'] / stats['total']
                    system_accuracy[system] = {
                        'accuracy': round(accuracy * 100, 1),
                        'total_analyzed': stats['total']
                    }
        
        # Get top improvement requests
        top_improvements = {}
        if hasattr(self, 'feedback_patterns') and 'improvement_requests' in self.feedback_patterns:
            improvements = self.feedback_patterns['improvement_requests']
            # Get top 5 most requested improvements
            sorted_improvements = sorted(improvements.items(), key=lambda x: x[1], reverse=True)
            top_improvements = dict(sorted_improvements[:5])
        
        return {
            'is_trained': self.is_trained,
            'has_system_classifier': self.system_classifier is not None,
            'supported_systems': list(self.system_keywords.keys()),
            'learning_statistics': {
                'solution_effectiveness_patterns': solution_effectiveness_count,
                'successful_combinations': successful_combinations_count,
                'ranking_weights': ranking_weights_count,
                'learning_active': solution_effectiveness_count > 0
            },
            'system_detection_accuracy': system_accuracy,
            'top_improvement_requests': top_improvements,
            'learning_version': '2.0 - Advanced Intelligent Learning'
        }
    
    def get_learning_insights(self) -> Dict:
        """Get insights about what the system has learned from feedback"""
        insights = {
            'most_effective_solutions': [],
            'least_effective_patterns': [],
            'best_performing_systems': [],
            'learning_recommendations': []
        }
        
        try:
            # Most effective solution patterns
            if hasattr(self, 'solution_effectiveness'):
                effective_patterns = []
                for pattern_key, data in self.solution_effectiveness.items():
                    if '_helpful' in pattern_key and data['helpful'] > 2:  # At least 3 helpful votes
                        token = pattern_key.replace('_helpful', '')
                        success_rate = data['helpful'] / (data['helpful'] + data.get('not_helpful', 0))
                        effective_patterns.append({
                            'pattern': token,
                            'success_rate': round(success_rate * 100, 1),
                            'total_feedback': data['helpful'] + data.get('not_helpful', 0)
                        })
                
                # Sort by success rate and take top 10
                effective_patterns.sort(key=lambda x: x['success_rate'], reverse=True)
                insights['most_effective_solutions'] = effective_patterns[:10]
            
            # Best performing systems
            if hasattr(self, 'feedback_patterns') and 'system_accuracy' in self.feedback_patterns:
                system_performance = []
                for system, stats in self.feedback_patterns['system_accuracy'].items():
                    if stats['total'] >= 3:  # At least 3 analyses
                        accuracy = stats['correct'] / stats['total']
                        system_performance.append({
                            'system': system,
                            'accuracy': round(accuracy * 100, 1),
                            'total_analyses': stats['total']
                        })
                
                system_performance.sort(key=lambda x: x['accuracy'], reverse=True)
                insights['best_performing_systems'] = system_performance
            
            # Learning recommendations
            recommendations = []
            if len(insights['most_effective_solutions']) > 0:
                recommendations.append("Sistema aprendendo com sucesso - padrões efetivos identificados")
            if len(insights['best_performing_systems']) > 0:
                best_system = insights['best_performing_systems'][0]
                recommendations.append(f"Detecção mais precisa para sistema {best_system['system']} ({best_system['accuracy']}%)")
            
            if hasattr(self, 'feedback_patterns') and len(self.feedback_patterns.get('improvement_requests', {})) > 0:
                top_request = max(self.feedback_patterns['improvement_requests'].items(), key=lambda x: x[1])
                recommendations.append(f"Principal melhoria solicitada: {top_request[0]}")
            
            insights['learning_recommendations'] = recommendations
            
        except Exception as e:
            logging.error(f"Error generating learning insights: {str(e)}")
        
        return insights