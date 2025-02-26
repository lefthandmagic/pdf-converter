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
            # Check if a file was uploaded
            if 'file' not in request.files:
                return 'No file uploaded', 400
            
            file = request.files['file']
            if file.filename == '':
                return 'No file selected', 400

            # Get file extension
            ext = os.path.splitext(file.filename)[1].lower()
            
            # Create PDF object
            pdf = PDF()
            pdf.add_page()
            
            if ext in ['.txt']:
                # Handle text file
                content = file.read().decode('utf-8')
                pdf.set_font('Arial', size=12)
                pdf.multi_cell(0, 10, content)
            elif ext in ['.jpg', '.jpeg', '.png']:
                # Save image temporarily
                temp_img = 'temp_image' + ext
                file.save(temp_img)
                # Add image to PDF
                pdf.image(temp_img, x=10, y=10, w=190)
                # Clean up temp file
                os.remove(temp_img)
            else:
                return 'Unsupported file type', 400
            
            # Save PDF
            pdf_path = 'output.pdf'
            pdf.output(pdf_path)
            
            # Return PDF file
            return send_file(pdf_path, as_attachment=True)
        
        return render_template('index.html')

    # Create templates folder and index.html
    if not os.path.exists('templates'):
        os.makedirs('templates')

    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>File to PDF Converter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>File to PDF Converter</h1>
    <p>Supported files: .txt, .jpg, .jpeg, .png</p>
    <form method="POST" enctype="multipart/form-data">
        <div class="upload-area">
            <input type="file" name="file" accept=".txt,.jpg,.jpeg,.png"><br><br>
            <button type="submit">Convert to PDF</button>
        </div>
    </form>
</body>
</html>
    ''')

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
