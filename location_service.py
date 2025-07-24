import geocoder
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="emergency_alert_system")
        self.google_api_key = Config.GOOGLE_MAPS_API_KEY
    
    def get_current_location_ip(self):
        """Get current location based on IP address (fallback method)"""
        try:
            g = geocoder.ip('me')
            if g.ok:
                return {
                    'latitude': g.latlng[0],
                    'longitude': g.latlng[1],
                    'address': g.address,
                    'method': 'ip'
                }
        except Exception as e:
            logger.error(f"Error getting IP location: {e}")
        return None
    
    def get_location_from_coordinates(self, latitude, longitude):
        """Get address from latitude and longitude"""
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            if location:
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': location.address,
                    'method': 'coordinates'
                }
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")
        return None
    
    def get_location_from_address(self, address):
        """Get coordinates from address"""
        try:
            location = self.geolocator.geocode(address)
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address,
                    'method': 'address'
                }
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
        return None
    
    def calculate_distance(self, coord1, coord2):
        """Calculate distance between two coordinates in kilometers"""
        try:
            return geodesic(coord1, coord2).kilometers
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return None
    
    def find_nearest_hospitals(self, latitude, longitude, radius=10):
        """Find nearest hospitals using Google Places API"""
        if not self.google_api_key:
            logger.warning("Google Maps API key not configured")
            return []
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius * 1000,  # Convert km to meters
                'type': 'hospital',
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                hospitals = []
                
                for place in data.get('results', []):
                    hospital = {
                        'name': place.get('name'),
                        'address': place.get('vicinity'),
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'rating': place.get('rating'),
                        'place_id': place.get('place_id')
                    }
                    
                    # Calculate distance
                    hospital['distance'] = self.calculate_distance(
                        (latitude, longitude),
                        (hospital['latitude'], hospital['longitude'])
                    )
                    
                    hospitals.append(hospital)
                
                # Sort by distance
                hospitals.sort(key=lambda x: x.get('distance', float('inf')))
                return hospitals[:5]  # Return top 5 nearest
                
        except Exception as e:
            logger.error(f"Error finding hospitals: {e}")
        
        return []
    
    def get_emergency_services_nearby(self, latitude, longitude, service_type='hospital'):
        """Get emergency services nearby based on type"""
        service_types = {
            'hospital': 'hospital',
            'police': 'police',
            'fire_station': 'fire_station'
        }
        
        if service_type not in service_types:
            service_type = 'hospital'
        
        if not self.google_api_key:
            return self._get_mock_emergency_services(latitude, longitude, service_type)
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{latitude},{longitude}",
                'radius': 10000,  # 10km radius
                'type': service_types[service_type],
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                services = []
                
                for place in data.get('results', []):
                    service = {
                        'name': place.get('name'),
                        'address': place.get('vicinity'),
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'type': service_type,
                        'rating': place.get('rating'),
                        'place_id': place.get('place_id')
                    }
                    
                    # Calculate distance
                    service['distance'] = self.calculate_distance(
                        (latitude, longitude),
                        (service['latitude'], service['longitude'])
                    )
                    
                    services.append(service)
                
                # Sort by distance
                services.sort(key=lambda x: x.get('distance', float('inf')))
                return services[:3]  # Return top 3 nearest
                
        except Exception as e:
            logger.error(f"Error finding emergency services: {e}")
        
        return self._get_mock_emergency_services(latitude, longitude, service_type)
    
    def _get_mock_emergency_services(self, latitude, longitude, service_type):
        """Mock emergency services data for testing"""
        mock_services = {
            'hospital': [
                {
                    'name': 'City General Hospital',
                    'address': 'Main Street',
                    'latitude': latitude + 0.01,
                    'longitude': longitude + 0.01,
                    'type': 'hospital',
                    'distance': 1.2,
                    'phone': '911'
                },
                {
                    'name': 'Emergency Medical Center',
                    'address': 'Oak Avenue',
                    'latitude': latitude - 0.01,
                    'longitude': longitude - 0.01,
                    'type': 'hospital',
                    'distance': 1.5,
                    'phone': '911'
                }
            ],
            'police': [
                {
                    'name': 'City Police Station',
                    'address': 'Police Plaza',
                    'latitude': latitude + 0.005,
                    'longitude': longitude + 0.005,
                    'type': 'police',
                    'distance': 0.8,
                    'phone': '911'
                }
            ],
            'fire_station': [
                {
                    'name': 'Fire Department Station 1',
                    'address': 'Fire Station Road',
                    'latitude': latitude - 0.005,
                    'longitude': longitude + 0.005,
                    'type': 'fire_station',
                    'distance': 0.9,
                    'phone': '911'
                }
            ]
        }
        
        return mock_services.get(service_type, [])
    
    def is_in_high_risk_zone(self, latitude, longitude):
        """Check if location is in a predefined high-risk zone"""
        for zone in Config.HIGH_RISK_ZONES:
            distance = self.calculate_distance(
                (latitude, longitude),
                (zone['lat'], zone['lng'])
            )
            if distance and distance <= (zone['radius'] / 1000):  # Convert meters to km
                return True
        return False
    
    def format_location_for_emergency(self, latitude, longitude, address=None):
        """Format location information for emergency services"""
        if not address:
            location_data = self.get_location_from_coordinates(latitude, longitude)
            address = location_data.get('address', 'Address not available') if location_data else 'Address not available'
        
        # Find nearest emergency services
        hospitals = self.get_emergency_services_nearby(latitude, longitude, 'hospital')
        
        emergency_info = {
            'coordinates': f"{latitude}, {longitude}",
            'address': address,
            'google_maps_link': f"https://www.google.com/maps?q={latitude},{longitude}",
            'nearest_hospitals': hospitals,
            'high_risk_zone': self.is_in_high_risk_zone(latitude, longitude)
        }
        
        return emergency_info