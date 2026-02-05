export const state = {
    genMode: 'rules',  // 'rules' o 'ai'
    patternType: 'drums',
    config: {
        density: 0.6,
        complexity: 0.5,
        tempo: 140,
        style: 'techno',
        temperature: 1.0,
        visualGain: 0.5,     // Inestabilidad
        visualDecay: 0.3,    // Persistencia
        visualColor: 0,      // Hue shift
        visualSymmetry: 2,   // Kaleidoscope
        musicalFriction: 0.2, // Fricción Musical
        // Advanced visual controls
        visualBrightness: 1.0,  // 0.5 to 2.0
        visualContrast: 1.0,    // 0.5 to 3.0
        visualBlur: 0,          // 0 to 10
        visualScale: 1.0,       // 0.5 to 2.0
        visualRotateSpeed: 0,   // -5 to 5
        visualPixelate: 0,      // 0 to 50
        // Dramatic effects (column 3)
        visualInvert: 0,        // 0 to 1
        visualSaturate: 1.0,    // 0 to 2
        visualPosterize: 20,    // 2 to 20 (higher = less posterization)
        visualShiftX: 0,        // -0.5 to 0.5
        visualModulate: 0       // 0 to 1
    },
    lastPattern: null,
    morphMode: false,
    cycleSendInterval: null,
    lastLayers: [],      // Capas orquestradas
    isHallucination: false, // Si el patrón fue auto-corregido
    favoritesList: []  // Lista de favoritos
};

// Event Bus simple para reactividad
const listeners = [];

export function subscribe(listener) {
    listeners.push(listener);
}

export function updateState(key, value) {
    state[key] = value;
    notifyListeners(key, value);
}

export function updateConfig(key, value) {
    state.config[key] = value;
    notifyListeners(`config.${key}`, value);
}

function notifyListeners(key, value) {
    listeners.forEach(fn => fn(key, value));
}
