import { state, updateState } from './js/core/state.js';
import { elements, patternTypeIcons } from './js/ui/ui-manager.js';
import { logActivity, showNotification } from './js/modules/logger.js';
import * as api from './js/modules/network.js';

// ============================================
// PRESETS SYSTEM
// ============================================

let presetsData = [];

export async function loadPresets() {
    try {
        const data = await api.getPresetsAPI();

        if (data.success) {
            presetsData = data.presets;
            updatePresetsSelector();
        }
    } catch (error) {
        console.error('Error cargando presets:', error);
    }
}

function updatePresetsSelector() {
    const selector = document.getElementById('preset-selector');
    if (!selector) return;

    selector.innerHTML = '<option value="">-- Seleccionar Preset --</option>';

    presetsData.forEach(preset => {
        const option = document.createElement('option');
        option.value = preset.name;
        option.textContent = preset.name;
        selector.appendChild(option);
    });
}

export async function savePreset() {
    const name = prompt('Nombre del preset:');
    if (!name) return;

    const presetData = {
        name: name,
        genMode: state.genMode,
        patternType: state.patternType,
        density: state.config.density,
        complexity: state.config.complexity,
        tempo: state.config.tempo,
        style: state.config.style,
        temperature: state.config.temperature
    };

    try {
        const data = await api.savePresetAPI(presetData);

        if (data.success) {
            logActivity(`Preset "${name}" guardado`);
            loadPresets();
        } else {
            logActivity(data.error || 'Error guardando preset', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

export async function loadPreset(name) {
    const preset = presetsData.find(p => p.name === name);
    if (!preset) return;

    // Aplicar configuración
    // changeGenMode(preset.genMode); // Assuming this is available globally or imported
    // selectPatternType(preset.patternType);

    // Actualizar sliders
    elements.densitySlider.value = preset.density * 100;
    elements.densityValue.textContent = Math.round(preset.density * 100) + '%';
    state.config.density = preset.density;

    elements.complexitySlider.value = preset.complexity * 100;
    elements.complexityValue.textContent = Math.round(preset.complexity * 100) + '%';
    state.config.complexity = preset.complexity;

    elements.tempoSlider.value = preset.tempo;
    elements.tempoValue.textContent = preset.tempo;
    state.config.tempo = preset.tempo;

    elements.styleSelect.value = preset.style;
    state.config.style = preset.style;

    if (preset.genMode === 'ai') {
        elements.temperatureSlider.value = preset.temperature;
        elements.temperatureValue.textContent = preset.temperature;
        state.config.temperature = preset.temperature;
    }

    logActivity(`Preset "${name}" cargado`);
}

export async function deletePreset(name) {
    if (!confirm(`¿Eliminar preset "${name}"?`)) return;

    try {
        const data = await api.deletePresetAPI(name);

        if (data.success) {
            logActivity(`Preset "${name}" eliminado`);
            loadPresets();
        } else {
            logActivity(data.error || 'Error eliminando preset', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

export function openPresetsModal() {
    const modal = document.getElementById('presets-modal');
    modal.style.display = 'block';
    displayPresetsList();
}

export function closePresetsModal() {
    const modal = document.getElementById('presets-modal');
    if (modal) modal.style.display = 'none';
}

function displayPresetsList() {
    const list = document.getElementById('presets-list');
    list.innerHTML = '';

    if (presetsData.length === 0) {
        list.innerHTML = `
            <div style="text-align: center; color: #888; padding: 40px;">
                <div style="font-size: 3rem; margin-bottom: 15px;">💾</div>
                <div>No hay presets guardados</div>
                <div style="font-size: 0.9em; margin-top: 10px;">Configura parámetros y guarda un preset</div>
            </div>
        `;
        return;
    }

    presetsData.forEach(preset => {
        const item = document.createElement('div');
        item.className = 'preset-item';
        item.innerHTML = `
            <div class="preset-info">
                <div class="preset-name">${preset.name}</div>
                <div class="preset-details">
                    ${preset.genMode === 'ai' ? '🧠' : '📐'} ${preset.patternType} | 
                    D:${Math.round(preset.density * 100)}% C:${Math.round(preset.complexity * 100)}% | 
                    ${preset.tempo} BPM
                </div>
            </div>
            <div class="preset-actions">
                <button class="btn-icon" onclick="loadPreset('${preset.name}')" title="Cargar preset">
                    ▶️
                </button>
                <button class="btn-icon btn-delete" onclick="deletePreset('${preset.name}')" title="Eliminar">
                    🗑️
                </button>
            </div>
        `;
        list.appendChild(item);
    });
}

// ============================================
// HISTORY SYSTEM
// ============================================

let historyData = [];

async function loadHistory() {
    try {
        const data = await api.getHistoryAPI();
        if (data.success) {
            historyData = data.history;
        }
    } catch (error) {
        console.error('Error cargando historial:', error);
    }
}

async function addToHistory(pattern, type, mode, temperature) {
    try {
        await api.addToHistoryAPI({ pattern, type, mode, temperature });
        loadHistory();
    } catch (error) {
        console.error('Error añadiendo al historial:', error);
    }
}

export function openHistoryModal() {
    const modal = document.getElementById('history-modal');
    modal.style.display = 'block';
    displayHistoryList();
}

export function closeHistoryModal() {
    const modal = document.getElementById('history-modal');
    if (modal) modal.style.display = 'none';
}

export function displayHistoryList(filterType = 'all', searchText = '') {
    const list = document.getElementById('history-list');
    list.innerHTML = '';

    // Load history from localStorage
    const historyStr = localStorage.getItem('pattern_history');
    const historyData = historyStr ? JSON.parse(historyStr) : [];

    if (historyData.length === 0) {
        list.innerHTML = `
            <div style="text-align: center; color: #888; padding: 40px;">
                <div style="font-size: 3rem; margin-bottom: 15px;">📜</div>
                <div>No hay historial. Genera algunos patrones primero.</div>
            </div>
        `;
        return;
    }

    // Display patterns (simple version - just strings)
    historyData.forEach((pattern, index) => {
        const item = document.createElement('div');
        item.className = 'history-item';
        const preview = pattern.substring(0, 100).replace(/\n/g, ' ');
        item.innerHTML = `
            <div class="history-info">
                <div class="history-pattern">${preview}...</div>
            </div>
            <div class="history-actions">
                <button class="btn-icon" onclick="useHistoryPattern(${index})" title="Usar patrón">
                    ▶️
                </button>
                <button class="btn-icon" onclick="addHistoryToFavorites(${index})" title="Añadir a favoritos">
                    ⭐
                </button>
            </div>
        `;
        list.appendChild(item);
    });
}

export function useHistoryPattern(index) {
    const entry = historyData[index];
    if (!entry) return;

    state.lastPattern = entry.pattern;
    // Usar el shim global o el exportado si fuera posible, pero aquí usamos el nombre global
    // que será asignado en main.js
    if (window.displayPattern) {
        window.displayPattern(entry.pattern, `Historial (${entry.mode})`, entry.temperature);
    }

    if (elements.sendBtn) elements.sendBtn.disabled = false;
    if (elements.copyBtn) elements.copyBtn.disabled = false;
    logActivity('Patrón del historial cargado');
    closeHistoryModal();
}

export async function addHistoryToFavorites(index) {
    const entry = historyData[index];
    if (!entry) return;

    try {
        const data = await api.addFavoriteAPI(entry.pattern, entry.type);

        if (data.success) {
            logActivity('Patrón añadido a favoritos desde historial');
            if (window.loadFavorites) window.loadFavorites(); // Use global if possible
        } else {
            logActivity(data.error || 'Error añadiendo favorito', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

export async function clearHistory() {
    if (!confirm('¿Limpiar todo el historial?')) return;

    try {
        const data = await api.clearHistoryAPI();

        if (data.success) {
            historyData = [];
            displayHistoryList();
            logActivity('Historial limpiado');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

export function exportHistory() {
    const text = historyData.map(h => `# ${h.type} - ${h.mode}\n${h.pattern}`).join('\n\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tidalai-history-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    logActivity('Historial exportado');
}

// ============================================
// BATCH GENERATION
// ============================================

export async function generateBatch() {
    const count = parseInt(prompt('¿Cuántos patrones generar? (1-50)', '10'));
    if (!count || count < 1 || count > 50) return;

    const modal = document.getElementById('batch-modal');
    const list = document.getElementById('batch-list');
    const progress = document.getElementById('batch-progress');

    modal.style.display = 'block';
    list.innerHTML = '';
    progress.style.display = 'block';
    progress.textContent = 'Generando patrones...';

    try {
        const useAI = state.genMode === 'ai';

        const requestData = {
            count: count,
            type: state.patternType,
            density: state.config.density,
            complexity: state.config.complexity,
            tempo: state.config.tempo,
            style: state.config.style,
            use_ai: useAI,
            temperature: useAI ? state.config.temperature : 1.0
        };

        const data = await api.generateBatchAPI(requestData);

        progress.style.display = 'none';

        if (data.success) {
            displayBatchResults(data.patterns, data.mode);
            if (window.particleEngine) window.particleEngine.burst();
            logActivity(`${count} patrones generados en lote`);
        } else {
            logActivity('Error generando lote', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        progress.style.display = 'none';
        logActivity('Error de conexión', 'error');
    }
}

export function displayBatchResults(patterns, mode) {
    const list = document.getElementById('batch-list');
    list.innerHTML = '';

    patterns.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'batch-item';
        div.innerHTML = `
            <input type="checkbox" id="batch-${index}" class="batch-checkbox">
            <label for="batch-${index}" class="batch-pattern">${item.pattern}</label>
            <button class="btn-icon" onclick="useBatchPattern('${escapeHtml(item.pattern)}')" title="Usar este">
                ▶️
            </button>
        `;
        list.appendChild(div);
    });
}

export function useBatchPattern(pattern) {
    state.lastPattern = pattern;
    if (window.displayPattern) {
        window.displayPattern(pattern, 'Lote', null);
    }
    if (elements.sendBtn) elements.sendBtn.disabled = false;
    if (elements.copyBtn) elements.copyBtn.disabled = false;
    logActivity('Patrón del lote cargado');
    closeBatchModal();
}

export function closeBatchModal() {
    const modal = document.getElementById('batch-modal');
    if (modal) modal.style.display = 'none';
}

export async function addSelectedToFavorites() {
    const checkboxes = document.querySelectorAll('.batch-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('Selecciona al menos un patrón');
        return;
    }

    let added = 0;
    for (const checkbox of checkboxes) {
        const pattern = checkbox.nextElementSibling.textContent;

        try {
            const data = await api.addFavoriteAPI(pattern, state.patternType);
            if (data.success) added++;
        } catch (error) {
            console.error('Error:', error);
        }
    }

    logActivity(`${added} patrones añadidos a favoritos`);
    if (window.loadFavorites) window.loadFavorites();
}

// ============================================
// INLINE EDITOR
// ============================================

let editorMode = false;

export function toggleEditor() {
    editorMode = !editorMode;
    const output = elements.patternOutput;
    const btn = document.getElementById('edit-btn');

    if (editorMode) {
        output.contentEditable = true;
        output.style.border = '2px solid #667eea';
        output.style.background = '#f0f0f0';
        btn.textContent = '💾 Guardar';
        btn.classList.add('btn-success');
        logActivity('Modo edición activado');
    } else {
        output.contentEditable = false;
        output.style.border = 'none';
        output.style.background = 'transparent';
        btn.textContent = '✏️ Editar';
        btn.classList.remove('btn-success');

        // Actualizar patrón
        const newPattern = output.textContent.replace(/^d\d+\s*\$\s*/, '').trim();
        if (newPattern) {
            state.lastPattern = newPattern;
            logActivity('Patrón editado manualmente');

            // Actualizar estado del botón Fav
            if (typeof updateFavoriteButton === 'function') {
                updateFavoriteButton(newPattern);
            }
        }
    }
}

// Syntax highlighting básico
function highlightSyntax(text) {
    // Resaltar palabras clave de TidalCycles
    const keywords = ['sound', 'note', 'slow', 'fast', 'every', 'degradeBy', 'sometimes', 'often', 'rarely'];
    let highlighted = text;

    keywords.forEach(kw => {
        const regex = new RegExp(`\\b${kw}\\b`, 'g');
        highlighted = highlighted.replace(regex, `<span style="color: #667eea; font-weight: bold;">${kw}</span>`);
    });

    return highlighted;
}

// --- SAMPLE SCOUT LOGIC (RECOVERED) ---
export async function reindexSamples() {
    logActivity('Sample Scout: Re-indexando librería SuperDirt...');

    try {
        const data = await api.reindexSamplesAPI();

        if (data.success) {
            showNotification('Librería re-indexada con éxito', 'success');
            logActivity('✓ Librería sincronizada');
            // Si hay un patrón actual, refrescar sugerencias
            if (state.lastPattern) getSampleSuggestions(state.lastPattern);
        } else {
            showNotification('Error indexando: ' + (data.error || 'N/A'), 'error');
        }
    } catch (error) {
        console.error('Error in reindex:', error);
    }
}

export async function getSampleSuggestions(pattern) {
    const scoutPanel = document.getElementById('sample-scout-panel');
    const container = document.getElementById('sample-suggestions');

    if (!pattern) return;

    try {
        const data = await api.getSampleSuggestionsAPI(pattern, 6);

        if (data.success && data.suggestions && data.suggestions.length > 0) {
            if (scoutPanel) scoutPanel.style.display = 'block';
            if (container) {
                container.innerHTML = '';
                // Extraer el sample original para el reemplazo
                const originalSampleMatch = pattern.match(/\"(\w+)/);
                const originalSample = originalSampleMatch ? originalSampleMatch[1] : null;

                data.suggestions.forEach(sample => {
                    const tag = document.createElement('div');
                    tag.className = 'sample-tag';
                    tag.textContent = sample;
                    tag.onclick = () => replaceSample(pattern, originalSample, sample);
                    container.appendChild(tag);
                });
            }
        } else {
            if (scoutPanel) scoutPanel.style.display = 'none';
        }
    } catch (error) {
        console.error('Error fetching suggestions:', error);
    }
}

export async function replaceSample(pattern, oldSample, newSample) {
    if (!oldSample || !newSample) return;

    logActivity(`Sample Scout: Reemplazando "${oldSample}" por "${newSample}"...`);

    try {
        const data = await api.replaceSampleAPI(pattern, oldSample, newSample);

        if (data.success) {
            updateState('lastPattern', data.pattern);
            if (window.displayPattern) {
                window.displayPattern(data.pattern, 'AI Scout (Swap) 🔎', null);
            }
            if (window.particleEngine) window.particleEngine.burst();
            showNotification(`Sample cambiado a ${newSample} `, 'success');
        }
    } catch (error) {
        console.error('Error replacing sample:', error);
    }
}

// --- SAMPLES MODAL LOGIC (RECOVERED) ---
export function showSampleList() {
    const list = document.getElementById('samples-list-container');
    const config = document.getElementById('samples-sc-config');
    if (list) list.style.display = 'block';
    if (config) config.style.display = 'none';
    renderSampleList();
}

export function showSCConfig() {
    const list = document.getElementById('samples-list-container');
    const config = document.getElementById('samples-sc-config');
    if (list) list.style.display = 'none';
    if (config) config.style.display = 'block';
    updateSCStartupCode();
}

async function renderSampleList() {
    const container = document.getElementById('samples-list-container');
    if (!container) return;
    container.innerHTML = 'Cargando librería...';

    try {
        const data = await api.getSamplesAPI();
        if (data.success) {
            // Transformar objeto de samples a lista de carpetas para visualización
            const folders = Object.entries(data.samples).map(([key, list]) => ({
                name: key,
                count: Array.isArray(list) ? list.length : 0
            }));

            container.innerHTML = `
                <div style="max-height: 400px; overflow-y: auto;">
                    ${folders.map(f => `
                        <div class="sample-item" style="display:flex; justify-content:space-between; padding:5px; border-bottom:1px solid #334155;">
                            <span>${f.name}</span>
                            <span style="color:#64748b; font-size:0.8rem;">${f.count} sonidos</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = 'Error cargando sonidos.';
    }
}

export function updateSCStartupCode() {
    const path = document.getElementById('samples-path-input').value || 'C:\\Samples';
    const codeElem = document.getElementById('sc-startup-code');
    if (codeElem) {
        codeElem.textContent = `(~dirt.loadSoundFiles("${path.replace(/\\/g, '/')}/*");)`;
    }
}

export async function saveSamples() {
    const path = document.getElementById('samples-path-input').value;
    localStorage.setItem('samples_path', path);
    logActivity('Ruta de samples guardada localmente');
    showNotification('Ruta guardada', 'success');
}

export function copySCCode() {
    const code = document.getElementById('sc-startup-code').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showNotification('Código copiado!', 'success');
    });
}

// --- ORACLE / INTENT CONTROL ---
export async function handleOracleInput(generatePatternFn) {
    const input = document.getElementById('oracle-input');
    if (!input) return;
    const intent = input.value.trim();
    if (!intent) return;

    input.disabled = true;
    logActivity(`🔮 Consultando al Oráculo: "${intent}"...`);

    try {
        // Primero intentamos una interpretación pura para mover sliders
        const interpreted = await interpretOracleIntent(intent);

        // Luego disparamos una generación que puede usar ese intent en el prompt
        if (generatePatternFn) {
            await generatePatternFn({ intent: intent });
        }
    } catch (e) {
        logActivity('Error en oráculo', 'error');
    } finally {
        input.disabled = false;
        input.value = '';
        input.focus();
    }
}

export async function interpretOracleIntent(text) {
    if (!text.trim()) return;

    try {
        const data = await api.interpretOracleAPI(text);

        if (data.success && data.result.detected_keywords.length > 0) {
            applyOracleResult(data.result);
            // Flash visual en el input
            const input = document.getElementById('oracle-input');
            if (input) {
                input.style.borderColor = '#10b981';
                setTimeout(() => input.style.borderColor = '', 1000);
            }
            if (window.particleEngine) window.particleEngine.burst();
            return data.result;
        } else {
            logActivity('El Oráculo no comprendió tu intención', 'warning');
        }
    } catch (error) {
        console.error('Error oracle:', error);
    }
    return null;
}

function applyOracleResult(result) {
    // 1. Sliders (Offsets)
    const newDensity = Math.max(0, Math.min(100, (state.config.density * 100) + (result.density_offset * 100)));
    const newComplexity = Math.max(0, Math.min(100, (state.config.complexity * 100) + (result.complexity_offset * 100)));

    if (elements.densitySlider) {
        elements.densitySlider.value = newDensity;
        elements.densitySlider.dispatchEvent(new Event('input'));
    }
    if (elements.complexitySlider) {
        elements.complexitySlider.value = newComplexity;
        elements.complexitySlider.dispatchEvent(new Event('input'));
    }

    // 2. Estilo
    if (result.style_pref && elements.styleSelect) {
        elements.styleSelect.value = result.style_pref;
        elements.styleSelect.dispatchEvent(new Event('change'));
    }

    // 3. Tempo
    if (result.tempo_mod !== 0) {
        const newTempo = Math.max(60, Math.min(200, state.config.tempo + result.tempo_mod));
        if (elements.tempoSlider) {
            elements.tempoSlider.value = newTempo;
            elements.tempoSlider.dispatchEvent(new Event('input'));
        }
    }

    logActivity(`Oráculo: Descriptores detectados[${result.detected_keywords.join(', ')}]`);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function (m) { return map[m]; });
}

// Inicializar funcionalidades avanzadas
function initAdvancedFeatures() {
    loadPresets();

    // Restaurar ruta de samples
    const pathInput = document.getElementById('samples-path-input');
    if (pathInput) {
        pathInput.value = localStorage.getItem('samples_path') || '';
        pathInput.addEventListener('input', updateSCStartupCode);
    }

    // Event listeners para controles que no son modales
    const presetSelector = document.getElementById('preset-selector');
    if (presetSelector) {
        presetSelector.addEventListener('change', (e) => {
            if (e.target.value) {
                loadPreset(e.target.value);
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', initAdvancedFeatures);
