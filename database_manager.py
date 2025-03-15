#!/usr/bin/env python3

import os
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

class PokemonDatabaseManager:
    def __init__(self, db_path="/etc/pokedexos/database/pokemon.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _ensure_db_directory(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _create_tables(self):
        # Create Pokemon table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                types TEXT NOT NULL,
                height REAL NOT NULL,
                weight REAL NOT NULL,
                sprite_path TEXT,
                last_updated TIMESTAMP
            )
        """)
        
        # Create Pokemon descriptions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_descriptions (
                pokemon_id INTEGER,
                language TEXT,
                description TEXT,
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                PRIMARY KEY (pokemon_id, language)
            )
        """)
        
        self.conn.commit()

    def store_pokemon(self, data):
        """Store Pokemon data in the local database"""
        # Convert types list to JSON string
        types_json = json.dumps([t['type']['name'] for t in data['types']])
        
        # Download and save sprite
        sprite_path = None
        if data['sprites']['front_default']:
            sprite_path = self._save_sprite(data['id'], data['sprites']['front_default'])

        # Insert or update Pokemon data
        self.cursor.execute("""
            INSERT OR REPLACE INTO pokemon 
            (id, name, types, height, weight, sprite_path, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['id'],
            data['name'],
            types_json,
            data['height'] / 10,  # Convert to meters
            data['weight'] / 10,  # Convert to kilograms
            sprite_path,
            datetime.now().isoformat()
        ))
        
        self.conn.commit()

    def _save_sprite(self, pokemon_id, sprite_url):
        """Download and save sprite image locally"""
        sprite_dir = "/etc/pokedexos/database/sprites"
        os.makedirs(sprite_dir, exist_ok=True)
        
        sprite_path = f"{sprite_dir}/{pokemon_id}.png"
        
        # Download sprite if it doesn't exist
        if not os.path.exists(sprite_path):
            response = requests.get(sprite_url)
            if response.status_code == 200:
                with open(sprite_path, 'wb') as f:
                    f.write(response.content)
                return sprite_path
        return sprite_path

    def get_pokemon(self, identifier):
        """Get Pokemon data from local database"""
        # Try to find by ID or name
        if isinstance(identifier, int) or identifier.isdigit():
            query = "SELECT * FROM pokemon WHERE id = ?"
        else:
            query = "SELECT * FROM pokemon WHERE name = ?"
            identifier = identifier.lower()

        self.cursor.execute(query, (identifier,))
        result = self.cursor.fetchone()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'types': json.loads(result[2]),
                'height': result[3],
                'weight': result[4],
                'sprite_path': result[5],
                'last_updated': result[6]
            }
        return None

    def is_pokemon_cached(self, identifier):
        """Check if Pokemon exists in local database"""
        pokemon = self.get_pokemon(identifier)
        return pokemon is not None

    def get_all_cached_pokemon(self):
        """Get list of all cached Pokemon"""
        self.cursor.execute("SELECT id, name FROM pokemon ORDER BY id")
        return self.cursor.fetchall()

    def clear_cache(self):
        """Clear all cached Pokemon data"""
        self.cursor.execute("DELETE FROM pokemon")
        self.cursor.execute("DELETE FROM pokemon_descriptions")
        self.conn.commit()
        
        # Remove sprite files
        sprite_dir = "/etc/pokedexos/database/sprites"
        if os.path.exists(sprite_dir):
            for file in os.listdir(sprite_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(sprite_dir, file))

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close() 