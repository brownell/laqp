# Louisiana QSO Party - Local Docker Testing

## Quick Start

### 1. Test Locally First

```bash
# Ensure you have data files
mkdir -p data
# Add LA_Parish_Abbrevs.txt and WVE_Abbrevs.txt

# Create config directory
mkdir -p config
# Add config.py with your settings

# Build and run
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Visit
http://localhost:5000
```

### 2. Verify Everything Works

```bash
# Check health
curl http://localhost:5000/health

# Check database
docker-compose exec laqp-web ls -la /data/database/

# Upload a test log
# Visit http://localhost:5000/upload

# Check it was saved
docker-compose exec laqp-web ls -la /data/logs/incoming/
```

### 3. Stop and Clean Up

```bash
# Stop containers
docker-compose down

# Remove volumes (⚠️ DELETES DATA!)
docker-compose down -v
```

## Accessing Volumes Locally

### View Volume Contents

```bash
# List all volumes
docker volume ls | grep laqp

# Inspect a volume
docker volume inspect laqp-database

# See where it's stored
docker volume inspect laqp-database | grep Mountpoint
```

### Access Files in Volume

```bash
# Method 1: Using docker exec (easiest)
docker-compose exec laqp-web bash
cd /data/database
ls -la
cat laqp.db  # (binary file)
exit

# Method 2: Copy files out
docker cp laqp-web:/data/database/laqp.db ./laqp-local.db

# Method 3: Copy files in
docker cp ./my-config.py laqp-web:/app/config/config.py
docker-compose restart
```

### Edit Config Files

```bash
# Option 1: Mount local config (already in docker-compose.yml)
# Edit ./config/config.py on your machine
# Changes auto-reflected (no rebuild needed)

# Option 2: Edit inside container
docker-compose exec laqp-web bash
nano /app/config/config.py
exit
docker-compose restart

# Option 3: Copy in new config
docker cp ./config/config.py laqp-web:/app/config/config.py
docker-compose restart
```

## Common Tasks

### View Database

```bash
# Copy database out
docker cp laqp-web:/data/database/laqp.db ./local.db

# View with sqlite3
sqlite3 local.db
> SELECT COUNT(*) FROM contest_results;
> .quit
```

### Run Scripts in Container

```bash
# Run batch processing
docker-compose exec laqp-web python batch.py

# Generate rankings
docker-compose exec laqp-web python generate_rankings.py 2026

# Generate final report
docker-compose exec laqp-web python generate_final_report.py 2026
```

### View Logs

```bash
# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Search logs
docker-compose logs | grep ERROR
```

### Backup Data

```bash
# Backup database
docker cp laqp-web:/data/database/laqp.db ./backup-$(date +%Y%m%d).db

# Backup everything
docker run --rm \
  -v laqp-database:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/laqp-backup-$(date +%Y%m%d).tar.gz -C /data .
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Check if port is in use
lsof -i :5000

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Permission errors

```bash
# Fix ownership
docker-compose exec --user root laqp-web chown -R laqp:laqp /data
docker-compose restart
```

### Config changes not applying

```bash
# Restart container
docker-compose restart

# Or rebuild if code changed
docker-compose up -d --build
```

## Testing Checklist

- [ ] Container starts successfully
- [ ] Health check passes: http://localhost:5000/health
- [ ] Upload page loads: http://localhost:5000/upload
- [ ] Can upload a test log
- [ ] Database file created: /data/database/laqp.db
- [ ] Log file saved: /data/logs/incoming/
- [ ] Results page loads: http://localhost:5000/results
- [ ] Can run batch.py in container
- [ ] Can generate rankings
- [ ] Can generate final report
- [ ] Volumes persist after restart

Once everything works locally, you're ready for Fly.io!
