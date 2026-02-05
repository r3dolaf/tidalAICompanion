# Pattern Timeline Visualizer

## Goal
Create a visual timeline component in the Intelligence sidebar that parses the current TidalCycles pattern and displays events (kicks, snares, hats, etc.) as a graphical representation, making the rhythmic structure immediately visible.

## Proposed Changes

### `raspberry-pi/web/templates/index.html`
- Add new Timeline component to Intelligence sidebar (between Insight and AI Reasoning)
- Structure:
  ```html
  <section class="card intelligence-card">
    <h2>🎼 Pattern Timeline</h2>
    <canvas id="pattern-timeline" class="timeline-canvas"></canvas>
  </section>
  ```

### `raspberry-pi/web/static/js/modules/timeline-visualizer.js` (NEW)
- **Parser**: Extract events from TidalCycles pattern string
  - Detect sound sources: `sound "bd"`, `sound "cp"`, etc.
  - Parse mini-notation: `"bd*4"`, `"[bd sd, hh*8]"`, etc.
  - Extract timing: cycles, subdivisions, rests `~`
- **Renderer**: Draw events on canvas
  - X-axis: Time (1 cycle = full width)
  - Y-axis: Tracks (one per sound/layer)
  - Visual encoding:
    - Kicks (bd) = Red bars
    - Snares (sd/cp) = Blue bars
    - Hats (hh/hc) = Yellow bars
    - Other = Gray bars
  - Event height = velocity/gain (if available)

### `raspberry-pi/web/static/intelligence-sidebar.css`
- Styles for timeline canvas
- Track labels
- Responsive sizing

### `raspberry-pi/web/static/js/main.js`
- Call `renderTimeline(pattern)` after successful generation
- Update timeline when pattern changes

## Technical Approach

### Pattern Parsing Strategy
1. **Regex-based extraction**: Identify `sound "..."` blocks
2. **Mini-notation parser**: Expand `*`, `/`, `[]`, `<>` operators
3. **Event list**: Convert to `[{time, duration, sound, track}]`

### Canvas Rendering
- Use 2D context for performance
- Grid lines for beat divisions
- Color-coded tracks
- Hover tooltips showing event details

## Verification Plan

### Manual Verification
1. Generate a simple pattern (e.g., `sound "bd sd bd sd"`)
2. Check timeline shows 4 events evenly spaced
3. Generate complex pattern with polyrhythms
4. Verify multiple tracks render correctly
5. Test with different pattern types (drums, bass, melody)
