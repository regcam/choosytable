"""
Mock authentication for local testing without Google OAuth.
"""
from flask import Blueprint, session, redirect, url_for
from flask_login import login_user
from app.models import User
import datetime

# Create a mock blueprint that mimics Google OAuth
mock_auth_bp = Blueprint('mock_auth', __name__, url_prefix='/mock')

@mock_auth_bp.route('/login')
def mock_login():
    """Mock login that creates a test user session."""
    # Create a test user profile
    test_user_info = {
        'email': 'test@example.com',
        'name': 'Test User',
        'id': 'mock_google_id_123',
        'verified_email': True
    }
    
    # Store in session to simulate OAuth response
    session['mock_user'] = test_user_info
    
    # Log in the user
    login_user(User(test_user_info['email']))
    
    return redirect(url_for('main.home'))

@mock_auth_bp.route('/authorized')
def mock_authorized():
    """Mock OAuth callback."""
    return redirect(url_for('main.home'))

def get_mock_user_info():
    """Get mock user info (simulates google.get('/oauth2/v1/userinfo'))"""
    return session.get('mock_user', {
        'email': 'test@example.com',
        'name': 'Test User',
        'id': 'mock_google_id_123',
        'verified_email': True
    })

class MockGoogle:
    """Mock google object for testing"""
    def __init__(self):
        self.authorized = True
        
    def get(self, endpoint):
        """Mock the google.get() method"""
        if endpoint == "/oauth2/v1/userinfo":
            return MockResponse(get_mock_user_info())
        return MockResponse({})

class MockResponse:
    """Mock response object"""
    def __init__(self, data):
        self.data = data
        
    def json(self):
        return self.data