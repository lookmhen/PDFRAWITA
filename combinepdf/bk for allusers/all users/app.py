from flask import Flask, render_template, request, send_file, session
from PyPDF2 import PdfMerger
from waitress import serve
import os
import uuid
import socket
import secrets
import time
import logging

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'temp'


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
tempdir=app.config['UPLOAD_FOLDER'] = 'temp'


# Define the maximum lifetime of a temporary file in seconds
MAX_LIFETIME = 120  # 2 min

# Define a cleanup function

def ensure_temp_directory_exists():
    """
    Ensure the temporary directory exists.
    """
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)

def cleanup_temp_files():
    
    """
    Remove expired temporary files.
    
    """
    
    current_time = time.time()
    
    for file_name in os.listdir(tempdir):
        file_path = os.path.join(tempdir, file_name)
        file_age = current_time - os.path.getctime(file_path)

        if file_age > MAX_LIFETIME:
            try:
                os.remove(file_path)
                logger.info("Removed expired file: %s", file_path)
            except Exception as e:
                logger.error("Error removing file: %s", e)



@app.route('/pdfmerge')
def home():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    uploaded_files = request.files.getlist("files[]")

    if not uploaded_files:
        return "No files selected for merging."

    merger = PdfMerger()
    temp_files = []

    try:
        session_id = secrets.token_hex(16)  # Generate a unique session ID
        session['session_id'] = session_id  # Store session ID in Flask session

        # Create the temp directory if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save uploaded files to the temp directory with unique names
        for file in uploaded_files:
            if file.filename.endswith(".pdf"):
                filename = str(uuid.uuid4()) + ".pdf"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                temp_files.append(file_path)
                merger.append(file_path)

        if not merger.inputs:
            return "No PDF files found in the selected files for merging."

        output_filename = session['session_id'] + ".pdf"  # Use session ID in the output filename
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        merger.write(output_path)
        merger.close()

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    finally:
        # Clean up uploaded files
        for file_path in temp_files:
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Remove the temp directory if it is empty
        if os.path.exists(app.config['UPLOAD_FOLDER']) and not os.listdir(app.config['UPLOAD_FOLDER']):
            os.rmdir(app.config['UPLOAD_FOLDER'])
            
@app.before_request
def run_cleanup():
    ensure_temp_directory_exists()
    cleanup_temp_files()
    
    
def start_server():
    """
    Start the Waitress server.
    """
    host = socket.gethostbyname(socket.gethostname())
    port = int(os.environ.get('PORT', 80))

    ensure_temp_directory_exists()

    logger.info("Starting the Mergepdf server on %s:%d%s", "http://"+host, port, '/pdfmerge')

    serve(app, host=host, port=port)

if __name__ == '__main__':
    start_server()
