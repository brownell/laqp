# Deployment Guide: Running LAQP Web App from Home
## ATT Fiber with BGW320 Router

This guide will help you make your Louisiana QSO Party log upload application accessible from the internet.

---

## Overview

You'll need to:
1. Set up a static IP for your web server computer
2. Configure port forwarding on your BGW320 router
3. Configure your computer's firewall
4. Run your Flask app in production mode
5. (Optional) Set up a domain name

---

## Part 1: Find Your Current Network Information

### On Your Web Server Computer (Linux):

```bash
# Find your local IP address
ip addr show | grep "inet " | grep -v 127.0.0.1

# Or simpler:
hostname -I

# Find your router's IP (gateway)
ip route | grep default

# Should show something like: 192.168.1.254
```

### On Your Web Server Computer (Windows):

```cmd
ipconfig

# Look for:
# - IPv4 Address (e.g., 192.168.1.100)
# - Default Gateway (e.g., 192.168.1.254)
```

**Write down:**
- Your computer's current IP: ________________
- Router/Gateway IP: ________________ (usually 192.168.1.254)

### Find Your Public IP:

Visit: https://whatismyipaddress.com/
- Your public IP: ________________

---

## Part 2: Configure Static IP on Your Computer

### Option A: Ubuntu/Debian Linux (Recommended if using headless server)

#### Using NetworkManager (Desktop):

1. Open Network Settings
2. Click the gear icon next to your connection
3. Go to IPv4 tab
4. Change from "Automatic (DHCP)" to "Manual"
5. Add address:
   - **Address**: 192.168.1.100 (choose any number 2-253)
   - **Netmask**: 255.255.255.0
   - **Gateway**: 192.168.1.254 (your router IP)
   - **DNS**: 8.8.8.8, 8.8.4.4 (Google DNS)
6. Apply and reconnect

#### Using netplan (Server):

Edit `/etc/netplan/01-netcfg.yaml`:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:  # Change to your interface name (use 'ip link' to find)
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.254
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Apply:
```bash
sudo netplan apply
```

### Option B: Windows

1. Open Control Panel → Network and Internet → Network Connections
2. Right-click your network adapter → Properties
3. Select "Internet Protocol Version 4 (TCP/IPv4)" → Properties
4. Select "Use the following IP address"
5. Enter:
   - **IP address**: 192.168.1.100
   - **Subnet mask**: 255.255.255.0
   - **Default gateway**: 192.168.1.254
   - **Preferred DNS**: 8.8.8.8
   - **Alternate DNS**: 8.8.4.4
6. Click OK

---

## Part 3: Configure ATT BGW320 Router

### Access Router Admin Interface:

1. Open browser to: http://192.168.1.254
2. Login credentials:
   - Default password is on a sticker on the router
   - Or use ATT login if you've changed it

### Set Up IP Passthrough (Recommended) OR Port Forwarding:

#### Option A: IP Passthrough (Simpler, gives your computer direct public IP)

**WARNING**: This exposes your computer directly to internet. Only use if:
- Computer has good firewall configured
- You understand security implications
- You want the simplest setup

1. Go to **Settings** → **LAN** → **IP Passthrough**
2. **Allocation Mode**: Passthrough
3. **Passthrough Mode**: DHCPS-fixed
4. **Passthrough Fixed MAC Address**: Select your computer's MAC address
5. Save

**Skip to Part 4 if using IP Passthrough**

#### Option B: Port Forwarding (More Secure, Recommended)

1. Navigate to **Firewall** → **NAT/Gaming** or **IP Passthrough**
2. Look for "Port Forwarding" or "Applications, Pinholes and DMZ"
3. Click **Add Service** or **Custom Services**
4. Create new service:
   - **Service Name**: LAQP-Web
   - **Protocol**: TCP
   - **Public Port**: 80 (or 8080 if AT&T blocks port 80)
   - **Private Port**: 5000 (Flask default) or 80
   - **Server IPv4 Address**: 192.168.1.100 (your static IP)
   - **Enable**: Yes/Checked
5. Save

### Additional Port Forwarding for HTTPS (Recommended for production):

Add another service:
- **Service Name**: LAQP-Web-SSL
- **Protocol**: TCP
- **Public Port**: 443
- **Private Port**: 443
- **Server IPv4 Address**: 192.168.1.100
- **Enable**: Yes/Checked

---

## Part 4: Configure Firewall on Your Computer

### Ubuntu/Linux (ufw):

```bash
# Enable firewall if not already
sudo ufw enable

# Allow SSH first (so you don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Allow Flask development port (if testing)
sudo ufw allow 5000/tcp

# Check status
sudo ufw status verbose
```

### Ubuntu/Linux (firewalld):

```bash
# Allow HTTP
sudo firewall-cmd --permanent --add-service=http

# Allow HTTPS
sudo firewall-cmd --permanent --add-service=https

# Allow custom port if needed
sudo firewall-cmd --permanent --add-port=5000/tcp

# Reload
sudo firewall-cmd --reload

# Check
sudo firewall-cmd --list-all
```

### Windows Firewall:

1. Open Windows Defender Firewall → Advanced Settings
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → Next
4. TCP, Specific local ports: 80,443,5000 → Next
5. Allow the connection → Next
6. Check all profiles (Domain, Private, Public) → Next
7. Name: "LAQP Web Server" → Finish

---

## Part 5: Configure Flask App for Production

### Update your app.py

Make sure your Flask app ends with:

```python
if __name__ == '__main__':
    # Development mode (testing only)
    # app.run(host='0.0.0.0', port=5000, debug=True)
    
    # Production mode
    app.run(host='0.0.0.0', port=80, debug=False)
```

**Important Notes:**
- `host='0.0.0.0'` makes Flask listen on ALL network interfaces
- `port=80` is standard HTTP (requires sudo/admin on Linux)
- `debug=False` for production (never use debug=True on public server!)

### Running Flask on Port 80 (Linux requires sudo):

```bash
# Option 1: Run with sudo (simple but not recommended)
sudo python3 web/app.py

# Option 2: Give Python permission to bind to port 80 (better)
sudo setcap 'cap_net_bind_service=+ep' $(which python3)
python3 web/app.py

# Option 3: Use a reverse proxy (best - see below)
```

---

## Part 6: Production Deployment (Recommended)

For a real production server, use **Gunicorn** with **Nginx**:

### Install Required Software:

```bash
# Install Gunicorn and Nginx
sudo apt update
sudo apt install nginx python3-pip
pip3 install gunicorn
```

### Create Gunicorn Service:

Create `/etc/systemd/system/laqp-web.service`:

```ini
[Unit]
Description=LAQP Web Application
After=network.target

[Service]
User=YOUR_USERNAME
Group=www-data
WorkingDirectory=/path/to/your/laqp/project
Environment="PATH=/home/YOUR_USERNAME/.local/bin:/usr/bin"
ExecStart=/home/YOUR_USERNAME/.local/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 web.app:app

[Install]
WantedBy=multi-user.target
```

Replace:
- `YOUR_USERNAME` with your actual username
- `/path/to/your/laqp/project` with actual path

Enable and start:
```bash
sudo systemctl enable laqp-web
sudo systemctl start laqp-web
sudo systemctl status laqp-web
```

### Configure Nginx:

Create `/etc/nginx/sites-available/laqp`:

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;  # Or your domain name

    client_max_body_size 10M;  # Allow 10MB uploads

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/laqp/project/web/static;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/laqp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Part 7: Testing Your Setup

### Test Locally First:

```bash
# From your server computer
curl http://localhost
curl http://192.168.1.100

# From another computer on your network
curl http://192.168.1.100
```

### Test from Internet:

1. From your phone (disable WiFi to use cellular):
   - Visit: http://YOUR_PUBLIC_IP
   
2. From another location:
   - Visit: http://YOUR_PUBLIC_IP

### If Port 80 is Blocked by AT&T:

Some ISPs block port 80. Test with port 8080:
- Router: Forward public port 8080 → private port 80
- Access via: http://YOUR_PUBLIC_IP:8080

---

## Part 8: Get a Domain Name (Optional but Recommended)

### Free Options:
- **DuckDNS**: Free subdomain (yourname.duckdns.org)
- **No-IP**: Free dynamic DNS
- **Cloudflare**: Free (but need to buy domain first)

### Paid Options (Recommended):
- **Namecheap**: ~$10/year for .com
- **Google Domains**: ~$12/year
- **Cloudflare Registrar**: At-cost pricing

### Set Up Dynamic DNS (if you don't have static public IP):

AT&T Fiber usually provides a stable IP, but it can change. Use dynamic DNS:

1. Sign up at DuckDNS.org
2. Create subdomain: laqp.duckdns.org
3. Install DuckDNS updater:

```bash
# Create directory
mkdir -p ~/duckdns
cd ~/duckdns

# Create update script
echo "echo url=\"https://www.duckdns.org/update?domains=YOUR_DOMAIN&token=YOUR_TOKEN&ip=\" | curl -k -o ~/duckdns/duck.log -K -" > duck.sh

chmod 700 duck.sh

# Add to crontab (updates every 5 minutes)
crontab -e
# Add line:
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

---

## Part 9: Security Checklist

### Essential Security Steps:

- [ ] Change default router password
- [ ] Enable router firewall
- [ ] Use static IP for web server
- [ ] Configure computer firewall (ufw/firewalld)
- [ ] Run Flask with `debug=False`
- [ ] Set strong `FLASK_SECRET_KEY` in config
- [ ] Limit upload file sizes (already done: 5MB)
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`
- [ ] Consider fail2ban to block brute force attempts
- [ ] Monitor logs regularly

### Install Fail2ban (Recommended):

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Part 10: Monitoring and Maintenance

### Check Application Logs:

```bash
# If using systemd service:
sudo journalctl -u laqp-web -f

# If running manually:
tail -f /path/to/your/app/logs/error.log
```

### Monitor Nginx:

```bash
# Access log
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services:

```bash
# Restart Flask app
sudo systemctl restart laqp-web

# Restart Nginx
sudo systemctl restart nginx

# Restart both
sudo systemctl restart laqp-web nginx
```

---

## Troubleshooting

### Can't access from internet:

1. **Check router port forwarding**:
   - Login to router, verify settings
   - Make sure service is enabled
   
2. **Check computer firewall**:
   ```bash
   sudo ufw status verbose
   ```

3. **Check if Flask is listening**:
   ```bash
   sudo netstat -tlnp | grep :80
   # or
   sudo ss -tlnp | grep :80
   ```

4. **Check AT&T blocks**:
   - Some ISPs block port 80
   - Try port 8080 instead

5. **Check public IP**:
   - Visit https://whatismyipaddress.com/
   - Make sure it matches what you're using

### Logs show errors:

```bash
# Check Flask logs
sudo journalctl -u laqp-web --no-pager | tail -50

# Check Nginx logs
sudo tail -50 /var/log/nginx/error.log

# Check system logs
sudo tail -50 /var/log/syslog
```

### Permission errors:

```bash
# Make sure www-data can read files
sudo chown -R $USER:www-data /path/to/laqp
sudo chmod -R 755 /path/to/laqp

# Make sure incoming logs directory is writable
sudo chmod 775 /path/to/laqp/logs/incoming
```

---

## Quick Reference Card

**Your Configuration:**
- Static IP: _________________
- Router IP: 192.168.1.254
- Public IP: _________________
- Domain: _________________
- Service Port: 80 (or 8080)
- Flask Port: 5000

**Router Login:**
- URL: http://192.168.1.254
- Password: (on router sticker)

**Important Commands:**
```bash
# Start app
sudo systemctl start laqp-web

# Stop app
sudo systemctl stop laqp-web

# Restart app
sudo systemctl restart laqp-web

# View logs
sudo journalctl -u laqp-web -f

# Check firewall
sudo ufw status
```

---

## Need Help?

Common issues:
1. Can't access from outside → Check port forwarding and firewall
2. Page loads but uploads fail → Check file permissions on logs/incoming/
3. Service won't start → Check logs with `journalctl`
4. 502 Bad Gateway → Gunicorn/Flask not running

Good luck with the Louisiana QSO Party! 73!
