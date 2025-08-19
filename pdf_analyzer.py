import logging
import re
import pdfplumber
from typing import Dict, List, Optional

class PDFAnalyzer:
    """Analisador universal de PDFs de ordens de serviço com classificação dinâmica"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Análise universal de PDF com sistema dinâmico"""
        try:
            # Extrair texto do PDF
            text = self._extract_text_from_pdf(pdf_path)
            
            # Identificar sistema
            system = self._identify_system(text)
            
            # Extrair número da OS
            os_number = self._extract_os_number(text)
            
            # Extrair descrição do problema
            problem = self._extract_problem_description(text)
            
            # Classificar problema dinamicamente
            problem_type = self._classify_problem_type(problem.lower())
            
            # Gerar solução dinâmica
            solution = self._generate_dynamic_solution(problem_type, problem, system, text)
            
            self.logger.info(f"PDF analisado: OS {os_number}, Sistema: {system}, Tipo: {problem_type}")
            
            return {
                'os_number': os_number,
                'problem_description': problem,
                'solution': solution,
                'system_type': system
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise do PDF: {str(e)}")
            return {
                'os_number': None,
                'problem_description': f"Erro ao processar PDF: {str(e)}",
                'solution': "1. Verificar integridade do arquivo PDF\n2. Tentar novamente o upload",
                'system_type': 'Desconhecido'
            }
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai texto do PDF usando pdfplumber"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _identify_system(self, text: str) -> str:
        """Identifica o sistema baseado no conteúdo"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['sgu', 'sistema sgu', 'sgu portal', 'sgu-crm', 'sgu suite']):
            return 'SGU'
        elif any(keyword in text_lower for keyword in ['tasy', 'sistema tasy']):
            return 'Tasy'
        elif any(keyword in text_lower for keyword in ['sgu card', 'card']):
            return 'SGU Card'
        elif any(keyword in text_lower for keyword in ['autorizador']):
            return 'Autorizador'
        else:
            return 'Sistema'
    
    def _extract_os_number(self, text: str) -> Optional[str]:
        """Extrai número da OS do cabeçalho"""
        number_match = re.search(r'Número\s+(\d+)', text, re.IGNORECASE)
        if number_match:
            return number_match.group(1)
        return None
    
    def _extract_problem_description(self, text: str) -> str:
        """Extrai descrição do problema do PDF"""
        dano_match = re.search(r'Dano\s+(.*?)(?=Execução|$)', text, re.DOTALL | re.IGNORECASE)
        if dano_match:
            description = dano_match.group(1).strip()
            description = re.sub(r'\s+', ' ', description)
            if len(description) > 50:
                return description
        
        desc_match = re.search(r'Descrição\s+([^\n]+)', text, re.IGNORECASE)
        if desc_match:
            return desc_match.group(1).strip()
        
        return "Problema não identificado no PDF"
    
    def _classify_problem_type(self, problem_text: str) -> str:
        """Classificação dinâmica universal que funciona para qualquer tipo de problema"""
        
        categories = {
            'authentication_access': {
                'keywords': ['senha', 'login', 'acesso', 'redefinir', 'recuperação', 'autenticação', 'bloqueado'],
                'weight': 1.0
            },
            'user_management': {
                'keywords': ['usuário', 'criar', 'criação', 'novo', 'colaborador', 'funcionário', 'cadastrar'],
                'weight': 0.9
            },
            'permissions_authorization': {
                'keywords': ['permissão', 'autorização', 'liberação', 'parametrizar', 'perfil', 'grupo', 'espelhar'],
                'weight': 0.9
            },
            'system_configuration': {
                'keywords': ['configuração', 'parametrização', 'setup', 'evento', 'módulo', 'competência'],
                'weight': 0.8
            },
            'data_correction': {
                'keywords': ['correção', 'alterar', 'atualizar', 'email', 'dados', 'informação', 'cadastro'],
                'weight': 0.8
            },
            'technical_issue': {
                'keywords': ['erro', 'bug', 'problema', 'falha', 'não funciona', 'travando', 'lento'],
                'weight': 0.7
            }
        }
        
        category_scores = {}
        for category, data in categories.items():
            score = 0
            keyword_count = 0
            for keyword in data['keywords']:
                if keyword in problem_text:
                    score += data['weight']
                    keyword_count += 1
            
            if keyword_count > 0:
                category_scores[category] = score * (keyword_count / len(data['keywords']))
        
        if category_scores:
            primary_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[primary_category]
            
            self.logger.info(f"Problema classificado dinamicamente: {primary_category} (score: {max_score:.2f})")
            return primary_category
        
        if any(word in problem_text for word in ['não consigo', 'impossível', 'bloqueado', 'negado']):
            return 'access_blocked'
        elif any(word in problem_text for word in ['preciso', 'necessário', 'solicito', 'favor']):
            return 'service_request'
        elif any(word in problem_text for word in ['urgente', 'importante', 'crítico', 'parado']):
            return 'critical_issue'
        else:
            self.logger.warning(f"Problema genérico identificado: {problem_text[:100]}...")
            return 'general_support'
    
    def _generate_dynamic_solution(self, problem_type: str, problem: str, system: str, full_text: str) -> str:
        """Gera soluções dinâmicas baseadas na categoria do problema"""
        
        solution_templates = {
            'authentication_access': [
                f"Acessar {system} como administrador de sistema",
                "Localizar usuário reportando problema de acesso",
                "Verificar status da conta (bloqueada, expirada, inativa)",
                "Analisar histórico de login e tentativas de acesso",
                "Resetar senha se necessário ou desbloquear conta",
                "Verificar e corrigir email cadastrado no sistema",
                "Testar login com credenciais atualizadas",
                "Orientar usuário sobre procedimentos de segurança",
                "Validar acesso funcionando com usuário final",
                "Documentar solução aplicada no chamado"
            ],
            'user_management': [
                f"Acessar módulo de gestão de usuários do {system}",
                "Analisar dados fornecidos do novo usuário/colaborador",
                "Verificar se usuário já existe no sistema",
                "Criar novo usuário com informações completas",
                "Definir perfil de acesso baseado na função/setor",
                "Configurar permissões específicas necessárias",
                "Gerar senha temporária segura",
                "Associar usuário a grupos/departamentos apropriados",
                "Testar login e funcionalidades básicas",
                "Enviar credenciais e orientações por email corporativo",
                "Validar funcionamento com solicitante",
                "Documentar usuário criado e permissões aplicadas"
            ],
            'permissions_authorization': [
                f"Acessar controle de permissões do {system}",
                "Identificar usuário de referência se mencionado",
                "Analisar permissões atuais do usuário solicitante",
                "Mapear permissões necessárias baseadas na solicitação",
                "Aplicar/ajustar permissões conforme necessário",
                "Verificar acesso a telas e funcionalidades específicas",
                "Testar operações críticas com o usuário",
                "Documentar permissões alteradas/adicionadas",
                "Validar funcionamento com usuário final",
                "Confirmar acesso adequado com solicitante"
            ],
            'system_configuration': [
                f"Acessar configurações administrativas do {system}",
                "Identificar módulo/área específica do problema",
                "Analisar configurações atuais relacionadas",
                "Verificar logs de sistema para identificar problemas",
                "Ajustar parâmetros/eventos conforme necessário",
                "Testar configurações em ambiente controlado",
                "Aplicar alterações no ambiente de produção",
                "Monitorar comportamento após mudanças",
                "Validar funcionamento com casos de teste",
                "Documentar configurações alteradas",
                "Confirmar resolução com usuário solicitante"
            ],
            'data_correction': [
                f"Acessar {system} com privilégios de edição",
                "Localizar registro/usuário com dados incorretos",
                "Verificar dados atuais versus dados corretos",
                "Fazer backup dos dados antes da alteração",
                "Aplicar correções nos campos identificados",
                "Verificar integridade dos dados após alteração",
                "Testar funcionalidades afetadas pela correção",
                "Validar dados corrigidos com solicitante",
                "Documentar alterações realizadas"
            ],
            'technical_issue': [
                f"Analisar problema técnico reportado no {system}",
                "Reproduzir o problema se possível",
                "Verificar logs de erro e sistema",
                "Identificar causa raiz do problema",
                "Implementar correção apropriada",
                "Testar solução em ambiente controlado",
                "Aplicar correção no ambiente de produção",
                "Monitorar estabilidade após correção",
                "Documentar problema e solução aplicada",
                "Validar funcionamento com usuário final"
            ]
        }
        
        if problem_type in solution_templates:
            base_steps = solution_templates[problem_type]
        else:
            base_steps = [
                f"Analisar problema reportado no {system}",
                "Identificar causa raiz do problema",
                "Implementar solução apropriada",
                "Testar funcionamento",
                "Validar com usuário solicitante",
                "Documentar solução aplicada"
            ]
        
        personalized_steps = self._personalize_solution(base_steps, problem, full_text)
        
        solution = '\n'.join(f"{i+1}. {step}" for i, step in enumerate(personalized_steps))
        
        self.logger.info(f"Solução dinâmica gerada: {len(personalized_steps)} etapas para {problem_type}")
        return solution
    
    def _personalize_solution(self, base_steps: list, problem: str, full_text: str) -> list:
        """Personaliza os passos da solução baseado no contexto específico"""
        personalized = base_steps.copy()
        problem_lower = problem.lower()
        
        names = re.findall(r'[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', full_text)
        if names:
            personalized.insert(-2, f"Confirmar dados específicos mencionados: {', '.join(names[:3])}")
        
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', full_text)
        if emails:
            personalized.insert(-2, f"Verificar e confirmar emails: {', '.join(emails[:2])}")
        
        numbers = re.findall(r'\b(?:evento|código|número)\s+(\d+)\b', problem_lower)
        if numbers:
            personalized.insert(2, f"Localizar especificamente: {', '.join(set(numbers))}")
        
        if any(word in problem_lower for word in ['urgente', 'crítico', 'parado', 'importante']):
            personalized.insert(0, "ATENÇÃO: Caso marcado como prioritário/urgente")
        
        return personalized
    
    def analyze_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, str]]:
        """Analisa múltiplos PDFs e retorna lista de casos"""
        cases = []
        for pdf_path in pdf_paths:
            try:
                case = self.analyze_pdf(pdf_path)
                cases.append(case)
                self.logger.info(f"PDF analisado com sucesso: {pdf_path}")
            except Exception as e:
                self.logger.error(f"Erro ao analisar PDF {pdf_path}: {str(e)}")
                continue
        
        return cases

def analyze_os_pdf(pdf_path: str) -> Dict[str, str]:
    """Função para análise rápida de PDF de OS"""
    analyzer = PDFAnalyzer()
    return analyzer.analyze_pdf(pdf_path)