import { state } from './js/core/state.js';
import { logActivity } from './js/modules/logger.js';

let audioContext = null;
let analyser = null;
let dataArray = null;
let visualizerRunning = false;
let animationId = null;
let canvas = null;
let canvasCtx = null;
let streamSource = null;

// Inicializar el visualizador
document.addEventListener('DOMContentLoaded', () => {
    // Vincular botón del dock si existe
    // (El HTML ya tiene onclick="openVisualizerModal()")

    // Configurar canvas al cargar si es posible
    setupCanvas();
});

function setupCanvas() {
    canvas = document.getElementById('visualizer-canvas');
    if (canvas) {
        canvasCtx = canvas.getContext('2d');
        // Ajustar tamaño del canvas al contenedor
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
    }
}

function resizeCanvas() {
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = 300; // Altura fija o dinámica
    }
}

// Abrir Modal y arrancar Audio
export async function openVisualizerModal() {
    const modal = document.getElementById('visualizer-modal');
    if (!modal) return;

    modal.style.display = 'block';

    if (!audioContext) {
        await initAudio();
    }

    // Si ya inicializó (o se acaba de inicializar), arrancar loop
    if (audioContext && !visualizerRunning) {
        visualizerRunning = true;
        drawVisualizer();
        logActivity('Visualizador iniciado');
    }
}

// Cerrar Modal y parar animación (pero mantener audio context vivo para reusar)
export function closeVisualizerModal() {
    const modal = document.getElementById('visualizer-modal');
    if (modal) {
        modal.style.display = 'none';
    }

    visualizerRunning = false;
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
}

// Inicializar Web Audio API
async function initAudio() {
    try {
        // Crear contexto de audio
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();

        // Solicitar acceso al micrófono
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("El navegador no soporta getUserMedia o el contexto no es seguro (necesitas HTTPS)");
        }
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });

        // Crear analizador
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256; // Resolución (baja para estilo retro/rápido)
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        // Conectar micrófono al analizador
        streamSource = audioContext.createMediaStreamSource(stream);
        streamSource.connect(analyser);

        // NO conectamos analyser a destination (speakers) para evitar feedback loop infernal

        logActivity('Audio input conectado para visualización');

    } catch (err) {
        console.error('Error accediendo al audio:', err);
        logActivity('Error: No se pudo acceder al micrófono para visualización', 'error');
        alert('Para ver el visualizador, necesitas permitir el acceso al micrófono (capturará el audio de tus altavoces).');
    }
}

// Bucle de dibujo
function drawVisualizer() {
    if (!visualizerRunning || !analyser) return;

    animationId = requestAnimationFrame(drawVisualizer);

    // Obtener datos de frecuencia
    analyser.getByteFrequencyData(dataArray);

    // Limpiar canvas
    canvasCtx.fillStyle = '#1e1e1e'; // Fondo oscuro (igual al tema)
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    const bufferLength = analyser.frequencyBinCount;
    const barWidth = (canvas.width / bufferLength) * 1.5;
    let barHeight;
    let x = 0;

    // Dibujar barras
    for (let i = 0; i < bufferLength; i++) {
        barHeight = dataArray[i];

        // Color dinámico basado en altura/frecuencia
        // Tidal style: R purples/pinks/cyans
        const r = barHeight + (25 * (i / bufferLength));
        const g = 150 * (i / bufferLength);
        const b = 255;

        if (state.patternType === 'drums') {
            canvasCtx.fillStyle = `rgb(${r},50,50)`; // Rojos para drums
        } else if (state.patternType === 'bass') {
            canvasCtx.fillStyle = `rgb(50,${r},50)`; // Verdes para bass
        } else {
            canvasCtx.fillStyle = `rgb(${r},${g},${b})`; // Multicolor
        }

        // Escalar altura al canvas
        const scaledHeight = (barHeight / 255) * canvas.height;

        canvasCtx.fillRect(x, canvas.height - scaledHeight, barWidth, scaledHeight);

        x += barWidth + 1;
    }

    // Opcional: Dibujar info del patrón actual superpuesta
    if (state.lastPattern) {
        canvasCtx.font = '14px "Fira Code", monospace';
        canvasCtx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        canvasCtx.fillText(state.lastPattern.substring(0, 50) + (state.lastPattern.length > 50 ? '...' : ''), 10, 30);
    }
}
