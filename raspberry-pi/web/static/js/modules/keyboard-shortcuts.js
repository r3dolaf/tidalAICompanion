/**
 * Keyboard Shortcuts System
 * Handles global keyboard shortcuts for TidalAI Studio
 */

// Shortcut definitions
const SHORTCUTS = {
    // Generation & Modes
    'ctrl+g': { action: 'generate', description: 'Generar patrón' },
    'ctrl+m': { action: 'toggleMacro', description: 'Toggle Macro Mode' },
    'ctrl+shift+m': { action: 'mutate', description: 'Mutar patrón' },
    'ctrl+p': { action: 'patternMode', description: 'Modo Pattern (desactiva Macro)' },
    'ctrl+z': { action: 'undo', description: 'Deshacer (History)' },
    'ctrl+y': { action: 'redo', description: 'Rehacer (History)' },
    'ctrl+shift+z': { action: 'redo', description: 'Rehacer (History)' },

    // Pattern Actions
    'ctrl+enter': { action: 'send', description: 'Enviar a TidalCycles' },
    'ctrl+f': { action: 'toggleFavorite', description: 'Toggle favorito' },

    // Navigation & Panels
    'ctrl+h': { action: 'openHistory', description: 'Abrir Historial' },
    'ctrl+shift+f': { action: 'openFavorites', description: 'Abrir Favoritos' },
    'ctrl+o': { action: 'focusOracle', description: 'Focus en Oracle' },
    'ctrl+r': { action: 'openRules', description: 'Abrir Reglas' },
    'escape': { action: 'closeModal', description: 'Cerrar modal/panel' },
    'alt+1': { action: 'tabVisuals', description: 'Panel Visuales (Bento)' },
    'alt+2': { action: 'tabInstruments', description: 'Panel Instrumentos (Bento)' },

    // Tools
    'ctrl+shift+o': { action: 'openMorph', description: 'Abrir Morfador' },
    'ctrl+j': { action: 'openJam', description: 'Abrir Jam Session' },
    'ctrl+b': { action: 'openBatch', description: 'Abrir Batch Generator' },

    // Utilities
    'ctrl+/': { action: 'showHelp', description: 'Mostrar ayuda de atajos' },
    'ctrl+l': { action: 'clearLog', description: 'Limpiar Activity Log' }
};

// Current pressed keys
let pressedKeys = new Set();

/**
 * Initialize keyboard shortcuts system
 */
export function initKeyboardShortcuts() {
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    console.log('⌨️ Keyboard shortcuts initialized');
}

/**
 * Handle key down event
 */
function handleKeyDown(e) {
    // Don't trigger shortcuts when typing in inputs/textareas
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        // Exception: Ctrl+Enter should work in inputs
        if (!(e.ctrlKey && e.key === 'Enter')) {
            return;
        }
    }

    // Build shortcut string
    const shortcut = buildShortcutString(e);

    // Check if shortcut exists
    if (SHORTCUTS[shortcut]) {
        e.preventDefault();
        executeShortcut(SHORTCUTS[shortcut].action);
    }
}

/**
 * Handle key up event
 */
function handleKeyUp(e) {
    pressedKeys.delete(e.key.toLowerCase());
}

/**
 * Build shortcut string from event
 */
function buildShortcutString(e) {
    const parts = [];

    if (e.ctrlKey || e.metaKey) parts.push('ctrl');
    if (e.shiftKey) parts.push('shift');
    if (e.altKey) parts.push('alt');

    // Add the main key
    const key = e.key.toLowerCase();
    if (key !== 'control' && key !== 'shift' && key !== 'alt' && key !== 'meta') {
        parts.push(key);
    }

    return parts.join('+');
}

/**
 * Execute shortcut action
 */
function executeShortcut(action) {
    console.log(`⌨️ Shortcut: ${action}`);

    switch (action) {
        // Generation & Modes
        case 'generate':
            const generateBtn = document.getElementById('generate-btn');
            // Force click even if other states are weird, but respect disabled attribute logic
            // (Unless it's incorrectly disabled, but we trust the disabling logic)
            if (generateBtn) {
                if (!generateBtn.disabled) {
                    generateBtn.click();
                    // Add visual feedback class momentarily
                    generateBtn.classList.add('active-keypress');
                    setTimeout(() => generateBtn.classList.remove('active-keypress'), 200);
                } else {
                    console.warn('[Shortcut] Generate button is disabled');
                    if (window.showNotification) window.showNotification("⚠️ Espera a que termine la generación...", "warning");
                }
            } else {
                console.error('[Shortcut] Generate button #generate-btn not found!');
            }
            break;

        case 'toggleMacro':
            const macroToggle = document.getElementById('macro-mode-toggle');
            if (macroToggle) {
                macroToggle.checked = !macroToggle.checked;
                macroToggle.dispatchEvent(new Event('change'));
            }
            break;

        case 'mutate':
            const mutateBtn = document.getElementById('mutate-btn');
            if (mutateBtn && !mutateBtn.disabled) {
                mutateBtn.click();
            }
            break;

        case 'patternMode':
            // Click the SOLO button directly to ensure UI updates
            const soloBtn = document.querySelector('.mode-segment[data-mode="solo"]');
            if (soloBtn) {
                soloBtn.click();

                // Visual feedback via notification
                if (window.showNotification) {
                    window.showNotification("🎵 Modo Solo Activado", "info");
                }
            }
            break;

        // Pattern Actions
        case 'send':
            const sendBtn = document.getElementById('send-btn');
            if (sendBtn && !sendBtn.disabled) {
                sendBtn.click();
            }
            break;

        case 'toggleFavorite':
            if (window.toggleFavorite) {
                window.toggleFavorite();
            }
            break;

        // Navigation & Panels
        case 'openHistory':
            if (window.openHistoryModal) {
                window.openHistoryModal();
            }
            break;

        case 'openFavorites':
            if (window.openFavoritesModal) {
                window.openFavoritesModal();
            }
            break;

        case 'focusOracle':
            const oracleInput = document.getElementById('oracle-input');
            if (oracleInput) {
                oracleInput.focus();
                oracleInput.select();
            }
            break;

        case 'openRules':
            if (window.openRulesModal) {
                window.openRulesModal();
            }
            break;

        case 'closeModal':
            // Close any open modal
            const modals = document.querySelectorAll('.modal[style*="display: block"], .floating-panel[style*="display: flex"]');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
            break;

        case 'tabVisuals':
            if (window.switchBentoPanel) window.switchBentoPanel('knobs');
            break;

        case 'tabInstruments':
            if (window.switchBentoPanel) window.switchBentoPanel('instruments');
            break;

        // Tools
        case 'openMorph':
            if (window.toggleMorphPanel) {
                window.toggleMorphPanel();
            }
            break;

        case 'openJam':
            if (window.openJamSessionModal) {
                window.openJamSessionModal();
            }
            break;

        case 'openBatch':
            if (window.generateBatch) {
                window.generateBatch();
            }
            break;

        // Utilities
        case 'showHelp':
            showShortcutsHelp();
            break;

        case 'clearLog':
            const activityLog = document.getElementById('activity-log');
            if (activityLog) {
                activityLog.innerHTML = '';
            }
            break;

        // History
        case 'undo':
            if (window.sessionHistory) window.sessionHistory.undo();
            break;
        case 'redo':
            if (window.sessionHistory) window.sessionHistory.redo();
            break;
    }
}

/**
 * Show shortcuts help modal
 */
function showShortcutsHelp() {
    // Create help modal if it doesn't exist
    let helpModal = document.getElementById('shortcuts-help-modal');

    if (!helpModal) {
        helpModal = document.createElement('div');
        helpModal.id = 'shortcuts-help-modal';
        helpModal.className = 'modal';
        helpModal.style.display = 'none';

        helpModal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h2>⌨️ Atajos de Teclado</h2>
                    <button class="close-btn" onclick="document.getElementById('shortcuts-help-modal').style.display='none'">×</button>
                </div>
                <div class="modal-body" style="max-height: 500px; overflow-y: auto;">
                    ${generateShortcutsHTML()}
                </div>
            </div>
        `;

        document.body.appendChild(helpModal);
    }

    helpModal.style.display = 'block';
}

/**
 * Generate shortcuts HTML for help modal
 */
function generateShortcutsHTML() {
    const categories = {
        'Generación & Modos': ['ctrl+g', 'ctrl+m', 'ctrl+shift+m', 'ctrl+p'],
        'Acciones sobre Patrón': ['ctrl+enter', 'ctrl+f'],
        'Navegación & Paneles': ['ctrl+h', 'ctrl+shift+f', 'ctrl+o', 'ctrl+r', 'escape', 'alt+1', 'alt+2'],
        'Herramientas': ['ctrl+shift+m', 'ctrl+j', 'ctrl+b'],
        'Utilidades': ['ctrl+/', 'ctrl+l']
    };

    let html = '';

    for (const [category, shortcuts] of Object.entries(categories)) {
        html += `<h3 style="margin-top: 20px; color: var(--primary);">${category}</h3>`;
        html += '<table style="width: 100%; border-collapse: collapse;">';

        shortcuts.forEach(shortcut => {
            const info = SHORTCUTS[shortcut];
            if (info) {
                const keyDisplay = shortcut
                    .split('+')
                    .map(k => `<kbd style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 3px; font-family: monospace;">${k.toUpperCase()}</kbd>`)
                    .join(' + ');

                html += `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px; width: 40%;">${keyDisplay}</td>
                        <td style="padding: 8px; color: #94a3b8;">${info.description}</td>
                    </tr>
                `;
            }
        });

        html += '</table>';
    }

    return html;
}

/**
 * Get all shortcuts (for external use)
 */
export function getShortcuts() {
    return SHORTCUTS;
}
