# Lead Intelligence Dashboard Frontend

A modern, responsive web dashboard for viewing and managing B2B leads discovered and enriched by the Lead Intelligence Platform.

## Features

- 📊 **Real-time Statistics** - Total leads, qualified leads, pending leads, and qualification rate
- 🔍 **Advanced Search & Filtering** - Filter by status, search by company name, email, or domain
- 📑 **Pagination** - Browse leads with configurable page sizes
- 📥 **CSV Export** - Download leads for use in CRM, email, or analytics tools
- 🎨 **Responsive Design** - Works on desktop, tablet, and mobile devices
- 🚀 **Lightweight** - Pure HTML, CSS, and JavaScript with no build step required
- 🔗 **API Ready** - Can fetch data from the Python backend API or use local data

## Directory Structure

```
frontend/
├── index.html      # Main dashboard page
├── styles.css      # Styling and responsive layout
├── app.js          # Interactive functionality
├── .nojekyll       # Tells GitHub Pages to serve files as-is
└── README.md       # This file
```

## Local Development

### Prerequisites
- A modern web browser (Chrome, Firefox, Safari, Edge)
- Python 3.13+ (for running the backend API)

### Running Locally

1. Open `index.html` in your browser directly:
   ```bash
   open frontend/index.html
   ```

2. Or use a simple local server:
   ```bash
   cd frontend
   python -m http.server 8000
   ```
   Then visit `http://localhost:8000`

## Backend Integration

The dashboard can fetch lead data from the Python backend API. To enable this:

1. Start the Flask/FastAPI backend:
   ```bash
   python main.py api
   ```

2. The frontend will automatically attempt to fetch from `/api/leads`

3. If the API is not available, the dashboard will display sample data

### API Endpoint

Expected endpoint: `GET /api/leads`

Response format:
```json
[
  {
    "id": "lead-uuid",
    "company": { "name": "Company Name" },
    "website": "https://company.example",
    "email": "contact@company.example",
    "phone": "+1 (555) 123-4567",
    "status": "qualified",
    "confidence_score": 0.92,
    "source": "opencorporates"
  }
]
```

## Deployment to GitHub Pages

### Option 1: Deploy to GitHub Pages Automatically

1. Push the `frontend` directory to your GitHub repository:
   ```bash
   git add frontend/
   git commit -m "Add dashboard frontend"
   git push
   ```

2. Go to your repository Settings → Pages
3. Under "Source", select `main` branch and `/frontend` folder
4. Click Save
5. Your dashboard will be available at `https://yourusername.github.io/LeadIntelPlatform`

### Option 2: Deploy with Custom Domain

1. Configure your custom domain in GitHub Pages settings
2. Update the `CNAME` file with your domain
3. Configure DNS records as instructed by GitHub

### Option 3: Deploy with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Dashboard to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/upload-pages-artifact@v1
        with:
          path: 'frontend'
      - uses: actions/deploy-pages@v1
```

## Features & Capabilities

### Dashboard Widgets

- **Total Leads** - Count of all discovered leads
- **Qualified Leads** - Count of leads passing qualification rules
- **Pending Review** - Count of leads awaiting manual review
- **Qualification Rate** - Percentage of leads qualified

### Data Table

- Sortable columns (click header to sort)
- Clickable website links (opens in new tab)
- Clickable email addresses (opens mail client)
- Clickable phone numbers (opens dialer)
- Status badges with color coding

### Search & Filter

- **Search Box** - Full-text search across company name, email, domain
- **Status Filter** - Filter by new, qualified, rejected, contacted
- **All Filter** - Reset to show all leads

### Actions

- **Export CSV** - Download filtered leads as CSV
- **Refresh** - Reload data from backend

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- **Page Load**: < 1s
- **No external dependencies** - All CSS and JS is inline
- **Optimized for 1000+ leads** - Uses pagination for performance

## Customization

### Change Colors

Edit `styles.css` CSS variables:

```css
:root {
    --primary: #3b82f6;      /* Primary blue */
    --secondary: #8b5cf6;    /* Purple accent */
    --success: #10b981;      /* Green */
    --warning: #f59e0b;      /* Orange */
    --danger: #ef4444;       /* Red */
}
```

### Change Page Size

In `app.js`, modify:

```javascript
this.pageSize = 10; // Change to 20, 50, etc.
```

### Add Custom Columns

Edit the `renderRow()` method in `app.js` to add more table columns

## Troubleshooting

### Dashboard shows "No leads available"
- Ensure the backend API is running: `python main.py api`
- Check browser console for errors: F12 → Console
- Verify CORS headers are configured correctly

### Styling looks broken on mobile
- Clear browser cache: Ctrl+Shift+Delete
- Ensure viewport meta tag is present in `index.html`

### Export CSV is empty
- Ensure leads are loaded in the dashboard
- Check that data is being filtered correctly

## Future Enhancements

- [ ] Real-time lead updates with WebSockets
- [ ] Advanced filtering by industry, location, revenue
- [ ] Lead quality scoring dashboard
- [ ] Campaign performance metrics
- [ ] AI-powered lead recommendations
- [ ] Email integration for outreach
- [ ] CRM sync (Salesforce, HubSpot)

## Contributing

To contribute improvements to the dashboard:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test locally
4. Push to your fork: `git push origin feature/your-feature`
5. Create a Pull Request

## License

This dashboard is part of the Lead Intelligence Platform project and is licensed under the same terms.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Review the main [README.md](../README.md) for project-level documentation
