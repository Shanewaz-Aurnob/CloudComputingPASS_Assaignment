from flask import Flask, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Even Numbers Generator</title>
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

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .input-section {
            text-align: center;
            margin-bottom: 30px;
        }

        .input-group {
            display: inline-flex;
            align-items: center;
            gap: 15px;
            background: #f8f9fa;
            padding: 20px 30px;
            border-radius: 15px;
            border: 2px solid #e9ecef;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .input-group label {
            font-weight: 600;
            color: #495057;
            font-size: 1.1rem;
        }

        .input-group input {
            width: 120px;
            padding: 12px 15px;
            border: 2px solid #ced4da;
            border-radius: 8px;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
            transition: border-color 0.3s ease;
        }

        .input-group input:focus {
            border-color: #11998e;
            outline: none;
            box-shadow: 0 0 0 3px rgba(17, 153, 142, 0.2);
        }

        .options-section {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .option-group {
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 10px;
            border: 2px solid #e9ecef;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .option-group label {
            font-weight: 600;
            color: #495057;
        }

        .option-group select {
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            font-size: 14px;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(17, 153, 142, 0.6);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4);
        }

        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(240, 147, 251, 0.6);
        }

        .result-section {
            text-align: center;
            margin-top: 30px;
        }

        .result-section h2 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }

        .result-info {
            background: #e2e3e5;
            color: #383d41;
            padding: 15px 20px;
            border-radius: 10px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-weight: 600;
        }

        .numbers-container {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 2px solid #28a745;
            max-height: 400px;
            overflow-y: auto;
        }

        .numbers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 10px;
        }

        .number-cell {
            background: white;
            border: 2px solid #28a745;
            border-radius: 8px;
            padding: 10px;
            font-weight: 600;
            color: #155724;
            text-align: center;
            transition: transform 0.2s ease;
        }

        .number-cell:hover {
            transform: scale(1.05);
        }

        .numbers-list {
            background: white;
            border: 2px solid #28a745;
            border-radius: 10px;
            padding: 20px;
            text-align: left;
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            max-height: 300px;
            overflow-y: auto;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #f5c6cb;
            text-align: center;
        }

        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 15px 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #c3e6cb;
            text-align: center;
        }

        .stats-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #e9ecef;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #11998e;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 5px;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .main-content {
                padding: 20px;
            }
            
            .input-group {
                flex-direction: column;
                gap: 10px;
            }
            
            .options-section {
                flex-direction: column;
                align-items: center;
            }
            
            .numbers-grid {
                grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔢 Even Numbers Generator</h1>
            <p>Generate sequences of even numbers with customizable options</p>
        </div>
        
        <div class="main-content">
            <div class="input-section">
                <div class="input-group">
                    <label for="numberCount">Generate</label>
                    <input type="number" id="numberCount" value="10" min="1" max="1000">
                    <label>even numbers</label>
                </div>
            </div>

            <div class="options-section">
                <div class="option-group">
                    <label for="startFrom">Start from:</label>
                    <input type="number" id="startFrom" value="0" step="2">
                </div>
                <div class="option-group">
                    <label for="displayMode">Display as:</label>
                    <select id="displayMode">
                        <option value="grid">Grid</option>
                        <option value="list">List</option>
                    </select>
                </div>
                <div class="option-group">
                    <label for="includeStats">Show stats:</label>
                    <input type="checkbox" id="includeStats" checked>
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn btn-primary" onclick="generateNumbers()">Generate Numbers</button>
                <button class="btn btn-secondary" onclick="clearResults()">Clear Results</button>
            </div>

            <div id="message"></div>
            
            <div class="result-section" id="resultSection" style="display: none;">
                <h2>Generated Even Numbers</h2>
                <div id="resultInfo" class="result-info"></div>
                <div id="statsSection" class="stats-section"></div>
                <div class="numbers-container" id="numbersContainer"></div>
            </div>
        </div>
    </div>

    <script>
        function displayNumbers(numbers, mode, info, stats) {
            const container = document.getElementById('numbersContainer');
            const resultInfo = document.getElementById('resultInfo');
            const statsSection = document.getElementById('statsSection');
            
            resultInfo.textContent = info;
            
            // Display stats if enabled
            if (document.getElementById('includeStats').checked && stats) {
                statsSection.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-value">${stats.count}</div>
                        <div class="stat-label">Total Numbers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.sum}</div>
                        <div class="stat-label">Sum</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.average}</div>
                        <div class="stat-label">Average</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.range}</div>
                        <div class="stat-label">Range</div>
                    </div>
                `;
                statsSection.style.display = 'grid';
            } else {
                statsSection.style.display = 'none';
            }
            
            if (mode === 'grid') {
                container.innerHTML = '<div class="numbers-grid"></div>';
                const grid = container.querySelector('.numbers-grid');
                
                numbers.forEach(num => {
                    const cell = document.createElement('div');
                    cell.className = 'number-cell';
                    cell.textContent = num;
                    grid.appendChild(cell);
                });
            } else {
                container.innerHTML = '<div class="numbers-list"></div>';
                const list = container.querySelector('.numbers-list');
                list.textContent = numbers.join(', ');
            }
            
            document.getElementById('resultSection').style.display = 'block';
        }

        function showMessage(message, isError = false) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="${isError ? 'error-message' : 'success-message'}">${message}</div>`;
            setTimeout(() => {
                messageDiv.innerHTML = '';
            }, 5000);
        }

        async function generateNumbers() {
            const count = parseInt(document.getElementById('numberCount').value);
            const startFrom = parseInt(document.getElementById('startFrom').value);
            const displayMode = document.getElementById('displayMode').value;
            const includeStats = document.getElementById('includeStats').checked;
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        count: count,
                        start_from: startFrom,
                        include_stats: includeStats
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayNumbers(data.numbers, displayMode, data.info, data.stats);
                    showMessage(`Successfully generated ${count} even numbers!`);
                } else {
                    showMessage(data.error, true);
                    document.getElementById('resultSection').style.display = 'none';
                }
            } catch (error) {
                showMessage('Error: ' + error.message, true);
                document.getElementById('resultSection').style.display = 'none';
            }
        }

        function clearResults() {
            document.getElementById('resultSection').style.display = 'none';
            document.getElementById('message').innerHTML = '';
            showMessage('Results cleared!');
        }

        // Initialize with default values
        document.addEventListener('DOMContentLoaded', function() {
            generateNumbers();
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/generate', methods=['POST'])
def generate_even_numbers():
    try:
        data = request.get_json()
        count = data.get('count', 10)
        start_from = data.get('start_from', 0)
        include_stats = data.get('include_stats', False)
        
        # Validate inputs
        if count <= 0 or count > 1000:
            return jsonify({
                'error': 'Count must be between 1 and 1000'
            }), 400
        
        # Ensure start_from is even
        if start_from % 2 != 0:
            start_from += 1
        
        # Generate even numbers
        numbers = []
        current = start_from
        for i in range(count):
            numbers.append(current)
            current += 2
        
        # Calculate statistics if requested
        stats = None
        if include_stats:
            total_sum = sum(numbers)
            stats = {
                'count': len(numbers),
                'sum': total_sum,
                'average': round(total_sum / len(numbers), 2),
                'range': f"{numbers[0]} - {numbers[-1]}"
            }
        
        return jsonify({
            'numbers': numbers,
            'info': f'Generated {count} even numbers starting from {start_from}',
            'stats': stats
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid input. Please enter valid numbers.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)