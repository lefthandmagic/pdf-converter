from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os

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

            # Create pdfs directory if it doesn't exist
            if not os.path.exists('pdfs'):
                os.makedirs('pdfs')

            # Get file extension
            ext = os.path.splitext(file.filename)[1].lower()
            
            # Create PDF object
            pdf = PDF()
            pdf.add_page()
            
            if ext in ['.txt']:
                content = file.read().decode('utf-8')
                pdf.set_font('Arial', size=12)
                pdf.multi_cell(0, 10, content)
            elif ext in ['.jpg', '.jpeg', '.png']:
                temp_img = 'temp_image' + ext
                file.save(temp_img)
                pdf.image(temp_img, x=10, y=10, w=190)
                os.remove(temp_img)
            else:
                return 'Unsupported file type', 400
            
            # Save PDF in pdfs directory with a safe filename
            original_name = os.path.splitext(file.filename)[0]
            safe_filename = "".join(c for c in original_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            pdf_path = os.path.join('pdfs', f"{safe_filename}.pdf")
            pdf.output(pdf_path)
            
            return render_template('editor.html', pdf_name=os.path.basename(pdf_path))
        
        return render_template('index.html')

    @app.route('/pdfs/<filename>')
    def serve_pdf(filename):
        try:
            return send_file(os.path.join('pdfs', filename), mimetype='application/pdf')
        except Exception as e:
            print(f"Error serving PDF: {e}")  # Debug log
            return str(e), 404

    # Create necessary directories
    for directory in ['templates', 'static', 'pdfs']:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Create editor.html with signature pad
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
        // Set PDF name before loading other scripts
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
            background-color: #f5f5f5;
            font-family: Arial, sans-serif;
        }
        .toolbar {
            margin-bottom: 20px;
            padding: 10px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        #pdf-container {
            width: 100%;
            height: 800px;
            border: 1px solid #ccc;
            margin-bottom: 20px;
            position: relative;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        .signature-container {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
            z-index: 1000;
            border: 2px solid #4CAF50;
        }
        #signature-pad {
            border: 1px solid #ccc;
            border-radius: 4px;
            margin: 15px 0;
            background-color: white;
        }
        .signature-container h3 {
            margin-top: 0;
            color: #2c3e50;
            text-align: center;
        }
        .signature-buttons {
            margin-top: 20px;
            text-align: center;
        }
        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0,0,0,0.5);
            z-index: 999;
        }
        .instructions {
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            color: #2c3e50;
            display: none;
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <button onclick="window.location.href='/'">Back to Upload</button>
        <button onclick="downloadPDF()">Download Signed PDF</button>
        <button id="addSignatureBtn">Add Your Signature</button>
        <button id="confirm-sig-btn" style="display:none;">Confirm Signature Position</button>
    </div>
    
    <div class="instructions" id="drag-instructions">
        Click and drag to position your signature. Click "Confirm Signature Position" when ready.
    </div>
    
    <div id="pdf-container">
        <div id="signature-preview"></div>
    </div>
    
    <div class="overlay" id="overlay"></div>
    
    <div class="signature-container" id="sig-container">
        <h3>Draw Your Signature Below</h3>
        <canvas id="signature-pad" width="400" height="200"></canvas>
        <div class="signature-buttons">
            <button onclick="clearSignature()">Clear</button>
            <button onclick="showSignaturePreview()">Add to Document</button>
            <button onclick="closeSignaturePad()">Cancel</button>
        </div>
    </div>
</body>
</html>
        ''')

    # Update index.html to remove target="_blank"
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Digital Signature Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .description {
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        .upload-area {
            border: 2px dashed #4CAF50;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .supported-files {
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
        button {
            padding: 12px 24px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        input[type="file"] {
            margin: 20px 0;
        }
        .features {
            margin: 30px 0;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .features ul {
            list-style-type: none;
            padding: 0;
        }
        .features li {
            margin: 10px 0;
            padding-left: 24px;
            position: relative;
        }
        .features li:before {
            content: "✓";
            color: #4CAF50;
            position: absolute;
            left: 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Digital Signature Tool</h1>
        <p class="description">
            Add your signature to documents easily. Draw, position, and save your signature on any document.
            Perfect for contracts, forms, and other documents requiring your signature.
        </p>
    </div>

    <div class="features">
        <h2>Features:</h2>
        <ul>
            <li>Draw your signature using our digital pad</li>
            <li>Drag and position your signature anywhere on the document</li>
            <li>Download your signed document as PDF</li>
            <li>Support for multiple file formats</li>
            <li>Easy to use interface</li>
        </ul>
    </div>

    <div class="supported-files">
        <h3>Supported File Types:</h3>
        <p>Upload any of these files to add your signature: PDF, Images (.jpg, .jpeg, .png), or Text files (.txt)</p>
    </div>

    <form method="POST" enctype="multipart/form-data">
        <div class="upload-area">
            <h3>Upload Your Document</h3>
            <input type="file" name="file" accept=".txt,.jpg,.jpeg,.png,.pdf">
            <br>
            <button type="submit">Upload and Add Signature</button>
        </div>
    </form>
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
