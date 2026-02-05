# Implementation Plan - AI Contextual Refinement (Phase 36)

This phase aims to evolve the AI from a "stateless" generator to a context-aware collaborator that remembers its own musical history and provides deeper analysis of the patterns it creates.

## Proposed Changes

### [Component] Pattern Generator Logic (`raspberry-pi/generator/pattern_generator.py`)

#### [MODIFY] [pattern_generator.py](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/generator/pattern_generator.py)
- **State Management**: Add `self.pattern_history` to the `PatternGenerator` class.
- **Contextual Friction**: 
    - Implement a mechanism to compare a newly generated pattern with the `pattern_history`.
    - If similarity is high (>80% token overlap), use the `mutate` engine with high strength to "force" variation.
- **Humanizer Engine**: 
    - Add a `_humanize_pattern` method that adds subtle random deviations to numeric parameters (e.g., `# gain 0.9` -> `# gain 0.92`).
- **Integration**: Update `generate()` to automatically use these features when `use_ai` is active.

### [Component] Musical Theory Engine (`raspberry-pi/generator/theory_engine.py`)

#### [MODIFY] [theory_engine.py](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/generator/theory_engine.py)
- **Advanced Metrics**: 
    - Add `analyze_syncopation(pattern)`: Detects rhythmic displacement.
    - Add `analyze_variety(pattern)`: Measures token distribution diversity.
- **Insight Upgrade**: 
    - Enhance `get_musical_insight()` to include specific terminology (e.g., "High Syncopation detected", "Polyrhythmic Structure detected").
    - Provide actionable advice based on these metrics.

## Verification Plan

### Automated Tests
- **Rhythmic Analysis Test**:
    1. Create a small script `test_theory_v2.py` that passes a simple pattern (bd*4) and a complex one (bd(5,8)) to `TheoryEngine`.
    2. Verify that the "Syncopation" score is significantly higher for the second one.
- **History Tracking Test**:
    1. Update `PatternGenerator.py`'s `if __name__ == "__main__":` block to generate 5 patterns and assert that `self.pattern_history` has 5 entries.

### Manual Verification
- **Generation Variety**:
    1. Use the Web UI in **IA Generativa** mode.
    2. Click **Generar** 5 times quickly.
    3. Observe the `thoughts` panel for messages related to "Contextual Variation Applied".
    4. Verify that the patterns feel like an "evolution" rather than random jumps.
