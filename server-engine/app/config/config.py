import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    DB_CONNECTION_URL = os.getenv('DB_CONNECTION_URL')
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-mini')
    
    # Security settings
    DEPLOY_MODE = os.getenv('DEPLOY_MODE', 'dev')
    SECRET_HASH = os.getenv('SECRET_HASH')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Request size limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size 