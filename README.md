# Assistente OS - Sistema de Suporte Técnico Inteligente

Sistema de machine learning para diagnóstico e resolução de Ordens de Serviço (OS) em ambiente hospitalar brasileiro.

## 🏥 Sistemas Suportados

- **Tasy** - Sistema hospitalar Philips
- **SGU** - Sistema de gestão hospitalar 
- **SGU Card** - Módulo de carteirinhas de pacientes
- **Autorizador** - Sistema de autorizações médicas
- **Sistemas personalizados** - Adicione seus próprios sistemas

## 🚀 Funcionalidades

- ✅ **Diagnóstico inteligente** - IA analisa problemas e sugere soluções
- ✅ **Base de conhecimento** - Gerencie casos históricos
- ✅ **Upload de casos** - Importe do Excel/PDF
- ✅ **Machine Learning próprio** - Sem dependência de APIs externas
- ✅ **Interface em português** - Totalmente localizada
- ✅ **Escalação para Nexdow** - Workflow de suporte avançado
- ✅ **CRUD completo** - Crie, edite, visualize e exclua casos

## 📋 Requisitos

- Python 3.10+
- Flask
- scikit-learn
- pandas
- openpyxl
- PyPDF2

## 🔧 Como Executar

### Opção 1: Replit (Recomendado)
1. Abra este projeto no Replit
2. Clique em "Run" 
3. Acesse via URL gerada
4. Para deploy: clique em "Deploy" para acesso permanente

### Opção 2: Servidor Local
```bash
# Clone o projeto
git clone <url-do-repositorio>

# Instale dependências
pip install flask scikit-learn pandas openpyxl PyPDF2 numpy

# Execute o servidor
python main.py

# Acesse: http://localhost:5000
```

### Opção 3: Servidor de Rede
```bash
# Execute para acesso em rede local
python main.py

# Configure firewall para porta 5000
# Equipe acessa via: http://IP-DO-SERVIDOR:5000
```

### Opção 4: Executável (Windows)
```bash
# Instale PyInstaller
pip install pyinstaller

# Gere executável
pyinstaller --onedir --windowed main.py

# Distribua pasta dist/ completa
# Execute main.exe
```

## 📖 Como Usar

### 1. Primeiro Acesso
1. Vá para **Tutorial** no menu superior
2. Clique em **"Carregar Exemplos"** no dashboard
3. Teste o diagnóstico com um problema conhecido

### 2. Adicionar Casos
- **Manual**: Use "Adicionar Caso" no dashboard
- **Upload**: Importe Excel/CSV com colunas: Problema, Solução, Sistema
- **PDF**: Upload de documentos de casos (processamento automático)

### 3. Usar o Assistente
1. Vá para **"Diagnosticar Problema"**
2. Descreva o problema técnico
3. Receba sugestões baseadas em casos similares
4. Avalie a eficácia das soluções

### 4. Gerenciar Sistemas
- Acesse **"Gerenciar Sistemas"** no dashboard
- Adicione sistemas personalizados (SAGE, MV PEP, AGFA, etc.)
- Configure categorias e descrições

## 📁 Formato de Import (Excel/CSV)

| Problema | Solução | Sistema |
|----------|---------|---------|
| Tasy não conecta com Oracle | Verificar tnsnames.ora e reiniciar listener | Tasy |
| SGU Card não imprime | Atualizar driver da impressora | SGU Card |
| Autorizador com timeout | Verificar certificados digitais | Autorizador |

## 🤖 Machine Learning

O sistema usa algoritmos próprios:
- **TF-IDF** para análise semântica
- **SVM e Naive Bayes** para classificação
- **Cosine Similarity** para encontrar casos similares
- **Treinamento automático** após adições/edições

### Treinamento
- Mínimo **5 casos** para treinar modelos
- Treinamento automático após mudanças
- Botão manual no dashboard

## 🌐 Deploy para Equipe

### Replit Deploy (Mais Fácil)
1. No Replit, clique em **"Deploy"**
2. Escolha o plano adequado
3. Configure domínio personalizado (opcional)
4. Compartilhe URL com a equipe

### Servidor Windows/Linux
```bash
# Configure firewall
ufw allow 5000

# Execute em modo produção
gunicorn --bind 0.0.0.0:5000 main:app

# Ou use o script integrado
python main.py
```

### Docker (Opcional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]
```

## 📊 Estrutura do Projeto

```
assistente-os/
├── main.py              # Ponto de entrada
├── app.py               # Configuração Flask
├── routes.py            # Rotas da aplicação
├── models.py            # Modelos de dados
├── case_service.py      # Serviços de casos
├── ml_service.py        # Machine Learning
├── templates/           # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── case_detail.html
│   ├── edit_case.html
│   ├── upload_cases.html
│   ├── manage_systems.html
│   └── tutorial.html
├── static/              # CSS/JS/imagens
├── ml_models/           # Modelos ML treinados
└── README.md
```

## 🔒 Segurança e Dados

- **Dados em memória**: Para prototipagem rápida
- **Sem APIs externas**: Funciona offline
- **Backup manual**: Exporte casos regularmente
- **Futuro**: Implementar PostgreSQL para persistência

## 🆘 Suporte e Escalação

- **Nexdow**: Casos complexos são escalados automaticamente
- **Tutorial integrado**: Documentação no próprio sistema
- **Feedback**: Sistema de avaliação de soluções

## 📈 Próximas Melhorias

- [ ] Persistência em banco de dados
- [ ] Sistema multi-usuário com autenticação
- [ ] API REST para integrações
- [ ] Relatórios avançados
- [ ] Backup automático
- [ ] Integração com sistemas hospitalares

## 📝 Licença

Projeto desenvolvido para ambientes hospitalares brasileiros.

---

**Desenvolvido para equipes técnicas de TI hospitalar** 🏥⚕️

Para dúvidas sobre implementação ou customização, consulte o Tutorial integrado no sistema.