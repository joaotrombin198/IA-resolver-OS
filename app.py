import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database with robust fallback strategy
database_url = os.environ.get("DATABASE_URL")
if database_url and "postgres" in database_url:
    # PostgreSQL configuration with connection resilience
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 10,
        "pool_size": 5,
        "max_overflow": 10,
        "echo": False,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "os_assistant"
        }
    }
else:
    # SQLite fallback for local development and reliability
    import os
    db_path = os.path.join(os.getcwd(), "os_assistant.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "echo": False,
        "connect_args": {"timeout": 20}
    }
    
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Initialize in-memory storage for prototyping (will migrate to DB later)
app.config['CASES_STORAGE'] = []
app.config['NEXT_CASE_ID'] = 1

with app.app_context():
    # Make sure to import the models here
    import models
    db.create_all()

# Import routes after app creation to avoid circular imports
from routes import *

# Import solution formatter and register template filter
from solution_formatter import solution_formatter

@app.template_filter('format_solution_steps')
def format_solution_steps_filter(solution):
    """Jinja2 template filter para formatar soluções em etapas"""
    return solution_formatter.format_solution_html(solution)

@app.template_filter('count_solution_steps')
def count_solution_steps_filter(solution):
    """Jinja2 template filter para contar número de etapas"""
    return solution_formatter.get_step_count(solution)

@app.template_filter('format_ml_solution_compact')
def format_ml_solution_compact_filter(solution):
    """Jinja2 template filter para formatar soluções ML compactas"""
    return solution_formatter.format_ml_solution_compact(solution)
