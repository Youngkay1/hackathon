from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    emergency_requests = db.relationship('EmergencyRequest', backref='user', lazy=True)
    ussd_sessions = db.relationship('USSDSession', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.phone_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'name': self.name,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }