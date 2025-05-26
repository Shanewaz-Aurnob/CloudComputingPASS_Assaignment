from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
import bcrypt
import secrets
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database configuration
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'database': 'sql12781272',
    'user': 'sql12781272',  # Replace with your MySQL username
    'password': '7qPLvwZDC4'  # Replace with your MySQL password
}

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# HTML Template for login/registration
LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Authentication System</title>
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
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .auth-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            width: 100%;
            max-width: 400px;
        }

        .auth-header {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .auth-header h1 {
            font-size: 2rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .auth-content {
            padding: 40px;
        }

        .tab-buttons {
            display: flex;
            margin-bottom: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 5px;
        }

        .tab-button {
            flex: 1;
            padding: 12px;
            border: none;
            background: transparent;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .tab-button.active {
            background: #11998e;
            color: white;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #495057;
        }

        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus {
            border-color: #11998e;
            outline: none;
            box-shadow: 0 0 0 3px rgba(17, 153, 142, 0.2);
        }

        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(17, 153, 142, 0.4);
        }

        .message {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .form-container {
            display: none;
        }

        .form-container.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="auth-header">
            <h1>🔐 User Authentication</h1>
            <p>Secure Login & Registration System</p>
        </div>
        
        <div class="auth-content">
            <div class="tab-buttons">
                <button class="tab-button active" onclick="showForm('login')">Login</button>
                <button class="tab-button" onclick="showForm('register')">Register</button>
            </div>

            <div id="message"></div>

            <!-- Login Form -->
            <div id="login-form" class="form-container active">
                <form onsubmit="submitLogin(event)">
                    <div class="form-group">
                        <label for="login-username">Username</label>
                        <input type="text" id="login-username" required>
                    </div>
                    <div class="form-group">
                        <label for="login-password">Password</label>
                        <input type="password" id="login-password" required>
                    </div>
                    <button type="submit" class="btn">Login</button>
                </form>
            </div>

            <!-- Registration Form -->
            <div id="register-form" class="form-container">
                <form onsubmit="submitRegister(event)">
                    <div class="form-group">
                        <label for="reg-username">Username</label>
                        <input type="text" id="reg-username" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-email">Email</label>
                        <input type="email" id="reg-email" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-fullname">Full Name</label>
                        <input type="text" id="reg-fullname" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-password">Password</label>
                        <input type="password" id="reg-password" required>
                    </div>
                    <div class="form-group">
                        <label for="reg-confirm">Confirm Password</label>
                        <input type="password" id="reg-confirm" required>
                    </div>
                    <button type="submit" class="btn">Register</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        function showForm(formType) {
            // Hide all forms
            document.querySelectorAll('.form-container').forEach(form => {
                form.classList.remove('active');
            });
            
            // Remove active class from all buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected form and activate button
            document.getElementById(formType + '-form').classList.add('active');
            event.target.classList.add('active');
            
            // Clear messages
            document.getElementById('message').innerHTML = '';
        }

        function showMessage(message, isError = false) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="message ${isError ? 'error' : 'success'}">${message}</div>`;
        }

        async function submitLogin(event) {
            event.preventDefault();
            
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showMessage('Login successful! Redirecting...');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    showMessage(data.error, true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
            }
        }

        async function submitRegister(event) {
            event.preventDefault();
            
            const username = document.getElementById('reg-username').value;
            const email = document.getElementById('reg-email').value;
            const fullname = document.getElementById('reg-fullname').value;
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('reg-confirm').value;
            
            if (password !== confirmPassword) {
                showMessage('Passwords do not match!', true);
                return;
            }
            
            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, email, full_name: fullname, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showMessage('Registration successful! You can now login.');
                    showForm('login');
                } else {
                    showMessage(data.error, true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
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
    <title>Dashboard - User Authentication System</title>
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
            padding: 20px;
        }

        .dashboard-container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .dashboard-header {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .dashboard-content {
            padding: 40px;
        }

        .user-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .info-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #11998e;
        }

        .info-label {
            font-weight: 600;
            color: #6c757d;
            font-size: 0.9rem;
        }

        .info-value {
            font-size: 1.1rem;
            color: #495057;
            margin-top: 5px;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }

        .btn-logout {
            background: #dc3545;
            color: white;
        }

        .btn-logout:hover {
            background: #c82333;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-header">
            <div>
                <h1>Welcome, {{ user.full_name }}!</h1>
                <p>User Dashboard</p>
            </div>
            <a href="/logout" class="btn btn-logout">Logout</a>
        </div>
        
        <div class="dashboard-content">
            <div class="user-info">
                <h2 style="margin-bottom: 20px; color: #495057;">Your Account Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Username</div>
                        <div class="info-value">{{ user.username }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Email</div>
                        <div class="info-value">{{ user.email }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Full Name</div>
                        <div class="info-value">{{ user.full_name }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Member Since</div>
                        <div class="info-value">{{ user.created_at.strftime('%B %d, %Y') }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Last Login</div>
                        <div class="info-value">{{ user.last_login.strftime('%B %d, %Y at %I:%M %p') if user.last_login else 'First time' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Account Status</div>
                        <div class="info-value">{{ 'Active' if user.is_active else 'Inactive' }}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE)
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if account is locked
        cursor.execute("""
            SELECT * FROM users 
            WHERE username = %s AND is_active = TRUE
        """, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check if account is temporarily locked
        if user['locked_until'] and user['locked_until'] > datetime.now():
            return jsonify({'error': 'Account temporarily locked due to multiple failed attempts'}), 423
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Reset failed attempts and update last login
            cursor.execute("""
                UPDATE users 
                SET failed_attempts = 0, locked_until = NULL, last_login = NOW()
                WHERE id = %s
            """, (user['id'],))
            
            connection.commit()
            
            # Create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            return jsonify({'message': 'Login successful', 'user': user['username']})
        else:
            # Increment failed attempts
            failed_attempts = user['failed_attempts'] + 1
            locked_until = None
            
            # Lock account after 5 failed attempts for 30 minutes
            if failed_attempts >= 5:
                locked_until = datetime.now() + timedelta(minutes=30)
            
            cursor.execute("""
                UPDATE users 
                SET failed_attempts = %s, locked_until = %s
                WHERE id = %s
            """, (failed_attempts, locked_until, user['id']))
            
            connection.commit()
            
            if locked_until:
                return jsonify({'error': 'Account locked due to multiple failed attempts. Try again in 30 minutes.'}), 423
            else:
                return jsonify({'error': f'Invalid password. {5 - failed_attempts} attempts remaining.'}), 401
    
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    full_name = data.get('full_name')
    password = data.get('password')
    
    if not all([username, email, full_name, password]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({'error': 'Username already exists'}), 409
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (username, password, email, full_name)
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_password, email, full_name))
        
        connection.commit()
        
        return jsonify({'message': 'User registered successfully'})
    
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/dashboard')
@login_required
def dashboard():
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            session.clear()
            return redirect(url_for('login'))
        
        return render_template_string(DASHBOARD_TEMPLATE, user=user)
    
    except Error as e:
        return f"Database error: {str(e)}", 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)