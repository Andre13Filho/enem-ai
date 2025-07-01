#!/usr/bin/env python3
"""
Sistema de RAG para Exercícios de Física do ENEM
Baseado no modelo de outros sistemas de exercícios do projeto
"""

import os
import json
from openai import OpenAI
from local_physics_rag import get_physics_knowledge

# Inicializa o cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Caminhos para os arquivos de questões e gabaritos
QUESTIONS_PRIMEIRO_DIA = "questions_primeiro_dia.json"
QUESTIONS_SEGUNDO_DIA = "questions_segundo_enem.json"
GABARITOS_PRIMEIRO_DIA = "gabaritos_primeiro_dia.json"
GABARITOS_SEGUNDO_DIA = "gabaritos_segundo_dia.json"

def load_json_file(file_path):
    """Carrega um arquivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar arquivo {file_path}: {e}")
        return {}

def get_physics_questions(year=None, num_questions=5):
    """
    Obtém questões de física do ENEM
    
    Args:
        year: Ano específico para filtrar questões (opcional)
        num_questions: Número de questões a retornar
        
    Returns:
        Lista de questões de física
    """
    # Carrega as questões do segundo dia (onde estão as questões de física)
    questions = load_json_file(QUESTIONS_SEGUNDO_DIA)
    
    # Filtra apenas questões de física
    physics_questions = []
    
    for question_id, question_data in questions.items():
        if "física" in question_data.get("area", "").lower():
            # Filtra por ano se especificado
            if year and str(year) != question_data.get("ano", ""):
                continue
                
            physics_questions.append({
                "id": question_id,
                "question": question_data.get("enunciado", ""),
                "options": question_data.get("alternativas", {}),
                "year": question_data.get("ano", ""),
                "area": question_data.get("area", "")
            })
            
            # Limita o número de questões
            if len(physics_questions) >= num_questions:
                break
    
    return physics_questions

def get_physics_question_solution(question_id, question_text):
    """
    Obtém a solução para uma questão de física
    
    Args:
        question_id: ID da questão
        question_text: Texto da questão
        
    Returns:
        Explicação da solução
    """
    # Carrega os gabaritos
    gabaritos = load_json_file(GABARITOS_SEGUNDO_DIA)
    
    # Obtém a resposta correta
    correct_answer = None
    if question_id in gabaritos:
        correct_answer = gabaritos[question_id].get("gabarito", "")
    
    # Obtém conhecimento relevante de física
    physics_context = get_physics_knowledge(question_text)
    
    # Constrói o prompt para o modelo
    system_prompt = """
    Você é o Professor Fernando, especialista em Física para o ENEM.
    Sua tarefa é explicar detalhadamente a solução de uma questão de física do ENEM.
    
    Forneça uma explicação completa, incluindo:
    1. Identificação dos conceitos físicos envolvidos
    2. Explicação teórica relevante
    3. Resolução passo a passo
    4. Justificativa para a alternativa correta
    5. Por que as outras alternativas estão incorretas
    
    Use fórmulas e notação matemática quando necessário (LaTeX).
    """
    
    user_prompt = f"""
    Questão de Física do ENEM:
    {question_text}
    
    Alternativa correta: {correct_answer if correct_answer else "Não disponível"}
    
    Conhecimento relevante:
    {physics_context}
    
    Explique detalhadamente como resolver esta questão.
    """
    
    try:
        # Chama a API do OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        # Retorna a explicação
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Erro ao obter solução: {e}")
        return "Não foi possível gerar a solução para esta questão no momento."

# Função principal para uso em outros módulos
def get_physics_exercise_with_solution(year=None):
    """
    Obtém um exercício de física com solução
    
    Args:
        year: Ano específico para filtrar questões (opcional)
        
    Returns:
        Dicionário com questão e solução
    """
    # Obtém uma questão de física
    questions = get_physics_questions(year=year, num_questions=1)
    
    if not questions:
        return {
            "question": "Não foi possível encontrar questões de física.",
            "solution": "",
            "year": "",
            "id": ""
        }
    
    question = questions[0]
    
    # Formata o texto completo da questão
    question_text = f"{question['question']}\n\n"
    for option_key, option_text in question['options'].items():
        question_text += f"{option_key}) {option_text}\n"
    
    # Obtém a solução
    solution = get_physics_question_solution(question['id'], question_text)
    
    return {
        "question": question_text,
        "solution": solution,
        "year": question['year'],
        "id": question['id']
    }

# Para teste direto
if __name__ == "__main__":
    exercise = get_physics_exercise_with_solution()
    print("Questão de Física:\n")
    print(exercise["question"])
    print("\nSolução:\n")
    print(exercise["solution"]) 