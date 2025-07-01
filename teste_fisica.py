#!/usr/bin/env python3
"""
Teste do Professor Fernando - Especialista em Física
"""

from professor_fernando_local import get_professor_fernando_response
from physics_exercises_rag import get_physics_exercise_with_solution

def test_professor_response():
    """Testa a resposta do Professor Fernando"""
    query = "Explique o que é acústica e como funciona o eco"
    
    print("Consultando o Professor Fernando...\n")
    response = get_professor_fernando_response(query)
    
    print("Resposta do Professor Fernando:\n")
    print(response)
    print("\n" + "-"*50 + "\n")

def test_physics_exercise():
    """Testa a obtenção de exercício de física com solução"""
    print("Obtendo um exercício de física...\n")
    exercise = get_physics_exercise_with_solution()
    
    print("Questão de Física:\n")
    print(exercise["question"])
    print("\nSolução:\n")
    print(exercise["solution"])
    print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    print("="*50)
    print("TESTE DO PROFESSOR FERNANDO - FÍSICA")
    print("="*50 + "\n")
    
    # Testa a resposta do professor
    test_professor_response()
    
    # Testa o exercício com solução
    test_physics_exercise() 