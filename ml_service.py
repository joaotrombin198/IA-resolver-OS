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
            # Password related terms
            'senha': ['password', 'pass', 'pwd', 'login', 'credencial', 'acesso', 'autenticacao'],
            'password': ['senha', 'pass', 'pwd', 'login', 'credencial', 'acesso', 'autenticacao'],
            'recuperar': ['recover', 'reset', 'resetar', 'restaurar', 'redefinir'],
            'expirada': ['expired', 'vencida', 'bloqueada', 'blocked', 'invalid', 'invalida'],
            'expiry': ['expiracao', 'vencimento', 'validade'],
            
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
        """Enhanced text preprocessing with normalization"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents and normalize unicode
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
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
    
    def analyze_problem(self, problem_description: str) -> SolutionSuggestion:
        """Analyze problem description and provide ML-based suggestions"""
        try:
            # Detect system type
            system_type = self._detect_system_type(problem_description)
            
            # Generate solution suggestions
            suggestions = self._generate_solutions(problem_description, system_type)
            
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
        """Generate solution suggestions based on problem patterns"""
        problem_lower = problem_description.lower()
        suggestions = []
        
        # Pattern-based solution generation
        if any(word in problem_lower for word in ['nao', 'não', 'erro', 'falha', 'problem']):
            if any(word in problem_lower for word in ['conectar', 'conexao', 'rede', 'network']):
                suggestions.extend(self.solution_patterns['network'])
            
            if any(word in problem_lower for word in ['banco', 'database', 'sql']):
                suggestions.extend(self.solution_patterns['database'])
            
            if any(word in problem_lower for word in ['memoria', 'memory', 'ram', 'lento', 'slow']):
                suggestions.extend(self.solution_patterns['memory'])
            
            if any(word in problem_lower for word in ['disco', 'disk', 'espaco', 'space']):
                suggestions.extend(self.solution_patterns['disk'])
            
            if any(word in problem_lower for word in ['permiss', 'acesso', 'login', 'auth']):
                suggestions.extend(self.solution_patterns['permissions'])
        
        # If no specific patterns matched, add generic restart solution
        if not suggestions:
            suggestions.extend(self.solution_patterns['restart'])
        
        # Add system-specific solutions
        system_specific = self._get_system_specific_solutions(system_type, problem_description)
        suggestions.extend(system_specific)
        
        # Remove duplicates and limit to 5 suggestions
        unique_suggestions = list(dict.fromkeys(suggestions))[:5]
        
        return unique_suggestions if unique_suggestions else [
            "Verificar logs do sistema para mais detalhes",
            "Contactar suporte técnico se o problema persistir",
            "Documentar os passos que levaram ao problema"
        ]
    
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
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            models_dir = "ml_models"
            os.makedirs(models_dir, exist_ok=True)
            
            if self.system_classifier:
                with open(f"{models_dir}/system_classifier.pkl", "wb") as f:
                    pickle.dump(self.system_classifier, f)
            
            if hasattr(self, 'label_encoder'):
                with open(f"{models_dir}/label_encoder.pkl", "wb") as f:
                    pickle.dump(self.label_encoder, f)
            
            # Save training metadata
            metadata = {
                'trained_at': datetime.now().isoformat(),
                'is_trained': self.is_trained
            }
            with open(f"{models_dir}/metadata.pkl", "wb") as f:
                pickle.dump(metadata, f)
                
        except Exception as e:
            logging.error(f"Error saving ML models: {str(e)}")
    
    def _load_models(self):
        """Load trained models from disk"""
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
            
            # Load metadata
            metadata_path = f"{models_dir}/metadata.pkl"
            if os.path.exists(metadata_path):
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)
                    self.is_trained = metadata.get('is_trained', False)
            
            if self.system_classifier and self.is_trained:
                logging.info("Loaded trained ML models")
            
        except Exception as e:
            logging.error(f"Error loading ML models: {str(e)}")
            self.is_trained = False
    
    def get_model_info(self) -> Dict:
        """Get information about trained models"""
        return {
            'is_trained': self.is_trained,
            'has_system_classifier': self.system_classifier is not None,
            'supported_systems': list(self.system_keywords.keys()),
            'solution_patterns': len(self.solution_patterns)
        }