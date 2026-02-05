# Implementation Plan - Hydra Visual Expansion

Add more performance-ready visual controls to the vertical sidebar.

## Proposed Changes

### [Component] Visual Sidebar (`raspberry-pi/web/templates/index.html`)
- **New Sliders**: Add two more vertical sliders:
  - **Cromaticidad**: For color shifting.
  - **Simetría**: For kaleidoscope/recursion effects.

### [Component] UI Logic (`raspberry-pi/web/static/js/ui/ui-manager.js`)
- **Element Mapping**: Add mapping for `visualColor` and `visualSymmetry` sliders and their hint labels.
- **Event Listeners**: Attach listeners to update the state when these sliders change.

### [Component] Hydra Engine (`raspberry-pi/web/static/js/modules/visuals-hydra.js`)
- **Parameter Extraction**: Extract `visualColor` and `visualSymmetry` from the config.
- **Dynamic Application**:
  - Use `visualColor` to apply a `.hue(value)` or modify `.color()`.
  - Use `visualSymmetry` to override or multiply the `.kaleid()` factor across styles.

### [Component] Styling (`raspberry-pi/web/static/v5-luxury.css`)
- **Grid Layout**: Adjust `.visual-vertical-sidebar` to handle 4 sliders instead of 2.

## Verification Plan

### Manual Verification
1. **Vertical UI**: Verify 4 sliders are visible in the sidebar.
2. **Cromaticidad**: Move the slider and check if the palette of the current style shifts colors.
3. **Simetría**: Move the slider and check if the visuals gain more "facets" (kaleidoscope effect).
4. **Persistence**: Ensure settings remain active when a new pattern is generated.
