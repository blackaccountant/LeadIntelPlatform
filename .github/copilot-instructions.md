# Lead Intelligence Platform - GitHub Copilot Instructions

## Project Overview

Lead Intelligence Platform is a production-grade, AI-assisted lead generation system designed to discover post-revenue US businesses and enrich them with useful contact information.

### Technology Stack

- **Python**: 3.13+
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Web Scraping**: BeautifulSoup4 with Selenium for dynamic content
- **Data Validation**: Pydantic
- **AI Enrichment**: OpenAI / Anthropic integration
- **Testing**: pytest with coverage
- **Code Quality**: black, flake8, mypy, ruff

## Project Structure

```
LeadIntelPlatform/
├── scrapers/               # Web scraping and data collection
├── database/               # Database models and operations
├── enrichment/             # AI-powered data enrichment
├── models/                 # Data models (dataclasses)
├── exporters/              # Data export functionality
├── services/               # Business logic layer
├── utils/                  # Utility functions and helpers
├── tests/                  # Unit and integration tests
├── main.py                 # Application entry point
├── config.py               # Configuration management
├── logging_config.py       # Logging setup
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## Development Guidelines

### Code Standards

- **Type Hints**: All functions must have type hints
- **Dataclasses**: Use `@dataclass` for data models
- **Documentation**: Every module, class, and public function needs docstrings
- **PEP 8**: Follow Python Enhancement Proposal 8 style guide
- **Testing**: Aim for >80% code coverage

### Configuration

- Environment-based configuration via `config.py`
- Use `.env` for local overrides (copy from `.env.example`)
- Logging configured in `logging_config.py`

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `scrapers/` | Discovers and collects lead data from sources |
| `database/` | Manages data persistence and ORM |
| `enrichment/` | Enhances leads with AI insights |
| `models/` | Defines typed data structures |
| `exporters/` | Exports processed leads to multiple formats |
| `services/` | Orchestrates business logic |
| `utils/` | Shared utilities and helpers |
| `tests/` | Automated test suite |

## Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Set Environment**: Copy `.env.example` to `.env` and configure
3. **Run Tests**: `pytest` to verify setup
4. **Implement Scraper**: Start with `scrapers/base.py`
5. **Build Database Layer**: Define models in `database/`
6. **Create Services**: Implement business logic in `services/`

## Important Notes

- This is the **initial project skeleton** - no scraping logic implemented yet
- All Python files use type hints and dataclasses as appropriate
- Production-ready logging is configured and ready to use
- Project follows a clean, scalable architecture
