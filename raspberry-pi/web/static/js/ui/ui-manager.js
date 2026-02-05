import { updateConfig, updateState } from '../core/state.js';
import { updateTheme } from '../modules/theme-engine.js';

// TidalAI UI Icons
export const patternTypeIcons = {
    'drums': '🥁',
    'bass': '🎸',
    'melody': '🎹',
    'percussion': '🪘',
    'fx': '✨',
    'unknown': '🎵'
};

export const elements = {
    genModeBtns: document.querySelectorAll('[data-genmode]'),
    // ... (Lazy load or init explicitly)
    temperatureSlider: document.getElementById('temperature'),
    temperatureValue: document.getElementById('temperature-value'),
    densitySlider: document.getElementById('density'),
    densityValue: document.getElementById('density-value'),
    complexitySlider: document.getElementById('complexity'),
    complexityValue: document.getElementById('complexity-value'),
    tempoSlider: document.getElementById('tempo'),
    tempoValue: document.getElementById('tempo-value'),
    styleSelect: document.getElementById('style'),
    generateBtn: document.getElementById('generate-btn'),
    sendBtn: document.getElementById('send-btn'),
    cycleSendBtn: document.getElementById('cycle-send-btn'),
    morphBtn: document.getElementById('morph-btn'),
    stopBtn: document.getElementById('stop-btn'),
    copyBtn: document.getElementById('copy-btn'),
    favoriteBtn: document.getElementById('favorite-btn'),
    retrainBtn: document.getElementById('retrain-btn'),
    mutateBtn: document.getElementById('mutate-btn'),
    mutationStrength: document.getElementById('mutation-strength'),
    mutationValue: document.getElementById('mutation-value'),
    oracleInput: document.getElementById('oracle-input'),
    addManualBtn: document.getElementById('add-manual-btn'),
    viewFavoritesBtn: document.getElementById('view-favorites-btn'),
    closeModal: document.getElementById('close-modal'),
    favoritesModal: document.getElementById('favorites-modal'),
    settingsModal: document.getElementById('settings-modal'),
    oscStatus: document.getElementById('osc-status'),
    oscStatusText: document.getElementById('osc-status-text'),
    activityLog: document.getElementById('activity-log'),
    patternOutput: document.getElementById('pattern-output'),
    patternInfo: document.getElementById('pattern-info'),
    patternMode: document.getElementById('pattern-mode'),
    favoritesList: document.getElementById('favorites-list'),
    favoritesCount: document.getElementById('favorites-count'),
    favoritesFilter: document.getElementById('favorites-filter'),
    targetIpInput: document.getElementById('target-ip'),
    targetPortInput: document.getElementById('target-port'),
    // Note: settingsModal is duplicated here, keeping the first one.

    // Panels & Modals
    brainPanel: document.getElementById('brain-panel'),
    morphPanel: document.getElementById('morph-panel'),
    lexiconModal: document.getElementById('lexicon-modal'),
    thoughtsPanel: document.getElementById('thoughts-panel'),
    thoughtsContent: document.getElementById('thoughts-content'),

    // Advanced Tools
    historyModal: document.getElementById('history-modal'),
    presetsModal: document.getElementById('presets-modal'),
    // Note: favoritesModal is duplicated here, keeping the first one.
    batchModal: document.getElementById('batch-modal'),
    jamModal: document.getElementById('jam-modal'),
    songTemplatesModal: document.getElementById('song-templates-modal'),
    comparatorModal: document.getElementById('comparator-modal'),

    // Containers
    historyList: document.getElementById('history-list'),
    presetsList: document.getElementById('presets-list'),
    // Note: favoritesList is duplicated here, keeping the first one.
    batchList: document.getElementById('batch-list'),
    templatesList: document.getElementById('templates-list'),

    sampleScoutPanel: document.getElementById('sample-scout-panel'),
    sampleSuggestions: document.getElementById('sample-suggestions'),

    musicalFriction: document.getElementById('musical-friction'),
    frictionValue: document.getElementById('friction-value')
};

export function initUI(actions) {
    const acts = actions; // Define early

    // Mode Selection
    elements.genModeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.genmode;
            actions.changeGenMode(mode);
            // UI Visual update should happen via subscription to state, 
            // but for now we can do it optimistically or expect main to call updateUI
        });
    });

    // Pattern Type
    elements.patternBtns = document.querySelectorAll('.pattern-btn');
    elements.patternBtns.forEach(btn => {
        btn.addEventListener('click', () => acts.selectPatternType(btn.dataset.type));
    });

    // Sliders
    elements.densitySlider.addEventListener('input', (e) => {
        elements.densityValue.textContent = e.target.value + '%';
        updateConfig('density', e.target.value / 100);
    });

    elements.complexitySlider.addEventListener('input', (e) => {
        elements.complexityValue.textContent = e.target.value + '%';
        updateConfig('complexity', e.target.value / 100);
    });

    elements.tempoSlider.addEventListener('input', (e) => {
        elements.tempoValue.textContent = e.target.value;
        updateConfig('tempo', parseInt(e.target.value));
    });

    elements.temperatureSlider.addEventListener('input', (e) => {
        elements.temperatureValue.textContent = e.target.value;
        updateConfig('temperature', parseFloat(e.target.value));
    });

    if (elements.mutationStrength) {
        elements.mutationStrength.addEventListener('input', (e) =>
            elements.mutationValue.textContent = e.target.value + '%'
        );
    }

    elements.styleSelect.addEventListener('change', (e) => {
        updateConfig('style', e.target.value);
        updateTheme(e.target.value);
    });

    // Segmented Mode Selector Logic
    const modeSelector = document.querySelector('.mode-selector-luxury');
    const segments = document.querySelectorAll('.mode-segment');
    const macroToggle = document.getElementById('macro-mode-toggle');

    if (modeSelector && segments && macroToggle) {
        segments.forEach(segment => {
            segment.addEventListener('click', () => {
                const mode = segment.dataset.mode;
                const isMacro = mode === 'macro';

                // Update segments
                segments.forEach(s => s.classList.toggle('active', s === segment));
                modeSelector.setAttribute('data-active', mode);

                // Update hidden toggle for backward compatibility
                macroToggle.checked = isMacro;

                // Update Generate Button
                const genBtn = elements.generateBtn;
                if (genBtn) {
                    if (isMacro) {
                        genBtn.innerHTML = '<span>🌊</span> GENERAR MACRO';
                        genBtn.classList.add('macro-active');
                    } else {
                        genBtn.innerHTML = '🎲 GENERAR PATRÓN';
                        genBtn.classList.remove('macro-active');
                    }
                }

                if (window.logActivity) {
                    window.logActivity(isMacro ? "Modo Macro-Wave Activado" : "Modo Solo Activado", isMacro ? "success" : "info");
                }
            });
        });
    }

    if (elements.musicalFriction) {
        elements.musicalFriction.addEventListener('input', (e) => {
            elements.frictionValue.textContent = e.target.value + '%';
            updateConfig('musicalFriction', e.target.value / 100);
        });
    }

    // Actions
    if (elements.generateBtn) elements.generateBtn.addEventListener('click', () => acts.generatePattern());
    elements.sendBtn.addEventListener('click', () => acts.sendPattern());
    elements.stopBtn.addEventListener('click', () => acts.stopAll());
    elements.copyBtn.addEventListener('click', () => acts.copyPattern());
    elements.mutateBtn.addEventListener('click', () => acts.mutatePattern());

    if (elements.cycleSendBtn) {
        elements.cycleSendBtn.addEventListener('click', () => acts.toggleCycleSend());
    }
    if (elements.morphBtn) {
        elements.morphBtn.addEventListener('click', () => acts.toggleMorph());
    }
    if (elements.favoriteBtn) elements.favoriteBtn.addEventListener('click', actions.toggleFavorite);
    if (elements.viewFavoritesBtn) elements.viewFavoritesBtn.addEventListener('click', actions.openFavoritesModal);
    if (elements.closeModal) elements.closeModal.addEventListener('click', actions.closeFavoritesModal);

    // acts = actions; // Moved up
}

// Update Status UI (Now supports True Reachability)
export function updateStatusUI(oscStatus, msg) {
    if (!elements.oscStatus) return;

    const connected = oscStatus?.connected;
    const reachable = oscStatus?.reachable;

    // Reset classes
    elements.oscStatus.classList.remove('online', 'offline', 'warning');

    if (reachable) {
        // Ping Success -> Green
        elements.oscStatus.classList.add('status-indicator', 'online');
        if (elements.oscStatusText) elements.oscStatusText.textContent = msg || 'Online';
        elements.oscStatus.style.backgroundColor = ''; // Reset inline
        elements.oscStatus.style.boxShadow = '';
    } else if (connected) {
        // UDP Ready but Ping Fail -> Orange (Likely Firewall)
        elements.oscStatus.classList.add('status-indicator', 'warning'); // CSS needs to support this or use offline style with diff color
        // If no 'warning' class in CSS yet, we can inline style or reuse
        elements.oscStatus.style.backgroundColor = '#f59e0b'; // Amber
        elements.oscStatus.style.boxShadow = '0 0 10px #f59e0b';
        if (elements.oscStatusText) elements.oscStatusText.textContent = msg || 'UDP Ready (No Ping)';
    } else {
        // Init Fail -> Red
        elements.oscStatus.classList.add('status-indicator', 'offline');
        elements.oscStatus.style.backgroundColor = ''; // Reset inline
        elements.oscStatus.style.boxShadow = '';
        if (elements.oscStatusText) elements.oscStatusText.textContent = msg || 'Offline';
    }
}

// Expose modal functions to window for HTML onclick handlers
import * as modals from './modals.js';
window.openSettingsModal = modals.openSettingsModal;
window.closeSettingsModal = modals.closeSettingsModal;
window.saveSystemConfig = modals.saveSystemConfig;
window.openBrainModal = modals.openBrainModal;
window.closeBrainModal = modals.closeBrainModal;
