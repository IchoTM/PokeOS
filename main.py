#!/usr/bin/env python3

import sys
import os
import json
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame,
                            QMessageBox, QMenu)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt5.QtMultimedia import QSound
from database_manager import PokemonDatabaseManager

class PokedexOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PokédexOS")
        self.setStyleSheet("background-color: #FF0000;")  # Classic Pokédex red
        self.setWindowState(Qt.WindowFullScreen)
        
        # Initialize database manager
        self.db_manager = PokemonDatabaseManager()
        
        # Initialize the interface
        self.init_ui()
        
        # Power state
        self.power_on = False
        
        # Current Pokemon ID for navigation
        self.current_pokemon_id = 0
        
        # Boot sound
        self.boot_sound = QSound("/etc/pokedexos/sounds/boot.wav")
        
        # Network status
        self.network_available = True
        self.check_network_status()
        
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Status LEDs
        led_layout = QHBoxLayout()
        self.power_led = self.create_led("blue")
        self.status_led = self.create_led("red")
        self.network_led = self.create_led("green")
        led_layout.addWidget(self.power_led)
        led_layout.addWidget(self.status_led)
        led_layout.addWidget(self.network_led)
        layout.addLayout(led_layout)
        
        # Main display
        self.display = QFrame()
        self.display.setStyleSheet("""
            QFrame {
                background-color: #98FB98;
                border: 2px solid #000000;
                border-radius: 10px;
            }
        """)
        self.display.setMinimumHeight(400)
        
        # Display content
        display_layout = QVBoxLayout(self.display)
        self.display_text = QLabel("System Offline")
        self.display_text.setAlignment(Qt.AlignCenter)
        self.display_text.setStyleSheet("color: #006400; font-size: 24px;")
        display_layout.addWidget(self.display_text)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Pokémon...")
        self.search_bar.setVisible(False)
        display_layout.addWidget(self.search_bar)
        
        # Pokemon display
        self.pokemon_image = QLabel()
        self.pokemon_image.setAlignment(Qt.AlignCenter)
        display_layout.addWidget(self.pokemon_image)
        
        # Cache status
        self.cache_status = QLabel("")
        self.cache_status.setAlignment(Qt.AlignRight)
        self.cache_status.setStyleSheet("color: #006400; font-size: 12px;")
        display_layout.addWidget(self.cache_status)
        
        layout.addWidget(self.display)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        # D-pad
        dpad_layout = QGridLayout()
        self.up_btn = QPushButton("↑")
        self.down_btn = QPushButton("↓")
        self.left_btn = QPushButton("←")
        self.right_btn = QPushButton("→")
        self.center_btn = QPushButton("●")
        
        # Connect D-pad buttons
        self.up_btn.clicked.connect(lambda: self.navigate_pokemon("prev"))
        self.down_btn.clicked.connect(lambda: self.navigate_pokemon("next"))
        self.left_btn.clicked.connect(self.show_cache_menu)
        self.right_btn.clicked.connect(self.toggle_network_mode)
        
        dpad_layout.addWidget(self.up_btn, 0, 1)
        dpad_layout.addWidget(self.left_btn, 1, 0)
        dpad_layout.addWidget(self.center_btn, 1, 1)
        dpad_layout.addWidget(self.right_btn, 1, 2)
        dpad_layout.addWidget(self.down_btn, 2, 1)
        
        # Power button
        self.power_btn = QPushButton("⏻")
        self.power_btn.clicked.connect(self.toggle_power)
        
        controls_layout.addLayout(dpad_layout)
        controls_layout.addWidget(self.power_btn)
        layout.addLayout(controls_layout)
        
        # Connect search functionality
        self.search_bar.returnPressed.connect(self.search_pokemon)
        
        # Update cache status
        self.update_cache_status()
        
    def create_led(self, color):
        led = QFrame()
        led.setFixedSize(20, 20)
        led.setStyleSheet(f"""
            QFrame {{
                background-color: #{color};
                border-radius: 10px;
                border: 1px solid #000000;
            }}
        """)
        return led
        
    def check_network_status(self):
        try:
            requests.get("https://pokeapi.co/api/v2/pokemon/1", timeout=3)
            self.network_available = True
            self.network_led.setStyleSheet("background-color: green; border-radius: 10px;")
        except:
            self.network_available = False
            self.network_led.setStyleSheet("background-color: red; border-radius: 10px;")
    
    def toggle_network_mode(self):
        if not self.power_on:
            return
        
        self.check_network_status()
        mode = "Online" if self.network_available else "Offline"
        self.display_text.setText(f"Mode: {mode}\nPress ← to manage cache")
        
    def show_cache_menu(self):
        if not self.power_on:
            return
            
        menu = QMenu(self)
        cache_all = menu.addAction("Cache First 151 Pokémon")
        clear_cache = menu.addAction("Clear Cache")
        
        action = menu.exec_(self.mapToGlobal(self.left_btn.pos()))
        
        if action == cache_all:
            self.cache_all_pokemon()
        elif action == clear_cache:
            self.db_manager.clear_cache()
            self.update_cache_status()
            
    def cache_all_pokemon(self):
        self.status_led.setStyleSheet("background-color: yellow; border-radius: 10px;")
        self.display_text.setText("Caching Pokémon...\nPlease wait...")
        
        for i in range(1, 152):  # First 151 Pokemon
            try:
                response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}")
                if response.status_code == 200:
                    self.db_manager.store_pokemon(response.json())
                    self.display_text.setText(f"Caching Pokémon...\n{i}/151 complete")
            except:
                continue
                
        self.status_led.setStyleSheet("background-color: red; border-radius: 10px;")
        self.display_text.setText("Cache complete!\nPress ↑/↓ to navigate")
        self.update_cache_status()
        
    def update_cache_status(self):
        cached_count = len(self.db_manager.get_all_cached_pokemon())
        self.cache_status.setText(f"Cached: {cached_count} Pokémon")
        
    def navigate_pokemon(self, direction):
        if not self.power_on:
            return
            
        cached_pokemon = self.db_manager.get_all_cached_pokemon()
        if not cached_pokemon:
            self.display_text.setText("No cached Pokémon!\nPress ← to manage cache")
            return
            
        if direction == "next":
            self.current_pokemon_id = min(self.current_pokemon_id + 1, len(cached_pokemon))
        else:
            self.current_pokemon_id = max(self.current_pokemon_id - 1, 0)
            
        pokemon_id = cached_pokemon[self.current_pokemon_id][0]
        self.display_pokemon_data(str(pokemon_id))
        
    def toggle_power(self):
        self.power_on = not self.power_on
        if self.power_on:
            self.boot_sound.play()
            self.power_led.setStyleSheet("background-color: blue; border-radius: 10px;")
            self.display_text.setText("PokédexOS v1.0\nInitializing...")
            self.search_bar.setVisible(True)
            QTimer.singleShot(2000, self.boot_sequence)
            self.check_network_status()
        else:
            self.power_led.setStyleSheet("background-color: gray; border-radius: 10px;")
            self.display_text.setText("System Offline")
            self.search_bar.setVisible(False)
            self.pokemon_image.clear()
            
    def boot_sequence(self):
        self.display_text.setText("PokédexOS Ready\nPlease enter a Pokémon name")
        self.update_cache_status()
        
    def display_pokemon_data(self, pokemon_id):
        pokemon = self.db_manager.get_pokemon(pokemon_id)
        if pokemon:
            # Load sprite from local storage
            if pokemon['sprite_path'] and os.path.exists(pokemon['sprite_path']):
                pixmap = QPixmap(pokemon['sprite_path'])
                self.pokemon_image.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            
            # Display Pokemon info
            self.display_text.setText(f"""
                #{pokemon['id']} {pokemon['name'].title()}
                Type: {', '.join(pokemon['types'])}
                Height: {pokemon['height']}m
                Weight: {pokemon['weight']}kg
                Last Updated: {pokemon['last_updated']}
            """)
        
    @pyqtSlot()
    def search_pokemon(self):
        if not self.power_on:
            return
            
        pokemon = self.search_bar.text().lower()
        
        # Check local cache first
        cached_pokemon = self.db_manager.get_pokemon(pokemon)
        if cached_pokemon:
            self.display_pokemon_data(pokemon)
            return
            
        # If not in cache and network is available, fetch from API
        if self.network_available:
            try:
                response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store in local database
                    self.db_manager.store_pokemon(data)
                    
                    # Display the Pokemon
                    self.display_pokemon_data(pokemon)
                    self.update_cache_status()
                else:
                    self.display_text.setText("Pokémon not found!")
            except Exception as e:
                self.display_text.setText(f"Error: {str(e)}")
        else:
            self.display_text.setText("No network connection!\nPokémon not in local cache")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont('Sans Serif', 10)
    app.setFont(font)
    
    # Create and show the main window
    pokedex = PokedexOS()
    pokedex.show()
    
    sys.exit(app.exec_()) 