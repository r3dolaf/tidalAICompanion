# Plan: Core Functionality Repair (main.js & ui-manager.js)

The "Generar" and "Macro" buttons are broken due to a syntax error (missing closing brace for `generatePattern`) and unintended function nesting.

## Proposed Changes

### [Component] Core Logic
#### [MODIFY] [main.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/main.js)
- **Fix nesting**: Add the missing closing brace `}` to `generatePattern` at the end of its `finally` block.
- **Un-nest functions**: Ensure `generateMacroWave`, `mutatePattern`, `sendPattern`, and `toggleCycleSend` are all top-level functions (not nested inside each other or `generatePattern`).
- **Fix Syntax**: Resolve the `'}' expected` error at the end of the file.
- **Remove Duplicates**: Check for and remove any duplicate definitions of `toggleCycleSend` if they exist.

### [Component] UI Management
#### [MODIFY] [ui-manager.js](file:///C:/Users/alfredo/Desktop/tidalai-companion/raspberry-pi/web/static/js/ui/ui-manager.js)
- **Verify bindings**: Ensure `generateBtn` and `macroBtn` listeners are correctly calling the intended functions.
- **Ensure Scope**: Verify that `acts` (or `actions`) is correctly passed and contains the repaired functions.

## Verification Plan

### Automated Verification
- Check for lint/syntax errors in the browser console (if possible, or via lint tool).

### Manual Verification
1. Open TidalAI Studio.
2. Click **🎲 GENERAR PATRÓN** -> Verify it works.
3. Toggle to **Modo Macro** and click **🌊 GENERAR MACRO** -> Verify it works.
4. Click **🧬 Mutar** -> Verify it works.
5. Click **🔄 Cycle** -> Verify it works.
