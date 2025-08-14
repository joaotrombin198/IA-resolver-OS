# OS Assistant - Documentação Completa do Sistema

## Visão Geral

O OS Assistant é um sistema de suporte técnico baseado em machine learning, projetado para diagnosticar e resolver problemas em múltiplos sistemas (especialmente sistemas hospitalares brasileiros como Tasy, SGU, SGU Card e Autorizador). O sistema funciona como um "mentor digital" que analisa descrições de problemas e sugere soluções baseadas em casos históricos.

## Arquitetura do Sistema

### Estrutura de Diretórios

```
OS-Assistant/
├── app.py                 # Configuração principal do Flask
├── main.py                # Ponto de entrada da aplicação
├── models.py              # Modelos de dados (SQLAlchemy)
├── routes.py              # Rotas e endpoints da aplicação
├── case_service.py        # Serviço para gerenciamento de casos
├── ml_service.py          # Serviço de machine learning
├── file_processor.py      # Processamento de arquivos de importação
├── static/                # Arquivos estáticos (CSS, JS)
│   ├── style.css
│   └── script.js
├── templates/             # Templates HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── add_case.html
│   └── ...
├── ml_models/             # Modelos de ML treinados (pickle)
│   ├── system_classifier.pkl
│   ├── label_encoder.pkl
│   └── metadata.pkl
└── attached_assets/       # Arquivos anexados pelos usuários
```

### Tecnologias Utilizadas

**Backend:**
- **Flask**: Framework web principal
- **PostgreSQL**: Banco de dados principal para persistência
- **SQLAlchemy**: ORM para interação com banco de dados
- **Scikit-learn**: Machine learning e processamento de texto
- **Pandas**: Manipulação de dados e importação de planilhas
- **Gunicorn**: Servidor WSGI para produção

**Frontend:**
- **Bootstrap**: Framework CSS responsivo com tema escuro
- **Feather Icons**: Biblioteca de ícones
- **JavaScript**: Funcionalidades interativas (validação, busca, confirmações)

**Machine Learning:**
- **TF-IDF Vectorization**: Análise de similaridade de texto
- **Support Vector Machine (SVM)**: Classificação de tipos de sistema
- **Naive Bayes**: Classificação complementar
- **Cosine Similarity**: Busca de casos similares

## Banco de Dados

### Localização e Configuração

O sistema utiliza **PostgreSQL** como banco de dados principal, configurado automaticamente no ambiente Replit:

**Variáveis de Ambiente:**
- `DATABASE_URL`: URL completa de conexão
- `PGHOST`: Host do banco de dados
- `PGPORT`: Porta (padrão: 5432)
- `PGUSER`: Usuário do banco
- `PGPASSWORD`: Senha do banco
- `PGDATABASE`: Nome do banco de dados

### Estrutura das Tabelas

#### Tabela `cases`
```sql
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    problem_description TEXT NOT NULL,
    solution TEXT NOT NULL,
    system_type VARCHAR(100) DEFAULT 'Unknown',
    created_at TIMESTAMP DEFAULT NOW(),
    effectiveness_score FLOAT,
    feedback_count INTEGER DEFAULT 0,
    tags VARCHAR(500) DEFAULT ''
);
```

#### Tabela `case_feedbacks`
```sql
CREATE TABLE case_feedbacks (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    effectiveness_score INTEGER NOT NULL,
    resolution_method VARCHAR(50) DEFAULT '',
    custom_solution TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Backup de Dados

O sistema mantém dois níveis de armazenamento:
1. **Principal**: PostgreSQL para persistência completa
2. **Fallback**: Armazenamento em memória (temporário) em caso de falha do banco

## Funcionalidades Principais

### 1. Análise de Problemas
- Entrada de descrição de problema via interface web
- Análise automática usando ML para detectar tipo de sistema
- Geração de sugestões de solução baseadas em padrões históricos
- Busca de casos similares usando TF-IDF e similaridade coseno

### 2. Gerenciamento de Casos (CRUD Completo)
- **Criar**: Adição de novos casos via formulário ou importação
- **Ler**: Visualização de casos individuais e listagem completa
- **Atualizar**: Edição de casos existentes
- **Deletar**: Remoção de casos com confirmação

### 3. Importação de Dados
Suporte para múltiplos formatos:
- **Excel (.xlsx, .xls)**: Formato preferido
- **CSV**: Dados tabulares
- **TXT**: Texto estruturado
- **PDF**: Extração de texto (quando PyPDF2 disponível)

#### Formato de Importação Esperado
Para arquivos Excel/CSV, as colunas devem ser nomeadas (case-insensitive):
- **Problema/Problem**: Descrição detalhada do problema
- **Solução/Solution**: Solução aplicada
- **Sistema/System**: Tipo de sistema afetado

### 4. Machine Learning Interno
- **100% Offline**: Sem dependências de APIs externas
- **Classificação Automática**: Detecção de tipo de sistema
- **Aprendizado Contínuo**: Modelos se adaptam com novos casos
- **Feedback Loop**: Melhoria baseada em efetividade reportada

### 5. Dashboard e Estatísticas
- Total de casos por sistema
- Efetividade média das soluções
- Casos recentes e tendências
- Estatísticas de feedback dos usuários

## Como Usar o Sistema

### 1. Análise de Problema
1. Acesse a página principal
2. Digite a descrição detalhada do problema
3. Clique em "Analisar Problema"
4. Revise as sugestões e casos similares
5. Aplique a solução e forneça feedback

### 2. Adicionar Novo Caso
1. Navegue para "Adicionar Caso"
2. Preencha problema, solução e tipo de sistema
3. Adicione tags relevantes (opcional)
4. Salve o caso

### 3. Importar Casos em Lote
1. Prepare arquivo Excel com colunas: Problema, Solução, Sistema
2. Acesse "Upload de Casos"
3. Selecione o arquivo
4. Escolha "Formato Estruturado"
5. Confirme a importação

### 4. Gerenciar Casos Existentes
1. Acesse "Dashboard" para visão geral
2. Use "Casos" para listar todos
3. Clique em qualquer caso para visualizar/editar
4. Use a busca integrada para encontrar casos específicos

## Segurança e Privacidade

### Características de Segurança
- **Sem Conexões Externas**: Sistema 100% interno, sem envio de dados para APIs externas
- **Validação de Entrada**: Sanitização de todos os inputs do usuário
- **Sessões Seguras**: Gerenciamento de sessão com chaves secretas
- **Separação Cliente/Servidor**: Arquitetura segura com validação no backend

### Dados Sensíveis
- Todos os casos permanecem no banco de dados local
- Nenhuma informação é enviada para serviços externos de IA
- Machine learning executado completamente on-premises

## Manutenção e Troubleshooting

### Logs do Sistema
- Logs disponíveis no console da aplicação
- Nível DEBUG ativado para desenvolvimento
- Erros de banco de dados logados com detalhes

### Comandos Úteis
```bash
# Verificar status do banco
psql $DATABASE_URL -c "SELECT COUNT(*) FROM cases;"

# Backup de casos
psql $DATABASE_URL -c "COPY cases TO STDOUT WITH CSV HEADER;" > backup_casos.csv

# Verificar modelos ML
ls -la ml_models/
```

### Problemas Comuns

#### 1. Erro de Conexão com Banco
- Verifique as variáveis de ambiente DATABASE_URL
- Reinicie o workflow se necessário
- Sistema faz fallback para armazenamento em memória

#### 2. Importação Falha
- Verifique se as colunas estão nomeadas corretamente
- Confirme que o arquivo não está corrompido
- Use template fornecido como referência

#### 3. ML Models Não Carregam
- Verifique diretório ml_models/
- Modelos são retreinados automaticamente com novos dados
- Mínimo de 5 casos necessário para treinamento

## Escalabilidade e Performance

### Otimizações Implementadas
- **Connection Pooling**: Reutilização de conexões do banco
- **TF-IDF Caching**: Vetorização armazenada para reuso
- **Lazy Loading**: Modelos ML carregados sob demanda
- **Batch Processing**: Importação otimizada para múltiplos casos

### Limites Recomendados
- **Casos**: Até 10.000 casos mantém performance ótima
- **Importação**: Arquivos até 5MB recomendados
- **Busca**: Resultados limitados a 50 casos similares

## Roadmap e Extensões Futuras

### Funcionalidades Planejadas
- Export de dados em múltiplos formatos
- Dashboard avançado com gráficos
- Sistema de notificações para casos críticos
- API REST para integração externa
- Workflow de aprovação para casos sensíveis

### Escalabilidade
- Suporte para múltiplos bancos de dados
- Cache distribuído para ML models
- Balanceamento de carga para alta disponibilidade

---

**Versão do Sistema**: 1.0.0  
**Última Atualização**: 14 de Agosto de 2025  
**Ambiente**: Replit Production Environment  
**Suporte**: Sistema interno - documentação completa disponível neste arquivo