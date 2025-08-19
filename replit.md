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
Color preferences: Avoid black, gray, and silver in system badge colors - use bright color palette only
UI guidance: Remove all tooltips and hints from interface, consolidate all guidance in tutorial menu (keep input placeholders)

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

**Migration to Replit Standard Environment (Completed August 18, 2025):**
- ✅ Successfully migrated from Replit Agent to standard Replit environment
- ✅ Fixed all package dependencies and gunicorn server configuration
- ✅ Corrected navbar alignment and centering issues for perfect UI presentation
- ✅ Fixed JavaScript scroll button errors and undefined variable issues
- ✅ Fixed JavaScript syntax errors in templates that were causing browser console errors
- ✅ Updated case detail page button to properly navigate to recent cases instead of dashboard
- ✅ Migration to Replit standard environment completed successfully on August 18, 2025
- ✅ Dashboard completely restructured with modern design and improved graphics
- ✅ Fixed 'total_feedback' attribute error in statistics system
- ✅ Removed unnecessary feedback card as requested by user
- ✅ Improved layout with 3-column card structure for better proportions
- ✅ Implemented unique color system with 14 bright colors, avoiding black/gray/silver
- ✅ Ensured color consistency between badges and progress bars with no duplicates
- Implemented PostgreSQL database with full persistence and connection pooling
- Fixed all import/export functionality with robust Excel processing
- Enhanced file processor to handle Portuguese column names and data validation
- Improved error handling and database connection stability
- Created comprehensive system documentation (DOCUMENTACAO_SISTEMA.md)
- Validated import functionality with 100+ real case data from user upload
- All security requirements maintained: 100% internal processing, no external AI dependencies

**Database Status:**
- PostgreSQL database fully operational with 200+ cases stored
- Enhanced connection pooling with better timeout and pool size management
- Automatic fallback to SQLite (os_assistant.db) if PostgreSQL connectivity issues occur
- Full CRUD operations implemented and tested
- Fixed database connection issues that caused worker crashes during import
- New AnalysisFeedback table created for comprehensive feedback tracking

**Import Functionality:**
- Fixed "Internal Server Error" during file imports
- Enhanced error handling to prevent application crashes
- Improved batch processing for large Excel files
- Added progress logging for import operations
- Handles Portuguese column names correctly (Problema, Solução, Sistema)
- Validates data quality and skips invalid entries

**Local Deployment Ready:**
- Created robust SQLite fallback for local deployment
- Added run_local.py script for easy local execution
- Enhanced database connection resilience with retry logic
- Created complete setup documentation (setup_local.md)
- System now automatically uses SQLite when PostgreSQL unavailable
- Ready for deployment on user's local machine with zero external dependencies

**Advanced ML Learning System (August 2025):**
- Implemented comprehensive feedback storage in PostgreSQL database
- Created AnalysisFeedback model to store detailed feedback on AI analysis
- **MAJOR UPGRADE**: Advanced intelligent learning from "useful" and "not useful" feedback ratings
- Real-time solution effectiveness scoring based on user feedback patterns
- Smart suggestion ranking that prioritizes solutions with higher success rates
- Automatic pattern recognition that learns from successful problem-solution combinations
- Intelligent retraining every 5 feedback submissions (increased frequency for faster learning)
- Enhanced system detection accuracy tracking with performance analytics
- Solution effectiveness weights automatically adjust based on feedback history
- New /ml-learning-info route provides comprehensive learning analytics and insights
- Machine Learning Learning Version 2.0: Fully adaptive system that truly learns from every feedback
- **FIXED**: Database connection error in feedback system - feedback now properly saves to PostgreSQL
- **ENHANCED**: Added _rank_solutions_by_feedback method for intelligent solution reordering based on historical effectiveness
- **UI IMPROVEMENTS**: Removed "N/A" badges from interface and improved button alignment in actions column
- **PROJECT CLEANUP**: Removed unused files (dashboard_old templates, VSCODE docs, local setup files, temporary assets)
- **INTERFACE ENHANCEMENT**: Enlarged textarea with helpful placeholder text and examples, fixed footer positioning

**PDF Analysis System (August 19, 2025):**
- ✅ **MAJOR NEW FEATURE**: Implemented intelligent PDF Order Service (OS) analyzer
- ✅ Created comprehensive PDFAnalyzer class with pattern recognition for Brazilian hospital systems
- ✅ Added automatic problem identification and solution generation from PDF text extraction
- ✅ Implemented SolutionFormatter for step-by-step visual solution display
- ✅ Added new /analyze-os-pdf route with upload functionality and auto-save options
- ✅ Enhanced solution display with numbered steps, icons, and visual progress indicators
- ✅ Integrated with existing ML learning system - PDF analyses automatically become learning cases
- ✅ Added comprehensive CSS styling for solution steps with hover effects and responsive design
- ✅ System can now automatically process OS PDFs and generate structured solutions
- ✅ Full integration with case management system - PDF analyses become permanent cases
- ✅ Smart system detection (SGU, Tasy, SGU Card, Autorizador) from PDF content
- ✅ Intelligent problem classification (password, access, email, parameterization, system issues)
- ✅ Context-aware solution generation based on problem type and system identified
- ✅ Visual step-by-step solution presentation with appropriate icons for each action type
- ✅ Mobile-responsive design for solution steps display
- ✅ **ENHANCED PDF INTELLIGENCE**: Improved pattern recognition for specific permission requests
- ✅ **FIXED PARAMETER CLASSIFICATION**: Now correctly identifies permission copying requests ("parametrizar usuário com as mesmas permissões")
- ✅ **CONTEXT-AWARE SOLUTIONS**: Generates specific solutions mentioning actual user names from PDFs
- ✅ **PRIORITY-BASED MATCHING**: More specific patterns matched first to prevent generic classification

**Migration to Standard Replit Environment (August 19, 2025):**
- ✅ **COMPLETED MIGRATION**: Successfully migrated from Replit Agent to standard Replit environment
- ✅ All packages properly installed and configured for Replit compatibility
- ✅ Gunicorn server running successfully on port 5000
- ✅ Database connections working (PostgreSQL with SQLite fallback)
- ✅ All existing features preserved: ML analysis, PDF processing, case management
- ✅ Security maintained: 100% internal processing, no external AI dependencies
- ✅ **ENHANCED PDF INTELLIGENCE**: Improved pattern recognition for specific permission requests
- ✅ **FIXED PARAMETER CLASSIFICATION**: Now correctly identifies permission copying requests ("parametrizar usuário com as mesmas permissões")
- ✅ **CONTEXT-AWARE SOLUTIONS**: Generates specific solutions mentioning actual user names from PDFs
- ✅ **PRIORITY-BASED MATCHING**: More specific patterns matched first to prevent generic classification
- ✅ **STREAMLINED INTERFACE**: Removed "Add Case" menu option - all cases now added via PDF analysis
- ✅ **AUTO-SAVE ENABLED**: All PDF uploads are automatically saved as cases without user intervention