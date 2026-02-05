/**
 * Conductor Module (Fase 16)
 * Gestiona el cliente del "Director de Orquesta" y la visualización de la Timeline.
 */

import * as api from './network.js';

let conductorInterval = null;
let isVisible = false;

// Default sections (matched to backend 'standard' template)
let sections = [
    { name: "INTRO", duration: 32 },
    { name: "VERSE", duration: 64 },
    { name: "BUILD", duration: 16 },
    { name: "DROP", duration: 32 },
    { name: "OUTRO", duration: 32 }
];
let currentTemplate = 'standard';

export function initConductor() {
    console.log("🎻 Conductor Module Initialized");

    // Expose for external updates (e.g. Arranger)
    window.updateTimelineStructure = (newSections) => {
        sections = newSections;
        const timelineTrack = document.getElementById('timeline-track');
        if (timelineTrack) {
            timelineTrack.innerHTML = ''; // Clear
            const cursor = document.createElement('div');
            cursor.className = 'timeline-cursor';
            cursor.id = 'timeline-cursor';
            timelineTrack.appendChild(cursor);
            renderTimeline(timelineTrack);
        }
    };

    // UI Elements
    const toggleBtn = document.getElementById('conductor-toggle-btn');
    const panel = document.getElementById('conductor-panel');
    const closeBtn = document.getElementById('conductor-close');
    const playBtn = document.getElementById('conductor-play');
    const stopBtn = document.getElementById('conductor-stop');
    const timelineTrack = document.getElementById('timeline-track');

    // Render Timeline
    renderTimeline(timelineTrack);

    // Load Templates
    loadTemplates();

    // timelineTrack assignment removed (was causing crash)

    // Event Listeners
    toggleBtn.addEventListener('click', () => togglePanel(panel));
    closeBtn.addEventListener('click', () => togglePanel(panel));
    playBtn.addEventListener('click', startConductor);
    stopBtn.addEventListener('click', stopConductor);

    // Template Select Listener
    const templateSelect = document.getElementById('conductor-template-select');
    if (templateSelect) {
        templateSelect.addEventListener('change', (e) => {
            currentTemplate = e.target.value;
            // We can't easily preview the timeline without starting, 
            // but we could try to fetch structure details.
            // For now, restarting is required to change structure visually if playing.
        });
    }
}

async function loadTemplates() {
    try {
        const data = await api.getConductorTemplatesAPI();
        if (data.success && data.templates) {
            const select = document.getElementById('conductor-template-select');
            if (select) {
                select.innerHTML = data.templates.map(t =>
                    `<option value="${t}">${t.charAt(0).toUpperCase() + t.slice(1).replace('_', ' ')}</option>`
                ).join('');
            }
        }
    } catch (e) { console.error('Error loading templates', e); }
}

function renderTimeline(container) {
    if (!container) return;

    // Total beats
    const totalDuration = sections.reduce((acc, s) => acc + s.duration, 0);

    sections.forEach(section => {
        const div = document.createElement('div');
        div.className = `timeline-section section-${section.name}`;
        div.id = `section-${section.name}`;
        div.innerText = section.name;

        // Width proportional to duration
        const widthPercent = (section.duration / totalDuration) * 100;
        div.style.width = `${widthPercent}%`;

        container.appendChild(div);
    });
}

function togglePanel(panel) {
    if (!panel) return;
    isVisible = !isVisible;
    if (isVisible) {
        panel.classList.remove('hidden');
        startPolling();
    } else {
        panel.classList.add('hidden');
        stopPolling();
    }
}

async function startConductor() {
    try {
        const bpm = parseInt(document.getElementById('param-tempo')?.value || 140);
        const template = document.getElementById('conductor-template-select')?.value || 'standard';

        const data = await api.startConductorAPI({ bpm, template });
        if (data.success) {
            console.log("Conductor Started");
            startPolling();
            document.getElementById('conductor-play').disabled = true;
            document.getElementById('conductor-stop').disabled = false;

            // Auto-Start Jam Session logic (Simulated) to ensure music plays
            // We reuse the existing Jam Session logic but bypass the modal
            if (window.startJamSessionMock) {
                window.startJamSessionMock(); // Function to be added to main.js or phase2
            } else {
                // Fallback: Trigger one generation immediately
                if (window.generatePattern) window.generatePattern();

                // Start a local loop that mimics Jam Session
                window.conductorJamInterval = setInterval(() => {
                    if (window.generatePattern) {
                        // Alternate instruments randomly
                        const types = ['drums', 'bass', 'melody', 'percussion', 'fx'];
                        const type = types[Math.floor(Math.random() * types.length)];
                        // Update state type (hacky but effective)
                        if (state && state.patternType) state.patternType = type;

                        window.generatePattern();

                        setTimeout(() => {
                            if (window.sendPattern) window.sendPattern();
                        }, 2000); // Send after gen
                    }
                }, 8000); // Every 8 seconds
            }
        }
    } catch (e) {
        console.error(e);
    }
}

async function stopConductor() {
    try {
        const data = await api.stopConductorAPI();
        if (data.success) {
            console.log("Conductor Stopped");
            document.getElementById('conductor-play').disabled = false;
            document.getElementById('conductor-stop').disabled = true;
            resetCursor();

            // Stop Auto-Jam
            if (window.conductorJamInterval) {
                clearInterval(window.conductorJamInterval);
                window.conductorJamInterval = null;
            }
        }
    } catch (e) {
        console.error(e);
    }
}

function startPolling() {
    if (conductorInterval) clearInterval(conductorInterval);
    conductorInterval = setInterval(updateStatus, 1000); // Poll every 1s
}

function stopPolling() {
    if (conductorInterval) clearInterval(conductorInterval);
    conductorInterval = null;
}

async function updateStatus() {
    try {
        const data = await api.getConductorStatusAPI();

        if (data.active) {
            const status = data.data;
            updateUI(status);
        } else {
            // Si el backend se detiene solo (fin de canción)
            document.getElementById('conductor-play').disabled = false;
            document.getElementById('conductor-stop').disabled = true;
            stopPolling(); // IMPORTANT: Stop polling to prevent loop

            // Check if we were recording
            if (window.sessionRecorder && window.sessionRecorder.isRecording) {
                window.sessionRecorder.stop();
                if (confirm("🏁 Canción finalizada.\n\n¿Quieres descargar el código fuente (.tidal)?")) {
                    window.sessionRecorder.download();
                }
            }
        }
    } catch (e) {
        console.error(e);
    }
}

function updateUI(status) {
    document.getElementById('conductor-section-name').innerText = status.section;
    document.getElementById('conductor-params').innerText =
        `Modulando: Densidad ${Math.round(status.target_density * 100)}% | Complejidad ${Math.round(status.target_complexity * 100)}%`;

    // Highlight active section
    document.querySelectorAll('.timeline-section').forEach(el => el.classList.remove('active', 'transition-warning'));
    const activeEl = document.getElementById(`section-${status.section}`);
    if (activeEl) {
        activeEl.classList.add('active');
        if (status.transition_imminent) {
            activeEl.classList.add('transition-warning');
            handleAutoTransition(status);
        }
    }

    // Move Cursor
    let barsPassed = 0;
    for (let s of sections) {
        if (s.name === status.section) break;
        barsPassed += s.duration;
    }
    const currentTotalBars = barsPassed + (status.section_progress * sections.find(s => s.name === status.section).duration);
    const totalSongBars = sections.reduce((acc, s) => acc + s.duration, 0);

    const progressPercent = (currentTotalBars / totalSongBars) * 100;

    const cursor = document.getElementById('timeline-cursor');
    if (cursor) cursor.style.left = `${progressPercent}%`;
}

/**
 * Gestiona la generación automática de Fills cuando una transición es inminente.
 */
let lastTransitionBar = -1;
async function handleAutoTransition(status) {
    // Evitar disparar múltiples veces en el mismo compás
    if (status.bar === lastTransitionBar) return;
    lastTransitionBar = status.bar;

    console.log(`🥁 Transición Inminente hacia ${status.next_section}! Generando Fill...`);

    try {
        const style = document.getElementById('param-style')?.value || 'techno';
        const data = await api.generateFillAPI({ style });

        if (data.success && data.pattern) {
            // Actualizar editor y enviar
            if (window.updateEditorContent) window.updateEditorContent(data.pattern);
            if (window.sendPattern) window.sendPattern();

            if (window.logActivity) {
                window.logActivity(`🎻 Conductor: Inyectando FILL para transición a ${status.next_section}`, "success");
            }
        }
    } catch (e) {
        console.error("Error en auto-transition fill", e);
    }
}

function resetCursor() {
    const cursor = document.getElementById('timeline-cursor');
    if (cursor) cursor.style.left = '0%';
    document.querySelectorAll('.timeline-section').forEach(el => el.classList.remove('active'));
}
