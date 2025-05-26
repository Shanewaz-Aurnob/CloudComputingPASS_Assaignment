from flask import Flask, render_template, request, jsonify
import numpy as np
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/multiply', methods=['POST'])
def multiply_matrices():
    try:
        data = request.get_json()
        matrix_a = np.array(data['matrixA'])
        matrix_b = np.array(data['matrixB'])
        
        # Check if matrices can be multiplied
        if matrix_a.shape[1] != matrix_b.shape[0]:
            return jsonify({
                'error': f'Cannot multiply matrices: Matrix A has {matrix_a.shape[1]} columns but Matrix B has {matrix_b.shape[0]} rows'
            }), 400
        
        # Perform matrix multiplication
        result = np.dot(matrix_a, matrix_b)
        
        return jsonify({
            'result': result.tolist(),
            'dimensions': f'{matrix_a.shape[0]}x{matrix_a.shape[1]} × {matrix_b.shape[0]}x{matrix_b.shape[1]} = {result.shape[0]}x{result.shape[1]}'
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid matrix format. Please enter numbers only.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)