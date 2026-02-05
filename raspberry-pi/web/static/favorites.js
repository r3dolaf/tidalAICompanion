// Añadir al final de app.js

// ============================================
// GESTIÓN DE FAVORITOS
// ============================================

let favoritesList = [];

// Cargar lista de favoritos
async function loadFavorites() {
    try {
        const response = await fetch('/api/favorites');
        const data = await response.json();

        if (data.success) {
            favoritesList = data.favorites;
            updateFavoritesCount();
        }
    } catch (error) {
        console.error('Error cargando favoritos:', error);
    }
}

// Actualizar contador de favoritos
function updateFavoritesCount() {
    elements.favoritesCount.textContent = `${favoritesList.length} patrón${favoritesList.length !== 1 ? 'es' : ''} favorito${favoritesList.length !== 1 ? 's' : ''}`;
}

// Verificar si patrón es favorito
function isFavorite(pattern) {
    return favoritesList.includes(pattern);
}

// Toggle favorito (añadir/eliminar)
async function toggleFavorite() {
    if (!state.lastPattern) {
        logActivity('No hay patrón para añadir a favoritos', 'warning');
        return;
    }

    const pattern = state.lastPattern;
    const isCurrentlyFavorite = isFavorite(pattern);

    try {
        const response = await fetch('/api/favorites', {
            method: isCurrentlyFavorite ? 'DELETE' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pattern })
        });

        const data = await response.json();

        if (data.success) {
            if (isCurrentlyFavorite) {
                // Eliminar de la lista local
                favoritesList = favoritesList.filter(p => p !== pattern);
                elements.favoriteBtn.textContent = '⭐ Añadir a Favoritos';
                elements.favoriteBtn.classList.remove('favorite-active');
                logActivity('Patrón eliminado de favoritos');
            } else {
                // Añadir a la lista local
                favoritesList.push(pattern);
                elements.favoriteBtn.textContent = '★ En Favoritos';
                elements.favoriteBtn.classList.add('favorite-active');
                logActivity('Patrón añadido a favoritos');
            }
            updateFavoritesCount();
        } else {
            logActivity(data.error || 'Error gestionando favorito', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

// Añadir patrón manual
async function addManualPattern() {
    const pattern = elements.manualPattern.value.trim();

    if (!pattern) {
        logActivity('Escribe un patrón primero', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/favorites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pattern })
        });

        const data = await response.json();

        if (data.success) {
            favoritesList.push(pattern);
            updateFavoritesCount();
            elements.manualPattern.value = '';
            logActivity('Patrón añadido a favoritos');
        } else {
            logActivity(data.error || 'Error añadiendo patrón', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

// Re-entrenar modelo
async function retrainModel() {
    if (favoritesList.length === 0) {
        const confirm = window.confirm('No hay favoritos. ¿Re-entrenar solo con corpus base?');
        if (!confirm) return;
    }

    elements.retrainBtn.disabled = true;
    elements.retrainBtn.textContent = '⏳ Re-entrenando...';

    logActivity('Iniciando re-entrenamiento del modelo...');

    try {
        const response = await fetch('/api/retrain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            logActivity(`✓ Modelo re-entrenado con ${data.pattern_count} patrones`);

            // Feedback visual
            elements.retrainBtn.textContent = '✓ Completado';
            setTimeout(() => {
                elements.retrainBtn.textContent = '🔄 Re-entrenar Modelo';
            }, 3000);
        } else {
            logActivity('Error re-entrenando modelo: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    } finally {
        elements.retrainBtn.disabled = false;
    }
}

// Actualizar botón de favorito cuando se genera un patrón
function updateFavoriteButton(pattern) {
    if (isFavorite(pattern)) {
        elements.favoriteBtn.textContent = '★ En Favoritos';
        elements.favoriteBtn.classList.add('favorite-active');
    } else {
        elements.favoriteBtn.textContent = '⭐ Añadir a Favoritos';
        elements.favoriteBtn.classList.remove('favorite-active');
    }
    elements.favoriteBtn.disabled = false;
}
