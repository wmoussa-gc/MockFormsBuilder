from flask import Blueprint, request, jsonify
from models import User, Form, data_store
from auth import require_api_key, get_current_user
import logging

api_bp = Blueprint('api', __name__)

# User endpoints
@api_bp.route('/signup', methods=['POST'])
def signup():
    """User sign-up endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request must contain JSON data'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Email and password are required'
            }), 400
        
        # Validate email format (basic)
        if '@' not in email or '.' not in email:
            return jsonify({
                'error': 'Invalid email format',
                'message': 'Please provide a valid email address'
            }), 400
        
        # Create user
        user_data = User.create_user(email, password)
        
        logging.info(f"New user created: {email}")
        
        return jsonify({
            'message': 'User created successfully',
            'user': user_data
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': 'User creation failed',
            'message': str(e)
        }), 409
        
    except Exception as e:
        logging.error(f"Signup error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

# Form endpoints
@api_bp.route('/forms', methods=['POST'])
@require_api_key
def create_form():
    """Create a new form"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request must contain JSON data'
            }), 400
        
        current_user = get_current_user()
        form = Form.create_form(current_user['email'], data)
        
        logging.info(f"New form created: {form['id']} by {current_user['email']}")
        
        return jsonify({
            'message': 'Form created successfully',
            'form': form
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': 'Form creation failed',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logging.error(f"Form creation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@api_bp.route('/forms/<form_id>', methods=['GET'])
def get_form(form_id):
    """Get form structure (public endpoint for displaying forms)"""
    try:
        form = Form.get_form(form_id)
        
        if not form:
            return jsonify({
                'error': 'Form not found',
                'message': f'No form found with ID: {form_id}'
            }), 404
        
        # Return form structure without sensitive owner information
        public_form = {
            'id': form['id'],
            'title': form['title'],
            'description': form['description'],
            'fields': form['fields'],
            'created_at': form['created_at']
        }
        
        return jsonify({
            'form': public_form
        }), 200
        
    except Exception as e:
        logging.error(f"Get form error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@api_bp.route('/forms', methods=['GET'])
@require_api_key
def get_user_forms():
    """Get all forms owned by the authenticated user"""
    try:
        current_user = get_current_user()
        forms = Form.get_user_forms(current_user['email'])
        
        return jsonify({
            'forms': forms,
            'count': len(forms)
        }), 200
        
    except Exception as e:
        logging.error(f"Get user forms error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@api_bp.route('/forms/<form_id>/responses', methods=['POST'])
def submit_response(form_id):
    """Submit a response to a form (public endpoint)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request must contain JSON data'
            }), 400
        
        # Check if form exists
        form = Form.get_form(form_id)
        if not form:
            return jsonify({
                'error': 'Form not found',
                'message': f'No form found with ID: {form_id}'
            }), 404
        
        # Validate response data against form fields
        response_data = data.get('responses', {})
        
        if not isinstance(response_data, dict):
            return jsonify({
                'error': 'Invalid response format',
                'message': 'Responses must be provided as a dictionary'
            }), 400
        
        # Basic validation - check if required fields are present
        form_fields = {field['name']: field for field in form['fields']}
        for field_name, field_config in form_fields.items():
            if field_config.get('required', False) and field_name not in response_data:
                return jsonify({
                    'error': 'Missing required field',
                    'message': f'Field "{field_name}" is required'
                }), 400
        
        # Add response
        success = Form.add_response(form_id, response_data)
        
        if success:
            logging.info(f"New response submitted to form: {form_id}")
            return jsonify({
                'message': 'Response submitted successfully',
                'form_id': form_id
            }), 201
        else:
            return jsonify({
                'error': 'Failed to submit response',
                'message': 'Could not save response'
            }), 500
            
    except Exception as e:
        logging.error(f"Submit response error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@api_bp.route('/forms/<form_id>/responses', methods=['GET'])
@require_api_key
def get_responses(form_id):
    """Get all responses for a form (owner only)"""
    try:
        current_user = get_current_user()
        
        # Check if form exists and user owns it
        form = Form.get_form(form_id)
        if not form:
            return jsonify({
                'error': 'Form not found',
                'message': f'No form found with ID: {form_id}'
            }), 404
        
        if form['owner_email'] != current_user['email']:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only view responses for your own forms'
            }), 403
        
        responses = Form.get_responses(form_id)
        
        return jsonify({
            'form_id': form_id,
            'form_title': form['title'],
            'responses': responses,
            'count': len(responses)
        }), 200
        
    except Exception as e:
        logging.error(f"Get responses error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

# Debug/Admin endpoints
@api_bp.route('/debug/stats', methods=['GET'])
def debug_stats():
    """Get system statistics (for debugging)"""
    try:
        stats = {
            'users_count': len(data_store.users),
            'forms_count': len(data_store.forms),
            'total_responses': sum(len(responses) for responses in data_store.responses.values()),
            'api_keys_count': len(data_store.api_keys)
        }
        
        return jsonify({
            'stats': stats,
            'message': 'System statistics'
        }), 200
        
    except Exception as e:
        logging.error(f"Debug stats error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@api_bp.route('/debug/clear', methods=['POST'])
def debug_clear():
    """Clear all data (for debugging/testing)"""
    try:
        data_store.clear_all()
        logging.info("All data cleared")
        
        return jsonify({
            'message': 'All data cleared successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Debug clear error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
