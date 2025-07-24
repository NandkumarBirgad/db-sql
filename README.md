# 🚨 Emergency Alert System - Python Backend

A comprehensive Python backend system for automatically sending a user's current location to emergency services (ambulance, police, fire) during accidents or emergencies. The system provides a single emergency trigger that can save lives by instantly notifying the appropriate emergency services and contacts.

## 🏥 Key Features

- **Single-Click Emergency Alert**: Trigger emergency response with one API call
- **Automatic Location Detection**: GPS coordinates, IP-based location, and address lookup
- **Multi-Channel Notifications**: SMS, Email, and Emergency Service APIs
- **Emergency Contact System**: Notify family/friends automatically
- **Hospital/Service Finder**: Locate nearest hospitals and emergency services
- **Real-time Tracking**: Location history and emergency alert monitoring
- **Alert Management**: Cancel, modify, and track emergency alerts
- **Comprehensive Logging**: Full audit trail for emergency responses

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd emergency-alert-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

### 2. Run the System

```bash
# Start the emergency alert system
python app.py
```

The system will start on `http://localhost:5000`

### 3. Test the System

```bash
# Run the demo script
python example_usage.py
```

## 📱 Core Emergency Endpoints

### Single-Click Emergency (Recommended)
```bash
POST /emergency/quick
{
  "phone": "+1234567890",
  "alert_type": "medical"
}
```

### Emergency with Specific Location
```bash
POST /emergency/trigger
{
  "phone": "+1234567890",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "alert_type": "medical",
  "message": "Car accident, need immediate help"
}
```

### User Registration
```bash
POST /register
{
  "name": "John Doe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "emergency_contact_1": "Wife: +1987654321",
  "emergency_contact_2": "Brother: +1555666777",
  "medical_info": "Type 1 Diabetes, Blood Type O+"
}
```

## 🔧 Configuration

Create a `.env` file with the following configuration:

```env
# SMS Notifications (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Email Notifications
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_specific_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Location Services
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Emergency Services API (Production)
EMERGENCY_API_ENDPOINT=https://api.emergency-services.local
EMERGENCY_API_KEY=your_emergency_api_key
```

### Required API Keys

1. **Twilio SMS** (Get from [Twilio Console](https://www.twilio.com/console))
   - Account SID, Auth Token, Phone Number
   - Used for SMS notifications to emergency contacts

2. **Google Maps API** (Get from [Google Cloud Console](https://console.cloud.google.com/))
   - Places API for finding hospitals
   - Geocoding API for address lookup

3. **Email Service** (Gmail recommended)
   - Use app-specific password for Gmail
   - Alternative SMTP servers supported

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Mobile App    │────│   Flask API      │────│   Database      │
│   Web Client    │    │   (app.py)       │    │   (SQLite)      │
│   IoT Device    │    └──────────────────┘    └─────────────────┘
└─────────────────┘             │
                                │
                    ┌──────────────────┐
                    │ Emergency Service │
                    │  (Core Logic)     │
                    └──────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Location     │    │ Notification     │    │ Database        │
│ Service      │    │ Service          │    │ Manager         │
│              │    │                  │    │                 │
│ • GPS        │    │ • SMS (Twilio)   │    │ • User Data     │
│ • Geocoding  │    │ • Email (SMTP)   │    │ • Locations     │
│ • Hospitals  │    │ • Emergency APIs │    │ • Alerts        │
└──────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Database Schema

The system uses SQLite with the following main tables:

- **users**: User profiles and medical information
- **location_history**: GPS tracking and location updates
- **emergency_alerts**: Active and historical emergency alerts
- **emergency_contacts**: Emergency contact information

## 🚨 Emergency Flow

1. **Trigger Received**: API call to emergency endpoint
2. **User Lookup**: Validate user and get profile
3. **Location Detection**: Get current or last known location
4. **Emergency Services**: Send alert to 911/emergency API
5. **Contact Notification**: SMS/Email to emergency contacts
6. **Hospital Lookup**: Find nearest medical facilities
7. **Confirmation**: Send confirmation to user
8. **Monitoring**: Track alert status and follow-up

## 📱 Integration Examples

### Mobile App (React Native/Flutter)

```javascript
// Emergency button in mobile app
const triggerEmergency = async () => {
  const location = await getCurrentPosition();
  
  const response = await fetch('/emergency/trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: userPhone,
      latitude: location.latitude,
      longitude: location.longitude,
      alert_type: 'medical'
    })
  });
};
```

### IoT Device (Car Crash Sensor)

```python
# Automatic crash detection
def crash_detected(impact_force, location):
    if impact_force > THRESHOLD:
        emergency_data = {
            'phone': vehicle_owner_phone,
            'latitude': location['lat'],
            'longitude': location['lng'],
            'alert_type': 'accident',
            'message': f'Vehicle crash detected. Impact force: {impact_force}G'
        }
        
        requests.post(f'{EMERGENCY_API}/emergency/trigger', json=emergency_data)
```

### Smart Home Integration

```python
# Medical emergency detection
def medical_emergency_detected(sensor_data):
    emergency_request = {
        'phone': homeowner_phone,
        'alert_type': 'medical',
        'message': 'Medical emergency detected by home sensors'
    }
    
    requests.post(f'{EMERGENCY_API}/emergency/quick', json=emergency_request)
```

## 🔒 Security Considerations

### Production Deployment

1. **HTTPS Only**: Use SSL/TLS certificates
2. **Authentication**: Implement JWT tokens or API keys
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: Sanitize all inputs
5. **Data Encryption**: Encrypt sensitive data at rest
6. **Audit Logging**: Log all emergency activities

### Data Privacy

- Medical information encrypted
- Location data retention policies
- GDPR/HIPAA compliance considerations
- Emergency contact consent management

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### System Test
```bash
python example_usage.py
```

### Load Testing
```bash
# Test emergency endpoint under load
python tests/load_test.py
```

## 📈 Monitoring & Alerts

### Production Monitoring

1. **Health Checks**: `/health` endpoint monitoring
2. **Alert Response Time**: Track emergency notification speed
3. **Location Accuracy**: Monitor GPS/location services
4. **Notification Delivery**: Track SMS/email success rates
5. **Database Performance**: Monitor response times

### Logging

```python
# Emergency alerts are logged with CRITICAL level
logger.critical(f"EMERGENCY ALERT - User: {user}, Location: {lat},{lng}")
```

## 🌍 Deployment Options

### Local Development
```bash
python app.py
```

### Docker Deployment
```bash
docker build -t emergency-alert-system .
docker run -p 5000:5000 emergency-alert-system
```

### Cloud Deployment (AWS/GCP/Azure)
- Use managed databases (RDS/Cloud SQL)
- Configure auto-scaling for high availability
- Set up monitoring and alerting
- Use managed SMS services (SNS/Pub-Sub)

## 🆘 Real-World Integration

### Emergency Services

To integrate with actual emergency services:

1. **Contact local emergency dispatch centers**
2. **Get certified emergency service API access**
3. **Implement local emergency number protocols**
4. **Follow regional emergency communication standards**

### Healthcare Integration

- Hospital emergency department APIs
- Medical alert service providers
- EMS dispatch systems
- Healthcare provider notifications

## 📞 Emergency Numbers by Region

The system can be configured for different regions:

```python
# config.py
EMERGENCY_NUMBERS = {
    'US': {'ambulance': '911', 'police': '911', 'fire': '911'},
    'UK': {'ambulance': '999', 'police': '999', 'fire': '999'},
    'EU': {'emergency': '112'},
    'AU': {'emergency': '000'}
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## ⚠️ Important Disclaimers

1. **Test Thoroughly**: Always test in non-emergency situations
2. **Local Compliance**: Ensure compliance with local emergency service protocols
3. **Backup Plans**: Always have alternative emergency communication methods
4. **False Alerts**: Implement safeguards against accidental emergency triggers
5. **Professional Integration**: Work with emergency service professionals for production deployment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For technical support or questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the example usage script

---

**⚠️ CRITICAL NOTE**: This system is designed to assist in emergencies but should not be the only method of emergency communication. Always ensure you have multiple ways to contact emergency services.

**🚨 IN A REAL EMERGENCY**: Call your local emergency number (911, 999, 112, etc.) directly if possible.
