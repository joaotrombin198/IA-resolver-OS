"""
Analisador de PDFs de Ordens de Serviço - Sistema 100% Interno
Extrai automaticamente problemas e soluções de PDFs de OS
"""
import os
import re
import logging
from typing import Dict, List, Optional, Tuple
import pdfplumber

class PDFAnalyzer:
    """Analisador inteligente de PDFs de Ordens de Serviço"""
    
    def __init__(self):
        self.system_patterns = {
            'SGU': r'SGU(?:-|\s)?(?:CRM|2\.0|Suite)?',
            'Tasy': r'Tasy',
            'SGU Card': r'SGU\s?Card',
            'Autorizador': r'Autorizador'
        }
        
        # Padrões para identificar tipos de problemas comuns
        self.problem_patterns = {
            'senha': r'(?:senha|password|redefinir|redefinição|esqueci|alteração|incorreta|provisória)',
            'acesso': r'(?:acesso|permissão|liberação|usuário|login|parametrizar|permissões|cadastral)',
            'email': r'(?:e-mail|email|corporativo|correio|pandion)',
            'parametrização': r'(?:parametrizar|configurar|permissões|perfil|mesmo.*permiss)',
            'sistema_indisponivel': r'(?:indisponível|fora do ar|não funciona|erro de sistema)',
            'lentidão': r'(?:lento|lentidão|demora|performance|travando)'
        }
        
    def analyze_pdf(self, pdf_path: str) -> Dict[str, str]:
        """
        Analisa PDF de OS e extrai problema, sistema e gera solução automaticamente
        
        Returns:
            Dict com 'problem_description', 'system_type', 'solution'
        """
        try:
            # Extrair texto do PDF
            pdf_text = self._extract_pdf_text(pdf_path)
            
            # Identificar sistema
            system_type = self._identify_system(pdf_text)
            
            # Extrair descrição do problema
            problem_description = self._extract_problem_description(pdf_text)
            
            # Gerar solução baseada nos padrões identificados
            solution = self._generate_solution(problem_description, system_type, pdf_text)
            
            return {
                'problem_description': problem_description,
                'system_type': system_type,
                'solution': solution
            }
            
        except Exception as e:
            logging.error(f"Erro ao analisar PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extrai texto completo do PDF"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def _identify_system(self, text: str) -> str:
        """Identifica o sistema baseado no conteúdo do PDF"""
        text_lower = text.lower()
        
        for system, pattern in self.system_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return system
                
        return "Unknown"
    
    def _extract_problem_description(self, text: str) -> str:
        """Extrai a descrição do problema do campo 'Dano' ou 'Descrição'"""
        # Procurar por seção "Dano" ou "Descrição"
        patterns = [
            r'Dano\s+(.+?)(?=\n\s*Execução|\n\s*Situação|\n\s*Históricos|$)',
            r'Descrição\s+(.+?)(?=\n\s*Dano|\n\s*Execução|\n\s*Situação|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                # Limpar texto e remover quebras desnecessárias
                description = re.sub(r'\s+', ' ', description)
                return description
        
        # Se não encontrar, tentar extrair do início do texto
        lines = text.split('\n')
        problem_text = ""
        for line in lines[10:]:  # Pular cabeçalho
            if line.strip() and not re.match(r'^(Número|Solicitante|Tel|Localização|Equipamento)', line):
                problem_text += line.strip() + " "
                if len(problem_text) > 500:  # Limitar tamanho
                    break
        
        return problem_text.strip() or "Problema não identificado no PDF"
    
    def _generate_solution(self, problem: str, system: str, full_text: str) -> str:
        """Gera solução baseada no problema identificado e sistema"""
        problem_lower = problem.lower()
        
        # Identificar tipo de problema
        problem_type = self._classify_problem_type(problem_lower)
        
        # Gerar solução baseada no tipo de problema e sistema
        solutions = {
            'senha': {
                'SGU': "1. Acessar o Sistema SGU como administrador\n2. Navegar até Gestão de Usuários\n3. Localizar o usuário solicitante\n4. Resetar senha temporária\n5. Orientar usuário a alterar senha no primeiro acesso\n6. Verificar se email corporativo está correto no cadastro\n7. Testar login com nova senha",
                'Tasy': "1. Acessar módulo de administração do Tasy\n2. Ir em Usuários e Senhas\n3. Selecionar usuário e resetar senha\n4. Gerar senha temporária\n5. Enviar instruções de alteração para o usuário",
                'default': "1. Verificar usuário no sistema de gestão\n2. Resetar senha temporária\n3. Validar email cadastrado\n4. Orientar troca de senha no primeiro acesso"
            },
            'acesso': {
                'SGU': "1. Acessar SGU como administrador\n2. Ir em Gestão de Usuários > Permissões\n3. Localizar usuário de referência (ex: gabrielly.batista)\n4. Copiar perfil de permissões para o usuário solicitante (ex: ruth.pasini)\n5. Aplicar permissões de alteração cadastral\n6. Validar acessos com o solicitante\n7. Documentar alterações realizadas no chamado",
                'Tasy': "1. Acessar administração do Tasy\n2. Configurar perfil de usuário\n3. Aplicar permissões necessárias\n4. Testar acessos",
                'default': "1. Verificar permissões necessárias\n2. Configurar perfil de usuário\n3. Aplicar acessos solicitados\n4. Validar funcionamento"
            },
            'email': {
                'default': "1. Verificar email cadastrado no sistema\n2. Atualizar para email corporativo correto\n3. Testar envio de email de recuperação\n4. Validar recebimento com usuário"
            },
            'parametrização': {
                'SGU': "1. Acessar SGU como administrador\n2. Localizar usuário de referência\n3. Exportar configurações de permissões\n4. Aplicar no usuário solicitante\n5. Testar funcionalidades\n6. Documentar configurações aplicadas",
                'default': "1. Analisar permissões necessárias\n2. Configurar perfil do usuário\n3. Aplicar parametrizações\n4. Validar funcionamento"
            },
            'sistema_indisponivel': {
                'default': "1. Verificar status dos serviços do sistema\n2. Checar conectividade de rede\n3. Validar serviços de banco de dados\n4. Reiniciar serviços se necessário\n5. Monitorar estabilidade\n6. Comunicar usuários sobre resolução"
            },
            'lentidão': {
                'default': "1. Verificar performance do servidor\n2. Analisar uso de recursos (CPU, memória)\n3. Checar conectividade de rede\n4. Revisar logs de sistema\n5. Otimizar consultas se necessário\n6. Monitorar melhorias"
            }
        }
        
        # Selecionar solução apropriada
        if problem_type in solutions:
            system_solutions = solutions[problem_type]
            if system in system_solutions:
                return system_solutions[system]
            else:
                return system_solutions.get('default', 'Solução específica não encontrada')
        
        # Solução genérica baseada no sistema
        return f"1. Analisar problema relatado no sistema {system}\n2. Verificar configurações e permissões\n3. Aplicar correções necessárias\n4. Testar funcionamento\n5. Validar com usuário solicitante"
    
    def _classify_problem_type(self, problem_text: str) -> str:
        """Classifica o tipo de problema baseado no texto"""
        for problem_type, pattern in self.problem_patterns.items():
            if re.search(pattern, problem_text, re.IGNORECASE):
                return problem_type
        
        return 'geral'
    
    def analyze_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, str]]:
        """Analisa múltiplos PDFs e retorna lista de casos"""
        cases = []
        for pdf_path in pdf_paths:
            try:
                case = self.analyze_pdf(pdf_path)
                cases.append(case)
                logging.info(f"PDF analisado com sucesso: {pdf_path}")
            except Exception as e:
                logging.error(f"Erro ao analisar PDF {pdf_path}: {str(e)}")
                continue
        
        return cases

# Função de conveniência para integração com o sistema principal
def analyze_os_pdf(pdf_path: str) -> Dict[str, str]:
    """Função para análise rápida de PDF de OS"""
    analyzer = PDFAnalyzer()
    return analyzer.analyze_pdf(pdf_path)