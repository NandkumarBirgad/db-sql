#!/usr/bin/env python3
"""
Example Usage Script for Emergency Alert System

This script demonstrates how to use the emergency alert system programmatically.
It shows various scenarios including user registration, location updates, and emergency triggers.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
DEMO_USER = {
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john.doe@example.com",
    "emergency_contact_1": "Emergency Contact 1: +1987654321",
    "emergency_contact_2": "Emergency Contact 2: +1555666777",
    "medical_info": "Type 1 Diabetes, Blood Type O+"
}

def make_request(method, endpoint, data=None):
    """Helper function to make HTTP requests"""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return None
        
        print(f"\n{'='*50}")
        print(f"{method.upper()} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        except:
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {url}")
        print("Make sure the server is running: python app.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def demo_system_check():
    """Demonstrate system health check"""
    print("\n🏥 CHECKING SYSTEM HEALTH...")
    return make_request('GET', '/health')

def demo_user_registration():
    """Demonstrate user registration"""
    print("\n👤 REGISTERING DEMO USER...")
    return make_request('POST', '/register', DEMO_USER)

def demo_location_update():
    """Demonstrate location update"""
    print("\n📍 UPDATING USER LOCATION...")
    location_data = {
        "phone": DEMO_USER["phone"],
        "latitude": 40.7128,  # New York City coordinates
        "longitude": -74.0060
    }
    return make_request('POST', '/location/update', location_data)

def demo_emergency_trigger():
    """Demonstrate emergency alert triggering"""
    print("\n🚨 TRIGGERING EMERGENCY ALERT...")
    emergency_data = {
        "phone": DEMO_USER["phone"],
        "alert_type": "medical",
        "message": "DEMO: Car accident on Highway 101, need immediate medical assistance",
        "latitude": 40.7589,  # Times Square coordinates
        "longitude": -73.9851
    }
    return make_request('POST', '/emergency/trigger', emergency_data)

def demo_quick_emergency():
    """Demonstrate quick emergency alert"""
    print("\n⚡ TRIGGERING QUICK EMERGENCY ALERT...")
    quick_data = {
        "phone": DEMO_USER["phone"],
        "alert_type": "medical"
    }
    return make_request('POST', '/emergency/quick', quick_data)

def demo_user_status():
    """Demonstrate getting user status"""
    print("\n📊 GETTING USER STATUS...")
    return make_request('GET', f'/user/status/{DEMO_USER["phone"]}')

def demo_active_alerts():
    """Demonstrate getting active alerts"""
    print("\n📋 GETTING ACTIVE ALERTS...")
    return make_request('GET', '/alerts/active')

def demo_cancel_alert(alert_id):
    """Demonstrate canceling an alert"""
    if alert_id:
        print(f"\n❌ CANCELING ALERT {alert_id}...")
        cancel_data = {"reason": "Demo completed - false alarm"}
        return make_request('POST', f'/emergency/cancel/{alert_id}', cancel_data)
    return None

def demo_system_test():
    """Demonstrate system testing"""
    print("\n🔧 TESTING SYSTEM FUNCTIONALITY...")
    test_data = {
        "phone": DEMO_USER["phone"],
        "test_location": True,
        "test_notifications": False  # Set to True to actually send test messages
    }
    return make_request('POST', '/test/system', test_data)

def demo_help():
    """Demonstrate getting help information"""
    print("\n❓ GETTING SYSTEM HELP...")
    return make_request('GET', '/emergency/help')

def main():
    """Main demonstration function"""
    print("🚨 EMERGENCY ALERT SYSTEM - DEMO SCRIPT")
    print("="*60)
    print("This script demonstrates the emergency alert system functionality.")
    print("It will register a demo user and show various features.")
    print("="*60)
    
    # Step 1: Check system health
    health = demo_system_check()
    if not health or not health.get('status') == 'healthy':
        print("❌ System is not healthy. Exiting demo.")
        return
    
    # Step 2: Register demo user
    registration = demo_user_registration()
    if not registration or not registration.get('success'):
        print("ℹ️  User might already be registered. Continuing with demo...")
    
    # Step 3: Update location
    location = demo_location_update()
    
    # Step 4: Get user status
    status = demo_user_status()
    
    # Step 5: Test system
    test_result = demo_system_test()
    
    # Step 6: Show help information
    help_info = demo_help()
    
    # Step 7: Trigger emergency alert
    print("\n⏰ Waiting 3 seconds before triggering emergency...")
    time.sleep(3)
    
    emergency_result = demo_emergency_trigger()
    alert_id = None
    if emergency_result and emergency_result.get('success'):
        alert_id = emergency_result.get('alert_id')
    
    # Step 8: Get active alerts
    active_alerts = demo_active_alerts()
    
    # Step 9: Wait and then cancel the alert
    if alert_id:
        print(f"\n⏰ Waiting 5 seconds before canceling alert {alert_id}...")
        time.sleep(5)
        cancel_result = demo_cancel_alert(alert_id)
    
    # Step 10: Final status check
    final_status = demo_user_status()
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("• User registration and management")
    print("• Location tracking and updates")
    print("• Emergency alert triggering")
    print("• Real-time notification system")
    print("• Alert management and cancellation")
    print("• System health monitoring")
    
    print("\n📱 INTEGRATION EXAMPLES:")
    print("\n1. Mobile App Integration:")
    print("   - Use /emergency/quick for panic button")
    print("   - Use /location/update for GPS tracking")
    print("   - Use /emergency/trigger for detailed alerts")
    
    print("\n2. IoT Device Integration:")
    print("   - Car crash sensors → /emergency/trigger")
    print("   - Medical alert devices → /emergency/quick")
    print("   - Home security systems → /emergency/trigger")
    
    print("\n3. Web Application:")
    print("   - Emergency contact dashboard")
    print("   - Real-time location monitoring")
    print("   - Alert history and management")
    
    print("\n⚠️  IMPORTANT PRODUCTION NOTES:")
    print("• Configure real SMS/email credentials in .env")
    print("• Integrate with actual emergency services APIs")
    print("• Implement proper authentication and security")
    print("• Set up monitoring and logging systems")
    print("• Test thoroughly before deployment")

if __name__ == '__main__':
    main()