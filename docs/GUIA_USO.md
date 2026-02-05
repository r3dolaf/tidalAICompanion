# Guía de Uso: TidalAI Companion

> Manual actualizado con las nuevas funcionalidades avanzadas (Fase 1-18)

---

## 📋 Tabla de Contenidos

1. [Características Principales](#características-principales)
2. [Gestión de Patrones](#gestión-de-patrones)
3. [Herramientas de Producción](#herramientas-de-producción)
4. [Herramientas Analíticas](#herramientas-analíticas)
5. [Uso Básico](#uso-básico)
6. [API REST](#api-rest)

---

## Características Principales

Hemos transformado TidalAI Companion en una suite completa de producción. Aquí están las herramientas que tienes a tu disposición:

### Funcionalidades Core
- **Generación Dual**: IA (Markov) + Reglas
- **Control Total**: Densidad, Complejidad, Tempo, Estilo
- **Responsive**: Funciona en tu celular o tablet

### Funcionalidades Avanzadas
- **Presets**: Guarda y recupera configuraciones.
- **Historial Interactiva**: Búsqueda instantánea y re-uso.
- **Batch Generator**: Ideas masivas en segundos.
- **Editor Inline**: Ajustes finos sin salir de la web.
- **Jam Session**: Generación continua multi-canal.
- **Templates**: Canciones completas con un click.
- **Visualizador**: Ve la música antes de escucharla.
- **Morfador de Riffs**: Mezcla de patrones rítmicos.
- **Skin Engine**: Estética autoadaptativa por género.
- **Partículas**: Feedback visual reactivo en el fondo.
- **The Theorist (Phase 17)**: Validación de reglas musicales con reintentos automáticos.
- **Rules Editor (Phase 17b)**: Gestión dinámica de reglas de validación.
- **Latent Space (Phase 18)**: Mezcla matemática de géneros (e.g., 70% Techno + 30% Ambient).

---

## Gestión de Patrones

### Presets del Sistema 💾
No pierdas tiempo reconfigurando.
1. Ajusta los sliders a tu gusto.
2. Click **"Guardar Actual"** y dale nombre.
3. Recupéralo instantáneamente desde el selector.
*Incluye 5 presets de fábrica profesionales.*

### Historial Inteligente 📜
Olvídate de "ese patrón genial de hace 5 minutos".
- Se guardan los últimos 100 patrones automáticamente.
- **Filtros**: ¿Buscas solo Drums? Filtra por tipo.
- **Búsqueda**: Escribe "techno" o "bd*4" para encontrarlo.
- **Acciones**: Reutilizar (▶️), Favorito (⭐), Exportar (.txt).

### Editor Inline ✏️
¿El patrón es casi perfecto pero sobra un golpe?
1. Click en **"Editar"**.
2. Modifica el texto `sound "bd*4 sn"` -> `sound "bd*4 sn cp"`.
3. Click "Guardar" y escucha el cambio.

---

## Herramientas de Producción

### Generación por Lotes (Batch) 🎲
Para cuando buscas inspiración rápida.
1. Click **"Generar Lote"**.
2. Pide 10, 20 o 50 patrones.
3. Escanea visualmente los resultados.
4. Selecciona tus favoritos y añadelos en masa a tu colección.

### Templates de Canciones 🎼
Rompe el bloqueo creativo con estructuras completas.
1. Abre el modal **Templates**.
2. Elige un género: Techno, House, Ambient, Breakbeat.
3. Click **Generar Canción**.
4. Obtén un archivo `.tidal` completo con Intro, Verse, Chorus, Outro.
5. Descárgalo e impórtalo en tu editor.

### Modo Jam Session 🎵
Convierte a TidalAI en tu compañero de banda virtual.
1. Configura duración (ej. 10 min) e intervalo (ej. 16s).
2. Selecciona qué "instrumentos" toca la IA (canales d1-d6).
3. Selecciona estilos permitidos.
4. **START** y toca encima mientras la IA te acompaña.

### 🎻 Director de Orquesta (Conductor)
Transforma loops infinitos en **canciones estructuradas**.
- **Diferencia Clave**:
    - **Jam Session**: Generación aleatoria infinita (Loop infinito).
    - **Conductor**: Generación con narrativa (Intro -> Verse -> Build -> Drop -> Outro).
- **Controla**: No solo genera notas, sino que modula la **Densidad** y **Complejidad** automáticamente según la sección de la canción.
- **Acceso**: Botón 🎻 en el Dock.

---

## Herramientas Analíticas

### Análisis de Corpus 📊
Entiende tu librería musical.
- Gráficos visuales de tus samples más usados.
- Qué efectos predominan en tu música.
- Distribución de géneros en tus favoritos.

### Comparador de Patrones 🔄
Aprende de las variaciones.
- Selecciona dos patrones (A y B).
- Ve las diferencias resaltadas en rojo/verde.
- Compara métricas de complejidad.
- Decide cuál quedarte.

### Visualizador de Patrones 📊
- Timeline gráfica de 16 pasos.
- Colores por tipo de instrumento.
- Identifica visualmente la estructura rítmica.

---

## Uso Básico

### Iniciar el Sistema
1. Asegúrate que tu Raspberry Pi está encendida.
2. Abre tu navegador en `http://192.168.1.147:5000`.
3. (Opcional) Usa `deploy.bat` para asegurar que tienes la última versión.

### Instalación en Nuevos Equipos 📦
¿Quieres usar TidalAI en otro ordenador?
1. Ve a `http://tidal.local:5000/admin`.
2. Busca la tarjeta **"Portable Client Kit"**.
3. Descarga el ZIP y ejecútalo. ¡Listo!

### Generar y Enviar
1. Elige **Tipo** (ej. Drums) y **Estilo** (ej. Techno).
2. Click **Generar**.
3. Revisa el código o el visualizador.
4. Click **Enviar a Tidal** para escuchar.

### Backup y Exportación
- **Backup Total**: Ve a Herramientas Avanzadas -> **Crear Backup**. Descarga un ZIP con todo.
- **Exportar .tidal**: Ve a Herramientas -> **Exportar Historial/Favoritos**. Obtén un archivo `.tidal` limpio y comentado.

---

## API REST

Para desarrolladores e integraciones:

```http
POST /api/generate
POST /api/generate-batch
POST /api/generate/morph
GET/POST /api/presets
GET/POST /api/history
GET /api/corpus-stats
POST /api/jam-session
GET/POST /api/backup
POST /api/export-tidal
POST /api/generate-song
GET /api/theory/rules
POST /api/theory/toggle
POST /api/theory/add
GET /api/latent/genres
POST /api/latent/blend
```

Más detalles en la documentación técnica del código.

---

## 🧠 The Intelligent Theorist (Phase 17)

El sistema ahora **valida automáticamente** los patrones generados contra reglas musicales.

### ¿Cómo funciona?
1. Cuando generas un patrón, el `TheoryEngine` lo valida contra reglas del género seleccionado.
2. Si **falla**, el sistema reintenta automáticamente hasta 3 veces con temperatura ligeramente aumentada.
3. El resultado muestra un **badge visual**:
   - ✅ **"Theoretically Verified"**: Patrón válido.
   - ⚠️ **"Theory Violation"**: Patrón no cumple las reglas (con detalles de qué falló).

### Reglas por Género
- **Techno**: Requiere bombo en el primer tiempo, pulso constante.
- **House**: Bombo en tiempos fuertes, groove estable.
- **Drum & Bass**: Ritmo complejo, alta densidad.
- **Ambient**: Densidad baja, sin bombos pesados.

### Editor de Reglas (Phase 17b) 📐

Ahora puedes **gestionar las reglas dinámicamente** desde la UI:

1. **Acceso**: Click en el icono 📐 "Reglas" en el Dock.
2. **Activar/Desactivar**: Usa los checkboxes para habilitar o deshabilitar reglas por género.
3. **Añadir Reglas Custom**: 
   - Selecciona género.
   - Define un ID único (e.g., `no_claps`).
   - Escribe una expresión regular (e.g., `cp` para prohibir claps).
   - Añade un mensaje de error.
4. **Persistencia**: Las reglas se guardan en `theory_rules.json`.

**Ejemplo de regla custom**:
```
Género: techno
ID: no_offbeat_kick
Regex: bd.*~
Mensaje: "Techno no permite bombos sincopados"
```

---

## 🌀 Latent Space Navigation (Phase 18)

Crea **híbridos musicales** mezclando géneros matemáticamente.

### ¿Cómo funciona?
Cada género es un "vector" de parámetros:
```
techno = {density: 0.8, complexity: 0.6, tempo: 140, samples: ["bd", "hh", "sn"]}
ambient = {density: 0.3, complexity: 0.4, tempo: 90, samples: ["pad", "texture"]}
```

Cuando mezclas **70% Techno + 30% Ambient**, el sistema calcula:
```
resultado = (techno * 0.7) + (ambient * 0.3)
# density = 0.65, tempo = 113, samples mezclados
```

### Uso
1. **Activa el Modo Blend**: Checkbox 🌀 en "Diseño Sonoro".
2. **Selecciona dos géneros**: Elige Género A y Género B.
3. **Ajusta el slider**: 0% = 100% A, 100% = 100% B.
4. **Genera**: El patrón usará parámetros interpolados.

### Ejemplos de Mezclas
- **70% Techno + 30% Ambient** = Bombo constante con densidad reducida y pads atmosféricos.
- **50% House + 50% Dub** = Groove bailable con delays y espacialidad.
- **80% Drum & Bass + 20% Breakbeat** = Ritmo frenético con breaks orgánicos.

### Validación en Modo Blend
Las reglas del Theorist se aplican según el **género dominante** (>50%). Si mezclas 70% Techno + 30% Ambient, las reglas de Techno son obligatorias, las de Ambient son opcionales.


---

## Control y Administración ⚙️

### 1. Panel de Admin Local (Launcher)
Tu centro de comando en Windows. Ejecuta `TidalAI-Launcher.bat` para:
- **Deploy**: Actualizar la RPi con un clic.
- **Cleanup**: Limpiar archivos basura.
- **SSH**: Configurar llaves de acceso.
- **Extract**: Alimentar a la IA con tus propios archivos `.tidal`.

### 2. TidalAI Control Center (Web)
Monitorización en tiempo real dentro de la Raspberry Pi (Accesible vía `http://<IP>:5000/admin` o el botón ⚙️ en el dock).
- **Dashboard**: Gráficos de CPU, RAM y Temperatura.
- **Live Logs**: Ve qué está pensando la IA "bajo el capó".
- **Reboot**: Reinicia el servicio remotamente si se atasca.

---

**¡Disfruta de la producción con IA! 🎵**
