from flask import Blueprint, request, jsonify
from app import db
from app.models import Resource, ResourceType, EmergencyRequest, User
from app.services import MatchingService, SMSService
from datetime import datetime

api_bp = Blueprint('api', __name__)
matching_service = MatchingService()
sms_service = SMSService()

@api_bp.route('/resources', methods=['GET'])
def get_resources():
    """Get all active resources"""
    resource_type = request.args.get('type')
    location = request.args.get('location')
    
    query = Resource.query.filter_by(is_active=True)
    
    if resource_type:
        try:
            query = query.filter_by(resource_type=ResourceType(resource_type))
        except ValueError:
            return jsonify({'error': 'Invalid resource type'}), 400
    
    if location:
        query = query.filter(Resource.location.ilike(f'%{location}%'))
    
    resources = query.all()
    return jsonify([resource.to_dict() for resource in resources])

@api_bp.route('/resources/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get specific resource"""
    resource = Resource.query.get_or_404(resource_id)
    return jsonify(resource.to_dict())

@api_bp.route('/resources', methods=['POST'])
def create_resource():
    """Create new resource"""
    try:
        data = request.get_json()
        
        resource = Resource(
            name=data['name'],
            description=data.get('description'),
            resource_type=ResourceType(data['resource_type']),
            location=data['location'],
            latitude=float(data.get('latitude', 0)),
            longitude=float(data.get('longitude', 0)),
            total_capacity=int(data.get('total_capacity', 0)),
            available_capacity=int(data.get('available_capacity', 0)),
            contact_person=data.get('contact_person'),
            contact_phone=data.get('contact_phone'),
            organization=data.get('organization')
        )
        
        db.session.add(resource)
        db.session.commit()
        
        return jsonify(resource.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/resources/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Update resource"""
    try:
        resource = Resource.query.get_or_404(resource_id)
        data = request.get_json()
        
        resource.name = data.get('name', resource.name)
        resource.description = data.get('description', resource.description)
        if 'resource_type' in data:
            resource.resource_type = ResourceType(data['resource_type'])
        resource.location = data.get('location', resource.location)
        resource.latitude = float(data.get('latitude', resource.latitude))
        resource.longitude = float(data.get('longitude', resource.longitude))
        resource.total_capacity = int(data.get('total_capacity', resource.total_capacity))
        resource.available_capacity = int(data.get('available_capacity', resource.available_capacity))
        resource.contact_person = data.get('contact_person', resource.contact_person)
        resource.contact_phone = data.get('contact_phone', resource.contact_phone)
        resource.organization = data.get('organization', resource.organization)
        resource.is_active = data.get('is_active', resource.is_active)
        resource.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(resource.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/requests', methods=['GET'])
def get_requests():
    """Get emergency requests"""
    status = request.args.get('status')
    user_phone = request.args.get('user_phone')
    
    query = EmergencyRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    if user_phone:
        user = User.query.filter_by(phone_number=user_phone).first()
        if user:
            query = query.filter_by(user_id=user.id)
        else:
            return jsonify([])
    
    requests = query.order_by(EmergencyRequest.created_at.desc()).limit(100).all()
    return jsonify([req.to_dict() for req in requests])

@api_bp.route('/requests/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """Get specific request"""
    req = EmergencyRequest.query.get_or_404(request_id)
    return jsonify(req.to_dict())

@api_bp.route('/requests/<int:request_id>/status', methods=['PUT'])
def update_request_status(request_id):
    """Update request status"""
    try:
        req = EmergencyRequest.query.get_or_404(request_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        req.update_status(new_status)
        db.session.commit()
        
        # Send SMS notification
        status_message = f"Your request has been updated to: {new_status}"
        sms_service.send_status_update(req.user, req, status_message)
        
        return jsonify(req.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/search', methods=['POST'])
def search_resources():
    """Search for resources based on criteria"""
    try:
        data = request.get_json()
        
        resource_type = ResourceType(data['resource_type'])
        location = data['location']
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        limit = data.get('limit', 5)
        
        resources = matching_service.find_nearby_resources(
            resource_type=resource_type,
            location=location,
            latitude=latitude,
            longitude=longitude,
            limit=limit
        )
        
        return jsonify([resource.to_dict() for resource in resources])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_bp.route('/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    return jsonify({
        'shelter': matching_service.get_resource_statistics(ResourceType.SHELTER),
        'food': matching_service.get_resource_statistics(ResourceType.FOOD),
        'transport': matching_service.get_resource_statistics(ResourceType.TRANSPORT),
        'overall': matching_service.get_resource_statistics()
    })

@api_bp.route('/alert', methods=['POST'])
def send_alert():
    """Send emergency alert to resource providers"""
    try:
        data = request.get_json()
        
        resource_type = ResourceType(data['resource_type'])
        location = data['location']
        message = data['message']
        
        sent_count = sms_service.send_resource_alert(resource_type, location, message)
        
        return jsonify({
            'success': True,
            'sent_count': sent_count,
            'message': f'Alert sent to {sent_count} providers'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400