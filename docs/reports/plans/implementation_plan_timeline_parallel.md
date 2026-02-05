# Plan: Fix Parallel Timeline Visualization

The pattern timeline currently fails to show parallel structures correctly, especially when using commas in mini-notation (e.g., `s "[bd sn, hh*8]"`) or when multiple channels are used (though the latter should work, it needs verification).

## Proposed Changes

### [Component] Frontend Visualization
#### [MODIFY] [timeline-visualizer.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/modules/timeline-visualizer.js)
- **Refactor `parseMiniNotation`**: 
    - Split the pattern by commas `,` first to handle parallel layers.
    - Each layer will reset its internal clock to 0.
    - Properly handle the `index / tokens.length` logic within each parallel layer.
- **Improve `parsePattern`**:
    - Ensure the regex handles `# s`, `s`, `sound` and variations like whitespace or lack thereof.
    - Add support for detecting `d1`, `d2`, etc., if we want to show track labels by channel.
- **Visual Improvements**:
    - If multiple sounds map to the same category but different channels, consider showing them separately or with a marker.

## Verification Plan

### Manual Verification
1. Open TidalAI Studio.
2. Generate a pattern that uses multiple channels or complex mini-notation (e.g., `d1 $ s "[bd sn, hh*8]"`).
3. Verify that the timeline shows the kick/snare and hi-hats starting at the same time (parallel) rather than sequentially.
4. Verify that multiple `s` calls in different lines are all displayed starting at time 0.
