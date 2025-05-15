# backend/app.py

import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # Needed for frontend development serving from different port

# Import the processing function from your core logic
# Assuming your structure is backend/malaphor_core/process.py
# Make sure backend/malaphor_core/__init__.py exists
from malaphor_mvp.process import run_full_pipeline



# frontend_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../', 'frontend')
# Or using app.root_path which is the directory containing app.py
# frontend_folder = os.path.join(app.root_path, '..', 'frontend') # This should also work

# Initialize Flask app, pointing static_folder to the absolute path
# --- CHANGE THIS LINE ---
# app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

# frontend_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
# app = Flask(__name__, static_folder=frontend_folder, static_url_path='')


app = Flask(__name__, static_folder='../frontend', static_url_path='') # Serve frontend static files
CORS(app) # Enable CORS for development
# app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# Define the directory to save temporary uploaded files
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Serve the main frontend HTML page."""
    # print("runnnnnnnbyy")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload, process it, and return results."""
    print("Got the file csv")
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        # Save the file temporarily
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_filepath)
        print(f"Received and saved file to: {temp_filepath}")

        try:
            # Run the processing pipeline
            # Use the temporary file path
            results = run_full_pipeline(temp_filepath)

            # Clean up the temporary file (optional, but good practice)
            # os.remove(temp_filepath)

            return jsonify(results)

        except Exception as e:
            # Log the error for debugging
            print(f"An error occurred during pipeline processing: {e}")
            # Return an error response to the frontend
            return jsonify({'error': 'Error processing the file', 'details': str(e)}), 500

    else:
        return jsonify({'error': 'Invalid file type. Please upload a CSV.'}), 400

# To run the Flask development server
if __name__ == '__main__':
    # You might need to run this from the 'backend' directory or adjust paths
    # using relative paths or app.root_path
    # For simplicity in development, run this script from the malaphor_web_mvp root
    # e.g., python backend/app.py
    app.run(debug=True) # debug=True allows hot-reloading