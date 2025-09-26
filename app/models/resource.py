from app import db
from datetime import datetime
from enum import Enum

class ResourceType(Enum):
    SHELTER = 'shelter'
    FOOD = 'food'
    TRANSPORT = 'transport'

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.Enum(ResourceType), nullable=False)
    
    # Location information
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Capacity and availability
    total_capacity = db.Column(db.Integer, default=0)
    available_capacity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Contact information
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    organization = db.Column(db.String(200))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emergency_requests = db.relationship('EmergencyRequest', backref='resource', lazy=True)
    
    def __repr__(self):
        return f'<Resource {self.name} ({self.resource_type.value})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resource_type': self.resource_type.value,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'total_capacity': self.total_capacity,
            'available_capacity': self.available_capacity,
            'is_active': self.is_active,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'organization': self.organization,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def has_capacity(self):
        return self.is_active and self.available_capacity > 0
    
    def reserve_capacity(self, amount=1):
        if self.available_capacity >= amount:
            self.available_capacity -= amount
            return True
        return False
    
    def release_capacity(self, amount=1):
        if self.available_capacity + amount <= self.total_capacity:
            self.available_capacity += amount
            return True
        return False