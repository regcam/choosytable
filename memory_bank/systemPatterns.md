# System Patterns

## Application Architecture

### Flask Blueprint Structure
```
app/
├── __init__.py          # App factory and global configuration
├── main/               # Main application blueprint
│   ├── __init__.py     # Blueprint registration
│   └── routes.py       # Route handlers and business logic
├── models.py           # Data models and forms
├── constants.py        # Application constants and choices
└── mock_auth.py        # Development authentication (optional)
```

### Key Design Patterns

#### 1. App Factory Pattern
- `create_app()` function for flexible app creation
- Environment-based configuration
- Modular component initialization
- Separation of concerns between creation and configuration

#### 2. Blueprint Organization
- Single main blueprint for core functionality
- Clean separation of routes and business logic
- Modular authentication (real OAuth vs mock)
- Easy extension for future features

#### 3. Caching Strategy Pattern
- **Three-tier TTL**: Short (5min), Medium (30min), Long (1hr)
- **Namespaced Keys**: Prevent cache collisions
- **Smart Invalidation**: Targeted cache clearing on data changes
- **Race Condition Protection**: Coordinated cache updates

## Data Patterns

### MongoDB Document Structure
```javascript
// User Document
{
  _id: ObjectId,
  email: "user@example.com",
  name: "User Name",
  gender: "Non-binary",
  ethnicity: "Asian",
  location: "CA",
  age: "25-34",
  created_at: Date,
  last_modified: Date
}

// Company Document  
{
  _id: ObjectId,
  company: "Company Name",
  reviews: [
    {
      _id: "review_id",
      review: "Review text",
      rating: 4,
      user: "user_object_id",
      created: Date
    }
  ],
  // Interview data by position
  senior_engineer: [
    {
      _id: "interview_id", 
      employee: "Employee Name",
      user: "user_object_id",
      user_ethnicity: "Black or African American",
      user_gender: "Woman",
      win: "y" // y/n/o (yes/no/other)
    }
  ],
  created: Date,
  last_modified: Date
}
```

### Query Optimization Patterns
- **Projection Queries**: Fetch only needed fields
- **Indexed Lookups**: Optimized query performance
- **Aggregation Pipelines**: Server-side data processing
- **Batch Operations**: Reduce database round trips

## Authentication Patterns

### Dual Authentication Strategy
```python
# Production: Google OAuth
if not use_mock_auth:
    blueprint = make_google_blueprint(...)
    
# Development: Mock Auth  
if use_mock_auth:
    # Simple test user creation
    login_user(User('test@example.com'))
```

### Session Management
- Flask-Login for session handling
- Persistent secret keys via environment
- Secure cookie configuration
- Proper logout handling

## Performance Patterns

### Caching Layers
1. **User Data Cache** (30 min TTL)
   - User profiles and preferences
   - User-specific review lists

2. **Company Data Cache** (5 min TTL)
   - Company lists and basic info
   - Frequently accessed company profiles

3. **Analytics Cache** (1 hour TTL)  
   - Interview statistics
   - Aggregated demographic data

### Database Indexing Strategy
```javascript
// Critical indexes for performance
db.choosytable.createIndex({"email": 1})                    // User auth
db.choosytable.createIndex({"reviews.user": 1})             // User reviews  
db.choosytable.createIndex({"last_modified": -1})           // Time-based sorting
db.choosytable.createIndex({"company": 1})                  // Company lookup
db.choosytable.createIndex({"reviews._id": 1})              // Review operations
```

## Error Handling Patterns

### Graceful Degradation
- Cache misses fallback to database
- Database errors return empty results with logging
- Authentication failures redirect to login
- Form validation with user-friendly messages

### Logging Strategy
- Error logging for debugging
- Performance logging for optimization
- User action logging for analytics
- Security event logging

## Code Organization Patterns

### Constants Management
- Centralized choice lists (ethnicity, gender, locations)
- Highlighted ethnicities for UI
- Position types for interview tracking
- Configuration via constants.py

### Helper Function Pattern
- Database query helpers with caching
- User authentication helpers
- Cache management utilities
- Pagination utilities

### Form Handling Pattern
- Flask-WTF for form security
- Validation at form and route level
- CSRF protection enabled
- User-friendly error messages

## Security Patterns

### Environment-Based Security
```python
# Secure secret management
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY required")

# Environment-conditional OAuth settings  
if os.environ.get('FLASK_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
```

### Input Validation
- Server-side form validation
- MongoDB injection prevention
- CSRF token validation
- Sanitized user inputs

## Future Pattern Considerations
- **API Endpoints**: RESTful API for mobile/SPA
- **Background Tasks**: Async processing for heavy operations
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Monitoring**: APM integration for performance tracking