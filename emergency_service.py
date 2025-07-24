import datetime
import threading
import time
from database import DatabaseManager
from location_service import LocationService
from notification_service import NotificationService
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyService:
    def __init__(self):
        self.db = DatabaseManager()
        self.location_service = LocationService()
        self.notification_service = NotificationService()
        self.active_alerts = {}
        self.monitoring_threads = {}
    
    def register_user(self, name, phone, email=None, emergency_contact_1=None, 
                     emergency_contact_2=None, medical_info=None):
        """Register a new user in the emergency system"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_phone(phone)
            if existing_user:
                logger.warning(f"User with phone {phone} already exists")
                return {'success': False, 'message': 'User already registered'}
            
            # Add user to database
            user_id = self.db.add_user(
                name=name,
                phone=phone,
                email=email,
                emergency_contact_1=emergency_contact_1,
                emergency_contact_2=emergency_contact_2,
                medical_info=medical_info
            )
            
            logger.info(f"User {name} registered successfully with ID {user_id}")
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User registered successfully'
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def update_user_location(self, phone, latitude, longitude):
        """Update user's location in the system"""
        try:
            # Get user information
            user = self.db.get_user_by_phone(phone)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user_id = user[0]  # user_id is the first column
            
            # Get address from coordinates
            location_data = self.location_service.get_location_from_coordinates(latitude, longitude)
            address = location_data.get('address') if location_data else None
            
            # Update location in database
            location_id = self.db.update_user_location(user_id, latitude, longitude, address)
            
            # Check if user is in a high-risk zone
            high_risk = self.location_service.is_in_high_risk_zone(latitude, longitude)
            
            return {
                'success': True,
                'location_id': location_id,
                'address': address,
                'high_risk_zone': high_risk,
                'message': 'Location updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating location: {e}")
            return {'success': False, 'message': f'Location update failed: {str(e)}'}
    
    def trigger_emergency_alert(self, phone, alert_type="medical", message=None, 
                               latitude=None, longitude=None):
        """Trigger an emergency alert for a user"""
        try:
            # Get user information
            user = self.db.get_user_by_phone(phone)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user_id = user[0]
            user_data = {
                'user_id': user_id,
                'name': user[1],
                'phone': user[2],
                'email': user[3],
                'emergency_contact_1': user[4],
                'emergency_contact_2': user[5],
                'medical_info': user[6]
            }
            
            # Get location (use provided coordinates or last known location)
            if latitude is not None and longitude is not None:
                location_data = self.location_service.get_location_from_coordinates(latitude, longitude)
                if location_data:
                    # Update location in database
                    self.db.update_user_location(user_id, latitude, longitude, location_data.get('address'))
                else:
                    location_data = {'latitude': latitude, 'longitude': longitude}
            else:
                # Get last known location
                last_location = self.db.get_user_location(user_id)
                if last_location:
                    latitude, longitude = last_location[0], last_location[1]
                    location_data = {
                        'latitude': latitude,
                        'longitude': longitude,
                        'address': last_location[2],
                        'timestamp': last_location[3]
                    }
                else:
                    # Try to get location from IP as fallback
                    ip_location = self.location_service.get_current_location_ip()
                    if ip_location:
                        latitude = ip_location['latitude']
                        longitude = ip_location['longitude']
                        location_data = ip_location
                        # Update location in database
                        self.db.update_user_location(user_id, latitude, longitude, ip_location.get('address'))
                    else:
                        return {'success': False, 'message': 'No location data available'}
            
            # Format location for emergency services
            emergency_location = self.location_service.format_location_for_emergency(
                latitude, longitude, location_data.get('address')
            )
            
            # Add timestamp
            emergency_location['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create emergency alert in database
            alert_id = self.db.create_emergency_alert(
                user_id=user_id,
                alert_type=alert_type,
                latitude=latitude,
                longitude=longitude,
                address=emergency_location.get('address'),
                message=message
            )
            
            # Send emergency notifications
            notification_result = self.notification_service.send_emergency_alert(
                user_data=user_data,
                location_data=emergency_location,
                alert_type=alert_type,
                message=message
            )
            
            # Store active alert
            self.active_alerts[alert_id] = {
                'user_id': user_id,
                'phone': phone,
                'alert_type': alert_type,
                'location': emergency_location,
                'timestamp': emergency_location['timestamp'],
                'notification_result': notification_result
            }
            
            # Start monitoring thread for this alert
            self._start_alert_monitoring(alert_id)
            
            logger.critical(f"EMERGENCY ALERT TRIGGERED - Alert ID: {alert_id}, User: {user_data['name']}, Location: {latitude}, {longitude}")
            
            return {
                'success': True,
                'alert_id': alert_id,
                'location': emergency_location,
                'notification_result': notification_result,
                'message': 'Emergency alert sent successfully'
            }
            
        except Exception as e:
            logger.error(f"Error triggering emergency alert: {e}")
            return {'success': False, 'message': f'Emergency alert failed: {str(e)}'}
    
    def cancel_emergency_alert(self, alert_id, reason="User cancelled"):
        """Cancel an active emergency alert"""
        try:
            if alert_id not in self.active_alerts:
                return {'success': False, 'message': 'Alert not found or already resolved'}
            
            # Mark alert as resolved in database
            self.db.resolve_alert(alert_id)
            
            # Get alert info
            alert_info = self.active_alerts[alert_id]
            
            # Stop monitoring thread
            if alert_id in self.monitoring_threads:
                self.monitoring_threads[alert_id].cancel()
                del self.monitoring_threads[alert_id]
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            # Send cancellation notification
            user = self.db.get_user_by_phone(alert_info['phone'])
            if user:
                cancellation_message = f"Emergency alert has been cancelled. Reason: {reason}"
                self.notification_service.send_sms(alert_info['phone'], cancellation_message)
            
            logger.info(f"Emergency alert {alert_id} cancelled. Reason: {reason}")
            
            return {
                'success': True,
                'message': f'Alert cancelled successfully. Reason: {reason}'
            }
            
        except Exception as e:
            logger.error(f"Error cancelling alert: {e}")
            return {'success': False, 'message': f'Failed to cancel alert: {str(e)}'}
    
    def get_user_status(self, phone):
        """Get current status of a user"""
        try:
            user = self.db.get_user_by_phone(phone)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user_id = user[0]
            
            # Get latest location
            location = self.db.get_user_location(user_id)
            
            # Get emergency contacts
            contacts = self.db.get_emergency_contacts(user_id)
            
            # Check for active alerts
            active_alert = None
            for alert_id, alert_info in self.active_alerts.items():
                if alert_info['user_id'] == user_id:
                    active_alert = {
                        'alert_id': alert_id,
                        'alert_type': alert_info['alert_type'],
                        'timestamp': alert_info['timestamp']
                    }
                    break
            
            return {
                'success': True,
                'user_info': {
                    'name': user[1],
                    'phone': user[2],
                    'email': user[3],
                    'medical_info': user[6]
                },
                'location': {
                    'latitude': location[0] if location else None,
                    'longitude': location[1] if location else None,
                    'address': location[2] if location else None,
                    'last_update': location[3] if location else None
                },
                'emergency_contacts': contacts,
                'active_alert': active_alert
            }
            
        except Exception as e:
            logger.error(f"Error getting user status: {e}")
            return {'success': False, 'message': f'Failed to get status: {str(e)}'}
    
    def _start_alert_monitoring(self, alert_id):
        """Start a monitoring thread for an emergency alert"""
        def monitor_alert():
            time.sleep(Config.AUTO_ALERT_TIMEOUT)
            
            if alert_id in self.active_alerts:
                alert_info = self.active_alerts[alert_id]
                
                # Send follow-up notification
                follow_up_message = "Emergency services have been dispatched to your location. If this was sent in error, please contact emergency services immediately."
                
                self.notification_service.send_sms(
                    alert_info['phone'],
                    follow_up_message,
                    emergency=True
                )
                
                logger.info(f"Follow-up notification sent for alert {alert_id}")
        
        # Create and start monitoring thread
        timer = threading.Timer(Config.AUTO_ALERT_TIMEOUT, monitor_alert)
        timer.start()
        self.monitoring_threads[alert_id] = timer
    
    def get_active_alerts(self):
        """Get all currently active emergency alerts"""
        try:
            return {
                'success': True,
                'active_alerts': self.active_alerts,
                'count': len(self.active_alerts)
            }
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return {'success': False, 'message': f'Failed to get alerts: {str(e)}'}
    
    def test_system(self, phone, test_location=True, test_notifications=True):
        """Test the emergency system functionality"""
        try:
            results = {'success': True, 'tests': {}}
            
            # Test user lookup
            user = self.db.get_user_by_phone(phone)
            if user:
                results['tests']['user_lookup'] = {'status': 'passed', 'message': 'User found'}
            else:
                results['tests']['user_lookup'] = {'status': 'failed', 'message': 'User not found'}
                results['success'] = False
                return results
            
            # Test location services
            if test_location:
                ip_location = self.location_service.get_current_location_ip()
                if ip_location:
                    results['tests']['location_service'] = {'status': 'passed', 'location': ip_location}
                else:
                    results['tests']['location_service'] = {'status': 'failed', 'message': 'Could not get location'}
            
            # Test notifications
            if test_notifications:
                user_data = {
                    'phone': user[2],
                    'email': user[3]
                }
                
                notification_results = self.notification_service.send_test_notification(
                    phone=user_data['phone'],
                    email=user_data['email']
                )
                
                results['tests']['notifications'] = {
                    'status': 'passed' if notification_results else 'failed',
                    'details': notification_results
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing system: {e}")
            return {'success': False, 'message': f'System test failed: {str(e)}'}
    
    def shutdown(self):
        """Shutdown the emergency service and clean up resources"""
        try:
            # Cancel all monitoring threads
            for timer in self.monitoring_threads.values():
                timer.cancel()
            
            logger.info("Emergency service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")