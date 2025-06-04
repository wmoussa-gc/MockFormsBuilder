# Form Builder REST API

A Flask-based REST API for creating and managing forms with user authentication, custom field definitions, and response collection. Features in-memory storage for simplicity and rapid deployment.

## Features

- **User Management**: Sign up with email/password and receive unique API keys
- **Form Creation**: Build custom forms with various field types and validation
- **Public Form Access**: Share forms publicly for response collection
- **Response Management**: Collect and retrieve form responses
- **API Authentication**: Secure endpoints with API key authentication
- **Documentation**: Built-in API documentation page

## Quick Start

### Prerequisites

- Python 3.11+
- Flask and dependencies (automatically installed)

### Installation & Running

1. **Clone or access the project**
   ```bash
   # The project is ready to run in your Replit environment
   ```

2. **Start the server**
   ```bash
   # Using the workflow (recommended)
   # Click "Run" or use the workflow "Start application"
   
   # Or manually:
   python main.py
   ```

3. **Access the API**
   - Documentation: `http://localhost:5000/` or your Replit URL
   - API Base URL: `http://localhost:5000/api/`

## API Endpoints

### Authentication
All endpoints marked with 🔐 require an API key in the `X-API-Key` header or `api_key` query parameter.

### User Management

#### Sign Up
```http
POST /api/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "email": "user@example.com",
    "api_key": "uuid-generated-key",
    "created_at": "2023-12-01T10:00:00"
  }
}
```

### Form Management

#### Create Form 🔐
```http
POST /api/forms
Content-Type: application/json
X-API-Key: your-api-key

{
  "title": "Contact Form",
  "description": "Get in touch with us",
  "fields": [
    {
      "name": "name",
      "type": "text",
      "label": "Full Name",
      "required": true
    },
    {
      "name": "email",
      "type": "email",
      "label": "Email Address",
      "required": true
    },
    {
      "name": "message",
      "type": "textarea",
      "label": "Your Message",
      "required": false
    }
  ]
}
```

#### Get User Forms 🔐
```http
GET /api/forms
X-API-Key: your-api-key
```

#### Get Form Structure (Public)
```http
GET /api/forms/{form_id}
```

### Response Management

#### Submit Response (Public)
```http
POST /api/forms/{form_id}/responses
Content-Type: application/json

{
  "responses": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello, this is a test message!"
  }
}
```

#### Get Form Responses 🔐
```http
GET /api/forms/{form_id}/responses
X-API-Key: your-api-key
```

## Field Types

Supported field types for form creation:

- `text` - Single line text input
- `textarea` - Multi-line text input
- `email` - Email address input
- `number` - Numeric input
- `date` - Date picker
- `checkbox` - Boolean checkbox
- `radio` - Radio button selection
- `select` - Dropdown selection

## Example Usage

### 1. Create a User Account
```bash
curl -X POST http://localhost:5000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "securepassword123"
  }'
```

### 2. Create a Form
```bash
curl -X POST http://localhost:5000/api/forms \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-received-api-key" \
  -d '{
    "title": "Feedback Survey",
    "description": "We value your feedback",
    "fields": [
      {
        "name": "rating",
        "type": "number",
        "label": "Rate us (1-5)",
        "required": true
      },
      {
        "name": "comments",
        "type": "textarea",
        "label": "Additional Comments",
        "required": false
      }
    ]
  }'
```

### 3. Submit a Response
```bash
curl -X POST http://localhost:5000/api/forms/{form_id}/responses \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "rating": 5,
      "comments": "Excellent service!"
    }
  }'
```

### 4. Retrieve Responses
```bash
curl -X GET http://localhost:5000/api/forms/{form_id}/responses \
  -H "X-API-Key: your-api-key"
```

## Debug Endpoints

For testing and development:

- `GET /api/debug/stats` - View system statistics
- `POST /api/debug/clear` - Clear all data (testing only)

## Architecture

### Data Storage
- **In-Memory Storage**: Uses Python dictionaries for rapid development
- **No Database Required**: Perfect for prototyping and testing
- **Data Persistence**: Data exists only while server is running

### Security
- **API Key Authentication**: Each user receives a unique UUID-based API key
- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Input Validation**: Validates form structures and required fields

### Structure
```
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── models.py           # Data models and storage logic
├── auth.py             # Authentication decorators
├── api_routes.py       # API endpoint definitions
└── templates/
    └── index.html      # API documentation page
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid API key)
- `403` - Forbidden (access denied)
- `404` - Not Found
- `409` - Conflict (user already exists)
- `500` - Internal Server Error

## Development

### Adding New Field Types
1. Update the field validation in `models.py`
2. Add any specific validation logic in the Form model
3. Update the documentation

### Extending Authentication
The authentication system can be extended to support:
- Password reset functionality
- API key regeneration
- User roles and permissions

### Database Integration
To add persistent storage:
1. Replace the in-memory `DataStore` with database models
2. Add database configuration to `app.py`
3. Implement database migrations

## Deployment

This API is ready for deployment on Replit or any Python hosting platform:

1. **Replit**: Click the "Deploy" button in your Replit environment
2. **Other Platforms**: Ensure Python 3.11+ and install dependencies from `pyproject.toml`

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the API documentation at the root URL
2. Review the debug endpoints for system status
3. Verify API key authentication for protected endpoints