# LAQP Web Server - Port 5000 Setup Guide

## Quick Setup (3 Steps)

### Step 1: Update Your Flask App

Replace your `web/app.py` with the new version, or just change the last lines to:

```python
if __name__ == '__main__':
    # Run on port 5000 (no sudo needed!)
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### Step 2: Configure Router Port Forwarding

Login to your BGW320 router at: http://192.168.1.254

1. Go to **Firewall** → **NAT/Gaming** or **Port Forwarding**
2. Find your existing "LAQP-Web" service (or create new)
3. Update the settings:
   - **Service Name**: LAQP-Web
   - **Protocol**: TCP
   - **Public Port**: 80
   - **Private Port**: 5000 ← **CHANGED FROM 80**
   - **Private IP**: 192.168.1.100 (your computer's static IP)
   - **Enable**: Yes/Checked
4. **Save**

### Step 3: Configure Firewall

Allow port 5000 on your computer:

```bash
# If using ufw (Ubuntu/Debian)
sudo ufw allow 5000/tcp

# If using firewalld (RHEL/CentOS)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## Running the Server

### Start the server:

```bash
# Navigate to your project directory
cd /path/to/your/laqp

# Run the Flask app (NO SUDO NEEDED!)
python3 web/app.py
```

You should see:
```
============================================================
Louisiana QSO Party - Log Upload Server
============================================================
Starting Flask application on port 5000
Incoming logs directory: /path/to/laqp/logs/incoming

Server will be accessible at:
  - Locally: http://localhost:5000
  - On network: http://YOUR_LOCAL_IP:5000
  - From internet: http://YOUR_PUBLIC_IP (via router port forwarding)

Make sure your router forwards:
  Public Port 80 → Private Port 5000 → This computer
============================================================

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

## Testing Your Setup

### 1. Test Locally (on the server computer):

```bash
curl http://localhost:5000
```

Should return the HTML of your upload page.

### 2. Test on Your Network (from another computer on same WiFi):

```bash
curl http://192.168.1.100:5000
```

Or open in browser: http://192.168.1.100:5000

### 3. Test from Internet:

**Use your phone (turn OFF WiFi, use cellular data):**

1. Find your public IP: https://whatismyipaddress.com/
2. Visit: http://YOUR_PUBLIC_IP

You should see the Louisiana QSO Party log upload page!

**Note**: Some ISPs block port 80. If it doesn't work, try:
- Change router public port to 8080
- Access via: http://YOUR_PUBLIC_IP:8080

## How It Works

```
Internet User
    ↓
http://YOUR_PUBLIC_IP:80  ← User enters this
    ↓
[ATT BGW320 Router]  ← Port forwarding: 80 → 5000
    ↓
http://192.168.1.100:5000  ← Flask listening here
    ↓
[Your Computer - Flask App]
```

**Benefits of this setup:**
- ✅ No sudo required
- ✅ Safer (not running as root)
- ✅ Easy to stop/start
- ✅ Standard practice
- ✅ Works with any router

## Keeping It Running

### Option 1: Run in Screen (Simple)

```bash
# Install screen if needed
sudo apt install screen

# Start a screen session
screen -S laqp-web

# Run your app
python3 web/app.py

# Detach: Press Ctrl+A, then D
# Reattach later: screen -r laqp-web
```

### Option 2: Systemd Service (Better)

Create `/etc/systemd/system/laqp-web.service`:

```ini
[Unit]
Description=LAQP Log Upload Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/your/laqp
ExecStart=/usr/bin/python3 /path/to/your/laqp/web/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable laqp-web
sudo systemctl start laqp-web
sudo systemctl status laqp-web
```

Now it starts automatically on boot!

## Troubleshooting

### "Address already in use" error:

Port 5000 is already used by something else.

```bash
# Find what's using port 5000
sudo lsof -i :5000
# or
sudo netstat -tlnp | grep :5000

# Kill it if needed
sudo kill <PID>

# Or use a different port (e.g., 5001)
# Update app.py and router forwarding accordingly
```

### Can't access from internet:

1. **Check router port forwarding**:
   - Login to 192.168.1.254
   - Verify: Public 80 → Private 5000 → 192.168.1.100
   - Make sure it's enabled

2. **Check firewall**:
   ```bash
   sudo ufw status
   # Should show: 5000/tcp ALLOW Anywhere
   ```

3. **Check Flask is listening**:
   ```bash
   sudo netstat -tlnp | grep :5000
   # Should show python3 listening on 0.0.0.0:5000
   ```

4. **Check public IP hasn't changed**:
   - Visit https://whatismyipaddress.com/
   - Verify it matches what you're using

5. **Try port 8080 instead of 80**:
   - Some ISPs block port 80
   - Change router: Public 8080 → Private 5000
   - Access: http://YOUR_PUBLIC_IP:8080

### Flask won't start:

```bash
# Check for Python errors
python3 web/app.py

# Check logs
tail -f /var/log/syslog | grep python

# Make sure config files exist
ls -la config/
ls -la reference_data/
```

## Viewing Logs

While the app is running:

```bash
# Watch incoming logs
watch -n 2 'ls -lh logs/incoming/'

# Or use tail to watch for changes
tail -f logs/incoming/*
```

## Stopping the Server

If running in terminal:
- Press **Ctrl+C**

If running as systemd service:
```bash
sudo systemctl stop laqp-web
```

## Quick Reference

| What | Value |
|------|-------|
| Flask Port | 5000 |
| Router Public Port | 80 (or 8080) |
| Router Private Port | 5000 |
| Your Static IP | 192.168.1.100 |
| Router IP | 192.168.1.254 |
| Incoming Logs | logs/incoming/ |

**Start Command:**
```bash
python3 web/app.py
```

**Access URLs:**
- Local: http://localhost:5000
- Network: http://192.168.1.100:5000
- Internet: http://YOUR_PUBLIC_IP

That's it! You're all set up with the port 5000 solution. 73!
