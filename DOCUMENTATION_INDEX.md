# 📚 Documentation Index

Welcome to the Lead Intelligence Platform! This guide helps you find the right documentation for your needs.

## 🚀 Getting Started (Pick One)

### I want to get running in 5 minutes
👉 **Read:** [QUICKSTART.md](QUICKSTART.md)
- Fastest way to try the platform
- Includes 3 methods to view the dashboard
- Copy-paste commands to get started

### I want to understand what this is
👉 **Read:** [README.md](README.md)
- Project overview and features
- Architecture diagram
- Technology stack

### I want to deploy to production
👉 **Read:** [DEPLOYMENT.md](DEPLOYMENT.md)
- Heroku, Railway, DigitalOcean instructions
- GitHub Pages deployment
- Environment configuration
- Security best practices

---

## 📖 Documentation by Purpose

### For Users (Using the Dashboard)
- [QUICKSTART.md](QUICKSTART.md) - Get the dashboard running
- [frontend/README.md](frontend/README.md) - Dashboard features and usage

### For Developers (Building & Extending)
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [README.md](README.md) - Architecture and design patterns
- Inline code comments - Docstrings in source files

### For DevOps (Deploying & Operating)
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup
- [QUICKSTART.md](QUICKSTART.md) - Local development
- Environment variables configuration

### For Integration (Using the API)
- [API_REFERENCE.md](API_REFERENCE.md) - Endpoint documentation
- [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) - API examples
- Postman collection (coming soon)

---

## 📁 File Guide

### Documentation Files
```
QUICKSTART.md              👈 Start here! 5-minute setup
DEPLOYMENT.md              Full production deployment guide
API_REFERENCE.md           Complete API endpoint documentation
README.md                  Project overview and architecture
COMPLETION_SUMMARY.md      What's been delivered
```

### Python Files (Backend)
```
main.py                    CLI entry point
api.py                     Flask REST API server
add_sample_leads.py        Populate test data
serve_frontend.py          Development frontend server

database/                  Data persistence layer
models/                    Domain models
services/                  Business logic
adapters/                  Data source adapters
tests/                     Test suite (10 tests)
```

### Frontend Files (Dashboard)
```
frontend/index.html        Professional dashboard UI
frontend/app.js            Interactive JavaScript (250+ lines)
frontend/styles.css        Responsive styling (480+ lines)
frontend/README.md         Frontend documentation
frontend/.nojekyll         GitHub Pages config
```

---

## 🎯 Common Tasks

### "I want to view the dashboard"
1. Open [frontend/index.html](frontend/index.html) in your browser
   - Or: `python main.py dashboard --output exports/dashboard.html`

### "I want to run the API server"
```bash
python main.py api
# Runs on http://localhost:5000
# Serves /api/leads, /api/stats, /api/health
```

### "I want to add more leads"
```bash
# Option 1: Add sample data
python add_sample_leads.py

# Option 2: Run a discovery campaign
python main.py campaign --country US --limit 100
```

### "I want to export leads to CSV"
```bash
python main.py export --output leads.csv
```

### "I want to deploy to GitHub Pages"
See [DEPLOYMENT.md](DEPLOYMENT.md) → "Deploying to GitHub Pages"

### "I want to deploy the API"
See [DEPLOYMENT.md](DEPLOYMENT.md) → "Deploying Backend API"

### "I want to integrate with my CRM"
See [API_REFERENCE.md](API_REFERENCE.md) → "Integration Examples"

---

## 🧪 Testing & Validation

### Run All Tests
```bash
python -m pytest tests/ -v
# Should see: 10/10 tests PASSED
```

### Test the API
```bash
# Health check
curl http://localhost:5000/api/health

# Get all leads
curl http://localhost:5000/api/leads

# Get statistics
curl http://localhost:5000/api/stats
```

### Verify Database
```bash
# Count leads
python main.py stats

# View database
sqlite3 lead_intelligence.db ".tables"
```

---

## 📋 Quick Reference

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/leads` | GET | List all leads (JSON) |
| `/api/leads/<id>` | GET | Get single lead |
| `/api/stats` | GET | Campaign statistics |
| `/api/health` | GET | Health check |

### CLI Commands
| Command | Purpose |
|---------|---------|
| `python main.py api` | Start API server |
| `python main.py campaign` | Run lead discovery |
| `python main.py export` | Export leads to CSV |
| `python main.py dashboard` | Generate HTML dashboard |
| `python main.py analyze-website` | Analyze single website |
| `python main.py stats` | Show database stats |

### URLs
| URL | Purpose | Status |
|-----|---------|--------|
| http://localhost:5000/api/leads | API endpoint | ✅ Working |
| http://localhost:8000 | Frontend server | ✅ Ready |
| file:///.../frontend/index.html | Standalone dashboard | ✅ Working |

---

## 💡 Key Concepts

### Adapter Pattern
New data sources are "adapters" that implement the fetch() method:
- WebsiteAdapter - Scrapes company websites
- OpenCorporatesAdapter - Queries company database
- BusinessDirectoryAdapter - Searches business registries

### Lead Qualification
Leads are filtered by business rules:
- Must be in US
- Must have website
- Must not be government/nonprofit
- No duplicates

### Lead Status
- `new` - Just discovered
- `qualified` - Passed all business rules
- `rejected` - Failed business rules
- `contacted` - Already reached out to

---

## 🔍 Finding Specific Information

### "How do I ...?"
Use QUICKSTART.md

### "What endpoints are available?"
Use API_REFERENCE.md

### "How do I deploy?"
Use DEPLOYMENT.md

### "What's the architecture?"
Use README.md

### "What's been completed?"
Use COMPLETION_SUMMARY.md

---

## 📞 Support Resources

### Within Documentation
- README.md - Technical overview
- QUICKSTART.md - 5-minute setup
- DEPLOYMENT.md - Production guide
- API_REFERENCE.md - API endpoints
- COMPLETION_SUMMARY.md - What's included

### In Code
- Docstrings in all Python modules
- Comments explaining complex logic
- Type hints for clarity
- Test files as usage examples

### Online Resources
- [Python Documentation](https://docs.python.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [GitHub Pages Guide](https://pages.github.com/)

---

## ✅ Verification Checklist

Before going to production:
- [ ] Read QUICKSTART.md
- [ ] Run `python main.py api` successfully
- [ ] Open dashboard in browser
- [ ] Run `python -m pytest -v` (all tests pass)
- [ ] Review API_REFERENCE.md for your integration
- [ ] Read DEPLOYMENT.md for your platform
- [ ] Set up environment variables
- [ ] Configure database
- [ ] Enable CORS if needed
- [ ] Plan backup strategy

---

## 🎓 Learning Path

**Beginner** (30 minutes)
1. Read QUICKSTART.md
2. Run `python main.py api`
3. Open frontend/index.html
4. Play with search and filters

**Intermediate** (1-2 hours)
1. Read README.md for architecture
2. Review API_REFERENCE.md
3. Run a campaign: `python main.py campaign --country US --limit 10`
4. Export results: `python main.py export --output leads.csv`

**Advanced** (2-4 hours)
1. Study DEPLOYMENT.md for your platform
2. Read source code in adapters/, services/
3. Create custom adapter
4. Deploy to GitHub Pages
5. Deploy API to Heroku/Railway

---

## 🚀 Next Steps

1. **Immediate**
   - [ ] Open QUICKSTART.md
   - [ ] Run API server
   - [ ] View dashboard

2. **Today**
   - [ ] Add sample leads
   - [ ] Run a campaign
   - [ ] Export to CSV

3. **This Week**
   - [ ] Deploy to GitHub Pages
   - [ ] Deploy API to cloud
   - [ ] Connect dashboard to API

4. **This Month**
   - [ ] Add authentication
   - [ ] Integrate with CRM
   - [ ] Scale database

---

## 📊 Platform Status

**Current Status:** ✅ **PRODUCTION READY**

- ✅ REST API - Fully functional
- ✅ Dashboard - All features working
- ✅ Database - SQLite with sample data
- ✅ Tests - 10/10 passing
- ✅ Documentation - Complete
- ✅ CLI - All commands working
- ✅ Deployment - Ready for GitHub Pages

---

## 🎉 Let's Get Started!

Choose your path:

### 🏃 Fast Track (5 min)
→ [QUICKSTART.md](QUICKSTART.md)

### 🏗️ Build & Integrate (1-2 hours)
→ [README.md](README.md) + [API_REFERENCE.md](API_REFERENCE.md)

### 🚀 Deploy to Production (30 min)
→ [DEPLOYMENT.md](DEPLOYMENT.md)

---

Good luck! The Lead Intelligence Platform is ready to discover, qualify, and export your leads. 🎯
