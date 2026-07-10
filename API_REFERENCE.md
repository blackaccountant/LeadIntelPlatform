# API Reference & Technical Specification

## REST API Endpoints

### 1. List All Leads
```
GET /api/leads
```

**Description:** Returns all leads in the database

**Response Format:**
```json
[
  {
    "id": "uuid-string",
    "company": {
      "name": "Company Name",
      "website": "https://example.com",
      "industry": "software"
    },
    "website": "https://example.com",
    "email": "contact@example.com",
    "phone": "+1 (555) 123-4567",
    "status": "qualified",
    "confidence_score": 0.92,
    "source": "opencorporates",
    "tags": ["sample", "software"],
    "notes": []
  }
]
```

**Status Codes:**
- `200 OK` - Successfully returned leads
- `500 Internal Server Error` - Database error

**Example:**
```bash
curl http://localhost:5000/api/leads
```

---

### 2. Get Single Lead
```
GET /api/leads/<lead_id>
```

**Parameters:**
- `lead_id` (path parameter, UUID string)

**Response Format:**
```json
{
  "id": "c64a9e0c-d067-4586-8a5b-98174631432a",
  "company": {
    "name": "TechFlow Solutions",
    "website": "https://techflow.example",
    "industry": "software"
  },
  "website": "https://techflow.example",
  "email": "sales@techflow.example",
  "phone": "+1 (555) 111-1111",
  "status": "qualified",
  "confidence_score": 0.95,
  "source": "website_crawler",
  "tags": ["sample", "software"],
  "notes": []
}
```

**Status Codes:**
- `200 OK` - Lead found
- `404 Not Found` - Lead doesn't exist
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/leads/c64a9e0c-d067-4586-8a5b-98174631432a
```

---

### 3. Campaign Statistics
```
GET /api/stats
```

**Description:** Returns aggregated statistics about leads

**Response Format:**
```json
{
  "total_leads": 5,
  "qualified_leads": 2,
  "pending_leads": 3,
  "qualification_rate": 40.0
}
```

**Metrics:**
- `total_leads`: Total leads in database
- `qualified_leads`: Count with status="qualified"
- `pending_leads`: Count with status="new" or "contacted"
- `qualification_rate`: Percentage (qualified/total * 100)

**Status Codes:**
- `200 OK` - Statistics calculated successfully
- `500 Internal Server Error` - Database error

**Example:**
```bash
curl http://localhost:5000/api/stats
```

---

### 4. Health Check
```
GET /api/health
```

**Description:** Verifies API is running and responding

**Response Format:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK` - API is healthy

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

## Data Models

### Lead Object
```python
{
  "id": str,                    # UUID
  "company": Company,           # Company object
  "website": str,               # Company website URL
  "email": str,                 # Contact email
  "phone": str,                 # Contact phone (normalized)
  "status": str,                # "new", "qualified", "rejected", "contacted"
  "confidence_score": float,    # 0.0 to 1.0
  "source": str,                # "website_crawler", "opencorporates", "business_registry"
  "tags": list[str],            # Array of tags
  "notes": list[str],           # Array of notes
}
```

### Company Object
```python
{
  "name": str,                  # Company legal name
  "website": str,               # Website URL
  "industry": str,              # Industry category
}
```

### Status Values
- `"new"` - Recently discovered
- `"qualified"` - Meets all business rules
- `"rejected"` - Failed qualification
- `"contacted"` - Already reached out

### Source Values
- `"website_crawler"` - Discovered via website scraping
- `"opencorporates"` - From OpenCorporates API
- `"business_registry"` - From business directory
- Custom sources from new adapters

---

## Error Handling

### Error Response Format
```json
{
  "error": "Error message describing what went wrong"
}
```

### Common Errors

#### 500 Internal Server Error
```json
{
  "error": "Database connection failed"
}
```
**Solution:** Check database file exists and is readable

#### 404 Not Found
```json
{
  "error": "Lead not found"
}
```
**Solution:** Verify the lead_id is correct (use /api/leads to list)

---

## Authentication & CORS

### CORS Headers
All responses include:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### Authentication
Currently: No authentication required (public API)

To add authentication (optional):
```python
from flask_jwt_extended import JWTManager, jwt_required

jwt = JWTManager(app)

@app.route('/api/leads')
@jwt_required()
def get_leads():
    ...
```

---

## Rate Limiting

Current: No rate limiting

To add rate limiting:
```bash
pip install Flask-Limiter

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/leads')
@limiter.limit("100 per hour")
def get_leads():
    ...
```

---

## Database Schema

### Leads Table
```sql
CREATE TABLE leads (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    contact_id TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    confidence_score REAL,
    source TEXT,
    tags TEXT,
    notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
```

### Companies Table
```sql
CREATE TABLE companies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    website TEXT,
    domain TEXT,
    industry TEXT
);
```

### Contacts Table
```sql
CREATE TABLE contacts (
    id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    address_id TEXT,
    FOREIGN KEY (address_id) REFERENCES addresses(id)
);
```

### Addresses Table
```sql
CREATE TABLE addresses (
    id TEXT PRIMARY KEY,
    city TEXT,
    region TEXT,
    postal_code TEXT,
    country TEXT
);
```

---

## Performance Characteristics

### Query Times (with 5 leads)
| Operation | Time |
|-----------|------|
| GET /api/leads | ~10-20ms |
| GET /api/stats | ~10-20ms |
| GET /api/health | ~1-5ms |
| Single lead lookup | ~5-10ms |

### Scaling
- **1000 leads**: ~50-100ms for list all
- **10000 leads**: ~200-500ms (recommend pagination)
- **100000+ leads**: Requires database indexing

---

## Usage Examples

### Python
```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Get all leads
response = requests.get(f"{BASE_URL}/api/leads")
leads = response.json()
print(f"Found {len(leads)} leads")

# Get specific lead
lead_id = leads[0]['id']
lead = requests.get(f"{BASE_URL}/api/leads/{lead_id}").json()
print(f"Lead: {lead['company']['name']}")

# Get stats
stats = requests.get(f"{BASE_URL}/api/stats").json()
print(f"Qualified rate: {stats['qualification_rate']}%")
```

### JavaScript
```javascript
const API_BASE_URL = "http://localhost:5000";

// Fetch all leads
fetch(`${API_BASE_URL}/api/leads`)
  .then(response => response.json())
  .then(leads => {
    console.log(`Found ${leads.length} leads`);
    leads.forEach(lead => {
      console.log(`- ${lead.company.name}: ${lead.email}`);
    });
  });

// Fetch stats
fetch(`${API_BASE_URL}/api/stats`)
  .then(response => response.json())
  .then(stats => {
    console.log(`Total: ${stats.total_leads}`);
    console.log(`Qualified: ${stats.qualified_leads}`);
  });
```

### PowerShell
```powershell
$API_BASE_URL = "http://localhost:5000"

# Get all leads
$leads = Invoke-WebRequest -Uri "$API_BASE_URL/api/leads" | ConvertFrom-Json
Write-Host "Found $($leads.Count) leads"

# Get stats
$stats = Invoke-WebRequest -Uri "$API_BASE_URL/api/stats" | ConvertFrom-Json
Write-Host "Total: $($stats.total_leads), Qualified: $($stats.qualified_leads)"
```

### cURL
```bash
# Health check
curl http://localhost:5000/api/health

# List all leads
curl http://localhost:5000/api/leads

# Get specific lead
curl http://localhost:5000/api/leads/c64a9e0c-d067-4586-8a5b-98174631432a

# Get stats
curl http://localhost:5000/api/stats

# Pretty print JSON
curl http://localhost:5000/api/leads | python -m json.tool
```

---

## Deployment Configuration

### Environment Variables
```bash
# Flask
FLASK_ENV=production              # or 'development'
FLASK_DEBUG=0                     # 0 for production, 1 for dev

# Database
DATABASE_URL=sqlite:///lead_intelligence.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost:5432/leads

# Optional: AI Enrichment
OPENCORPORATES_API_TOKEN=your_token

# CORS
CORS_ORIGINS=https://yourdomain.com
```

### Production Checklist
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=0
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Add authentication if needed
- [ ] Enable rate limiting
- [ ] Set up monitoring/logging
- [ ] Configure backups
- [ ] Use production WSGI server (gunicorn, uWSGI)

### Production WSGI Command
```bash
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

---

## Troubleshooting

### API won't start
```bash
# Check if port is in use
lsof -i :5000

# Kill process using port
kill -9 <PID>

# Try different port
python main.py api --port 8080
```

### CORS errors in browser
```javascript
// Error: CORS policy blocked request
// Solution: Ensure frontend and API on same domain or
// API has proper CORS headers (should be automatic)
```

### Database errors
```bash
# Recreate database
rm lead_intelligence.db
python main.py stats  # Creates empty DB

# Check database integrity
sqlite3 lead_intelligence.db ".check"
```

### 404 errors on API
```bash
# Verify endpoint exists
curl http://localhost:5000/api/health

# Check Flask app is running
ps aux | grep "main.py api"

# Check logs for errors
tail -f logs/app.log
```

---

## Integration Examples

### With CRM (Salesforce)
```python
import requests
from salesforce import Salesforce

api_leads = requests.get("http://localhost:5000/api/leads").json()
sf = Salesforce(instance_url="...", session_id="...")

for lead in api_leads:
    sf.Lead.create({
        "Company": lead['company']['name'],
        "Email": lead['email'],
        "Phone": lead['phone'],
        "Industry": lead['company']['industry'],
    })
```

### With Email Outreach (SendGrid)
```python
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

leads = requests.get("http://localhost:5000/api/leads").json()

for lead in leads:
    if lead['status'] == 'qualified':
        message = Mail(
            from_email="sales@company.com",
            to_emails=lead['email'],
            subject="Partnership Opportunity",
            html_content="..."
        )
        SendGridAPIClient("SENDGRID_API_KEY").send(message)
```

### With Analytics (Amplitude)
```python
import requests
from amplitude import Amplitude

client = Amplitude("YOUR_API_KEY")
leads = requests.get("http://localhost:5000/api/leads").json()

for lead in leads:
    client.track(
        user_id=lead['id'],
        event_type="lead_discovered",
        event_properties={
            "company": lead['company']['name'],
            "score": lead['confidence_score'],
            "source": lead['source'],
        }
    )
```

---

## API Versioning

Current API: **v1.0**

To add versioning:
```python
@app.route('/api/v1/leads', ...)
@app.route('/api/v2/leads', ...)  # Future version
```

---

## Support & Documentation

- API runs on: http://localhost:5000
- Frontend runs on: http://localhost:8000
- Database: lead_intelligence.db
- Logs: logs/app.log

For more information, see [DEPLOYMENT.md](DEPLOYMENT.md) and [QUICKSTART.md](QUICKSTART.md)
