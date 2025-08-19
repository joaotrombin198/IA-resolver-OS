"""
Formatador de Soluções - Transforma soluções em steps organizados
"""
import re
from typing import List, Dict

class SolutionFormatter:
    """Formatar soluções em etapas visualmente organizadas"""
    
    def __init__(self):
        # Padrões para identificar etapas
        self.step_patterns = [
            r'^\d+\.\s*(.+)$',  # "1. Fazer algo"
            r'^Step\s*\d+:\s*(.+)$',  # "Step 1: Fazer algo"
            r'^-\s*(.+)$',  # "- Fazer algo"
            r'^•\s*(.+)$',  # "• Fazer algo"
        ]
    
    def format_solution_to_steps(self, solution: str) -> List[Dict[str, str]]:
        """
        Converte solução em lista de etapas organizadas
        
        Returns:
            Lista de dicionários com 'step_number', 'description', 'icon'
        """
        if not solution or not solution.strip():
            return []
        
        # Dividir por linhas e processar
        lines = solution.strip().split('\n')
        steps = []
        current_step = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Tentar extrair etapa com número
            step_content = self._extract_step_content(line)
            if step_content:
                # Determinar ícone baseado no conteúdo
                icon = self._get_step_icon(step_content)
                
                steps.append({
                    'step_number': current_step,
                    'description': step_content,
                    'icon': icon
                })
                current_step += 1
            else:
                # Se não é uma etapa numerada, adicionar como continuação da anterior
                if steps:
                    steps[-1]['description'] += f" {line}"
                else:
                    # Primeira linha sem número, criar etapa
                    icon = self._get_step_icon(line)
                    steps.append({
                        'step_number': current_step,
                        'description': line,
                        'icon': icon
                    })
                    current_step += 1
        
        return steps
    
    def _extract_step_content(self, line: str) -> str:
        """Extrai o conteúdo da etapa removendo numeração"""
        for pattern in self.step_patterns:
            match = re.match(pattern, line)
            if match:
                return match.group(1).strip()
        return ""
    
    def _get_step_icon(self, content: str) -> str:
        """Determina ícone apropriado baseado no conteúdo da etapa"""
        content_lower = content.lower()
        
        # Ícones baseados em palavras-chave
        if any(word in content_lower for word in ['acessar', 'login', 'entrar']):
            return 'log-in'
        elif any(word in content_lower for word in ['navegar', 'ir para', 'abrir']):
            return 'navigation'
        elif any(word in content_lower for word in ['localizar', 'encontrar', 'procurar']):
            return 'search'
        elif any(word in content_lower for word in ['resetar', 'redefinir', 'alterar']):
            return 'refresh-cw'
        elif any(word in content_lower for word in ['verificar', 'validar', 'checar']):
            return 'check-circle'
        elif any(word in content_lower for word in ['testar', 'teste']):
            return 'play'
        elif any(word in content_lower for word in ['orientar', 'instruir', 'comunicar']):
            return 'message-circle'
        elif any(word in content_lower for word in ['documentar', 'registrar']):
            return 'file-text'
        elif any(word in content_lower for word in ['copiar', 'exportar']):
            return 'copy'
        elif any(word in content_lower for word in ['aplicar', 'configurar', 'parametrizar']):
            return 'settings'
        elif any(word in content_lower for word in ['monitorar', 'acompanhar']):
            return 'activity'
        elif any(word in content_lower for word in ['reiniciar', 'restart']):
            return 'power'
        else:
            return 'arrow-right'  # Ícone padrão
    
    def format_solution_html(self, solution: str) -> str:
        """Gera HTML formatado para as etapas da solução"""
        steps = self.format_solution_to_steps(solution)
        
        if not steps:
            return f'<p class="mb-0">{solution}</p>'
        
        html = '<div class="solution-steps">'
        
        for i, step in enumerate(steps):
            is_last = i == len(steps) - 1
            
            html += f'''
            <div class="step-item d-flex align-items-start mb-3 {'last-step' if is_last else ''}">
                <div class="step-indicator me-3">
                    <div class="step-number">
                        <i data-feather="{step['icon']}" class="step-icon"></i>
                        <span class="step-num">{step['step_number']}</span>
                    </div>
                    {'' if is_last else '<div class="step-line"></div>'}
                </div>
                <div class="step-content flex-grow-1">
                    <p class="mb-0">{step['description']}</p>
                </div>
            </div>'''
        
        html += '</div>'
        return html
    
    def format_ml_solution_compact(self, solution: str) -> str:
        """Gera HTML compacto para soluções na análise ML"""
        steps = self.format_solution_to_steps(solution)
        
        if not steps:
            return f'<span class="solution-text">{solution}</span>'
        
        # Se é só um passo, exibir como texto simples
        if len(steps) == 1:
            return f'<span class="solution-text">{steps[0]["description"]}</span>'
        
        # Para múltiplos passos, criar versão compacta
        html = '<div class="solution-compact">'
        html += f'<div class="solution-summary">{steps[0]["description"]}</div>'
        
        if len(steps) > 1:
            html += f'<div class="solution-more-steps">+{len(steps)-1} etapas adicionais</div>'
        
        html += '</div>'
        return html
    
    def get_step_count(self, solution: str) -> int:
        """Retorna número de etapas na solução"""
        steps = self.format_solution_to_steps(solution)
        return len(steps)

# Instância global para uso nos templates
solution_formatter = SolutionFormatter()