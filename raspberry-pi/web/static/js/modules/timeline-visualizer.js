/**
 * Pattern Timeline Visualizer
 * Parses TidalCycles patterns and renders them as a visual timeline
 */

// Sound category mapping with colors (More lenient regexes)
const SOUND_CATEGORIES = {
    // Drums
    kick: { regex: /(bd|bass|kick)/i, color: '#ef4444', label: 'Kick' },
    snare: { regex: /(sd|snare|cp|clap)/i, color: '#3b82f6', label: 'Snare' },
    hihat: { regex: /(hh|hc|ho|hat)/i, color: '#fbbf24', label: 'Hi-Hat' },
    tom: { regex: /(lt|mt|ht|tom)/i, color: '#f97316', label: 'Tom' },
    cymbal: { regex: /(cy|crash|ride)/i, color: '#e5e7eb', label: 'Cymbal' },
    perc: { regex: /(perc|shaker|conga|bongo)/i, color: '#a855f7', label: 'Perc' },

    // Melodic
    bass: { regex: /(bass|sub|jung|deep)/i, color: '#10b981', label: 'Bass' },
    synth: { regex: /(synth|lead|pad|juno|moog)/i, color: '#06b6d4', label: 'Synth' },
    keys: { regex: /(piano|keys|organ|casio)/i, color: '#60a5fa', label: 'Keys' },

    // FX
    fx: { regex: /(fx|noise|glitch|rev)/i, color: '#6b7280', label: 'FX' }
};

/**
 * Categorize a sound name
 */
function categorizeSound(soundName) {
    if (!soundName) return { color: '#64748b', label: '?', key: 'unknown' };

    for (const [key, category] of Object.entries(SOUND_CATEGORIES)) {
        if (category.regex.test(soundName)) {
            return { ...category, key };
        }
    }

    // Generate color from hash for unknown sounds
    const hash = soundName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const hue = hash % 360;
    return {
        color: `hsl(${hue}, 70%, 60%)`,
        label: soundName.substring(0, 8),
        key: soundName
    };
}

/**
 * Parse TidalCycles pattern to extract events
 */
export function parsePattern(patternCode) {
    const events = [];
    const tracks = new Map();

    if (!patternCode || typeof patternCode !== 'string') {
        return { events: [], tracks: [] };
    }

    // Split by lines and clean them
    const lines = patternCode.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);

    let currentChannel = 'd1'; // Fallback channel

    lines.forEach((line) => {
        // 1. Detect channel if present (e.g. "d1 $ ...")
        const chMatch = line.match(/^d(\d+)/);
        if (chMatch) {
            currentChannel = `d${chMatch[1]}`;
        }

        // 2. Extract sound patterns: sound "..." or s '...' or even # s "..."
        // Also captures cases like d1 "bd sn" (implicit s)
        // More robust regex for sound/s keyword + quotes
        const soundRegex = /(?:#\s+)?\b(?:sound|s)\s+["']([^"']+)["']/g;
        let match;
        let foundSomething = false;

        while ((match = soundRegex.exec(line)) !== null) {
            foundSomething = true;
            const soundPattern = match[1];
            const parsedEvents = parseMiniNotation(soundPattern);

            processEvents(parsedEvents, currentChannel, tracks, events);
        }

        // 3. Fallback: If no 's' or 'sound' but there is 1+ quoted string, assume those are sounds
        if (!foundSomething) {
            const fallbackRegex = /["']([^"']+)["']/g;
            let fbMatch;
            while ((fbMatch = fallbackRegex.exec(line)) !== null) {
                const soundPattern = fbMatch[1];
                // Ignore small strings that look like numeric notes if they are just digits
                if (/^\d+(\.\d+)?$/.test(soundPattern)) continue;

                const parsedEvents = parseMiniNotation(soundPattern);
                processEvents(parsedEvents, currentChannel, tracks, events);
            }
        }
    });

    return {
        events: events.sort((a, b) => a.time - b.time),
        tracks: Array.from(tracks.values())
    };
}

/**
 * Helper to process events into tracks
 */
function processEvents(parsedEvents, channel, tracks, events) {
    parsedEvents.forEach(event => {
        const category = categorizeSound(event.sound);

        // Track ID includes channel to separate parallel tracks of same type
        const trackId = `${channel}-${category.key}`;
        const trackLabel = `${channel} ${category.label}`;

        if (!tracks.has(trackId)) {
            tracks.set(trackId, {
                id: trackId,
                label: trackLabel,
                color: category.color
            });
        }

        events.push({
            time: event.time,
            duration: event.duration,
            sound: event.sound,
            track: trackId,
            color: category.color
        });
    });
}

/**
 * Parse mini-notation
 * Supports: basic sequences, multiplication (*), rests (~), and parallel layers (comma ,)
 */
function parseMiniNotation(pattern) {
    const events = [];
    if (!pattern || typeof pattern !== 'string') return events;

    // Handle parallel layers: "[bd sn, hh*8]"
    let cleanPattern = pattern.trim();
    // Remove brackets if they enclose the whole thing
    if (cleanPattern.startsWith('[') && cleanPattern.endsWith(']')) {
        cleanPattern = cleanPattern.substring(1, cleanPattern.length - 1);
    }
    if (cleanPattern.startsWith('<') && cleanPattern.endsWith('>')) {
        cleanPattern = cleanPattern.substring(1, cleanPattern.length - 1);
    }

    // Split by commas to find parallel layers
    const layers = cleanPattern.split(',');

    layers.forEach(layer => {
        // Clean layer from other brackets
        const cleanLayer = layer.replace(/[\[\]<>]/g, ' ');
        const tokens = cleanLayer.split(/\s+/).filter(t => t.length > 0);

        if (tokens.length === 0) return;

        tokens.forEach((token, index) => {
            if (token === '~') return;

            // Handle multiplication: "bd*4"
            const multMatch = token.match(/^(.+?)\*(\d+)$/);
            if (multMatch) {
                const sound = multMatch[1];
                const count = parseInt(multMatch[2]);
                if (count <= 0) return;

                const stepDuration = 1.0 / (tokens.length * count);

                for (let i = 0; i < count; i++) {
                    events.push({
                        sound,
                        time: (index / tokens.length) + (i * stepDuration),
                        duration: stepDuration * 0.9
                    });
                }
            } else {
                // Simple token
                events.push({
                    sound: token,
                    time: index / tokens.length,
                    duration: (1.0 / tokens.length) * 0.9
                });
            }
        });
    });

    return events;
}

/**
 * Render timeline on canvas
 */
export function renderTimeline(canvasId, patternCode) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const { events, tracks } = parsePattern(patternCode);

    // Set canvas size
    const width = canvas.clientWidth;
    const height = Math.max(150, tracks.length * 30 + 40);
    canvas.width = width;
    canvas.height = height;

    // Clear canvas
    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
    ctx.fillRect(0, 0, width, height);

    if (tracks.length === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No pattern detected', width / 2, height / 2);
        return;
    }

    const padding = 10;
    const labelWidth = 60;
    const timelineWidth = width - labelWidth - padding * 2;
    const trackHeight = 25;
    const eventHeight = 18;

    // Draw grid lines (beats)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const x = labelWidth + (i / 4) * timelineWidth;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.moveTo(x, height - padding);
        ctx.stroke();
    }

    // Draw tracks and events
    tracks.forEach((track, trackIndex) => {
        const y = padding + trackIndex * trackHeight;

        // Draw track label
        ctx.fillStyle = track.color;
        ctx.font = 'bold 11px Inter, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(track.label, labelWidth - 5, y + eventHeight / 2 + 4);

        // Draw events for this track
        const trackEvents = events.filter(e => e.track === track.id);
        trackEvents.forEach(event => {
            const x = labelWidth + event.time * timelineWidth;
            const w = event.duration * timelineWidth;

            // Draw event bar
            ctx.fillStyle = event.color;
            ctx.fillRect(x, y, w, eventHeight);

            // Draw border
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, w, eventHeight);
        });
    });

    // Draw cycle marker
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('1 cycle', labelWidth + timelineWidth / 2, height - 5);
}

/**
 * Initialize timeline with auto-update
 */
export function initTimeline(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Make canvas responsive
    const resizeCanvas = () => {
        const pattern = document.getElementById('pattern-output')?.textContent || '';
        renderTimeline(canvasId, pattern);
    };

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
}
