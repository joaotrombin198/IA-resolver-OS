# OS Assistant - Instalação e Configuração Local

## Como Rodar na Sua Máquina

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação Rápida

1. **Baixe todos os arquivos do projeto** para uma pasta no seu computador

2. **Abra o terminal/prompt na pasta do projeto**

3. **Instale as dependências:**
```bash
pip install flask flask-sqlalchemy pandas openpyxl scikit-learn gunicorn werkzeug numpy PyPDF2 email-validator psycopg2-binary
```

4. **Execute o aplicativo:**
```bash
python run_local.py
```

5. **Acesse no navegador:**
```
http://localhost:5000
```

### Estrutura de Arquivos Necessários

Certifique-se de ter todos estes arquivos na pasta:

```
OS-Assistant/
├── run_local.py           # ← Script principal para executar
├── app.py                 # Configuração do Flask
├── main.py                # Ponto de entrada alternativo
├── models.py              # Modelos do banco de dados
├── routes.py              # Rotas da aplicação
├── case_service.py        # Serviço de gerenciamento de casos
├── ml_service.py          # Serviço de machine learning
├── file_processor.py      # Processamento de arquivos
├── static/
│   ├── style.css          # Estilos CSS
│   └── script.js          # JavaScript
├── templates/             # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── add_case.html
│   ├── upload_cases.html
│   └── ... (outros templates)
└── ml_models/             # Modelos de ML (criados automaticamente)
```

### Banco de Dados Local

- **Tipo:** SQLite (arquivo local)
- **Localização:** `os_assistant.db` na pasta do projeto
- **Backup:** Simplesmente copie o arquivo `os_assistant.db`
- **Reset:** Delete o arquivo para começar do zero

### Importação de Dados

1. Acesse "Upload de Casos" no menu
2. Selecione seu arquivo Excel com colunas:
   - **Problema**: Descrição do problema
   - **Solução**: Solução aplicada
   - **Sistema**: Tipo de sistema (opcional)
3. Clique em "Importar"

### Funcionalidades Principais

- ✅ **Análise de Problemas**: IA analisa e sugere soluções
- ✅ **Importação Excel**: Carregue casos em lote
- ✅ **Dashboard**: Estatísticas e casos recentes
- ✅ **CRUD Completo**: Criar, editar, deletar casos
- ✅ **Busca Inteligente**: Encontre casos similares
- ✅ **100% Offline**: Sem dependências externas

### Solução de Problemas

#### Erro: "ModuleNotFoundError"
```bash
pip install --upgrade pip
pip install flask flask-sqlalchemy pandas openpyxl scikit-learn
```

#### Erro: "Port already in use"
```bash
# Use outra porta editando run_local.py, linha:
app.run(port=5001)  # Mude de 5000 para 5001
```

#### Erro: "Permission denied" no banco
```bash
# Verifique permissões da pasta
chmod 755 .
```

#### Importação falha
- Verifique se as colunas estão nomeadas: "Problema", "Solução", "Sistema"
- Arquivo deve ser .xlsx ou .csv
- Máximo 5MB recomendado

### Performance

- **Casos suportados:** Até 10.000 casos
- **Importação:** Até 1.000 casos por vez
- **Memória:** ~100MB RAM
- **Espaço:** ~50MB disco

### Backup e Migração

#### Backup Completo
```bash
# Copie estes arquivos:
cp os_assistant.db backup/
cp -r ml_models/ backup/
```

#### Restaurar Backup
```bash
cp backup/os_assistant.db .
cp -r backup/ml_models/ .
```

### Customização

#### Mudar Porta
Edite `run_local.py`, linha 57:
```python
app.run(port=8080)  # Sua porta preferida
```

#### Ativar Debug SQL
Edite `app.py`, linha 49:
```python
"echo": True  # Mostra queries SQL no console
```

#### Adicionar Sistemas
Acesse "Gerenciar Sistemas" no menu da aplicação

### Suporte

- **Documentação completa:** `DOCUMENTACAO_SISTEMA.md`
- **Logs de erro:** Aparecem no terminal onde executou
- **Banco de dados:** SQLite Browser para visualizar dados