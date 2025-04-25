import logging
import json
from datetime import datetime
from functools import wraps
import uuid
from flask import request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_request_id():
    """Generate a unique request ID."""
    return str(uuid.uuid4())

def log_request(f):
    """Decorator to log request details."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_id = generate_request_id()
        request_data = {
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
        
        logger.info(f"Request started: {json.dumps(request_data)}")
        
        try:
            response = f(*args, **kwargs)
            response_data = {
                'request_id': request_id,
                'status_code': response.status_code if hasattr(response, 'status_code') else 200,
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.info(f"Request completed: {json.dumps(response_data)}")
            return response
        except Exception as e:
            error_data = {
                'request_id': request_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.error(f"Request failed: {json.dumps(error_data)}")
            raise
    
    return decorated_function

def log_error(error, context=None):
    """Log an error with context."""
    error_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'error': str(error),
        'context': context or {}
    }
    logger.error(f"Error occurred: {json.dumps(error_data)}")

def log_info(message, data=None):
    """Log an info message with optional data."""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'message': message,
        'data': data or {}
    }
    logger.info(f"Info: {json.dumps(log_data)}") 