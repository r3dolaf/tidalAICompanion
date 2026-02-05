# Plan: Glass Segmented Mode Switcher 🎨✨

Replace the current "Pattern Mode" button with a sleek, dual-segment control for switching between Single Pattern ("Solo") and Macro Ensemble ("Macro").

## Proposed Changes

### [Component] Frontend UI
#### [MODIFY] [index.html](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/templates/index.html)
- Replace `macro-toggle-wrapper` with a new `mode-selector-luxury` container.
- Add two segments: "Solo" and "Macro".
- Keep the hidden checkbox if needed for backward compatibility, but update logic to use the segments.

#### [MODIFY] [v5-luxury.css](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/v5-luxury.css)
- Implement styles for `.mode-selector-luxury`.
- Create a sliding "pill" effect that moves when the mode changes.
- Use glassmorphism and neon accents.

### [Component] UI Logic
#### [MODIFY] [ui-manager.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/ui/ui-manager.js)
- Update click listeners to handle the new segmented control.
- Ensure the `generate-btn` still updates its text/style based on the selection.

## Verification Plan

### Manual Verification
1. Open TidalAI Studio.
2. Observe the new **Solo / Macro** switcher.
3. Click **Macro** -> Verify the slider moves and the "Generar" button changes to "GENERAR MACRO".
4. Click **Solo** -> Verify it returns to normal.
5. Generate in both modes to ensure full functionality.
