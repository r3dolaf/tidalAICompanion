import { elements } from './ui-manager.js';
import { logActivity } from '../modules/logger.js';
import * as api from '../modules/network.js';

// --- BRAIN PANEL (MAPA MENTAL) ---
export function toggleBrainPanel() {
    if (!elements.brainPanel) return;
    if (elements.brainPanel.style.display === 'flex') {
        closeBrainPanel();
    } else {
        elements.brainPanel.style.display = 'flex';
        renderBrainGraph();
        makeDraggable(elements.brainPanel, document.getElementById('brain-header'));
    }
}

export function closeBrainPanel() {
    if (elements.brainPanel) elements.brainPanel.style.display = 'none';
}

function renderBrainGraph() {
    const svgId = "#brain-svg";
    const container = elements.brainPanel?.querySelector('#brain-viz');
    if (!container || typeof d3 === 'undefined') return;

    const svg = d3.select(svgId);
    svg.selectAll("*").remove();

    fetch('/api/brain/graph')
        .then(res => res.json())
        .then(data => {
            const width = container.clientWidth;
            const height = container.clientHeight;

            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(80))
                .force("charge", d3.forceManyBody().strength(-100))
                .force("center", d3.forceCenter(width / 2, height / 2));

            const link = svg.append("g")
                .attr("stroke", "#334155")
                .attr("stroke-opacity", 0.6)
                .selectAll("line")
                .data(data.links)
                .join("line")
                .attr("stroke-width", d => Math.sqrt(d.value));

            const node = svg.append("g")
                .selectAll("g")
                .data(data.nodes)
                .join("g")
                .call(d3.drag()
                    .on("start", (event) => {
                        if (!event.active) simulation.alphaTarget(0.3).restart();
                        event.subject.fx = event.subject.x;
                        event.subject.fy = event.subject.y;
                    })
                    .on("drag", (event) => {
                        event.subject.fx = event.x;
                        event.subject.fy = event.y;
                    })
                    .on("end", (event) => {
                        if (!event.active) simulation.alphaTarget(0);
                        event.subject.fx = null;
                        event.subject.fy = null;
                    }));

            node.append("circle")
                .attr("r", d => 4 + Math.sqrt(d.weight))
                .attr("fill", d => {
                    if (d.type === 'sample') return "#8b5cf6";
                    if (d.type === 'function') return "#2dd4bf";
                    if (d.type === 'number') return "#f59e0b";
                    return "#94a3b8";
                })
                .attr("stroke", "#fff")
                .attr("stroke-width", 1);

            node.append("text")
                .text(d => d.label)
                .attr("x", 8)
                .attr("y", 4)
                .attr("fill", "#e2e8f0")
                .style("font-size", "10px")
                .style("pointer-events", "none");

            simulation.on("tick", () => {
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node.attr("transform", d => `translate(${d.x}, ${d.y})`);
            });
        })
        .catch(err => console.error("Error cargando grafo:", err));
}

// --- MORPH PANEL ---
export function toggleMorphPanel() {
    if (!elements.morphPanel) return;
    if (elements.morphPanel.style.display === 'flex') {
        closeMorphPanel();
    } else {
        elements.morphPanel.style.display = 'flex';
        loadMorphOptions();
        makeDraggable(elements.morphPanel, document.getElementById('morph-header'));
    }
}

export function closeMorphPanel() {
    if (elements.morphPanel) elements.morphPanel.style.display = 'none';
}

async function loadMorphOptions() {
    const selectA = document.getElementById('morph-select-a');
    const selectB = document.getElementById('morph-select-b');

    if (!selectA || !selectB) return;

    selectA.innerHTML = '<option value="">Cargando...</option>';
    selectB.innerHTML = '<option value="">Cargando...</option>';

    try {
        // Get history and favorites from Server DB
        const [histData, favData] = await Promise.all([
            api.getHistoryAPI(),
            api.getFavoritesAPI()
        ]);

        const history = histData.history || [];
        const favorites = favData.favorites || [];

        let options = '<option value="">-- Selecciona un patrón --</option>';

        if (favorites.length > 0) {
            options += '<optgroup label="⭐ Favoritos">';
            favorites.forEach(f => {
                const pat = typeof f === 'string' ? f : f.pattern;
                const preview = pat.substring(0, 50).replace(/\n/g, ' ');
                options += `<option value="${escapeHtml(pat)}">${preview}...</option>`;
            });
            options += '</optgroup>';
        }

        if (history.length > 0) {
            options += '<optgroup label="🕒 Historial Reciente">';
            history.slice(0, 15).forEach(h => {
                const pat = typeof h === 'string' ? h : h.pattern;
                const preview = pat.substring(0, 50).replace(/\n/g, ' ');
                options += `<option value="${escapeHtml(pat)}">${preview}...</option>`;
            });
            options += '</optgroup>';
        }

        if (favorites.length === 0 && history.length === 0) {
            options += '<option value="" disabled>No hay patrones guardados. Genera algunos primero.</option>';
        }

        selectA.innerHTML = options;
        selectB.innerHTML = options;
    } catch (e) {
        console.error('Error loading morph options:', e);
        selectA.innerHTML = '<option value="">Error cargando patrones</option>';
        selectB.innerHTML = '<option value="">Error cargando patrones</option>';
    }
}

let lastMorphedPattern = null;

export async function generateMorph() {
    const patternA = document.getElementById('morph-select-a').value;
    const patternB = document.getElementById('morph-select-b').value;
    const ratio = document.getElementById('morph-ratio-slider').value / 100;
    const preview = document.getElementById('morph-preview');
    const sendBtn = document.getElementById('morph-send-btn');

    if (!patternA || !patternB) {
        alert("Selecciona dos patrones para morfar");
        return;
    }

    if (preview) {
        preview.textContent = "Generando híbrido...";
        preview.style.opacity = "0.5";
    }

    try {
        const data = await api.generateMorphAPI({ pattern_a: patternA, pattern_b: patternB, ratio: ratio });
        if (data.success) {
            lastMorphedPattern = data.pattern;
            if (preview) {
                preview.textContent = data.pattern;
                preview.style.opacity = "1";
            }
            if (sendBtn) sendBtn.disabled = false;
        } else {
            if (preview) {
                preview.textContent = "Error: " + data.error;
                preview.style.color = "#ef4444";
            }
        }
    } catch (error) {
        console.error('Error morphing:', error);
    }
}

export async function sendMorphedPattern() {
    if (!lastMorphedPattern) return;

    try {
        const data = await api.sendPatternAPI({ channel: 'd1', pattern: lastMorphedPattern });
        if (data.success) {
            logActivity("Híbrido enviado a d1 🚀", "success");
        }
    } catch (e) {
        logActivity("Error enviando híbrido", "error");
    }
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

// --- LEXICON (ORÁCULO) ---
export function openLexiconModal() {
    if (elements.lexiconModal) elements.lexiconModal.style.display = 'block';
}

export function closeLexiconModal() {
    if (elements.lexiconModal) elements.lexiconModal.style.display = 'none';
}

// --- SONG TEMPLATES ---
export async function openSongTemplatesModal() {
    if (!elements.songTemplatesModal) return;
    elements.songTemplatesModal.style.display = 'block';

    try {
        const data = await api.getSongTemplatesAPI();
        if (data.success) {
            displayTemplates(data.templates);
        }
    } catch (e) {
        console.error(e);
        logActivity('Error cargando templates', 'error');
    }
}

export function closeSongTemplatesModal() {
    if (elements.songTemplatesModal) elements.songTemplatesModal.style.display = 'none';
}

function displayTemplates(templates) {
    if (!elements.templatesList) return;
    elements.templatesList.innerHTML = '';

    templates.forEach(t => {
        const item = document.createElement('div');
        item.className = 'preset-item';
        item.innerHTML = `
            <div class="preset-info">
                <div class="preset-name">${t.name}</div>
                <div class="preset-details">${t.sections.length} secciones | ${t.description || ''}</div>
            </div>
            <button class="btn btn-primary btn-small" onclick="generateSong('${t.name}')">🎼 Gen</button>
        `;
        elements.templatesList.appendChild(item);
    });
}

export async function generateSong(name) {
    logActivity(`Generando canción: ${name}...`);
    try {
        const data = await api.generateSongAPI({ template_name: name });
        if (data.success) {
            // Mostrar en el output principal o permitir descargar
            const output = document.getElementById('pattern-output');
            if (output) output.textContent = data.song_content;
            logActivity(`¡Canción "${name}" lista!`, 'success');
            closeSongTemplatesModal();
        }
    } catch (e) {
        console.error(e);
        logActivity('Error generando canción', 'error');
    }
}

// --- COMPARATOR ---
export function openComparatorModal() {
    if (elements.comparatorModal) elements.comparatorModal.style.display = 'block';
}

export function closeComparatorModal() {
    if (elements.comparatorModal) elements.comparatorModal.style.display = 'none';
}

// Estos hooks se pueden expandir luego si se necesita lógica real de comparación
export function selectPatternForComparison(side) {
    console.log(`Seleccionando patrón para lado ${side}`);
}

export function usePatternFromComparator(side) {
    const patternElem = document.getElementById(`pattern-${side.toLowerCase()}`);
    if (patternElem && patternElem.textContent) {
        window.state?.updateState('lastPattern', patternElem.textContent);
        logActivity(`Patrón ${side} seleccionado`);
        closeComparatorModal();
    }
}

// --- AI THOUGHTS (Intelligence Sidebar) ---
export function renderThoughts(thoughts) {
    const thoughtStream = document.getElementById('thought-stream');
    if (!thoughtStream) return;

    if (!thoughts || thoughts.length === 0) {
        thoughtStream.innerHTML = '<div class="thought-entry">Esperando generación...</div>';
        return;
    }

    thoughtStream.innerHTML = '';

    thoughts.forEach((t, i) => {
        const entry = document.createElement('div');
        entry.className = 'thought-entry';

        const prob = (t.prob || 0) * 100;

        // Add type-specific class
        if (prob > 70) entry.classList.add('step');
        else if (prob > 30) entry.classList.add('decision');
        else entry.classList.add('warning');

        const alternatives = (t.alternatives || t.alts || []).slice(0, 3).map(a =>
            `${a.token} (${(a.prob * 100).toFixed(0)}%)`
        ).join(', ');

        const altText = alternatives ? ` [alt: ${alternatives}]` : '';

        entry.textContent = `• ${t.token}${window.state?.genMode === 'ai' ? ` (${prob.toFixed(0)}%)` : ''}${altText}`;

        thoughtStream.appendChild(entry);
    });

    thoughtStream.scrollTop = thoughtStream.scrollHeight;
}

// --- UTILIDADES ---
function makeDraggable(element, header) {
    if (!header) return;
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    header.onmousedown = (e) => {
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = () => {
            document.onmouseup = null;
            document.onmousemove = null;
        };
        document.onmousemove = (e) => {
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            element.style.top = (element.offsetTop - pos2) + "px";
            element.style.left = (element.offsetLeft - pos1) + "px";
            element.style.right = 'auto';
        };
    };
}
