"""Authentication routes with OAuth and GDPR compliance."""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import logging

from . import db
from .models import User, AuditLog
from .forms import LoginForm, SignUpForm, ChangePasswordForm, AccountSettingsForm

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)

# Initialize OAuth
oauth = OAuth()


def init_oauth_client(app):
    """Initialize OAuth client with Flask app."""
    client_id = app.config.get('GOOGLE_CLIENT_ID')
    client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        app.logger.warning(
            "Google OAuth credentials not configured. "
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file."
        )
    
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=client_id or 'placeholder',
        client_secret=client_secret or 'placeholder',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    return oauth


def log_audit_event(user_id, action, description=None):
    """Log user actions for GDPR compliance."""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging audit event: {str(e)}")


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # Update last login info
        user.last_login = datetime.utcnow()
        user.last_ip = request.remote_addr
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        log_audit_event(user.id, 'login', 'User logged in successfully')
        
        flash(f'Welcome back, {user.first_name or user.email}!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
            data_processing_consent=form.data_processing_consent.data,
            marketing_consent=form.marketing_consent.data,
            gdpr_consent_date=datetime.utcnow(),
            email_verified=False
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            log_audit_event(user.id, 'signup', 'New user registered')
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            flash('Error creating account. Please try again.', 'error')
    
    return render_template('auth/signup.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout."""
    log_audit_event(current_user.id, 'logout', 'User logged out')
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/login/google')
def login_google():
    """Google OAuth login redirect."""
    # Check if credentials are configured
    if not current_app.config.get('GOOGLE_CLIENT_ID') or not current_app.config.get('GOOGLE_CLIENT_SECRET'):
        flash(
            'Google login is not configured. '
            'Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file.',
            'error'
        )
        return redirect(url_for('auth.login'))
    
    google = oauth.google
    if google is None:
        flash('Google login configuration error. Please contact support.', 'error')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)


@bp.route('/authorize/google')
def authorize_google():
    """Handle Google OAuth callback."""
    try:
        google = oauth.google
        if google is None:
            flash('Google login is not configured.', 'error')
            return redirect(url_for('auth.login'))
        
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            flash('Failed to retrieve user information from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user exists
        user = User.query.filter_by(google_id=user_info['sub']).first()
        
        if user is None:
            # Create new user from Google data
            user = User(
                email=user_info['email'].lower(),
                google_id=user_info['sub'],
                first_name=user_info.get('given_name'),
                last_name=user_info.get('family_name'),
                google_profile_pic=user_info.get('picture'),
                data_processing_consent=True,  # OAuth implies consent
                gdpr_consent_date=datetime.utcnow(),
                email_verified=user_info.get('email_verified', False)
            )
            
            try:
                db.session.add(user)
                db.session.commit()
                log_audit_event(user.id, 'oauth_signup', 'New user registered via Google OAuth')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creating OAuth user: {str(e)}")
                flash('Error creating account. Please try again.', 'error')
                return redirect(url_for('auth.login'))
        
        # Update last login info
        user.last_login = datetime.utcnow()
        user.last_ip = request.remote_addr
        db.session.commit()
        
        login_user(user, remember=True)
        log_audit_event(user.id, 'oauth_login', 'User logged in via Google OAuth')
        
        flash(f'Welcome, {user.first_name or user.email}!', 'success')
        return redirect(url_for('main.index'))
    
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Account settings and privacy controls."""
    form = AccountSettingsForm()
    change_password_form = ChangePasswordForm()
    
    if form.validate_on_submit() and form.submit.data:
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.marketing_consent = form.marketing_consent.data
        current_user.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            log_audit_event(current_user.id, 'settings_update', 'User updated account settings')
            flash('Settings updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating settings: {str(e)}")
            flash('Error updating settings.', 'error')
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.marketing_consent.data = current_user.marketing_consent
    
    return render_template('auth/settings.html', form=form, change_password_form=change_password_form)


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
        else:
            current_user.set_password(form.new_password.data)
            current_user.updated_at = datetime.utcnow()
            
            try:
                db.session.commit()
                log_audit_event(current_user.id, 'password_change', 'User changed password')
                flash('Password changed successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error changing password: {str(e)}")
                flash('Error changing password.', 'error')
    
    return redirect(url_for('auth.settings'))


@bp.route('/data-export')
@login_required
def export_data():
    """GDPR: Export user data as JSON."""
    import json
    from flask import Response
    
    user_data = {
        'user': current_user.to_dict(include_sensitive=True),
        'habits': [
            {
                'id': h.id,
                'name': h.name,
                'category': h.category,
                'frequency': h.frequency,
                'created_at': h.created_at.isoformat()
            }
            for h in current_user.habits
        ],
        'journals': [
            {
                'id': j.id,
                'title': j.title,
                'mood': j.mood,
                'created_at': j.created_at.isoformat()
            }
            for j in current_user.journals
        ],
        'goals': [
            {
                'id': g.id,
                'title': g.title,
                'status': g.status,
                'created_at': g.created_at.isoformat()
            }
            for g in current_user.goals
        ]
    }
    
    current_user.data_export_requested = True
    db.session.commit()
    log_audit_event(current_user.id, 'data_export', 'User exported personal data')
    
    return Response(
        json.dumps(user_data, indent=2),
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment;filename=checklist_data_{current_user.id}_{datetime.utcnow().strftime("%Y%m%d")}.json'
        }
    )


@bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """GDPR: Request account and data deletion."""
    user_id = current_user.id
    
    try:
        log_audit_event(user_id, 'data_deletion_request', 'User requested account deletion')
        
        # Soft delete first (set deletion flag)
        current_user.data_deletion_requested = True
        current_user.is_active = False
        db.session.commit()
        
        logout_user()
        flash('Your account deletion has been initiated. We will permanently delete your data within 30 days as per GDPR regulations.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting account: {str(e)}")
        flash('Error processing deletion request.', 'error')
        return redirect(url_for('auth.settings'))
