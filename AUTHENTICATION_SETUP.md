# Authentication & User Management Setup Guide

## Overview

This checklist app now includes a complete authentication system with:
- ✅ Email/Password registration and login
- ✅ Google OAuth 2.0 integration
- ✅ GDPR compliance with user data protection
- ✅ User data export and deletion (right to be forgotten)
- ✅ Audit logging for all user actions
- ✅ Session management and security

## Prerequisites

1. Python 3.8+
2. Flask and dependencies (install from `requirements.txt`)
3. Google OAuth 2.0 credentials

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google OAuth

#### Get Google Credentials:

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project
3. Enable the "Google+ API"
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs:
     - `http://localhost:5000/auth/authorize/google` (development)
     - `https://yourdomain.com/auth/authorize/google` (production)
5. Copy your Client ID and Client Secret

#### Configure Environment Variables:

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add:

```env
FLASK_ENV=development
SECRET_KEY=your-secure-random-key-here

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Security (change in production)
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### 3. Initialize Database

```bash
python run.py
```

The database will be created automatically with user, audit log, and other tables.

### 4. Run the Application

```bash
python run.py
```

Visit `http://localhost:5000/auth/login`

## User Features

### Authentication
- **Sign Up**: Email, username, password registration with GDPR consent
- **Sign In**: Email/password login with "Remember Me" option
- **Google OAuth**: One-click login with Google
- **Session Management**: Automatic logout after 30 days of inactivity

### Privacy & GDPR Compliance

#### Rights Available to Users

1. **Right to Access** (`/auth/settings` → "Export My Data")
   - Download all personal data as JSON
   - Includes habits, goals, journals, and account info

2. **Right to Erasure** (`/auth/settings` → "Delete Account")
   - Request permanent account deletion
   - Data deleted within 30 days per GDPR
   - Irreversible action

3. **Right to Data Portability**
   - Export data in portable JSON format
   - Can import to another service

4. **Right to Rectification**
   - Update profile information in settings
   - Change marketing preferences

5. **Consent Management**
   - Explicit opt-in required for data processing
   - Separate consent for marketing emails
   - Can withdraw consent anytime

### Account Management

**Profile Settings** (`/auth/settings`):
- Update first name and last name
- View account creation date and last login
- Change marketing preferences

**Security** (`/auth/settings` → Security):
- Change password (for email/password accounts)
- View session information
- View last login IP address

**Privacy & GDPR** (`/auth/settings` → Privacy & GDPR):
- View data processing consent status
- Understand GDPR rights
- Export personal data
- Request account deletion

## Data Model

### User Model

```python
class User(UserMixin, db.Model):
    id                              # Unique identifier
    email                           # User email (unique, indexed)
    username                        # Optional username
    password_hash                   # Hashed password (nullable for OAuth)
    
    # OAuth
    google_id                       # Google sub identifier
    google_profile_pic              # Profile picture URL
    
    # Profile
    first_name, last_name          # Optional user names
    
    # GDPR & Privacy
    data_processing_consent        # Explicit consent for data processing
    marketing_consent              # Opt-in for marketing emails
    gdpr_consent_date              # When user consented
    last_gdpr_review               # Last policy review date
    data_export_requested          # Track export requests
    data_deletion_requested        # Track deletion requests
    
    # Account Status
    is_active                      # Account active/deactivated
    email_verified                 # Email verification status
    created_at, updated_at         # Timestamps
    last_login                     # Last login time
    last_ip                        # Last login IP address
```

### Audit Log Model

```python
class AuditLog(db.Model):
    id
    user_id                        # User being audited
    action                         # login, logout, password_change, data_export, etc.
    description                    # Additional details
    ip_address                     # Request IP
    user_agent                     # Browser info
    created_at                     # When action occurred
```

## GDPR Compliance Features

### Data Collection
- Only necessary data collected
- Explicit consent required before data processing
- Separate consent for marketing communications

### Data Security
- Passwords hashed with PBKDF2
- HTTPS encryption for data in transit
- Database-level encryption at rest
- Audit logging of all data access

### Data Rights
- Users can access their data anytime
- Users can delete their data (deleted within 30 days)
- Users can export data in portable format
- Compliance with all GDPR Articles 15-22

### Privacy Policies
- Comprehensive privacy policy available
- Clear explanation of data usage
- Links to GDPR documentation
- Data retention periods specified

## Security Best Practices

### Production Deployment

1. **Set Strong Secret Key**:
   ```bash
   export SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Use HTTPS**:
   ```env
   SESSION_COOKIE_SECURE=True
   PREFERRED_URL_SCHEME=https
   ```

3. **Set Debug Mode**:
   ```bash
   export FLASK_ENV=production
   ```

4. **Database Security**:
   - Use strong database passwords
   - Enable database encryption
   - Regular backups

5. **Environment Variables**:
   - Never commit `.env` to version control
   - Use secrets management service in production
   - Rotate credentials regularly

## User Queries & Routes

### Authentication Routes
- `GET  /auth/login` - Login page
- `POST /auth/login` - Submit login
- `GET  /auth/signup` - Registration page
- `POST /auth/signup` - Create account
- `GET  /auth/logout` - Logout user
- `GET  /auth/login/google` - Google OAuth redirect
- `GET  /auth/authorize/google` - Google OAuth callback

### User Management
- `GET  /auth/settings` - Account settings page
- `POST /auth/settings` - Update profile
- `POST /auth/change-password` - Change password
- `GET  /auth/data-export` - Download personal data (JSON)
- `POST /auth/delete-account` - Request account deletion

### Public Pages
- `GET  /privacy` - Privacy policy & GDPR info

## User Data Organization

Each user's data is isolated:
- Habits belong to user via `user_id` foreign key
- Journals belong to user via `user_id` foreign key
- Goals belong to user via `user_id` foreign key
- Schedules belong to user via `user_id` foreign key
- All queries filtered by `current_user.id` to ensure data isolation

## Testing

### Test User Account
Create a test user in signup:
- Email: `test@example.com`
- Password: `TestPass123`
- Accept GDPR consent

### Test OAuth Flow
1. Click "Sign in with Google"
2. Sign in with a Google account
3. Confirm data collection consent
4. Redirected to dashboard

### Test GDPR Features
1. Go to `/auth/settings`
2. Click "Export My Data" to download JSON
3. View data deletion request process
4. Check audit logs for actions

## Troubleshooting

### "Google login is not configured"
- Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `.env`
- Verify Google OAuth application is set up correctly
- Check redirect URI matches in Google Console

### "Please log in to access this page"
- Session may have expired (30 days)
- User not authenticated
- `@login_required` decorator blocking access

### Database Migration Issues
- Delete `data.db` to reset database
- Run `python run.py` to create fresh database
- May lose existing data

## References

- [GDPR Official Documentation](https://gdpr-info.eu/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Authlib OAuth 2.0](https://docs.authlib.org/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [OWASP Security Best Practices](https://owasp.org/)
