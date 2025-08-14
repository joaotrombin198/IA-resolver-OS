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

@app.route('/train-models', methods=['POST'])
def train_models():
    """Manually trigger ML model training"""
    try:
        all_cases = case_service.get_all_cases()
        if len(all_cases) < 5:
            flash('Need at least 5 cases to train ML models.', 'warning')
        else:
            success = ml_service.train_models(all_cases)
            if success:
                flash('ML models trained successfully!', 'success')
            else:
                flash('Failed to train ML models. Check logs for details.', 'error')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Error training models: {str(e)}")
        flash(f'Error training models: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/populate-sample-data', methods=['POST'])
def populate_sample_data():
    """Add sample cases for demonstration"""
    try:
        sample_cases = [
            {
                'problem': 'Sistema Tasy apresentando erro de conexão com banco de dados Oracle. Usuários não conseguem acessar módulo de prontuário eletrônico. Erro: ORA-12154 TNS could not resolve the connect identifier.',
                'solution': '1. Verificar conectividade de rede com servidor Oracle\n2. Validar configurações do tnsnames.ora\n3. Testar conexão usando sqlplus\n4. Reiniciar listener do Oracle se necessário\n5. Verificar logs do Tasy para detalhes adicionais',
                'system': 'Tasy'
            },
            {
                'problem': 'Lentidão extrema no sistema administrativo. Relatórios de RH demoram mais de 30 minutos para gerar. Sistema usando 95% da memória RAM do servidor.',
                'solution': '1. Verificar processos consumindo alta memória\n2. Analisar queries SQL executadas nos relatórios\n3. Otimizar índices no banco de dados\n4. Adicionar mais RAM ao servidor se necessário\n5. Implementar cache para relatórios frequentes',
                'system': 'Administrative'
            },
            {
                'problem': 'Falha na rede hospitalar. Switches principais não respondem. Erro intermitente de conectividade entre setores. VLAN 100 (setor emergência) completamente offline.',
                'solution': '1. Verificar status físico dos switches principais\n2. Testar cabos de uplink entre switches\n3. Revisar configurações VLAN no switch core\n4. Verificar logs de spanning-tree\n5. Executar diagnóstico de hardware nos switches',
                'system': 'Network'
            },
            {
                'problem': 'Banco de dados PostgreSQL com deadlocks frequentes. Backup noturno falha com erro "database is being accessed by other users". Performance muito baixa em consultas.',
                'solution': '1. Identificar queries que causam deadlock\n2. Revisar transações de longa duração\n3. Configurar timeout apropriado para conexões\n4. Executar VACUUM e ANALYZE nas tabelas\n5. Agendar backup em horário de menor uso',
                'system': 'Database'
            },
            {
                'problem': 'Servidor de aplicação Apache Tomcat reiniciando automaticamente. Logs mostram OutOfMemoryError: Java heap space. Aplicações web ficam indisponíveis por períodos.',
                'solution': '1. Aumentar heap size do Java (-Xmx parameter)\n2. Analisar vazamentos de memória na aplicação\n3. Configurar monitoramento JVM\n4. Otimizar garbage collection\n5. Implementar balanceamento de carga se necessário',
                'system': 'Application Server'
            },
            {
                'problem': 'Sistema EMR não sincroniza dados entre unidades. Erro de autenticação HL7. Mensagens ficam na fila sem processar.',
                'solution': '1. Verificar configurações HL7 MLLP\n2. Validar certificados de autenticação\n3. Testar conectividade entre interfaces\n4. Limpar fila de mensagens pendentes\n5. Reconfigurar roteamento de mensagens',
                'system': 'Healthcare'
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
