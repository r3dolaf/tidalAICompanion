# Plan de Implementación - Reparación de Conectividad del Proyecto

Este plan detalla los pasos para centralizar todas las llamadas a la API del frontend en `network.js` y reparar brechas funcionales como la auto-actualización del Sample Scout y la ruta rota de `/api/samples/list`.

## Revisión del Usuario Requerida

> [!IMPORTANT]
> Esta refactorización centralizará toda la comunicación de la API. Aunque mejora el mantenimiento, afectará a múltiples módulos críticos de la interfaz (`advanced-features.js`, `phase2-features.js`, `panels.js`).

## Cambios Propuestos

### [Core] Centralización de la API

#### [MODIFY] [network.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/modules/network.js)
- Añadir las siguientes funciones envolventes:
  - `getCorpusStatsAPI()` -> `/api/corpus-stats`
  - `startJamSessionAPI(payload)` -> `/api/jam-session` (POST)
  - `createBackupAPI()` -> `/api/backup` (GET)
  - `restoreBackupAPI(formData)` -> `/api/restore` (POST)
  - `getSongTemplatesAPI()` -> `/api/song-templates`
  - `generateSongAPI(payload)` -> `/api/generate-song`
  - `getSamplesAPI()` -> `/api/samples` (GET)
  - `getSampleSuggestionsAPI(pattern, count)` -> `/api/samples/suggest`
  - `replaceSampleAPI(payload)` -> `/api/samples/replace`
  - `reindexSamplesAPI()` -> `/api/samples/index` (POST)
  - `getTheoryRulesAPI()` -> `/api/theory/rules`
  - `toggleTheoryRuleAPI(payload)` -> `/api/theory/toggle`
  - `addTheoryRuleAPI(payload)` -> `/api/theory/add`
  - `generateBatchAPI(payload)` -> `/api/generate-batch`
  - `interpretOracleAPI(text)` -> `/api/oracle/interpret`

---

### [Módulos UI] Reparación de Conectividad

#### [MODIFY] [advanced-features.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/advanced-features.js)
- Reemplazar todas las llamadas `fetch` por las nuevas funciones de `api.*`.
- Corregir `renderSampleList()` para usar `getSamplesAPI()` en lugar de `/api/samples/list` (que no existe en el backend).

#### [MODIFY] [phase2-features.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/phase2-features.js)
- Reemplazar todos los `fetch` (Jam, Stats, Backup/Restore) por funciones `api.*`.

#### [MODIFY] [panels.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/ui/panels.js)
- Reemplazar todos los `fetch` (Morph, Song Templates) por funciones `api.*`.

#### [MODIFY] [main.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/main.js)
- Reemplazar llamadas `fetch` de reglas y favoritos por funciones `api.*`.
- **Auto-actualización de Sample Scout**: Actualizar `displayPattern()` para que llame a `advanced.getSampleSuggestions(pattern)`. Esto hará que el panel de scout se refresque automáticamente con cada nueva generación.

---

## Plan de Verificación

### Verificación Manual
1. **Sample Scout**: Generar un patrón y verificar que el panel "Sample Scout" aparece y muestra sugerencias sin necesidad de clics manuales.
2. **Explorador de Librería**: Hacer clic en "Samples" en el dock de herramientas y verificar que enumera correctamente las carpetas de SuperDirt (esto verifica el arreglo de `/api/samples/list`).
3. **Generación por Lotes (Batch)**: Abrir la herramienta "Batch" y generar 10 patrones. Verificar que aparecen en el modal.
4. **Jam Session**: Iniciar una sesión de Jam y verificar que genera y envía patrones a TidalCycles automáticamente.
5. **Backup**: Activar un backup y verificar la notificación de éxito.
6. **Reglas Teóricas**: Abrir el gestor de reglas y verificar que activar/desactivar una regla funciona correctamente.
