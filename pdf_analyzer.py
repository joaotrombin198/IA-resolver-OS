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
        
        # Padrões para identificar tipos de problemas comuns (em ordem de prioridade)
        self.problem_patterns = {
            'parametrizacao_permissoes': r'(?:parametrizar.*usuário.*com.*mesmas.*permissões|copiar.*permissões|mesmo.*permissões.*que|permissões.*alteração.*cadastral)',
            'liberacao_acesso': r'(?:liberação.*acesso|liberar.*acesso|solicita.*acesso|permissão.*para)',
            'evento_lancamento': r'(?:evento.*\d+.*lança|lançamento.*evento|impossibilitando.*lançar.*evento|evento.*não.*permite|problema.*evento.*\d+)',
            'configuracao_sistema': r'(?:configuração.*sistema|parametrização.*evento|cadastro.*evento|sistema.*não.*habilitado|campo.*não.*habilitado)',
            'competencia_fiscal': r'(?:competência.*\d{6}|competência.*fiscal|período.*fiscal|mês.*competência)',
            'pessoa_fisica_juridica': r'(?:pessoa.*física|pessoa.*jurídica|tipo.*pessoa|PF.*PJ|física.*jurídica)',
            'bug_sistema': r'(?:bug.*sistema|erro.*sistema|falha.*sistema|sistema.*com.*problema|não.*funciona.*corretamente)',
            'senha': r'(?:senha|password|redefinir|redefinição|esqueci|alteração.*senha|incorreta|provisória)(?!.*permiss)',
            'email': r'(?:e-mail|email|corporativo|correio|pandion)',
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
            
            # Extrair número da OS
            os_number = self._extract_os_number(pdf_text)
            
            # Identificar sistema
            system_type = self._identify_system(pdf_text)
            
            # Extrair descrição do problema
            problem_description = self._extract_problem_description(pdf_text)
            
            # Gerar solução baseada nos padrões identificados
            solution = self._generate_solution(problem_description, system_type, pdf_text)
            
            return {
                'os_number': os_number,
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
    
    def _extract_os_number(self, text: str) -> str:
        """Extrai o número da OS do cabeçalho do PDF"""
        # Procurar por padrão "Número" seguido do número da OS
        patterns = [
            r'Número\s+(\d+)',  # Padrão principal: "Número 693803"
            r'OS[\s#]*(\d+)',   # Alternativo: "OS 693803" ou "OS#693803"
            r'Ordem[\s\w]*\s+(\d+)'  # Alternativo: "Ordem de Serviço 693803"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                os_number = match.group(1).strip()
                logging.info(f"Número da OS extraído: {os_number}")
                return os_number
        
        logging.warning("Número da OS não encontrado no PDF")
        return None
    
    def _identify_system(self, text: str) -> str:
        """Identifica o sistema baseado no conteúdo do PDF"""
        text_lower = text.lower()
        
        for system, pattern in self.system_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return system
                
        return "Unknown"
    
    def _extract_problem_description(self, text: str) -> str:
        """Extrai a descrição do problema do campo 'Dano' ou 'Descrição'"""
        # Procurar por seção "Dano" ou "Descrição" - incluindo múltiplas linhas
        patterns = [
            r'Dano\s+(.+?)(?=\n\s*Execução|\n\s*Situação|\n\s*Históricos|\n\s*Impresso|$)',
            r'Descrição\s+(.+?)(?=\n\s*Dano|\n\s*Execução|\n\s*Situação|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                # Limpar texto preservando quebras de linha importantes
                description = re.sub(r'\n+', ' ', description)  # Múltiplas quebras em espaço
                description = re.sub(r'\s+', ' ', description)  # Múltiplos espaços em um
                
                # Incluir também a descrição curta se existir
                desc_match = re.search(r'Descrição\s+([^\n]+)', text, re.IGNORECASE)
                if desc_match and desc_match.group(1).strip() not in description:
                    short_desc = desc_match.group(1).strip()
                    description = f"{short_desc}. {description}"
                
                return description
        
        # Se não encontrar, tentar extrair informações relevantes
        lines = text.split('\n')
        problem_text = ""
        capturing = False
        
        for line in lines:
            line = line.strip()
            if re.match(r'(Descrição|Dano)', line, re.IGNORECASE):
                capturing = True
                continue
            elif capturing and re.match(r'(Execução|Situação|Históricos)', line, re.IGNORECASE):
                break
            elif capturing and line:
                problem_text += line + " "
                if len(problem_text) > 1000:  # Limite maior para problemas complexos
                    break
        
        return problem_text.strip() or "Problema não identificado no PDF"
    
    def _generate_solution(self, problem: str, system: str, full_text: str) -> str:
        """Gera solução baseada no problema identificado e sistema"""
        problem_lower = problem.lower()
        
        # Identificar tipo de problema
        problem_type = self._classify_problem_type(problem_lower)
        
        # Gerar solução baseada no tipo de problema e sistema
        solutions = {
            'evento_lancamento': {
                'SGU': "1. Acessar SGU como administrador com privilégios de sistema\n2. Ir em Configurações > Eventos > Cadastro de Eventos\n3. Localizar o evento específico (ex: Evento 655 - INSS)\n4. Verificar configurações do evento para a competência atual\n5. Validar se o campo 'Tipo de Pessoa' está habilitado para PF e PJ\n6. Verificar parâmetros da competência no módulo fiscal\n7. Analisar logs de erro do sistema para identificar bloqueios\n8. Testar lançamento do evento em ambiente de homologação\n9. Aplicar correções na configuração do evento se necessário\n10. Validar funcionalidade com usuário final\n11. Documentar solução aplicada e configurações alteradas",
                'default': "1. Identificar evento específico com problema\n2. Verificar configurações do evento no sistema\n3. Analisar parâmetros da competência\n4. Aplicar correções necessárias\n5. Testar funcionalidade\n6. Validar com usuário"
            },
            'configuracao_sistema': {
                'SGU': "1. Acessar SGU como administrador de sistema\n2. Ir em Configurações > Parâmetros Gerais\n3. Verificar configurações específicas do módulo afetado\n4. Revisar parâmetros de competência e período fiscal\n5. Validar configurações de eventos e lançamentos\n6. Verificar permissões de campos para tipos de pessoa\n7. Aplicar correções na parametrização\n8. Testar configurações em ambiente controlado\n9. Implementar correções em produção\n10. Validar funcionamento com casos de teste\n11. Documentar alterações realizadas",
                'default': "1. Analisar configurações atuais do sistema\n2. Identificar parâmetros incorretos\n3. Aplicar correções necessárias\n4. Testar funcionalidade\n5. Validar com usuário"
            },
            'parametrizacao_permissoes': {
                'SGU': "1. Acessar SGU 2.0 como administrador\n2. Ir em Gestão de Usuários > Permissões\n3. Localizar usuário de referência para copiar permissões\n4. Visualizar e exportar perfil de permissões de alteração cadastral\n5. Localizar usuário solicitante\n6. Aplicar as mesmas permissões de alteração cadastral\n7. Validar acessos às telas necessárias\n8. Testar funcionalidades com o usuário\n9. Documentar alterações realizadas no chamado",
                'Tasy': "1. Acessar administração do Tasy\n2. Localizar usuário modelo\n3. Copiar perfil de permissões\n4. Aplicar no usuário solicitante\n5. Testar funcionalidades\n6. Validar com usuário",
                'default': "1. Identificar usuário modelo para copiar permissões\n2. Exportar configurações de permissões\n3. Aplicar no usuário solicitante\n4. Validar funcionamento\n5. Documentar alterações"
            },
            'liberacao_acesso': {
                'SGU': "1. Acessar SGU como administrador\n2. Ir em Gestão de Usuários > Permissões\n3. Localizar usuário solicitante\n4. Analisar permissões necessárias para as telas/funcionalidades\n5. Aplicar liberações de acesso conforme solicitado\n6. Validar acessos com o solicitante\n7. Documentar alterações realizadas",
                'Tasy': "1. Acessar administração do Tasy\n2. Configurar permissões de usuário\n3. Liberar acessos solicitados\n4. Testar funcionalidades",
                'default': "1. Analisar acessos necessários\n2. Configurar permissões de usuário\n3. Liberar acessos solicitados\n4. Validar funcionamento"
            },
            'bug_sistema': {
                'SGU': "1. Documentar detalhadamente o bug identificado\n2. Reproduzir o problema em ambiente de teste\n3. Analisar logs de erro e sistema\n4. Verificar versão atual do SGU e patches aplicados\n5. Consultar base de conhecimento para problemas similares\n6. Aplicar hotfixes disponíveis se existirem\n7. Escalar para suporte técnico especializado se necessário\n8. Implementar workaround temporário se possível\n9. Testar solução aplicada\n10. Documentar correção para casos futuros",
                'default': "1. Documentar bug detalhadamente\n2. Reproduzir problema\n3. Analisar logs de sistema\n4. Aplicar correções disponíveis\n5. Escalar se necessário\n6. Implementar workaround temporário"
            },
            'senha': {
                'SGU': "1. Acessar o Sistema SGU como administrador\n2. Navegar até Gestão de Usuários\n3. Localizar o usuário solicitante\n4. Resetar senha temporária\n5. Orientar usuário a alterar senha no primeiro acesso\n6. Verificar se email corporativo está correto no cadastro\n7. Testar login com nova senha",
                'Tasy': "1. Acessar módulo de administração do Tasy\n2. Ir em Usuários e Senhas\n3. Selecionar usuário e resetar senha\n4. Gerar senha temporária\n5. Enviar instruções de alteração para o usuário",
                'default': "1. Verificar usuário no sistema de gestão\n2. Resetar senha temporária\n3. Validar email cadastrado\n4. Orientar troca de senha no primeiro acesso"
            },
            'email': {
                'default': "1. Verificar email cadastrado no sistema\n2. Atualizar para email corporativo correto\n3. Testar envio de email de recuperação\n4. Validar recebimento com usuário"
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
        """Classifica o tipo de problema baseado nos padrões (em ordem de prioridade)"""
        problem_lower = problem_text.lower()
        
        # Verificar em ordem de prioridade - os mais específicos primeiro
        for problem_type, pattern in self.problem_patterns.items():
            if re.search(pattern, problem_lower, re.IGNORECASE):
                logging.info(f"Problema identificado como: {problem_type} (padrão: {pattern})")
                return problem_type
        
        logging.warning(f"Problema não classificado, usando genérico. Texto: {problem_text[:100]}...")
        return 'generico'
    
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