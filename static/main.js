
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
