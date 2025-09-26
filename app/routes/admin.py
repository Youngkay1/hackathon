from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models import Resource, ResourceType, EmergencyRequest, User
from app.services import MatchingService
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
matching_service = MatchingService()

@admin_bp.route('/')
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_resources = Resource.query.filter_by(is_active=True).count()
    total_requests = EmergencyRequest.query.count()
    pending_requests = EmergencyRequest.query.filter_by(status='pending').count()
    
    # Get recent requests
    recent_requests = EmergencyRequest.query.order_by(
        EmergencyRequest.created_at.desc()
    ).limit(10).all()
    
    # Get resource statistics by type
    shelter_stats = matching_service.get_resource_statistics(ResourceType.SHELTER)
    food_stats = matching_service.get_resource_statistics(ResourceType.FOOD)
    transport_stats = matching_service.get_resource_statistics(ResourceType.TRANSPORT)
    
    return render_template('admin/dashboard.html',
                         total_resources=total_resources,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         recent_requests=recent_requests,
                         shelter_stats=shelter_stats,
                         food_stats=food_stats,
                         transport_stats=transport_stats)

@admin_bp.route('/resources')
def resources():
    """Manage resources"""
    page = request.args.get('page', 1, type=int)
    resource_type = request.args.get('type')
    
    query = Resource.query
    if resource_type:
        query = query.filter_by(resource_type=ResourceType(resource_type))
    
    resources = query.order_by(Resource.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/resources.html', resources=resources)

@admin_bp.route('/resources/add', methods=['GET', 'POST'])
def add_resource():
    """Add new resource"""
    if request.method == 'POST':
        try:
            resource = Resource(
                name=request.form['name'],
                description=request.form.get('description'),
                resource_type=ResourceType(request.form['resource_type']),
                location=request.form['location'],
                latitude=float(request.form.get('latitude', 0)),
                longitude=float(request.form.get('longitude', 0)),
                total_capacity=int(request.form.get('total_capacity', 0)),
                available_capacity=int(request.form.get('available_capacity', 0)),
                contact_person=request.form.get('contact_person'),
                contact_phone=request.form.get('contact_phone'),
                organization=request.form.get('organization')
            )
            
            db.session.add(resource)
            db.session.commit()
            
            return redirect(url_for('admin.resources'))
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return render_template('admin/add_resource.html')

@admin_bp.route('/resources/<int:resource_id>/edit', methods=['GET', 'POST'])
def edit_resource(resource_id):
    """Edit resource"""
    resource = Resource.query.get_or_404(resource_id)
    
    if request.method == 'POST':
        try:
            resource.name = request.form['name']
            resource.description = request.form.get('description')
            resource.resource_type = ResourceType(request.form['resource_type'])
            resource.location = request.form['location']
            resource.latitude = float(request.form.get('latitude', 0))
            resource.longitude = float(request.form.get('longitude', 0))
            resource.total_capacity = int(request.form.get('total_capacity', 0))
            resource.available_capacity = int(request.form.get('available_capacity', 0))
            resource.contact_person = request.form.get('contact_person')
            resource.contact_phone = request.form.get('contact_phone')
            resource.organization = request.form.get('organization')
            resource.is_active = 'is_active' in request.form
            resource.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return redirect(url_for('admin.resources'))
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return render_template('admin/edit_resource.html', resource=resource)

@admin_bp.route('/requests')
def requests():
    """View emergency requests"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = EmergencyRequest.query
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(EmergencyRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/requests.html', requests=requests)

@admin_bp.route('/api/resources', methods=['GET'])
def api_resources():
    """API endpoint for resources"""
    resources = Resource.query.filter_by(is_active=True).all()
    return jsonify([resource.to_dict() for resource in resources])

@admin_bp.route('/api/requests', methods=['GET'])
def api_requests():
    """API endpoint for requests"""
    requests = EmergencyRequest.query.order_by(
        EmergencyRequest.created_at.desc()
    ).limit(50).all()
    return jsonify([req.to_dict() for req in requests])

@admin_bp.route('/api/stats', methods=['GET'])
def api_stats():
    """API endpoint for statistics"""
    return jsonify({
        'shelter': matching_service.get_resource_statistics(ResourceType.SHELTER),
        'food': matching_service.get_resource_statistics(ResourceType.FOOD),
        'transport': matching_service.get_resource_statistics(ResourceType.TRANSPORT),
        'overall': matching_service.get_resource_statistics()
    })