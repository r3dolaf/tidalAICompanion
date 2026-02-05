import sqlite3
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to 'tidal.db' in the parent directory (raspberry-pi root)
            base_dir = os.path.dirname(os.path.dirname(__file__))
            self.db_path = os.path.join(base_dir, 'tidal.db')
        else:
            self.db_path = db_path
            
        self._init_db()

    def _get_conn(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database schema"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # History Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    style TEXT,
                    density REAL,
                    complexity REAL,
                    tempo INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    thoughts TEXT,
                    is_favorite INTEGER DEFAULT 0
                )
            ''')
            
            # Favorites Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    name TEXT,
                    style TEXT,
                    tags TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"💾 Database initialized at: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    # --- HISTORY METHODS ---
    
    def add_history_entry(self, pattern, style, density, complexity, tempo, thoughts=None):
        """Add a generated pattern to history"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            thoughts_json = json.dumps(thoughts) if thoughts else "[]"
            
            cursor.execute('''
                INSERT INTO history (pattern, style, density, complexity, tempo, thoughts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pattern, style, density, complexity, tempo, thoughts_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding history: {e}")
            return False

    def get_history(self, limit=50):
        """Get recent history entries"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM history 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dicts
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []

    # --- FAVORITES METHODS ---

    def add_favorite(self, pattern, name, style, tags=None, metadata=None):
        """Save a pattern as favorite"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Check for duplicates? For now, allow duplicates with different names
            metadata_json = json.dumps(metadata) if metadata else "{}"
            
            cursor.execute('''
                INSERT INTO favorites (pattern, name, style, tags, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (pattern, name, style, tags or "", metadata_json))
            
            new_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return new_id
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return None

    def get_favorites(self):
        """Get all favorites"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM favorites ORDER BY timestamp DESC')
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting favorites: {e}")
            return []

    def delete_favorite(self, fav_id):
        """Delete a favorite by ID"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM favorites WHERE id = ?', (fav_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting favorite: {e}")
            return False

    def import_client_data(self, history_list, favorites_list):
        """Bulk import data from client localStorage"""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            
            # Import History
            count_h = 0
            for h in history_list:
                # Basic validation
                if 'pattern' in h:
                    cursor.execute('''
                        INSERT INTO history (pattern, style, density, complexity, tempo, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        h.get('pattern'),
                        h.get('style', 'unknown'),
                        h.get('density', 0.5),
                        h.get('complexity', 0.5),
                        h.get('tempo', 140),
                        h.get('timestamp', datetime.now())
                    ))
                    count_h += 1
            
            # Import Favorites
            count_f = 0
            for f in favorites_list:
                if 'pattern' in f:
                    cursor.execute('''
                        INSERT INTO favorites (pattern, name, style, tags, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        f.get('pattern'),
                        f.get('name', 'Imported Favorite'),
                        f.get('style', 'unknown'),
                        f.get('tags', 'imported'),
                        f.get('timestamp', datetime.now())
                    ))
                    count_f += 1
            
            conn.commit()
            return count_h, count_f
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            conn.rollback()
            return 0, 0
        finally:
            conn.close()
