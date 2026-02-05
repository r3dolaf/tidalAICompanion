from theory_engine import TheoryEngine

def test_metrics():
    te = TheoryEngine()
    
    patterns = {
        "Simple 4/4": 'sound "bd*4"',
        "Syncopated Euclidean": 'sound "bd(5,8)"',
        "Complex Glitch": 'sound "[bd ~ sn [cp cp]] hh*8" # speed 1.2',
        "Ambient Texture": 'sound "pad" # room 0.8 # gain 0.5'
    }
    
    print("=== TheoryEngine v2: Metrics Verification ===\n")
    
    for name, code in patterns.items():
        sync = te.analyze_syncopation(code)
        variety = te.analyze_variety(code)
        insight = te.get_musical_insight(code, "techno")
        
        print(f"Patrón: {name}")
        print(f"Código: {code}")
        print(f"Síncopa: {sync:.2f}")
        print(f"Variedad: {variety:.2f}")
        print(f"Insight: {insight}\n")
        print("-" * 30)

if __name__ == "__main__":
    test_metrics()
