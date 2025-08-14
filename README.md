# OS Assistant - Sistema de Suporte Técnico Inteligente

## 📋 Descrição
Sistema de machine learning para diagnosticar e resolver problemas técnicos baseado em casos históricos. Focado em sistemas hospitalares brasileiros (Tasy, SGU, SGU Card, Autorizador).

## 🚀 Configuração Rápida no VSCode

### 1. Pré-requisitos
- Python 3.8+ instalado
- VSCode instalado
- Terminal/Prompt de comando

### 2. Passos de Instalação

1. **Clone/Baixe o projeto** para uma pasta local
2. **Abra a pasta no VSCode**
3. **Abra o terminal integrado** (Ctrl+` ou Terminal → New Terminal)
4. **Execute os comandos:**

```bash
# Instalar dependências
pip install flask flask-sqlalchemy pandas openpyxl scikit-learn werkzeug numpy PyPDF2 email-validator

# Executar o sistema
python run_local.py
```

5. **Acesse:** http://localhost:5000

## 📁 Estrutura do Projeto

```
OS-Assistant/
├── README.md                  # ← Este arquivo
├── run_local.py              # ← Script principal para executar
├── setup_local.md            # ← Guia detalhado de instalação
├── DOCUMENTACAO_SISTEMA.md   # ← Documentação completa técnica
├── 
├── 🎯 CORE (Arquivos principais)
├── app.py                    # Configuração Flask e banco
├── main.py                   # Ponto de entrada alternativo
├── routes.py                 # Todas as rotas da aplicação
├── models.py                 # Modelos do banco de dados
├── 
├── 🧠 SERVICES (Lógica de negócio)
├── case_service.py           # Gerenciamento de casos
├── ml_service.py             # Machine learning interno
├── file_processor.py         # Importação de arquivos Excel
├── 
├── 🎨 FRONTEND
├── static/
│   ├── style.css            # Estilos (Bootstrap + customizações)
│   └── script.js            # JavaScript (busca, confirmações)
├── templates/               # Templates HTML (Jinja2)
│   ├── base.html           # Layout base
│   ├── index.html          # Página principal
│   ├── dashboard.html      # Dashboard com estatísticas
│   ├── add_case.html       # Adicionar caso
│   ├── upload_cases.html   # Upload de planilhas
│   └── ... (outros templates)
├── 
├── 🤖 ML MODELS (Auto-gerados)
└── ml_models/              # Modelos treinados (pickle)
    ├── system_classifier.pkl
    ├── label_encoder.pkl
    └── metadata.pkl
```

## ⚡ Funcionalidades Principais

- **🔍 Análise Inteligente**: IA analisa problemas e sugere soluções
- **📊 Dashboard**: Estatísticas e visualização de casos
- **📁 Importação Excel**: Carregue centenas de casos via planilha
- **🔧 CRUD Completo**: Criar, editar, visualizar, deletar casos
- **🔎 Busca Inteligente**: Encontra casos similares automaticamente
- **🏥 Sistemas Suportados**: Tasy, SGU, SGU Card, Autorizador
- **🔒 100% Offline**: Sem dependências de APIs externas

## 💾 Banco de Dados

- **Desenvolvimento Local**: SQLite (arquivo `os_assistant.db`)
- **Produção**: PostgreSQL (configuração automática)
- **Backup**: Simplesmente copie o arquivo `os_assistant.db`

## 📤 Importação de Dados

### Formato de Planilha Excel
Suas planilhas devem ter estas colunas (exato como está):

| Problema | Solução | Sistema |
|----------|---------|---------|
| Descrição detalhada do problema | Como foi resolvido | Tasy/SGU/etc |

### Como Importar
1. Menu → "Upload de Casos"
2. Selecione arquivo Excel (.xlsx)
3. Clique "Importar"
4. Aguarde confirmação

## 🛠️ Comandos Úteis

```bash
# Executar em modo desenvolvimento
python run_local.py

# Executar em modo produção (alternativo)
python main.py

# Ver casos no banco
python -c "from app import *; with app.app_context(): print(f'Casos: {Case.query.count()}')"
```

## 📝 Logs e Debug

- **Logs aparecem no terminal** onde executou o comando
- **Para debug SQL**: Edite `app.py`, linha 49, mude `"echo": False` para `True`
- **Arquivo de log**: Não necessário, tudo aparece no console

## 🔧 Customizações

### Mudar Porta
Edite `run_local.py`, linha 57:
```python
app.run(port=8080)  # Sua porta preferida
```

### Adicionar Sistemas
Interface → "Gerenciar Sistemas" → Adicionar

### Backup Automático
Copie periodicamente:
- `os_assistant.db` (dados)
- `ml_models/` (modelos treinados)

## 🚨 Solução de Problemas

### Erro: ModuleNotFoundError
```bash
pip install --upgrade pip
pip install flask flask-sqlalchemy pandas openpyxl scikit-learn
```

### Erro: "Port 5000 in use"
- Mude a porta em `run_local.py`
- Ou pare o processo: `pkill -f python`

### Importação Falha
- Verifique colunas: "Problema", "Solução", "Sistema"
- Arquivo deve ser .xlsx (Excel)
- Máximo 5MB recomendado

### Performance Lenta
- Mais de 10.000 casos? Considere limpeza
- Feche outros programas pesados
- Use SSD se possível

## 📚 Documentação Completa

- **setup_local.md**: Guia detalhado de instalação
- **DOCUMENTACAO_SISTEMA.md**: Documentação técnica completa
- **Comentários no código**: Cada arquivo é bem documentado

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] VSCode instalado
- [ ] Projeto baixado em pasta local
- [ ] Terminal aberto na pasta do projeto
- [ ] Dependências instaladas (`pip install...`)
- [ ] `python run_local.py` executado
- [ ] http://localhost:5000 acessível
- [ ] Teste de importação realizado

## 🎯 Próximos Passos

1. Execute `python run_local.py`
2. Acesse http://localhost:5000
3. Teste as funcionalidades básicas
4. Importe seus dados Excel
5. Configure sistemas personalizados
6. Explore o dashboard e relatórios

---

**Versão:** 1.0.0 | **Suporte:** Sistema 100% interno | **Licença:** Uso interno