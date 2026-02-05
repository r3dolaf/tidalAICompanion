import { state, updateState } from './js/core/state.js';
import { elements } from './js/ui/ui-manager.js';
import { logActivity } from './js/modules/logger.js';
import * as api from './js/modules/network.js';

// ============================================
// CORPUS ANALYSIS
// ============================================

let corpusStats = null;

async function loadCorpusStats() {
    try {
        const data = await api.getCorpusStatsAPI();

        if (data.success) {
            corpusStats = data.stats;
            displayCorpusStats();
        } else {
            logActivity(data.error || 'Error cargando estadísticas', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

function displayCorpusStats() {
    if (!corpusStats) return;

    const container = document.getElementById('corpus-stats-content');
    if (!container) return;

    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${corpusStats.total_patterns}</div>
                <div class="stat-label">Patrones Totales</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${corpusStats.avg_length}</div>
                <div class="stat-label">Longitud Promedio</div>
            </div>
        </div>
        
        <div class="stats-section">
            <h3>🎵 Samples Más Usados</h3>
            <div class="stats-list">
                ${corpusStats.top_samples.map(s => `
                    <div class="stats-item">
                        <span class="stats-name">${s.name}</span>
                        <span class="stats-bar" style="width: ${(s.count / corpusStats.top_samples[0].count) * 100}%"></span>
                        <span class="stats-count">${s.count}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="stats-section">
            <h3>✨ Efectos Más Usados</h3>
            <div class="stats-list">
                ${corpusStats.top_effects.map(e => `
                    <div class="stats-item">
                        <span class="stats-name">${e.name}</span>
                        <span class="stats-bar" style="width: ${(e.count / corpusStats.top_effects[0].count) * 100}%"></span>
                        <span class="stats-count">${e.count}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        
        ${Object.keys(corpusStats.type_distribution).length > 0 ? `
            <div class="stats-section">
                <h3>📊 Distribución por Tipo</h3>
                <div class="stats-list">
                    ${Object.entries(corpusStats.type_distribution).map(([type, count]) => `
                        <div class="stats-item">
                            <span class="stats-name">${patternTypeIcons[type] || '🎵'} ${type}</span>
                            <span class="stats-bar" style="width: ${(count / Object.values(corpusStats.type_distribution).reduce((a, b) => Math.max(a, b))) * 100}%"></span>
                            <span class="stats-count">${count}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

export function toggleCorpusStats() {
    const section = document.getElementById('corpus-stats-section');
    const content = document.getElementById('corpus-stats-content');

    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
        loadCorpusStats();
    } else {
        content.style.display = 'none';
    }
}

// ============================================
// JAM SESSION
// ============================================

let jamSessionActive = false;
let jamSessionInterval = null;
let jamSessionConfig = null;

export function openJamSessionModal() {
    const modal = document.getElementById('jam-modal');
    modal.style.display = 'block';
}

export function closeJamSessionModal() {
    const modal = document.getElementById('jam-modal');
    if (modal) modal.style.display = 'none';
}

export async function startJamSession() {
    const duration = parseInt(document.getElementById('jam-duration').value);
    const interval = parseInt(document.getElementById('jam-interval').value);

    // Obtener canales seleccionados
    const channelCheckboxes = document.querySelectorAll('.jam-channel:checked');
    const channels = Array.from(channelCheckboxes).map(cb => cb.value);

    // Obtener tipos seleccionados
    const typeCheckboxes = document.querySelectorAll('.jam-type:checked');
    const types = Array.from(typeCheckboxes).map(cb => cb.value);

    if (channels.length === 0) {
        alert('Selecciona al menos un canal');
        return;
    }

    if (types.length === 0) {
        alert('Selecciona al menos un tipo de patrón');
        return;
    }

    try {
        const data = await api.startJamSessionAPI({ duration, interval, channels, types });

        if (data.success) {
            jamSessionConfig = data.config;
            jamSessionActive = true;

            closeJamSessionModal();
            logActivity(`Jam session iniciada: ${duration}min, ${channels.length} canales`);

            // Iniciar generación automática
            runJamSession();

            // Actualizar UI
            document.getElementById('jam-status').style.display = 'block';
            document.getElementById('jam-status-text').textContent =
                `🎵 Jam activa: ${channels.join(', ')} | ${interval}s`;
        } else {
            logActivity(data.error || 'Error iniciando jam session', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

function runJamSession() {
    if (!jamSessionActive || !jamSessionConfig) return;

    let patternIndex = 0;
    const totalPatterns = jamSessionConfig.estimated_patterns;

    jamSessionInterval = setInterval(async () => {
        if (patternIndex >= totalPatterns) {
            stopJamSession();
            return;
        }

        // Seleccionar canal y tipo aleatorio
        const channel = jamSessionConfig.channels[Math.floor(Math.random() * jamSessionConfig.channels.length)];
        const type = jamSessionConfig.types[Math.floor(Math.random() * jamSessionConfig.types.length)];

        // Generar patrón
        try {
            const useAI = state.genMode === 'ai';

            const requestData = {
                type: type,
                density: state.config.density,
                complexity: state.config.complexity,
                tempo: state.config.tempo,
                style: state.config.style,
                use_ai: useAI,
                temperature: useAI ? state.config.temperature : 1.0
            };

            const genData = await api.generatePatternAPI(requestData);

            if (genData.success) {
                // Enviar a canal
                const targetIp = localStorage.getItem('target_ip') || '127.0.0.1';
                const targetPort = parseInt(localStorage.getItem('target_port') || '6010');

                const sendData = await api.sendPatternAPI({
                    channel: channel,
                    pattern: genData.pattern,
                    target_ip: targetIp,
                    target_port: targetPort
                });

                if (sendData.success) {
                    // ACTUALIZACIÓN VISUAL CLAVE: Mostrar código en pantalla
                    const displayCode = `-- Jam: ${channel} (${type})\n${channel} $ ${genData.pattern}`;
                    const outputElem = document.getElementById('pattern-output');
                    if (outputElem) outputElem.textContent = displayCode;

                    logActivity(`Jam: ${channel} <- ${type} patrón`);
                    patternIndex++;

                    // Actualizar progreso
                    const progress = Math.round((patternIndex / totalPatterns) * 100);
                    document.getElementById('jam-status-text').textContent =
                        `🎵 Jam activa: ${jamSessionConfig.channels.join(', ')} | ${progress}%`;
                } else {
                    logActivity(`Error enviando OSC: ${sendData.error}`, 'error');
                }
            }
        } catch (error) {
            console.error('Error en jam session:', error);
            // Mostrar error visualmente
            const outputElem = document.getElementById('pattern-output');
            if (outputElem) outputElem.textContent = `-- Error de conexión con Raspberry Pi --\nComprueba la IP configurada.`;
        }

    }, jamSessionConfig.interval * 1000);
}

export function stopJamSession() {
    if (jamSessionInterval) {
        clearInterval(jamSessionInterval);
        jamSessionInterval = null;
    }

    jamSessionActive = false;
    jamSessionConfig = null;

    const status = document.getElementById('jam-status');
    if (status) status.style.display = 'none';
    logActivity('Jam session detenida');
}

// ============================================
// BACKUP / RESTORE
// ============================================

export async function createBackup() {
    try {
        const data = await api.createBackupAPI();

        if (data.success) {
            logActivity(`Backup creado: ${data.filename} (${Math.round(data.size / 1024)} KB)`);
            alert(`Backup creado exitosamente:\n${data.filename}\n\nGuardado en: raspberry-pi/backups/`);
        } else {
            logActivity(data.error || 'Error creando backup', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

export function openRestoreModal() {
    const modal = document.getElementById('restore-modal');
    modal.style.display = 'block';
}

export function closeRestoreModal() {
    const modal = document.getElementById('restore-modal');
    modal.style.display = 'none';
}

export async function restoreBackup() {
    const fileInput = document.getElementById('restore-file');

    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Selecciona un archivo ZIP');
        return;
    }

    const file = fileInput.files[0];

    if (!file.name.endsWith('.zip')) {
        alert('El archivo debe ser ZIP');
        return;
    }

    if (!confirm('¿Restaurar backup? Esto sobrescribirá los datos actuales.')) {
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        const data = await api.restoreBackupAPI(formData);

        if (data.success) {
            logActivity(`Backup restaurado: ${data.files_restored.length} archivos`);
            alert(`Backup restaurado exitosamente!\n\nArchivos restaurados:\n${data.files_restored.join('\n')}\n\nRecarga la página para ver los cambios.`);
            closeRestoreModal();

            // Recargar datos
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            logActivity(data.error || 'Error restaurando backup', 'error');
            alert('Error restaurando backup: ' + (data.error || 'Error desconocido'));
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
        alert('Error de conexión');
    }
}

// Inicializar Phase 2
document.addEventListener('DOMContentLoaded', () => {
    // Cargar estadísticas si la sección existe
    const statsSection = document.getElementById('corpus-stats-section');
    if (statsSection) {
        // Se cargará cuando el usuario haga click
    }
});
