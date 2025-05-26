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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt-secret-key-change-this')
JWT_ALGORITHM = 'HS256'

# Email Configuration (for password reset)
EMAIL_CONFIG = {
    'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.environ.get('SMTP_PORT', '587')),
    'email': os.environ.get('EMAIL_USER', 'your-email@gmail.com'),
    'password': os.environ.get('EMAIL_PASSWORD', 'your-app-password')
}

# Database configuration - UPDATE THESE WITH YOUR ACTUAL DATABASE CREDENTIALS
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'database': 'sql12781272',
    'user': 'sql12781272',
    'password': '7qPLvwZDC4',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'use_unicode': True,
    'autocommit': False  # Changed to False for better transaction control
}

# HTML Templates
ADVANCED_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Login System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        
        .form-toggle {
            display: flex;
            margin-bottom: 2rem;
            border-radius: 5px;
            overflow: hidden;
            border: 1px solid #ddd;
        }
        
        .toggle-btn {
            flex: 1;
            padding: 0.75rem;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .toggle-btn.active {
            background: #667eea;
            color: white;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        
        input[type="text"], input[type="email"], input[type="password"] {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus, input[type="email"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .checkbox-group input[type="checkbox"] {
            margin-right: 0.5rem;
        }
        
        .submit-btn {
            width: 100%;
            padding: 0.75rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .submit-btn:hover {
            background: #5a6fd8;
        }
        
        .message {
            padding: 0.75rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .forgot-password {
            text-align: center;
            margin-top: 1rem;
        }
        
        .forgot-password a {
            color: #667eea;
            text-decoration: none;
        }
        
        .forgot-password a:hover {
            text-decoration: underline;
        }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-toggle">
            <button class="toggle-btn active" onclick="showLogin()">Sign In</button>
            <button class="toggle-btn" onclick="showRegister()">Sign Up</button>
        </div>
        
        {% if message %}
            <div class="message {{ 'success' if success else 'error' }}">
                {{ message }}
            </div>
        {% endif %}
        
        <!-- Login Form -->
        <form id="loginForm" method="POST" action="/login">
            <div class="form-group">
                <label for="username">Username or Email</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="remember_me" name="remember_me">
                <label for="remember_me">Remember me</label>
            </div>
            
            <button type="submit" class="submit-btn">Sign In</button>
            
            <div class="forgot-password">
                <a href="/forgot-password">Forgot your password?</a>
            </div>
        </form>
        
        <!-- Registration Form -->
        <form id="registerForm" method="POST" action="/register" class="hidden">
            <div class="form-group">
                <label for="reg_full_name">Full Name</label>
                <input type="text" id="reg_full_name" name="full_name" required>
            </div>
            
            <div class="form-group">
                <label for="reg_username">Username</label>
                <input type="text" id="reg_username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="reg_email">Email</label>
                <input type="email" id="reg_email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="reg_password">Password</label>
                <input type="password" id="reg_password" name="password" required>
            </div>
            
            <div class="form-group">
                <label for="reg_confirm_password">Confirm Password</label>
                <input type="password" id="reg_confirm_password" name="confirm_password" required>
            </div>
            
            <button type="submit" class="submit-btn">Create Account</button>
        </form>
    </div>
    
    <script>
        function showLogin() {
            document.getElementById('loginForm').classList.remove('hidden');
            document.getElementById('registerForm').classList.add('hidden');
            document.querySelectorAll('.toggle-btn')[0].classList.add('active');
            document.querySelectorAll('.toggle-btn')[1].classList.remove('active');
        }
        
        function showRegister() {
            document.getElementById('loginForm').classList.add('hidden');
            document.getElementById('registerForm').classList.remove('hidden');
            document.querySelectorAll('.toggle-btn')[0].classList.remove('active');
            document.querySelectorAll('.toggle-btn')[1].classList.add('active');
        }
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Secure Auth System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 1.5rem;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.3s;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        .welcome-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .sessions-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .sessions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        .sessions-table th,
        .sessions-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .sessions-table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        
        .status-active {
            color: #28a745;
            font-weight: 500;
        }
        
        .status-inactive {
            color: #dc3545;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Secure Dashboard</h1>
        <div class="user-info">
            <span>Welcome, {{ user.full_name }}!</span>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="welcome-card">
            <h2>Welcome to your secure dashboard!</h2>
            <p>You are successfully logged in as <strong>{{ user.username }}</strong></p>
            <p>Email: {{ user.email or 'Not provided' }}</p>
            <p>Last login: {{ user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'First time login' }}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ sessions|length }}</div>
                <div>Active Sessions</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{{ user.failed_attempts or 0 }}</div>
                <div>Failed Login Attempts</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">
                    {{ user.created_at.strftime('%b %d, %Y') if user.created_at else 'Unknown' }}
                </div>
                <div>Member Since</div>
            </div>
        </div>
        
        <div class="sessions-card">
            <h3>Active Sessions</h3>
            {% if sessions %}
                <table class="sessions-table">
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Created</th>
                            <th>Expires</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for session in sessions %}
                        <tr>
                            <td>{{ session.id }}</td>
                            <td>{{ session.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td>{{ session.expires_at.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td>
                                {% if session.is_active %}
                                    <span class="status-active">Active</span>
                                {% else %}
                                    <span class="status-inactive">Inactive</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>No active sessions found.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

RESET_PASSWORD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 500;
        }
        input[type="email"], input[type="password"] {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        .submit-btn {
            width: 100%;
            padding: 0.75rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            margin-bottom: 1rem;
        }
        .submit-btn:hover {
            background: #5a6fd8;
        }
        .back-link {
            text-align: center;
        }
        .back-link a {
            color: #667eea;
            text-decoration: none;
        }
        .message {
            padding: 0.75rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            text-align: center;
        }
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ 'Set New Password' if token else 'Reset Password' }}</h1>
        
        {% if message %}
            <div class="message {{ 'success' if success else 'error' }}">
                {{ message }}
            </div>
        {% endif %}
        
        {% if token %}
            <form method="POST" action="/reset-password/{{ token }}">
                <div class="form-group">
                    <label for="password">New Password</label>
                    <input type="password" id="password" name="password" required minlength="8">
                </div>
                <div class="form-group">
                    <label for="confirm_password">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" required>
                </div>
                <button type="submit" class="submit-btn">Update Password</button>
            </form>
        {% else %}
            <p>Please enter your email to receive a password reset link.</p>
            <form method="POST" action="/reset-password">
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <button type="submit" class="submit-btn">Send Reset Link</button>
            </form>
        {% endif %}
        
        <div class="back-link">
            <a href="/login">Back to Login</a>
        </div>
    </div>
</body>
</html>
'''

# Database connection function - Simplified without connection pooling
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
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
                    SELECT us.*, u.username, u.full_name, u.email, u.created_at, u.last_login, u.failed_attempts
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
            else:
                return redirect(url_for('login'))
            
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

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

def generate_reset_token():
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)

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
            INSERT INTO user_sessions (user_id, session_token, expires_at, is_active)
            VALUES (%s, %s, %s, %s)
        """, (user_id, token, expires_at, True))
        
        connection.commit()
        cursor.close()
        return True
        
    except Error as e:
        print(f"Session creation error: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def send_reset_email(email, reset_token):
    """Send password reset email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = email
        msg['Subject'] = "Password Reset Request"
        
        reset_link = f"{request.host_url}reset-password/{reset_token}"
        
        body = f"""
        Hello,
        
        You have requested a password reset. Click the link below to reset your password:
        
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you did not request this reset, please ignore this email.
        
        Best regards,
        Your App Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def log_login_attempt(username, success):
    """Log login attempts (basic implementation)"""
    print(f"Login attempt - Username: {username}, Success: {success}, IP: {get_client_ip()}")

# Initialize database tables if they don't exist
def init_database():
    """Initialize database tables"""
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                failed_attempts INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        """)
        
        # Create user_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create password_resets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                reset_token VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        connection.commit()
        cursor.close()
        print("✅ Database tables initialized successfully")
        return True
        
    except Error as e:
        print(f"❌ Database initialization error: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

# Check database connection
def check_database():
    """Check if database connection works"""
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
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
                # Reset failed attempts on successful login
                cursor.execute("UPDATE users SET last_login = NOW(), failed_attempts = 0 WHERE id = %s", (user['id'],))
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
                # Increment failed attempts
                if user:
                    cursor.execute("UPDATE users SET failed_attempts = failed_attempts + 1 WHERE id = %s", (user['id'],))
                    connection.commit()
                
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
        connection.rollback()
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
            connection.rollback()
        finally:
            connection.close()
    
    # Remove token from cookies and redirect to login
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('auth_token')
    return response

@app.route('/forgot-password')
def forgot_password():
    return render_template_string(RESET_PASSWORD_TEMPLATE)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                        message="Please enter your email address", success=False)
        
        connection = get_db_connection()
        if not connection:
            return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                        message="Database connection error", success=False)
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = %s AND is_active = TRUE", (email,))
            user = cursor.fetchone()
            
            if user:
                # Generate reset token
                reset_token = generate_reset_token()
                expires_at = datetime.now() + timedelta(hours=1)
                
                # Store reset token
                cursor.execute("""
                    INSERT INTO password_resets (user_id, reset_token, expires_at)
                    VALUES (%s, %s, %s)
                """, (user['id'], reset_token, expires_at))
                
                connection.commit()
                
                # Send reset email (simplified - in production, use proper email service)
                if send_reset_email(email, reset_token):
                    return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                                message="Password reset link sent to your email", success=True)
                else:
                    return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                                message="Failed to send reset email. Please try again.", success=False)
            else:
                # Don't reveal if email exists or not for security
                return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                            message="If the email exists, a reset link has been sent", success=True)
                
        except Error as e:
            print(f"Reset password error: {e}")
            connection.rollback()
            return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                        message="An error occurred. Please try again.", success=False)
        finally:
            cursor.close()
            connection.close()
    
    return render_template_string(RESET_PASSWORD_TEMPLATE)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_confirm(token):
    connection = get_db_connection()
    if not connection:
        return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                    message="Database connection error", success=False, token=token)
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verify reset token
        cursor.execute("""
            SELECT pr.*, u.email FROM password_resets pr
            JOIN users u ON pr.user_id = u.id
            WHERE pr.reset_token = %s AND pr.expires_at > NOW() AND pr.used = FALSE
        """, (token,))
        
        reset_data = cursor.fetchone()
        
        if not reset_data:
            return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                        message="Invalid or expired reset token", success=False)
        
        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not password or not confirm_password:
                return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                            message="Please fill in all fields", success=False, token=token)
            
            if password != confirm_password:
                return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                            message="Passwords do not match", success=False, token=token)
            
            if len(password) < 8:
                return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                            message="Password must be at least 8 characters", success=False, token=token)
            
            # Update password
            password_hash = hash_password(password)
            
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                         (password_hash, reset_data['user_id']))
            
            # Mark reset token as used
            cursor.execute("UPDATE password_resets SET used = TRUE WHERE id = %s", 
                         (reset_data['id'],))
            
            connection.commit()
            
            return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                        message="Password updated successfully! You can now sign in.", success=True)
        
        return render_template_string(RESET_PASSWORD_TEMPLATE, token=token)
        
    except Error as e:
        print(f"Reset password confirm error: {e}")
        connection.rollback()
        return render_template_string(RESET_PASSWORD_TEMPLATE, 
                                    message="An error occurred. Please try again.", success=False, token=token)
    finally:
        cursor.close()
        connection.close()

# API Routes for additional functionality
@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile():
    """Get current user profile"""
    user = request.current_user
    return jsonify({
        'id': user['user_id'],
        'username': user['username'],
        'email': user['email'],
        'full_name': user['full_name'],
        'created_at': user['created_at'].isoformat() if user['created_at'] else None,
        'last_login': user['last_login'].isoformat() if user['last_login'] else None
    })

@app.route('/api/user/sessions', methods=['GET'])
@token_required
def get_user_sessions():
    """Get user's active sessions"""
    user = request.current_user
    connection = get_db_connection()
    
    if not connection:
        return jsonify({'error': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, created_at, expires_at, is_active
            FROM user_sessions 
            WHERE user_id = %s AND is_active = TRUE AND expires_at > NOW()
            ORDER BY created_at DESC
        """, (user['user_id'],))
        
        sessions = cursor.fetchall()
        
        # Convert datetime objects to strings
        for session in sessions:
            session['created_at'] = session['created_at'].isoformat()
            session['expires_at'] = session['expires_at'].isoformat()
        
        return jsonify({'sessions': sessions})
        
    except Error as e:
        print(f"Error fetching sessions: {e}")
        return jsonify({'error': 'Failed to fetch sessions'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/user/logout-all', methods=['POST'])
@token_required
def logout_all_sessions():
    """Logout from all sessions"""
    user = request.current_user
    connection = get_db_connection()
    
    if not connection:
        return jsonify({'error': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE user_sessions SET is_active = FALSE WHERE user_id = %s", (user['user_id'],))
        connection.commit()
        
        # Remove current session cookie
        response = make_response(jsonify({'message': 'Logged out from all sessions'}))
        response.delete_cookie('auth_token')
        return response
        
    except Error as e:
        print(f"Error logging out all sessions: {e}")
        connection.rollback()
        return jsonify({'error': 'Failed to logout all sessions'}), 500
    finally:
        cursor.close()
        connection.close()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Page Not Found</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            .error-container { max-width: 500px; margin: 0 auto; }
            .error-code { font-size: 72px; color: #667eea; margin-bottom: 20px; }
            .error-message { font-size: 24px; margin-bottom: 30px; }
            .back-link { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">404</div>
            <div class="error-message">Page Not Found</div>
            <a href="/login" class="back-link">Return to Login</a>
        </div>
    </body>
    </html>
    '''), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Internal Server Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            .error-container { max-width: 500px; margin: 0 auto; }
            .error-code { font-size: 72px; color: #dc3545; margin-bottom: 20px; }
            .error-message { font-size: 24px; margin-bottom: 30px; }
            .back-link { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-code">500</div>
            <div class="error-message">Internal Server Error</div>
            <a href="/login" class="back-link">Return to Login</a>
        </div>
    </body>
    </html>
    '''), 500

# Main execution
if __name__ == '__main__':
    print("🚀 Starting Flask Authentication System...")
    
    # Check database connection
    if not check_database():
        print("❌ Failed to connect to database. Please check your database configuration.")
        exit(1)
    
    # Initialize database tables
    if not init_database():
        print("❌ Failed to initialize database tables.")
        exit(1)
    
    print("✅ Database connection and initialization successful!")
    print("📧 Note: Email functionality requires proper SMTP configuration")
    print("🔐 Remember to change SECRET_KEY and JWT_SECRET in production")
    print("🌐 Server starting on http://localhost:5000")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)