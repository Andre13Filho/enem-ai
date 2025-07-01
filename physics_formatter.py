#!/usr/bin/env python3
"""
Formatador de Física para o Professor Fernando
Versão SIMPLIFICADA e ROBUSTA - foca no que realmente funciona
"""

import re

def format_physics_content(text: str) -> str:
    """
    Formata conteúdo físico - versão simplificada
    """
    
    formatted_text = text
    
    # 1. Fórmulas físicas - PRIORIDADE MÁXIMA
    formatted_text = format_physics_formulas_simple(formatted_text)
    
    # 2. Expoentes simples
    formatted_text = format_simple_exponents(formatted_text)
    
    # 3. Unidades físicas
    formatted_text = format_physics_units(formatted_text)
    
    # 4. Símbolos físicos
    formatted_text = format_physics_symbols(formatted_text)
    
    return formatted_text

def format_physics_formulas_simple(text: str) -> str:
    """Formata fórmulas físicas de forma simples e robusta"""
    
    # F = ma (força)
    text = re.sub(r'\bF\s*=\s*m\s*a\b', r'$$F = ma$$', text)
    
    # E = mc² (energia)
    text = re.sub(r'\bE\s*=\s*mc²\b', r'$$E = mc^2$$', text)
    
    # v = λf (velocidade da onda)
    text = re.sub(r'\bv\s*=\s*λ\s*f\b', r'$$v = \lambda f$$', text)
    
    return text

def format_simple_exponents(text: str) -> str:
    """Formata expoentes de forma simples"""
    
    # x² vira $x^2$
    text = re.sub(r'([a-zA-Z])²', r'$\1^2$', text)
    
    # x³ vira $x^3$
    text = re.sub(r'([a-zA-Z])³', r'$\1^3$', text)
    
    return text

def format_physics_units(text: str) -> str:
    """Formata unidades físicas"""
    
    # m/s vira $m/s$
    text = re.sub(r'\b(\d+(?:\.\d+)?)\s*(m/s|km/h|N|J|W|Hz|Pa|V|Ω)\b', r'$\1 \2$', text)
    
    return text

def format_physics_symbols(text: str) -> str:
    """Converte símbolos físicos básicos"""
    
    # λ vira \lambda
    text = text.replace('λ', '\\lambda')
    
    # Δ vira \Delta
    text = text.replace('Δ', '\\Delta')
    
    # ω vira \omega
    text = text.replace('ω', '\\omega')
    
    return text

def improve_visual_structure_simple(text: str) -> str:
    """Melhora estrutura visual - versão simples"""
    
    # Destaca palavras-chave importantes
    keywords = ['força', 'energia', 'velocidade', 'aceleração', 'frequência', 'resistência']
    
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
    Formatação SIMPLIFICADA da resposta do Professor Fernando
    Versão robusta que funciona de forma consistente
    """
    
    # 1. Remove texto de raciocínio
    response = remove_reasoning_text(response)
    
    # 2. Formata física (versão simples)
    response = format_physics_content(response)
    
    # 3. Melhora estrutura visual
    response = improve_visual_structure_simple(response)
    
    # 4. Remove duplicações
    response = remove_duplicates(response)
    
    return response.strip()

# Funções legadas para compatibilidade (mantidas vazias ou simples)
def format_mechanics_formulas(text: str) -> str:
    return text

def format_thermodynamics_formulas(text: str) -> str:
    return text

def format_electromagnetism_formulas(text: str) -> str:
    return text

def format_optics_formulas(text: str) -> str:
    return text

def format_modern_physics_formulas(text: str) -> str:
    return text

def format_wave_formulas(text: str) -> str:
    return text

def improve_physics_readability(text: str) -> str:
    return format_physics_content(text) 