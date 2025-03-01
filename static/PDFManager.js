
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
