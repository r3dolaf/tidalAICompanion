// Añadir al final de app.js - FUNCIONES DE MODAL Y FAVORITOS MEJORADAS

// ============================================
// MODAL DE FAVORITOS
// ============================================

function openFavoritesModal() {
    elements.favoritesModal.style.display = 'block';
    displayFavoritesList();
}

function closeFavoritesModal() {
    elements.favoritesModal.style.display = 'none';
}

// Mostrar lista de favoritos en el modal
function displayFavoritesList() {
    elements.favoritesList.innerHTML = '';

    if (state.favoritesList.length === 0) {
        elements.favoritesList.innerHTML = `
            <div style="text-align: center; color: #888; padding: 40px;">
                <div style="font-size: 3rem; margin-bottom: 15px;">⭐</div>
                <div>No hay favoritos guardados</div>
                <div style="font-size: 0.9em; margin-top: 10px;">Genera patrones y añádelos a favoritos</div>
            </div>
        `;
        return;
    }

    // Agrupar por tipo
    const byType = {};
    state.favoritesList.forEach(fav => {
        const type = fav.type || 'unknown';
        if (!byType[type]) byType[type] = [];
        byType[type].push(fav);
    });

    // Mostrar por tipo
    Object.keys(byType).sort().forEach(type => {
        const typeSection = document.createElement('div');
        typeSection.className = 'favorites-type-section';

        const typeHeader = document.createElement('div');
        typeHeader.className = 'favorites-type-header';
        typeHeader.innerHTML = `${patternTypeIcons[type]} ${type.toUpperCase()} (${byType[type].length})`;
        typeSection.appendChild(typeHeader);

        byType[type].forEach(fav => {
            const item = document.createElement('div');
            item.className = 'favorite-item';
            item.innerHTML = `
                <div class="favorite-pattern">${fav.pattern}</div>
                <div class="favorite-actions">
                    <button class="btn-icon" onclick="useFavoriteFromModal('${escapeHtml(fav.pattern)}')" title="Usar este patrón">
                        ▶️
                    </button>
                    <button class="btn-icon btn-delete" onclick="deleteFavoriteFromModal('${escapeHtml(fav.pattern)}')" title="Eliminar">
                        🗑️
                    </button>
                </div>
            `;
            typeSection.appendChild(item);
        });

        elements.favoritesList.appendChild(typeSection);
    });
}

// Usar favorito desde modal
function useFavoriteFromModal(pattern) {
    const favorite = state.favoritesList.find(f => f.pattern === pattern);
    if (favorite) {
        state.lastPattern = pattern;
        displayPattern(pattern, `Favorito (${favorite.type})`, null);
        elements.sendBtn.disabled = false;
        elements.copyBtn.disabled = false;
        logActivity(`Patrón favorito cargado: ${favorite.type}`);
        closeFavoritesModal();
    }
}

// Eliminar favorito desde modal
async function deleteFavoriteFromModal(pattern) {
    if (!confirm('¿Eliminar este patrón de favoritos?')) {
        return;
    }

    try {
        const response = await fetch('/api/favorites', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pattern })
        });

        const data = await response.json();

        if (data.success) {
            state.favoritesList = state.favoritesList.filter(f => f.pattern !== pattern);
            updateFavoritesCount();
            displayFavoritesList();
            logActivity('Patrón eliminado de favoritos');

            // Actualizar botón si es el patrón actual
            if (state.lastPattern === pattern) {
                updateFavoriteButton(pattern);
            }
        } else {
            logActivity(data.error || 'Error eliminando favorito', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}

// ============================================
// FAVORITOS CON TIPO
// ============================================

// Verificar si patrón es favorito (actualizado para objetos)
function isFavorite(pattern) {
    return state.favoritesList.some(fav => fav.pattern === pattern);
}

// Toggle favorito (actualizado para incluir tipo)
async function toggleFavorite() {
    if (!state.lastPattern) {
        logActivity('No hay patrón para añadir a favoritos', 'warning');
        return;
    }

    const pattern = state.lastPattern;
    const isCurrentlyFavorite = isFavorite(pattern);

    if (isCurrentlyFavorite) {
        // Eliminar
        try {
            const response = await fetch('/api/favorites', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pattern })
            });

            const data = await response.json();

            if (data.success) {
                state.favoritesList = state.favoritesList.filter(f => f.pattern !== pattern);
                elements.favoriteBtn.textContent = '⭐ Añadir a Favoritos';
                elements.favoriteBtn.classList.remove('favorite-active');
                updateFavoritesCount();
                logActivity('Patrón eliminado de favoritos');
            } else {
                logActivity(data.error || 'Error eliminando favorito', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            logActivity('Error de conexión', 'error');
        }
    } else {
        // Añadir con tipo
        try {
            const response = await fetch('/api/favorites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pattern: pattern,
                    type: state.patternType  // Incluir tipo actual
                })
            });

            const data = await response.json();

            if (data.success) {
                state.favoritesList.push({
                    pattern: pattern,
                    type: state.patternType,
                    timestamp: Date.now()
                });
                elements.favoriteBtn.textContent = '★ En Favoritos';
                elements.favoriteBtn.classList.add('favorite-active');
                updateFavoritesCount();
                logActivity(`Patrón ${state.patternType} añadido a favoritos`);
            } else {
                logActivity(data.error || 'Error añadiendo favorito', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            logActivity('Error de conexión', 'error');
        }
    }
}

// Añadir patrón manual (actualizado para pedir tipo)
async function addManualPattern() {
    const pattern = elements.manualPattern.value.trim();

    if (!pattern) {
        logActivity('Escribe un patrón primero', 'warning');
        return;
    }

    // Pedir tipo al usuario
    const type = prompt('¿Qué tipo de patrón es?\nOpciones: drums, bass, melody, percussion, fx', 'drums');

    if (!type) return;

    const validTypes = ['drums', 'bass', 'melody', 'percussion', 'fx'];
    const patternType = validTypes.includes(type.toLowerCase()) ? type.toLowerCase() : 'unknown';

    try {
        const response = await fetch('/api/favorites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pattern: pattern,
                type: patternType
            })
        });

        const data = await response.json();

        if (data.success) {
            state.favoritesList.push({
                pattern: pattern,
                type: patternType,
                timestamp: Date.now()
            });
            updateFavoritesCount();
            elements.manualPattern.value = '';
            logActivity(`Patrón ${patternType} añadido a favoritos`);
        } else {
            logActivity(data.error || 'Error añadiendo patrón', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        logActivity('Error de conexión', 'error');
    }
}
