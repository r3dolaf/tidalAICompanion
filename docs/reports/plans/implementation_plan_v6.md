# Implementation Plan - TidalAI Studio v6 (Bento Grid)

**Goal:** Transform the current rigid 4-column layout into a modern, modular **Bento Grid** interface. This aims to maximize screen real estate, unify related controls, and improve the "flow" of music creation.

**Safety Protocol:** We will work "non-destructively" where possible, verifying each zone's functionality before moving to the next.

## User Review Required
> [!IMPORTANT]
> **Major Layout Change:** This moves knobs and instruments into a SINGLE unified "Control Deck" on the left.
> **CSS Strategy:** We will create a fresh `v6-bento.css` to avoid polluting the existing `v5-luxury.css` during the transition, eventually replacing it.

---

## Architecture: The 3 Zones
Instead of "Columns 1, 2, 3, 4", we define "Zones":

1.  **Zone A: Command Deck (Left)** ~350px
    *   *Combines:* Visual Knobs + Instrument Selectors + Generic Parameters.
    *   *New Widget:* "Unified Parameter Panel" (Tabbed or Scrollable).
2.  **Zone B: Composition Core (Center)** ~Flexible (1fr)
    *   *Focus:* Code Editor + Action Bar + Terminal Output.
    *   *Upgrade:* Larger, cleaner editor space.
3.  **Zone C: Intelligence Stack (Right)** ~260px
    *   *Focus:* Timeline + AI Reasoning + Insight.
    *   *Style:* Vertical stack of "glass" cards.

---

## Proposed Changes

### 1. Style Foundation
#### [NEW] [v6-bento.css](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/v6-bento.css)
- Define CSS Grid areas: `'header header header' 'controls editor ai'`.
- Define "Bento Card" utility classes (frosted glass, rounded corners, inner padding).
- Port essential animations from v5 (neon scan, pulses).

### 2. HTML Restructuring
#### [MODIFY] [index.html](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/templates/index.html)
- **Step 1:** Change main container class to `.layout-bento`.
- **Step 2 (Zone A):** Wrap `.visual-knobs-sidebar` and `.left-panel-content` into a new container: `<div class="bento-zone-controls">`.
- **Step 3 (Zone B):** Optimize `.right-panel` (remove internal wrappers if redundant) to become `<div class="bento-zone-editor">`.
- **Step 4 (Zone C):** Refine `.intelligence-sidebar` to `<div class="bento-zone-ai">`.

### 3. Logic & JS Updates
#### [MODIFY] [main.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/main.js)
- Verify `displayPattern` and `renderTimeline` render correctly in new containers.
- Ensure "Generate" button animations target correct selectors in new CSS.

---

## Verification Plan

### Automated / Structural Checks
- [ ] Verify 3 main columns exist (Controls, Editor, AI).
- [ ] Verify `bento-zone-controls` contains BOTH knobs and instrument buttons.
- [ ] Check console for JS errors (especially relating to missing DOM IDs).

### Manual Verification (User)
- [ ] **Functionality:** Do the knobs still control Hydra? Do the instrument buttons still insert code?
- [ ] **Responsiveness:** Does the code editor expand when the window is resized?
- [ ] **Visuals:** Is the "Generate" button animation glitch-free?
