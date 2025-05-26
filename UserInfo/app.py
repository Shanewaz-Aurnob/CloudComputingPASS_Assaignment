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

# Database configuration
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'database': 'sql12781272',
    'user': 'sql12781272',  # Replace with your MySQL username
    'password': '7qPLvwZDC4'  # Replace with your MySQL password
}

# Database connection function with connection pooling
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG,
            autocommit=True,
            pool_name='auth_pool',
            pool_size=5
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
                        <td>{{ session.device_info or 'Unknown Device' }}</td>
                        <td>{{ session.ip_address }}</td>
                        <td>{{ session.location or 'Unknown' }}</td>
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

# Initialize database tables
def init_database():
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check if users table exists and has correct structure
        cursor.execute("SHOW TABLES LIKE 'users'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if password_hash column exists
            cursor.execute("SHOW COLUMNS FROM users LIKE 'password_hash'")
            column_exists = cursor.fetchone()
            
            if not column_exists:
                print("🔧 Adding missing password_hash column to users table...")
                try:
                    # Try to add the column (might fail if 'password' column exists)
                    cursor.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
                    
                    # If there's an old 'password' column, migrate data
                    cursor.execute("SHOW COLUMNS FROM users LIKE 'password'")
                    old_password_exists = cursor.fetchone()
                    
                    if old_password_exists:
                        print("🔄 Migrating password data...")
                        # Get all users with old password format
                        cursor.execute("SELECT id, password FROM users WHERE password IS NOT NULL")
                        users_to_migrate = cursor.fetchall()
                        
                        for user_id, old_password in users_to_migrate:
                            # Hash the old password and update
                            new_hash = hash_password(old_password)
                            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
                        
                        # Drop the old password column
                        cursor.execute("ALTER TABLE users DROP COLUMN password")
                        print("✅ Password migration completed")
                        
                except Error as alter_error:
                    print(f"⚠️  Column modification error: {alter_error}")
        
        # Create users table with correct structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        """)
        
        # User sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_token VARCHAR(512) NOT NULL,
                ip_address VARCHAR(45),
                device_info TEXT,
                location VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_token (session_token),
                INDEX idx_user_active (user_id, is_active)
            )
        """)
        
        # Login attempts table for security
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ip_address VARCHAR(45) NOT NULL,
                username VARCHAR(50),
                success BOOLEAN DEFAULT FALSE,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_ip_time (ip_address, attempted_at)
            )
        """)
        
        connection.commit()
        cursor.close()
        
        print("✅ Database schema verified and updated")
        return True
        
    except Error as e:
        print(f"❌ Database initialization error: {e}")
        return False
    finally:
        connection.close()

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_jwt_token(user_id, remember_me=False):
    expiry = datetime.utcnow() + timedelta(days=30 if remember_me else 1)
    payload = {
        'user_id': user_id,
        'exp': expiry,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def create_user_session(user_id, token, remember_me=False):
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
            INSERT INTO user_sessions (user_id, session_token, ip_address, device_info, expires_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, token, get_client_ip(), request.headers.get('User-Agent', ''), expires_at))
        
        connection.commit()
        cursor.close()
        return True
        
    except Error as e:
        print(f"Session creation error: {e}")
        return False
    finally:
        connection.close()

def log_login_attempt(username, success):
    connection = get_db_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO login_attempts (ip_address, username, success)
            VALUES (%s, %s, %s)
        """, (get_client_ip(), username, success))
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Login attempt logging error: {e}")
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
            
            # First check what columns exist in the users table
            cursor.execute("SHOW COLUMNS FROM users")
            columns = [row['Field'] for row in cursor.fetchall()]
            
            # Use appropriate password column
            password_column = 'password_hash' if 'password_hash' in columns else 'password'
            
            cursor.execute(f"""
                SELECT * FROM users 
                WHERE (username = %s OR email = %s) AND is_active = TRUE
            """, (username, username))
            
            user = cursor.fetchone()
            
            if user:
                # Check password based on available column
                password_valid = False
                if password_column == 'password_hash' and password_column in user:
                    password_valid = verify_password(password, user[password_column])
                elif 'password' in user:
                    # Handle plain text password (less secure, for backward compatibility)
                    password_valid = (password == user['password'])
                    
                    # If login successful with plain text, upgrade to hashed password
                    if password_valid and 'password_hash' in columns:
                        new_hash = hash_password(password)
                        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                                     (new_hash, user['id']))
                        connection.commit()
                
                if password_valid:
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
        
        # Check what columns exist in the users table
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [row[0] for row in cursor.fetchall()]
        
        # Create new user with proper column structure
        password_hash = hash_password(password)
        
        if 'password_hash' in columns:
            cursor.execute("""
                INSERT INTO users (username, email, full_name, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (username, email, full_name, password_hash))
        else:
            # Fallback for older schema (less secure)
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
            print(f"Dashboard error: {e}")
        finally:
            connection.close()
    
    return render_template_string(DASHBOARD_TEMPLATE, user=user, sessions=sessions)

@app.route('/logout')
def logout():
    token = request.cookies.get('auth_token')
    
    if token:
        # Deactivate session in database
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE user_sessions 
                    SET is_active = FALSE 
                    WHERE session_token = %s
                """, (token,))
                connection.commit()
                cursor.close()
            except Error as e:
                print(f"Logout error: {e}")
            finally:
                connection.close()
    
    # Clear cookie and redirect
    response = make_response(redirect(url_for('login')))
    response.set_cookie('auth_token', '', expires=0)
    return response

@app.route('/api/user-info')
@token_required
def api_user_info():
    """API endpoint to get current user information"""
    return jsonify({
        'user_id': request.current_user['user_id'],
        'username': request.current_user['username'],
        'full_name': request.current_user['full_name'],
        'last_login': request.current_user.get('last_login')
    })

@app.route('/api/sessions')
@token_required
def api_sessions():
    """API endpoint to get user's active sessions"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, ip_address, device_info, location, created_at, expires_at
            FROM user_sessions 
            WHERE user_id = %s AND is_active = TRUE AND expires_at > NOW()
            ORDER BY created_at DESC
        """, (request.current_user['user_id'],))
        
        sessions = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects to strings for JSON serialization
        for session in sessions:
            if session['created_at']:
                session['created_at'] = session['created_at'].isoformat()
            if session['expires_at']:
                session['expires_at'] = session['expires_at'].isoformat()
        
        return jsonify({'sessions': sessions})
        
    except Error as e:
        print(f"API sessions error: {e}")
        return jsonify({'error': 'Failed to fetch sessions'}), 500
    finally:
        connection.close()

@app.route('/api/revoke-session/<int:session_id>', methods=['POST'])
@token_required
def api_revoke_session(session_id):
    """API endpoint to revoke a specific session"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE user_sessions 
            SET is_active = FALSE 
            WHERE id = %s AND user_id = %s
        """, (session_id, request.current_user['user_id']))
        
        if cursor.rowcount > 0:
            connection.commit()
            cursor.close()
            return jsonify({'success': True, 'message': 'Session revoked successfully'})
        else:
            cursor.close()
            return jsonify({'error': 'Session not found or access denied'}), 404
            
    except Error as e:
        print(f"API revoke session error: {e}")
        return jsonify({'error': 'Failed to revoke session'}), 500
    finally:
        connection.close()

@app.route('/forgot-password')
def forgot_password():
    # Simple forgot password page (placeholder)
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forgot Password - SecureAuth</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 400px; 
                margin: 100px auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: 600; }
            input { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #e5e7eb; 
                border-radius: 8px; 
                font-size: 16px;
            }
            button { 
                width: 100%; 
                padding: 12px; 
                background: #667eea; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                font-size: 16px; 
                cursor: pointer;
            }
            button:hover { background: #5a67d8; }
            .back-link { text-align: center; margin-top: 20px; }
            .back-link a { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Reset Password</h2>
            <p>Enter your email address and we'll send you a reset link.</p>
            <form>
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" required>
                </div>
                <button type="submit">Send Reset Link</button>
            </form>
            <div class="back-link">
                <a href="/login">← Back to Sign In</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.errorhandler(404)
def not_found(error):
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>404 - Page Not Found</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin-top: 100px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                max-width: 500px;
                margin: 0 auto;
            }
            h1 { font-size: 4rem; margin-bottom: 20px; }
            p { font-size: 1.2rem; margin-bottom: 30px; }
            a { 
                color: white; 
                text-decoration: none; 
                background: rgba(255,255,255,0.2);
                padding: 12px 24px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.3);
            }
            a:hover { background: rgba(255,255,255,0.3); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>404</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/login">Go to Login</a>
        </div>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def internal_error(error):
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>500 - Internal Server Error</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin-top: 100px;
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                max-width: 500px;
                margin: 0 auto;
            }
            h1 { font-size: 4rem; margin-bottom: 20px; }
            p { font-size: 1.2rem; margin-bottom: 30px; }
            a { 
                color: white; 
                text-decoration: none; 
                background: rgba(255,255,255,0.2);
                padding: 12px 24px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.3);
            }
            a:hover { background: rgba(255,255,255,0.3); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>500</h1>
            <p>Something went wrong on our end. Please try again later.</p>
            <a href="/login">Go to Login</a>
        </div>
    </body>
    </html>
    ''', 500

# Application initialization
if __name__ == '__main__':
    print("🔐 Initializing SecureAuth System...")
    
    # Force database initialization
    print("🔧 Checking database schema...")
    if init_database():
        print("✅ Database initialized successfully")
        print("🚀 Starting Flask application...")
        print("📍 Access the application at: http://localhost:5000")
        print("🛡️  Features enabled:")
        print("   • JWT Token Authentication")
        print("   • Password Hashing with bcrypt")
        print("   • Session Management")
        print("   • Login Attempt Logging")
        print("   • Responsive UI Design")
        print("   • RESTful API Endpoints")
        print("   • Database Schema Auto-Migration")
        
        # Create a test user if none exist
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM users")
                user_count = cursor.fetchone()[0]
                
                if user_count == 0:
                    print("👤 Creating default admin user...")
                    admin_password = "admin123"
                    admin_hash = hash_password(admin_password)
                    
                    # Check column structure
                    cursor.execute("SHOW COLUMNS FROM users")
                    columns = [row[0] for row in cursor.fetchall()]
                    
                    if 'password_hash' in columns:
                        cursor.execute("""
                            INSERT INTO users (username, email, full_name, password_hash)
                            VALUES (%s, %s, %s, %s)
                        """, ('admin', 'admin@example.com', 'Administrator', admin_hash))
                    else:
                        cursor.execute("""
                            INSERT INTO users (username, email, full_name, password)
                            VALUES (%s, %s, %s, %s)
                        """, ('admin', 'admin@example.com', 'Administrator', admin_hash))
                    
                    connection.commit()
                    print("✅ Default user created - Username: admin, Password: admin123")
                
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"⚠️  Could not create default user: {e}")
        
        # Run the application
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to initialize database. Please check your MySQL connection.")
        print("🔍 Troubleshooting steps:")
        print("   1. Verify your database credentials in DB_CONFIG")
        print("   2. Ensure MySQL server is running")
        print("   3. Check if the database exists")
        print("   4. Verify network connectivity to the database server")