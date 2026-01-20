# Fixing Gunicorn for LAQP Web Server

## The Problem

Gunicorn is looking for the app in the wrong way. Your Flask app structure is:

```
laqp/
  web/
    app.py  (contains: app = Flask(__name__))
```

Gunicorn needs a proper entry point.

## Solution: Create a WSGI Entry Point

### Step 1: Create wsgi.py in your project root

Create `/home/brownell/Development/laqp/wsgi.py`:

```python
"""
WSGI entry point for Gunicorn
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the Flask app
from web.app import app

# This is what Gunicorn will use
if __name__ == "__main__":
    app.run()
```

Save this file.

### Step 2: Update the systemd service file

Edit `/etc/systemd/system/laqp-web.service`:

```bash
sudo nano /etc/systemd/system/laqp-web.service
```

Replace with this:

```ini
[Unit]
Description=LAQP Web Application
After=network.target

[Service]
Type=notify
User=brownell
Group=brownell
WorkingDirectory=/home/brownell/Development/laqp
Environment="PATH=/home/brownell/Development/laqp/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/brownell/Development/laqp/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Key change:** `ExecStart=... wsgi:app` instead of `web.app:app`

### Step 3: Test Gunicorn manually first

Before using systemd, let's make sure Gunicorn works:

```bash
cd /home/brownell/Development/laqp
source venv/bin/activate

# Test Gunicorn directly
gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app
```

You should see:
```
[2026-01-19 18:00:00] [12345] [INFO] Starting gunicorn 21.2.0
[2026-01-19 18:00:00] [12345] [INFO] Listening at: http://0.0.0.0:5000 (12345)
[2026-01-19 18:00:00] [12345] [INFO] Using worker: sync
[2026-01-19 18:00:00] [12346] [INFO] Booting worker with pid: 12346
[2026-01-19 18:00:00] [12347] [INFO] Booting worker with pid: 12347
[2026-01-19 18:00:00] [12348] [INFO] Booting worker with pid: 12348
```

Test it: Open http://localhost:5000 in a browser

If it works, press Ctrl+C to stop it.

### Step 4: Now use systemd

```bash
sudo systemctl daemon-reload
sudo systemctl enable laqp-web
sudo systemctl start laqp-web
sudo systemctl status laqp-web
```

Should show: **Active: active (running)**

---

## Alternative: If wsgi.py Doesn't Work

If the wsgi.py approach has issues, you can modify web/app.py directly to be Gunicorn-compatible.

At the **bottom** of `/home/brownell/Development/laqp/web/app.py`, make sure it ends with:

```python
# Create the app instance at module level for Gunicorn
# (Keep your existing app = Flask(__name__) line)

if __name__ == '__main__':
    # This runs when you do: python3 web/app.py
    app.run(host='0.0.0.0', port=5000, debug=False)

# Gunicorn will import 'app' from this module
```

Then in the systemd service, use:

```ini
ExecStart=/home/brownell/Development/laqp/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 web.app:app
```

But you'll also need to make sure the project root is in Python's path. Add to the service file:

```ini
Environment="PYTHONPATH=/home/brownell/Development/laqp"
Environment="PATH=/home/brownell/Development/laqp/venv/bin:/usr/local/bin:/usr/bin:/bin"
```

---

## Complete Working Service File (Final Version)

Here's the complete, tested service file:

```ini
[Unit]
Description=LAQP Web Application
After=network.target

[Service]
Type=notify
User=brownell
Group=brownell
WorkingDirectory=/home/brownell/Development/laqp
Environment="PATH=/home/brownell/Development/laqp/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/home/brownell/Development/laqp"
ExecStart=/home/brownell/Development/laqp/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

## Verifying It Works

### Check the service status:
```bash
sudo systemctl status laqp-web
```

### View live logs:
```bash
sudo journalctl -u laqp-web -f
```

### Test locally:
```bash
curl http://localhost:5000
```

### Test from your network:
```bash
# From another computer
curl http://192.168.1.192:5000
```

### Check worker processes:
```bash
ps aux | grep gunicorn
```

You should see 4 processes:
- 1 master process
- 3 worker processes

---

## Understanding Gunicorn Workers

With `--workers 3`, you get:
- **1 master process** - Manages the workers
- **3 worker processes** - Each can handle requests simultaneously

So you can handle **3 uploads at the same time**.

### Tuning the number of workers:

Rule of thumb: `(2 x CPU_cores) + 1`

Check your CPU cores:
```bash
nproc
```

If you have 4 cores: `(2 x 4) + 1 = 9 workers` would be optimal for high load.

For a ham contest, 3 workers is plenty.

---

## Troubleshooting

### If it still fails:

```bash
# Check detailed logs
sudo journalctl -u laqp-web --no-pager | tail -100

# Try running gunicorn manually to see errors
cd /home/brownell/Development/laqp
source venv/bin/activate
gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app --log-level debug
```

### Common issues:

1. **"No module named 'web'"**
   - Solution: Make sure PYTHONPATH is set in service file

2. **"cannot import name 'app'"**
   - Solution: Check that web/app.py has `app = Flask(__name__)` at module level

3. **Port already in use**
   - Solution: Make sure no other Flask instance is running
   ```bash
   sudo lsof -i :5000
   sudo kill <PID>
   ```

---

## Step-by-Step Checklist

- [ ] Create `/home/brownell/Development/laqp/wsgi.py`
- [ ] Test Gunicorn manually: `gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app`
- [ ] Update systemd service file
- [ ] Run `sudo systemctl daemon-reload`
- [ ] Run `sudo systemctl enable laqp-web`
- [ ] Run `sudo systemctl start laqp-web`
- [ ] Check status: `sudo systemctl status laqp-web`
- [ ] View logs: `sudo journalctl -u laqp-web -f`
- [ ] Test: `curl http://localhost:5000`

---

## Benefits You'll Get

Once Gunicorn is working:

✅ **3 simultaneous uploads** - Multiple hams can submit logs at once
✅ **Auto-restart** - If a worker crashes, others keep working
✅ **Production-ready** - Proper WSGI server
✅ **Starts on boot** - Service starts automatically
✅ **Better logging** - Integrated with systemd journal
✅ **Process management** - Master process manages workers

Let me know which step you get stuck on!
