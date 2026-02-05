#!/bin/bash
# Script simplificado para probar el modelo Markov

echo "==================================="
echo "TidalAI - Prueba de Modelo Markov"
echo "==================================="
echo ""

cd ~/tidalai-companion/raspberry-pi/generator

echo "[1/2] Probando modelo Markov..."
echo ""
python3 markov_model.py

echo ""
echo "[2/2] Generando patrones con diferentes temperaturas..."
echo ""
python3 << 'EOF'
from pattern_generator import PatternGenerator

print("=== Generador con IA (Markov) ===\n")
generator = PatternGenerator(use_ai=True)

print("1. Temperatura BAJA (conservador, T=0.5):")
for i in range(3):
    pattern = generator.generate(use_ai=True, temperature=0.5)
    print(f"   d{i+1} $ {pattern}")
print()

print("2. Temperatura MEDIA (balanceado, T=1.0):")
for i in range(3):
    pattern = generator.generate(use_ai=True, temperature=1.0)
    print(f"   d{i+1} $ {pattern}")
print()

print("3. Temperatura ALTA (creativo, T=1.5):")
for i in range(3):
    pattern = generator.generate(use_ai=True, temperature=1.5)
    print(f"   d{i+1} $ {pattern}")
print()

print("=== Prueba completada ===")
print("\nCopia cualquiera de estos patrones a TidalCycles y evalúa con Ctrl+Enter")
EOF

echo ""
echo "Modelo Markov listo!"
echo ""
