export function initThemeEngine() {
    // Subscriber to state changes handled in main.js or here if we import state
}

export function updateTheme(style) {
    if (!style) return;

    // Remover temas previos
    document.body.classList.remove(
        'theme-techno', 'theme-ambient', 'theme-glitch', 'theme-organic',
        'theme-cyberpunk', 'theme-industrial', 'theme-deepsea',
        'theme-house', 'theme-breakbeat', 'theme-experimental',
        'theme-dnb', 'theme-dub', 'theme-trap'
    );

    // Mapear estilos a temas
    const styleLower = style.toLowerCase();
    let theme = 'theme-techno'; // Default

    if (['ambient', 'chill', 'soft'].some(s => styleLower.includes(s))) theme = 'theme-ambient';
    else if (['glitch', 'noise'].some(s => styleLower.includes(s))) theme = 'theme-glitch';
    else if (['experimental', 'avant', 'abstract'].some(s => styleLower.includes(s))) theme = 'theme-experimental';
    else if (['organic', 'tribal', 'wood', 'nature'].some(s => styleLower.includes(s))) theme = 'theme-organic';
    else if (['house', 'disco', 'funk'].some(s => styleLower.includes(s))) theme = 'theme-house';
    else if (['dnb', 'drum', 'bass'].some(s => styleLower.includes(s))) theme = 'theme-dnb';
    else if (['breakbeat', 'jungle'].some(s => styleLower.includes(s))) theme = 'theme-breakbeat';
    else if (['techno', 'electro', 'drums'].some(s => styleLower.includes(s))) theme = 'theme-techno';
    else if (['cyberpunk', 'futuristic', 'neon'].some(s => styleLower.includes(s))) theme = 'theme-cyberpunk';
    else if (['industrial', 'hard', 'metal', 'steel'].some(s => styleLower.includes(s))) theme = 'theme-industrial';
    else if (['deepsea', 'ocean', 'darknavy', 'liquid'].some(s => styleLower.includes(s))) theme = 'theme-deepsea';
    else if (['dub', 'reggae', 'roots'].some(s => styleLower.includes(s))) theme = 'theme-dub';
    else if (['trap', '808', 'urban'].some(s => styleLower.includes(s))) theme = 'theme-trap';

    // Trigger pulse animation
    document.body.classList.add('theme-transitioning');
    setTimeout(() => {
        document.body.classList.remove('theme-transitioning');
    }, 600);

    document.body.classList.add(theme);

    // Sincronizar motor de partículas (Global por ahora)
    if (window.particleEngine) {
        window.particleEngine.setTheme(styleLower);
    }

    return theme;
}
