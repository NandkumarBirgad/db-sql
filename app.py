from flask import Flask, request, jsonify
from flask_cors import CORS
from emergency_service import EmergencyService
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Emergency Service
emergency_service = EmergencyService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Emergency Alert System is running',
        'version': '1.0.0'
    })

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user in the emergency system"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'phone' not in data:
            return jsonify({
                'success': False,
                'message': 'Name and phone are required fields'
            }), 400
        
        result = emergency_service.register_user(
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            emergency_contact_1=data.get('emergency_contact_1'),
            emergency_contact_2=data.get('emergency_contact_2'),
            medical_info=data.get('medical_info')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in register_user: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/location/update', methods=['POST'])
def update_location():
    """Update user's current location"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'phone' not in data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'message': 'Phone, latitude, and longitude are required'
            }), 400
        
        result = emergency_service.update_user_location(
            phone=data['phone'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude'])
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in update_location: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/emergency/trigger', methods=['POST'])
def trigger_emergency():
    """Trigger an emergency alert - THIS IS THE MAIN EMERGENCY ENDPOINT"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'phone' not in data:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400
        
        result = emergency_service.trigger_emergency_alert(
            phone=data['phone'],
            alert_type=data.get('alert_type', 'medical'),
            message=data.get('message'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in trigger_emergency: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/emergency/cancel/<int:alert_id>', methods=['POST'])
def cancel_emergency(alert_id):
    """Cancel an active emergency alert"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'User cancelled')
        
        result = emergency_service.cancel_emergency_alert(alert_id, reason)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in cancel_emergency: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/user/status/<phone>', methods=['GET'])
def get_user_status(phone):
    """Get current status of a user"""
    try:
        result = emergency_service.get_user_status(phone)
        
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_user_status: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/alerts/active', methods=['GET'])
def get_active_alerts():
    """Get all currently active emergency alerts"""
    try:
        result = emergency_service.get_active_alerts()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_active_alerts: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/test/system', methods=['POST'])
def test_system():
    """Test the emergency system functionality"""
    try:
        data = request.get_json()
        
        if not data or 'phone' not in data:
            return jsonify({
                'success': False,
                'message': 'Phone number is required for testing'
            }), 400
        
        result = emergency_service.test_system(
            phone=data['phone'],
            test_location=data.get('test_location', True),
            test_notifications=data.get('test_notifications', False)  # Default False to avoid sending test messages
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in test_system: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/emergency/quick', methods=['POST'])
def quick_emergency():
    """Quick emergency endpoint - automatically get location and send alert"""
    try:
        data = request.get_json()
        
        if not data or 'phone' not in data:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400
        
        # This endpoint is designed for single-click emergency activation
        # It will use the last known location or try to get current location
        result = emergency_service.trigger_emergency_alert(
            phone=data['phone'],
            alert_type=data.get('alert_type', 'medical'),
            message="URGENT: Single-click emergency alert activated"
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in quick_emergency: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/emergency/help', methods=['GET'])
def emergency_help():
    """Get help information about using the emergency system"""
    help_info = {
        'emergency_system_usage': {
            'quick_emergency': {
                'endpoint': '/emergency/quick',
                'method': 'POST',
                'description': 'Single-click emergency alert',
                'required_fields': ['phone'],
                'optional_fields': ['alert_type'],
                'example': {
                    'phone': '+1234567890',
                    'alert_type': 'medical'
                }
            },
            'emergency_with_location': {
                'endpoint': '/emergency/trigger',
                'method': 'POST',
                'description': 'Emergency alert with specific location',
                'required_fields': ['phone'],
                'optional_fields': ['latitude', 'longitude', 'alert_type', 'message'],
                'example': {
                    'phone': '+1234567890',
                    'latitude': 40.7128,
                    'longitude': -74.0060,
                    'alert_type': 'medical',
                    'message': 'Car accident, need immediate help'
                }
            }
        },
        'alert_types': ['medical', 'fire', 'police', 'general'],
        'emergency_numbers': {
            'ambulance': '911',
            'police': '911',
            'fire': '911'
        },
        'system_features': [
            'Automatic location detection',
            'Emergency contact notification',
            'Hospital/emergency service lookup',
            'SMS and email alerts',
            'Real-time location tracking'
        ]
    }
    
    return jsonify({
        'success': True,
        'help': help_info
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

def main():
    """Main function to run the emergency alert system"""
    logger.info("Starting Emergency Alert System...")
    
    # Print system information
    print("\n" + "="*60)
    print("🚨 EMERGENCY ALERT SYSTEM BACKEND 🚨")
    print("="*60)
    print("Server Status: RUNNING")
    print("Emergency Services: READY")
    print("Location Services: READY")
    print("Notification System: READY")
    print("="*60)
    print("\nMain Emergency Endpoints:")
    print("• POST /emergency/quick - Single-click emergency")
    print("• POST /emergency/trigger - Emergency with location")
    print("• POST /register - Register new user")
    print("• GET /emergency/help - System help")
    print("="*60)
    print("\nIMPORTANT SETUP NOTES:")
    print("1. Create a .env file with your API keys:")
    print("   - TWILIO_ACCOUNT_SID=your_twilio_sid")
    print("   - TWILIO_AUTH_TOKEN=your_twilio_token")
    print("   - TWILIO_PHONE_NUMBER=your_twilio_phone")
    print("   - EMAIL_USERNAME=your_email")
    print("   - EMAIL_PASSWORD=your_email_password")
    print("   - GOOGLE_MAPS_API_KEY=your_google_maps_key")
    print("\n2. In production, configure real emergency service APIs")
    print("3. Test the system with /test/system endpoint")
    print("="*60)
    
    try:
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Set to False in production
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Shutting down Emergency Alert System...")
        emergency_service.shutdown()
    except Exception as e:
        logger.error(f"Error running server: {e}")
    finally:
        emergency_service.shutdown()

if __name__ == '__main__':
    main()