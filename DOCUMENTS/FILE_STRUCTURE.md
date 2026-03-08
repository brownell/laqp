# Louisiana QSO Party - File Structure Reference

## Key Application Files

```
laqp/
├── web.py                      # ← Main Flask application (NOT app.py!)
├── processor.py                # Unified log processor
├── database.py                 # SQLite database management
├── batch.py                    # Batch log processing
├── leaderboards.py             # Leaderboard generator
├── generate_rankings.py        # Rankings calculation script
├── generate_final_report.py   # Final report HTML generator
│
├── config/
│   └── config.py               # Configuration (LEADERBOARDS, RANKINGS, etc.)
│
├── data/
│   ├── batch_input/            # Batch log files for batch.py
│   ├── database/               # SQLite database
│   │   └── laqp.db
│   ├── final_reports/          # Final HTML reports with all leaderboards
│   │   └── final_report_2026.html
│   └── reference_data/         # Static input files
│       ├── LA_Parish_Abbrevs.txt
│       └── WVE_Abbrevs.txt
│
├── templates/
│   ├── upload.html             # Log upload form
│   ├── results_lookup.html     # Results lookup page
│   └── *.html                  # Other templates
│
├── static/
│   ├── css/
│   │   ├── upload.css          # Main CSS
│   │   └── results.css         # Results page CSS
│   ├── js/
│   │   ├── upload.js           # Upload form JS
│   │   └── results_lookup.js   # Results lookup JS
│   └── images/
│       ├── fleur.svg           # Fleur-de-lis
│       └── sticker2.png        # Club logo
│
├── Dockerfile                  # Docker build instructions
├── docker-compose.yml          # Local Docker setup
├── fly.toml                    # Fly.io configuration
├── .dockerignore               # Docker ignore rules
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (create from .env.example)
```

## Critical: It's web.py, NOT app.py!

The main Flask application is **`web.py`**, not `app.py`.

### Dockerfile CMD
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", 
     "--access-logfile", "-", "--error-logfile", "-", "web:app"]
                                                           ^^^^
                                                           web.py with app variable
```

### Running Locally
```bash
# Development
python web.py

# Production with Gunicorn
gunicorn --bind 0.0.0.0:5000 web:app
```

### Environment Variable
```bash
export FLASK_APP=web.py
```

## Volume Structure (Docker/Fly.io)

```
/data/                          # Persistent volume
├── batch_input/                # Log files for batch processing
│   ├── K5ABC.log
│   └── W5XYZ.log
├── database/                   # SQLite database
│   └── laqp.db
├── final_reports/              # Generated final report HTML files
│   ├── final_report_2026.html
│   └── final_report_2025.html
└── reference_data/             # Static reference files (read-only)
    ├── LA_Parish_Abbrevs.txt
    └── WVE_Abbrevs.txt
```

## Import Structure

```python
# In other scripts (batch.py, generate_rankings.py, etc.)
from processor import process_single_log
from database import save_result, get_result
from config.config import LEADERBOARDS, RANKINGS

# web.py defines the Flask app
# Run it directly: python web.py
# Or via Gunicorn: gunicorn web:app
```

## Docker Build Process

1. **COPY** source files into `/app`
2. **CREATE** volume mount points in `/data`
3. **RUN** as non-root user `laqp`
4. **EXPOSE** port 5000
5. **CMD** runs `gunicorn web:app`

## Common Mistakes to Avoid

❌ **WRONG:**
```bash
python app.py                    # File doesn't exist!
gunicorn app:app                 # Wrong module name!
ENV FLASK_APP=app.py            # Wrong in Dockerfile!
```

✅ **CORRECT:**
```bash
python web.py                    # Correct!
gunicorn web:app                 # Correct!
ENV FLASK_APP=web.py            # Correct!
```

## Quick Reference

| Task | Command |
|------|---------|
| Run development | `python web.py` |
| Run production | `gunicorn web:app` |
| Process logs | `python batch.py` |
| Generate rankings | `python generate_rankings.py 2026` |
| Generate report | `python generate_final_report.py 2026` |
| Test locally | `docker-compose up -d --build` |
| Deploy to Fly.io | `flyctl deploy` |

The main Flask app is **web.py** - remember this when debugging or deploying!
