import sqlite3
import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    email TEXT,
                    emergency_contact_1 TEXT,
                    emergency_contact_2 TEXT,
                    medical_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Location history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS location_history (
                    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Emergency alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_alerts (
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    alert_type TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    address TEXT,
                    status TEXT DEFAULT 'active',
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Emergency contacts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_contacts (
                    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    relationship TEXT,
                    is_primary BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Emergency services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emergency_services (
                    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    service_type TEXT,
                    coverage_area TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.commit()
    
    def add_user(self, name, phone, email=None, emergency_contact_1=None, 
                 emergency_contact_2=None, medical_info=None):
        """Add a new user to the system"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, phone, email, emergency_contact_1, 
                                 emergency_contact_2, medical_info)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, emergency_contact_1, emergency_contact_2, medical_info))
            return cursor.lastrowid
    
    def get_user_by_phone(self, phone):
        """Get user information by phone number"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
            return cursor.fetchone()
    
    def update_user_location(self, user_id, latitude, longitude, address=None):
        """Update user's current location"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO location_history (user_id, latitude, longitude, address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, latitude, longitude, address))
            return cursor.lastrowid
    
    def create_emergency_alert(self, user_id, alert_type, latitude, longitude, 
                             address=None, message=None):
        """Create a new emergency alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emergency_alerts (user_id, alert_type, latitude, 
                                            longitude, address, message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, alert_type, latitude, longitude, address, message))
            return cursor.lastrowid
    
    def get_user_location(self, user_id):
        """Get user's latest location"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT latitude, longitude, address, timestamp 
                FROM location_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (user_id,))
            return cursor.fetchone()
    
    def add_emergency_contact(self, user_id, name, phone, relationship=None, is_primary=False):
        """Add emergency contact for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emergency_contacts (user_id, name, phone, relationship, is_primary)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, phone, relationship, is_primary))
            return cursor.lastrowid
    
    def get_emergency_contacts(self, user_id):
        """Get all emergency contacts for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, phone, relationship, is_primary 
                FROM emergency_contacts 
                WHERE user_id = ?
                ORDER BY is_primary DESC
            ''', (user_id,))
            return cursor.fetchall()
    
    def get_active_alerts(self):
        """Get all active emergency alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, u.name, u.phone 
                FROM emergency_alerts a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.status = 'active'
                ORDER BY a.created_at DESC
            ''')
            return cursor.fetchall()
    
    def resolve_alert(self, alert_id):
        """Mark an emergency alert as resolved"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE emergency_alerts 
                SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
                WHERE alert_id = ?
            ''', (alert_id,))
            return cursor.rowcount > 0