# Implementation Plan - Nano Dock Expansion

To maximize the utility of the vertical "Nano Dock", we will add high-frequency edition tools.

## Proposed Changes

### HTML (index.html)
Add 3 new buttons to the `.nano-dock` container:
```html
<button id="undo-btn" class="nano-btn" onclick="undoPattern()" title="Deshacer (Undo)">⏮</button>
<button id="lock-btn" class="nano-btn" onclick="toggleLock()" title="Bloquear Generación (Freeze)">🔓</button>
<button id="copy-nano-btn" class="nano-btn" onclick="copyPattern()" title="Copiar al portapapeles">📋</button>
```
*Note: We will keep the existing Rec and Marker buttons.*

### JavaScript (main.js)

1.  **Undo Logic:**
    -   We already have `sessionHistory`. We can simply pop the last item?
    -   Actually, `sessionHistory` is for the long term. We might need a generic `undoStack` for the current session.
    -   *Simpler:* When generating, push current editor content to `undoStack`.
    -   `undoPattern()`: Pops from `undoStack` and sets editor content.

2.  **Lock Logic:**
    -   `isGenerationLocked` boolean.
    -   If true, `displayPattern` returns early (refuses to update).
    -   Visuals: Change icon 🔓 -> 🔒 and color (Amber/Orange).

3.  **Copy Logic:**
    -   Reuse existing `copyToClipboard` function but trigger from new button.

### CSS (style.css)
Add specific styles for:
-   `#lock-btn.locked`: Amber glow.
-   `#undo-btn`: Standard hover.

## Verification
1.  **Undo:** Generate pattern A -> B. Click Undo. Should revert to A.
2.  **Lock:** Click Lock. Click Generate. Output should NOT change.
3.  **Copy:** Click Copy. Paste in Notepad. Should match.
