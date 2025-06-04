import uuid
import datetime
from typing import Dict, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

class DataStore:
    """In-memory data storage using dictionaries"""
    def __init__(self):
        self.users: Dict[str, dict] = {}  # email -> user data
        self.api_keys: Dict[str, str] = {}  # api_key -> email
        self.forms: Dict[str, dict] = {}  # form_id -> form data
        self.responses: Dict[str, List[dict]] = {}  # form_id -> list of responses
        
    def clear_all(self):
        """Clear all data - useful for testing"""
        self.users.clear()
        self.api_keys.clear()
        self.forms.clear()
        self.responses.clear()

# Global data store instance
data_store = DataStore()

class User:
    """User model for managing user data"""
    
    @staticmethod
    def create_user(email: str, password: str) -> dict:
        """Create a new user and return user data with API key"""
        if email in data_store.users:
            raise ValueError("User already exists")
        
        # Generate API key
        api_key = str(uuid.uuid4())
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Store user data
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'api_key': api_key,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        data_store.users[email] = user_data
        data_store.api_keys[api_key] = email
        
        return {
            'email': email,
            'api_key': api_key,
            'created_at': user_data['created_at']
        }
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[dict]:
        """Get user by email"""
        return data_store.users.get(email)
    
    @staticmethod
    def get_user_by_api_key(api_key: str) -> Optional[dict]:
        """Get user by API key"""
        email = data_store.api_keys.get(api_key)
        if email:
            return data_store.users.get(email)
        return None
    
    @staticmethod
    def verify_password(email: str, password: str) -> bool:
        """Verify user password"""
        user = data_store.users.get(email)
        if user:
            return check_password_hash(user['password_hash'], password)
        return False

class Form:
    """Form model for managing form data"""
    
    @staticmethod
    def create_form(owner_email: str, form_data: dict) -> dict:
        """Create a new form"""
        form_id = str(uuid.uuid4())
        
        # Validate form structure
        if 'title' not in form_data:
            raise ValueError("Form must have a title")
        
        if 'fields' not in form_data or not isinstance(form_data['fields'], list):
            raise ValueError("Form must have fields as a list")
        
        # Validate each field
        for field in form_data['fields']:
            if not isinstance(field, dict):
                raise ValueError("Each field must be a dictionary")
            
            required_keys = ['name', 'type']
            for key in required_keys:
                if key not in field:
                    raise ValueError(f"Field must have '{key}' property")
        
        # Store form
        form = {
            'id': form_id,
            'owner_email': owner_email,
            'title': form_data['title'],
            'description': form_data.get('description', ''),
            'fields': form_data['fields'],
            'created_at': datetime.datetime.utcnow().isoformat(),
            'response_count': 0
        }
        
        data_store.forms[form_id] = form
        data_store.responses[form_id] = []
        
        return form
    
    @staticmethod
    def get_form(form_id: str) -> Optional[dict]:
        """Get form by ID"""
        return data_store.forms.get(form_id)
    
    @staticmethod
    def get_user_forms(owner_email: str) -> List[dict]:
        """Get all forms owned by a user"""
        user_forms = []
        for form in data_store.forms.values():
            if form['owner_email'] == owner_email:
                user_forms.append(form)
        return user_forms
    
    @staticmethod
    def add_response(form_id: str, response_data: dict) -> bool:
        """Add a response to a form"""
        if form_id not in data_store.forms:
            return False
        
        # Add timestamp to response
        response = {
            'id': str(uuid.uuid4()),
            'form_id': form_id,
            'data': response_data,
            'submitted_at': datetime.datetime.utcnow().isoformat()
        }
        
        data_store.responses[form_id].append(response)
        
        # Update response count
        data_store.forms[form_id]['response_count'] = len(data_store.responses[form_id])
        
        return True
    
    @staticmethod
    def get_responses(form_id: str) -> List[dict]:
        """Get all responses for a form"""
        return data_store.responses.get(form_id, [])
    
    @staticmethod
    def get_all_forms() -> List[dict]:
        """Get all forms (for admin/debugging purposes)"""
        return list(data_store.forms.values())
