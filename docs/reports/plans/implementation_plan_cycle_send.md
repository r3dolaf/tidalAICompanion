# Plan: Loop Send Mode (Cycle Send)

Add a feature to automatically re-send the current pattern at regular intervals, synchronized with the project's BPM. This creates a "Live Loop" feel where the code is constantly re-evaluated, similar to manual repetitive sending in a native environment.

## Proposed Changes

### [Component] Frontend UI
#### [MODIFY] [index.html](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/templates/index.html)
- Add the button next to the "Enviar" button in the `action-footer`.
- The new button will have a loop icon `🔄` and be called "Auto-Cycle".
- ID: `cycle-send-btn`.

#### [MODIFY] [v5-luxury.css](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/v5-luxury.css)
- Add styles for the active state of the cycle send button (pulsing glow).

### [Component] UI Logic
#### [MODIFY] [main.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/main.js)
- Implement `toggleCycleSend` function.
- Maintain a `cycleInterval` that tracks the `setInterval`.
- Calculate interval based on `state.config.tempo` (assuming 4 beats per cycle).
- Ensure the interval restarts if the BPM changes.
- Automatically re-send the `state.lastPattern` or the current editor content.

## Verification Plan

### Manual Verification
1. Open TidalAI Studio.
2. Generate a pattern and start the Cycle Send mode.
3. Verify that the "Send" visual feedback (LEDs, logs) occurs repeatedly.
4. Change the BPM and verify that the cycle speed adjusts (if possible, or at least stays functional).
5. Verify that stopping the mode clears the interval.
