(
// Configuración de memoria para evitar crasheos (AUMENTADA)
s.options.numBuffers = 1024 * 256; 
s.options.memSize = 8192 * 128; // Aumentado x4 para evitar 'alloc failed'
s.options.maxNodes = 1024 * 32;
s.options.numOutputBusChannels = 2; // Estéreo
s.options.numInputBusChannels = 2;

// Esperar a que el servidor arranque antes de cargar sonidos
s.waitForBoot {
    ~dirt = SuperDirt(2, s); 
    ~dirt.loadSoundFiles; 
    
    // Configuración opcional de latencia si es necesario
    // s.latency = 0.3; 
    
    s.sync; 
    ~dirt.start(57120, 0 ! 12); 
    
    "¡LISTO! SuperDirt cargado correctamente.".postln;
};
)

/*
 * TidalAI Companion - OSC Receiver for SuperCollider
 * Recibe patrones TidalCycles vía OSC y los ejecuta
 */

(
// Configuración
var port = 6010;  // Puerto OSC para escuchar

"=== TidalAI Companion - OSC Receiver ===".postln;
("Listening on port: " ++ port).postln;
"".postln;

// Receptor para patrones completos
OSCdef(\tidalPattern, { |msg, time, addr, recvPort|
    var channel = msg[1].asString;
    var pattern = msg[2].asString;
    // Variables declaradas al inicio (Requisito SC)
    var soundIndex, rest, soundString, samples, rawName, soundName;
    var noteVal, noteIndex, restNote, noteString, firstNote, noteList; 
    var paramSpeed, paramGain, paramPan, paramVowel;
    var segments;
    
    // ("Received pattern for " ++ channel ++ ": " ++ pattern).postln;
    
    // === PARSEO BÁSICO MEJORADO PARA MELODÍAS ===
    // Buscar explícitamente el parámetro "sound"
    soundIndex = pattern.find("sound \"");
    
    if (soundIndex.notNil) {
        // Extraer lo que hay después de 'sound "'
        rest = pattern.copyRange(soundIndex + 7, pattern.size - 1);
        soundString = rest.split($")[0]; // Tomar hasta la siguiente comilla
        samples = soundString.split($ ); // Separar por espacios (ej: "bd sn")
        
        ("-> Found sound signature: " ++ soundString).postln;

        if (samples.size > 0) {
            // Tocar el primer sample inmediatamente
            rawName = samples[0];
            
            // LIMPIEZA ROBUSTA: Eliminar modificadores de Tidal (*, /, :)
            soundName = rawName.split($*)[0].split($/)[0].split($:)[0];
            soundName = soundName.reject({ |c| c == $" });
            
            // --- PARSEO DE NOTA/ÍNDICE (NUEVO) ---
            noteVal = 0;
            noteList = [];
            noteIndex = pattern.find("note \"");
            
            if (noteIndex.isNil) { noteIndex = pattern.find("n \""); }; // Buscar 'n' como alternativa
            
            if (noteIndex.notNil) {
                 restNote = pattern.copyRange(noteIndex + 6, pattern.size - 1); // +6 por 'note "'
                 if (noteIndex == pattern.find("n \"")) { restNote = pattern.copyRange(noteIndex + 3, pattern.size - 1); }; // Ajuste para 'n "'
                 
                 noteString = restNote.split($")[0];
                 noteList = noteString.split($ ); // Crear array de notas (ej: ["0", "2", "4"])
            };
            
            // --- PARSEO DE EFECTOS (High Fidelity) ---
            paramSpeed = 1.0;
            paramGain = 0.6; // Default gain
            paramPan = 0.5;
            paramVowel = ""; 
            
            // Separar efectos por '#'
            segments = pattern.split($#);
            
            // El primer segmento es siempre el sonido/nota (ya parseado arriba como 'soundString' / 'noteString')
            // Pero analizamos los siguientes segmentos para extraer valores
            if (segments.size > 1) {
                segments[1..].do({ |seg|
                    var cleanSeg = seg.stripWhiteSpace;
                    
                    if (cleanSeg.beginsWith("speed")) {
                        var val = cleanSeg.split($ )[1]; // "speed 0.96" -> "0.96"
                        if (val.notNil) { paramSpeed = val.asFloat };
                    };
                    
                    if (cleanSeg.beginsWith("gain")) {
                        var val = cleanSeg.split($ )[1];
                        if (val.notNil) { paramGain = val.asFloat };
                    };
                    
                    if (cleanSeg.beginsWith("pan")) {
                        var val = cleanSeg.split($ )[1];
                        if (val.notNil) { paramPan = val.asFloat };
                    };

                    if (cleanSeg.beginsWith("vowel")) {
                        var val = cleanSeg.split($")[1]; // "vowel "a"" -> "a"
                        if (val.notNil) { paramVowel = val };
                    };
                });
                
                ("-> Applied Effects: speed=" ++ paramSpeed ++ " gain=" ++ paramGain).postln;
            };

            // ESTRATEGIA DE REPRODUCCIÓN (Lógica Aplanada para evitar errores de sintaxis)
            
            // Caso A: Melodía (1 sonido, muchas notas)
            if (noteList.size > 1) {
                ("-> Triggering Melody Sequence (" ++ noteList.size ++ " notes)").postln;
                {
                    var dur = 1.0 / noteList.size; 
                    noteList.do({ |nVal, i|
                        var cleanN = nVal.asInteger;
                        NetAddr("127.0.0.1", 57120).sendMsg("/dirt/play", \s, soundName, \n, cleanN, \gain, paramGain, \speed, paramSpeed, \pan, paramPan, \vowel, paramVowel);
                        dur.wait;
                    });
                }.fork;
            };

            // Caso B: Ritmo de Samples (muchos sonidos) - CON SOPORTE PARA MULTIPLICADORES (*) y EFECTOS
            if ((noteList.size <= 1) and: { samples.size > 1 }) {
                {
                     var stepDur = 1.0 / samples.size; 
                     samples.do({ |s, i|
                        // Detectar multiplicador (ej: "dr*5")
                        var parts = s.split($*);
                        var cleanSample = parts[0];
                        var repeats = 1;
                        
                        if (parts.size > 1) {
                            repeats = parts[1].asInteger;
                            if (repeats < 1) { repeats = 1 };
                        };

                        // Limpieza final del nombre
                        cleanSample = cleanSample.split($/)[0].split($:)[0].reject({ |c| c == $" });
                        
                        // Sub-bucle para repetir el sonido N veces en el espacio de 1 paso
                        if(cleanSample.size > 0, {
                            repeats.do({
                                NetAddr("127.0.0.1", 57120).sendMsg("/dirt/play", \s, cleanSample, \gain, paramGain, \speed, paramSpeed, \pan, paramPan, \vowel, paramVowel);
                                (stepDur / repeats).wait; 
                            });
                        }, {
                            stepDur.wait; 
                        });
                     });
                }.fork;
            };

            // Caso C: Disparo Único (1 sonido, 0 o 1 nota)
            if ((noteList.size <= 1) and: { samples.size <= 1 }) {
                var finalNote = 0;
                if (noteList.size > 0) { finalNote = noteList[0].asInteger };
                NetAddr("127.0.0.1", 57120).sendMsg("/dirt/play", \s, soundName, \n, finalNote, \gain, paramGain, \speed, paramSpeed, \pan, paramPan, \vowel, paramVowel);
            };
        };
    }; 
    
    addr.sendMsg('/tidal/received', channel, "OK");

}, '/tidal/pattern', recvPort: port);

OSCdef(\tidalStop, { |msg, time, addr, recvPort|
    "Stopping all sounds (Hush)".postln;
    NetAddr("127.0.0.1", 57120).sendMsg("/dirt/handshake"); // A veces sirve para reset
    NetAddr("127.0.0.1", 57120).sendMsg("/sys/stop"); // Parar audio
}, '/tidal/stop', recvPort: port);


// Receptor para ping/test
OSCdef(\tidalPing, { |msg, time, addr, recvPort|
    "Ping received!".postln;
    addr.sendMsg('/tidal/pong', "alive");
}, '/tidal/ping', recvPort: port);


"".postln;
"OSC Receivers configured:".postln;
"  /tidal/pattern - Receive full patterns".postln;
"  /tidal/param   - Receive individual parameters".postln;
"  /tidal/stop    - Stop channels".postln;
"  /tidal/ping    - Test connection".postln;
"".postln;
"Ready to receive OSC messages!".postln;
"".postln;

// Función helper para escribir patrones a archivo temporal
// (alternativa para ejecutar en Tidal)
~writeTidalPattern = { |channel, pattern|
    var file, filepath;
    filepath = "/tmp/tidalai_" ++ channel ++ ".tidal";
    file = File(filepath, "w");
    file.write(channel ++ " $ " ++ pattern);
    file.close;
    ("Pattern written to: " ++ filepath).postln;
};

)

/*
 * INSTRUCCIONES DE USO:
 *
 * 1. Iniciar SuperCollider
 * 2. Evaluar este archivo completo (Ctrl+A, Ctrl+Enter)
 * 3. Los receptores OSC estarán activos
 * 4. Iniciar TidalCycles en otra ventana
 * 5. Iniciar el servidor Flask en la Raspberry Pi
 * 6. Los patrones recibidos se mostrarán en el post window
 *
 * INTEGRACIÓN CON TIDAL:
 *
 * Para ejecutar automáticamente los patrones en Tidal, hay varias opciones:
 *
 * Opción A - Manual (MVP1):
 *   - Copiar el patrón del post window
 *   - Pegarlo en TidalCycles y evaluar
 *
 * Opción B - Archivo temporal:
 *   - Usar ~writeTidalPattern para escribir a archivo
 *   - Configurar Tidal para cargar automáticamente
 *
 * Opción C - Bridge Haskell (futuro):
 *   - Crear programa Haskell que escuche OSC
 *   - Ejecute código en el contexto de Tidal
 *   - Más complejo pero totalmente automático
 *
 * TESTING:
 *
 * Desde la Raspberry Pi, ejecutar:
 *   python raspberry-pi/generator/osc_client.py
 *
 * Deberías ver los mensajes en el post window de SuperCollider.
 */
