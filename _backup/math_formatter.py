#!/usr/bin/env python3
"""
Formatador de Matemática para o Professor Carlos
Melhora a exibição de fórmulas matemáticas usando LaTeX/MathJax
"""

import re

def format_mathematical_content(text: str) -> str:
    """
    Formata conteúdo matemático para melhor visualização
    Converte notações matemáticas para LaTeX quando possível
    """
    
    # Se o texto já contém LaTeX, retorna como está
    if '$$' in text or '\\(' in text:
        return text
    
    # Aplica formatações matemáticas
    formatted_text = text
    
    # 1. Fórmulas de determinante
    formatted_text = format_determinant_formulas(formatted_text)
    
    # 2. Fórmulas de função quadrática
    formatted_text = format_quadratic_formulas(formatted_text)
    
    # 3. Fórmulas trigonométricas
    formatted_text = format_trigonometric_formulas(formatted_text)
    
    # 4. Frações simples
    formatted_text = format_fractions(formatted_text)
    
    # 5. Expoentes e índices
    formatted_text = format_exponents_and_subscripts(formatted_text)
    
    # 6. Matrizes
    formatted_text = format_matrices(formatted_text)
    
    # 7. Raízes quadradas
    formatted_text = format_square_roots(formatted_text)
    
    # 8. Somatórios e produtórios
    formatted_text = format_summations(formatted_text)
    
    return formatted_text

def format_determinant_formulas(text: str) -> str:
    """Formata fórmulas de determinante"""
    
    # Fórmula geral do determinante
    patterns = [
        # \det(A) = \sum_{j=1}^{n} a_{ij} \cdot C_{ij}
        (r'\\det\(([^)]+)\)\s*=\s*\\sum_\{j=1\}\^\{n\}\s*a_\{ij\}\s*\\cdot\s*C_\{ij\}',
         r'$$\\det(\1) = \\sum_{j=1}^{n} a_{ij} \\cdot C_{ij}$$'),
        
        # det(A) = ... (versão sem barra)
        (r'det\(([^)]+)\)\s*=\s*(.+?)(?=\n|$)',
         r'$$\\det(\1) = \2$$'),
        
        # Cofator patterns
        (r'cofator\s*\(([^)]+)\)',
         r'C_{\1}'),
        
        # (-1)^{i+j}
        (r'\(-1\)\^(\{?[^}]+\}?)',
         r'(-1)^{\1}'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_quadratic_formulas(text: str) -> str:
    """Formata fórmulas de função quadrática"""
    
    patterns = [
        # f(x) = ax² + bx + c
        (r'f\(x\)\s*=\s*([a-z]?)x²?\s*\+\s*([a-z]?)x\s*\+\s*([a-z]?)',
         r'$$f(x) = \1x^2 + \2x + \3$$'),
        
        # y = ax² + bx + c  
        (r'y\s*=\s*([a-z]?)x²?\s*\+\s*([a-z]?)x\s*\+\s*([a-z]?)',
         r'$$y = \1x^2 + \2x + \3$$'),
        
        # Fórmula de Bhaskara
        (r'x\s*=\s*\(-b\s*±\s*√\(b²\s*-\s*4ac\)\)\s*/\s*2a',
         r'$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$'),
        
        # Delta
        (r'Δ\s*=\s*b²\s*-\s*4ac',
         r'$$\\Delta = b^2 - 4ac$$'),
         
        (r'delta\s*=\s*b²\s*-\s*4ac',
         r'$$\\Delta = b^2 - 4ac$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_trigonometric_formulas(text: str) -> str:
    """Formata fórmulas trigonométricas"""
    
    patterns = [
        # sen²(x) + cos²(x) = 1
        (r'sen²\(([^)]+)\)\s*\+\s*cos²\(([^)]+)\)\s*=\s*1',
         r'$$\\sin^2(\1) + \\cos^2(\2) = 1$$'),
        
        # sen(x), cos(x), tan(x)
        (r'sen\(([^)]+)\)',
         r'\\sin(\1)'),
        (r'cos\(([^)]+)\)',
         r'\\cos(\1)'),
        (r'tan\(([^)]+)\)',
         r'\\tan(\1)'),
        (r'tg\(([^)]+)\)',
         r'\\tan(\1)'),
        
        # Lei dos senos
        (r'a/sen\(A\)\s*=\s*b/sen\(B\)\s*=\s*c/sen\(C\)',
         r'$$\\frac{a}{\\sin(A)} = \\frac{b}{\\sin(B)} = \\frac{c}{\\sin(C)}$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_fractions(text: str) -> str:
    """Formata frações simples"""
    
    # Frações no formato a/b
    pattern = r'(\d+|\([^)]+\))/(\d+|\([^)]+\))'
    
    def replace_fraction(match):
        numerator = match.group(1)
        denominator = match.group(2)
        return f'\\frac{{{numerator}}}{{{denominator}}}'
    
    # Aplica apenas se não estiver já em LaTeX
    if '\\frac' not in text:
        text = re.sub(pattern, replace_fraction, text)
    
    return text

def format_exponents_and_subscripts(text: str) -> str:
    """Formata expoentes e índices"""
    
    patterns = [
        # x²
        (r'([a-zA-Z])²', r'\1^2'),
        # x³
        (r'([a-zA-Z])³', r'\1^3'),
        # x^n (se não estiver em LaTeX)
        (r'([a-zA-Z])\^([0-9]+)', r'\1^{\2}'),
        # a_ij
        (r'([a-zA-Z])_([a-zA-Z0-9]+)', r'\1_{\2}'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    
    return text

def format_matrices(text: str) -> str:
    """Formata matrizes"""
    
    # Detecta padrões como \begin{pmatrix} ... \end{pmatrix}
    if '\\begin{pmatrix}' in text:
        # Já está formatado, apenas melhora a apresentação
        text = text.replace('\\begin{pmatrix}', '\n$$\\begin{pmatrix}')
        text = text.replace('\\end{pmatrix}', '\\end{pmatrix}$$\n')
    
    return text

def format_square_roots(text: str) -> str:
    """Formata raízes quadradas"""
    
    patterns = [
        # √(expressão)
        (r'√\(([^)]+)\)', r'\\sqrt{\1}'),
        # sqrt(expressão)
        (r'sqrt\(([^)]+)\)', r'\\sqrt{\1}'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_summations(text: str) -> str:
    """Formata somatórios e produtórios"""
    
    patterns = [
        # Σ (soma de 1 a n)
        (r'Σ\s*\(([^)]+)\)', r'\\sum \1'),
        (r'∑\s*\(([^)]+)\)', r'\\sum \1'),
        
        # Π (produto)
        (r'Π\s*\(([^)]+)\)', r'\\prod \1'),
        (r'∏\s*\(([^)]+)\)', r'\\prod \1'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    
    return text

def improve_math_readability(text: str) -> str:
    """
    Melhora a legibilidade geral de conteúdo matemático
    """
    
    # Aplica formatação matemática
    formatted = format_mathematical_content(text)
    
    # Melhora estrutura visual
    formatted = improve_visual_structure(formatted)
    
    return formatted

def improve_visual_structure(text: str) -> str:
    """Melhora a estrutura visual do texto matemático"""
    
    # Adiciona quebras de linha antes de passos importantes
    text = re.sub(r'(Passo \d+:|Exemplo:|Resolução:|Calculando:)', r'\n**\1**\n', text)
    
    # Destaca palavras-chave matemáticas
    keywords = [
        'determinante', 'matriz', 'cofator', 'função quadrática', 
        'vértice', 'discriminante', 'raízes', 'trigonometria',
        'seno', 'cosseno', 'tangente', 'teorema', 'fórmula'
    ]
    
    for keyword in keywords:
        text = re.sub(f'({keyword})', r'**\1**', text, flags=re.IGNORECASE)
    
    return text

# Função principal para uso no Professor Carlos
def format_professor_response(response: str) -> str:
    """
    Função principal para formatar respostas do Professor Carlos
    com matemática melhorada
    """
    return improve_math_readability(response) 