#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
BOT_NAME="servstatbot"
BOT_DIR="$(pwd)"
VENV_DIR="$BOT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/$BOT_NAME.service"
USER_NAME=$(whoami)

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv $VENV_DIR

# Activate virtual environment
source $VENV_DIR/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r $BOT_DIR/requirements.txt

# Create systemd service file
echo "Creating systemd service file..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=$BOT_NAME Discord Bot Service
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$BOT_DIR
ExecStart=$VENV_DIR/bin/python $BOT_DIR/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd manager configuration
echo "Reloading systemd manager configuration..."
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling $BOT_NAME service..."
sudo systemctl enable $BOT_NAME.service

# Start the service
echo "Starting $BOT_NAME service..."
sudo systemctl start $BOT_NAME.service

# Check the status of the service
echo "Checking the status of $BOT_NAME service..."
sudo systemctl status $BOT_NAME.service

echo "$BOT_NAME setup complete!"
