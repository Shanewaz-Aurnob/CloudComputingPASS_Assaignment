# app.py
from flask import Flask, render_template_string, request, jsonify
import numpy as np
import json

app = Flask(__name__)

# HTML template as a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nth Largest Number Finder</title>
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
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 700px;
            transition: transform 0.3s ease;
        }

        .container:hover {
            transform: translateY(-2px);
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .input-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
            font-size: 1.1em;
        }

        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
        }

        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 10px;
            position: relative;
        }

        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .btn.loading::after {
            content: '';
            position: absolute;
            width: 16px;
            height: 16px;
            margin: auto;
            border: 2px solid transparent;
            border-top-color: #ffffff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
        }

        @keyframes spin {
            0% { transform: translateY(-50%) rotate(0deg); }
            100% { transform: translateY(-50%) rotate(360deg); }
        }

        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: 600;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.5s ease;
        }

        .result.show {
            opacity: 1;
            transform: translateY(0);
        }

        .result.error {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
        }

        .result.success {
            background: linear-gradient(135deg, #00d2d3 0%, #54a0ff 100%);
            color: white;
        }

        .result-details {
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.9;
            line-height: 1.5;
        }

        .tech-stack {
            margin-top: 20px;
            text-align: center;
            color: #888;
            font-size: 0.8em;
        }

        .tech-stack span {
            background: rgba(102, 126, 234, 0.1);
            padding: 4px 8px;
            border-radius: 4px;
            margin: 0 4px;
        }

        @media (max-width: 480px) {
            .container {
                padding: 25px;
            }
            
            h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔢 Nth Largest Finder</h1>
        <div class="subtitle">Flask Backend with NumPy Processing</div>
        
        <div class="input-group">
            <label for="numbers">Enter Numbers (comma-separated):</label>
            <input type="text" id="numbers" placeholder="e.g., 10, 5, 8, 20, 3, 15, 12" value="10, 5, 8, 20, 3, 15, 12">
        </div>
        
        <div class="input-group">
            <label for="n">Find the Nth Largest Number:</label>
            <input type="number" id="n" min="1" placeholder="e.g., 3 for 3rd largest" value="3">
        </div>
        
        <button class="btn" id="findBtn" onclick="findNthLargest()">Find Nth Largest</button>
        
        <div id="result" class="result"></div>
        
        # <div class="tech-stack">
        #     <span>Flask</span>
        #     <span>NumPy</span>
        #     <span>JavaScript</span>
        #     <span>CSS3</span>
        # </div>
    </div>

    <script>
        // Flask API call function
        async function findNthLargest() {
            const numbersInput = document.getElementById('numbers').value.trim();
            const nInput = document.getElementById('n').value.trim();
            const resultDiv = document.getElementById('result');
            const findBtn = document.getElementById('findBtn');
            
            // Clear previous result
            resultDiv.classList.remove('show', 'error', 'success');
            
            // Show loading state
            findBtn.disabled = true;
            findBtn.classList.add('loading');
            findBtn.textContent = 'Processing...';
            
            try {
                // Make API call to Flask backend
                const response = await fetch('/find_nth_largest', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        numbers: numbersInput,
                        n: nInput
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const resultHtml = `
                        <div>The ${data.n}${data.ordinal} largest number is: <strong>${data.nth_largest}</strong></div>
                        <div class="result-details">
                            <div>📊 Total numbers: ${data.total_numbers}</div>
                            <div>🎯 Unique numbers: ${data.unique_count}</div>
                            <div>📈 All numbers sorted: [${data.all_numbers_sorted.join(', ')}]</div>
                            <div>🔢 Unique numbers sorted: [${data.unique_numbers_sorted.join(', ')}]</div>
                        </div>
                    `;
                    showResult(resultHtml, 'success');
                } else {
                    showResult(data.error, 'error');
                }
                
            } catch (error) {
                showResult(`Network error: ${error.message}`, 'error');
            } finally {
                // Reset button state
                findBtn.disabled = false;
                findBtn.classList.remove('loading');
                findBtn.textContent = 'Find Nth Largest';
            }
        }
        
        function showResult(message, type) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = message;
            resultDiv.className = `result ${type}`;
            
            setTimeout(() => {
                resultDiv.classList.add('show');
            }, 100);
        }
        
        // Allow Enter key to trigger calculation
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                findNthLargest();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/find_nth_largest', methods=['POST'])
def find_nth_largest():
    try:
        data = request.get_json()
        numbers_str = data.get('numbers', '')
        n = data.get('n', 0)
        
        # Validate inputs
        if not numbers_str or not n:
            return jsonify({
                'success': False,
                'error': 'Please provide both numbers and n value'
            })
        
        # Parse numbers
        try:
            numbers = [float(x.strip()) for x in numbers_str.split(',') if x.strip()]
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid number format. Please use comma-separated numbers.'
            })
        
        if not numbers:
            return jsonify({
                'success': False,
                'error': 'No valid numbers found'
            })
        
        n = int(n)
        if n < 1:
            return jsonify({
                'success': False,
                'error': 'N must be a positive integer'
            })
        
        # Convert to numpy array for efficient processing
        np_numbers = np.array(numbers)
        
        # Get unique numbers and sort in descending order
        unique_numbers = np.unique(np_numbers)[::-1]  # Reverse for descending
        all_numbers_sorted = np.sort(np_numbers)[::-1]  # All numbers sorted
        
        if n > len(unique_numbers):
            return jsonify({
                'success': False,
                'error': f'Cannot find {n}{get_ordinal_suffix(n)} largest number. Only {len(unique_numbers)} unique numbers available.'
            })
        
        nth_largest = unique_numbers[n-1]
        
        return jsonify({
            'success': True,
            'nth_largest': float(nth_largest),
            'n': n,
            'ordinal': get_ordinal_suffix(n),
            'all_numbers_sorted': all_numbers_sorted.tolist(),
            'unique_numbers_sorted': unique_numbers.tolist(),
            'total_numbers': len(numbers),
            'unique_count': len(unique_numbers)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

def get_ordinal_suffix(n):
    """Get ordinal suffix for a number (1st, 2nd, 3rd, etc.)"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask app is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)