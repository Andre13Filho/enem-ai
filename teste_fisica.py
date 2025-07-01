#!/usr/bin/env python3
"""
Teste do Professor Fernando - Especialista em Física
"""

import os
import streamlit as st
from professor_fernando_local import professor_fernando_local
from physics_exercises_rag import get_physics_exercise_with_solution

def setup_api_key():
    """Configura a API key da Groq para os testes"""
    # Tenta obter a API key do ambiente
    api_key = os.environ.get("GROQ_API_KEY")
    
    # Se não encontrou, solicita ao usuário
    if not api_key:
        print("GROQ_API_KEY não encontrada no ambiente.")
        api_key = input("Por favor, digite sua API key da Groq: ")
        os.environ["GROQ_API_KEY"] = api_key
        
    return bool(api_key)

def test_professor_response():
    """Testa a resposta do Professor Fernando"""
    query = "Explique o que é acústica e como funciona o eco"
    
    print("Inicializando o Professor Fernando...")
    api_key = os.environ.get("GROQ_API_KEY")
    professor_fernando_local.initialize_system(api_key)
    
    print("Consultando o Professor Fernando...\n")
    response = professor_fernando_local.get_response(query, api_key)
    
    print("Resposta do Professor Fernando:\n")
    print(response)
    print("\n" + "-"*50 + "\n")

def test_physics_exercise():
    """Testa a obtenção de exercício de física com solução"""
    print("Obtendo um exercício de física...\n")
    api_key = os.environ.get("GROQ_API_KEY")
    exercise = get_physics_exercise_with_solution(api_key=api_key)
    
    print("Questão de Física:\n")
    print(exercise["question"])
    print("\nSolução:\n")
    print(exercise["solution"])
    print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    print("="*50)
    print("TESTE DO PROFESSOR FERNANDO - FÍSICA")
    print("="*50 + "\n")
    
    # Configura a API key
    if not setup_api_key():
        print("Não foi possível configurar a API key. Encerrando testes.")
        exit(1)
    
    # Cria um objeto st.session_state falso para os testes
    if not hasattr(st, "session_state"):
        class SessionState:
            pass
        st.session_state = SessionState()
        st.session_state.rag_initialized_fernando = False
    
    # Testa a resposta do professor
    test_professor_response()
    
    # Testa o exercício com solução
    test_physics_exercise() 