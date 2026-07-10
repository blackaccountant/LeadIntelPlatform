# Lead Intelligence Platform - Deployment Guide

## Quick Start

### Prerequisites
- Python 3.13+
- Git (for version control)
- Modern web browser

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd LeadIntelPlatform

# Install dependencies
pip install -r requirements.txt

# Add sample data (optional, for testing)
python add_sample_leads.py
```

## Running Locally

### Method 1: API + Static Frontend (Recommended)

**Terminal 1 - Start API Server:**
```bash
python main.py api --port 5000
# Runs on http://localhost:5000
```

**Terminal 2 - Start Frontend Server:**
```bash
python serve_frontend.py
# Runs on http://localhost:8000
# Automatically loads API data from http://localhost:5000/api/leads
```

Then open: `http://localhost:8000`

### Method 2: Standalone Dashboard (No API)

```bash
python main.py dashboard --output dashboard.html
```

Open `dashboard.html` in your browser.

### Method 3: Direct File Access

Open `frontend/index.html` directly in your browser.
- Will display sample data
- No API required
- Good for offline demo

## Running Campaigns

### Example: Discover US Software Companies

```bash
python main.py campaign --country US --industry software --limit 100
```

### Example: Export Results to CSV

```bash
python main.py campaign --country US --export results.csv
```

### Campaign Options

```
--country          Country code (e.g., US, UK) [default: US]
--state            State/region name [optional]
--city             City name [optional]
--industry         Industry keyword [optional]
--keyword          Search keyword [optional]
--limit            Max results [default: 100]
--export           CSV export path [optional]
--ai               Enable AI enrichment [optional]
--dry-run          Test without saving [optional]
```

## Deploying to GitHub Pages

### Step 1: Push Frontend to GitHub

```bash
# Ensure frontend/ directory is ready
git add frontend/
git commit -m "Add Lead Intelligence Dashboard"
git push origin main
```

### Step 2: Configure GitHub Pages

1. Go to repository Settings → Pages
2. Select `main` branch
3. Choose `/frontend` folder
4. Click Save
5. Wait for GitHub Pages to build (usually 1-2 minutes)

### Step 3: Access Dashboard

Your dashboard is now live at:
```
https://YOUR_USERNAME.github.io/LeadIntelPlatform/
```

### Step 4: Connect to Backend API (Optional)

Update `frontend/app.js` to point to your backend:

```javascript
// In LeadsDashboard constructor, change:
const API_BASE_URL = 'http://localhost:5000'; // local
// To:
const API_BASE_URL = 'https://api.example.com'; // production
```

## Deploying Backend API

### Option 1: Heroku Deployment

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-lead-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set OPENCORPORATES_API_TOKEN=your_token

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

API will run at: `https://your-lead-api.herokuapp.com`

### Option 2: Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

### Option 3: DigitalOcean Deployment

```bash
# Create droplet with Python
# SSH into droplet
ssh root@your_droplet_ip

# Clone repo
git clone <repo>
cd LeadIntelPlatform

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# Use systemd for persistence (see below)
```

### Setup Systemd Service (Linux)

Create `/etc/systemd/system/lead-api.service`:

```ini
[Unit]
Description=Lead Intelligence API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/LeadIntelPlatform
ExecStart=/usr/bin/python3 main.py api --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lead-api
sudo systemctl start lead-api
```

## Environment Configuration

### Local Development (.env)

```bash
# Database
DATABASE_URL=sqlite:///lead_intelligence.db

# API
FLASK_ENV=development
FLASK_DEBUG=1

# AI Enrichment (optional)
OPENCORPORATES_API_TOKEN=your_token_here
```

### Production (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/leads

# API
FLASK_ENV=production
FLASK_DEBUG=0

# CORS (allow GitHub Pages)
CORS_ORIGINS=https://username.github.io

# AI Enrichment
OPENCORPORATES_API_TOKEN=your_token_here
```

## Database Management

### Backup

```bash
# SQLite
cp lead_intelligence.db lead_intelligence.backup.db

# PostgreSQL
pg_dump -h localhost -U user leads_db > backup.sql
```

### Restore

```bash
# SQLite
cp lead_intelligence.backup.db lead_intelligence.db

# PostgreSQL
psql -h localhost -U user leads_db < backup.sql
```

## Monitoring & Logging

### View Logs

```bash
# Local server
tail -f logs/app.log

# Heroku
heroku logs --tail

# Systemd service
journalctl -u lead-api -f
```

### Performance Monitoring

```bash
# Count leads
python main.py stats

# Check database size
sqlite3 lead_intelligence.db "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size();"
```

## Troubleshooting

### Issue: API won't start

```bash
# Check if port is in use
lsof -i :5000

# Kill process
kill -9 <PID>

# Try different port
python main.py api --port 8000
```

### Issue: Frontend can't reach API

```bash
# Check CORS headers
curl -H "Origin: http://localhost:8000" \
  http://localhost:5000/api/health

# Check firewall
sudo ufw allow 5000/tcp
```

### Issue: Database errors

```bash
# Recreate tables
python -c "from database.database import DatabaseManager; db = DatabaseManager('sqlite:///lead_intelligence.db'); db.create_tables()"

# Clear database
rm lead_intelligence.db
python main.py stats  # Will recreate
```

## Performance Optimization

### API Response Caching

```bash
# Install Redis
pip install redis

# Use caching decorator
from functools import lru_cache

@app.route("/api/leads")
@lru_cache(maxsize=128)
def get_leads():
    ...
```

### Database Indexing

```bash
# Add indices for common searches
CREATE INDEX idx_status ON leads(status);
CREATE INDEX idx_source ON leads(source);
CREATE INDEX idx_website ON companies(website);
```

### Load Testing

```bash
pip install locust

# Create locustfile.py and run
locust -f locustfile.py --host=http://localhost:5000
```

## Security Best Practices

1. **Never commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use HTTPS in production**
   ```bash
   # Use nginx/apache with SSL certificates
   # Or use Heroku's automatic SSL
   ```

3. **Validate input**
   ```python
   from pydantic import BaseModel, validator
   ```

4. **Rate limiting**
   ```bash
   pip install Flask-Limiter
   ```

5. **Authentication** (optional)
   ```bash
   pip install Flask-JWT-Extended
   ```

## Scaling for Production

### For 1000+ leads:
- Add database indices
- Implement pagination API
- Use Redis for caching
- Consider CDN for static files

### For high traffic:
- Load balance with multiple API instances
- Use message queue (Celery)
- Implement async jobs
- Monitor with NewRelic/DataDog

## Support & Documentation

- **API Docs**: `http://localhost:5000/api/health`
- **Frontend Docs**: [frontend/README.md](../frontend/README.md)
- **Main Docs**: [README.md](../README.md)

## License

This project is licensed under the same terms as the main repository.
