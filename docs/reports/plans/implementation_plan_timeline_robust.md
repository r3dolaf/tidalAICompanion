# Plan: Robust Parallel Timeline Fix

The current timeline visualizer is failing to detect patterns in some cases, likely due to strict regex patterns or issues with multi-line channel tracking.

## Proposed Changes

### [Component] Timeline Visualizer
#### [MODIFY] [timeline-visualizer.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/modules/timeline-visualizer.js)
- **Robust Channel Tracking**: Maintain the last detected channel (d1, d2, etc.) across multiple lines until a new channel is detected.
- **Lenient Sound Detection**:
    - Support both `sound "..."` and `s "..."`.
    - Support optional `#` and whitespace variations.
    - Support single quotes `'` as well as double quotes `"`.
- **Improved Sound Categorization**:
    - Remove strict word boundaries `\b` for categories like `kick`, `snare`, etc., to support composite names like `clubkick` or `808sd`.
- **Parser Robustness**:
    - Handle `\r\n` and `\n` line endings.
    - Ensure `parseMiniNotation` handles empty layers gracefully.
    - Add a "fallback" track detection for lines that contain string patterns even if the keyword `sound` is missing (Tidal often assumes the first string is the sound).

## Verification Plan

### Manual Verification
1. Open TidalAI Studio.
2. Generate a Macro Ensemble.
3. Verify that all tracks (d1, d2, d3) appear on the timeline.
4. Manually type `d1 $ s "bd sn"` and check if it appears.
5. Manually type `d1 $ s "bd" # gain 1 # s "sn"` and check if both appear in parallel.
