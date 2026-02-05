
"""
Structure Engine (The Conductor)
Gestiona la progresión de la canción a través de secciones definidas (Intro, Verse, Build, Drop, Outro).
"""
import time

class Conductor:
    def __init__(self):
        self.is_active = False
        self.start_time = 0
        self.templates = {
            "standard": [
                {"name": "INTRO", "duration": 32, "density": 0.2, "complexity": 0.2},
                {"name": "VERSE", "duration": 64, "density": 0.5, "complexity": 0.4},
                {"name": "BUILD", "duration": 16, "density": 0.8, "complexity": 0.7},
                {"name": "DROP", "duration": 32, "density": 0.9, "complexity": 0.9},
                {"name": "OUTRO", "duration": 32, "density": 0.3, "complexity": 0.2}
            ],
            "extended": [
                {"name": "INTRO", "duration": 64, "density": 0.2, "complexity": 0.2},
                {"name": "BUILD_1", "duration": 32, "density": 0.4, "complexity": 0.3},
                {"name": "VERSE", "duration": 64, "density": 0.6, "complexity": 0.5},
                {"name": "BREAK", "duration": 16, "density": 0.1, "complexity": 0.1},
                {"name": "BUILD_2", "duration": 32, "density": 0.8, "complexity": 0.8},
                {"name": "DROP", "duration": 64, "density": 1.0, "complexity": 0.9},
                {"name": "OUTRO", "duration": 64, "density": 0.3, "complexity": 0.2}
            ],
            "quick_drop": [
                {"name": "INTRO", "duration": 8, "density": 0.2, "complexity": 0.2},
                {"name": "BUILD", "duration": 8, "density": 0.8, "complexity": 0.6},
                {"name": "DROP", "duration": 32, "density": 0.95, "complexity": 0.9},
                {"name": "OUTRO", "duration": 16, "density": 0.4, "complexity": 0.2}
            ],
            "ambient_flow": [
                {"name": "DRIFT", "duration": 64, "density": 0.3, "complexity": 0.2},
                {"name": "SWELL", "duration": 64, "density": 0.5, "complexity": 0.4},
                {"name": "PEAK", "duration": 64, "density": 0.6, "complexity": 0.6},
                {"name": "FADE", "duration": 64, "density": 0.2, "complexity": 0.1}
            ]
        }
        self.current_template_name = "standard"
        self.sections = self.templates["standard"]
        self.current_section_index = 0
        self.current_bar = 0
        self.bpm = 140

    def start(self, bpm=140, template_name="standard", custom_structure=None):
        self.is_active = True
        self.start_time = time.time()
        self.current_section_index = 0
        self.current_bar = 0
        self.bpm = bpm
        
        if custom_structure:
            self.current_template_name = "custom"
            self.sections = custom_structure
        elif template_name in self.templates:
            self.current_template_name = template_name
            self.sections = self.templates[template_name]
        
        print(f"🎻 Conductor Started: {self.sections[0]['name']} (Template: {self.current_template_name})")

    def stop(self):
        self.is_active = False
        print("🎻 Conductor Stopped")

    def update(self):
        if not self.is_active:
            return None

        # Calcular compás actual basado en el tiempo
        elapsed = time.time() - self.start_time
        seconds_per_beat = 60 / self.bpm
        seconds_per_bar = seconds_per_beat * 4
        self.current_bar = int(elapsed / seconds_per_bar)

        # Determinar sección actual
        bars_accumulated = 0
        target_section = None
        
        for i, section in enumerate(self.sections):
            if self.current_bar < (bars_accumulated + section["duration"]):
                target_section = section
                self.current_section_index = i
                break
            bars_accumulated += section["duration"]

        if not target_section:
            # Fin de la canción
            self.stop()
            return {"status": "finished"}

        # Calcular progreso dentro de la sección (0.0 - 1.0)
        section_start_bar = bars_accumulated
        section_progress = (self.current_bar - section_start_bar) / target_section["duration"]

        # SEÑALIZACIÓN DE TRANSICIÓN (Last bar detection)
        is_transition_imminent = (self.current_bar == (bars_accumulated + target_section["duration"] - 1))

        return {
            "status": "playing",
            "section": target_section["name"],
            "bar": self.current_bar,
            "section_progress": section_progress,
            "target_density": target_section["density"],
            "target_complexity": target_section["complexity"],
            "transition_imminent": is_transition_imminent,
            "next_section": self.sections[self.current_section_index + 1]["name"] if self.current_section_index + 1 < len(self.sections) else "FIN"
        }
