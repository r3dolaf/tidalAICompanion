# Plan: Centralized Timeline Update

The timeline currently doesn't update when using Macro generation because the `renderTimeline` call is missing in that code path. It's also missing for mutations and history actions.

## Proposed Changes

### [Component] UI Logic
#### [MODIFY] [main.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/main.js)
- **Centralize update**: Add `renderTimeline('pattern-timeline', elements.patternOutput.textContent)` to the end of `displayPattern`.
- **Remove redundancy**: Delete the manual `renderTimeline` call in `generatePattern`.
- **Ensure sync**: This ensures that *any* action calling `displayPattern` (Normal Gen, Macro Gen, Mutate, Undo, Redo, Favorite Loading) will automatically refresh the timeline.

## Verification Plan

### Manual Verification
1. Open TidalAI Studio.
2. Generate a normal pattern -> Verify timeline.
3. Generate a Macro Ensemble -> Verify timeline.
4. Apply a mutation -> Verify timeline.
5. Use Undo/Redo -> Verify timeline.
