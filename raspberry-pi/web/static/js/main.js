import { state, updateState, updateConfig, subscribe } from './core/state.js';
import { elements, initUI, updateStatusUI, patternTypeIcons } from './ui/ui-manager.js';
import { initThemeEngine, updateTheme } from './modules/theme-engine.js';
import * as api from './modules/network.js';
import { logActivity, showNotification } from './modules/logger.js';
import * as panels from './ui/panels.js';
import * as modals from './ui/modals.js';
import * as advanced from '../advanced-features.js';
import * as phase2 from '../phase2-features.js';
import * as phase3 from '../phase3-features.js';
import * as visuals from './modules/visuals-hydra.js';
import * as conductor from './modules/conductor.js';
import { renderTimeline, initTimeline } from './modules/timeline-visualizer.js';
import { initKeyboardShortcuts } from './modules/keyboard-shortcuts.js';
import { initAllKnobs } from './modules/luxury-knobs.js';
import { initArranger } from './modules/arranger.js'; // Phase 19

// --- THEORY RULES LOGIC (Phase 17b) ---

async function loadRules() {
    try {
        const data = await api.getTheoryRulesAPI();
        if (data.success && data.rules) {
            renderRulesList(data.rules);
        }
    } catch (e) {
        console.error("Error loading rules:", e);
    }
}

function renderRulesList(rules) {
    const container = document.getElementById('rules-list-container');
    if (!container) return;

    let html = '';

    // 1. Mostrar reglas GENERALES primero (si existen)
    if (rules.general) {
        html += `<div style="margin-bottom:20px; border:2px solid #34d399; border-radius:8px; padding:12px; background:rgba(52,211,153,0.1);">
            <h3 style="color:#34d399; margin-bottom:10px; display:flex; align-items:center; gap:8px;">
                <span>🌍</span> General Music Theory
                <span style="font-size:0.7em; background:#059669; padding:2px 6px; border-radius:4px;">ALWAYS APPLIED</span>
            </h3>
            <div style="display:grid; grid-template-columns: 1fr; gap:8px;">`;

        rules.general.forEach(rule => {
            const isChecked = rule.active ? 'checked' : '';
            const typeLabel = rule.type === 'regex' ? '<span style="font-size:0.7em; background:#475569; padding:2px 4px; border-radius:4px; margin-left:5px;">REGEX</span>' : '';

            html += `
            <div style="background:rgba(255,255,255,0.05); padding:8px; border-radius:6px; display:flex; align-items:center;">
                <label class="switch" style="margin-right:10px;">
                    <input type="checkbox" ${isChecked} onchange="toggleRuleAPI('general', '${rule.id}', this.checked)">
                    <span class="slider round"></span>
                </label>
                <div>
                    <div style="font-weight:bold; font-size:0.9rem;">${rule.desc} ${typeLabel}</div>
                    <div style="font-size:0.75rem; color:#94a3b8; font-family:monospace;">ID: ${rule.id}</div> 
                    ${rule.pattern ? `<div style="font-size:0.75rem; color:#f59e0b; font-family:monospace;">/${rule.pattern}/</div>` : ''}
                </div>
            </div>`;
        });

        html += `</div></div>`;
    }

    // 2. Mostrar reglas por GÉNERO
    for (const [genre, genreRules] of Object.entries(rules)) {
        if (genre === 'general') continue; // Ya lo mostramos arriba

        html += `<div style="margin-bottom:15px;">
            <h3 style="color:#34d399; margin-bottom:8px; text-transform:capitalize;">${genre}</h3>
            <div style="display:grid; grid-template-columns: 1fr; gap:8px;">`;

        genreRules.forEach(rule => {
            const isChecked = rule.active ? 'checked' : '';
            const typeLabel = rule.type === 'regex' ? '<span style="font-size:0.7em; background:#475569; padding:2px 4px; border-radius:4px; margin-left:5px;">REGEX</span>' : '';

            html += `
            <div style="background:rgba(255,255,255,0.05); padding:8px; border-radius:6px; display:flex; align-items:center;">
                <label class="switch" style="margin-right:10px;">
                    <input type="checkbox" ${isChecked} onchange="toggleRuleAPI('${genre}', '${rule.id}', this.checked)">
                    <span class="slider round"></span>
                </label>
                <div>
                    <div style="font-weight:bold; font-size:0.9rem;">${rule.desc} ${typeLabel}</div>
                    <div style="font-size:0.75rem; color:#94a3b8; font-family:monospace;">ID: ${rule.id}</div> 
                    ${rule.regex ? `<div style="font-size:0.75rem; color:#f59e0b; font-family:monospace;">/${rule.regex}/</div>` : ''}
                </div>
            </div>`;
        });

        html += `</div></div>`;
    }
    container.innerHTML = html;
}

async function toggleRuleAPI(genre, ruleId, active) {
    try {
        await api.toggleTheoryRuleAPI(genre, ruleId, active);
        showNotification(`Regla ${active ? 'Activada' : 'Desactivada'}`, 'success');
    } catch (e) {
        showNotification("Error al cambiar regla", "error");
    }
}

async function addNewRuleAPI() {
    const genre = document.getElementById('new-rule-genre').value;
    const rule_id = document.getElementById('new-rule-id').value;
    const regex = document.getElementById('new-rule-regex').value;
    const message = document.getElementById('new-rule-msg').value;

    if (!genre || !rule_id || !regex) return showNotification("Faltan campos", "error");

    try {
        const data = await api.addTheoryRuleAPI({ genre, rule_id, regex, message });
        if (data.success) {
            showNotification("Regla añadida", "success");
            loadRules(); // Reload list
            // Clear inputs
            document.getElementById('new-rule-id').value = '';
            document.getElementById('new-rule-regex').value = '';
        } else {
            showNotification(data.message, "error");
        }
    } catch (e) {
        showNotification("Error añadiendo regla", "error");
    }
}

// --- CONTROLLER LOGIC ---

async function generatePattern(options = {}) {
    const btn = elements.generateBtn;

    // Check if Macro Mode is active via the toggle (Redundant check if called via handleGenerateClick, but safe)
    const isMacro = document.getElementById('macro-mode-toggle')?.checked;
    if (isMacro) {
        return generateMacroWave();
    }

    if (btn) {
        btn.disabled = true;
        btn.textContent = '🎲 GENERANDO...';
        document.body.classList.add('is-generating');
    }

    try {
        // --- LATENT SPACE BLEND (Phase 18) ---
        let blend = null;
        const blendMode = document.getElementById('blend-mode-toggle')?.checked;
        if (blendMode) {
            const genreA = document.getElementById('blend-genre-a').value;
            const genreB = document.getElementById('blend-genre-b').value;
            const sliderValue = parseInt(document.getElementById('blend-slider').value);

            // Slider: 0 = 100% A, 100 = 100% B
            const weightB = sliderValue / 100;
            const weightA = 1.0 - weightB;

            blend = {};
            blend[genreA] = weightA;
            blend[genreB] = weightB;

            logActivity(`🌀 Blend: ${Math.round(weightA * 100)}% ${genreA} + ${Math.round(weightB * 100)}% ${genreB}`);
        }

        const payload = {
            mode: state.genMode,
            pattern_type: state.patternType,
            density: state.config.density,
            complexity: state.config.complexity,
            tempo: state.config.tempo,
            style: state.config.style,
            blend: blend,  // NEW: Blend config
            use_ai: state.genMode === 'ai',
            temperature: state.config.temperature,
            intent: options.intent || null
        };

        // Activar LEDs de actividad
        const leds = document.querySelectorAll('.led-indicator');
        leds.forEach(led => led.classList.add('blink'));

        const data = await api.generatePatternAPI(payload);

        // Mantener LEDs encendidos (active) al recibir datos
        leds.forEach(led => {
            led.classList.remove('blink');
            led.classList.add('active');
            setTimeout(() => led.classList.remove('active'), 2000);
        });

        if (data.success) {
            // PUSH TO UNDO STACK
            if (state.lastPattern) undoStack.push(state.lastPattern);
            if (undoStack.length > 50) undoStack.shift(); // Limit stack size

            updateState('lastPattern', data.pattern);
            updateState('lastLayers', data.layers || []);
            updateState('isHallucination', data.is_hallucination || false);

            updateState('lastLayers', data.layers || []);
            updateState('isHallucination', data.is_hallucination || false);

            displayPattern(data.pattern, state.genMode, state.config.temperature, data.layers, data.is_hallucination, data.validation);

            if (data.thoughts) panels.renderThoughts(data.thoughts);
            if (data.insight) renderInsight(data.insight);
            if (window.particleEngine) window.particleEngine.burst();

            // Actualizar visuales de Hydra (Reactivo al código)
            visuals.updateVisuals(state, data.pattern);

            // Save to history for morph panel
            saveToHistory(data.pattern);

            // Update favorite button state
            updateFavoriteUI();

            logActivity(`Patrón generado (${state.config.style})`, 'success');
        } else {
            logActivity(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error generating:', error);
        logActivity('Error de conexión', 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '🎲 GENERAR PATRÓN';
            document.body.classList.remove('is-generating');
        }
    }
}


async function generateMacroWave() {
    const btn = elements.generateBtn;
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>🌊</span> ORQUESTANDO...';
        btn.classList.add('macro-generating');
    }

    try {
        logActivity('Iniciando Macro-Wave: Generando ensamble completo...', 'info');
        document.body.classList.add('is-generating');

        // Activar LEDs de actividad
        const leds = document.querySelectorAll('.led-indicator');
        leds.forEach(led => led.classList.add('blink'));

        const data = await api.generateMacroWaveAPI({
            style: state.config.style,
            density: state.config.density,
            complexity: state.config.complexity,
            tempo: state.config.tempo,
            use_ai: state.genMode === 'IA'
        });

        if (data.success) {
            // PUSH TO UNDO STACK
            if (state.lastPattern) undoStack.push(state.lastPattern);

            updateState('lastPattern', data.pattern);
            updateState('lastLayers', data.parts.map((p, i) => ({ id: `d${i + 1}`, code: p.pattern })) || []);

            displayPattern(data.pattern, state.genMode, state.config.temperature, state.lastLayers, false);

            if (data.thoughts) panels.renderThoughts(data.thoughts);
            if (data.insight) renderInsight(data.insight);

            if (window.particleEngine) window.particleEngine.burst();
            visuals.updateVisuals(state, data.pattern);

            logActivity(`Ensamble Macro-Wave generado (${state.config.style})`, 'success');
        } else {
            logActivity(`Error Macro: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error generating macro:', error);
        logActivity('Error de conexión Macro', 'error');
    } finally {
        if (btn) {
            const isMacro = document.getElementById('macro-mode-toggle')?.checked;
            btn.disabled = false;
            btn.innerHTML = isMacro ? '<span>🌊</span> GENERAR MACRO' : '🎲 GENERAR PATRÓN';
            btn.classList.remove('macro-generating');
            document.body.classList.remove('is-generating');
        }
    }
}

async function mutatePattern() {
    if (!state.lastPattern) return showNotification("No hay patrón para mutar", "error");

    const btn = elements.mutateBtn;
    if (btn) {
        btn.disabled = true;
        btn.textContent = '🧬 Mutando...';
    }

    try {
        const strength = elements.mutationStrength ? (parseFloat(elements.mutationStrength.value) / 100) : 0.5;
        const data = await api.mutatePatternAPI({
            pattern: state.lastPattern,
            strength: strength
        });

        if (data.success) {
            // PUSH TO UNDO STACK
            if (state.lastPattern) undoStack.push(state.lastPattern);

            updateState('lastPattern', data.pattern);
            updateState('lastLayers', data.layers || []);
            updateState('isHallucination', data.is_hallucination || false);

            displayPattern(data.pattern, 'Mutación 🧬', null, data.layers, data.is_hallucination);

            if (data.thoughts) panels.renderThoughts(data.thoughts);
            if (data.insight) renderInsight(data.insight);
            if (window.particleEngine) window.particleEngine.burst();

            const percent = (strength * 100).toFixed(0);
            logActivity(`Evolución aplicada (${percent}%)`, 'success');
        } else {
            logActivity(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error mutating:', error);
        logActivity('Error de conexión en mutación', 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '🧬 Mutar';
        }
    }
}

async function sendPattern() {
    if (!state.lastPattern) return;

    const targetIp = localStorage.getItem('target_ip') || '127.0.0.1';
    const targetPort = parseInt(localStorage.getItem('target_port') || '6010');

    try {
        await api.sendPatternAPI({
            channel: 'd1',
            pattern: state.lastPattern,
            morph: state.morphMode,
            target_ip: targetIp,
            target_port: targetPort
        });
        logActivity(state.morphMode ? 'Patrón Morfado enviado' : 'Patrón enviado a Tidal');
    } catch (e) {
        console.error(e);
        logActivity('Error de envío', 'error');
    }
}

let cycleIntervalId = null;

function toggleCycleSend() {
    const btn = elements.cycleSendBtn;
    if (!btn) return;

    if (cycleIntervalId) {
        clearInterval(cycleIntervalId);
        cycleIntervalId = null;
        btn.classList.remove('active', 'active-cycle');
        logActivity('Ciclo automático desactivado', 'info');
    } else {
        if (!state.lastPattern) {
            showNotification("No hay patrón para ciclar", "error");
            return;
        }

        btn.classList.add('active', 'active-cycle');
        logActivity('Ciclo automático activado (Live)', 'success');

        sendPattern();

        const msPerCycleBase = (bpm) => (60000 / bpm) * 4;

        const startCycleWithBPM = (bpm) => {
            return setInterval(() => {
                sendPattern();
                elements.sendBtn.classList.add('btn-pulse');
                setTimeout(() => elements.sendBtn.classList.remove('btn-pulse'), 200);
            }, msPerCycleBase(bpm));
        };

        cycleIntervalId = startCycleWithBPM(state.config.tempo || 120);

        subscribe((key, value) => {
            if (key === 'config.tempo' && cycleIntervalId) {
                clearInterval(cycleIntervalId);
                cycleIntervalId = startCycleWithBPM(value);
                logActivity(`Sincronizando ciclo a ${value} BPM`, 'info');
            }
        });
    }
}

function stopAll() {
    api.stopAllAPI().then(() => logActivity('Todos los canales detenidos', 'warning'));
}

// --- HELPERS ---

async function loadInitialData() {
    try {
        const favs = await api.getFavoritesAPI();
        if (favs.success) {
            updateState('favoritesList', favs.favorites);
            logActivity(`Favoritos cargados (${favs.favorites.length})`);
            renderFavoritesList();
        }
        modals.loadSystemConfig();
    } catch (e) {
        console.error('Error loading initial data:', e);
    }
}

function renderFavoritesList() {
    const list = document.getElementById('favorites-list');
    if (!list) return;

    if (!state.favoritesList || state.favoritesList.length === 0) {
        list.innerHTML = '<div style="padding:20px; text-align:center; color:#64748b;">No hay favoritos guardados aún.</div>';
        return;
    }

    list.innerHTML = '';
    state.favoritesList.forEach((fav, index) => {
        const item = document.createElement('div');
        item.className = 'preset-item';
        item.style.animationDelay = `${index * 0.05}s`;

        const type = fav.type || 'unknown';
        const icon = patternTypeIcons[type.split('_').pop()] || '🎵';

        item.innerHTML = `
            <div class="preset-info">
                <div class="preset-name">${icon} ${type.toUpperCase()}</div>
                <div class="preset-code" style="font-family: monospace; font-size: 0.75rem; color: #94a3b8; margin-top: 5px;">
                    ${fav.pattern.substring(0, 80)}${fav.pattern.length > 80 ? '...' : ''}
                </div>
            </div>
            <div style="display: flex; gap: 5px;">
                <button class="btn btn-primary btn-small" onclick="useFavoritePattern(${index})" title="Cargar">📥</button>
                <button class="btn btn-danger btn-small" onclick="deleteFavorite(${index})" title="Eliminar">🗑️</button>
            </div>
        `;
        list.appendChild(item);
    });
}

async function useFavoritePattern(index) {
    const fav = state.favoritesList[index];
    if (fav) {
        updateState('lastPattern', fav.pattern);
        displayPattern(fav.pattern);
        logActivity('Favorito cargado');
        actions.closeFavoritesModal();
    }
}

async function deleteFavorite(index) {
    const fav = state.favoritesList[index];
    if (fav) {
        if (confirm('¿Eliminar este favorito?')) {
            await api.deleteFavoriteAPI(fav.pattern);
            await loadInitialData();
            logActivity('Favorito eliminado');
        }
    }
}

function updateFavoriteUI() {
    if (!elements.favoriteBtn || !state.lastPattern) return;
    const isFav = state.favoritesList.some(f => f.pattern === state.lastPattern);

    if (isFav) {
        elements.favoriteBtn.classList.add('active');
    } else {
        elements.favoriteBtn.classList.remove('active');
    }
}

function displayPattern(pattern, mode, temp, layers, isHallu, validation) {
    updateFavoriteUI();
    if (!elements.patternOutput) return;

    let html = '';
    if (layers && layers.length > 1) {
        layers.forEach((l, i) => html += `<span style="color:#94a3b8">d${i + 1} $</span> ${l.code}\n`);
    } else {
        html = `<span style="color:#94a3b8">d1 $</span> ${pattern}`;
    }

    elements.patternOutput.innerHTML = html;

    // Flash effect
    elements.patternOutput.classList.remove('pattern-update-flash');
    void elements.patternOutput.offsetWidth;
    elements.patternOutput.classList.add('pattern-update-flash');

    // --- UPDATE THEORY BADGE (Phase 17) ---
    const badge = document.getElementById('theory-badge');
    if (badge && validation) {
        badge.classList.remove('hidden');
        if (validation.valid) {
            badge.classList.remove('warning');
            badge.querySelector('.theory-text').innerText = "Theoretically Verified";
            badge.querySelector('.theory-icon').innerText = "✅";
        } else {
            badge.classList.add('warning');
            badge.querySelector('.theory-text').innerText = "Theory Violation";
            badge.querySelector('.theory-icon').innerText = "⚠️";
            badge.title = validation.issues.join(", ");
        }
    } else if (badge) {
        badge.classList.add('hidden');
    }

    // --- ENABLE ACTION BUTTONS ---
    const actionButtons = [
        elements.sendBtn,
        elements.cycleSendBtn,
        elements.mutateBtn,
        elements.copyBtn,
        elements.favoriteBtn,
        elements.morphBtn
    ];
    actionButtons.forEach(btn => {
        if (btn) btn.disabled = false;
    });

    // --- CENTRALIZED TIMELINE UPDATE ---
    // Extract text from output to ensure it's what the user sees
    const currentCode = elements.patternOutput.textContent || pattern;
    renderTimeline('pattern-timeline', currentCode);

    // --- AUTO-UPDATE SAMPLE SCOUT (Phase 38) ---
    if (advanced && advanced.getSampleSuggestions) {
        advanced.getSampleSuggestions(pattern);
    }

    if (state.morphMode && elements.morphBtn) {
        elements.morphBtn.classList.add('active-morph');
    }

    // Persistencia visual del ciclo (v5.2)
    if (cycleIntervalId && elements.cycleSendBtn) {
        elements.cycleSendBtn.classList.add('active-cycle');
    }
}

// --- ACTIONS FOR UI ---

const actions = {
    generatePattern,
    sendPattern,
    mutatePattern,
    stopAll,
    changeGenMode: (mode) => {
        updateState('genMode', mode);
        elements.genModeBtns.forEach(b => b.classList.toggle('active', b.dataset.genmode === mode));
        // Limpiar panel de pensamientos al cambiar modo para evitar confusión
        if (mode === 'rules' && elements.thoughtsPanel) {
            panels.renderThoughts([]);
        }
    },
    selectPatternType: (type) => {
        updateState('patternType', type);
        elements.patternBtns.forEach(b => b.classList.toggle('active', b.dataset.type === type));
    },
    copyPattern: async () => {
        const text = state.lastPattern || elements.patternOutput.textContent;
        if (!text) return;
        try {
            await navigator.clipboard.writeText(text);
            showNotification('Copiado!', 'success');
        } catch (e) { console.error(e); }
    },
    toggleFavorite: async () => {
        if (!state.lastPattern) return;

        const patternToSave = state.lastPattern;
        // Robust check with trim
        const exists = state.favoritesList.some(f => f.pattern.trim() === patternToSave.trim());

        try {
            if (exists) {
                await api.deleteFavoriteAPI(patternToSave);
                logActivity('Eliminado de favoritos', 'info');
                if (elements.favoriteBtn) elements.favoriteBtn.classList.remove('active');
            } else {
                await api.addFavoriteAPI(patternToSave, state.config.style + "_" + state.patternType);
                logActivity(`Añadido a favoritos ⭐`, 'success');
                if (elements.favoriteBtn) elements.favoriteBtn.classList.add('active');
                if (window.particleEngine) window.particleEngine.burst();
            }
            // Delay slightly to allow DB transaction to settle
            setTimeout(async () => {
                await loadInitialData();
                updateFavoriteUI();
            }, 100);
        } catch (error) {
            console.error('Error toggling favorite:', error);
            logActivity('Error al guardar favorito', 'error');
        }
    },
    addManualPattern: async () => {
        const pattern = elements.patternOutput?.textContent?.replace(/^d\d+\s*\$\s*/, '').trim() || '';
        if (!pattern) return;

        const type = prompt('Tipo de patrón (drums, bass, melody, percussion, fx):', 'drums');
        if (!type) return;

        await api.addFavoriteAPI(pattern, type);
        logActivity('Patrón manual guardado');
        loadInitialData();
    },
    openHistoryModal: () => { advanced.openHistoryModal(); },
    openPresetsModal: () => { advanced.openPresetsModal(); },
    openFavoritesModal: () => {
        if (elements.favoritesModal) elements.favoritesModal.style.display = 'block';
        loadInitialData();
    },
    closeFavoritesModal: () => { if (elements.favoritesModal) elements.favoritesModal.style.display = 'none'; },
    openSamplesModal: () => {
        const m = document.getElementById('samples-modal');
        if (m) m.style.display = 'block';
    },
    closeSamplesModal: () => {
        const m = document.getElementById('samples-modal');
        if (m) m.style.display = 'none';
    },
    toggleCycleSend: () => { toggleCycleSend(); },
    toggleMorph: () => {
        state.morphMode = !state.morphMode;
        const btn = document.getElementById('morph-btn');
        if (btn) {
            if (state.morphMode) {
                btn.classList.add('active-morph');
                logActivity('Modo MORPH activado (Suavizado de transiciones)');
            } else {
                btn.classList.remove('active-morph');
                logActivity('Modo MORPH desactivado');
            }
        }
    }
};

// --- INIT ---

export function init() {
    console.log('🚀 Initializing Modular v5.2 Frontend');

    // Exponer acciones globalmente para compatibilidad con eventos inline
    window.actions = actions;

    initUI(actions);
    initThemeEngine();
    visuals.initHydra();
    conductor.initConductor();
    loadInitialData();

    // Reaccionar a cambios de estilo en tiempo real para Hydra
    subscribe((key, value) => {
        if (key === 'config.style') {
            visuals.updateVisuals(state);
        }
    });

    // Initial Theme
    updateTheme(state.config.style);

    // Status Loop
    const checkStatus = async () => {
        try {
            const status = await api.checkStatusAPI();
            updateStatusUI(status.osc);
        } catch (e) { }
    };

    checkStatus(); // Immediate check
    setInterval(checkStatus, 5000);

    // Oracle Input Listener
    const oracleInput = document.getElementById('oracle-input');
    if (oracleInput) {
        oracleInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                advanced.handleOracleInput(generatePattern);
            }
        });
    }

    // Initialize Luxury Knobs (visual only - no auto-update)
    const knobs = initAllKnobs();

    // Store knob instances by ID (AUTO-MAPPING)
    // This maps 'knob-gain' -> window.visualKnobs.gain, etc.
    window.visualKnobs = {};
    knobs.forEach(knob => {
        const id = knob.element.id; // e.g., 'knob-gain'
        if (id && id.startsWith('knob-')) {
            const key = id.replace('knob-', ''); // 'gain'
            window.visualKnobs[key] = knob;
        }
    });

    // Toggle Advanced Controls
    const toggleAdvancedBtn = document.getElementById('toggle-advanced-btn');
    const advancedControls = document.getElementById('advanced-controls');
    if (toggleAdvancedBtn && advancedControls) {
        toggleAdvancedBtn.addEventListener('click', () => {
            const isExpanded = advancedControls.style.display !== 'none';
            advancedControls.style.display = isExpanded ? 'none' : 'grid';
            toggleAdvancedBtn.textContent = isExpanded ? '⬇️ Advanced' : '⬆️ Close';
        });
    }

    // Apply Visuals Button - reads knob values and updates Hydra ONCE
    const applyVisualsBtn = document.getElementById('apply-visuals-btn');
    if (applyVisualsBtn) {
        applyVisualsBtn.addEventListener('click', () => {
            // Core values
            const gainValue = window.visualKnobs.gain?.value || 50;
            const decayValue = window.visualKnobs.decay?.value || 30;
            const colorValue = window.visualKnobs.color?.value || 0;
            const symmValue = window.visualKnobs.symmetry?.value || 2;

            // Advanced values (column 2)
            const brightValue = window.visualKnobs.brightness?.value || 100;
            const contrastValue = window.visualKnobs.contrast?.value || 100;
            const blurValue = window.visualKnobs.blur?.value || 0;
            const scaleValue = window.visualKnobs.scale?.value || 100;
            const rotateValue = window.visualKnobs.rotate?.value || 0;
            const pixelateValue = window.visualKnobs.pixelate?.value || 0;

            // Dramatic effects (column 3)
            const invertValue = window.visualKnobs.invert?.value || 0;
            const saturateValue = window.visualKnobs.saturate?.value || 100;
            const posterizeValue = window.visualKnobs.posterize?.value || 20;
            const shiftxValue = window.visualKnobs.shiftx?.value || 0;
            const modulateValue = window.visualKnobs.modulate?.value || 0;

            // Update state with CORRECTED MAPPINGS
            // Core (0-100 → 0-1)
            // Update state with CORRECTED MAPPINGS
            // Core (0-100 → 0-1)
            updateConfig('visualGain', gainValue / 100);
            updateConfig('visualDecay', decayValue / 100);
            updateConfig('visualColor', colorValue / 100);
            updateConfig('visualSymmetry', parseInt(symmValue));

            // Advanced column 2
            updateConfig('visualBrightness', brightValue / 100);  // 50-200 → 0.5-2.0
            updateConfig('visualContrast', contrastValue / 100);  // 50-300 → 0.5-3.0
            updateConfig('visualBlur', blurValue);                // 0-10 stays 0-10
            updateConfig('visualScale', scaleValue / 100);        // 50-200 → 0.5-2.0
            updateConfig('visualRotateSpeed', rotateValue);       // -5 to 5 stays as is
            updateConfig('visualPixelate', pixelateValue);        // 0-50 stays 0-50

            // Dramatic column 3
            updateConfig('visualInvert', invertValue / 100);      // 0-100 → 0-1
            updateConfig('visualSaturate', saturateValue / 100);  // 0-200 → 0-2
            updateConfig('visualPosterize', posterizeValue);      // 2-20 stays as is
            updateConfig('visualShiftX', shiftxValue / 100);      // -50 to 50 → -0.5 to 0.5
            updateConfig('visualModulate', modulateValue / 100);  // 0-100 → 0-1

            // Single Hydra update
            visuals.updateVisuals(state);

            // Button feedback
            applyVisualsBtn.style.transform = 'scale(0.95)';
            setTimeout(() => applyVisualsBtn.style.transform = 'scale(1)', 100);
        });
    }

    // Escape key to close all modals and panels
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal, .floating-panel').forEach(m => {
                if (window.getComputedStyle(m).display !== 'none') {
                    m.style.display = 'none';
                    logActivity('Ventana cerrada (Esc)');
                }
            });
        }
    });

    // --- LATENT SPACE UI LISTENERS (Phase 18) ---
    const blendToggle = document.getElementById('blend-mode-toggle');
    const blendControls = document.getElementById('blend-controls');
    const blendSlider = document.getElementById('blend-slider');
    const weightALabel = document.getElementById('blend-weight-a');
    const weightBLabel = document.getElementById('blend-weight-b');

    if (blendToggle && blendControls) {
        blendToggle.addEventListener('change', (e) => {
            blendControls.style.display = e.target.checked ? 'block' : 'none';
            logActivity(e.target.checked ? '🌀 Modo Blend activado' : 'Modo Blend desactivado');
        });
    }

    if (blendSlider && weightALabel && weightBLabel) {
        blendSlider.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            const weightB = val;
            const weightA = 100 - val;
            weightALabel.textContent = `${weightA}%`;
            weightBLabel.textContent = `${weightB}%`;
        });
    }

    // --- LEGACY SHIMS (Para soportar index.html onclicks y otros scripts) ---
    window.state = state;
    window.elements = elements;
    window.logActivity = logActivity;
    window.showNotification = showNotification;
    window.updateTheme = updateTheme;
    window.patternTypeIcons = patternTypeIcons;

    window.generatePattern = actions.generatePattern;
    window.generateMacroWave = generateMacroWave;
    window.sendPattern = actions.sendPattern;
    window.mutatePattern = actions.mutatePattern;
    window.stopAll = actions.stopAll;
    window.changeGenMode = actions.changeGenMode;
    window.selectPatternType = actions.selectPatternType;

    window.openFavoritesModal = actions.openFavoritesModal;
    window.closeFavoritesModal = actions.closeFavoritesModal;
    window.useFavoritePattern = useFavoritePattern;
    window.deleteFavorite = deleteFavorite;
    window.toggleFavorite = actions.toggleFavorite;

    // Exponer funciones Phase 3 (Visualizer)
    window.openVisualizerModal = phase3.openVisualizerModal;
    window.closeVisualizerModal = phase3.closeVisualizerModal;

    // Exponer funciones Evolution (Nuevo)
    window.triggerEvolution = async () => {
        if (!confirm('¿Iniciar ciclo de evolución manual? Esto entrenará a la IA con tus favoritos.')) return;
        try {
            const res = await api.triggerEvolutionAPI();
            if (res.success) {
                showNotification(`Evolución completada. ${res.survivors} supervivientes.`, 'success');
                logActivity('🧬 Evolución manual completada con éxito');
            } else {
                showNotification('Error en evolución: ' + res.error, 'error');
            }
        } catch (e) {
            console.error(e);
            showNotification('Error de conexión', 'error');
        }
    };

    // Modals
    window.openSettingsModal = modals.openSettingsModal;
    window.closeSettingsModal = modals.closeSettingsModal;
    window.saveSystemConfig = modals.saveSystemConfig;
    window.openBrainModal = modals.openBrainModal;
    window.closeBrainModal = modals.closeBrainModal;

    // Panels
    window.openLexiconModal = panels.openLexiconModal;
    window.closeLexiconModal = panels.closeLexiconModal;
    window.openSongTemplatesModal = panels.openSongTemplatesModal;
    window.closeSongTemplatesModal = panels.closeSongTemplatesModal;
    window.generateSong = panels.generateSong;
    window.openComparatorModal = panels.openComparatorModal;
    window.closeComparatorModal = panels.closeComparatorModal;
    window.selectPatternForComparison = panels.selectPatternForComparison;
    window.usePatternFromComparator = panels.usePatternFromComparator;
    window.toggleMorphPanel = panels.toggleMorphPanel;
    window.closeMorphPanel = panels.closeMorphPanel;
    window.generateMorph = panels.generateMorph;
    window.sendMorphedPattern = panels.sendMorphedPattern;
    window.toggleBrainPanel = panels.toggleBrainPanel;
    window.closeBrainPanel = panels.closeBrainPanel;

    window.openVisualizerModal = phase3.openVisualizerModal;
    window.closeVisualizerModal = phase3.closeVisualizerModal;
    window.loadFavorites = loadInitialData;

    // Secondary Tools Shims
    window.openHistoryModal = advanced.openHistoryModal;
    window.closeHistoryModal = advanced.closeHistoryModal;
    window.useHistoryPattern = advanced.useHistoryPattern;
    window.addHistoryToFavorites = advanced.addHistoryToFavorites;
    window.clearHistory = advanced.clearHistory;
    window.exportHistory = advanced.exportHistory;

    window.openPresetsModal = advanced.openPresetsModal;
    window.closePresetsModal = advanced.closePresetsModal;
    window.savePreset = advanced.savePreset;
    window.loadPresets = advanced.loadPresets;
    window.loadPreset = advanced.loadPreset;
    window.deletePreset = advanced.deletePreset;

    window.generateBatch = advanced.generateBatch;
    window.closeBatchModal = advanced.closeBatchModal;
    window.addSelectedToFavorites = advanced.addSelectedToFavorites;
    window.useBatchPattern = advanced.useBatchPattern;

    window.toggleEditor = advanced.toggleEditor;
    window.reindexSamples = advanced.reindexSamples;

    window.openJamSessionModal = phase2.openJamSessionModal;
    window.closeJamSessionModal = phase2.closeJamSessionModal;
    window.startJamSession = phase2.startJamSession;
    window.stopJamSession = phase2.stopJamSession;

    window.createBackup = phase2.createBackup;
    window.openRestoreModal = phase2.openRestoreModal;
    window.closeRestoreModal = phase2.closeRestoreModal;

    // Validate / Rules Shims (Phase 17b)
    window.openRulesModal = () => {
        document.getElementById('rules-modal').style.display = 'block';
        loadRules();
    };
    window.closeRulesModal = () => { document.getElementById('rules-modal').style.display = 'none'; };
    window.toggleRuleAPI = toggleRuleAPI;
    window.addNewRuleAPI = addNewRuleAPI;
    window.restoreBackup = phase2.restoreBackup;
    window.toggleCorpusStats = phase2.toggleCorpusStats;

    window.openFavoritesModal = actions.openFavoritesModal;
    window.closeFavoritesModal = actions.closeFavoritesModal;
    window.toggleFavorite = actions.toggleFavorite;
    window.addManualPattern = actions.addManualPattern;
    window.openSamplesModal = actions.openSamplesModal;
    window.closeSamplesModal = actions.closeSamplesModal;
    window.showSampleList = advanced.showSampleList;
    window.showSCConfig = advanced.showSCConfig;
    window.saveSamples = advanced.saveSamples;
    window.copySCCode = advanced.copySCCode;

    // Helper shim for the pattern display
    window.displayPattern = displayPattern;
}

// Start app
init();

// Initialize timeline visualizer
initTimeline('pattern-timeline');

// Initialize keyboard shortcuts
initKeyboardShortcuts();

// Initialize Arranger (Phase 19)
initArranger();

// --- OSC STATUS POLLING ---
async function checkOSCStatus() {
    try {
        const response = await fetch('/api/osc/status');
        const status = await response.json();
        if (window.updateStatusUI) window.updateStatusUI(status.connected, status.connected ? 'Online' : 'Offline');
    } catch (e) {
        if (window.updateStatusUI) window.updateStatusUI(false, 'Error');
    }
}
setInterval(checkOSCStatus, 5000);
checkOSCStatus();

// --- SESSION HISTORY (UNDO/REDO) ---
window.sessionHistory = {
    stack: [],
    index: -1,
    max: 20,
    push(pattern) {
        if (!pattern || this.stack[this.index] === pattern) return;
        if (this.index < this.stack.length - 1) {
            this.stack = this.stack.slice(0, this.index + 1);
        }
        this.stack.push(pattern);
        if (this.stack.length > this.max) this.stack.shift();
        else this.index++;
    },
    undo() {
        if (this.index > 0) {
            this.index--;
            const pattern = this.stack[this.index];
            if (window.displayPattern) window.displayPattern(pattern, 'Deshacer (History)', null);
            if (window.logActivity) window.logActivity('Historial: Undo', 'info');
        }
    },
    redo() {
        if (this.index < this.stack.length - 1) {
            this.index++;
            const pattern = this.stack[this.index];
            if (window.displayPattern) window.displayPattern(pattern, 'Rehacer (History)', null);
            if (window.logActivity) window.logActivity('Historial: Redo', 'info');
        }
    }
};

// --- SESSION RECORDER (Export .tidal) ---
window.sessionRecorder = {
    isRecording: false,
    buffer: [],
    start() {
        this.isRecording = true;
        this.buffer = [];
        this.buffer.push(`-- TidalAI Session Export - ${new Date().toLocaleString()}`);
        this.buffer.push('-- BPM: ' + (document.getElementById('param-tempo')?.value || 140));
        this.buffer.push('setcps (140/60/4)');
        this.buffer.push('');
        if (window.showNotification) window.showNotification("🔴 Grabando sesión (.tidal)", "info");
    },
    stop() {
        this.isRecording = false;
        if (window.showNotification) window.showNotification("⏹ Grabación finalizada", "info");
    },
    add(pattern, info) {
        if (!this.isRecording) return;
        const timestamp = new Date().toLocaleTimeString();
        this.buffer.push(`-- [${timestamp}] ${info || 'Pattern'}`);
        this.buffer.push(pattern);
        this.buffer.push('hush'); // Optional: Add hush or assume user handles it
        this.buffer.push('');
    },
    download() {
        if (this.buffer.length === 0) {
            alert("No hay patrones grabados en esta sesión.");
            return;
        }
        const text = this.buffer.join('\n');
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tidal_session_${Date.now()}.tidal`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};



// --- LUXURY v5 UTILS ---
// --- ACCIONES DE PERFORMANCE ---

// Comentado para evitar colisión con la nueva implementación en actions
// window.actions.toggleMorph = function () { ... }

window.toggleHydraBg = function () {
    document.body.classList.toggle('hydra-bg-active');
    const isActive = document.body.classList.contains('hydra-bg-active');
    if (window.logActivity) {
        window.logActivity(isActive ? "Activando modo inmersivo" : "Regresando a modo estándar", "info");
    }
};

window.toggleActivityPanel = function () {
    const panel = document.getElementById('activity-panel');
    if (panel) {
        const isVisible = panel.style.display === 'flex';
        panel.style.display = isVisible ? 'none' : 'flex';
    }
};

function renderInsight(text) {
    const panel = document.getElementById('insight-panel');
    const content = document.getElementById('insight-content');
    if (panel && content) {
        content.textContent = text;
        panel.classList.remove('hidden');
        // Efecto de escritura simple o flash
        content.style.opacity = 0;
        setTimeout(() => content.style.opacity = 1, 100);
    }
}

// Save pattern to history for morph panel
// Save pattern to history (Deprecated: Saved by Server DB now)
function saveToHistory(pattern) {
    // console.log("History saved by server");
}

/* --- DATA MIGRATION (LocalStorage -> SQLite) --- */
window.checkDataMigration = async function () {
    if (localStorage.getItem('db_migration_done')) return;

    // Check if there is data to migrate
    const historyStr = localStorage.getItem('pattern_history');
    const favoritesStr = localStorage.getItem('pattern_favorites');

    if (!historyStr && !favoritesStr) {
        localStorage.setItem('db_migration_done', 'true');
        return;
    }

    try {
        if (window.showNotification) window.showNotification("📦 Migrando datos a Base de Datos...", "info");
        if (window.logActivity) window.logActivity("📦 Migrando datos a Base de Datos...", "info");

        const history = historyStr ? JSON.parse(historyStr) : [];
        const favorites = favoritesStr ? JSON.parse(favoritesStr) : [];

        const payload = {
            history: history.map(h => typeof h === 'string' ? { pattern: h } : h),
            favorites: favorites.map(f => typeof f === 'string' ? { pattern: f } : f)
        };

        const res = await fetch('/api/data/import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (data.success) {
            localStorage.setItem('db_migration_done', 'true');
            const msg = `✅ Migración completada: ${data.imported.history} en historial, ${data.imported.favorites} favoritos.`;
            if (window.showNotification) window.showNotification(msg, "success");
            if (window.logActivity) window.logActivity(msg);

            // Optional: Clear old method storage
            // localStorage.removeItem('pattern_history');
            // localStorage.removeItem('pattern_favorites');
        }
    } catch (e) {
        console.error("Migration failed:", e);
        if (window.showNotification) window.showNotification("❌ Error crítico en migración", "error");
    }
}
// --- OSC RECORDING (User Requested) ---
let isOSCRecording = false;
window.toggleOSCRecording = async function () {
    isOSCRecording = !isOSCRecording;
    const btn = document.getElementById('rec-osc-btn');
    const value = isOSCRecording ? 1 : 0;

    // UI Feedback
    if (isOSCRecording) {
        if (btn) {
            btn.innerText = "⏹";
            btn.classList.add('blink-active');
            btn.style.color = '#ef4444'; // Red
        }
        if (window.showNotification) window.showNotification("🔴 REC iniciado (OSC /record 1)", "warning");
    } else {
        if (btn) {
            btn.innerText = "🔴";
            btn.classList.remove('blink-active');
            btn.style.color = '';
        }
        if (window.showNotification) window.showNotification("⏹ REC detenido (OSC /record 0)", "info");
    }

    // Send OSC
    try {
        await fetch('/api/osc/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                address: "/record",
                args: [value]
            })
        });
    } catch (e) {
        console.error("Error sending OSC Record:", e);
        if (window.showNotification) window.showNotification("Error enviando señal REC", "error");
    }
};

// --- LOG MARKER (Highlights) ---
window.addLogMarker = function () {
    // 1. Add to Session Recording if active
    if (window.sessionRecorder && window.sessionRecorder.isRecording) {
        window.sessionRecorder.add("-- 🚩 [HIGHLIGHT MARKER] 🚩", "MARKER");
    }

    // 2. Visual Feedback
    if (window.showNotification) window.showNotification("🚩 Marcador añadido al log", "success");
    if (window.logActivity) window.logActivity("🚩 Marcador de usuario insertado", "warning");

    // 3. Button Animation
    const btn = document.getElementById('add-marker-btn');
    if (btn) {
        btn.classList.add('pulse-once');
        setTimeout(() => btn.classList.remove('pulse-once'), 500);
    }
};

// --- NANO TOOLS (Undo, Lock, Copy) ---
let undoStack = [];
let isGenerationLocked = false;

window.toggleLock = function () {
    isGenerationLocked = !isGenerationLocked;
    const btn = document.getElementById('lock-btn');
    const generateBtn = document.getElementById('generate-btn');

    if (isGenerationLocked) {
        if (btn) {
            btn.classList.add('locked');
            btn.style.color = '#f59e0b'; // Amber
            btn.style.borderColor = '#f59e0b';
        }
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.style.opacity = '0.5';
            generateBtn.innerText = "🔒 LOCKED";
        }
        if (window.showNotification) window.showNotification("🔒 Generación Bloqueada (Freeze)", "warning");
    } else {
        if (btn) {
            btn.classList.remove('locked');
            btn.style.color = '';
            btn.style.borderColor = '';
        }
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.style.opacity = '1';
            generateBtn.innerText = "🎲 GENERAR PATRÓN";
        }
        if (window.showNotification) window.showNotification("🔓 Generación Desbloqueada", "info");
    }
};

window.undoPattern = function () {
    if (undoStack.length === 0) {
        if (window.showNotification) window.showNotification("No hay nada que deshacer", "warning");
        return;
    }

    // Pop last state
    const lastState = undoStack.pop();

    // Bypass lock for undo
    const wasLocked = isGenerationLocked;
    isGenerationLocked = false;

    // Restore text directly
    const output = document.getElementById('pattern-output');
    if (output) output.innerText = lastState;

    // Log
    if (window.logActivity) window.logActivity("Undo realizado ↩️", "info");

    isGenerationLocked = wasLocked;
};

window.copyPattern = function () {
    const output = document.getElementById('pattern-output');
    if (!output) return;

    const text = output.innerText;
    navigator.clipboard.writeText(text).then(() => {
        if (window.showNotification) window.showNotification("📋 Copiado al portapapeles", "success");
        const btn = document.getElementById('copy-nano-btn');
        if (btn) {
            btn.innerText = "✅";
            setTimeout(() => btn.innerText = "📋", 1000);
        }
    }).catch(err => {
        console.error('Error copying:', err);
        if (window.showNotification) window.showNotification("Error al copiar", "error");
    });
};

// Hook displayPattern to save to history AND Recorder AND Undo Stack AND Check Lock
const originalDisplayPattern = window.displayPattern;
if (originalDisplayPattern) {
    window.displayPattern = function (pattern, info, temp) {
        // LOCK CHECK
        if (isGenerationLocked) {
            console.log("Generation blocked by Lock/Freeze");
            if (window.showNotification) window.showNotification("🔒 Generación bloqueada por usuario", "warning");
            return;
        }

        // UNDO PUSH
        const output = document.getElementById('pattern-output');
        if (output && output.innerText && output.innerText.trim() !== "") {
            undoStack.push(output.innerText);
            if (undoStack.length > 20) undoStack.shift(); // Limit stack size
        }

        originalDisplayPattern(pattern, info, temp);
        if (window.sessionHistory) window.sessionHistory.push(pattern);
        if (window.sessionRecorder) window.sessionRecorder.add(pattern, info);
    };
}

// Run migration check
setTimeout(window.checkDataMigration, 2000);


// End of Modular Studio Core

