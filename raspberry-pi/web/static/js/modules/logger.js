import { elements } from '../ui/ui-manager.js';

export function logActivity(message, type = 'info') {
    if (!elements.activityLog) return;

    // Fallback if elements not fully ready, though import should handle it
    const timestamp = new Date().toLocaleTimeString('es-ES');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`; // Assumes CSS uses log-info, log-error
    // Or legacy style:
    if (type === 'error') entry.style.color = '#ef4444';
    if (type === 'success') entry.style.color = '#10b981';

    entry.innerHTML = `<span style="opacity:0.6">[${timestamp}]</span> ${message}`;

    elements.activityLog.appendChild(entry);
    elements.activityLog.scrollTop = elements.activityLog.scrollHeight;

    while (elements.activityLog.children.length > 50) {
        elements.activityLog.removeChild(elements.activityLog.firstChild);
    }

    // --- BRAIN MIRROR (Mirror logs to the new Terminal) ---
    import('../ui/modals.js').then(modals => {
        if (modals.logToBrainTerminal) modals.logToBrainTerminal(message, type);
    }).catch(e => { }); // Silent fail if module not ready
}

export function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    Object.assign(notification.style, {
        position: 'fixed', bottom: '100px', left: '50%', transform: 'translateX(-50%)',
        padding: '10px 20px', borderRadius: '20px', color: 'white', zIndex: '1000',
        background: type === 'success' ? '#10b981' : (type === 'error' ? '#ef4444' : '#6366f1'),
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)', transition: 'opacity 0.5s'
    });

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}
