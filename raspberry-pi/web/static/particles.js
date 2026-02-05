/**
 * TidalAI Bio-Reactive Particle System
 * Motor de partículas ligero para el fondo del Companion Studio.
 */

class ParticleEngine {
    constructor() {
        this.canvas = document.getElementById('bg-canvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.maxParticles = 80;
        this.theme = 'techno';
        this.color = '#8b5cf6';

        this.resize();
        window.addEventListener('resize', () => this.resize());

        this.init();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    setTheme(theme) {
        this.theme = theme;
        const rootStyle = getComputedStyle(document.documentElement);
        this.color = rootStyle.getPropertyValue('--primary').trim() || '#8b5cf6';
    }

    init() {
        this.particles = [];
        for (let i = 0; i < this.maxParticles; i++) {
            this.particles.push(this.createParticle());
        }
    }

    createParticle(isBurst = false) {
        const x = isBurst ? window.innerWidth / 2 : Math.random() * this.canvas.width;
        const y = isBurst ? window.innerHeight / 2 : Math.random() * this.canvas.height;

        return {
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * (isBurst ? 10 : 1),
            vy: (Math.random() - 0.5) * (isBurst ? 10 : 1),
            size: Math.random() * 3 + 1,
            life: isBurst ? 1.0 : 1.0,
            decay: isBurst ? 0.02 + Math.random() * 0.02 : 0,
            isBurst: isBurst
        };
    }

    burst() {
        for (let i = 0; i < 30; i++) {
            this.particles.push(this.createParticle(true));
        }
    }

    update() {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.isBurst) {
                p.life -= p.decay;
                if (p.life <= 0) {
                    this.particles.splice(i, 1);
                    continue;
                }
            } else {
                // Mantenimiento de límites para partículas base
                if (p.x < 0) p.x = this.canvas.width;
                if (p.x > this.canvas.width) p.x = 0;
                if (p.y < 0) p.y = this.canvas.height;
                if (p.y > this.canvas.height) p.y = 0;
            }
        }

        // Mantener población base si bajó por los bursts expirados (no debería pero por seguridad)
        const baseCount = this.particles.filter(p => !p.isBurst).length;
        if (baseCount < this.maxParticles) {
            this.particles.push(this.createParticle(false));
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach(p => {
            this.ctx.beginPath();

            this.ctx.globalAlpha = p.isBurst ? p.life : 0.3;
            this.ctx.fillStyle = this.color;

            if (this.theme === 'ambient' || this.theme === 'deepsea') {
                // Orbes difusos
                this.ctx.arc(p.x, p.y, p.size * (p.isBurst ? 2 : 1), 0, Math.PI * 2);
                this.ctx.fill();
            } else if (this.theme === 'glitch' || this.theme === 'cyberpunk') {
                // Cuadrados digitales
                const s = p.size * (p.isBurst ? 3 : 1);
                this.ctx.fillRect(p.x, p.y, s, s);
            } else if (this.theme === 'organic') {
                // Lineas / Formas alargadas
                this.ctx.moveTo(p.x, p.y);
                this.ctx.lineTo(p.x + p.vx * 10, p.y + p.vy * 10);
                this.ctx.strokeStyle = this.color;
                this.ctx.stroke();
            } else {
                // Standard dots
                this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                this.ctx.fill();
            }
        });
    }

    animate() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// Inicializar cuando el DOM esté listo
window.particleEngine = null;
document.addEventListener('DOMContentLoaded', () => {
    window.particleEngine = new ParticleEngine();
    // Obtener tema inicial
    setTimeout(() => {
        if (window.updateTheme) {
            const style = document.getElementById('style')?.value || 'techno';
            window.particleEngine.setTheme(style);
        }
    }, 500);
});
