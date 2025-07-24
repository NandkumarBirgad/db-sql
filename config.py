import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Emergency Services Configuration
    EMERGENCY_NUMBERS = {
        'ambulance': '911',  # Replace with local emergency number
        'police': '911',
        'fire': '911',
        'general_emergency': '911'
    }
    
    # Twilio Configuration for SMS notifications
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Database Configuration
    DATABASE_PATH = 'emergency_system.db'
    
    # Emergency Services API (Replace with actual emergency services API)
    EMERGENCY_API_ENDPOINT = os.getenv('EMERGENCY_API_ENDPOINT', 'https://api.emergency-services.local')
    EMERGENCY_API_KEY = os.getenv('EMERGENCY_API_KEY')
    
    # Location Services
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Alert Configuration
    AUTO_ALERT_TIMEOUT = 30  # seconds before auto-alert
    LOCATION_UPDATE_INTERVAL = 5  # seconds
    
    # Emergency Contact Configuration
    MAX_EMERGENCY_CONTACTS = 5
    
    # Geofencing (for high-risk areas)
    HIGH_RISK_ZONES = [
        # Add coordinates for high-risk areas
        # {'lat': 40.7128, 'lng': -74.0060, 'radius': 1000}  # Example: NYC area
    ]