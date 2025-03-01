
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
