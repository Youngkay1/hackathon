from app import db
from datetime import datetime, timedelta
import json

class USSDSession(db.Model):
    __tablename__ = 'ussd_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session state
    current_menu = db.Column(db.String(50), default='main')
    menu_history = db.Column(db.Text)  # JSON array of menu history
    user_input_history = db.Column(db.Text)  # JSON array of user inputs
    
    # Session data
    session_data = db.Column(db.Text)  # JSON object for storing session variables
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<USSDSession {self.session_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'current_menu': self.current_menu,
            'menu_history': self.get_menu_history(),
            'user_input_history': self.get_input_history(),
            'session_data': self.get_session_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }
    
    def get_menu_history(self):
        if self.menu_history:
            try:
                return json.loads(self.menu_history)
            except json.JSONDecodeError:
                return []
        return []
    
    def add_to_menu_history(self, menu):
        history = self.get_menu_history()
        history.append(menu)
        self.menu_history = json.dumps(history)
    
    def get_input_history(self):
        if self.user_input_history:
            try:
                return json.loads(self.user_input_history)
            except json.JSONDecodeError:
                return []
        return []
    
    def add_to_input_history(self, user_input):
        history = self.get_input_history()
        history.append(user_input)
        self.user_input_history = json.dumps(history)
    
    def get_session_data(self):
        if self.session_data:
            try:
                return json.loads(self.session_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_session_data(self, data):
        self.session_data = json.dumps(data)
    
    def update_session_data(self, key, value):
        data = self.get_session_data()
        data[key] = value
        self.set_session_data(data)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, minutes=10):
        self.expires_at = datetime.utcnow() + timedelta(minutes=minutes)
        self.last_activity = datetime.utcnow()
    
    def end_session(self):
        self.is_active = False