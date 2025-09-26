import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///emergency_response.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USSD_GATEWAY_URL = os.environ.get('USSD_GATEWAY_URL')
    SMS_GATEWAY_URL = os.environ.get('SMS_GATEWAY_URL')
    SMS_API_KEY = os.environ.get('SMS_API_KEY')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}