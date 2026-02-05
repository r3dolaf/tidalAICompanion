/**
 * Arranger Module (Phase 19)
 * Allows users to build custom song structures (Intro -> Verse -> Chorus -> Drop).
 */

let customSections = [
    { name: "INTRO", duration: 16, density: 0.2, complexity: 0.1 },
    { name: "BUILD", duration: 16, density: 0.5, complexity: 0.4 },
    { name: "DROP", duration: 32, density: 0.9, complexity: 0.8 },
    { name: "OUTRO", duration: 32, density: 0.3, complexity: 0.2 }
];

export function initArranger() {
    console.log("🎼 Arranger Module Initialized");
    renderArrangerTable();

    // Global hooks
    window.openArrangerModal = openArrangerModal;
    window.closeArrangerModal = closeArrangerModal;
    window.addArrangerSection = addArrangerSection;
    window.loadArrangerTemplate = loadArrangerTemplate;
    window.playCustomSong = playCustomSong;
    window.removeArrangerSection = removeArrangerSection;
    window.updateArrangerSection = updateArrangerSection;
    window.moveArrangerSection = moveArrangerSection;
}

function openArrangerModal() {
    document.getElementById('arranger-modal').classList.remove('hidden');
    renderArrangerTable();
}

function closeArrangerModal() {
    document.getElementById('arranger-modal').classList.add('hidden');
}

function renderArrangerTable() {
    const tbody = document.getElementById('arranger-sections-list');
    if (!tbody) return;

    tbody.innerHTML = '';

    customSections.forEach((section, index) => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid #333';

        tr.innerHTML = `
            <td style="padding:8px; color:#aaa;">${index + 1}</td>
            <td style="padding:8px;">
                <input type="text" value="${section.name}" 
                    onchange="updateArrangerSection(${index}, 'name', this.value)"
                    style="background:#222; border:1px solid #444; color:#fff; padding:4px; border-radius:4px; width:120px;">
            </td>
            <td style="padding:8px;">
                <input type="number" value="${section.duration}" min="4" step="4"
                    onchange="updateArrangerSection(${index}, 'duration', this.value)"
                    style="background:#222; border:1px solid #444; color:#fff; padding:4px; border-radius:4px; width:60px;">
            </td>
            <td style="padding:8px;">
                <input type="range" min="0" max="1" step="0.1" value="${section.density}"
                    onchange="updateArrangerSection(${index}, 'density', this.value)"
                    title="${section.density}">
            </td>
             <td style="padding:8px;">
                <input type="range" min="0" max="1" step="0.1" value="${section.complexity}"
                    onchange="updateArrangerSection(${index}, 'complexity', this.value)"
                    title="${section.complexity}">
            </td>
            <td style="padding:8px;">
                <button class="btn btn-small" onclick="moveArrangerSection(${index}, -1)" title="Subir">▲</button>
                <button class="btn btn-small" onclick="moveArrangerSection(${index}, 1)" title="Bajar">▼</button>
                <button class="btn btn-danger btn-small" onclick="removeArrangerSection(${index})" title="Eliminar">×</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function addArrangerSection() {
    customSections.push({ name: "NEW SECTION", duration: 32, density: 0.5, complexity: 0.5 });
    renderArrangerTable();
}

function removeArrangerSection(index) {
    customSections.splice(index, 1);
    renderArrangerTable();
}

function moveArrangerSection(index, direction) {
    if (direction === -1 && index > 0) {
        // Move Up
        [customSections[index], customSections[index - 1]] = [customSections[index - 1], customSections[index]];
    } else if (direction === 1 && index < customSections.length - 1) {
        // Move Down
        [customSections[index], customSections[index + 1]] = [customSections[index + 1], customSections[index]];
    }
    renderArrangerTable();
}

function updateArrangerSection(index, field, value) {
    if (field === 'duration') value = parseInt(value);
    if (field === 'density' || field === 'complexity') value = parseFloat(value);

    customSections[index][field] = value;
}

function loadArrangerTemplate(templateName) {
    if (templateName === 'standard') {
        customSections = [
            { name: "INTRO", duration: 32, density: 0.2, complexity: 0.2 },
            { name: "VERSE", duration: 64, density: 0.5, complexity: 0.4 },
            { name: "BUILD", duration: 16, density: 0.8, complexity: 0.7 },
            { name: "DROP", duration: 32, density: 0.9, complexity: 0.9 },
            { name: "OUTRO", duration: 32, density: 0.3, complexity: 0.2 }
        ];
        renderArrangerTable();
    }
}

async function playCustomSong() {
    const bpm = parseInt(document.getElementById('param-tempo')?.value || 140);

    // Close modal to see the action
    closeArrangerModal();

    if (window.showNotification) window.showNotification("🎼 Iniciando Canción Personalizada...", "info");

    try {
        const res = await fetch('/api/conductor/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bpm: bpm,
                structure: customSections,
                template: 'custom'
            })
        });

        const data = await res.json();
        if (data.success) {
            console.log("Custom Song Started");

            // Update Timeline Visualization
            if (window.updateTimelineStructure) {
                window.updateTimelineStructure(customSections);
            }

            // Start Session Recording
            if (window.sessionRecorder) window.sessionRecorder.start();

            // If conductor module is present, ensure panel is visible
            const conductorToggle = document.getElementById('conductor-toggle-btn');
            const conductorPanel = document.getElementById('conductor-panel');
            if (conductorPanel && conductorPanel.classList.contains('hidden')) {
                conductorToggle.click(); // Open panel
            }
        }
    } catch (e) {
        console.error("Error playing custom song:", e);
        alert("Error al iniciar la canción");
    }
}
