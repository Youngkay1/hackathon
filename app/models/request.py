from app import db
from datetime import datetime
from enum import Enum
from .resource import ResourceType

class RequestStatus(Enum):
    PENDING = 'pending'
    MATCHED = 'matched'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class EmergencyRequest(db.Model):
    __tablename__ = 'emergency_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    
    # Request details
    resource_type = db.Column(db.Enum(ResourceType), nullable=False)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.PENDING)
    priority = db.Column(db.Integer, default=1)  # 1=low, 5=critical
    
    # Location information
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Additional details
    notes = db.Column(db.Text)
    people_count = db.Column(db.Integer, default=1)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    matched_at = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<EmergencyRequest {self.id} - {self.resource_type.value} ({self.status.value})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type.value,
            'status': self.status.value,
            'priority': self.priority,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'notes': self.notes,
            'people_count': self.people_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'matched_at': self.matched_at.isoformat() if self.matched_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def update_status(self, new_status):
        self.status = new_status
        now = datetime.utcnow()
        
        if new_status == RequestStatus.MATCHED:
            self.matched_at = now
        elif new_status == RequestStatus.CONFIRMED:
            self.confirmed_at = now
        elif new_status == RequestStatus.COMPLETED:
            self.completed_at = now