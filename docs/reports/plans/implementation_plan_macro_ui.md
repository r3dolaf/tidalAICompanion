# Implementación: Refinamiento UI Macro-Wave

## Objetivo
Optimizar la ubicación y presentación del botón "Macro-Wave" (Generación de Ensamble Completo) basándose en el feedback del usuario.

## Opciones Propuestas

### Opción A: "El Director" (Panel Central Superior)
Mover el botón al panel central superior, justo encima o al lado del selector de estilos.
*   **Pros:** Jerarquía alta. Se entiende como un "modo maestro" que afecta a todo.
*   **Contras:** Puede saturar la zona de configuración.

### Opción B: "Botón Nuclear" (Integrado en Command Center)
Integrarlo en el panel derecho "Command Center", quizás reemplazando o complementando el botón principal de "GENERAR PATRÓN".
*   **Idea:** Un switch "Modo: Single / Macro" que cambie el comportamiento del botón grande.
*   **Pros:** Limpia la interfaz. Unifica la acción de generar.
*   **Contras:** Requiere un clic extra para cambiar de modo.

### Opción C: "Floating Action Button" (FAB)
Un botón flotante distintivo en la esquina inferior derecha del "Visualizer/Glass Panel".
*   **Pros:** Muy estético y accesible. Se siente "especial".
*   **Contras:** Puede tapar contenido o estorbar en móviles (aunque esto es desktop-first).

### Opción D: "Dock Dedicado"
Crear una pequeña sección "Ensamble" en la barra de docks inferior, separada de las herramientas creativas estándar.

## Recomendación
La **Opción B (Switch en Command Center)** parece la más coherente con la filosofía "Luxury v5", ya que reduce el ruido visual y empodera el botón principal.
