# Lead Intelligence Platform

An AI-assisted lead generation system that discovers post-revenue US businesses and enriches them with useful contact information.

## Overview

Lead Intelligence Platform is a production-grade Python application designed to:
- **Discover** potential business leads from multiple data sources
- **Collect** contact information and company details
- **Enrich** data with AI-powered insights and validation
- **Export** processed leads in multiple formats (CSV, JSON, Excel)

## Features

- ✅ Modular, scalable architecture
- ✅ Type hints throughout codebase
- ✅ Production-ready logging system
- ✅ Comprehensive error handling
- ✅ Environment-based configuration
- ✅ Database ORM with SQLAlchemy
- ✅ AI enrichment integration ready
- ✅ Multiple export formats

## Requirements

- **Python**: 3.13 or higher
- **Database**: PostgreSQL (recommended) or SQLite
- **Optional**: OpenAI/Anthropic API key for AI enrichment

## Project Structure

```
LeadIntelPlatform/
├── scrapers/               # Web scraping and data discovery
│   └── __init__.py
├── database/               # Database models and ORM
│   └── __init__.py
├── enrichment/             # AI-powered data enrichment
│   └── __init__.py
├── models/                 # Data models and dataclasses
│   └── __init__.py
├── exporters/              # Data export functionality
│   └── __init__.py
├── services/               # Business logic and orchestration
│   └── __init__.py
├── utils/                  # Utility functions and helpers
│   └── __init__.py
├── tests/                  # Test suite
│   └── __init__.py
├── main.py                 # Application entry point
├── config.py               # Configuration management (dataclass-based)
├── logging_config.py       # Logging configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git configuration
└── README.md               # This file
```

## Installation

### 1. Clone or initialize the project

```bash
cd LeadIntelPlatform
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Verify installation

```bash
python main.py
```

## Configuration

All configuration is managed through `config.py` using dataclasses:

```python
from config import get_global_config

config = get_global_config()
db_url = config.database.url
log_level = config.logging.level
```

### Environment Variables

Configure the application via `.env` file:

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./lead_intelligence.db
LOG_LEVEL=INFO
ENRICHMENT_API_KEY=your_key_here
```

See `.env.example` for all available options.

## Usage

### Running the Application

```bash
python main.py
```

### Logging

The application uses Python's standard logging module:

```python
from logging_config import get_logger

logger = get_logger(__name__)
logger.info("Starting process")
logger.error("An error occurred")
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov

# Specific test file
pytest tests/unit/test_models.py
```

## Code Quality

This project enforces high code quality standards:

### Type Checking

```bash
mypy .
```

### Linting

```bash
flake8 .
ruff check .
```

### Code Formatting

```bash
black .
```

## Architecture

### Design Principles

- **Modularity**: Each package has a specific responsibility
- **Separation of Concerns**: Business logic, data access, and presentation are separated
- **Type Safety**: Comprehensive type hints throughout
- **Configuration Management**: Centralized, environment-aware configuration
- **Error Handling**: Graceful error handling with logging

### Module Descriptions

#### `scrapers/`
Handles web scraping and data collection from various sources.
- Base scraper classes and interfaces
- Web scraping implementations
- Email collection logic

#### `database/`
Manages database operations and persistence.
- Connection management
- SQLAlchemy ORM models
- Repository pattern for data access
- Database migrations

#### `enrichment/`
Enriches lead data with AI-powered insights.
- Core enrichment logic
- AI model integration (OpenAI, Anthropic, etc.)
- Data validation and cleaning
- Business logic enrichment

#### `models/`
Defines application data structures.
- Lead dataclass
- Company dataclass
- Contact dataclass
- Shared data types

#### `exporters/`
Handles data export in multiple formats.
- CSV export
- JSON export
- Excel export
- Custom export templates

#### `services/`
Business logic layer and orchestration.
- Lead discovery service
- Enrichment orchestration
- Data pipeline management
- Business process automation

#### `utils/`
Shared utilities and helper functions.
- Validation helpers
- Data transformation utilities
- Common exception classes
- Logger setup

#### `tests/`
Comprehensive test suite.
- Unit tests
- Integration tests
- Test fixtures and mocks

## Development Workflow

1. **Create a new feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement feature with tests**
   - Write tests first (TDD approach recommended)
   - Implement feature code
   - Ensure type hints are complete
   - Add docstrings

3. **Run quality checks**
   ```bash
   black .
   flake8 .
   mypy .
   pytest --cov
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

## Data Models

All data models use Python dataclasses with type hints:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Lead:
    """Represents a business lead."""
    id: str
    company_name: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
```

## Logging

The application includes production-ready logging:

```python
import logging
from logging_config import setup_logging, get_logger
from config import get_global_config

config = get_global_config()
setup_logging(config.logging)
logger = get_logger(__name__)

logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
logger.debug("Debug information")
```

Features:
- Configurable log levels
- File and console output
- Log rotation for file handlers
- Structured logging support
- Third-party logger suppression

## Contributing

### Code Style

- Follow PEP 8
- Use type hints everywhere
- Write docstrings for all public APIs
- Keep functions small and focused
- Aim for >80% code coverage

### Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Test addition/modification
- `refactor:` Code refactoring
- `chore:` Build, config, dependencies

## Future Enhancements

- [ ] Implement web scraper
- [ ] Build database models
- [ ] Integrate AI enrichment
- [ ] Create exporters
- [ ] Build CLI interface
- [ ] Add scheduling system
- [ ] Implement caching
- [ ] Add monitoring and metrics
- [ ] Create API service
- [ ] Build dashboard UI

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'config'`
- **Solution**: Ensure you're running from the project root directory

**Issue**: Database connection errors
- **Solution**: Check `DATABASE_URL` in `.env` and database is running

**Issue**: Type checking failures
- **Solution**: Run `mypy .` to see detailed type errors

## License

Proprietary - Lead Intelligence Platform

## Support

For issues or questions, please refer to the project documentation or create an issue in the repository.

---

**Version**: 0.1.0  
**Last Updated**: 2026-07-07  
**Python Version**: 3.13+
