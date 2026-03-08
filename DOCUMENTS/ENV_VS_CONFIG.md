# Environment Variables vs Configuration

## Quick Answer

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**What goes where:**
- **`.env`** → Secrets, paths, environment-specific settings
- **`config.py`** → Contest rules, leaderboards, application logic

## 🔑 Generating SECRET_KEY

### Recommended Method

```bash
# Generate a 64-character hex string
python3 -c "import secrets; print(secrets.token_hex(32))"

# Copy output to .env file
# Example output: 3a7f8b2e9c1d4a6f5e8b7c2a1d3f9e4b8c7a2f1e6d9b3c5a8e2f7d1b4c6a9e3f
```

### Alternative Methods

```bash
# Using openssl
openssl rand -hex 32

# Using UUID (less secure but works)
python3 -c "import uuid; print(uuid.uuid4().hex + uuid.uuid4().hex)"

# Using /dev/urandom (Linux/Mac)
head -c 32 /dev/urandom | base64
```

## 📋 Split Strategy

### ✅ Put in .env (Secrets & Environment)

**Definitely in .env:**
- `SECRET_KEY` - Flask session encryption
- `DATABASE_PATH` - Database location
- `BATCH_INPUT_DIR` - Input directory
- `FINAL_REPORTS_DIR` - Output directory
- `REFERENCE_DATA_DIR` - Reference data location
- `FLASK_ENV` - development/production
- `CONTEST_YEAR` - Current year

**Why?**
- Different per environment (local vs Docker vs Fly.io)
- Contains secrets
- Easy to change without code modification
- Not committed to git

### ✅ Keep in config.py (Application Logic)

**Definitely in config.py:**
- `LEADERBOARDS` - Contest structure
- `RANKINGS` - Category descriptions
- `PHONE_POINTS`, `CW_DIGITAL_POINTS` - Scoring rules
- `N5LCC_BONUS`, `ROVER_PARISH_BONUS` - Bonus points
- `CATEGORY_ABBREVS` - Category codes
- `FINAL_REPORT_TXT` - Report intro text
- `CONTEST_YEARS` - Available years list

**Why?**
- Part of contest rules (same everywhere)
- Large data structures
- Application business logic
- Version controlled in git

## 📁 File Setup

### 1. Create .env file

```bash
# In your laqp/ directory
cp .env.example .env

# Edit .env
nano .env

# Generate and add secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy output and paste into .env
```

### 2. Your .env file

```bash
# .env (DO NOT COMMIT TO GIT!)
SECRET_KEY=3a7f8b2e9c1d4a6f5e8b7c2a1d3f9e4b8c7a2f1e6d9b3c5a8e2f7d1b4c6a9e3f
FLASK_ENV=production
CONTEST_YEAR=2026
DATABASE_PATH=/data/database/laqp.db
BATCH_INPUT_DIR=/data/batch_input
FINAL_REPORTS_DIR=/data/final_reports
REFERENCE_DATA_DIR=/data/reference_data
```

### 3. Your config.py reads from .env

```python
# config/config.py
import os

# Read from environment
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set!")

CONTEST_YEAR = os.environ.get('CONTEST_YEAR', '2026')
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'laqp/data/database/laqp.db')

# Contest logic stays here
RANKINGS = {
    'LFQ': 'Louisiana - Fixed QRP Power',
    # ... rest of rankings
}

LEADERBOARDS = [
    # ... your leaderboards config
]
```

## 🔒 Security Best Practices

### Add .env to .gitignore

```bash
# .gitignore
.env
*.db
__pycache__/
```

### Create .env.example (template)

```bash
# .env.example (COMMIT THIS!)
# Copy to .env and fill in real values

SECRET_KEY=change-this-to-a-random-secret-key
FLASK_ENV=production
CONTEST_YEAR=2026
DATABASE_PATH=/data/database/laqp.db
BATCH_INPUT_DIR=/data/batch_input
FINAL_REPORTS_DIR=/data/final_reports
REFERENCE_DATA_DIR=/data/reference_data
```

**Commit .env.example, NOT .env!**

## 🐳 Docker Usage

### Local Development

```yaml
# docker-compose.yml
environment:
  - SECRET_KEY=${SECRET_KEY}
  - CONTEST_YEAR=${CONTEST_YEAR}
  - DATABASE_PATH=/data/database/laqp.db
```

Docker reads from your `.env` file automatically!

### Fly.io Production

```bash
# Set secrets on Fly.io (not in .env)
flyctl secrets set SECRET_KEY="your-generated-key"
flyctl secrets set CONTEST_YEAR="2026"

# List secrets
flyctl secrets list
```

## 📊 Comparison Table

| Setting | .env | config.py | Why |
|---------|------|-----------|-----|
| SECRET_KEY | ✅ | ❌ | Secret! |
| DATABASE_PATH | ✅ | ❌ | Changes per environment |
| BATCH_INPUT_DIR | ✅ | ❌ | Path varies |
| FLASK_ENV | ✅ | ❌ | dev vs production |
| LEADERBOARDS | ❌ | ✅ | Business logic |
| RANKINGS | ❌ | ✅ | Contest rules |
| PHONE_POINTS | ❌ | ✅ | Scoring rule |
| N5LCC_BONUS | ❌ | ✅ | Contest constant |

## ✅ Setup Checklist

- [ ] Generate SECRET_KEY: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Create `.env` from `.env.example`
- [ ] Add SECRET_KEY to `.env`
- [ ] Add `.env` to `.gitignore`
- [ ] Keep `.env.example` in git (template only)
- [ ] Move secrets from `config.py` to `.env`
- [ ] Keep contest logic in `config.py`
- [ ] Test locally: `docker-compose up -d`
- [ ] For Fly.io: `flyctl secrets set SECRET_KEY="..."`

## 🚨 Never Commit These

```
❌ .env
❌ *.db
❌ Secrets in config.py
❌ Real API keys
❌ Production passwords
```

## ✅ Always Commit These

```
✅ .env.example
✅ config.py (with logic, not secrets)
✅ .gitignore
✅ README.md
```

The split is simple: **Secrets in .env, logic in config.py!**
