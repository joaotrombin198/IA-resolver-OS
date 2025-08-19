# OS Assistant - AI Technical Support System

## Overview

OS Assistant is a machine learning-powered technical support system designed to help technicians diagnose and resolve work order issues across multiple systems. It acts as a "digital mentor," analyzing problem descriptions and suggesting solutions based on historical cases and proprietary ML models. The system focuses on multi-system support for Brazilian hospital management systems (Tasy, SGU, SGU Card, Autorizador). It uses custom, internal machine learning algorithms that continuously improve through user feedback and case history, operating without any external AI dependencies. The system also includes a workflow for escalating complex cases.

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
Color preferences: Avoid black, gray, and silver in system badge colors - use bright color palette only
UI guidance: Remove all tooltips and hints from interface, consolidate all guidance in tutorial menu (keep input placeholders)

## System Architecture

### Core Architecture Pattern
The application follows a traditional Flask MVC architecture with service layer separation. The frontend uses server-side rendered HTML templates with Bootstrap. The backend is a Flask web framework with a modular service-based architecture. Storage is handled by a PostgreSQL database with full persistence and multi-user synchronization. AI processing is managed by a custom ML service using scikit-learn, operating 100% internally.

### Key Architectural Components

**Web Framework**
Flask application with blueprint-style route organization, session management, and Jinja2 templating.

**Service Layer Architecture**
- `MLService`: Custom machine learning for problem analysis, system type detection, and solution generation.
- `CaseService`: Manages case storage, similarity searches using TF-IDF vectorization, and statistics generation.
- Modular design for easy service replacement or enhancement.

**Machine Learning Architecture**
Custom ML pipeline using scikit-learn for classification and pattern recognition. It utilizes TF-IDF vectorization, SVM and Naive Bayes classifiers, and rule-based solution generation. The system has incremental learning capabilities and continuously retrains the model after case modifications or user feedback. It intelligently learns from "useful" and "not useful" feedback, providing smart suggestion ranking and pattern recognition.

**Data Models**
- `Case`: Stores problem descriptions, solutions, system types, and effectiveness feedback.
- `SolutionSuggestion`: Contains AI-generated recommendations with confidence scoring.
- `AnalysisFeedback`: Stores detailed feedback on AI analysis for comprehensive learning.

**Frontend Architecture**
Bootstrap-based responsive design with a dark theme and Feather Icons. The interface is entirely in Portuguese and uses JavaScript for enhanced UX features like form validation, auto-save, search, and deletion confirmation. It provides a CRUD interface for case management with inline editing. A significant new feature is the intelligent PDF Order Service (OS) analyzer, which processes PDFs, extracts information, identifies problems, generates solutions, and automatically saves them as cases. It supports batch processing of multiple PDFs.

### Design Patterns and Principles

**Service-Oriented Design**
Separates concerns into distinct services for modularity and easy component replacement.

**Template-Based UI**
Utilizes Flask's template inheritance for consistent layouts and reusable components.

**Stateless Design**
Application state is stored in Flask's application config, allowing for easy transition to external databases.

## External Dependencies

### AI/ML Services (100% Internal)
- **Scikit-learn**: Used for the complete ML pipeline, including TF-IDF vectorization, classification models (SVM, Naive Bayes), and similarity calculations.
- **Custom ML Service**: Proprietary machine learning algorithms for system type detection and solution pattern matching.
- **Model Persistence**: Pickle-based storage for ML models.
- **No External AI**: The system operates entirely offline without any external AI service dependencies (e.g., OpenAI).

### Frontend Libraries
- **Bootstrap**: Responsive UI framework.
- **Feather Icons**: Icon library.

### Python Framework Stack
- **Flask**: Core web framework.
- **Jinja2**: Template engine.
- **NumPy**: For mathematical operations in similarity calculations.

### Database
- **PostgreSQL**: Primary database for persistence and multi-user synchronization.
- **SQLite**: Used as a fallback for local deployment if PostgreSQL is unavailable.