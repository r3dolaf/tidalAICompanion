# User Objective
Move the "Theorist Insight" panel to the right of the Code Editor + Action Buttons block, creating a side-by-side layout within the right panel.

## Proposed Changes

### `raspberry-pi/web/templates/index.html`

- **Correct Structure**: Identify the premature closing `</div>` of `.right-panel` (approx line 245) and remove it.
- **Split View Container**: Insert `<div class="split-view-container" style="display: flex; gap: 10px; align-items: flex-start;">` before the `.code-editor-wrapper`.
- **Left Column**: Wrap `.code-editor-wrapper` and `.action-footer` in `<div class="left-col" style="flex: 1; display:flex; flex-direction:column;">`.
- **Right Column**: Wrap `#insight-panel` in `<div class="right-col" style="width: 250px; flex-shrink: 0;">`.
- **Close Containers**: Ensure all new divs are closed properly and finally close `.right-panel` at the end of the block.

## Verification Plan

### Manual Verification
- **Visual Check**: Reload the page. Verify that the "Insight Panel" (initially hidden or visible) appears to the right of the code editor.
- **Interaction Check**: Click "Generate Pattern" to trigger content in both the code editor and the insight panel.
- **Layout Check**: Ensure buttons stay attached to the bottom of the code editor and do not jump. Ensure the Insight panel expands vertically without affecting the code editor's position.
