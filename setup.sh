#!/bin/bash

# Update package lists
sudo apt-get update
sudo apt-get upgrade -y

# Install basic dependencies
sudo apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    git \
    xorg \
    openbox \
    lightdm \
    alsa-utils \
    pulseaudio \
    network-manager \
    plymouth \
    plymouth-themes \
    sqlite3 \
    python3-sqlite3

# Install GUI dependencies
sudo apt-get install -y \
    qt5-default \
    qtcreator \
    qt5-qmake \
    python3-pyqt5 \
    python3-pyqt5.qtmultimedia

# Install Python packages
pip3 install \
    requests \
    pillow \
    pygame \
    pokebase \
    numpy \
    scipy

# Create directory structure
mkdir -p /etc/pokedexos/themes
mkdir -p /etc/pokedexos/sounds
mkdir -p /etc/pokedexos/database
mkdir -p /etc/pokedexos/database/sprites

# Set proper permissions
sudo chown -R pokedex:pokedex /etc/pokedexos
sudo chmod -R 755 /etc/pokedexos

# Clone the PokedexOS repository
git clone https://github.com/IchoTM/PokeOS.git

# Set up Plymouth theme
sudo cp -r PokeOS/plymouth-theme/pokedex /usr/share/plymouth/themes/
sudo plymouth-set-default-theme pokedex -R

# Set up auto-login
echo "[Seat:*]
autologin-user=pokedex
autologin-user-timeout=0" | sudo tee /etc/lightdm/lightdm.conf.d/autologin.conf

# Create systemd service for PokedexOS
echo "[Unit]
Description=PokedexOS Interface
After=graphical.target

[Service]
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pokedex/.Xauthority
ExecStart=/usr/bin/python3 /opt/pokedexos/main.py
Restart=always
User=pokedex

[Install]
WantedBy=graphical.target" | sudo tee /etc/systemd/system/pokedexos.service

# Copy application files to the correct location
sudo mkdir -p /opt/pokedexos
sudo cp main.py database_manager.py create_boot_sound.py /opt/pokedexos/
sudo chown -R pokedex:pokedex /opt/pokedexos
sudo chmod -R 755 /opt/pokedexos

# Generate boot sound
python3 create_boot_sound.py

# Enable the service
sudo systemctl enable pokedexos.service 