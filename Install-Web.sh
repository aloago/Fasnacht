#!/bin/bash

# Update & upgrade system
sudo apt update && sudo apt upgrade -y

# Install X server, Openbox, and Chromium (instead of Falkon)
sudo apt install --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox chromium-browser git unclutter -y

# Clone the web application repository
git clone https://github.com/aloago/Fasnacht.git ~/Fasnacht

# Create Openbox config directory if it doesn't exist
mkdir -p ~/.config/openbox

# Create the autostart file for Chromium in kiosk mode
echo 'chromium-browser \
--kiosk \
--incognito \
--noerrdialogs \
--disable-infobars \
--disable-session-crashed-bubble \
--disable-features=TranslateUI \
--disable-pinch \
--block-new-web-contents \
file://'"$HOME"'/Fasnacht/Web_2.0/index.html' > ~/.config/openbox/autostart

# Add screen saver/power management disable commands
echo 'xset s off' >> ~/.config/openbox/autostart
echo 'xset -dpms' >> ~/.config/openbox/autostart
echo 'xset s noblank' >> ~/.config/openbox/autostart

# Add unclutter command
echo 'unclutter -idle 0 &' >> ~/.config/openbox/autostart

# Make the autostart script executable
chmod +x ~/.config/openbox/autostart

# Ensure startx runs on login
echo '[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && startx' >> ~/.bash_profile

# Reboot the system
sudo reboot