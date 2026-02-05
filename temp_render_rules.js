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
