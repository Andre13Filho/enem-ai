#!/usr/bin/env python3
"""
Formatador de Matemática para o Professor Carlos
Versão SIMPLIFICADA e ROBUSTA - foca no que realmente funciona
"""

import re

def format_mathematical_content(text: str) -> str:
    """
    Formata conteúdo matemático - versão simplificada
    """
    
    formatted_text = text
    
    # 1. Determinantes - PRIORIDADE MÁXIMA
    formatted_text = format_determinants_simple(formatted_text)
    
    # 2. Expoentes simples
    formatted_text = format_simple_exponents(formatted_text)
    
    # 3. Raízes
    formatted_text = format_square_roots_simple(formatted_text)
    
    # 4. Símbolos matemáticos
    formatted_text = format_math_symbols(formatted_text)
    
    return formatted_text

def format_determinants_simple(text: str) -> str:
    """Formata determinantes de forma simples e robusta"""
    
    # det(A) = algo (mais preciso - para antes de pontuação ou conectivos)
    text = re.sub(r'\bdet\(([^)]+)\)\s*=\s*([^.,\n]+?)(?=\s*[.,!?]|\s+e\s|\s*$)', r'$$\\det(\1) = \2$$', text, flags=re.IGNORECASE)
    
    return text

def format_simple_exponents(text: str) -> str:
    """Formata expoentes de forma simples"""
    
    # x² vira $x^2$
    text = re.sub(r'([a-zA-Z])²', r'$\1^2$', text)
    
    # x³ vira $x^3$
    text = re.sub(r'([a-zA-Z])³', r'$\1^3$', text)
    
    return text

def format_square_roots_simple(text: str) -> str:
    """Formata raízes de forma simples"""
    
    # √(algo) vira $\sqrt{algo}$
    text = re.sub(r'√\(([^)]+)\)', r'$\\sqrt{\1}$', text)
    
    return text

def format_math_symbols(text: str) -> str:
    """Converte símbolos matemáticos básicos"""
    
    # π vira \pi
    text = text.replace('π', '\\pi')
    
    return text

def improve_visual_structure_simple(text: str) -> str:
    """Melhora estrutura visual - versão simples"""
    
    # Destaca palavras-chave importantes
    keywords = ['determinante', 'matriz', 'fórmula']
    
    for keyword in keywords:
        text = re.sub(f'\\b({keyword})\\b', r'**\1**', text, flags=re.IGNORECASE)
    
    return text

def remove_reasoning_text(text: str) -> str:
    """Remove texto de raciocínio interno"""
    
    patterns = [
        r'Vou calcular.*?(?=\n|$)',
        r'Pensando.*?(?=\n|$)',
        r'<thinking>.*?</thinking>',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text

def remove_duplicates(text: str) -> str:
    """Remove duplicações simples"""
    
    # Divide em parágrafos
    paragraphs = text.split('\n\n')
    
    # Remove parágrafos duplicados
    unique_paragraphs = []
    seen = set()
    
    for paragraph in paragraphs:
        normalized = re.sub(r'\s+', ' ', paragraph.strip().lower())
        
        if normalized and normalized not in seen and len(normalized) > 10:
            seen.add(normalized)
            unique_paragraphs.append(paragraph)
    
    return '\n\n'.join(unique_paragraphs)

# Função principal SIMPLIFICADA
def format_professor_response(response: str) -> str:
    """
    Formatação SIMPLIFICADA da resposta do Professor Carlos
    Versão robusta que funciona de forma consistente
    """
    
    # 1. Remove texto de raciocínio
    response = remove_reasoning_text(response)
    
    # 2. Formata matemática (versão simples)
    response = format_mathematical_content(response)
    
    # 3. Melhora estrutura visual
    response = improve_visual_structure_simple(response)
    
    # 4. Remove duplicações
    response = remove_duplicates(response)
    
    return response.strip()

# Funções legadas para compatibilidade (mantidas vazias ou simples)
def format_determinant_formulas(text: str) -> str:
    return format_determinants_simple(text)

def format_quadratic_formulas(text: str) -> str:
    return text

def format_trigonometric_formulas(text: str) -> str:
    return text

def format_fractions(text: str) -> str:
    return text

def format_exponents_and_subscripts(text: str) -> str:
    return format_simple_exponents(text)

def format_matrices(text: str) -> str:
    return text

def format_square_roots(text: str) -> str:
    return format_square_roots_simple(text)

def format_summations(text: str) -> str:
    return text

def format_simple_equations(text: str) -> str:
    return text

def improve_math_readability(text: str) -> str:
    return format_mathematical_content(text)

def clean_latex_duplicates(text: str) -> str:
    return text

def improve_visual_structure(text: str) -> str:
    return improve_visual_structure_simple(text) 