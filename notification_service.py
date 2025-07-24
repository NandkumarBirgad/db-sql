import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from config import Config
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.twilio_client = None
        self.setup_twilio()
    
    def setup_twilio(self):
        """Initialize Twilio client if credentials are available"""
        try:
            if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
                self.twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
                logger.info("Twilio client initialized successfully")
            else:
                logger.warning("Twilio credentials not configured")
        except Exception as e:
            logger.error(f"Error initializing Twilio: {e}")
    
    def send_sms(self, to_phone, message, emergency=False):
        """Send SMS notification"""
        try:
            if not self.twilio_client:
                logger.error("Twilio client not initialized")
                return False
            
            if emergency:
                message = f"🚨 EMERGENCY ALERT 🚨\n{message}"
            
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=Config.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully. Message SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def send_email(self, to_email, subject, body, emergency=False):
        """Send email notification"""
        try:
            if not Config.EMAIL_USERNAME or not Config.EMAIL_PASSWORD:
                logger.error("Email credentials not configured")
                return False
            
            if emergency:
                subject = f"🚨 EMERGENCY ALERT: {subject}"
            
            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(Config.EMAIL_USERNAME, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def notify_emergency_services(self, emergency_data):
        """Send alert to emergency services"""
        try:
            # In a real implementation, this would integrate with actual emergency services API
            # For now, we'll log the emergency and simulate the notification
            
            emergency_message = self._format_emergency_message(emergency_data)
            
            # Log the emergency (in production, this would be sent to emergency services)
            logger.critical(f"EMERGENCY ALERT SENT TO SERVICES: {emergency_message}")
            
            # Simulate API call to emergency services
            if Config.EMERGENCY_API_ENDPOINT and Config.EMERGENCY_API_KEY:
                response = self._send_to_emergency_api(emergency_data)
                return response
            else:
                # Fallback: Send to emergency number via SMS
                return self._send_emergency_sms(emergency_data)
                
        except Exception as e:
            logger.error(f"Error notifying emergency services: {e}")
            return False
    
    def _send_to_emergency_api(self, emergency_data):
        """Send emergency data to official emergency services API"""
        try:
            headers = {
                'Authorization': f'Bearer {Config.EMERGENCY_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'alert_type': emergency_data.get('alert_type', 'general'),
                'location': {
                    'latitude': emergency_data['latitude'],
                    'longitude': emergency_data['longitude'],
                    'address': emergency_data.get('address')
                },
                'user_info': {
                    'name': emergency_data.get('user_name'),
                    'phone': emergency_data.get('user_phone'),
                    'medical_info': emergency_data.get('medical_info')
                },
                'timestamp': emergency_data.get('timestamp'),
                'message': emergency_data.get('message')
            }
            
            response = requests.post(
                Config.EMERGENCY_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Emergency alert sent to official services successfully")
                return True
            else:
                logger.error(f"Emergency API responded with status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending to emergency API: {e}")
            return False
    
    def _send_emergency_sms(self, emergency_data):
        """Send emergency SMS to emergency number"""
        try:
            emergency_number = Config.EMERGENCY_NUMBERS.get('ambulance', '911')
            message = self._format_emergency_message(emergency_data)
            
            # Note: In real implementation, sending SMS to 911 might not be supported
            # This is for demonstration purposes
            logger.info(f"Would send emergency SMS to {emergency_number}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending emergency SMS: {e}")
            return False
    
    def _format_emergency_message(self, emergency_data):
        """Format emergency data into a readable message"""
        message = f"""
🚨 EMERGENCY ALERT 🚨

Alert Type: {emergency_data.get('alert_type', 'General Emergency')}
User: {emergency_data.get('user_name', 'Unknown')}
Phone: {emergency_data.get('user_phone', 'Not provided')}

LOCATION:
Coordinates: {emergency_data['latitude']}, {emergency_data['longitude']}
Address: {emergency_data.get('address', 'Address not available')}
Google Maps: https://www.google.com/maps?q={emergency_data['latitude']},{emergency_data['longitude']}

Time: {emergency_data.get('timestamp', 'Not specified')}
Message: {emergency_data.get('message', 'No additional message')}

Medical Info: {emergency_data.get('medical_info', 'None provided')}

NEAREST HOSPITALS:
"""
        
        # Add nearest hospitals information
        hospitals = emergency_data.get('nearest_hospitals', [])
        if hospitals:
            for i, hospital in enumerate(hospitals[:3], 1):
                message += f"\n{i}. {hospital.get('name', 'Unknown Hospital')}"
                message += f"\n   Address: {hospital.get('address', 'Unknown')}"
                message += f"\n   Distance: {hospital.get('distance', 'Unknown')} km"
        else:
            message += "\nNo nearby hospitals found"
        
        return message.strip()
    
    def send_emergency_alert(self, user_data, location_data, alert_type="medical", message=None):
        """Send complete emergency alert to all relevant parties"""
        try:
            # Prepare emergency data
            emergency_data = {
                'alert_type': alert_type,
                'user_name': user_data.get('name'),
                'user_phone': user_data.get('phone'),
                'user_email': user_data.get('email'),
                'medical_info': user_data.get('medical_info'),
                'latitude': location_data['latitude'],
                'longitude': location_data['longitude'],
                'address': location_data.get('address'),
                'nearest_hospitals': location_data.get('nearest_hospitals', []),
                'timestamp': location_data.get('timestamp'),
                'message': message
            }
            
            # Send to emergency services
            emergency_sent = self.notify_emergency_services(emergency_data)
            
            # Send to emergency contacts
            contacts_notified = self._notify_emergency_contacts(user_data, emergency_data)
            
            # Send confirmation to user (if conscious and able to receive)
            user_notified = self._notify_user(user_data, emergency_data)
            
            return {
                'emergency_services': emergency_sent,
                'emergency_contacts': contacts_notified,
                'user_notified': user_notified,
                'alert_id': emergency_data.get('alert_id')
            }
            
        except Exception as e:
            logger.error(f"Error sending emergency alert: {e}")
            return False
    
    def _notify_emergency_contacts(self, user_data, emergency_data):
        """Notify user's emergency contacts"""
        try:
            notified_contacts = []
            
            # Get emergency contacts from user data
            contacts = [
                user_data.get('emergency_contact_1'),
                user_data.get('emergency_contact_2')
            ]
            
            for contact in contacts:
                if contact:
                    # Assume contact is in format "Name: Phone" or just phone
                    if ':' in contact:
                        contact_name, contact_phone = contact.split(':', 1)
                        contact_name = contact_name.strip()
                        contact_phone = contact_phone.strip()
                    else:
                        contact_name = "Emergency Contact"
                        contact_phone = contact.strip()
                    
                    # Send SMS to contact
                    contact_message = f"""
Emergency Alert for {user_data.get('name', 'Unknown')}

Location: {emergency_data.get('address', 'Unknown location')}
Coordinates: {emergency_data['latitude']}, {emergency_data['longitude']}
Google Maps: https://www.google.com/maps?q={emergency_data['latitude']},{emergency_data['longitude']}

Time: {emergency_data.get('timestamp', 'Unknown')}
Alert Type: {emergency_data.get('alert_type', 'General')}

Emergency services have been notified.
                    """
                    
                    if self.send_sms(contact_phone, contact_message, emergency=True):
                        notified_contacts.append(contact_phone)
                        logger.info(f"Emergency contact {contact_name} ({contact_phone}) notified")
            
            return notified_contacts
            
        except Exception as e:
            logger.error(f"Error notifying emergency contacts: {e}")
            return []
    
    def _notify_user(self, user_data, emergency_data):
        """Send confirmation to user that help is on the way"""
        try:
            user_phone = user_data.get('phone')
            user_email = user_data.get('email')
            
            confirmation_message = f"""
Help is on the way! 

Emergency services have been notified of your location:
{emergency_data.get('address', 'Unknown location')}

Your emergency contacts have been informed.

Stay calm and wait for assistance.
            """
            
            notifications_sent = []
            
            if user_phone:
                if self.send_sms(user_phone, confirmation_message):
                    notifications_sent.append('sms')
            
            if user_email:
                if self.send_email(
                    user_email, 
                    "Emergency Alert Confirmation", 
                    confirmation_message,
                    emergency=True
                ):
                    notifications_sent.append('email')
            
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Error notifying user: {e}")
            return []
    
    def send_test_notification(self, phone=None, email=None):
        """Send test notification to verify service is working"""
        try:
            test_message = "This is a test message from the Emergency Alert System. The system is working correctly."
            
            results = {}
            
            if phone:
                results['sms'] = self.send_sms(phone, test_message)
            
            if email:
                results['email'] = self.send_email(email, "Test Notification", test_message)
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            return False