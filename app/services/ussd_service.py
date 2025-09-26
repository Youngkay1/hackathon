from app import db
from app.models import User, USSDSession, EmergencyRequest, Resource, ResourceType
from app.services.matching_service import MatchingService
from app.services.sms_service import SMSService
from datetime import datetime
import uuid
import json

class USSDService:
    def __init__(self):
        self.matching_service = MatchingService()
        self.sms_service = SMSService()
    
    def process_ussd_request(self, phone_number, session_id, user_input):
        """Process incoming USSD request and return response"""
        
        # Get or create user
        user = self.get_or_create_user(phone_number)
        
        # Get or create session
        session = self.get_or_create_session(session_id, user.id)
        
        # Process user input and generate response
        response = self.handle_menu_navigation(session, user_input)
        
        # Update session
        session.extend_session()
        db.session.commit()
        
        return response
    
    def get_or_create_user(self, phone_number):
        """Get existing user or create new one"""
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.session.add(user)
            db.session.flush()
        else:
            user.last_active = datetime.utcnow()
        return user
    
    def get_or_create_session(self, session_id, user_id):
        """Get existing session or create new one"""
        session = USSDSession.query.filter_by(session_id=session_id).first()
        if not session or session.is_expired():
            if session:
                session.end_session()
            session = USSDSession(
                session_id=session_id,
                user_id=user_id
            )
            db.session.add(session)
            db.session.flush()
        return session
    
    def handle_menu_navigation(self, session, user_input):
        """Handle menu navigation based on current menu and user input"""
        
        current_menu = session.current_menu
        
        if current_menu == 'main':
            return self.handle_main_menu(session, user_input)
        elif current_menu == 'shelter':
            return self.handle_shelter_menu(session, user_input)
        elif current_menu == 'food':
            return self.handle_food_menu(session, user_input)
        elif current_menu == 'transport':
            return self.handle_transport_menu(session, user_input)
        elif current_menu == 'location':
            return self.handle_location_input(session, user_input)
        elif current_menu == 'confirm':
            return self.handle_confirmation(session, user_input)
        else:
            return self.show_main_menu(session)
    
    def handle_main_menu(self, session, user_input):
        """Handle main menu selection"""
        if user_input == '':
            return self.show_main_menu(session)
        
        if user_input == '1':
            session.current_menu = 'shelter'
            session.add_to_menu_history('main')
            session.add_to_input_history(user_input)
            return self.show_shelter_menu(session)
        elif user_input == '2':
            session.current_menu = 'food'
            session.add_to_menu_history('main')
            session.add_to_input_history(user_input)
            return self.show_food_menu(session)
        elif user_input == '3':
            session.current_menu = 'transport'
            session.add_to_menu_history('main')
            session.add_to_input_history(user_input)
            return self.show_transport_menu(session)
        else:
            return self.show_main_menu(session, error="Invalid option. Please try again.")
    
    def handle_shelter_menu(self, session, user_input):
        """Handle shelter submenu"""
        if user_input == '1':
            return self.request_location(session, ResourceType.SHELTER, 'emergency_shelter')
        elif user_input == '2':
            return self.request_location(session, ResourceType.SHELTER, 'temporary_housing')
        elif user_input == '3':
            return self.request_location(session, ResourceType.SHELTER, 'evacuation_center')
        elif user_input == '0':
            return self.go_back(session)
        else:
            return self.show_shelter_menu(session, error="Invalid option. Please try again.")
    
    def handle_food_menu(self, session, user_input):
        """Handle food submenu"""
        if user_input == '1':
            return self.request_location(session, ResourceType.FOOD, 'emergency_food')
        elif user_input == '2':
            return self.request_location(session, ResourceType.FOOD, 'cooking_facilities')
        elif user_input == '3':
            return self.request_location(session, ResourceType.FOOD, 'water_sanitation')
        elif user_input == '0':
            return self.go_back(session)
        else:
            return self.show_food_menu(session, error="Invalid option. Please try again.")
    
    def handle_transport_menu(self, session, user_input):
        """Handle transport submenu"""
        if user_input == '1':
            return self.request_location(session, ResourceType.TRANSPORT, 'evacuation_transport')
        elif user_input == '2':
            return self.request_location(session, ResourceType.TRANSPORT, 'medical_transport')
        elif user_input == '3':
            return self.request_location(session, ResourceType.TRANSPORT, 'general_transport')
        elif user_input == '0':
            return self.go_back(session)
        else:
            return self.show_transport_menu(session, error="Invalid option. Please try again.")
    
    def request_location(self, session, resource_type, subtype):
        """Request user location for resource matching"""
        session.current_menu = 'location'
        session.update_session_data('resource_type', resource_type.value)
        session.update_session_data('subtype', subtype)
        
        return {
            'message': "Please enter your current location or nearest landmark:",
            'continue_session': True
        }
    
    def handle_location_input(self, session, user_input):
        """Handle location input and find matching resources"""
        if user_input.strip() == '':
            return {
                'message': "Location cannot be empty. Please enter your current location:",
                'continue_session': True
            }
        
        session.update_session_data('location', user_input)
        
        # Find matching resources
        resource_type = ResourceType(session.get_session_data().get('resource_type'))
        matches = self.matching_service.find_nearby_resources(
            resource_type=resource_type,
            location=user_input,
            limit=3
        )
        
        if matches:
            session.current_menu = 'confirm'
            session.update_session_data('matches', [r.to_dict() for r in matches])
            return self.show_matches(session, matches)
        else:
            return {
                'message': f"Sorry, no {resource_type.value} resources are currently available in your area. We have recorded your request and will notify you when resources become available.",
                'continue_session': False
            }
    
    def show_matches(self, session, matches):
        """Show available resource matches"""
        message = "Available resources near you:\n\n"
        
        for i, resource in enumerate(matches, 1):
            message += f"{i}. {resource.name}\n"
            message += f"   Location: {resource.location}\n"
            message += f"   Contact: {resource.contact_phone}\n"
            if resource.available_capacity > 0:
                message += f"   Available: {resource.available_capacity} spaces\n"
            message += "\n"
        
        message += "Select a resource (1-3) or 0 to go back:"
        
        return {
            'message': message,
            'continue_session': True
        }
    
    def handle_confirmation(self, session, user_input):
        """Handle resource selection confirmation"""
        if user_input == '0':
            return self.go_back(session)
        
        try:
            selection = int(user_input) - 1
            matches = session.get_session_data().get('matches', [])
            
            if 0 <= selection < len(matches):
                selected_resource = matches[selection]
                return self.create_emergency_request(session, selected_resource)
            else:
                return {
                    'message': "Invalid selection. Please choose 1-3 or 0 to go back:",
                    'continue_session': True
                }
        except ValueError:
            return {
                'message': "Invalid input. Please enter a number (1-3) or 0 to go back:",
                'continue_session': True
            }
    
    def create_emergency_request(self, session, selected_resource):
        """Create emergency request and send notifications"""
        user = session.user
        resource = Resource.query.get(selected_resource['id'])
        
        if not resource or not resource.has_capacity():
            return {
                'message': "Sorry, this resource is no longer available. Please try another option.",
                'continue_session': False
            }
        
        # Create emergency request
        request = EmergencyRequest(
            user_id=user.id,
            resource_id=resource.id,
            resource_type=ResourceType(selected_resource['resource_type']),
            location=session.get_session_data().get('location'),
            notes=session.get_session_data().get('subtype')
        )
        
        # Reserve capacity
        resource.reserve_capacity(1)
        
        db.session.add(request)
        db.session.commit()
        
        # Send SMS notifications
        self.sms_service.send_confirmation_sms(user, resource, request)
        self.sms_service.send_provider_alert(resource, request)
        
        message = f"✓ Request confirmed!\n\n"
        message += f"Resource: {resource.name}\n"
        message += f"Location: {resource.location}\n"
        message += f"Contact: {resource.contact_phone}\n\n"
        message += f"Request ID: {request.id}\n"
        message += "You will receive an SMS confirmation shortly."
        
        session.end_session()
        
        return {
            'message': message,
            'continue_session': False
        }
    
    def show_main_menu(self, session, error=None):
        """Show main menu"""
        message = "🚨 EMERGENCY RESPONSE SYSTEM 🚨\n\n"
        if error:
            message += f"❌ {error}\n\n"
        
        message += "Select your need:\n"
        message += "1. Shelter\n"
        message += "2. Food\n"
        message += "3. Transport\n"
        
        return {
            'message': message,
            'continue_session': True
        }
    
    def show_shelter_menu(self, session, error=None):
        """Show shelter submenu"""
        message = "🏠 SHELTER OPTIONS\n\n"
        if error:
            message += f"❌ {error}\n\n"
        
        message += "1. Emergency shelter\n"
        message += "2. Temporary housing\n"
        message += "3. Safe evacuation center\n"
        message += "0. Back to main menu\n"
        
        return {
            'message': message,
            'continue_session': True
        }
    
    def show_food_menu(self, session, error=None):
        """Show food submenu"""
        message = "🍽️ FOOD OPTIONS\n\n"
        if error:
            message += f"❌ {error}\n\n"
        
        message += "1. Emergency food supplies\n"
        message += "2. Cooking facilities\n"
        message += "3. Water and sanitation\n"
        message += "0. Back to main menu\n"
        
        return {
            'message': message,
            'continue_session': True
        }
    
    def show_transport_menu(self, session, error=None):
        """Show transport submenu"""
        message = "🚗 TRANSPORT OPTIONS\n\n"
        if error:
            message += f"❌ {error}\n\n"
        
        message += "1. Evacuation transport\n"
        message += "2. Medical transport\n"
        message += "3. General transport\n"
        message += "0. Back to main menu\n"
        
        return {
            'message': message,
            'continue_session': True
        }
    
    def go_back(self, session):
        """Go back to previous menu"""
        history = session.get_menu_history()
        if history:
            session.current_menu = history[-1]
            # Remove last item from history
            history.pop()
            session.menu_history = json.dumps(history) if history else None
            
            if session.current_menu == 'main':
                return self.show_main_menu(session)
            elif session.current_menu == 'shelter':
                return self.show_shelter_menu(session)
            elif session.current_menu == 'food':
                return self.show_food_menu(session)
            elif session.current_menu == 'transport':
                return self.show_transport_menu(session)
        
        return self.show_main_menu(session)