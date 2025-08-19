from flask import render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app import app
from models import Case, SolutionSuggestion
from ml_service import MLService
from case_service import CaseService
from file_processor import FileProcessor
from pdf_analyzer import PDFAnalyzer
import logging
import os
import tempfile
from datetime import datetime, timedelta

# Initialize services
ml_service = MLService()
case_service = CaseService()
file_processor = FileProcessor()
pdf_analyzer = PDFAnalyzer()

@app.route('/')
def index():
    """Main page with problem input form"""
    try:
        recent_cases = case_service.get_recent_cases(limit=6)
        return render_template('index.html', recent_cases=recent_cases)
    except Exception as e:
        logging.error(f"Error loading recent cases: {str(e)}")
        return render_template('index.html', recent_cases=[])

@app.route('/analyze', methods=['POST'])
def analyze_problem():
    """Analyze problem and provide AI suggestions"""
    try:
        problem_description = request.form.get('problem_description', '').strip()
        
        if not problem_description:
            flash('Please enter a problem description.', 'error')
            return redirect(url_for('index'))
        
        # Find similar cases first
        similar_cases = case_service.find_similar_cases(problem_description, limit=5)
        
        # Get ML analysis and suggestions with similar cases priority
        suggestion = ml_service.analyze_problem(problem_description, similar_cases)
        suggestion.similar_cases = similar_cases
        
        # Get recent cases for reference
        recent_cases = case_service.get_recent_cases(limit=6)
        
        return render_template('index.html', 
                             suggestion=suggestion, 
                             problem_description=problem_description,
                             recent_cases=recent_cases)
        
    except Exception as e:
        logging.error(f"Error analyzing problem: {str(e)}")
        flash(f'Error analyzing problem: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard showing analytics and system overview"""
    try:
        stats = case_service.get_statistics()
        return render_template('dashboard.html', stats=stats)
        
    except Exception as e:
        logging.error(f"Error loading dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', stats={})

@app.route('/recent-cases')
def recent_cases():
    """Page dedicated to recent cases with search and pagination"""
    search_query = request.args.get('search', '').strip()
    system_filter = request.args.get('system', '')
    sort_by = request.args.get('sort', 'recent')
    page = int(request.args.get('page', 1))
    per_page = 30  # Cases per page
    
    try:
        # Get all cases first
        if search_query or system_filter:
            all_cases = case_service.search_cases(search_query, system_filter)
        else:
            all_cases = case_service.get_all_cases()
        
        # Apply sorting
        if sort_by == 'oldest':
            all_cases = sorted(all_cases, key=lambda x: x.created_at or datetime.min)
        elif sort_by == 'system':
            all_cases = sorted(all_cases, key=lambda x: x.system_type)
        else:  # recent (default)
            all_cases = sorted(all_cases, key=lambda x: x.created_at or datetime.min, reverse=True)
        
        # Calculate pagination
        total_cases = len(all_cases)
        total_pages = (total_cases + per_page - 1) // per_page if total_cases > 0 else 1
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        cases = all_cases[start_idx:end_idx]
        
        # Pagination info
        has_prev = page > 1
        has_next = page < total_pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None
        
        # Get additional stats for the page
        stats = case_service.get_statistics()
        systems = case_service.get_unique_systems()
        
        # Quick stats for this page
        today_cases = len([c for c in all_cases if c.created_at and c.created_at.date() == datetime.now().date()]) if all_cases else 0
        week_cases = len([c for c in all_cases if c.created_at and c.created_at >= datetime.now() - timedelta(days=7)]) if all_cases else 0
        with_feedback = len([c for c in all_cases if c.effectiveness_score is not None]) if all_cases else 0
        
        return render_template('recent_cases.html',
                             cases=cases,
                             search_query=search_query,
                             system_filter=system_filter,
                             sort_by=sort_by,
                             systems=systems,
                             # Pagination
                             current_page=page,
                             total_pages=total_pages,
                             total_cases=total_cases,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_page=prev_page,
                             next_page=next_page,
                             # Quick stats
                             today_cases=today_cases,
                             week_cases=week_cases,
                             with_feedback=with_feedback)
        
    except Exception as e:
        logging.error(f"Error loading recent cases: {str(e)}")
        flash(f'Error loading cases: {str(e)}', 'error')
        return render_template('recent_cases.html', cases=[], systems=[], total_cases=0, total_pages=1, current_page=1, has_prev=False, has_next=False)

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

@app.route('/cases/<int:case_id>')
def view_case(case_id):
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
        system_type = request.form.get('system_type', 'Desconhecido').strip()
        custom_system = request.form.get('custom_system', '').strip()
        
        # Se selecionou "Outros", usar o sistema customizado
        if system_type == 'Outros' and custom_system:
            system_type = custom_system
        
        if not problem_description or not solution:
            flash('Descrição do problema e solução são obrigatórias.', 'error')
            return render_template('add_case.html')
        
        case = case_service.add_case(problem_description, solution, system_type)
        
        # Retrain ML models with new case
        all_cases = case_service.get_all_cases()
        if len(all_cases) >= 5:  # Only retrain if we have enough cases
            ml_service.train_models(all_cases)
        
        flash(f'Case #{case.id} added successfully!', 'success')
        
        return redirect(url_for('view_case', case_id=case.id))
        
    except Exception as e:
        logging.error(f"Error adding case: {str(e)}")
        flash(f'Error adding case: {str(e)}', 'error')
        return render_template('add_case.html')

@app.route('/cases/<int:case_id>/feedback')
def case_feedback_form(case_id):
    """Show detailed feedback form for a specific case"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            flash('Caso não encontrado.', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('case_feedback.html', case=case)
        
    except Exception as e:
        logging.error(f"Error loading feedback form for case {case_id}: {str(e)}")
        flash(f'Erro ao carregar formulário de feedback: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/cases/<int:case_id>/feedback', methods=['POST'])
def add_case_feedback(case_id):
    """Add detailed feedback to a case"""
    try:
        effectiveness_score = request.form.get('effectiveness_score', type=int)
        resolution_method = request.form.get('resolution_method', '').strip()
        custom_solution = request.form.get('custom_solution', '').strip()
        
        if not effectiveness_score or effectiveness_score < 1 or effectiveness_score > 5:
            flash('Avaliação deve ser entre 1 e 5 estrelas.', 'error')
            return redirect(url_for('case_feedback_form', case_id=case_id))
        
        if not resolution_method:
            flash('Selecione como o problema foi resolvido.', 'error')
            return redirect(url_for('case_feedback_form', case_id=case_id))
        
        success = case_service.add_case_feedback(case_id, effectiveness_score, resolution_method, custom_solution)
        
        if success:
            flash('Feedback adicionado com sucesso!', 'success')
            return redirect(url_for('view_case', case_id=case_id))
        else:
            flash('Caso não encontrado.', 'error')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        logging.error(f"Error adding feedback to case {case_id}: {str(e)}")
        flash(f'Erro ao adicionar feedback: {str(e)}', 'error')
        return redirect(url_for('case_feedback_form', case_id=case_id))

@app.route('/submit-case-feedback', methods=['POST'])
def submit_case_feedback():
    """Submit feedback on solution effectiveness"""
    try:
        case_id = request.form.get('case_id', type=int)
        effectiveness = request.form.get('effectiveness', type=int)
        
        if not case_id or effectiveness is None:
            return jsonify({'error': 'Case ID e effectiveness são obrigatórios'}), 400
        
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

@app.route('/convert-to-case', methods=['POST'])
def convert_suggestion_to_case():
    """Convert an ML suggestion to a permanent case"""
    try:
        problem_description = request.form.get('problem_description', '').strip()
        solution = request.form.get('solution', '').strip()
        system_type = request.form.get('system_type', 'Unknown').strip()
        
        if not problem_description or not solution:
            flash('Descrição do problema e solução são obrigatórias.', 'error')
            return redirect(url_for('index'))
        
        # Add the case
        case = case_service.add_case(problem_description, solution, system_type)
        
        # Retrain ML models with new case
        all_cases = case_service.get_all_cases()
        if len(all_cases) >= 5:
            ml_service.train_models(all_cases)
        
        flash(f'✅ Caso #{case.id} criado com sucesso! Obrigado por contribuir para a base de conhecimento.', 'success')
        return redirect(url_for('view_case', case_id=case.id))
        
    except Exception as e:
        logging.error(f"Error converting suggestion to case: {str(e)}")
        flash(f'Erro ao criar caso: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze-os-pdf')
def analyze_os_pdf_form():
    """Formulário para upload e análise de PDFs de Ordem de Serviço"""
    return render_template('analyze_os_pdf.html')

@app.route('/analyze-os-pdf', methods=['POST'])
def analyze_os_pdf():
    """Analisa múltiplos PDFs de OS e extrai automaticamente problema e solução"""
    try:
        if 'os_pdf_files' not in request.files:
            flash('Nenhum arquivo foi selecionado.', 'error')
            return redirect(url_for('analyze_os_pdf_form'))
        
        files = request.files.getlist('os_pdf_files')
        if not files or all(file.filename == '' for file in files):
            flash('Nenhum arquivo foi selecionado.', 'error')
            return redirect(url_for('analyze_os_pdf_form'))
        
        # Filtrar apenas arquivos PDF válidos
        valid_files = []
        for file in files:
            if file.filename and file.filename.lower().endswith('.pdf'):
                valid_files.append(file)
        
        if not valid_files:
            flash('Nenhum arquivo PDF válido foi encontrado.', 'error')
            return redirect(url_for('analyze_os_pdf_form'))
        
        processed_cases = []
        errors = []
        
        # Processar cada PDF
        for file in valid_files:
            try:
                # Salvar arquivo temporariamente
                filename = secure_filename(file.filename)
                temp_path = os.path.join(tempfile.gettempdir(), filename)
                file.save(temp_path)
                
                try:
                    # Analisar PDF com o sistema de ML interno
                    analysis_result = pdf_analyzer.analyze_pdf(temp_path)
                    
                    # Salvar automaticamente como novo caso (sempre)
                    case = case_service.add_case(
                        analysis_result['problem_description'],
                        analysis_result['solution'],
                        analysis_result['system_type']
                    )
                    
                    processed_cases.append({
                        'filename': filename,
                        'case_id': case.id,
                        'system_type': analysis_result['system_type']
                    })
                    
                    logging.info(f"PDF {filename} processado com sucesso - Caso #{case.id}")
                
                finally:
                    # Limpar arquivo temporário
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except Exception as e:
                error_msg = f"Erro ao processar {file.filename}: {str(e)}"
                errors.append(error_msg)
                logging.error(error_msg)
        
        # Retreinar ML se temos casos suficientes
        if processed_cases:
            all_cases = case_service.get_all_cases()
            if len(all_cases) >= 5:
                ml_service.train_models(all_cases)
        
        # Gerar mensagens de feedback
        success_count = len(processed_cases)
        error_count = len(errors)
        
        if success_count > 0:
            if success_count == 1:
                case = processed_cases[0]
                flash(f'✅ PDF "{case["filename"]}" analisado e Caso #{case["case_id"]} criado automaticamente!', 'success')
                return redirect(url_for('view_case', case_id=case['case_id']))
            else:
                flash(f'✅ {success_count} PDFs processados com sucesso! {error_count} erro(s) encontrado(s).', 'success')
                return render_template('batch_analysis_result.html', 
                                     processed_cases=processed_cases,
                                     errors=errors)
        else:
            flash(f'❌ Nenhum PDF foi processado com sucesso. {error_count} erro(s) encontrado(s).', 'error')
            for error in errors[:3]:  # Mostrar apenas os primeiros 3 erros
                flash(error, 'error')
            return redirect(url_for('analyze_os_pdf_form'))
    
    except Exception as e:
        logging.error(f"Erro geral ao processar PDFs: {str(e)}")
        flash(f'Erro ao processar PDFs: {str(e)}', 'error')
        return redirect(url_for('analyze_os_pdf_form'))

@app.route('/save-os-analysis', methods=['POST'])
def save_os_analysis():
    """Salva resultado da análise de PDF como novo caso"""
    try:
        problem_description = request.form.get('problem_description', '').strip()
        solution = request.form.get('solution', '').strip()
        system_type = request.form.get('system_type', 'Unknown').strip()
        
        if not problem_description or not solution:
            flash('Descrição do problema e solução são obrigatórias.', 'error')
            return redirect(url_for('analyze_os_pdf_form'))
        
        # Criar novo caso
        case = case_service.add_case(problem_description, solution, system_type)
        
        # Retreinar ML com novo caso
        all_cases = case_service.get_all_cases()
        if len(all_cases) >= 5:
            ml_service.train_models(all_cases)
        
        flash(f'✅ Caso #{case.id} criado com sucesso a partir da análise do PDF!', 'success')
        return redirect(url_for('view_case', case_id=case.id))
        
    except Exception as e:
        logging.error(f"Erro ao salvar análise de OS: {str(e)}")
        flash(f'Erro ao salvar caso: {str(e)}', 'error')
        return redirect(url_for('analyze_os_pdf_form'))

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
            return redirect(url_for('view_case', case_id=case_id))
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

@app.route('/delete_all_cases', methods=['POST'])
def delete_all_cases():
    """Delete all cases from the system"""
    try:
        # Get current case count for logging
        current_cases = case_service.get_all_cases()
        case_count = len(current_cases)
        
        if case_count == 0:
            flash('Nenhum caso encontrado para remover.', 'info')
            return redirect(url_for('recent_cases'))
        
        # Delete all cases
        success_count = case_service.delete_all_cases()
        
        if success_count > 0:
            flash(f'✅ Sucesso: {success_count} casos foram removidos permanentemente do sistema.', 'success')
            logging.warning(f"BULK DELETE: {success_count} cases deleted by user")
            
            # Clear ML models since all training data is gone
            try:
                ml_service.is_trained = False
                logging.info("ML models reset after bulk delete")
            except:
                pass
        else:
            flash('Erro: Nenhum caso foi removido. Tente novamente.', 'error')
            
    except Exception as e:
        logging.error(f"Error in bulk delete operation: {str(e)}")
        flash('Erro crítico durante remoção em massa. Contate o administrador.', 'error')
    
    return redirect(url_for('recent_cases'))

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

@app.route('/ml-learning-info')
def ml_learning_info():
    """Show ML learning insights and effectiveness analysis"""
    try:
        # Get comprehensive model information
        model_info = ml_service.get_model_info()
        
        # Get learning insights
        learning_insights = ml_service.get_learning_insights()
        
        return render_template('ml_learning_info.html', 
                             model_info=model_info,
                             learning_insights=learning_insights)
        
    except Exception as e:
        logging.error(f"Error getting ML learning info: {str(e)}")
        flash(f'Erro ao carregar informações de aprendizado: {str(e)}', 'error')
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

@app.route('/upload-cases')
def upload_cases_form():
    """Show form to upload cases from files"""
    return render_template('upload_cases.html')

@app.route('/upload-cases', methods=['POST'])
def upload_cases():
    """Process uploaded file with cases"""
    try:
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(url_for('upload_cases_form'))
        
        file = request.files['file']
        file_type = request.form.get('file_type')
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(url_for('upload_cases_form'))
        
        # Import required libraries
        import pandas as pd
        import PyPDF2
        import io
        from flask import current_app
        
        cases_added = 0
        
        if file_type == 'excel':
            # Process Excel/CSV file
            try:
                if file.filename and file.filename.endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(file.read()), encoding='utf-8')
                else:
                    df = pd.read_excel(io.BytesIO(file.read()))
                
                problem_col = request.form.get('problem_column', 'Problema')
                solution_col = request.form.get('solution_column', 'Solução')
                system_col = request.form.get('system_column', 'Sistema')
                
                for _, row in df.iterrows():
                    problem_val = row.get(problem_col)
                    solution_val = row.get(solution_col)
                    if (problem_val is not None and pd.notna(problem_val) and 
                        solution_val is not None and pd.notna(solution_val)):
                        case = case_service.add_case(
                            problem_description=str(problem_val),
                            solution=str(solution_val),
                            system_type=str(row.get(system_col, 'Unknown'))
                        )
                        cases_added += 1
                        
            except Exception as e:
                flash(f'Erro ao processar planilha: {str(e)}', 'error')
                return redirect(url_for('upload_cases_form'))
        
        elif file_type == 'pdf':
            # Process PDF file
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # Simple text processing for PDF (basic implementation)
                lines = text.split('\n')
                current_problem = ""
                current_solution = ""
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Simple heuristics to identify problem/solution pairs
                    if any(word in line.lower() for word in ['problema:', 'erro:', 'issue:', 'falha:']):
                        if current_problem and current_solution:
                            case = case_service.add_case(
                                problem_description=current_problem,
                                solution=current_solution,
                                system_type='Unknown'
                            )
                            cases_added += 1
                        current_problem = line
                        current_solution = ""
                    elif any(word in line.lower() for word in ['solução:', 'resolução:', 'fix:', 'correção:']):
                        current_solution = line
                    elif current_solution and line:
                        current_solution += " " + line
                
                # Add last case
                if current_problem and current_solution:
                    case = case_service.add_case(
                        problem_description=current_problem,
                        solution=current_solution,
                        system_type='Unknown'
                    )
                    cases_added += 1
                    
            except Exception as e:
                flash(f'Erro ao processar PDF: {str(e)}', 'error')
                return redirect(url_for('upload_cases_form'))
        
        if cases_added > 0:
            # Retrain ML models with new cases
            all_cases = case_service.get_all_cases()
            if len(all_cases) >= 5:
                ml_service.train_models(all_cases)
            
            flash(f'{cases_added} casos adicionados com sucesso!', 'success')
        else:
            flash('Nenhum caso válido encontrado no arquivo.', 'warning')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logging.error(f"Error uploading cases: {str(e)}")
        flash(f'Erro ao processar arquivo: {str(e)}', 'error')
        return redirect(url_for('upload_cases_form'))

@app.route('/download-template')
def download_template():
    """Download Excel template for case upload"""
    try:
        import pandas as pd
        import io
        
        # Create sample data
        sample_data = {
            'Problema': [
                'Sistema Tasy apresentando lentidão extrema',
                'SGU não consegue processar admissões',
                'Autorizador rejeitando guias válidas'
            ],
            'Solução': [
                'Reiniciar serviço do Tasy e limpar cache',
                'Verificar conectividade com banco SGU',
                'Atualizar certificados digitais'
            ],
            'Sistema': ['Tasy', 'SGU', 'Autorizador']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Casos', index=False)
        
        output.seek(0)
        
        from flask import send_file
        return send_file(
            output,
            as_attachment=True,
            download_name='template_casos.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logging.error(f"Error creating template: {str(e)}")
        flash(f'Erro ao gerar template: {str(e)}', 'error')
        return redirect(url_for('upload_cases_form'))

@app.route('/systems')
def manage_systems():
    """Manage system types"""
    try:
        # Get system usage statistics
        all_cases = case_service.get_all_cases()
        system_stats = {}
        
        for case in all_cases:
            system = case.system_type
            if system not in system_stats:
                system_stats[system] = {
                    'name': system,
                    'category': 'Healthcare' if system in ['Tasy', 'SGU', 'SGU Card', 'Autorizador'] else 'Other',
                    'case_count': 0,
                    'last_used': None
                }
            system_stats[system]['case_count'] += 1
            if not system_stats[system]['last_used'] or case.created_at > system_stats[system]['last_used']:
                system_stats[system]['last_used'] = case.created_at
        
        # Get custom systems from config
        from flask import current_app
        custom_systems = current_app.config.get('CUSTOM_SYSTEMS', [])
        
        # Merge with usage stats
        all_systems = []
        for system_name, stats in system_stats.items():
            all_systems.append(stats)
        
        # Add custom systems that haven't been used
        for custom in custom_systems:
            if custom['name'] not in system_stats:
                custom['case_count'] = 0
                custom['last_used'] = None
                all_systems.append(custom)
        
        return render_template('manage_systems.html', systems=all_systems)
        
    except Exception as e:
        logging.error(f"Error loading systems: {str(e)}")
        flash(f'Erro ao carregar sistemas: {str(e)}', 'error')
        return render_template('manage_systems.html', systems=[])

@app.route('/systems/add', methods=['POST'])
def add_system():
    """Add new system type"""
    try:
        system_name = request.form.get('system_name', '').strip()
        system_category = request.form.get('system_category', 'Other')
        system_description = request.form.get('system_description', '').strip()
        
        if not system_name:
            flash('Nome do sistema é obrigatório.', 'error')
            return redirect(url_for('manage_systems'))
        
        # Get current custom systems
        from flask import current_app
        custom_systems = current_app.config.get('CUSTOM_SYSTEMS', [])
        
        # Check if system already exists
        if any(s['name'].lower() == system_name.lower() for s in custom_systems):
            flash('Sistema já cadastrado.', 'error')
            return redirect(url_for('manage_systems'))
        
        # Add new system
        new_system = {
            'name': system_name,
            'category': system_category,
            'description': system_description
        }
        custom_systems.append(new_system)
        current_app.config['CUSTOM_SYSTEMS'] = custom_systems
        
        flash(f'Sistema "{system_name}" adicionado com sucesso!', 'success')
        return redirect(url_for('manage_systems'))
        
    except Exception as e:
        logging.error(f"Error adding system: {str(e)}")
        flash(f'Erro ao adicionar sistema: {str(e)}', 'error')
        return redirect(url_for('manage_systems'))

@app.route('/tutorial')
def tutorial():
    """Show tutorial and documentation"""
    return render_template('tutorial.html')



@app.route('/feedback', methods=['POST'])
def feedback():
    """Process detailed feedback from users"""
    try:
        from datetime import datetime
        import json
        
        # Log received data for debugging
        logging.info(f"Feedback form data: {dict(request.form)}")
        
        # Get form data
        score = request.form.get('score', type=int)
        problem_description = request.form.get('problem_description', '')
        comments = request.form.get('comments', '')
        good_aspects = request.form.get('good_aspects', '[]')
        improvements = request.form.get('improvements', '[]')
        suggestion_ratings = request.form.get('suggestion_ratings', '{}')
        
        # Validate required data
        if score is None:
            return jsonify({
                'success': False,
                'message': 'Score é obrigatório'
            }), 400
        
        # Parse JSON strings
        try:
            good_aspects_list = json.loads(good_aspects)
            improvements_list = json.loads(improvements)
            suggestion_ratings_dict = json.loads(suggestion_ratings)
        except json.JSONDecodeError:
            good_aspects_list = []
            improvements_list = []
            suggestion_ratings_dict = {}
        
        # Log feedback for analysis (in a real system, this would go to a database)
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'problem_description': problem_description[:200],  # Truncate for privacy
            'good_aspects': good_aspects_list,
            'improvements': improvements_list,
            'suggestion_ratings': suggestion_ratings_dict,
            'comments': comments,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Save feedback to database for ML learning
        try:
            from models import AnalysisFeedback
            from app import db
            import json
            
            analysis_feedback = AnalysisFeedback()
            analysis_feedback.problem_description = problem_description
            analysis_feedback.overall_score = score
            analysis_feedback.suggestion_ratings = json.dumps(suggestion_ratings_dict)
            analysis_feedback.good_aspects = json.dumps(good_aspects_list)
            analysis_feedback.improvements = json.dumps(improvements_list)
            analysis_feedback.comments = comments
            
            db.session.add(analysis_feedback)
            db.session.commit()
            
            logging.info(f"Saved analysis feedback to database: score={score}")
            
            # Trigger ML model improvement based on feedback
            ml_service.process_analysis_feedback(analysis_feedback)
            
        except Exception as e:
            logging.error(f"Error saving analysis feedback: {str(e)}")
        
        # Log the feedback for immediate debugging
        logging.info(f"User Feedback Received: {feedback_data}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback processado com sucesso!'
        })
        
    except Exception as e:
        logging.error(f"Error processing feedback: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao processar feedback'
        }), 500

@app.route('/admin/feedbacks')
def view_feedbacks():
    """View all feedback data for system improvement"""
    try:
        from models import AnalysisFeedback, CaseFeedback
        
        # Get analysis feedbacks (from AI suggestions)
        analysis_feedbacks = AnalysisFeedback.query.order_by(AnalysisFeedback.created_at.desc()).limit(50).all()
        
        # Get case feedbacks (from individual cases)
        case_feedbacks = db.session.query(CaseFeedback, Case).join(Case).order_by(CaseFeedback.created_at.desc()).limit(50).all()
        
        # Calculate feedback statistics
        total_analysis_feedbacks = AnalysisFeedback.query.count()
        avg_analysis_score = db.session.query(db.func.avg(AnalysisFeedback.overall_score)).scalar() or 0
        
        total_case_feedbacks = CaseFeedback.query.count()
        avg_case_score = db.session.query(db.func.avg(CaseFeedback.effectiveness_score)).scalar() or 0
        
        feedback_stats = {
            'total_analysis_feedbacks': total_analysis_feedbacks,
            'avg_analysis_score': round(avg_analysis_score, 1),
            'total_case_feedbacks': total_case_feedbacks,
            'avg_case_score': round(avg_case_score, 1)
        }
        
        return render_template('admin_feedbacks.html', 
                             analysis_feedbacks=analysis_feedbacks,
                             case_feedbacks=case_feedbacks,
                             feedback_stats=feedback_stats)
        
    except Exception as e:
        logging.error(f"Error viewing feedbacks: {str(e)}")
        flash(f'Erro ao carregar feedbacks: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Import additional feedback routes
try:
    import routes_analysis_feedback
    logging.info("Analysis feedback routes loaded successfully")
except ImportError as e:
    logging.warning(f"Could not import analysis feedback routes: {e}")

