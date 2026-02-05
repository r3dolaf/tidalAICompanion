# Implementation Plan - Nano Dock Refactor

## Goal
Optimize the Nano Dock layout by stacking buttons vertically to save horizontal space and removing redundancy.

## Proposed Changes

### HTML (index.html)
1.  **Remove** the `copy-nano-btn`.
2.  **Wrap** the remaining buttons (`undo`, `lock`, `marker`, `rec`, `stop`) in a new container `<div class="nano-vertical-dock">`.
3.  Ensure the new container is placed logically next to the editor.

### CSS (style.css)
1.  **Create `.nano-vertical-dock` rule**:
    ```css
    .nano-vertical-dock {
        display: flex;
        flex-direction: column;
        gap: 8px; /* Spacing between buttons */
        margin-left: 10px; /* Space from standard editor */
        align-items: center;
        padding: 5px;
        background: rgba(0,0,0,0.2);
        border-radius: 20px;
    }
    ```
2.  **Modify `.nano-btn`**:
    -   Ensure dimensions work well in column.

### JavaScript (main.js)
1.  **Remove `copyPattern` logic** (clean up).
2.  **Verify** references to `copy-nano-btn` are removed or handled safely.

## Verification
1.  **Visual:** Check buttons are stacked vertically.
2.  **Functional:** Undo, Lock, Marker, Rec, Stop should still work.
3.  **Clean:** No "Copy" button in the dock (User relies on Action Footer).
