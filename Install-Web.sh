# Update & upgrade system
sudo apt update && sudo apt upgrade -y

# Install minimal X server & Falkon browser
sudo apt install --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox falkon git -y

# Clone the web application repository
git clone https://github.com/aloago/Fasnacht.git ~

# Create Openbox config directory if it doesn't exist
mkdir -p ~/.config/openbox

# Create the autostart file for Openbox (corrected syntax)
echo 'falkon --kiosk file://'"$HOME"'/Fasnacht/Web_2.0/index.html' > ~/.config/openbox/autostart

# Make sure the autostart script is executable
chmod +x ~/.config/openbox/autostart

# Ensure startx runs on login
echo '[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && startx' >> ~/.bash_profile

# Start the X session manually for this run (will autostart on reboot)
startx
