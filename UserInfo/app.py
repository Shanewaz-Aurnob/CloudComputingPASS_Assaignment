from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, make_response
import mysql.connector
from mysql.connector import Error
import bcrypt
import secrets
import jwt
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt-secret-key-change-this')
JWT_ALGORITHM = 'HS256'

# Database configuration - UPDATE THESE WITH YOUR ACTUAL DATABASE CREDENTIALS
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'database': 'sql12781272',
    'user': 'sql12781272',
    'password': '7qPLvwZDC4'
}

# Database connection function with connection pooling
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG,
            autocommit=True,
            pool_name='auth_pool',
            pool_size=5,
            pool_reset_session=True
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# Token-based authentication decorator
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            token = request.cookies.get('auth_token')
        
        if not token:
            return redirect(url_for('login'))
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = data['user_id']
            
            # Verify session is still active
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT us.*, u.username, u.full_name 
                    FROM user_sessions us
                    JOIN users u ON us.user_id = u.id
                    WHERE us.session_token = %s AND us.is_active = TRUE AND us.expires_at > NOW()
                """, (token,))
                
                session_data = cursor.fetchone()
                cursor.close()
                connection.close()
                
                if not session_data:
                    return redirect(url_for('login'))
                
                request.current_user = session_data
            
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# Advanced login template with enhanced features
ADVANCED_LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced User Authentication System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .auth-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            box-shadow: 0 32px 64px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            width: 100%;
            max-width: 440px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .auth-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }

        .auth-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" fill-opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }

        .auth-header h1 {
            font-size: 2.2rem;
            margin-bottom: 8px;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }

        .auth-header p {
            font-size: 1rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        .auth-content {
            padding: 40px 30px;
        }

        .tab-buttons {
            display: flex;
            margin-bottom: 32px;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 4px;
            position: relative;
        }

        .tab-button {
            flex: 1;
            padding: 14px;
            border: none;
            background: transparent;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }

        .tab-button.active {
            background: white;
            color: #667eea;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .form-group {
            margin-bottom: 24px;
            position: relative;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #374151;
            font-size: 14px;
        }

        .form-input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: #fafafa;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .form-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(102, 126, 234, 0.3);
        }

        .form-button:active {
            transform: translateY(0);
        }

        .alert {
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 24px;
            font-weight: 500;
        }

        .alert-success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }

        .alert-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .forgot-password {
            text-align: center;
            margin-top: 20px;
        }

        .forgot-password a {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }

        .forgot-password a:hover {
            text-decoration: underline;
        }

        .password-strength {
            margin-top: 8px;
            height: 4px;
            background: #e5e7eb;
            border-radius: 2px;
            overflow: hidden;
        }

        .password-strength-bar {
            height: 100%;
            transition: all 0.3s ease;
            border-radius: 2px;
        }

        .strength-weak { width: 25%; background: #ef4444; }
        .strength-fair { width: 50%; background: #f59e0b; }
        .strength-good { width: 75%; background: #10b981; }
        .strength-strong { width: 100%; background: #059669; }

        @media (max-width: 480px) {
            .auth-container {
                margin: 10px;
                border-radius: 16px;
            }
            
            .auth-header {
                padding: 30px 20px;
            }
            
            .auth-content {
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <h1>🔐 SecureAuth</h1>
            <p>Advanced Authentication System</p>
        </div>
        
        <div class="auth-content">
            {% if message %}
                <div class="alert alert-{{ 'success' if success else 'error' }}">
                    {{ message }}
                </div>
            {% endif %}

            <div class="tab-buttons">
                <button class="tab-button active" onclick="switchTab('login')">Sign In</button>
                <button class="tab-button" onclick="switchTab('register')">Sign Up</button>
            </div>

            <!-- Login Form -->
            <div id="login-tab" class="tab-content active">
                <form method="POST" action="/login">
                    <div class="form-group">
                        <label class="form-label">Username or Email</label>
                        <input type="text" name="username" class="form-input" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Password</label>
                        <input type="password" name="password" class="form-input" required>
                    </div>
                    
                    <div class="form-group">
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" name="remember_me" style="margin-right: 8px;">
                            Remember me for 30 days
                        </label>
                    </div>
                    
                    <button type="submit" class="form-button">Sign In</button>
                </form>
                
                <div class="forgot-password">
                    <a href="/forgot-password">Forgot your password?</a>
                </div>
            </div>

            <!-- Register Form -->
            <div id="register-tab" class="tab-content">
                <form method="POST" action="/register">
                    <div class="form-group">
                        <label class="form-label">Full Name</label>
                        <input type="text" name="full_name" class="form-input" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Username</label>
                        <input type="text" name="username" class="form-input" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="form-input" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Password</label>
                        <input type="password" name="password" class="form-input" id="password" required onkeyup="checkPasswordStrength()">
                        <div class="password-strength">
                            <div class="password-strength-bar" id="strength-bar"></div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Confirm Password</label>
                        <input type="password" name="confirm_password" class="form-input" required>
                    </div>
                    
                    <button type="submit" class="form-button">Create Account</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tab) {
            // Remove active class from all buttons and content
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }

        function checkPasswordStrength() {
            const password = document.getElementById('password').value;
            const strengthBar = document.getElementById('strength-bar');
            
            let strength = 0;
            if (password.length >= 8) strength++;
            if (password.match(/[a-z]/)) strength++;
            if (password.match(/[A-Z]/)) strength++;
            if (password.match(/[0-9]/)) strength++;
            if (password.match(/[^a-zA-Z0-9]/)) strength++;
            
            strengthBar.className = 'password-strength-bar';
            
            if (strength <= 2) {
                strengthBar.classList.add('strength-weak');
            } else if (strength === 3) {
                strengthBar.classList.add('strength-fair');
            } else if (strength === 4) {
                strengthBar.classList.add('strength-good');
            } else {
                strengthBar.classList.add('strength-strong');
            }
        }
    </script>
</body>
</html>'''

# Dashboard template
DASHBOARD_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - SecureAuth</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f8fafc;
            min-height: 100vh;
        }

        .navbar {
            background: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar h1 {
            color: #667eea;
            font-size: 1.5rem;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logout-btn {
            background: #ef4444;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            text-decoration: none;
            font-weight: 600;
        }

        .logout-btn:hover {
            background: #dc2626;
        }

        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }

        .welcome-card h2 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .stat-card h3 {
            color: #6b7280;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }

        .stat-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: #111827;
        }

        .sessions-table {
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .table-header {
            background: #f9fafb;
            padding: 1rem;
            border-bottom: 1px solid #e5e7eb;
        }

        .table-header h3 {
            color: #111827;
            font-size: 1.125rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        th {
            background: #f9fafb;
            font-weight: 600;
            color: #6b7280;
        }

        .status-active {
            background: #d1fae5;
            color: #065f46;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>🔐 SecureAuth Dashboard</h1>
        <div class="user-info">
            <span>Welcome, {{ user.full_name }}!</span>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
    </nav>

    <div class="container">
        <div class="welcome-card">
            <h2>Welcome back, {{ user.full_name }}! 👋</h2>
            <p>You're successfully authenticated and ready to go.</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Active Sessions</h3>
                <div class="value">{{ sessions|length }}</div>
            </div>
            <div class="stat-card">
                <h3>Last Login</h3>
                <div class="value" style="font-size: 1rem;">{{ user.last_login or 'First login' }}</div>
            </div>
            <div class="stat-card">
                <h3>Account Status</h3>
                <div class="value" style="font-size: 1rem; color: #10b981;">Active</div>
            </div>
        </div>

        <div class="sessions-table">
            <div class="table-header">
                <h3>Active Sessions</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>IP Address</th>
                        <th>Location</th>
                        <th>Created</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for session in sessions %}
                    <tr>
                        <td>{{ (request.headers.get('User-Agent', 'Unknown Device'))[:50] + '...' if request.headers.get('User-Agent', '') | length > 50 else request.headers.get('User-Agent', 'Unknown Device') }}</td>
                        <td>{{ session.get('ip_address', 'Unknown') }}</td>
                        <td>{{ session.get('location', 'Unknown') }}</td>
                        <td>{{ session.created_at.strftime('%Y-%m-%d %H:%M') if session.created_at else 'N/A' }}</td>
                        <td><span class="status-active">Active</span></td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="5" style="text-align: center; color: #6b7280;">No active sessions found</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>'''

# Helper functions
def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def generate_jwt_token(user_id, remember_me=False):
    """Generate a JWT token for the user"""
    expiry = datetime.utcnow() + timedelta(days=30 if remember_me else 1)
    payload = {
        'user_id': user_id,
        'exp': expiry,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_client_ip():
    """Get the client's IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or '127.0.0.1'

def create_user_session(user_id, token, remember_me=False):
    """Create a new user session in the database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Clean up old expired sessions
        cursor.execute("DELETE FROM user_sessions WHERE expires_at < NOW()")
        
        # Create new session
        expires_at = datetime.now() + timedelta(days=30 if remember_me else 1)
        
        cursor.execute("""
            INSERT INTO user_sessions (user_id, session_token, expires_at)
            VALUES (%s, %s, %s)
        """, (user_id, token, expires_at))
        
        connection.commit()
        cursor.close()
        return True
        
    except Error as e:
        print(f"Session creation error: {e}")
        return False
    finally:
        connection.close()

def log_login_attempt(username, success):
    """Log login attempts (basic implementation)"""
    print(f"Login attempt - Username: {username}, Success: {success}, IP: {get_client_ip()}")

# Initialize database (check if tables exist)
def check_database():
    """Check if database connection works"""
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        # Test if users table exists
        cursor.execute("SELECT COUNT(*) FROM users LIMIT 1")
        cursor.fetchone()
        cursor.close()
        print("✅ Database connection successful")
        return True
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        connection.close()

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        if not username or not password:
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                        message="Please fill in all fields", success=False)
        
        connection = get_db_connection()
        if not connection:
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                        message="Database connection error", success=False)
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Find user by username or email
            cursor.execute("""
                SELECT * FROM users 
                WHERE (username = %s OR email = %s) AND is_active = TRUE
            """, (username, username))
            
            user = cursor.fetchone()
            
            if user and verify_password(password, user['password']):
                # Update last login
                cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
                connection.commit()
                
                # Generate JWT token
                token = generate_jwt_token(user['id'], remember_me)
                
                # Create session record
                if create_user_session(user['id'], token, remember_me):
                    log_login_attempt(username, True)
                    
                    # Set cookie and redirect
                    response = make_response(redirect(url_for('dashboard')))
                    response.set_cookie('auth_token', token, 
                                      max_age=30*24*60*60 if remember_me else 24*60*60,
                                      httponly=True, secure=False, samesite='Lax')
                    return response
                else:
                    return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                                message="Session creation failed", success=False)
            else:
                log_login_attempt(username, False)
                return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                            message="Invalid username or password", success=False)
                
        except Error as e:
            print(f"Login error: {e}")
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                        message="An error occurred during login", success=False)
        finally:
            cursor.close()
            connection.close()
    
    return render_template_string(ADVANCED_LOGIN_TEMPLATE)

@app.route('/register', methods=['POST'])
def register():
    full_name = request.form.get('full_name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation
    if not all([full_name, username, email, password, confirm_password]):
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                    message="Please fill in all fields", success=False)
    
    if password != confirm_password:
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                    message="Passwords do not match", success=False)
    
    if len(password) < 8:
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                    message="Password must be at least 8 characters", success=False)
    
    if len(username) < 3:
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                    message="Username must be at least 3 characters", success=False)
    
    connection = get_db_connection()
    if not connection:
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                    message="Database connection error", success=False)
    
    try:
        cursor = connection.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                        message="Username or email already exists", success=False)
        
        # Create new user with hashed password
        password_hash = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, email, full_name, password)
            VALUES (%s, %s, %s, %s)
        """, (username, email, full_name, password_hash))
        
        connection.commit()
        cursor.close()
        
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                    message="Account created successfully! Please sign in.", success=True)
        
    except Error as e:
        print(f"Registration error: {e}")
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                    message="An error occurred during registration", success=False)
    finally:
        connection.close()

@app.route('/dashboard')
@token_required
def dashboard():
    user = request.current_user
    
    # Get user's active sessions
    connection = get_db_connection()
    sessions = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM user_sessions 
                WHERE user_id = %s AND is_active = TRUE AND expires_at > NOW()
                ORDER BY created_at DESC
            """, (user['user_id'],))
            sessions = cursor.fetchall()
            cursor.close()
        except Error as e:
            print(f"Error fetching sessions: {e}")
        finally:
            connection.close()

    return render_template_string(DASHBOARD_TEMPLATE, user=user, sessions=sessions)

@app.route('/logout')
@token_required
def logout():
    token = request.cookies.get('auth_token')
    
    # Invalidate session
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE user_sessions SET is_active = FALSE WHERE session_token = %s", (token,))
            connection.commit()
            cursor.close()
        except Error as e:
            print(f"Error logging out: {e}")
        finally:
            connection.close()
    
    # Remove token from cookies and redirect to login
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('auth_token')
    return response

@app.route('/forgot-password')
def forgot_password():
    return render_template_string('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forgot Password</title>
</head>
<body>
    <h1>Forgot Password</h1>
    <p>Please enter your email to reset your password.</p>
    <form method="POST" action="/reset-password">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required>
        <button type="submit">Reset Password</button>
    </form>
</body>
</html>''')

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email', '').strip()
    
    if not email:
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                      message="Please provide your email", success=False)
    
    connection = get_db_connection()
    if not connection:
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                      message="Database connection error", success=False)
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if email exists
        cursor.execute("SELECT id, full_name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate a password reset token (this could be implemented using a real token system)
            reset_token = secrets.token_hex(16)
            reset_expiry = datetime.utcnow() + timedelta(hours=1)
            
            cursor.execute("""
                INSERT INTO password_resets (user_id, reset_token, reset_expiry)
                VALUES (%s, %s, %s)
            """, (user['id'], reset_token, reset_expiry))
            connection.commit()

            # Send an email (this is a placeholder and should be replaced with actual email sending logic)
            print(f"Password reset link for {user['full_name']} is: /reset-password/{reset_token}")
            
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                          message="Password reset link has been sent to your email", success=True)
        else:
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                          message="No account found with that email", success=False)
        
    except Error as e:
        print(f"Error resetting password: {e}")
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                      message="An error occurred while resetting your password", success=False)
    finally:
        connection.close()

@app.route('/reset-password/<reset_token>', methods=['GET', 'POST'])
def reset_password_with_token(reset_token):
    connection = get_db_connection()
    if not connection:
        return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                      message="Database connection error", success=False)
    
    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if new_password != confirm_password:
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                          message="Passwords do not match", success=False)
        
        if len(new_password) < 8:
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                          message="Password must be at least 8 characters", success=False)
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if reset token is valid
            cursor.execute("""
                SELECT pr.user_id, u.email 
                FROM password_resets pr 
                JOIN users u ON pr.user_id = u.id
                WHERE pr.reset_token = %s AND pr.reset_expiry > NOW()
            """, (reset_token,))
            
            reset_data = cursor.fetchone()
            
            if reset_data:
                hashed_password = hash_password(new_password)
                
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, reset_data['user_id']))
                connection.commit()

                # Invalidate the reset token
                cursor.execute("DELETE FROM password_resets WHERE reset_token = %s", (reset_token,))
                connection.commit()

                return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                              message="Your password has been reset successfully. Please log in.", success=True)
            else:
                return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                              message="Invalid or expired reset token", success=False)
        except Error as e:
            print(f"Error resetting password with token: {e}")
            return render_template_string(ADVANCED_LOGIN_TEMPLATE, 
                                          message="An error occurred while resetting your password", success=False)
        finally:
            connection.close()

    return render_template_string('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password</title>
</head>
<body>
    <h1>Reset Password</h1>
    <form method="POST" action="/reset-password/{{ reset_token }}">
        <label for="password">New Password</label>
        <input type="password" id="password" name="password" required>
        <label for="confirm_password">Confirm Password</label>
        <input type="password" id="confirm_password" name="confirm_password" required>
        <button type="submit">Submit</button>
    </form>
</body>
</html>''', reset_token=reset_token)

if __name__ == '__main__':
    check_database()  # Ensure the database connection is successful
    app.run(debug=True)
