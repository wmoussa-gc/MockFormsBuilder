from functools import wraps
from flask import request, jsonify
from models import User

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            # Also check for API key in query parameters as fallback
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Provide API key in X-API-Key header or api_key query parameter'
            }), 401
        
        # Validate API key
        user = User.get_user_by_api_key(api_key)
        if not user:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 401
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """Get the current authenticated user"""
    return getattr(request, 'current_user', None)
