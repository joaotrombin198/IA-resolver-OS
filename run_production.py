#!/usr/bin/env python3
"""
OS Assistant - Production Server

Para uso com múltiplos usuários simultâneos em rede.
Use este script quando várias pessoas acessarem ao mesmo tempo.
"""

import os
import sys
import logging
from pathlib import Path

# Set environment variables for production
os.environ["DATABASE_URL"] = ""  # Forces SQLite usage
os.environ["SESSION_SECRET"] = "production-secret-key-change-this"
os.environ["FLASK_ENV"] = "production"

# Ensure we can import from the current directory
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("="*60)
print("OS ASSISTANT - SERVIDOR PRODUÇÃO (Multi-usuário)")
print("="*60)
print("Configuração: SQLite (Compartilhado)")
print("Porta: 5000")
print("Acesso em rede: Habilitado")
print("Usuários simultâneos: Suportado")
print("="*60)

try:
    from app import app, db
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados SQLite inicializado")
        print(f"📁 Arquivo do banco: {os.path.join(os.getcwd(), 'os_assistant.db')}")
        
        # Check if we have any existing cases
        from models import Case
        case_count = Case.query.count()
        print(f"📊 Casos existentes: {case_count}")
    
    print("\n🚀 Iniciando servidor de produção...")
    print("🌐 Acesso em rede habilitado para múltiplos usuários")
    print("💡 Pressione Ctrl+C para parar")
    print("="*60)
    
    # Run with Gunicorn-like settings for better performance
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Disabled for production
        threaded=True,  # Enable threading for multiple users
        use_reloader=False
    )

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("\n📦 Instale as dependências:")
    print("pip install -r requirements_local.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao iniciar: {e}")
    sys.exit(1)