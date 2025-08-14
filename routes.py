from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app
from models import Case, SolutionSuggestion
from ml_service import MLService
from case_service import CaseService
import logging

# Initialize services
ml_service = MLService()
case_service = CaseService()

@app.route('/')
def index():
    """Main page with problem input form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_problem():
    """Analyze problem and provide AI suggestions"""
    try:
        problem_description = request.form.get('problem_description', '').strip()
        
        if not problem_description:
            flash('Please enter a problem description.', 'error')
            return redirect(url_for('index'))
        
        # Get ML analysis and suggestions
        suggestion = ml_service.analyze_problem(problem_description)
        
        # Find similar cases
        similar_cases = case_service.find_similar_cases(problem_description, limit=5)
        suggestion.similar_cases = similar_cases
        
        return render_template('index.html', 
                             suggestion=suggestion, 
                             problem_description=problem_description)
        
    except Exception as e:
        logging.error(f"Error analyzing problem: {str(e)}")
        flash(f'Error analyzing problem: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard showing case statistics and recent cases"""
    try:
        stats = case_service.get_statistics()
        recent_cases = case_service.get_recent_cases(limit=10)
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_cases=recent_cases)
        
    except Exception as e:
        logging.error(f"Error loading dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', stats={}, recent_cases=[])

@app.route('/cases')
def list_cases():
    """List all cases with search functionality"""
    search_query = request.args.get('search', '').strip()
    system_filter = request.args.get('system', '')
    
    try:
        if search_query or system_filter:
            cases = case_service.search_cases(search_query, system_filter)
        else:
            cases = case_service.get_all_cases()
        
        systems = case_service.get_unique_systems()
        
        return render_template('dashboard.html', 
                             cases=cases, 
                             search_query=search_query,
                             system_filter=system_filter,
                             systems=systems)
        
    except Exception as e:
        logging.error(f"Error listing cases: {str(e)}")
        flash(f'Error loading cases: {str(e)}', 'error')
        return render_template('dashboard.html', cases=[], systems=[])

@app.route('/case/<int:case_id>')
def case_detail(case_id):
    """Show detailed view of a specific case"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            flash('Case not found.', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('case_detail.html', case=case)
        
    except Exception as e:
        logging.error(f"Error loading case {case_id}: {str(e)}")
        flash(f'Error loading case: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/add_case')
def add_case_form():
    """Show form to add a new case manually"""
    return render_template('add_case.html')

@app.route('/add_case', methods=['POST'])
def add_case():
    """Add a new case to the knowledge base"""
    try:
        problem_description = request.form.get('problem_description', '').strip()
        solution = request.form.get('solution', '').strip()
        system_type = request.form.get('system_type', 'Unknown').strip()
        
        if not problem_description or not solution:
            flash('Problem description and solution are required.', 'error')
            return render_template('add_case.html')
        
        case = case_service.add_case(problem_description, solution, system_type)
        
        # Retrain ML models with new case
        all_cases = case_service.get_all_cases()
        if len(all_cases) >= 5:  # Only retrain if we have enough cases
            ml_service.train_models(all_cases)
        
        flash(f'Case #{case.id} added successfully!', 'success')
        
        return redirect(url_for('case_detail', case_id=case.id))
        
    except Exception as e:
        logging.error(f"Error adding case: {str(e)}")
        flash(f'Error adding case: {str(e)}', 'error')
        return render_template('add_case.html')

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on solution effectiveness"""
    try:
        case_id = request.form.get('case_id', type=int)
        effectiveness = request.form.get('effectiveness', type=int)
        
        if not case_id or effectiveness is None:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        if effectiveness < 1 or effectiveness > 5:
            return jsonify({'error': 'Effectiveness must be between 1 and 5'}), 400
        
        success = case_service.add_feedback(case_id, effectiveness)
        
        if success:
            return jsonify({'message': 'Feedback submitted successfully'})
        else:
            return jsonify({'error': 'Case not found'}), 404
            
    except Exception as e:
        logging.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    try:
        stats = case_service.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml-info')
def api_ml_info():
    """API endpoint for ML model information"""
    try:
        ml_info = ml_service.get_model_info()
        return jsonify(ml_info)
    except Exception as e:
        logging.error(f"Error getting ML info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/cases/<int:case_id>/edit')
def edit_case_form(case_id):
    """Show form to edit an existing case"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            flash('Caso não encontrado.', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('edit_case.html', case=case)
        
    except Exception as e:
        logging.error(f"Error loading edit form for case {case_id}: {str(e)}")
        flash(f'Erro ao carregar formulário de edição: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/cases/<int:case_id>/edit', methods=['POST'])
def edit_case(case_id):
    """Update an existing case"""
    try:
        problem_description = request.form.get('problem_description', '').strip()
        solution = request.form.get('solution', '').strip()
        system_type = request.form.get('system_type', 'Unknown').strip()
        
        if not problem_description or not solution:
            flash('Descrição do problema e solução são obrigatórios.', 'error')
            return redirect(url_for('edit_case_form', case_id=case_id))
        
        success = case_service.update_case(case_id, problem_description, solution, system_type)
        
        if success:
            # Retrain ML models with updated cases
            all_cases = case_service.get_all_cases()
            if len(all_cases) >= 5:
                ml_service.train_models(all_cases)
            
            flash(f'Caso #{case_id} atualizado com sucesso!', 'success')
            return redirect(url_for('case_detail', case_id=case_id))
        else:
            flash('Caso não encontrado.', 'error')
            return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Error updating case {case_id}: {str(e)}")
        flash(f'Erro ao atualizar caso: {str(e)}', 'error')
        return redirect(url_for('edit_case_form', case_id=case_id))

@app.route('/cases/<int:case_id>/delete', methods=['POST'])
def delete_case(case_id):
    """Delete a case"""
    try:
        success = case_service.delete_case(case_id)
        
        if success:
            # Retrain ML models after deletion
            all_cases = case_service.get_all_cases()
            if len(all_cases) >= 5:
                ml_service.train_models(all_cases)
            
            flash(f'Caso #{case_id} excluído com sucesso!', 'success')
        else:
            flash('Caso não encontrado.', 'error')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Error deleting case {case_id}: {str(e)}")
        flash(f'Erro ao excluir caso: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/train-models', methods=['POST'])
def train_models():
    """Manually trigger ML model training"""
    try:
        all_cases = case_service.get_all_cases()
        if len(all_cases) < 5:
            flash('Necessário pelo menos 5 casos para treinar os modelos ML.', 'warning')
        else:
            success = ml_service.train_models(all_cases)
            if success:
                flash('Modelos ML treinados com sucesso!', 'success')
            else:
                flash('Falha ao treinar modelos ML. Verifique os logs para detalhes.', 'error')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Error training models: {str(e)}")
        flash(f'Erro ao treinar modelos: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/populate-sample-data', methods=['POST'])
def populate_sample_data():
    """Add sample cases for demonstration"""
    try:
        sample_cases = [
            {
                'problem': 'Sistema Tasy apresentando erro de conexão com banco de dados Oracle. Usuários não conseguem acessar módulo de prontuário eletrônico. Erro: ORA-12154 TNS could not resolve the connect identifier.',
                'solution': '1. Verificar conectividade de rede com servidor Oracle\n2. Validar configurações do tnsnames.ora\n3. Testar conexão usando sqlplus\n4. Reiniciar listener do Oracle se necessário\n5. Verificar logs do Tasy para detalhes adicionais\n6. Se problema persistir, abrir chamado para Nexdow',
                'system': 'Tasy'
            },
            {
                'problem': 'SGU não consegue processar admissões. Erro "Timeout na comunicação com base de dados" aparece ao tentar registrar novos pacientes. Módulo de gestão hospitalar indisponível.',
                'solution': '1. Verificar status dos serviços SGU no servidor\n2. Testar conectividade com banco de dados SGU\n3. Analisar logs de erro do SGU\n4. Verificar configurações de timeout\n5. Reiniciar serviços SGU se necessário\n6. Caso não resolva, escalar para Nexdow',
                'system': 'SGU'
            },
            {
                'problem': 'SGU Card não imprime carteirinhas de pacientes. Impressora conectada mas recebe dados corrompidos. Erro "Falha na geração de layout" no módulo de cartões.',
                'solution': '1. Verificar driver da impressora de cartões\n2. Testar impressão manual de arquivo teste\n3. Validar template de layout no SGU Card\n4. Verificar dados do paciente no sistema\n5. Limpar cache do módulo Card\n6. Se necessário, abrir chamado Nexdow para revisão do layout',
                'system': 'SGU Card'
            },
            {
                'problem': 'Autorizador não processa guias de consulta. Fila com 500+ autorizações pendentes. Erro "Falha na comunicação com operadora" em todas as tentativas.',
                'solution': '1. Verificar conectividade com APIs das operadoras\n2. Validar certificados digitais expirados\n3. Testar manualmente autorização de uma guia\n4. Verificar configurações de proxy/firewall\n5. Processar fila manualmente se urgente\n6. Contatar Nexdow para problemas de integração com operadoras',
                'system': 'Autorizador'
            },
            {
                'problem': 'Tasy módulo farmácia lento para dispensar medicamentos. Consulta de estoque demora mais de 2 minutos. Pacientes aguardando na fila da farmácia.',
                'solution': '1. Analisar performance de queries no módulo farmácia\n2. Verificar índices das tabelas de estoque\n3. Executar reorganização de índices\n4. Limpar dados antigos da tabela de logs\n5. Considerar aumento de memória do servidor\n6. Se problema persistir, solicitar análise Nexdow',
                'system': 'Tasy'
            },
            {
                'problem': 'Rede hospitalar com perda de pacotes na VLAN dos equipamentos médicos. Monitores cardíacos perdendo conexão intermitentemente. Setor UTI afetado.',
                'solution': '1. Verificar cabos de rede na UTI\n2. Analisar logs dos switches da VLAN médica\n3. Testar largura de banda disponível\n4. Verificar configurações QoS para tráfego médico\n5. Substituir cabos defeituosos se identificados\n6. Priorizar tráfego crítico nos switches',
                'system': 'Network'
            }
        ]
        
        added_count = 0
        for sample in sample_cases:
            case = case_service.add_case(
                problem_description=sample['problem'],
                solution=sample['solution'],
                system_type=sample['system']
            )
            added_count += 1
        
        # Train ML models with new cases
        all_cases = case_service.get_all_cases()
        ml_service.train_models(all_cases)
        
        flash(f'{added_count} casos de exemplo adicionados e modelos ML treinados!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Error adding sample data: {str(e)}")
        flash(f'Erro ao adicionar dados de exemplo: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
