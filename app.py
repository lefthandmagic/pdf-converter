from flask import Flask, render_template, request, send_file, redirect, url_for
from fpdf import FPDF
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io

def create_app():
    app = Flask(__name__)
    
    class PDF(FPDF):
        def header(self):
            # Remove the entire header content
            pass

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if 'file' not in request.files:
                return 'No file uploaded', 400
            
            file = request.files['file']
            if file.filename == '':
                return 'No file selected', 400
            
            if file:
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Create pdfs directory if it doesn't exist
                if not os.path.exists('pdfs'):
                    os.makedirs('pdfs')
                
                if file_ext == '.pdf':
                    # Save PDF directly
                    output_path = os.path.join('pdfs', filename)
                    file.save(output_path)
                elif file_ext in ['.jpg', '.jpeg', '.png']:
                    # Handle image files
                    image = Image.open(file)
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')
                    output_path = os.path.join('pdfs', os.path.splitext(filename)[0] + '.pdf')
                    image.save(output_path, 'PDF')
                else:
                    return 'Unsupported file type', 400
                
                # Get just the filename without path for the template
                pdf_name = os.path.basename(output_path)
                return redirect(url_for('editor', pdf_name=pdf_name))
        
        return render_template('index.html')

    @app.route('/editor/<pdf_name>')
    def editor(pdf_name):
        return render_template('editor.html', pdf_name=pdf_name)

    @app.route('/pdfs/<filename>')
    def serve_pdf(filename):
        try:
            return send_file(os.path.join('pdfs', filename), mimetype='application/pdf')
        except Exception as e:
            print(f"Error serving PDF: {e}")
            return str(e), 404

    # Create necessary directories
    for directory in ['templates', 'static', 'pdfs']:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Create editor.html with cleaner Google-inspired design
    with open('templates/editor.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Add Your Signature</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script>
        window.pdfName = "{{ pdf_name }}";
    </script>
    <script src="/static/PDFManager.js"></script>
    <script src="/static/SignatureManager.js"></script>
    <script src="/static/DragManager.js"></script>
    <script src="/static/main.js"></script>
    <style>
        body { 
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #fff;
            color: #202124;
        }
        .toolbar {
            margin-bottom: 20px;
            padding: 8px;
            border-bottom: 1px solid #dadce0;
            background-color: #fff;
        }
        #pdf-container {
            width: 100%;
            max-width: 850px;
            height: 800px;
            margin: 0 auto;
            position: relative;
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            border-radius: 8px;
        }
        button {
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 24px;
            font-size: 14px;
            cursor: pointer;
            margin: 4px;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #1557b0;
        }
        .signature-container {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: #fff;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        #signature-pad {
            border: 1px solid #dadce0;
            border-radius: 4px;
            margin: 15px 0;
        }
        .signature-container h3 {
            margin: 0 0 16px 0;
            color: #202124;
            font-size: 18px;
        }
        .signature-buttons {
            margin-top: 16px;
            text-align: right;
        }
        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(32,33,36,0.6);
            z-index: 999;
        }
        .instructions {
            background-color: #f8f9fa;
            padding: 12px 16px;
            border-radius: 4px;
            margin: 16px auto;
            color: #202124;
            display: none;
            max-width: 850px;
            border: 1px solid #dadce0;
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="window.location.href='/'">Back</button>
        <button onclick="downloadPDF()">Download</button>
        <button id="addSignatureBtn">Add Signature</button>
        <button id="confirm-sig-btn" style="display:none;">Confirm Position</button>
    </div>
    
    <div class="instructions" id="drag-instructions">
        Click and drag to position your signature. Click "Confirm Position" when ready.
    </div>
    
    <div id="pdf-container">
        <div id="signature-preview"></div>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <div class="signature-container" id="sig-container">
        <h3>Draw Your Signature</h3>
        <canvas id="signature-pad" width="400" height="200"></canvas>
        <div class="signature-buttons">
            <button onclick="closeSignaturePad()">Cancel</button>
            <button onclick="clearSignature()">Clear</button>
            <button onclick="showSignaturePreview()">Add</button>
        </div>
    </div>
</body>
</html>
        ''')

    # Update index.html with cleaner Google-inspired design
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Digital Signature Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: #fff;
            color: #202124;
        }
        .main-content {
            flex: 1;
            max-width: 650px;
            margin: 40px auto;
            padding: 20px;
            text-align: center;
        }
        h1 {
            color: #202124;
            font-size: 24px;
            margin-bottom: 8px;
            font-weight: normal;
        }
        .description {
            color: #5f6368;
            margin-bottom: 32px;
            font-size: 14px;
            line-height: 1.6;
        }
        .upload-area {
            border: 2px dashed #dadce0;
            border-radius: 8px;
            padding: 32px;
            margin: 24px 0;
            background-color: #f8f9fa;
            transition: border-color 0.2s;
        }
        .upload-area:hover {
            border-color: #1a73e8;
        }
        .supported-files {
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin: 24px 0;
            font-size: 14px;
            color: #5f6368;
            border: 1px solid #dadce0;
        }
        button {
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 24px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #1557b0;
        }
        input[type="file"] {
            margin: 16px 0;
        }
        .features {
            text-align: left;
            margin: 32px 0;
            padding: 24px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dadce0;
        }
        .features h2 {
            font-size: 18px;
            color: #202124;
            margin-top: 0;
        }
        .features ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        .features li {
            margin: 12px 0;
            padding-left: 24px;
            position: relative;
            color: #5f6368;
        }
        .features li:before {
            content: "✓";
            color: #1a73e8;
            position: absolute;
            left: 0;
        }
    </style>
</head>
<body>
    <div class="main-content">
        <h1>Digital Signature Tool</h1>
        <p class="description">
            Add your signature to documents securely and easily
        </p>

        <form method="POST" enctype="multipart/form-data">
            <div class="upload-area">
                <input type="file" name="file" accept=".jpg,.jpeg,.png,.pdf">
                <br>
                <button type="submit">Upload Document</button>
            </div>
        </form>

        <div class="supported-files">
            Supported formats: PDF, JPG, JPEG, PNG
        </div>

        <div class="features">
            <h2>Features</h2>
            <ul>
                <li>Draw your signature digitally</li>
                <li>Position signature anywhere on document</li>
                <li>Instant PDF download</li>
                <li>Support for images and PDFs</li>
                <li>Simple and secure</li>
            </ul>
        </div>
    </div>
</body>
</html>
        ''')

    # First, ensure static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Create the JavaScript modules
    with open('static/PDFManager.js', 'w') as f:
        f.write('''
class PDFManager {
    constructor(container) {
        this.container = container;
        this.canvas = null;
    }

    async loadPDF(pdfPath) {
        try {
            const pdf = await pdfjsLib.getDocument(pdfPath).promise;
            const page = await pdf.getPage(1);
            const scale = 1.5;
            const viewport = page.getViewport({scale: scale});

            this.canvas = document.createElement('canvas');
            this.container.appendChild(this.canvas);
            const context = this.canvas.getContext('2d');
            this.canvas.height = viewport.height;
            this.canvas.width = viewport.width;

            await page.render({
                canvasContext: context,
                viewport: viewport
            }).promise;

            return this.canvas;
        } catch (error) {
            console.error("Error loading PDF:", error);
            this.container.textContent = "Error loading PDF: " + error.message;
            throw error;
        }
    }

    async downloadPDF() {
        try {
            const imgData = this.canvas.toDataURL('image/jpeg', 1.0);
            
            const pdf = new jspdf.jsPDF({
                orientation: this.canvas.width > this.canvas.height ? 'landscape' : 'portrait',
                unit: 'px',
                format: [this.canvas.width, this.canvas.height]
            });
            
            pdf.addImage(imgData, 'JPEG', 0, 0, this.canvas.width, this.canvas.height);
            pdf.save('signed_document.pdf');
        } catch (error) {
            console.error('Error downloading PDF:', error);
            throw error;
        }
    }
}
''')

    with open('static/SignatureManager.js', 'w') as f:
        f.write('''
class SignatureManager {
    constructor(padElement, previewElement) {
        this.signaturePad = new SignaturePad(padElement, {
            backgroundColor: 'rgb(255, 255, 255)'
        });
        this.previewElement = previewElement;
        this.position = { x: 50, y: 50 };
    }

    clear() {
        this.signaturePad.clear();
    }

    isEmpty() {
        return this.signaturePad.isEmpty();
    }

    getSignatureData() {
        return this.signaturePad.toDataURL();
    }

    showPreview() {
        if (this.isEmpty()) {
            throw new Error('No signature to preview');
        }
        
        const signatureData = this.getSignatureData();
        this.previewElement.dataset.signatureImage = signatureData;
        this.previewElement.style.display = 'block';
        this.previewElement.style.backgroundImage = `url(${signatureData})`;
        this.previewElement.style.backgroundSize = 'contain';
        this.previewElement.style.backgroundRepeat = 'no-repeat';
        this.previewElement.style.width = '200px';
        this.previewElement.style.height = '100px';
        this.previewElement.style.position = 'absolute';
        this.previewElement.style.left = '50px';
        this.previewElement.style.top = '50px';
        this.previewElement.style.cursor = 'grab';
        this.previewElement.style.zIndex = '1000';
    }

    hidePreview() {
        this.previewElement.style.display = 'none';
    }
}
''')

    with open('static/DragManager.js', 'w') as f:
        f.write('''
class DragManager {
    constructor(element) {
        this.element = element;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.position = { x: 0, y: 0 };
        
        this.initDragging();
    }

    initDragging() {
        this.element.addEventListener('mousedown', this.startDragging.bind(this));
        document.addEventListener('mousemove', this.drag.bind(this));
        document.addEventListener('mouseup', this.stopDragging.bind(this));
    }

    startDragging(e) {
        e.preventDefault();
        this.isDragging = true;
        const rect = this.element.getBoundingClientRect();
        this.dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        this.element.style.cursor = 'grabbing';
    }

    drag(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        
        const containerRect = this.element.parentElement.getBoundingClientRect();
        
        const newX = e.clientX - containerRect.left - this.dragOffset.x;
        const newY = e.clientY - containerRect.top - this.dragOffset.y;
        
        this.element.style.left = `${newX}px`;
        this.element.style.top = `${newY}px`;
        
        this.position = { x: newX, y: newY };
    }

    stopDragging(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        this.isDragging = false;
        this.element.style.cursor = 'grab';
    }

    getPosition() {
        return this.position;
    }
}
''')

    with open('static/main.js', 'w') as f:
        f.write('''
class PDFEditor {
    constructor(pdfName) {  // Add pdfName parameter
        this.pdfManager = null;
        this.signatureManager = null;
        this.dragManager = null;
        this.pdfName = pdfName;  // Store PDF name
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeComponents();
            this.initializeEventListeners();
            this.loadPDF();
        });
    }

    initializeComponents() {
        const container = document.getElementById('pdf-container');
        const padElement = document.getElementById('signature-pad');
        const previewElement = document.getElementById('signature-preview');
        
        this.pdfManager = new PDFManager(container);
        this.signatureManager = new SignatureManager(padElement, previewElement);
        this.dragManager = new DragManager(previewElement);
    }

    initializeEventListeners() {
        document.getElementById('addSignatureBtn').addEventListener('click', () => this.startSignature());
        document.getElementById('confirm-sig-btn').addEventListener('click', () => this.confirmSignature());
    }

    async loadPDF() {
        const pdfPath = `/pdfs/${this.pdfName}`;  // Use the stored PDF name
        await this.pdfManager.loadPDF(pdfPath);
    }

    startSignature() {
        document.getElementById('overlay').style.display = 'block';
        document.getElementById('sig-container').style.display = 'block';
    }

    closeSignaturePad() {
        document.getElementById('overlay').style.display = 'none';
        document.getElementById('sig-container').style.display = 'none';
        this.signatureManager.clear();
    }

    showSignaturePreview() {
        try {
            this.signatureManager.showPreview();
            this.closeSignaturePad();
            document.getElementById('drag-instructions').style.display = 'block';
            document.getElementById('confirm-sig-btn').style.display = 'inline-block';
        } catch (error) {
            alert(error.message);
        }
    }

    confirmSignature() {
        const preview = document.getElementById('signature-preview');
        const signatureData = preview.dataset.signatureImage;
        const position = this.dragManager.getPosition();
        
        const img = new Image();
        img.onload = () => {
            const context = this.pdfManager.canvas.getContext('2d');
            context.drawImage(img, position.x, position.y, 200, 100);
            
            preview.style.display = 'none';
            document.getElementById('drag-instructions').style.display = 'none';
            document.getElementById('confirm-sig-btn').style.display = 'none';
        };
        img.src = signatureData;
    }
}

// Initialize the application with PDF name from the window object
const editor = new PDFEditor(window.pdfName);  // Get PDF name from window object

// Global function references for HTML buttons
window.downloadPDF = () => editor.pdfManager.downloadPDF();
window.clearSignature = () => editor.signatureManager.clear();
window.showSignaturePreview = () => editor.showSignaturePreview();
window.closeSignaturePad = () => editor.closeSignaturePad();
''')

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
