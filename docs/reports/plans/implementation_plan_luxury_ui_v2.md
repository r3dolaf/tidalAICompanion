# Implementation Plan - Morph Persistence & Luxury Blend UI

This plan aims to improve the user experience of the performance controls and the overall aesthetics of the Genre Blender component.

## User Review Required
> [!IMPORTANT]
> I will replace the standard HTML checkbox for "Modo Blend" with a custom-styled "Luxury Switch". This will change its appearance from a square box to a sliding toggle.

## Proposed Changes

### [Component] Action Buttons Logic (`raspberry-pi/web/static/js/main.js`)
- **Persistence**: Update `displayPattern` to re-apply the `active-morph` class to `elements.morphBtn` if `state.morphMode` is true.
- **Cycle Mode Sync**: Ensure that `morphMode` behaves as a global toggle that doesn't reset when generating new patterns.

### [Component] UI Elements (`raspberry-pi/web/templates/index.html`)
- **Luxury Switch**: Replace the `<input type="checkbox">` in the Genre Blender section with a luxury switch structure:
  ```html
  <label class="luxury-switch">
      <input type="checkbox" id="blend-mode-toggle">
      <span class="luxury-slider"></span>
      <span class="label-text">🌀 Modo Blend</span>
  </label>
  ```

### [Component] Luxury Styling (`raspberry-pi/web/static/v5-luxury.css`)
- **Switch CSS**: Add styles for `.luxury-switch`, `.luxury-slider`, and its `:checked` states. Use glassmorphism and neon glows.
- **Morph Animation**: Refine `morph-glow` to be slightly faster or more multi-colored to distinguish it from the standard pulse.

## Verification Plan

### Manual Verification
1. **Morph Persistence**:
    - Activate **Morph** (〰️).
    - Click **Generar** 🎲.
    - Verify that the button remains glowing/active after the pattern updates.
2. **Luxury Switch**:
    - Open the **Identidad** card.
    - Verify that the "Modo Blend" looks like a modern toggle rather than a checkbox.
    - Click it to ensure it still opens/closes the blend controls correctly.
