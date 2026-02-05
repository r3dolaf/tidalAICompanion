/**
 * TidalAI Studio - Hydra Visuals Module (Reactive v2.2)
 * Traduce parámetros musicales Y estructura de código a síntesis de video.
 * Incluye controles de Inestabilidad (Gain) y Persistencia (Decay).
 */

let hydra;
let canvas;
let currentStyle = 'techno';
let randomSeed = 0.5;

export function initHydra() {
    canvas = document.getElementById('hydra-bg'); // Changed to background canvas
    if (!canvas) return;

    try {
        const width = window.innerWidth;
        const height = window.innerHeight;

        canvas.width = width;
        canvas.height = height;

        hydra = new Hydra({
            canvas: canvas,
            detectAudio: false,
            enableStreamCapture: false,
            width: width,
            height: height
        });

        renderNeutral();
        console.log("👁️ Hydra Initialized (The Living Background v5.0)");
    } catch (e) {
        console.error("Hydra init failed:", e);
    }
}

function analyzePattern(pattern) {
    if (!pattern) return { energy: 0.5, hasFX: false };
    const tokenCount = (pattern.match(/ /g) || []).length;
    const energy = Math.min(tokenCount / 20, 1.0);
    const hasFX = pattern.includes('#') || pattern.includes('$');
    const hasGlitch = pattern.includes('glitch') || pattern.includes('pixel');
    return { energy, hasFX, hasGlitch };
}

/**
 * Actualiza los visuales basado en el estado musical y el código generado
 */
export function updateVisuals(state, pattern = "") {
    if (!hydra) return;

    const {
        density, complexity, style,
        visualGain, visualDecay, visualColor, visualSymmetry,
        visualBrightness, visualContrast, visualBlur, visualScale, visualRotateSpeed, visualPixelate,
        visualInvert, visualSaturate, visualPosterize, visualShiftX, visualModulate
    } = state.config;
    const analysis = analyzePattern(pattern);

    // Core parameters
    const gain = visualGain || 0.5;
    const decay = visualDecay || 0.3;
    const hueShift = visualColor || 0;
    const symm = visualSymmetry || 2;

    // Advanced parameters (with defaults)
    const brightness = visualBrightness || 1.0;
    const contrast = visualContrast || 1.0;
    const blur = visualBlur || 0;
    const scale = visualScale || 1.0;
    const rotateSpeed = visualRotateSpeed || 0;
    const pixelate = visualPixelate || 0;

    // Dramatic effects
    const invert = visualInvert || 0;
    const saturate = visualSaturate || 1.0;
    const posterize = visualPosterize || 20;
    const shiftX = visualShiftX || 0;
    const modulate = visualModulate || 0;

    const speed = 0.3 + (density * 1.5 * gain) + (analysis.energy * gain);
    const mod = (complexity * 5 * gain) + (analysis.hasFX ? 3 * gain : 0);

    randomSeed = Math.random();
    currentStyle = style;

    // Debug: check if knob values are reaching Hydra
    console.log('🎛️ Hydra params:', { brightness, contrast, scale, pixelate, invert, saturate });

    // Apply global effects including advanced controls
    const applyGlobal = (srcnode) => {
        let n = srcnode;

        // Core effects
        if (hueShift > 0) n = n.hue(hueShift);

        // Scale (apply early)
        if (scale !== 1.0) n = n.scale(scale);

        // Pixelate (dramatic effect)
        if (pixelate > 0) n = n.pixelate(pixelate, pixelate);

        // Brightness: Hydra works with offset, convert 0.5-2.0 range to -0.5 to +1.0
        if (brightness !== 1.0) {
            const offset = (brightness - 1.0) * 0.5; // 0.5->-0.25, 1.0->0, 2.0->+0.5
            n = n.brightness(offset);
        }

        // Contrast: works as multiplier
        if (contrast !== 1.0) n = n.contrast(contrast);

        // Blur: Hydra blur is very subtle, scale it up
        if (blur > 0 && typeof n.blur === 'function') {
            n = n.blur(blur / 5); // Divide less for more visible effect
        }

        // Rotate animation
        if (rotateSpeed !== 0) n = n.rotate(() => time * rotateSpeed * 0.15);

        // === DRAMATIC EFFECTS (Column 3) ===
        // Invert colors (0-1 range)
        if (invert > 0) n = n.invert(invert);

        // Saturation (multiplier)
        if (saturate !== 1.0) n = n.saturate(saturate);

        // Posterize (reduce color palette)
        if (posterize < 20) n = n.posterize(posterize, posterize);

        // Scroll X (horizontal shift)
        if (shiftX !== 0) n = n.scrollX(shiftX);

        // Modulate with noise for glitch effect
        if (modulate > 0) n = n.modulate(noise(3), modulate);

        // Kaleid symmetry
        if (symm > 2) n = n.kaleid(symm);

        // Persistence/decay (always last)
        return n.blend(src(o0), decay);
    };

    switch (style) {
        case 'techno':
            applyGlobal(
                osc(10 + (analysis.energy * 20), 0.1, mod)
                    .rotate(randomSeed * speed)
                    .modulate(noise(3), analysis.hasFX ? 0.2 : 0.05)
                    .color(0.6, analysis.hasGlitch ? 0.8 : 0.3, 1)
            ).out();
            break;

        case 'house':
            applyGlobal(
                shape(4, 0.7, 0.01)
                    .repeat(mod + 2, mod + 2)
                    .rotate(() => time * speed * 0.2)
                    .color(1, 0.5, 0.2)
                    .modulate(osc(10), 0.1)
            ).out();
            break;

        case 'ambient':
            applyGlobal(
                voronoi(5 + (analysis.energy * 10), 0.3, speed)
                    .modulate(noise(2), analysis.hasFX ? 0.6 : 0.2)
                    .color(0.1, 0.5 + (randomSeed * 0.2), 0.8)
                // Kaleid local a ambient se suma al global si existe
            ).out();
            break;

        case 'breakbeat':
            applyGlobal(
                osc(30, 0.1, speed)
                    .modulate(noise(3), 1)
                    .color(analysis.hasFX ? 1 : 0.5, 1, 0.2)
            ).out();
            break;

        case 'experimental':
            applyGlobal(
                src(o0)
                    .modulate(noise(3), 0.01)
                    .layer(osc(10 * gain, 0.1, speed).mask(shape(4, 0.5)))
                    .rotate(0.1)
                    .color(randomSeed, 0.2, 0.8)
            ).out();
            break;

        case 'cyberpunk':
            applyGlobal(
                osc(50, 0.01, 1.5)
                    .modulate(noise(3), speed * 0.5)
                    .color(1, 0, 0.8)
                    .layer(osc(20, 0.1, 2).mask(shape(4, 0.4, 0.1)).color(0, 1, 1))
                    .rotate(randomSeed)
                    .pixelate(analysis.hasGlitch ? 20 : 100, 20)
            ).out();
            break;

        case 'industrial':
            applyGlobal(
                noise(3, speed * 0.2)
                    .contrast(2)
                    .modulateScale(osc(2), 0.5)
                    .color(0.7, 0.7, 0.7)
                    .scrollX(0, 0.1 * gain)
            ).out();
            break;

        case 'deepsea':
            applyGlobal(
                osc(5, 0.1, speed)
                    .modulate(noise(2), 0.5)
                    .color(0, 0.2, 0.7)
                    .mask(voronoi(10, 0.5))
            ).out();
            break;

        case 'glitch':
            applyGlobal(
                osc(20, 0.5, 2)
                    .modulatePixelate(noise(3), 10, mod + (analysis.energy * 5))
                    .color(1, analysis.hasGlitch ? 0.6 : 0.2, 0.5)
                    .pixelate(analysis.hasGlitch ? 5 : 30, 30)
            ).out();
            break;

        case 'organic':
            applyGlobal(
                shape(analysis.hasFX ? 3 : 4, 0.5, speed)
                    .repeat(mod, mod)
                    .modulateRotate(noise(2), randomSeed)
                    .color(0.2, 0.8, 0.4 + (analysis.energy * 0.3))
            ).out();
            break;

        case 'drum_and_bass':
        case 'dnb':
            applyGlobal(
                osc(40, 0, 1)
                    .modulate(noise(3), speed * 0.5)
                    .scrollX(0, () => time * speed * 0.5)
                    .color(0.4, 0.4, 1)
                    .pixelate(20, 1000)
            ).out();
            break;

        case 'dub':
            applyGlobal(
                osc(5, 0.05, speed * 0.2)
                    .modulate(noise(2), 0.8)
                    .color(1, 0.8, 0.2)
            ).out();
            break;

        case 'trap':
            applyGlobal(
                shape(4, 0.8, 0.01)
                    .repeat(mod, mod)
                    .modulateScale(osc(10), 0.5)
                    .color(0.8, 0, 1)
                    .invert(randomSeed > 0.8 ? 1 : 0)
                    .pixelate(10, 10)
            ).out();
            break;

        default:
            renderNeutral(speed);
    }

    const status = document.getElementById('visuals-status');
    if (status) status.innerText = `REACTIVE: ${style.toUpperCase()} (Gain: ${Math.round(gain * 100)}%)`;
}

function renderNeutral(speed = 1) {
    osc(10, 0.1, 1)
        .color(0.2, 0.2, 0.3)
        .rotate(() => Math.sin(time * 0.1) * speed)
        .out();
}
