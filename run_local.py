#!/usr/bin/env python3
"""
OS Assistant - Local Development Runner

This script sets up and runs the OS Assistant application locally with SQLite database.
Perfect for running on your local machine without external dependencies.
"""

import os
import sys
import logging
from pathlib import Path

# Set environment variables for local development
os.environ["DATABASE_URL"] = ""  # Forces SQLite usage
os.environ["SESSION_SECRET"] = "local-dev-secret-key-change-for-production"

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("="*60)
print("OS ASSISTANT - Sistema de Suporte Técnico Inteligente")
print("="*60)
print("Configuração: SQLite (Banco Local)")
print("Porta: 5000")
print("URL: http://localhost:5000")
print("Pasta do projeto:", Path(__file__).parent)
print("="*60)

try:
    from app import app, db
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados SQLite inicializado com sucesso")
        print(f"📁 Arquivo do banco: {os.path.join(os.getcwd(), 'os_assistant.db')}")
        
        # Check if we have any existing cases
        from models import Case
        case_count = Case.query.count()
        print(f"📊 Casos existentes no banco: {case_count}")
    
    print("\n🚀 Iniciando servidor Flask...")
    print("💡 Pressione Ctrl+C para parar o servidor")
    print("="*60)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("\n📦 Instale as dependências necessárias:")
    print("pip install flask flask-sqlalchemy pandas openpyxl scikit-learn")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao iniciar aplicação: {e}")
    sys.exit(1)