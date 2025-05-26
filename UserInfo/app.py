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
    'host': 'localhost',
    'database': 'user_auth_db',
    'user': 'your_username',  # Replace with your MySQL username
    'password': 'your_password'  # Replace with your MySQL password
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
            box-shadow: 0