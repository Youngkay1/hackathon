import requests
from flask import current_app
import logging

class SMSService:
    def __init__(self):
        self.api_key = current_app.config.get('SMS_API_KEY') if current_app else None
        self.gateway_url = current_app.config.get('SMS_GATEWAY_URL') if current_app else None
    
    def send_sms(self, phone_number, message):
        """Send SMS message to phone number"""
        try:
            # In production, this would integrate with SMS gateway like Twilio, Nexmo, etc.
            # For development, we'll just log the message
            
            if not self.gateway_url or not self.api_key:
                logging.info(f"SMS to {phone_number}: {message}")
                return True
            
            payload = {
                'to': phone_number,
                'message': message,
                'api_key': self.api_key
            }
            
            response = requests.post(self.gateway_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logging.info(f"SMS sent successfully to {phone_number}")
                return True
            else:
                logging.error(f"Failed to send SMS to {phone_number}: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"SMS sending error: {str(e)}")
            return False
    
    def send_confirmation_sms(self, user, resource, request):
        """Send confirmation SMS to user"""
        message = f"🚨 EMERGENCY RESPONSE CONFIRMED\n\n"
        message += f"Service: {resource.name}\n"
        message += f"Location: {resource.location}\n"
        message += f"Contact: {resource.contact_phone}\n"
        message += f"Request ID: {request.id}\n\n"
        message += "Please proceed to the location. Show this SMS if needed."
        
        return self.send_sms(user.phone_number, message)
    
    def send_provider_alert(self, resource, request):
        """Send alert to resource provider"""
        if not resource.contact_phone:
            return False
        
        message = f"🚨 NEW EMERGENCY REQUEST\n\n"
        message += f"Service: {resource.name}\n"
        message += f"Requester: {request.user.phone_number}\n"
        message += f"Location: {request.location}\n"
        message += f"Type: {request.resource_type.value}\n"
        message += f"Request ID: {request.id}\n\n"
        message += "Please prepare to assist."
        
        return self.send_sms(resource.contact_phone, message)
    
    def send_status_update(self, user, request, status_message):
        """Send status update to user"""
        message = f"🚨 REQUEST UPDATE\n\n"
        message += f"Request ID: {request.id}\n"
        message += f"Status: {status_message}\n\n"
        message += "For assistance, call emergency services."
        
        return self.send_sms(user.phone_number, message)
    
    def send_bulk_alert(self, phone_numbers, message):
        """Send bulk SMS alert"""
        success_count = 0
        for phone_number in phone_numbers:
            if self.send_sms(phone_number, message):
                success_count += 1
        
        return success_count
    
    def send_resource_alert(self, resource_type, location, message):
        """Send alert to all resource providers of a specific type in a location"""
        from app.models import Resource
        
        resources = Resource.query.filter(
            Resource.resource_type == resource_type,
            Resource.is_active == True,
            Resource.location.ilike(f'%{location}%'),
            Resource.contact_phone.isnot(None)
        ).all()
        
        phone_numbers = [r.contact_phone for r in resources if r.contact_phone]
        
        return self.send_bulk_alert(phone_numbers, message)