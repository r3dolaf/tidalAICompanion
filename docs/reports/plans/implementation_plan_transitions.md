# Plan: Structural Evolution & Transitions 🎼🥁

This phase moves TidalAI from a "loop generator" to a "performance engine" by adding narrative intelligence.

## Proposed Changes

### [Component] Backend: Transition Engine
#### [MODIFY] [structure_engine.py](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/generator/structure_engine.py)
- Add a `get_next_event()` method that signals if a section change is imminent (e.g., in the last bar of a section).
- Define "Fill" logic: short, high-energy patterns designed to resolve into a new section.

#### [MODIFY] [app.py](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/app.py)
- Create `/api/generate/fill` endpoint.
- Integrate transition signals in `/api/conductor/status`.

### [Component] Frontend: Performance UI
#### [MODIFY] [ui-manager.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/ui/ui-manager.js)
- Add a **"Morph"** control: allows smooth transitions between two patterns using Tidal's `xfade` or `interpolate`.
- Add a **"Transition Warning"** indicator in the Timeline.

#### [MODIFY] [conductor.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/modules/conductor.js)
- Update polling to handle transition events.
- Automatically trigger a "Fill" if the section is ending and "Auto-Transitions" is enabled.

## Feature Clarifications

| Feature | Goal | Logic |
| :--- | :--- | :--- |
| **Jam Session** | Improvisation | Random generation every N bars. Chaos-oriented. |
| **Cycle Send** | Live Evaluation | Continuous sending of current pattern. Performance stability. |
| **Conductor** | Narrative | Pre-planned structure (Intro-Verse-Drop). Goal-oriented. |
| **Transition Engine** | Cohesion | Connects section changes with fills and xfades. Flow-oriented. |

## Verification Plan

### Automated Tests
- Test `/api/generate/fill` to ensure it generates high-density, short patterns.
- Mock conductor status to verify transition triggers.

### Manual Verification
1. Start the Conductor on "Standard" template.
2. Observe the Timeline: as it reaches the end of "INTRO", check if a "FILL" message appears and the music changes for 1 bar.
3. Use the "Morph" button to manually transition between two disparate patterns.
