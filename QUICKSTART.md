# Quick Start Guide - Lead Intelligence Platform

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies (1 minute)
```bash
cd c:\Users\USER\LeadIntelPlatform
pip install -r requirements.txt
```

### Step 2: Add Sample Data (30 seconds)
```bash
python add_sample_leads.py
```
✅ Creates 5 sample companies in the database

### Step 3: Start API Server (in Terminal 1)
```bash
python main.py api
```
✅ API running on http://localhost:5000

### Step 4: View Dashboard
Open one of these in your browser:

**Option A - Standalone (offline):**
```
file:///c:/Users/USER/LeadIntelPlatform/frontend/index.html
```

**Option B - With API (online):**
Open `http://localhost:8000` after step 5

### Step 5: Optional - Start Frontend Server (Terminal 2)
```bash
python serve_frontend.py
```
✅ Frontend running on http://localhost:8000

---

## 📊 Key URLs

| URL | Purpose | Status |
|-----|---------|--------|
| http://localhost:5000/api/leads | List all leads | ✅ Working |
| http://localhost:5000/api/health | Health check | ✅ Working |
| http://localhost:5000/api/stats | Campaign statistics | ✅ Working |
| http://localhost:8000 | Dashboard UI | ✅ Working |
| file:///c:/Users/USER/LeadIntelPlatform/frontend/index.html | Standalone dashboard | ✅ Working |

---

## 🎯 Common Commands

### View Dashboard (Offline)
```bash
# Desktop: Right-click frontend/index.html → Open with Browser
# Or in browser: Ctrl+O → select frontend/index.html
```

### Run Discovery Campaign
```bash
python main.py campaign --country US --limit 10
```

### Export Leads to CSV
```bash
python main.py export --output leads.csv
```

### Generate HTML Dashboard
```bash
python main.py dashboard --output exports/dashboard.html
```

### Check Database Stats
```bash
python main.py stats
```

### Analyze a Website
```bash
python main.py analyze-website https://example.com
```

---

## 🧪 Testing the API

### Using curl (PowerShell)
```powershell
# Get all leads
Invoke-WebRequest http://localhost:5000/api/leads | ConvertFrom-Json

# Get stats
Invoke-WebRequest http://localhost:5000/api/stats | ConvertFrom-Json

# Health check
Invoke-WebRequest http://localhost:5000/api/health
```

### Using Python
```python
import requests

# Get all leads
response = requests.get('http://localhost:5000/api/leads')
leads = response.json()
print(f"Found {len(leads)} leads")

# Get stats
stats = requests.get('http://localhost:5000/api/stats').json()
print(f"Total: {stats['total_leads']}, Qualified: {stats['qualified_leads']}")
```

---

## 📁 Project Structure

```
LeadIntelPlatform/
├── main.py                    ← Entry point for all commands
├── api.py                     ← REST API server (NEW)
├── add_sample_leads.py        ← Sample data generator (NEW)
├── serve_frontend.py          ← Frontend dev server (NEW)
├── requirements.txt           ← Dependencies
├── config.py                  ← Configuration
├── DEPLOYMENT.md              ← Detailed deployment guide (NEW)
│
├── frontend/                  ← Dashboard UI (NEW)
│   ├── index.html            ← Main page
│   ├── app.js                ← JavaScript logic
│   ├── styles.css            ← Styling
│   └── README.md             ← Frontend docs
│
├── database/                  ← Data persistence
├── models/                    ← Data models
├── services/                  ← Business logic
├── adapters/                  ← Data sources
└── tests/                     ← Test suite
```

---

## ⚙️ What's Included

✅ **REST API** - Serves lead data as JSON
✅ **Dashboard** - Professional web UI with search, filter, export
✅ **Database** - SQLite with leads, companies, contacts
✅ **CLI** - Command-line tools for campaigns, export, analysis
✅ **Sample Data** - 5 test companies pre-configured
✅ **Documentation** - Complete user and developer guides

---

## 🔧 Configuration

### Default Settings
- Database: SQLite (lead_intelligence.db)
- API Port: 5000
- Frontend Port: 8000
- Sample Database: lead_intelligence.db

### Custom Configuration

Edit `config.py` or create `.env` file:

```bash
# .env (create this file in project root)
DATABASE_URL=sqlite:///lead_intelligence.db
OPENCORPORATES_API_TOKEN=your_api_token
FLASK_ENV=development
```

---

## 🐛 Troubleshooting

### "Port already in use" error?
```bash
# Kill the process using the port
taskkill /F /IM python.exe

# Or use a different port
python main.py api --port 8080
```

### "Module not found" error?
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Dashboard shows no data?
```bash
# Populate sample data
python add_sample_leads.py

# Or run a campaign
python main.py campaign --country US --limit 5
```

### API won't connect?
```bash
# Check if server is running
# If not, run: python main.py api

# Check if CORS is enabled (should be automatic)
# Verify port: netstat -ano | findstr 5000
```

---

## 📈 Next Steps

1. **Add Real Data**
   ```bash
   # Set OpenCorporates API token in .env
   python main.py campaign --country US --limit 100
   ```

2. **Deploy Dashboard**
   - Push `frontend/` to GitHub Pages
   - Dashboard becomes available globally

3. **Deploy API**
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
   - Use Heroku, Railway, or your own server

4. **Integrate with CRM**
   - Export to CSV and import to Salesforce
   - Or connect via API to HubSpot

---

## 📚 Learn More

- [Deployment Guide](DEPLOYMENT.md) - Full production setup
- [Frontend Documentation](frontend/README.md) - Dashboard features
- [Main README](README.md) - Project overview
- [API Documentation](api.py) - Endpoint reference

---

## ✨ You're All Set!

Your Lead Intelligence Platform is ready to use:

1. **API Running** → Serving lead data
2. **Dashboard Available** → Professional UI ready
3. **Sample Data Loaded** → Ready to test
4. **Commands Ready** → Run campaigns, export, analyze

**Start with**: `python main.py api` then open `frontend/index.html`

Good luck! 🚀
