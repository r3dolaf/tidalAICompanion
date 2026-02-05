# Implementación: v5 Luxury Features

## 1. Hydra Living Background ("The Ether")
Transformar el motor Hydra de un "widget" a un "fondo activo".
*   **Canvas:** Insertar `<canvas id="hydra-bg">` con `position: fixed; z-index: -1`.
*   **Coexistencia:**
    *   `#hydra-bg`: Opacidad 0.3 (Sutil).
    *   `#particle-canvas`: Opacidad 1.0 (Partículas brillantes encima).
    *   Esto crea profundidad: Hydra es el "clima" y las partículas son la "vida".

## 2. The Brain Terminal (Modal de Pensamiento)
Crear un modal dedicado para ver los logs de razonamiento de la IA ('Thoughts').
*   **UI:** Estilo "Terminal Futurista" (fuente monospace, verde/ámbar sobre negro translúcido).
*   **Acceso:** Nuevo botón en la cabecera o dock: 🧠.
*   **Data:** Conectar `state.thoughts` para renderizar el historial completo.

## 3. Floating Header & Micro-Animations
*   **Header:** Cambiar `background: var(--surface)` a `backdrop-filter: blur(10px); background: transparent`.
*   **Animations:** Añadir keyframes `scanline` a los bordes de los paneles principales.

## Plan de Ejecución
1.  **HTML:** Añadir canvas Hydra y botón Brain. Crear estructura Modal Brain.
2.  **CSS:** Estilos para Background, nuevo Modal y Floating Header.
3.  **JS:** Inicializar Hydra en el nuevo canvas y lógica del Modal.
