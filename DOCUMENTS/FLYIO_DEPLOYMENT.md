# Louisiana QSO Party - Fly.io Deployment Guide

## Why Fly.io?

- ✅ **FREE tier** - Stays free for your use case
- ✅ **Docker-native** - Uses your Dockerfile
- ✅ **Persistent volumes** - SQLite works perfectly
- ✅ **Auto SSL** - HTTPS automatic
- ✅ **Global CDN** - Fast everywhere
- ✅ **Easy scaling** - Grows with you

## Prerequisites

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

# Verify installation
flyctl version
```

## Initial Setup

### 1. Create Fly.io Account

```bash
# Sign up (opens browser)
flyctl auth signup

# Or login if you have account
flyctl auth login
```

### 2. Create Volume (Persistent Storage)

```bash
# Create 1GB volume for database, logs, results
flyctl volumes create laqp_data --region iad --size 1

# Verify
flyctl volumes list
```

**Regions:**
- `iad` - Washington DC (East Coast)
- `dfw` - Dallas (Central)
- `lax` - Los Angeles (West Coast)

Choose closest to you!

### 3. Set Secrets

```bash
# Generate a secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set in Fly.io
flyctl secrets set SECRET_KEY="your-generated-key-here"
flyctl secrets set CONTEST_YEAR="2026"
```

## Deploy Application

### 1. First Deployment

```bash
# From your project directory
flyctl launch

# Follow prompts:
# - App name: laqp-contest
# - Region: iad (or closest)
# - Database: NO (we use SQLite)
# - Deploy now: YES
```

### 2. Deploy Updates

```bash
# After code changes
flyctl deploy
```

## Accessing Volume (Config, Database)

### SSH into Container

```bash
# Open shell
flyctl ssh console

# Navigate to volume
cd /data
ls -la

# Exit
exit
```

### Edit Config Files

```bash
# SSH in
flyctl ssh console

# View/edit config
nano /app/config/config.py

# Exit and restart
exit
flyctl apps restart laqp-contest
```

### Access Database

```bash
# Copy database locally
flyctl ssh sftp get /data/database/laqp.db ./local-db.db

# View with sqlite3
sqlite3 local-db.db
```

### Run Scripts

```bash
# SSH in
flyctl ssh console

# Run batch processing
python batch.py

# Generate rankings
python generate_rankings.py 2026

exit
```

## Quick Reference

```bash
flyctl deploy              # Deploy
flyctl logs                # View logs
flyctl ssh console         # SSH
flyctl status              # Check status
flyctl open                # Open in browser
flyctl apps restart        # Restart
```

Your app: `https://laqp-contest.fly.dev`
