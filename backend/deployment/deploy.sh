#!/bin/bash

# Audio Classification Middleware Deployment Script
# For Linux/Unix systems

echo "🚀 Deploying Audio Classification Middleware..."

# Configuration
APP_NAME="audio-classifier"
APP_USER="appuser"
VENV_PATH="/opt/$APP_NAME/venv"
APP_PATH="/opt/$APP_NAME"
SERVICE_NAME="audio-classifier"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Create application user if it doesn't exist
if ! id "$APP_USER" &>/dev/null; then
    echo "👤 Creating application user: $APP_USER"
    useradd -r -s /bin/false -d $APP_PATH $APP_USER
fi

# Create application directory
echo "📁 Creating application directory..."
mkdir -p $APP_PATH
chown $APP_USER:$APP_USER $APP_PATH

# Copy application files
echo "📋 Copying application files..."
cp -r . $APP_PATH/
chown -R $APP_USER:$APP_USER $APP_PATH

# Install Python dependencies
echo "🐍 Setting up Python environment..."
cd $APP_PATH

# Create virtual environment
python3 -m venv $VENV_PATH
chown -R $APP_USER:$APP_USER $VENV_PATH

# Install dependencies
sudo -u $APP_USER $VENV_PATH/bin/pip install --upgrade pip
sudo -u $APP_USER $VENV_PATH/bin/pip install -r requirements.txt

# Create systemd service file
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Audio Classification Middleware
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_PATH
Environment=PATH=$VENV_PATH/bin
ExecStart=$VENV_PATH/bin/python main.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Create nginx configuration (optional)
if command -v nginx > /dev/null; then
    echo "🌐 Creating nginx configuration..."
    cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain

    # Increase client max body size for audio uploads
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

    # Enable nginx site
    ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    nginx -t && systemctl reload nginx
    echo "✅ Nginx configuration created"
fi

# Create log directory
mkdir -p /var/log/$APP_NAME
chown $APP_USER:$APP_USER /var/log/$APP_NAME

# Start the service
echo "🚀 Starting service..."
systemctl start $SERVICE_NAME

# Check service status
sleep 3
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service started successfully!"
    
    # Show service status
    systemctl status $SERVICE_NAME --no-pager
    
    echo ""
    echo "🎉 Deployment completed!"
    echo ""
    echo "📋 Service Information:"
    echo "  Service name: $SERVICE_NAME"
    echo "  Status: systemctl status $SERVICE_NAME"
    echo "  Logs: journalctl -u $SERVICE_NAME -f"
    echo "  Restart: systemctl restart $SERVICE_NAME"
    echo "  Stop: systemctl stop $SERVICE_NAME"
    echo ""
    echo "🌐 Access Information:"
    echo "  API: http://localhost:8000"
    echo "  Health: http://localhost:8000/health"
    echo "  Docs: http://localhost:8000/docs"
    echo ""
    echo "📁 Application Directory: $APP_PATH"
    echo "🐍 Virtual Environment: $VENV_PATH"
    
else
    echo "❌ Failed to start service!"
    echo "Check logs with: journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi
