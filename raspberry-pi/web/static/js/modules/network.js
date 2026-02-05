// API Wrapper for TidalAI

export async function generatePatternAPI(payload) {
    const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function generateMacroWaveAPI(payload) {
    const response = await fetch('/api/generate/macro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function mutatePatternAPI(payload) {
    const response = await fetch('/api/mutate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function sendPatternAPI(payload) {
    const response = await fetch('/api/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function stopAllAPI() {
    const response = await fetch('/api/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel: 'all' })
    });
    return response.ok; // No JSON returned usually for stop
}

export async function getFavoritesAPI() {
    const response = await fetch('/api/favorites');
    return await response.json();
}

export async function addFavoriteAPI(pattern, type = 'unknown') {
    const response = await fetch('/api/favorites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern, type })
    });
    return await response.json();
}

export async function deleteFavoriteAPI(pattern) {
    const response = await fetch('/api/favorites', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern })
    });
    return await response.json();
}

export async function retrainModelAPI() {
    const response = await fetch('/api/retrain', { method: 'POST' });
    return await response.json();
}

export async function checkStatusAPI() {
    try {
        const response = await fetch('/api/status');
        return await response.json();
    } catch (e) {
        return { success: false, osc: { connected: false } };
    }
}

export async function getSystemConfigAPI() {
    const response = await fetch('/api/config');
    return await response.json();
}

export async function saveSystemConfigAPI(config) {
    const response = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    });
    return await response.json();
}

// --- PHASE 38: CENTRALIZED API EXTENSIONS ---

export async function getCorpusStatsAPI() {
    const response = await fetch('/api/corpus-stats');
    return await response.json();
}

export async function startJamSessionAPI(payload) {
    const response = await fetch('/api/jam-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function createBackupAPI() {
    const response = await fetch('/api/backup');
    return await response.json();
}

export async function restoreBackupAPI(formData) {
    const response = await fetch('/api/restore', {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

export async function getSongTemplatesAPI() {
    const response = await fetch('/api/song-templates');
    return await response.json();
}

export async function generateSongAPI(payload) {
    const response = await fetch('/api/generate-song', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function getSamplesAPI() {
    const response = await fetch('/api/samples');
    return await response.json();
}

export async function getSampleSuggestionsAPI(pattern, count = 6) {
    const response = await fetch('/api/samples/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern, count })
    });
    return await response.json();
}

export async function replaceSampleAPI(pattern, oldSample, newSample) {
    const response = await fetch('/api/samples/replace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern, old_sample: oldSample, new_sample: newSample })
    });
    return await response.json();
}

export async function reindexSamplesAPI() {
    const response = await fetch('/api/samples/index', { method: 'POST' });
    return await response.json();
}

export async function getTheoryRulesAPI() {
    const response = await fetch('/api/theory/rules');
    return await response.json();
}

export async function toggleTheoryRuleAPI(genre, ruleId, active) {
    const response = await fetch('/api/theory/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ genre, rule_id: ruleId, active })
    });
    return await response.json();
}

export async function triggerEvolutionAPI() {
    const response = await fetch('/api/evolution/run', {
        method: 'POST'
    });
    return await response.json();
}

export async function addTheoryRuleAPI(payload) {
    const response = await fetch('/api/theory/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function generateBatchAPI(payload) {
    const response = await fetch('/api/generate-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function getBrainGraphAPI() {
    const response = await fetch('/api/brain/graph');
    return await response.json();
}

export async function generateMorphAPI(payload) {
    const response = await fetch('/api/generate/morph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function interpretOracleAPI(text) {
    const response = await fetch('/api/oracle/interpret', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    return await response.json();
}

export async function getPresetsAPI() {
    const response = await fetch('/api/presets');
    return await response.json();
}

export async function savePresetAPI(payload) {
    const response = await fetch('/api/presets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function deletePresetAPI(name) {
    const response = await fetch('/api/presets', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
    return await response.json();
}

export async function getHistoryAPI() {
    const response = await fetch('/api/history');
    return await response.json();
}

export async function addToHistoryAPI(payload) {
    const response = await fetch('/api/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function clearHistoryAPI() {
    const response = await fetch('/api/history', {
        method: 'DELETE'
    });
    return await response.json();
}

// --- CONDUCTOR ---

export async function getConductorTemplatesAPI() {
    const response = await fetch('/api/conductor/templates');
    return await response.json();
}

export async function startConductorAPI(payload) {
    const response = await fetch('/api/conductor/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function stopConductorAPI() {
    const response = await fetch('/api/conductor/stop', { method: 'POST' });
    return await response.json();
}

export async function getConductorStatusAPI() {
    const response = await fetch('/api/conductor/status');
    return await response.json();
}

export async function generateFillAPI(payload) {
    const response = await fetch('/api/generate/fill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

// --- SYSTEM ADMIN ---

export async function getSystemStatsAPI() {
    const response = await fetch('/api/system/stats');
    return await response.json();
}

export async function getSystemLogsAPI() {
    const response = await fetch('/api/system/logs');
    return await response.json();
}

export async function restartSystemAPI() {
    const response = await fetch('/api/system/restart', { method: 'POST' });
    return await response.json();
}

// --- AI TRAINING & EVOLUTION ---

export async function startEvolutionAPI(payload) {
    const response = await fetch('/api/train/evolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}

export async function runScavengeAPI() {
    const response = await fetch('/api/train/scavenge', { method: 'POST' });
    return await response.json();
}

export async function getEvolutionConfigAPI() {
    const response = await fetch('/api/config/evolution');
    return await response.json();
}

export async function saveEvolutionConfigAPI(payload) {
    const response = await fetch('/api/config/evolution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await response.json();
}
