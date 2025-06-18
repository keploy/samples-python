import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Base configuration"""
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    
    # MongoDB configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'studentsdb')
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv('RATE_LIMIT', '200 per day')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 
                         '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGO_DB_NAME = 'test_studentsdb'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Dictionary to map config names to classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Retrieve environment configuration"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])
