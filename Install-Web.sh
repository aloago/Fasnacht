#!/bin/bash

# Exit on error
set -e

# Update & upgrade system
echo "Updating and upgrading system..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing X server, Openbox, Chromium, and utilities..."
sudo apt install --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox chromium-browser git unclutter -y

# Clone the web application repository
if [ -d ~/Fasnacht ]; then
    echo "Fasnacht repository already exists. Skipping clone."
else
    echo "Cloning Fasnacht repository..."
    git clone https://github.com/aloago/Fasnacht.git ~/Fasnacht
fi

# Create Openbox config directory if it doesn't exist
mkdir -p ~/.config/openbox

# Backup existing autostart file
if [ -f ~/.config/openbox/autostart ]; then
    mv ~/.config/openbox/autostart ~/.config/openbox/autostart.bak
    echo "Existing autostart file backed up as autostart.bak"
fi

# Create the autostart file for Chromium in kiosk mode
echo "Configuring Openbox autostart..."
cat > ~/.config/openbox/autostart <<EOF
chromium-browser \\
--kiosk \\
--start-fullscreen \\
--incognito \\
--noerrdialogs \\
--disable-infobars \\
--disable-session-crashed-bubble \\
--disable-features=TranslateUI \\
--disable-pinch \\
--block-new-web-contents \\
file://$HOME/Fasnacht/Web_2.0/index.html > ~/chromium.log 2>&1

xset s off
xset -dpms
xset s noblank

unclutter -idle 0 &
EOF

# Make the autostart script executable
chmod +x ~/.config/openbox/autostart

# Install Python dependencies for the WebSocket server
echo "Installing Python dependencies..."
sudo apt install python3-pip -y
pip3 install --user websockets gpiozero

# Add ~/.local/bin to PATH if not already present
if ! grep -q "~/.local/bin" ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi

# Create the Python WebSocket server script
echo "Creating GPIO WebSocket server script..."
cat > ~/gpio_websocket.py <<EOF
import asyncio
import websockets
from gpiozero import Button

# GPIO setup
button = Button(2, pull_up=True)  # GPIO 2 with internal pull-up

async def gpio_state_server(websocket, path):
    while True:
        # Read GPIO state (True = high, False = low)
        state = button.is_pressed
        # Send state to the client
        await websocket.send(str(state))
        await asyncio.sleep(0.1)  # Throttle updates

# Start WebSocket server
start_server = websockets.serve(gpio_state_server, "0.0.0.0", 8765)

# Run the server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
EOF

# Make the Python script executable
chmod +x ~/gpio_websocket.py

# Create a systemd service to run the WebSocket server on boot
echo "Creating systemd service for GPIO WebSocket server..."
sudo bash -c 'cat > /etc/systemd/system/gpio-websocket.service <<EOF
[Unit]
Description=GPIO WebSocket Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/gpio_websocket.py
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF'

# Enable and start the systemd service
sudo systemctl enable gpio-websocket.service
sudo systemctl start gpio-websocket.service

# Ensure startx runs on login
echo "Configuring startx on login..."
echo '[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && startx' >> ~/.bash_profile

# Reboot the system
read -p "Reboot the system now? (y/n): " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo "Rebooting..."
    sudo reboot
else
    echo "Reboot canceled. Please reboot manually later."
fi