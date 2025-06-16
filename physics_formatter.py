#!/usr/bin/env python3
"""
Formatador de Física para o Professor Fernando
Melhora a exibição de fórmulas físicas usando LaTeX/MathJax
"""

import re

def format_physics_content(text: str) -> str:
    """
    Formata conteúdo físico para melhor visualização
    Converte notações físicas para LaTeX quando possível
    """
    
    formatted_text = text
    
    # Aplica formatações físicas
    # 1. Fórmulas de cinemática
    formatted_text = format_kinematics_formulas(formatted_text)
    
    # 2. Fórmulas de dinâmica
    formatted_text = format_dynamics_formulas(formatted_text)
    
    # 3. Fórmulas de energia
    formatted_text = format_energy_formulas(formatted_text)
    
    # 4. Fórmulas de eletromagnetismo
    formatted_text = format_electromagnetic_formulas(formatted_text)
    
    # 5. Fórmulas de termodinâmica
    formatted_text = format_thermodynamics_formulas(formatted_text)
    
    # 6. Fórmulas de óptica
    formatted_text = format_optics_formulas(formatted_text)
    
    # 7. Fórmulas de ondas
    formatted_text = format_waves_formulas(formatted_text)
    
    # 8. Unidades físicas
    formatted_text = format_physics_units(formatted_text)
    
    # 9. Frações e expoentes
    formatted_text = format_fractions_and_exponents(formatted_text)
    
    return formatted_text

def format_kinematics_formulas(text: str) -> str:
    """Formata fórmulas de cinemática"""
    
    patterns = [
        # v = Δs/Δt
        (r'v\s*=\s*Δs\s*/\s*Δt', r'$$v = \\frac{\\Delta s}{\\Delta t}$$'),
        (r'v\s*=\s*\\Delta s\s*/\s*\\Delta t', r'$$v = \\frac{\\Delta s}{\\Delta t}$$'),
        
        # v = v₀ + at
        (r'v\s*=\s*v₀\s*\+\s*at', r'$$v = v_0 + at$$'),
        (r'v\s*=\s*v0\s*\+\s*at', r'$$v = v_0 + at$$'),
        
        # s = s₀ + v₀t + (1/2)at²
        (r's\s*=\s*s₀\s*\+\s*v₀t\s*\+\s*\(1/2\)at²', r'$$s = s_0 + v_0 t + \\frac{1}{2}at^2$$'),
        (r's\s*=\s*s0\s*\+\s*v0t\s*\+\s*\(1/2\)at²', r'$$s = s_0 + v_0 t + \\frac{1}{2}at^2$$'),
        
        # v² = v₀² + 2aΔs
        (r'v²\s*=\s*v₀²\s*\+\s*2aΔs', r'$$v^2 = v_0^2 + 2a\\Delta s$$'),
        (r'v²\s*=\s*v0²\s*\+\s*2aΔs', r'$$v^2 = v_0^2 + 2a\\Delta s$$'),
        
        # Movimento circular: v = ωr
        (r'v\s*=\s*ωr', r'$$v = \\omega r$$'),
        (r'v\s*=\s*\\omega r', r'$$v = \\omega r$$'),
        
        # Aceleração centrípeta: ac = v²/r
        (r'ac\s*=\s*v²\s*/\s*r', r'$$a_c = \\frac{v^2}{r}$$'),
        (r'a_c\s*=\s*v²\s*/\s*r', r'$$a_c = \\frac{v^2}{r}$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_dynamics_formulas(text: str) -> str:
    """Formata fórmulas de dinâmica"""
    
    patterns = [
        # F = ma (Segunda Lei de Newton)
        (r'F\s*=\s*ma(?!\w)', r'$$F = ma$$'),
        
        # F = μN (Força de atrito)
        (r'F\s*=\s*μN', r'$$F = \\mu N$$'),
        (r'Fat\s*=\s*μN', r'$$F_{at} = \\mu N$$'),
        
        # P = mg (Peso)
        (r'P\s*=\s*mg(?!\w)', r'$$P = mg$$'),
        
        # Lei da Gravitação Universal: F = G(m₁m₂)/r²
        (r'F\s*=\s*G\s*\(m₁m₂\)\s*/\s*r²', r'$$F = G\\frac{m_1 m_2}{r^2}$$'),
        (r'F\s*=\s*G\s*m1\s*m2\s*/\s*r²', r'$$F = G\\frac{m_1 m_2}{r^2}$$'),
        
        # Impulso: J = FΔt
        (r'J\s*=\s*FΔt', r'$$J = F\\Delta t$$'),
        (r'I\s*=\s*FΔt', r'$$I = F\\Delta t$$'),
        
        # Quantidade de movimento: Q = mv
        (r'Q\s*=\s*mv(?!\w)', r'$$Q = mv$$'),
        (r'p\s*=\s*mv(?!\w)', r'$$p = mv$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_energy_formulas(text: str) -> str:
    """Formata fórmulas de energia"""
    
    patterns = [
        # Energia cinética: Ec = (1/2)mv²
        (r'Ec\s*=\s*\(1/2\)mv²', r'$$E_c = \\frac{1}{2}mv^2$$'),
        (r'E_c\s*=\s*\(1/2\)mv²', r'$$E_c = \\frac{1}{2}mv^2$$'),
        (r'Ec\s*=\s*mv²/2', r'$$E_c = \\frac{mv^2}{2}$$'),
        
        # Energia potencial gravitacional: Epg = mgh
        (r'Epg\s*=\s*mgh', r'$$E_{pg} = mgh$$'),
        (r'E_pg\s*=\s*mgh', r'$$E_{pg} = mgh$$'),
        
        # Energia potencial elástica: Epe = (1/2)kx²
        (r'Epe\s*=\s*\(1/2\)kx²', r'$$E_{pe} = \\frac{1}{2}kx^2$$'),
        (r'E_pe\s*=\s*\(1/2\)kx²', r'$$E_{pe} = \\frac{1}{2}kx^2$$'),
        
        # Trabalho: W = F·d·cos(θ)
        (r'W\s*=\s*F\s*\*\s*d\s*\*\s*cos\(θ\)', r'$$W = F \\cdot d \\cdot \\cos(\\theta)$$'),
        (r'W\s*=\s*Fd\s*cos\(θ\)', r'$$W = F \\cdot d \\cdot \\cos(\\theta)$$'),
        
        # Potência: P = W/t
        (r'P\s*=\s*W\s*/\s*t(?!\w)', r'$$P = \\frac{W}{t}$$'),
        
        # Potência: P = Fv
        (r'P\s*=\s*Fv(?!\w)', r'$$P = F \\cdot v$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_electromagnetic_formulas(text: str) -> str:
    """Formata fórmulas de eletromagnetismo"""
    
    patterns = [
        # Lei de Coulomb: F = k(q₁q₂)/r²
        (r'F\s*=\s*k\s*\(q₁q₂\)\s*/\s*r²', r'$$F = k\\frac{q_1 q_2}{r^2}$$'),
        (r'F\s*=\s*k\s*q1\s*q2\s*/\s*r²', r'$$F = k\\frac{q_1 q_2}{r^2}$$'),
        
        # Campo elétrico: E = F/q
        (r'E\s*=\s*F\s*/\s*q(?!\w)', r'$$E = \\frac{F}{q}$$'),
        
        # Potencial elétrico: V = k·q/r
        (r'V\s*=\s*k\s*\*\s*q\s*/\s*r', r'$$V = k\\frac{q}{r}$$'),
        (r'V\s*=\s*kq\s*/\s*r', r'$$V = k\\frac{q}{r}$$'),
        
        # Lei de Ohm: V = R·I
        (r'V\s*=\s*R\s*\*\s*I(?!\w)', r'$$V = R \\cdot I$$'),
        (r'V\s*=\s*RI(?!\w)', r'$$V = R \\cdot I$$'),
        
        # Potência elétrica: P = V·I
        (r'P\s*=\s*V\s*\*\s*I(?!\w)', r'$$P = V \\cdot I$$'),
        (r'P\s*=\s*VI(?!\w)', r'$$P = V \\cdot I$$'),
        
        # Potência elétrica: P = V²/R
        (r'P\s*=\s*V²\s*/\s*R(?!\w)', r'$$P = \\frac{V^2}{R}$$'),
        
        # Energia elétrica: E = P·t
        (r'E\s*=\s*P\s*\*\s*t(?!\w)', r'$$E = P \\cdot t$$'),
        (r'E\s*=\s*Pt(?!\w)', r'$$E = P \\cdot t$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_thermodynamics_formulas(text: str) -> str:
    """Formata fórmulas de termodinâmica"""
    
    patterns = [
        # Dilatação linear: ΔL = L₀·α·ΔT
        (r'ΔL\s*=\s*L₀\s*\*\s*α\s*\*\s*ΔT', r'$$\\Delta L = L_0 \\cdot \\alpha \\cdot \\Delta T$$'),
        (r'ΔL\s*=\s*L0\s*α\s*ΔT', r'$$\\Delta L = L_0 \\cdot \\alpha \\cdot \\Delta T$$'),
        
        # Calor sensível: Q = m·c·ΔT
        (r'Q\s*=\s*m\s*\*\s*c\s*\*\s*ΔT', r'$$Q = m \\cdot c \\cdot \\Delta T$$'),
        (r'Q\s*=\s*mcΔT', r'$$Q = m \\cdot c \\cdot \\Delta T$$'),
        
        # Calor latente: Q = m·L
        (r'Q\s*=\s*m\s*\*\s*L(?!\w)', r'$$Q = m \\cdot L$$'),
        (r'Q\s*=\s*mL(?!\w)', r'$$Q = m \\cdot L$$'),
        
        # Lei dos gases ideais: PV = nRT
        (r'PV\s*=\s*nRT', r'$$PV = nRT$$'),
        (r'P\s*\*\s*V\s*=\s*n\s*\*\s*R\s*\*\s*T', r'$$PV = nRT$$'),
        
        # Primeira lei da termodinâmica: ΔU = Q - W
        (r'ΔU\s*=\s*Q\s*-\s*W(?!\w)', r'$$\\Delta U = Q - W$$'),
        
        # Rendimento: η = W/Q
        (r'η\s*=\s*W\s*/\s*Q(?!\w)', r'$$\\eta = \\frac{W}{Q}$$'),
        (r'rendimento\s*=\s*W\s*/\s*Q', r'$$\\eta = \\frac{W}{Q}$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_optics_formulas(text: str) -> str:
    """Formata fórmulas de óptica"""
    
    patterns = [
        # Equação de Gauss: 1/f = 1/p + 1/p'
        (r'1/f\s*=\s*1/p\s*\+\s*1/p\'', r'$$\\frac{1}{f} = \\frac{1}{p} + \\frac{1}{p\'}$$'),
        
        # Lei de Snell: n₁·sen(θ₁) = n₂·sen(θ₂)
        (r'n₁\s*\*\s*sen\(θ₁\)\s*=\s*n₂\s*\*\s*sen\(θ₂\)', r'$$n_1 \\cdot \\sin(\\theta_1) = n_2 \\cdot \\sin(\\theta_2)$$'),
        (r'n1\s*sen\(θ1\)\s*=\s*n2\s*sen\(θ2\)', r'$$n_1 \\cdot \\sin(\\theta_1) = n_2 \\cdot \\sin(\\theta_2)$$'),
        
        # Aumento linear: A = p'/p
        (r'A\s*=\s*p\'\s*/\s*p(?!\w)', r'$$A = \\frac{p\'}{p}$$'),
        
        # Velocidade da luz: c = λ·f
        (r'c\s*=\s*λ\s*\*\s*f(?!\w)', r'$$c = \\lambda \\cdot f$$'),
        (r'c\s*=\s*λf(?!\w)', r'$$c = \\lambda \\cdot f$$'),
        
        # Índice de refração: n = c/v
        (r'n\s*=\s*c\s*/\s*v(?!\w)', r'$$n = \\frac{c}{v}$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_waves_formulas(text: str) -> str:
    """Formata fórmulas de ondas"""
    
    patterns = [
        # Velocidade da onda: v = λ·f
        (r'v\s*=\s*λ\s*\*\s*f(?!\w)', r'$$v = \\lambda \\cdot f$$'),
        (r'v\s*=\s*λf(?!\w)', r'$$v = \\lambda \\cdot f$$'),
        
        # Período e frequência: T = 1/f
        (r'T\s*=\s*1\s*/\s*f(?!\w)', r'$$T = \\frac{1}{f}$$'),
        
        # Velocidade do som: v = 331 + 0,6T
        (r'v\s*=\s*331\s*\+\s*0,6T', r'$$v = 331 + 0{,}6T$$'),
        
        # Efeito Doppler: f' = f(v ± vo)/(v ± vf)
        (r'f\'\s*=\s*f\s*\(v\s*±\s*vo\)\s*/\s*\(v\s*±\s*vf\)', r'$$f\' = f\\frac{v \\pm v_o}{v \\pm v_f}$$'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def format_physics_units(text: str) -> str:
    """Formata unidades físicas"""
    
    patterns = [
        # Unidades básicas
        (r'(\d+)\s*m/s', r'\1\\,\\text{m/s}'),
        (r'(\d+)\s*m/s²', r'\1\\,\\text{m/s}^2'),
        (r'(\d+)\s*kg', r'\1\\,\\text{kg}'),
        (r'(\d+)\s*N', r'\1\\,\\text{N}'),
        (r'(\d+)\s*J', r'\1\\,\\text{J}'),
        (r'(\d+)\s*W', r'\1\\,\\text{W}'),
        (r'(\d+)\s*V', r'\1\\,\\text{V}'),
        (r'(\d+)\s*A', r'\1\\,\\text{A}'),
        (r'(\d+)\s*Ω', r'\1\\,\\Omega'),
        (r'(\d+)\s*°C', r'\1\\,°\\text{C}'),
        (r'(\d+)\s*K', r'\1\\,\\text{K}'),
        (r'(\d+)\s*Hz', r'\1\\,\\text{Hz}'),
        (r'(\d+)\s*m', r'\1\\,\\text{m}'),
        (r'(\d+)\s*s', r'\1\\,\\text{s}'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    
    return text

def format_fractions_and_exponents(text: str) -> str:
    """Formata frações e expoentes"""
    
    # Frações no formato a/b (se não estiver em LaTeX)
    if '\\frac' not in text:
        pattern = r'(\d+|\([^)]+\))/(\d+|\([^)]+\))'
        def replace_fraction(match):
            numerator = match.group(1)
            denominator = match.group(2)
            return f'\\frac{{{numerator}}}{{{denominator}}}'
        text = re.sub(pattern, replace_fraction, text)
    
    # Expoentes
    patterns = [
        (r'([a-zA-Z])²', r'\1^2'),
        (r'([a-zA-Z])³', r'\1^3'),
        (r'([a-zA-Z])\^([0-9]+)', r'\1^{\2}'),
        (r'([a-zA-Z])_([a-zA-Z0-9]+)', r'\1_{\2}'),
    ]
    
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    
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

def improve_physics_readability(text: str) -> str:
    """
    Melhora a legibilidade geral de conteúdo físico
    """
    
    # Aplica formatação física
    formatted = format_physics_content(text)
    
    # Melhora estrutura visual
    formatted = improve_visual_structure(formatted)
    
    return formatted

def improve_visual_structure(text: str) -> str:
    """Melhora a estrutura visual do texto físico"""
    
    # Adiciona quebras de linha antes de passos importantes
    text = re.sub(r'(Passo \d+:|Exemplo:|Resolução:|Calculando:|Aplicando:)', r'\n**\1**\n', text)
    
    # Destaca palavras-chave físicas
    keywords = [
        'velocidade', 'aceleração', 'força', 'energia', 'trabalho', 'potência',
        'campo elétrico', 'campo magnético', 'corrente', 'tensão', 'resistência',
        'temperatura', 'calor', 'pressão', 'volume', 'densidade',
        'frequência', 'período', 'amplitude', 'comprimento de onda',
        'reflexão', 'refração', 'difração', 'interferência'
    ]
    
    for keyword in keywords:
        text = re.sub(f'({keyword})', r'**\1**', text, flags=re.IGNORECASE)
    
    return text

def fix_latex_formatting(text: str) -> str:
    """
    Corrige problemas específicos de formatação LaTeX
    """
    
    # Remove colchetes em torno de fórmulas e converte para LaTeX
    # Exemplo: [ D = \frac{n(n - 3)}{2} ] -> $$D = \frac{n(n - 3)}{2}$$
    text = re.sub(r'\[\s*([^]]+)\s*\]', r'$$\1$$', text)
    
    # Corrige parênteses em fórmulas inline
    # Exemplo: ( n ) -> $n$
    text = re.sub(r'\(\s*([a-zA-Z])\s*\)', r'$\1$', text)
    
    # Corrige símbolos especiais
    text = text.replace('( n )', '$n$')
    text = text.replace('( S )', '$S$')
    text = text.replace('( D )', '$D$')
    text = text.replace('( Ã )', '$\\alpha$')
    
    # Converte graus adequadamente
    text = text.replace('180°', '180^\\circ')
    text = text.replace('360°', '360^\\circ')
    text = text.replace('90°', '90^\\circ')
    text = text.replace('108°', '108^\\circ')
    
    # Corrige multiplicação
    text = text.replace(' x ', ' \\times ')
    text = text.replace(' × ', ' \\times ')
    
    return text

def remove_reasoning_text(text: str) -> str:
    """
    Remove texto de raciocínio/pensamento que não deveria aparecer
    """
    
    # Padrões comuns de raciocínio interno
    reasoning_patterns = [
        r'Vou calcular.*?(?=\n|$)',
        r'Primeiro.*?vamos.*?(?=\n|$)',
        r'Pensando.*?(?=\n|$)',
        r'Let me.*?(?=\n|$)',
        r'I need to.*?(?=\n|$)',
        r'Hmm.*?(?=\n|$)',
        r'Actually.*?(?=\n|$)',
        r'Wait.*?(?=\n|$)',
        r'<thinking>.*?</thinking>',
        r'Raciocínio:.*?(?=\n\n|\n[A-Z]|$)',
        r'Processo mental:.*?(?=\n\n|\n[A-Z]|$)',
    ]
    
    for pattern in reasoning_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text

def remove_duplicates(text: str) -> str:
    """
    Remove duplicações de conteúdo
    """
    
    # Divide em parágrafos
    paragraphs = text.split('\n\n')
    
    # Remove parágrafos duplicados
    unique_paragraphs = []
    seen = set()
    
    for paragraph in paragraphs:
        # Normaliza o parágrafo para comparação
        normalized = re.sub(r'\s+', ' ', paragraph.strip().lower())
        
        if normalized and normalized not in seen and len(normalized) > 10:
            seen.add(normalized)
            unique_paragraphs.append(paragraph)
    
    return '\n\n'.join(unique_paragraphs)

# Função principal para uso no Professor Carlos
def format_professor_response(response: str) -> str:
    """
    Função principal para formatar respostas do Professor Carlos
    Aplica todas as melhorias de formatação matemática
    """
    
    # 1. Remove duplicações
    formatted = remove_duplicates(response)
    
    # 2. Remove texto de raciocínio
    formatted = remove_reasoning_text(formatted)
    
    # 3. Corrige formatação LaTeX específica
    formatted = fix_latex_formatting(formatted)
    
    # 4. Aplica formatação física geral
    formatted = format_physics_content(formatted)
    
    # 5. Melhora legibilidade
    formatted = improve_physics_readability(formatted)
    
    # 6. Melhora estrutura visual
    formatted = improve_visual_structure(formatted)
    
    return formatted.strip() 