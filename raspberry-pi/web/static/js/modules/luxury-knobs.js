/**
 * Luxury Knobs Module - v5.2 Studio Edition
 * Interactive rotary knobs with drag control
 */

export class LuxuryKnob {
    constructor(element, options = {}) {
        this.element = element;
        this.min = options.min || 0;
        this.max = options.max || 100;
        this.value = options.value || this.min;
        this.step = options.step || 1;
        this.onChange = options.onChange || (() => { });

        this.isDragging = false;
        this.startY = 0;
        this.startValue = 0;
        this.debounceTimeout = null;
        this.rafId = null;

        this.init();
    }

    init() {
        this.render();
        this.attachEvents();
        this.updateVisual();
    }

    render() {
        const knobId = `knob-${Math.random().toString(36).substr(2, 9)}`;

        this.element.innerHTML = `
            <div class="luxury-knob-container" data-knob-id="${knobId}">
                <svg class="luxury-knob-svg" viewBox="0 0 100 100" width="45" height="45">
                    <!-- Background circle -->
                    <circle cx="50" cy="50" r="42" 
                        fill="rgba(0, 0, 0, 0.4)" 
                        stroke="rgba(255, 255, 255, 0.1)" 
                        stroke-width="1"/>
                    
                    <!-- Progress arc -->
                    <path class="knob-progress" 
                        d="" 
                        fill="none" 
                        stroke="url(#knobGradient-${knobId})" 
                        stroke-width="3"
                        stroke-linecap="round"/>
                    
                    <!-- Center knob -->
                    <circle cx="50" cy="50" r="30" 
                        fill="rgba(255, 255, 255, 0.05)" 
                        stroke="rgba(255, 255, 255, 0.2)" 
                        stroke-width="1.5"/>
                    
                    <!-- Indicator line -->
                    <line class="knob-indicator" 
                        x1="50" y1="50" 
                        x2="50" y2="25" 
                        stroke="#fff" 
                        stroke-width="2.5" 
                        stroke-linecap="round"/>
                    
                    <!-- Gradient definition -->
                    <defs>
                        <linearGradient id="knobGradient-${knobId}" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color: var(--primary); stop-opacity: 1"/>
                            <stop offset="100%" style="stop-color: var(--primary-hover); stop-opacity: 0.8"/>
                        </linearGradient>
                    </defs>
                </svg>
                
                <div class="knob-value-display"></div>
            </div>
        `;

        this.svg = this.element.querySelector('.luxury-knob-svg');
        this.progressPath = this.element.querySelector('.knob-progress');
        this.indicator = this.element.querySelector('.knob-indicator');
        this.valueDisplay = this.element.querySelector('.knob-value-display');
        this.container = this.element.querySelector('.luxury-knob-container');
    }

    attachEvents() {
        this.container.addEventListener('mousedown', this.onMouseDown.bind(this));
        document.addEventListener('mousemove', this.onMouseMove.bind(this));
        document.addEventListener('mouseup', this.onMouseUp.bind(this));

        // Touch support
        this.container.addEventListener('touchstart', this.onTouchStart.bind(this));
        document.addEventListener('touchmove', this.onTouchMove.bind(this));
        document.addEventListener('touchend', this.onTouchEnd.bind(this));
    }

    onMouseDown(e) {
        e.preventDefault();
        this.isDragging = true;
        this.startY = e.clientY;
        this.startValue = this.value;
        this.container.classList.add('dragging');
    }

    onMouseMove(e) {
        if (!this.isDragging) return;

        const deltaY = this.startY - e.clientY;
        const sensitivity = (this.max - this.min) / 150; // 150px for full range
        const newValue = this.startValue + (deltaY * sensitivity);

        this.setValue(newValue);
    }

    onMouseUp() {
        this.isDragging = false;
        this.container.classList.remove('dragging');
    }

    onTouchStart(e) {
        const touch = e.touches[0];
        this.isDragging = true;
        this.startY = touch.clientY;
        this.startValue = this.value;
        this.container.classList.add('dragging');
    }

    onTouchMove(e) {
        if (!this.isDragging) return;
        e.preventDefault();

        const touch = e.touches[0];
        const deltaY = this.startY - touch.clientY;
        const sensitivity = (this.max - this.min) / 150;
        const newValue = this.startValue + (deltaY * sensitivity);

        this.setValue(newValue);
    }

    onTouchEnd() {
        this.isDragging = false;
        this.container.classList.remove('dragging');
    }

    setValue(value) {
        // Clamp and round to step
        value = Math.max(this.min, Math.min(this.max, value));
        value = Math.round(value / this.step) * this.step;

        if (value !== this.value) {
            this.value = value;

            // Only update visual - no auto-callback
            if (this.rafId) cancelAnimationFrame(this.rafId);
            this.rafId = requestAnimationFrame(() => {
                this.updateVisual();
                this.rafId = null;
            });
        }
    }

    updateVisual() {
        // Calculate rotation angle (-135 to 135 degrees)
        const percentage = (this.value - this.min) / (this.max - this.min);
        const angle = -135 + (percentage * 270);

        // Update indicator rotation (properly centered)
        this.indicator.setAttribute('transform', `rotate(${angle} 50 50)`);

        // Update progress arc
        this.updateProgressArc(percentage);

        // Update value display
        const displayValue = Number.isInteger(this.value) ? this.value : this.value.toFixed(1);
        this.valueDisplay.textContent = displayValue;
    }

    updateProgressArc(percentage) {
        if (percentage < 0.01) {
            // Don't render arc for very small values
            this.progressPath.setAttribute("d", "");
            return;
        }

        const startAngle = -135; // Bottom-left starting point
        const sweepAngle = percentage * 270; // Total angle to sweep
        const endAngle = startAngle + sweepAngle;

        const start = this.polarToCartesian(50, 50, 40, startAngle);
        const end = this.polarToCartesian(50, 50, 40, endAngle);

        const largeArcFlag = sweepAngle > 180 ? 1 : 0;

        const d = [
            "M", start.x.toFixed(2), start.y.toFixed(2),
            "A", 40, 40, 0, largeArcFlag, 1, end.x.toFixed(2), end.y.toFixed(2)
        ].join(" ");

        this.progressPath.setAttribute("d", d);
    }

    polarToCartesian(centerX, centerY, radius, angleInDegrees) {
        const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
        return {
            x: centerX + (radius * Math.cos(angleInRadians)),
            y: centerY + (radius * Math.sin(angleInRadians))
        };
    }
}

// Initialize all knobs on the page
export function initAllKnobs() {
    const knobElements = document.querySelectorAll('[data-luxury-knob]');
    const knobs = [];

    knobElements.forEach(el => {
        const config = {
            min: parseFloat(el.dataset.min) || 0,
            max: parseFloat(el.dataset.max) || 100,
            value: parseFloat(el.dataset.value) || 0,
            step: parseFloat(el.dataset.step) || 1,
            onChange: (value) => {
                // Dispatch custom event
                el.dispatchEvent(new CustomEvent('knobchange', {
                    detail: { value },
                    bubbles: true
                }));
            }
        };

        const knob = new LuxuryKnob(el, config);
        knobs.push(knob);
    });

    return knobs;
}
