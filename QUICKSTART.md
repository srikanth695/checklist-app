# Quick Start Guide - User Authentication

## 🚀 Get Started in 5 Minutes

### Step 1: Configure Google OAuth (2 min)

1. Visit [Google Cloud Console](https://console.developers.google.com/)
2. Create a new project → "Checklist App"
3. Search for "Google+ API" → Enable it
4. Go to "Credentials" → Create OAuth 2.0 Web Application
5. Add Authorized redirect URI:
   ```
   http://localhost:5000/auth/authorize/google
   ```
6. Copy Client ID and Client Secret

### Step 2: Set Environment Variables (1 min)

Create `.env` file in project root:

```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key-123

GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
```

### Step 3: Install & Run (2 min)

```bash
# Install packages
pip install -r requirements.txt

# Run the app
python run.py
```

Visit: `http://localhost:5000/auth/login`

## 📝 Test Features

### Email/Password Registration
1. Click "Create Account"
2. Fill form and accept GDPR consent ✓
3. Create account → redirects to login
4. Sign in with new credentials

### Google OAuth
1. Click "Sign in with Google"
2. Select your Google account
3. Approve data sharing
4. Auto-logged in ✓

### Settings & Privacy
1. Click user menu → "Settings"
2. Update profile info
3. Export your data (JSON download)
4. View GDPR rights
5. Delete account (requires confirmation)

## 🔐 Security Checklist

- [x] Passwords hashed (PBKDF2)
- [x] HTTPS ready (SESSION_COOKIE_SECURE)
- [x] CSRF protection (Flask-WTF)
- [x] SQL injection protection (SQLAlchemy)
- [x] User data isolation (filtered by user_id)
- [x] Audit logging enabled
- [x] GDPR compliant

## 📊 Database Schema

```
users (table)
├── id, email, username
├── password_hash (nullable for OAuth)
├── google_id, google_profile_pic
├── first_name, last_name
├── data_processing_consent ✓
├── marketing_consent
├── is_active, email_verified
├── created_at, last_login, last_ip

audit_logs (table)
├── user_id, action (login, logout, etc)
├── ip_address, user_agent
└── created_at

habits, journals, goals, schedules
└── user_id (foreign key)
```

## 🎯 Key Routes

| Route | Purpose | Auth Required |
|-------|---------|---------------|
| `/auth/login` | Login page | ❌ |
| `/auth/signup` | Register | ❌ |
| `/auth/logout` | Logout | ✅ |
| `/auth/login/google` | Google OAuth | ❌ |
| `/auth/settings` | Profile & Privacy | ✅ |
| `/auth/data-export` | Download data | ✅ |
| `/privacy` | Privacy policy | ❌ |

## 🆘 Troubleshooting

**"Google login is not configured"**
- Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to `.env`
- Restart the app

**"Please log in"**
- Session expired or not logged in
- Visit `/auth/login`

**Database errors**
- Delete `data.db` and restart
- Fresh database created automatically

## 📚 Full Documentation

See `AUTHENTICATION_SETUP.md` for:
- Complete setup instructions
- GDPR compliance details
- Security best practices
- Advanced configuration

See `GDPR_QUERIES.sql` for:
- Database audit queries
- User data export queries
- Compliance checks
- Security monitoring

## 💡 What's Different

Before: Open app, use immediately
Now: 
- ✅ Create account (email or Google)
- ✅ Your data is private & secure
- ✅ GDPR compliant with data export
- ✅ Can delete account anytime
- ✅ Audit trail of all actions

## 🎓 User Rights (GDPR)

You can:
- 📥 **Export data** as JSON anytime
- 🗑️ **Delete account** permanently
- 🔒 **Update profile** information
- 🚫 **Opt-out** of marketing emails
- 🔍 **View** data processing status

## 🔗 OAuth Providers

Currently supported:
- ✅ Google (implemented)
- 📝 GitHub (can add)
- 📝 Microsoft (can add)

Add more in `app/auth_routes.py`

---

**Questions?** Check `AUTHENTICATION_SETUP.md` or the privacy policy at `/privacy`
