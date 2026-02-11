# IT Help Desk AI Backend

FastAPI backend for IT Help Desk with Banking-Grade Security

## Features

### 🔒 Multi-Level Security
- **Level 1**: URL Whitelist Validation
- **Level 2**: User ID Validation (Optional - Can be disabled)
- **Level 3**: Rate Limiting
- **Level 4**: Request Size & Content Validation
- JWT-based Authentication
- Security Audit Logging
- Automatic User Blocking on Failed Attempts

### 📊 Smart Logging System
- Logs organized by type, method, date, and time
- Automatic cleanup of logs older than 10 days (configurable)
- Multiple log types: Application, Security, Database, Agent, API
- JSON-formatted logs for easy parsing
- Can be imported and used anywhere in the project

### 🤖 AI Agent Services
- Automatic ticket categorization
- Priority assessment
- Solution suggestions
- Sentiment analysis
- Similar ticket detection

### 🗄️ Database Services
- Generic database service with CRUD operations
- Transaction management
- SQLAlchemy ORM support

## Project Structure

```
IT Help Desk AI Backend/
├── main.py                      # Main FastAPI application
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── core/                        # Core functionality
│   ├── config.py               # Configuration management
│   ├── security/               # Security implementations
│   │   ├── middleware.py       # Security middleware
│   │   ├── auth.py            # JWT authentication
│   │   ├── validators.py      # Security validators
│   │   └── rate_limiter.py    # Rate limiting
│   └── logging/                # Logging system
│       └── logger.py           # Advanced logger with auto-cleanup
├── services/                    # Business logic services
│   ├── db_services/            # Database operations
│   │   ├── database.py        # Database configuration
│   │   └── database_service.py # Database service class
│   ├── agent_services/         # AI Agent logic
│   │   └── agent_service.py   # AI processing service
│   └── security_services/      # Security services
│       └── audit_service.py   # Security audit service
├── api/                         # API endpoints
│   ├── routes.py               # Main router
│   └── endpoints/              # Endpoint modules
│       ├── auth.py            # Authentication endpoints
│       ├── tickets.py         # Ticket management
│       ├── users.py           # User management
│       └── admin.py           # Admin operations
└── logs/                        # Auto-generated log files
    ├── application/            # Application logs
    ├── security/               # Security logs
    ├── database/               # Database logs
    ├── agent/                  # AI Agent logs
    └── api/                    # API logs
```

## Installation

### 1. Create Virtual Environment
```bash
python -m venv venv_IT_Help_Desk
```

### 2. Activate Virtual Environment
Windows:
```bash
venv_IT_Help_Desk\Scripts\activate
```

Linux/Mac:
```bash
source venv_IT_Help_Desk/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
copy .env.example .env
```

Edit `.env` file with your configuration:
- Change `SECRET_KEY` to a strong random string
- Configure database URL
- Set allowed origins for CORS
- Configure security features

## Configuration

### Security Features (Can be enabled/disabled in .env)

```env
# Enable/Disable User ID Validation
ENABLE_USER_ID_VALIDATION=True  # Set to False to disable

# Enable/Disable URL Whitelist
ENABLE_URL_WHITELIST=True  # Set to False to disable

# Enable/Disable Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
```

### Adding Allowed Endpoints

Edit `core/config.py`:
```python
ALLOWED_ENDPOINTS: List[str] = [
    "/health",
    "/api/auth/login",
    "/api/tickets",  # Add your endpoint
    # Add more as needed
]
```

## Running the Application

### Development Mode
```bash
python main.py
```
or
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Security Implementation

### User ID Validation
Every request (except public endpoints) must include user_id:
- In header: `X-User-ID: your-user-id`
- Or in query param: `?user_id=your-user-id`

### Public Endpoints (No User ID Required)
- `/health`
- `/api/auth/login`
- `/api/auth/register`
- `/api/docs`
- `/api/redoc`

### Protected Endpoints
All other endpoints require valid user_id

## Logging Usage

### Using Loggers in Your Code

```python
from core.logging.logger import api_logger, security_logger, db_logger

# Log with method and extra info
api_logger.info(
    "User created successfully",
    method="POST",
    extra_info={"user_id": "123", "email": "user@example.com"}
)

# Security log
security_logger.warning(
    "Failed login attempt",
    method="LOGIN",
    extra_info={"ip": "192.168.1.1", "user_id": "unknown"}
)

# Database log
db_logger.error(
    "Database connection failed",
    method="CONNECT",
    extra_info={"error": "Connection timeout"}
)
```

### Creating Custom Logger

```python
from core.logging.logger import get_logger

# Create custom logger
my_logger = get_logger("my_service", "custom_type")
my_logger.info("My custom message", method="CUSTOM_METHOD")
```

## Log Management

Logs are automatically:
- Organized by type/date/hour
- Cleaned up after 10 days (configurable)
- Saved in JSON format
- Available at: `logs/{type}/{date}/{filename}.log`

## Next Steps

1. ✅ Project structure created
2. ✅ Security layers implemented
3. ✅ Logging system with auto-cleanup ready
4. ⏳ Tell me what endpoints to create
5. ⏳ Define database models
6. ⏳ Implement AI agent logic
7. ⏳ Connect to your React frontend

## Testing Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Login (Public - No User ID Required)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

### Create Ticket (Protected - User ID Required)
```bash
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{"title":"Laptop not working","description":"My laptop won't start"}'
```

## Support

For questions or issues, check the logs in the `logs/` directory organized by type and date.

## License

[Your License Here]
