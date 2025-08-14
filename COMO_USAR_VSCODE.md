# 🎯 Como Usar no VSCode - Guia Completo

## 📥 DOWNLOAD E CONFIGURAÇÃO

### 1. Baixar o Projeto
1. **Baixe TODOS os arquivos** desta pasta para seu computador
2. **Crie uma pasta** (ex: `C:\OS-Assistant` ou `~/OS-Assistant`)
3. **Copie todos os arquivos** para essa pasta

### 2. Estrutura Necessária
Sua pasta deve ter exatamente estes arquivos:

```
OS-Assistant/
├── 📋 DOCUMENTAÇÃO
│   ├── README.md                    ← Leia primeiro
│   ├── INSTALACAO_VSCODE.md        ← Guia passo a passo
│   ├── setup_local.md              ← Instalação detalhada
│   └── DOCUMENTACAO_SISTEMA.md     ← Manual técnico
│
├── 🚀 EXECUÇÃO
│   ├── run_local.py                ← PRINCIPAL - Execute este arquivo
│   ├── main.py                     ← Alternativo
│   └── requirements_local.txt      ← Lista de dependências
│
├── 🔧 CORE DO SISTEMA
│   ├── app.py                      ← Configuração Flask
│   ├── routes.py                   ← Todas as páginas/rotas
│   ├── models.py                   ← Estrutura do banco
│   ├── case_service.py             ← Gerenciamento de casos
│   ├── ml_service.py               ← Inteligência artificial
│   └── file_processor.py           ← Importação Excel
│
├── 🎨 INTERFACE
│   ├── static/
│   │   ├── style.css               ← Estilos visuais
│   │   └── script.js               ← Interações
│   └── templates/                  ← Páginas HTML
│       ├── base.html
│       ├── index.html
│       ├── dashboard.html
│       └── ... (outras páginas)
│
├── ⚙️ VSCODE (Configurações)
│   └── .vscode/
│       ├── settings.json           ← Configurações do editor
│       ├── launch.json             ← Debug do sistema
│       └── tasks.json              ← Comandos rápidos
│
└── 🤖 ML MODELS (Criados automaticamente)
    └── ml_models/                  ← Modelos de IA (vazio no início)
```

---

## ⚡ INSTALAÇÃO SUPER RÁPIDA

### Passo 1: Instalar Python
- **Windows:** https://python.org/downloads (marque "Add to PATH")
- **Mac:** `brew install python3`
- **Linux:** `sudo apt install python3 python3-pip`

### Passo 2: Instalar VSCode
- Baixe em: https://code.visualstudio.com/

### Passo 3: Configurar Projeto
1. **Abra VSCode**
2. **File → Open Folder** → Selecione pasta `OS-Assistant`
3. **Abra Terminal** (Ctrl+` ou Terminal → New Terminal)
4. **Execute:**

```bash
# Instalar dependências
pip install -r requirements_local.txt

# OU instalar manualmente:
pip install flask flask-sqlalchemy pandas openpyxl scikit-learn werkzeug numpy PyPDF2 email-validator

# Executar sistema
python run_local.py
```

### Passo 4: Acessar Sistema
- **URL:** http://localhost:5000
- **Deve aparecer:** Tela inicial do OS Assistant

---

## 🎮 COMANDOS DO VSCODE

### Executar Sistema
- **Método 1:** `python run_local.py` no terminal
- **Método 2:** Ctrl+Shift+P → "Tasks: Run Task" → "Executar OS Assistant"
- **Método 3:** F5 (Debug mode)

### Comandos Úteis via Terminal
```bash
# Executar sistema
python run_local.py

# Instalar dependências
pip install -r requirements_local.txt

# Verificar casos no banco
python -c "from app import *; with app.app_context(): print(f'Casos: {Case.query.count()}')"

# Backup do banco
cp os_assistant.db backup_$(date +%Y%m%d).db
```

### Tasks Automáticas (Ctrl+Shift+P → Tasks)
- **"Executar OS Assistant"** - Inicia o sistema
- **"Instalar Dependências"** - Instala todas as bibliotecas
- **"Verificar Status do Banco"** - Mostra estatísticas

---

## 🔧 CONFIGURAÇÕES DO VSCODE

### Extensões Recomendadas
1. **Python** (Microsoft) - Essencial
2. **Python Debugger** - Para debug
3. **Pylance** - IntelliSense avançado

### Configurações Incluídas
- **Auto-complete** para Python ativado
- **Debug** configurado para Flask
- **Formatação** automática
- **Syntax highlighting** para templates

---

## 📊 USANDO O SISTEMA

### 1. Primeira Execução
1. Execute `python run_local.py`
2. Aguarde mensagem "Banco de dados SQLite inicializado"
3. Acesse http://localhost:5000
4. Você verá: "0 casos existentes"

### 2. Importar Seus Dados
1. **Prepare planilha Excel** com colunas:
   - **Problema**: Descrição do problema
   - **Solução**: Como foi resolvido  
   - **Sistema**: Tipo de sistema (Tasy, SGU, etc)

2. **No sistema:**
   - Menu → "Upload de Casos"
   - Selecione sua planilha .xlsx
   - Clique "Importar"
   - Aguarde confirmação

### 3. Funcionalidades Principais
- **📊 Dashboard**: Estatísticas e casos recentes
- **➕ Adicionar Caso**: Inserir problema manualmente
- **🔍 Analisar Problema**: IA sugere soluções
- **📋 Gerenciar Casos**: Ver, editar, deletar casos
- **📁 Upload de Casos**: Importação em massa

---

## 🚨 SOLUÇÃO DE PROBLEMAS

### Erro: "python: command not found"
```bash
# Windows - use:
py run_local.py

# Mac/Linux - use:
python3 run_local.py
```

### Erro: "ModuleNotFoundError"
```bash
pip install --upgrade pip
pip install -r requirements_local.txt
```

### Erro: "Port 5000 in use"
**Edite `run_local.py`** linha final:
```python
app.run(port=8080)  # Mude de 5000 para 8080
```

### Sistema Lento
- **Feche outros programas** pesados
- **Use SSD** se possível
- **Máximo 10.000 casos** recomendado

### Importação Falha
- **Verifique colunas:** Exatamente "Problema", "Solução", "Sistema"
- **Formato:** Arquivo .xlsx (Excel), não .xls
- **Tamanho:** Máximo 5MB por arquivo

---

## 💾 BACKUP E MANUTENÇÃO

### Backup Simples
```bash
# Copiar banco de dados
cp os_assistant.db backup/

# Copiar modelos treinados
cp -r ml_models/ backup/
```

### Limpeza
```bash
# Resetar banco (CUIDADO!)
rm os_assistant.db

# Limpar modelos (sistema vai retreinar)
rm -rf ml_models/
```

### Atualização
1. **Baixe nova versão** dos arquivos
2. **Mantenha** seu `os_assistant.db`
3. **Mantenha** pasta `ml_models/`
4. **Substitua** outros arquivos

---

## 📈 PERFORMANCE

### Configuração Mínima
- **Python 3.8+**
- **2GB RAM**
- **100MB espaço livre**
- **Windows 10/Mac 10.15/Ubuntu 18.04+**

### Configuração Recomendada
- **Python 3.11+**
- **4GB RAM**
- **1GB espaço livre**
- **SSD**

### Limites Sugeridos
- **Casos:** Até 10.000 funcionam bem
- **Importação:** Até 1.000 casos por vez
- **Arquivo:** Máximo 5MB por planilha

---

## 📞 SUPORTE

### Documentação
- **README.md** - Visão geral e comandos
- **INSTALACAO_VSCODE.md** - Passo a passo detalhado
- **DOCUMENTACAO_SISTEMA.md** - Manual técnico completo

### Debug
- **Logs:** Aparecem no terminal do VSCode
- **Erros:** Copie mensagem completa para análise
- **SQL Debug:** Edite `app.py`, mude `echo: False` para `True`

### Arquivos Importantes
- **Dados:** `os_assistant.db`
- **Config:** `.vscode/` (configurações VSCode)
- **Modelos:** `ml_models/` (IA treinada)

---

## ✅ CHECKLIST FINAL

**Antes de começar:**
- [ ] Python instalado e funcionando
- [ ] VSCode instalado
- [ ] Pasta do projeto criada
- [ ] Todos os arquivos copiados

**Configuração:**
- [ ] VSCode aberto na pasta correta
- [ ] Terminal integrado funcionando
- [ ] Dependências instaladas sem erro

**Teste:**
- [ ] `python run_local.py` executa
- [ ] http://localhost:5000 carrega
- [ ] Dashboard mostra "0 casos"
- [ ] Upload de teste funciona

**🎉 PRONTO! Seu OS Assistant está rodando perfeitamente no VSCode!**