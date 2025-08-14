# OS Assistant - AI Technical Support System

## Overview

OS Assistant is a machine learning-powered technical support system designed to help technicians diagnose and resolve work order issues across multiple systems. The application serves as a "digital mentor" that analyzes problem descriptions and suggests solutions based on historical cases and proprietary ML models.

The system focuses on multi-system support (particularly Brazilian hospital management systems like Tasy, SGU, SGU Card, and Autorizador) and uses custom machine learning algorithms to continuously improve its recommendations through user feedback and case history. It operates as a completely internal system with NO external AI dependencies, learning from exported data, reports, or manually entered information using its own ML engine. The system includes workflow for escalating complex cases to Nexdow when internal resolution is not possible.

## User Preferences

Preferred communication style: Simple, everyday language.
Interface language: Portuguese (complete system translation implemented)
Specific systems supported: Tasy, SGU, SGU Card, Autorizador (Brazilian hospital systems)
Escalation workflow: Include Nexdow escalation options when internal resolution fails
Case management: Full CRUD operations (Create, Read, Update, Delete) for case management
Upload functionality: Excel/CSV/PDF import for bulk case addition (structured format only)
Tutorial system: Complete documentation and usage guide integrated
Security requirement: NO external AI connections - system must be 100% internal
Search integration: Integrated search within cases panel (no separate search box)

## System Architecture

### Core Architecture Pattern
The application follows a traditional Flask MVC architecture with service layer separation:

- **Frontend**: Server-side rendered HTML templates with Bootstrap for responsive UI
- **Backend**: Flask web framework with modular service-based architecture
- **Storage**: PostgreSQL database with full persistence and multi-user synchronization
- **AI Processing**: Custom ML service using scikit-learn for intelligent problem analysis (100% internal)

### Key Architectural Components

**Web Framework**
- Flask application with blueprint-style route organization
- Session management with configurable secret keys
- Template-based rendering using Jinja2

**Service Layer Architecture**
- `MLService`: Custom machine learning service using scikit-learn for problem analysis, system type detection, and solution generation
- `CaseService`: Manages case storage, similarity searches using TF-IDF vectorization, and statistics generation
- Modular design allows easy service replacement or enhancement

**Machine Learning Architecture**
- Custom ML pipeline using scikit-learn for classification and pattern recognition
- TF-IDF vectorization for text analysis and similarity matching
- Support Vector Machine (SVM) and Naive Bayes classifiers for system type detection
- Rule-based solution generation with pattern matching
- Incremental learning capabilities that improve with more case data

**Data Models**
- `Case`: Core entity storing problem descriptions, solutions, system types, and effectiveness feedback
- `SolutionSuggestion`: Container for AI-generated recommendations with confidence scoring
- In-memory storage with simple list-based persistence for rapid prototyping
- Full CRUD operations implemented: Create, Read, Update, Delete cases
- Real-time ML model retraining after case modifications

**Machine Learning Integration**
- Scikit-learn TF-IDF vectorization for case similarity matching
- Cosine similarity calculations for finding related historical cases
- Continuous learning through user feedback and effectiveness scoring

**Frontend Architecture**
- Bootstrap-based responsive design with dark theme
- Feather Icons for consistent iconography
- Complete Portuguese language interface
- JavaScript for enhanced UX (form validation, auto-save, search functionality, deletion confirmation)
- CRUD interface for case management with inline editing and deletion

### Design Patterns and Principles

**Service-Oriented Design**
The application separates concerns into distinct services, making it easy to replace components (e.g., switching from in-memory to database storage, or changing AI providers).

**Template-Based UI**
Uses Flask's template inheritance for consistent page layouts and reusable components across all views.

**Stateless Design**
The application stores state in Flask's application config, making it easy to transition to external databases when needed.

## External Dependencies

### AI/ML Services (100% Internal)
- **Scikit-learn**: Complete ML pipeline including TF-IDF vectorization, classification models (SVM, Naive Bayes), and similarity calculations
- **Custom ML Service**: Proprietary machine learning algorithms for system type detection and solution pattern matching
- **Model Persistence**: Pickle-based model storage for training persistence and performance optimization
- **No External AI**: System operates completely offline without OpenAI or any external AI service dependencies

### Frontend Libraries
- **Bootstrap**: Responsive UI framework with dark theme support
- **Feather Icons**: Icon library for consistent interface elements

### Python Framework Stack
- **Flask**: Core web framework for routing and request handling
- **Jinja2**: Template engine for server-side rendering
- **NumPy**: Mathematical operations for similarity calculations

### Development Dependencies
- **Logging**: Built-in Python logging for debugging and error tracking
- Environment variable management for API keys and configuration

The system is designed to be easily deployable with Docker and can be hosted on various cloud platforms (AWS, Azure, GCP) or on-premises servers.

## Recent Updates (August 2025)

**Migration to Replit Standard Environment:**
- Successfully migrated from Replit Agent to standard Replit environment
- Implemented PostgreSQL database with full persistence and connection pooling
- Fixed all import/export functionality with robust Excel processing
- Enhanced file processor to handle Portuguese column names and data validation
- Improved error handling and database connection stability
- Created comprehensive system documentation (DOCUMENTACAO_SISTEMA.md)
- Validated import functionality with 100+ real case data from user upload
- All security requirements maintained: 100% internal processing, no external AI dependencies

**Database Status:**
- PostgreSQL database fully operational with 114+ cases stored
- Enhanced connection pooling with better timeout and pool size management
- Automatic fallback to in-memory storage if database connectivity issues occur
- Full CRUD operations implemented and tested
- Fixed database connection issues that caused worker crashes during import

**Import Functionality:**
- Fixed "Internal Server Error" during file imports
- Enhanced error handling to prevent application crashes
- Improved batch processing for large Excel files
- Added progress logging for import operations
- Handles Portuguese column names correctly (Problema, Solução, Sistema)
- Validates data quality and skips invalid entries