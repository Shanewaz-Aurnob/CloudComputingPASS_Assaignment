from flask import Flask, render_template_string
import os

app = Flask(__name__)

# HTML Template with embedded CSS and styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Computing Assignment - CSE-814</title>
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 2rem;
            color: #2c3e50;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            position: relative;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 3rem 2rem;
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.15"/><circle cx="20" cy="80" r="0.5" fill="white" opacity="0.15"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }

        .header h1 {
            font-family: 'Merriweather', serif;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 1;
        }

        .header h2 {
            font-size: 1.3rem;
            font-weight: 300;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        .content {
            padding: 3rem 2rem;
        }

        .instructor-student-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border: 1px solid #e8ecf4;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }

        .card-label {
            font-size: 0.9rem;
            font-weight: 500;
            color: #7c3aed;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1rem;
        }

        .profile-section {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .profile-image {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 2rem;
            font-weight: bold;
            flex-shrink: 0;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            overflow: hidden;
        }

        .profile-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 50%;
        }

        .profile-info h3 {
            font-family: 'Merriweather', serif;
            font-size: 1.3rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }

        .profile-info p {
            color: #64748b;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 0.3rem;
        }

        .problems-section {
            background: #f8fafc;
            border-radius: 15px;
            padding: 2.5rem;
            border: 1px solid #e2e8f0;
        }

        .problems-title {
            font-family: 'Merriweather', serif;
            font-size: 1.8rem;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
        }

        .problems-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
        }

        .problems-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .problem-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 2px solid #e2e8f0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .problem-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }

        .problem-card:hover {
            border-color: #3b82f6;
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(59, 130, 246, 0.15);
        }

        .problem-card:hover::before {
            transform: scaleX(1);
        }

        .problem-number {
            font-weight: 700;
            font-size: 1.1rem;
            color: #7c3aed;
            margin-bottom: 0.8rem;
        }

        .problem-link {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .problem-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            background: linear-gradient(135deg, #5a67d8, #6b46c1);
        }

        .footer {
            text-align: center;
            padding: 2rem;
            border-top: 1px solid #e2e8f0;
            background: #f8fafc;
        }

        .university-logo {
            width: 60px;
            height: 60px;
            margin: 0 auto 1rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.5rem;
        }

        .footer p {
            color: #64748b;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .instructor-student-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .profile-section {
                flex-direction: column;
                text-align: center;
            }
            
            .problems-grid {
                grid-template-columns: 1fr;
            }
            
            body {
                padding: 1rem;
            }
        }

        .animate-fadeIn {
            animation: fadeIn 1s ease-out;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .status-indicator {
            position: absolute;
            top: 1rem;
            right: 1rem;
            width: 12px;
            height: 12px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container animate-fadeIn">
        <div class="header">
            <div class="status-indicator" title="Live Application"></div>
            <h1>Cloud Computing (Programs on PAAS) Assignment</h1>
            <h2>Course Code: CSE-814</h2>
        </div>
        
        <div class="content">
            <div class="instructor-student-grid">
                <div class="card">
                    <div class="card-label">Submitted To:</div>
                    <div class="profile-section">
                        <div class="profile-image">
                            <!-- Replace with actual image URL -->
                            <img src="https://via.placeholder.com/80x80/667eea/ffffff?text=DR" alt="Dr. Atiqur Rahman" onerror="this.style.display='none'; this.parentElement.innerHTML='DR';">
                        </div>
                        <div class="profile-info">
                            <h3>Dr. Atiqur Rahman</h3>
                            <p>Associate Professor</p>
                            <p>Department of Computer Science and Engineering</p>
                            <p>University of Chittagong</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-label">Submitted From:</div>
                    <div class="profile-section">
                        <div class="profile-image">
                            <!-- Replace with actual image URL -->
                            <img src="https://via.placeholder.com/80x80/667eea/ffffff?text=SA" alt="Shanewaz Aurnob" onerror="this.style.display='none'; this.parentElement.innerHTML='SA';">
                        </div>
                        <div class="profile-info">
                            <h3>Shanewaz Aurnob</h3>
                            <p>Student ID: 20701066</p>
                            <p>Department of Computer Science and Engineering</p>
                            <p>University of Chittagong</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="problems-section">
                <h2 class="problems-title">Assignment Problems</h2>
                <div class="problems-grid">
                    <div class="problem-card">
                        <div class="problem-number">Problem 1: Even Number Generator</div>
                        <a href="https://evennumbergenerator-f14k.onrender.com/" class="problem-link" target="_blank">
                            View Solution →
                        </a>
                    </div>
                    
                    <div class="problem-card">
                        <div class="problem-number">Problem 2: Basic Application</div>
                        <a href="https://cloudcomputingpass-assaignment.onrender.com/" class="problem-link" target="_blank">
                            View Solution →
                        </a>
                    </div>
                    
                    <div class="problem-card">
                        <div class="problem-number">Problem 3: User Authentication</div>
                        <a href="https://userauthentication-dygk.onrender.com/login" class="problem-link" target="_blank">
                            View Solution →
                        </a>
                    </div>
                    
                    <div class="problem-card">
                        <div class="problem-number">Problem 4: Advanced Application</div>
                        <a href="https://cloudcomputingpass-assaignment-4.onrender.com/" class="problem-link" target="_blank">
                            View Solution →
                        </a>
                    </div>
                    
                    <div class="problem-card">
                        <div class="problem-number">Problem 5: Login System</div>
                        <a href="https://cloudcomputingpass-assaignment-2.onrender.com/login" class="problem-link" target="_blank">
                            View Solution →
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div class="university-logo">UC</div>
            <p>University of Chittagong • Department of Computer Science and Engineering</p>
            <p style="margin-top: 0.5rem; font-size: 0.8rem; opacity: 0.7;">
                Deployed on PAAS Platform • Flask Application
            </p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Main route that serves the cover page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "message": "Cloud Computing Assignment Cover Page",
        "student": "Shanewaz Aurnob",
        "course": "CSE-814"
    }

@app.route('/problems')
def problems_list():
    """API endpoint that returns all problem links"""
    problems = {
        "assignment": "Cloud Computing (Programs on PAAS)",
        "course_code": "CSE-814",
        "student": {
            "name": "Shanewaz Aurnob",
            "id": "20701066"
        },
        "problems": [
            {
                "number": 1,
                "title": "Even Number Generator",
                "url": "https://evennumbergenerator-f14k.onrender.com/",
                "status": "deployed"
            },
            {
                "number": 2,
                "title": "Basic Application",
                "url": "https://cloudcomputingpass-assaignment.onrender.com/",
                "status": "deployed"
            },
            {
                "number": 3,
                "title": "User Authentication",
                "url": "https://userauthentication-dygk.onrender.com/login",
                "status": "deployed"
            },
            {
                "number": 4,
                "title": "Advanced Application",
                "url": "https://cloudcomputingpass-assaignment-4.onrender.com/",
                "status": "deployed"
            },
            {
                "number": 5,
                "title": "Login System",
                "url": "https://cloudcomputingpass-assaignment-2.onrender.com/login",
                "status": "deployed"
            }
        ]
    }
    return problems

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',  # Make it accessible from any IP
        port=port,
        debug=True  # Set to False for production
    )
