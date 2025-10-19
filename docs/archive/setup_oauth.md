# 🔐 Google OAuth Setup Guide

## Current Issue
Your ChoosyTable app is running but login fails because Google OAuth credentials are not configured.

## Error Details
- **URL being generated**: `https://accounts.google.com/o/oauth2/auth?client_id=your_google_oauth_client_id_here`
- **Problem**: `your_google_oauth_client_id_here` is a placeholder, not a real Client ID

## Fix Steps

### 1. Create Google Cloud Project
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Name it something like "ChoosyTable Dev"

### 2. Enable Required APIs
1. Go to "APIs & Services" → "Library"
2. Search and enable:
   - Google+ API (for user info)
   - Google OAuth2 API

### 3. Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure:
   - **Application type**: Web application
   - **Name**: ChoosyTable Local Dev
   - **Authorized redirect URIs**: 
     ```
     http://localhost:5000/login/google/authorized
     ```
4. Save and copy:
   - Client ID (looks like: `123456789-abc123.apps.googleusercontent.com`)
   - Client Secret (looks like: `GOCSPX-abc123def456`)

### 4. Update Environment File
Edit `.env` file and replace:
```bash
GOOGLE_CLIENT_ID=your_google_oauth_client_id_here
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret_here
```

With your actual values:
```bash
GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456
```

### 5. Restart Application
```bash
# Kill current process
pkill -f "python3.*app"

# Start again
python3 -c "from app import app; app.run(debug=True, port=5000)"
```

## Testing
1. Visit: http://localhost:5000
2. Click login - should redirect to Google
3. Authenticate with your Google account
4. Should redirect back to ChoosyTable successfully

## Troubleshooting
- **"redirect_uri_mismatch"**: Check authorized URIs match exactly
- **"invalid_client"**: Verify Client ID and Secret are correct
- **"access_blocked"**: App may need verification for production use

## Development vs Production
- **Development**: Use `http://localhost:5000` 
- **Production**: Use your actual domain like `https://choosytable.com`