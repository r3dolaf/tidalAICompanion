# User Objective
Move the "Theorist Insight" and "Brain/Thought" logic into a dedicated Right Sidebar, creating a 3-column layout (Instruments | Code | Intelligence). Remove the now-redundant "Brain" button from the header.

## Proposed Changes

### `raspberry-pi/web/templates/index.html`
- **Container Structure**: 
    - Verify `main` container uses `display: flex`.
    - Current: `.sidebar` (Left) and `.right-panel` (everything else).
    - New: `.sidebar` (Left), `.center-panel` (Code + Actions), `.intelligence-sidebar` (Right).
- **Header**: Remove the Brain button (`toggleBrainPanel`).
- **Right Sidebar Content**:
    - **Thought Stream**: A persistent log of AI thoughts (moved from modal).
    - **Theorist Insight**: The existing hypothesis panel.
    - **Visuals**: Maybe move the "Theorist Verified" badge here too?

### `raspberry-pi/web/static/js/main.js` (and `modals.js`?)
- Update `logToBrainTerminal` logic (if it exists) to target the new persistent visible div instead of checking for a modal.
- Remove `toggleBrainPanel` event listener.

### `raspberry-pi/web/static/style.css` / `v5-luxury.css`
- Define `.intelligence-sidebar` styles (width: ~300px, glassmorphism).
- Ensure 3-column layout is responsive (collapse to stack on mobile?).

## Verification Plan

### Manual Verification
- **Layout**: Reload page. Check for 3 distinct columns.
- **Brain Button**: Confirm it's gone from the header.
- **Functionality**: Generate a pattern. Confirm "Thoughts" and "Insight" appear in the right sidebar.
