from flask import Blueprint, request, jsonify
from app.services import USSDService
import logging

ussd_bp = Blueprint('ussd', __name__)
ussd_service = USSDService()

@ussd_bp.route('/callback', methods=['POST'])
def ussd_callback():
    """Handle USSD callback from telecom provider"""
    try:
        # Get USSD parameters from request
        # Different telecom providers may use different parameter names
        data = request.get_json() or request.form.to_dict()
        
        phone_number = data.get('phoneNumber') or data.get('msisdn') or data.get('from')
        session_id = data.get('sessionId') or data.get('session_id')
        user_input = data.get('text') or data.get('input') or ''
        
        if not phone_number or not session_id:
            return jsonify({
                'error': 'Missing required parameters: phoneNumber and sessionId'
            }), 400
        
        # Process USSD request
        response = ussd_service.process_ussd_request(phone_number, session_id, user_input)
        
        # Format response for telecom provider
        # Different providers may expect different response formats
        ussd_response = {
            'message': response['message'],
            'continueSession': response['continue_session']
        }
        
        # Alternative response format for some providers
        if not response['continue_session']:
            ussd_response['action'] = 'end'
        else:
            ussd_response['action'] = 'input'
        
        return jsonify(ussd_response)
        
    except Exception as e:
        logging.error(f"USSD callback error: {str(e)}")
        return jsonify({
            'message': 'System temporarily unavailable. Please try again later.',
            'continueSession': False,
            'action': 'end'
        })

@ussd_bp.route('/test', methods=['POST'])
def test_ussd():
    """Test endpoint for USSD simulation"""
    try:
        data = request.get_json()
        
        phone_number = data.get('phone_number', '+2348000000000')
        session_id = data.get('session_id', 'test_session_123')
        user_input = data.get('input', '')
        
        response = ussd_service.process_ussd_request(phone_number, session_id, user_input)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logging.error(f"USSD test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ussd_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'USSD Gateway'
    })