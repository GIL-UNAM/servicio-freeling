#!/bin/bash
# Production deployment script for servicio-freeling v2 (Flask + gunicorn + Apache)
#
# Run as root: sudo bash deploy_production.sh
#
# What this does:
#   1. Installs system packages (python3-venv, apache2 proxy modules)
#   2. Creates a Python virtualenv and installs pip dependencies + spaCy models
#   3. Sets correct ownership for www-data
#   4. Installs and enables the gunicorn systemd service
#   5. Configures Apache as a reverse proxy to gunicorn
#   6. Restarts everything

set -e

APP_DIR="/var/www/html/servicio-freeling"
SERVICE_NAME="servicio-freeling"

# --- Preflight checks ---

if [ "$EUID" -ne 0 ]; then
    echo "Error: run this script as root (sudo bash deploy_production.sh)"
    exit 1
fi

if [ ! -f "$APP_DIR/app.py" ]; then
    echo "Error: $APP_DIR/app.py not found."
    echo "Make sure the repo is deployed to $APP_DIR before running this script."
    exit 1
fi

echo "=== Deploying servicio-freeling v2 ==="

# --- 1. System packages ---

echo ""
echo "--- Installing system packages ---"
apt-get update -qq
apt-get install -y -qq python3-venv python3-dev

# Enable Apache proxy modules (idempotent)
a2enmod proxy proxy_http > /dev/null 2>&1

# --- 2. Python virtualenv + dependencies ---

echo ""
echo "--- Setting up Python virtualenv ---"
cd "$APP_DIR"

if [ ! -d venv ]; then
    python3 -m venv venv
fi

venv/bin/pip install --upgrade pip -q
venv/bin/pip install -r requirements.txt -q

echo ""
echo "--- Downloading spaCy models ---"
venv/bin/python -m spacy download en_core_web_sm
venv/bin/python -m spacy download fr_core_news_sm
venv/bin/python -m spacy download de_core_news_sm
venv/bin/python -m spacy download it_core_news_sm
venv/bin/python -m spacy download pt_core_news_sm

# --- 3. File ownership ---

echo ""
echo "--- Setting file ownership ---"
chown -R www-data:www-data "$APP_DIR"

# --- 4. Systemd service ---

echo ""
echo "--- Installing systemd service ---"
cp "$APP_DIR/$SERVICE_NAME.service" "/etc/systemd/system/$SERVICE_NAME.service"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "Waiting for gunicorn to start..."
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "gunicorn is running."
else
    echo "WARNING: gunicorn failed to start. Check: journalctl -u $SERVICE_NAME"
fi

# --- 5. Apache configuration ---

echo ""
echo "--- Configuring Apache ---"

# Disable the default site if it's the only one serving this content
# and install our reverse proxy config
cp "$APP_DIR/$SERVICE_NAME.conf" "/etc/apache2/sites-available/$SERVICE_NAME.conf"

# Disable default site, enable ours
a2dissite 000-default.conf > /dev/null 2>&1 || true
a2ensite "$SERVICE_NAME.conf" > /dev/null 2>&1

# Test config before restarting
if apache2ctl configtest 2>&1 | grep -q "Syntax OK"; then
    systemctl restart apache2
    echo "Apache restarted with new configuration."
else
    echo "ERROR: Apache config test failed:"
    apache2ctl configtest
    exit 1
fi

# --- Done ---

echo ""
echo "=== Deployment complete ==="
echo ""
echo "Service status:"
echo "  gunicorn: systemctl status $SERVICE_NAME"
echo "  apache:   systemctl status apache2"
echo ""
echo "Logs:"
echo "  gunicorn: journalctl -u $SERVICE_NAME -f"
echo "  apache:   tail -f /var/log/apache2/error.log"
echo ""
echo "Remember: the FreeLing daemon must also be running (./start.sh)"
