-- Script para listar todos los samples instalados en SuperDirt
-- Ejecutar en SuperCollider para ver qué samples tienes disponibles

(
// Configuración de memoria para evitar crasheos
s.options.numBuffers = 1024 * 256;
s.options.memSize = 8192 * 32;
s.options.maxNodes = 1024 * 32;
s.options.numOutputBusChannels = 2; // Estéreo
s.options.numInputBusChannels = 2;

// Esperar a que el servidor arranque antes de cargar sonidos
s.waitForBoot {
    ~dirt = SuperDirt(2, s);
    ~dirt.loadSoundFiles;
    s.sync;
    ~dirt.start(57120, 0 ! 12);

    "¡LISTO! SuperDirt cargado correctamente.".postln;
    "".postln;
    "=== LISTA DE SAMPLES CARGADOS ===".postln;
    
    // Fix: Acceder al diccionario 'buffers' dentro de la librería
    if (~dirt.soundLibrary.respondsTo(\buffers)) {
        ~dirt.soundLibrary.buffers.keys.asArray.sort.do({ |s| s.postln });
    } {
        "No se pudo acceder a buffers directamente.".postln;
    };
    
    "=================================".postln;
    
    "".postln;
    "=== LISTA DE SINTETIZADORES (Synths) ===".postln;
    // Listar SynthDefs globales que empiezan por "super" (típico de SuperDirt) o todos
    SynthDescLib.global.synthDescs.keys.asArray.sort.do({ |s| 
        if (s.asString.contains("super") || s.asString.contains("dirt")) {
            s.postln 
        };
    });
    "=================================".postln;
};
)