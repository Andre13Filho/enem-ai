#!/usr/bin/env python3
"""
Professor Fernando - Especialista em Física
Baseado no modelo de outros professores do projeto
"""

import os
from openai import OpenAI
from physics_formatter import format_professor_response
from local_physics_rag import get_physics_knowledge

# Inicializa o cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Prompt do sistema para o Professor Fernando
SYSTEM_PROMPT = """
Você é o Professor Fernando, um especialista em Física com mais de 20 anos de experiência ensinando alunos do ensino médio.

Seu objetivo é explicar conceitos de Física de forma clara, precisa e didática, adequada para estudantes que estão se preparando para o ENEM.

Características importantes:
- Use linguagem acessível, mas precisa cientificamente
- Explique os conceitos físicos com exemplos do cotidiano
- Utilize fórmulas e notação matemática quando necessário (use LaTeX)
- Destaque os conceitos-chave que são frequentemente cobrados no ENEM
- Evite explicações excessivamente técnicas ou que fujam do escopo do ensino médio

Ao responder questões:
1. Identifique os conceitos físicos envolvidos
2. Explique a teoria relevante de forma concisa
3. Demonstre a aplicação das fórmulas quando necessário
4. Resolva o problema passo a passo
5. Conclua com a resposta final destacada

Lembre-se que você está preparando alunos para o ENEM, então foque nos tópicos mais relevantes para a prova.
"""

def get_professor_fernando_response(query, model="gpt-4o", temperature=0.2):
    """
    Obtém resposta do Professor Fernando para uma consulta
    
    Args:
        query: A consulta do usuário
        model: O modelo de linguagem a ser usado
        temperature: Temperatura para geração de texto
        
    Returns:
        A resposta formatada do Professor Fernando
    """
    try:
        # Obtém o conhecimento relevante de física
        physics_context = get_physics_knowledge(query)
        
        # Constrói o prompt completo
        prompt = f"""
        Consulta do aluno: {query}
        
        Conhecimento relevante de Física:
        {physics_context}
        
        Responda à consulta do aluno como o Professor Fernando, usando o conhecimento fornecido.
        """
        
        # Chama a API do OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        # Extrai e formata a resposta
        raw_response = response.choices[0].message.content
        formatted_response = format_professor_response(raw_response)
        
        return formatted_response
    
    except Exception as e:
        print(f"Erro ao obter resposta do Professor Fernando: {e}")
        return "Desculpe, não consegui processar sua consulta no momento. Por favor, tente novamente mais tarde."

# Função para uso direto em testes
if __name__ == "__main__":
    query = input("Digite sua pergunta sobre Física: ")
    response = get_professor_fernando_response(query)
    print("\nResposta do Professor Fernando:\n")
    print(response) 