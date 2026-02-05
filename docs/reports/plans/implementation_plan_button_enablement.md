# Plan: Centralized Button Enablement Fix

The "Cycle" button and sometimes others are staying disabled because the enablement logic is fragmented and incomplete.

## Proposed Changes

### [Component] UI Logic
#### [MODIFY] [main.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/main.js)
- **Centralize enablement**: Add a new helper function `enableActionButtons()` or add the logic directly into `displayPattern`.
- **Include all buttons**: Ensure `sendBtn`, `cycleSendBtn`, `mutateBtn`, `copyBtn`, and `favoriteBtn` are all set to `disabled = false`.
- **Remove fragmented logic**: Clean up the `if (state.lastPattern) { ... }` blocks in `generatePattern`, `generateMacroWave`, `mutatePattern`, and `useHistoryPattern`.

## Verification Plan

### Manual Verification
1. Open TidalAI Studio.
2. Generate a regular pattern -> Check if ALL 5 buttons are enabled.
3. Generate a Macro Ensemble -> Check if ALL 5 buttons are enabled.
4. Load a favorite -> Check if ALL 5 buttons are enabled.
5. Verify that `Cycle` button is now clickable.
