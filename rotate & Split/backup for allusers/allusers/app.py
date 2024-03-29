from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfWriter, PdfReader
from waitress import serve
from pathlib import Path
import os
import logging
import socket

app = Flask(__name__)

DOWNLOADS_FOLDER = str(Path.home() / "Downloads")
ALLOWED_EXTENSIONS = {'pdf'}


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.config['DOWNLOADS_FOLDER'] = DOWNLOADS_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_pages(pdf_file, start_page, end_page):
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    for page_num in range(start_page - 1, end_page):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)

    output_filename = 'Split_completed_' + secure_filename(pdf_file.filename)
    output_path = os.path.join(app.config['DOWNLOADS_FOLDER'], output_filename)

    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)
    return output_path

def rotate_pages(pdf_file, page_numbers_input, degrees_input):
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()
    
    # Handle rotation for all pages
    if page_numbers_input == 'all':
        # Rotate all pages by the specified degree
        try:
            degree = int(degrees_input)  # Assuming degrees_input is a single integer string when 'all' is specified
        except ValueError:
            return "Invalid degree. Please provide a valid integer."
        
        for page in pdf_reader.pages:
            page.rotate(degree)
            pdf_writer.add_page(page)
    else:
        # Convert page_numbers and degrees from strings to lists of integers
        page_numbers = [int(num) for num in page_numbers_input.split(',')]
        degrees = [int(deg) for deg in degrees_input.split(',')]
        
        if any(page_num <= 0 or page_num > len(pdf_reader.pages) for page_num in page_numbers):
            return "Invalid page number provided. Please try again."

        for i, page in enumerate(pdf_reader.pages):
            if i + 1 in page_numbers:
                rotation_degree = degrees[page_numbers.index(i + 1)]  # Match the degree to the page number
                page.rotate(rotation_degree)
            pdf_writer.add_page(page)
    
    output_filename = 'Rotate_completed_' + secure_filename(pdf_file.filename)
    output_path = os.path.join(app.config['DOWNLOADS_FOLDER'], output_filename)

    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)
    return output_path


@app.route('/pdftools')
def index():
    return render_template('index.html')


@app.route('/split', methods=['POST'])
def split():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        start_page = int(request.form['start_page'])
        end_page = int(request.form['end_page'])
        output_filename = split_pages(file, start_page, end_page)
        return send_file(output_filename, as_attachment=True)
    else:
        return 'Invalid file format'
    

@app.route('/rotate', methods=['POST'])
def rotate():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        page_numbers = request.form.get('page_number')  # No immediate conversion to integers
        degrees = request.form.get('degree')
        
        output_filename = rotate_pages(file, page_numbers, degrees)
        return send_file(output_filename, as_attachment=True)
    else:
        return 'Invalid file format'


def start_server():
    """
    Start the Waitress server.
    """
    host = socket.gethostbyname(socket.gethostname())
    port = int(os.environ.get('PORT', 80))

    logger.info("Starting the PDFTools server on %s:%d%s", "http://"+host, port, '/pdftools')

    serve(app, host=host, port=port)

    
if __name__ == '__main__':
    start_server()
