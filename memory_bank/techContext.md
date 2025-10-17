# Technical Context

## Technology Stack

### Backend Framework
- **Flask 3.0.3**: Latest Python web framework (updated for security & performance)
- **Python 3.8+**: Core programming language
- **Flask-Dance 7.1.0**: Google OAuth integration
- **Flask-Login 0.6.3**: User session management
- **Flask-WTF 1.2.2**: Form handling and CSRF protection

### Database & Storage
- **MongoDB 4.0+**: Document-based data storage
- **PyMongo 4.15.3**: Latest Python MongoDB driver (updated)
- **Flask-PyMongo 3.0.1**: Flask 3.x compatible MongoDB integration
- **ObjectId**: MongoDB document identification

### Caching & Performance
- **Memcached**: High-performance caching layer
- **PyMemcache 4.0.0**: Python memcached client
- **Custom Cache Manager**: Intelligent invalidation strategies

### Authentication & Security
- **Google OAuth 2.0**: Secure user authentication
- **Environment-based Secrets**: Production-ready security
- **CSRF Protection**: Form security
- **HTTPS Required**: Production security

### Frontend & Assets
- **Jinja2 Templates**: Server-side rendering
- **Bootstrap**: Responsive UI framework
- **Flask-Navigation**: Dynamic navigation
- **Asset Bundling**: Performance optimization

## Development Setup Requirements

### System Dependencies
```bash
# macOS
brew install python3 mongodb-community memcached

# Linux (Ubuntu/Debian)  
sudo apt install python3 python3-pip mongodb memcached
```

### Python Dependencies
- Core packages defined in `requirements.txt`
- Virtual environment recommended
- Specific versions locked for stability

### Environment Configuration
Required environment variables:
- `SECRET_KEY`: Flask session security (64+ chars)
- `GOOGLE_CLIENT_ID`: OAuth client identifier
- `GOOGLE_CLIENT_SECRET`: OAuth client secret
- `MONGO_URI`: Database connection string
- `MEMCACHED_HOST`: Cache server location

### Development vs Production
- **Development**: Mock authentication available (`USE_MOCK_AUTH=true`)
- **Production**: Full OAuth, HTTPS required, optimized settings

## Technical Constraints

### Performance Requirements
- Page loads < 1 second
- Database queries < 100ms average
- Cache hit rate > 85%
- Support 100+ concurrent users

### Security Requirements
- All user data encrypted in transit (HTTPS)
- OAuth-only authentication (no passwords)
- Environment-based secret management
- CSRF protection on all forms

### Scalability Considerations
- MongoDB horizontal scaling capability
- Memcached distributed caching
- Stateless application design
- Connection pooling for databases

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- Progressive enhancement approach

## Development Workflow
1. **Local Setup**: Use mock authentication for rapid development
2. **Testing**: Comprehensive test suite with performance benchmarks
3. **Deployment**: Automated deployment with environment validation
4. **Monitoring**: Performance tracking and error logging

## Key Technical Decisions
- **MongoDB over SQL**: Better fit for flexible review/interview data
- **Memcached over Redis**: Simpler setup, sufficient for current needs
- **Flask over Django**: Lightweight, appropriate for scope
- **Server-side rendering**: Better SEO, simpler architecture
- **Google OAuth only**: Reduces complexity, leverages existing accounts