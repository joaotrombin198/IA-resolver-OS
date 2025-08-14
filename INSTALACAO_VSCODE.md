# 🎯 Guia de Instalação VSCode - Passo a Passo

## 📋 O que você vai precisar
- Windows/Mac/Linux com Python 3.8+
- VSCode (Visual Studio Code)
- 10 minutos do seu tempo

---

## 🔧 PASSO 1: Verificar Python

Abra o **Prompt de Comando** (Windows) ou **Terminal** (Mac/Linux):

```bash
python --version
```

**Resultado esperado:** `Python 3.8.x` ou superior

**Se não funcionar:**
- Windows: Baixe em https://python.org/downloads
- Mac: `brew install python3`
- Ubuntu: `sudo apt install python3 python3-pip`

---

## 📁 PASSO 2: Preparar Pasta do Projeto

1. **Crie uma pasta** no seu computador (ex: `C:\OS-Assistant` ou `~/OS-Assistant`)
2. **Copie TODOS os arquivos** do projeto para essa pasta
3. **Estrutura deve ficar assim:**

```
OS-Assistant/
├── README.md
├── run_local.py              ← IMPORTANTE
├── app.py
├── routes.py
├── models.py
├── case_service.py
├── ml_service.py
├── file_processor.py
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   ├── base.html
│   ├── index.html
│   └── ... (outros arquivos)
└── ml_models/               ← Pasta pode estar vazia
```

---

## 🚀 PASSO 3: Abrir no VSCode

1. **Abra o VSCode**
2. **File → Open Folder** (ou Ctrl+K, Ctrl+O)
3. **Selecione a pasta** `OS-Assistant`
4. **Confira**: Você deve ver todos os arquivos na barra lateral

---

## ⚡ PASSO 4: Instalar Dependências

1. **Abra o Terminal integrado** no VSCode:
   - **Menu:** Terminal → New Terminal
   - **Atalho:** Ctrl+` (aspas simples)

2. **Execute este comando:**
```bash
pip install flask flask-sqlalchemy pandas openpyxl scikit-learn werkzeug numpy PyPDF2 email-validator
```

**Aguarde a instalação** (pode demorar 2-3 minutos)

**Se der erro de permissão:**
```bash
pip install --user flask flask-sqlalchemy pandas openpyxl scikit-learn werkzeug numpy PyPDF2 email-validator
```

---

## 🎯 PASSO 5: Executar o Sistema

No terminal do VSCode, digite:

```bash
python run_local.py
```

**Você deve ver:**
```
============================================================
OS ASSISTANT - Sistema de Suporte Técnico Inteligente
============================================================
Configuração: SQLite (Banco Local)
Porta: 5000
URL: http://localhost:5000
============================================================
✅ Banco de dados SQLite inicializado com sucesso
📁 Arquivo do banco: C:\OS-Assistant\os_assistant.db
📊 Casos existentes no banco: 0

🚀 Iniciando servidor Flask...
💡 Pressione Ctrl+C para parar o servidor
============================================================
```

---

## 🌐 PASSO 6: Testar no Navegador

1. **Abra seu navegador** (Chrome, Firefox, Edge, Safari)
2. **Digite:** `http://localhost:5000`
3. **Deve aparecer** a tela inicial do OS Assistant

**Se não funcionar:**
- Verifique se não há erro no terminal
- Tente `http://127.0.0.1:5000`
- Veja se outra aplicação está usando a porta 5000

---

## 📊 PASSO 7: Testar Importação

1. **Prepare uma planilha Excel** com colunas:
   - **Problema** (descrição do problema)
   - **Solução** (como foi resolvido)
   - **Sistema** (tipo de sistema)

2. **Na aplicação:**
   - Clique **"Upload de Casos"**
   - Selecione sua planilha
   - Clique **"Importar"**

3. **Verifique no Dashboard** se os casos apareceram

---

## 🔧 Configurações do VSCode (Opcional)

### Extensões Recomendadas
1. **Python** (Microsoft)
2. **Python Debugger** (Microsoft)
3. **Pylance** (Microsoft)

### Configurar Python Interpreter
1. **Ctrl+Shift+P**
2. **Digite:** `Python: Select Interpreter`
3. **Escolha** a versão do Python instalada

---

## 🚨 Soluções de Problemas Comuns

### ❌ "python: command not found"
**Windows:**
- Reinstale Python marcando "Add to PATH"
- Use `py` em vez de `python`

**Mac/Linux:**
- Use `python3` em vez de `python`
- Instale via gerenciador de pacotes

### ❌ "ModuleNotFoundError: No module named 'flask'"
```bash
pip install --upgrade pip
pip install flask flask-sqlalchemy pandas openpyxl scikit-learn
```

### ❌ "Port 5000 is already in use"
**Edite `run_local.py`** linha 57:
```python
app.run(port=8080)  # Mude de 5000 para 8080
```

### ❌ "Permission denied" ao criar banco
**Windows:**
- Execute VSCode como Administrador
- Verifique antivírus

**Mac/Linux:**
```bash
chmod 755 .
```

### ❌ Importação de Excel falha
- Verifique se colunas estão nomeadas exatamente: "Problema", "Solução", "Sistema"
- Use arquivo .xlsx (Excel), não .xls
- Arquivo deve ter menos de 5MB

---

## 📈 Próximos Passos

### 1. Explorar Funcionalidades
- ✅ Adicionar casos manualmente
- ✅ Testar análise de problemas
- ✅ Verificar dashboard
- ✅ Importar sua planilha de dados

### 2. Customizar Sistema
- Adicionar seus sistemas específicos
- Ajustar tipos de problema
- Configurar tags personalizadas

### 3. Backup dos Dados
- Copie o arquivo `os_assistant.db` periodicamente
- Salve a pasta `ml_models/` após treinar

---

## 📞 Suporte

**Documentação Completa:**
- `DOCUMENTACAO_SISTEMA.md` - Guia técnico completo
- `setup_local.md` - Guia de instalação detalhado

**Logs de Erro:**
- Aparecem no terminal do VSCode
- Copie e cole para debug

**Backup/Restore:**
- Dados: arquivo `os_assistant.db`
- Modelos: pasta `ml_models/`

---

## ✅ Checklist Final

- [ ] Python instalado e funcionando
- [ ] VSCode instalado
- [ ] Projeto copiado para pasta local
- [ ] Dependências instaladas sem erro
- [ ] `python run_local.py` executa sem erro
- [ ] http://localhost:5000 carrega a aplicação
- [ ] Teste de importação realizado
- [ ] Dashboard mostra dados corretamente

**🎉 Parabéns! Seu OS Assistant está funcionando!**