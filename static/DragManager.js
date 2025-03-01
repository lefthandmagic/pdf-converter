
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
