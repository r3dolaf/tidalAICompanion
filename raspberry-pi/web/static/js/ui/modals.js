import { elements } from './ui-manager.js';
import { logActivity, showNotification } from '../modules/logger.js';
import * as api from '../modules/network.js';

export function openSettingsModal() {
    if (!elements.settingsModal) return;
    elements.targetIpInput.value = localStorage.getItem('target_ip') || '';
    elements.targetPortInput.value = localStorage.getItem('target_port') || '6010';
    elements.settingsModal.style.display = 'block';
}

export function closeSettingsModal() {
    if (elements.settingsModal) elements.settingsModal.style.display = 'none';
}

export async function saveSystemConfig() {
    const ip = elements.targetIpInput.value;
    const port = parseInt(elements.targetPortInput.value);

    if (!ip) {
        showNotification('IP no válida', 'error');
        return;
    }

    localStorage.setItem('target_ip', ip);
    localStorage.setItem('target_port', port);

    logActivity(`Guardando config: ${ip}:${port}...`);

    try {
        const data = await api.saveSystemConfigAPI({ target_ip: ip, target_port: port });
        if (data.success) {
            showNotification('Configuración guardada y aplicada', 'success');
            closeSettingsModal();
        } else {
            showNotification('Error: ' + (data.error || 'N/A'), 'error');
        }
    } catch (e) {
        console.error('Error saving config:', e);
        showNotification('Error al conectar con el servidor', 'error');
    }
}

export function loadSystemConfig() {
    const ip = localStorage.getItem('target_ip');
    const port = localStorage.getItem('target_port');
    if (ip && port) {
        api.saveSystemConfigAPI({
            target_ip: ip,
            target_port: parseInt(port)
        }).catch(e => console.log('Syncing config...'));
    }
}

// --- BRAIN TERMINAL LOGIC ---
export function openBrainModal() {
    const modal = document.getElementById('brain-terminal-modal');
    if (modal) {
        modal.style.display = 'block';
        modal.classList.remove('hidden');
    }
}

export function closeBrainModal() {
    const modal = document.getElementById('brain-terminal-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
}

export function logToBrainTerminal(message, type = 'info') {
    const terminal = document.getElementById('brain-terminal');
    if (!terminal) return;

    const entry = document.createElement('div');
    entry.className = 'stream-entry';

    // Add type-specific class
    if (type === 'error') entry.classList.add('error');
    else if (type === 'thought' || type === 'success') entry.classList.add('thought');
    else entry.classList.add('info');

    const timestamp = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    entry.textContent = `[${timestamp}] ${message}`;

    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight; // Auto-scroll

    // Limit to 50 entries
    while (terminal.children.length > 50) {
        terminal.removeChild(terminal.firstChild);
    }
}
