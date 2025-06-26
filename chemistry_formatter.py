#!/usr/bin/env python3
"""
Formatador específico para Química - A.T.E.N.A.
Formata fórmulas químicas, equações e conceitos para melhor visualização
"""

import re
from typing import Dict, List, Tuple

class ChemistryFormatter:
    """Formatador para conteúdo de química"""
    
    def __init__(self):
        self.chemical_formulas = self._load_chemical_formulas()
        self.chemical_equations = self._load_chemical_equations()
        self.chemistry_units = self._load_chemistry_units()
        
    def _load_chemical_formulas(self) -> Dict[str, str]:
        """Carrega fórmulas químicas comuns"""
        return {
            # Compostos inorgânicos básicos
            'H2O': r'H₂O',
            'CO2': r'CO₂',
            'O2': r'O₂',
            'H2': r'H₂',
            'N2': r'N₂',
            'NH3': r'NH₃',
            'HCl': r'HCl',
            'H2SO4': r'H₂SO₄',
            'HNO3': r'HNO₃',
            'NaOH': r'NaOH',
            'Ca(OH)2': r'Ca(OH)₂',
            'NaCl': r'NaCl',
            'CaCO3': r'CaCO₃',
            'Na2CO3': r'Na₂CO₃',
            'K2SO4': r'K₂SO₄',
            'Al2O3': r'Al₂O₃',
            'Fe2O3': r'Fe₂O₃',
            'CuSO4': r'CuSO₄',
            'AgNO3': r'AgNO₃',
            'BaCl2': r'BaCl₂',
            'MgO': r'MgO',
            'CaO': r'CaO',
            'SO2': r'SO₂',
            'SO3': r'SO₃',
            'NO': r'NO',
            'NO2': r'NO₂',
            'N2O': r'N₂O',
            'P2O5': r'P₂O₅',
            'SiO2': r'SiO₂',
            
            # Compostos orgânicos básicos
            'CH4': r'CH₄',
            'C2H6': r'C₂H₆',
            'C2H4': r'C₂H₄',
            'C2H2': r'C₂H₂',
            'C3H8': r'C₃H₈',
            'C4H10': r'C₄H₁₀',
            'C6H6': r'C₆H₆',
            'C2H5OH': r'C₂H₅OH',
            'CH3OH': r'CH₃OH',
            'CH3COOH': r'CH₃COOH',
            'C6H12O6': r'C₆H₁₂O₆',
            'C12H22O11': r'C₁₂H₂₂O₁₁',
            
            # Íons comuns
            'H+': r'H⁺',
            'OH-': r'OH⁻',
            'Na+': r'Na⁺',
            'K+': r'K⁺',
            'Ca2+': r'Ca²⁺',
            'Mg2+': r'Mg²⁺',
            'Al3+': r'Al³⁺',
            'Fe2+': r'Fe²⁺',
            'Fe3+': r'Fe³⁺',
            'Cu2+': r'Cu²⁺',
            'Zn2+': r'Zn²⁺',
            'Ag+': r'Ag⁺',
            'Cl-': r'Cl⁻',
            'Br-': r'Br⁻',
            'I-': r'I⁻',
            'F-': r'F⁻',
            'SO42-': r'SO₄²⁻',
            'NO3-': r'NO₃⁻',
            'CO32-': r'CO₃²⁻',
            'PO43-': r'PO₄³⁻',
            'NH4+': r'NH₄⁺',
        }
    
    def _load_chemical_equations(self) -> Dict[str, str]:
        """Carrega equações químicas importantes"""
        return {
            # Reações de combustão
            'combustao_metano': r'CH₄ + 2O₂ → CO₂ + 2H₂O',
            'combustao_etanol': r'C₂H₅OH + 3O₂ → 2CO₂ + 3H₂O',
            
            # Reações ácido-base
            'neutralizacao': r'HCl + NaOH → NaCl + H₂O',
            'acido_carbonato': r'2HCl + CaCO₃ → CaCl₂ + H₂O + CO₂',
            
            # Reações de síntese
            'sintese_amonia': r'N₂ + 3H₂ ⇌ 2NH₃',
            'sintese_agua': r'2H₂ + O₂ → 2H₂O',
            
            # Reações de decomposição
            'decomposicao_agua': r'2H₂O → 2H₂ + O₂',
            'decomposicao_carbonato': r'CaCO₃ → CaO + CO₂',
            
            # Reações de oxirredução
            'oxidacao_ferro': r'4Fe + 3O₂ → 2Fe₂O₃',
            'reducao_oxido': r'Fe₂O₃ + 3CO → 2Fe + 3CO₂',
        }
    
    def _load_chemistry_units(self) -> Dict[str, str]:
        """Carrega unidades químicas"""
        return {
            'mol/L': r'mol·L⁻¹',
            'g/mol': r'g·mol⁻¹',
            'J/mol': r'J·mol⁻¹',
            'kJ/mol': r'kJ·mol⁻¹',
            'cal/mol': r'cal·mol⁻¹',
            'L/mol': r'L·mol⁻¹',
            'atm': r'atm',
            'mmHg': r'mmHg',
            'Pa': r'Pa',
            'kPa': r'kPa',
            'bar': r'bar',
            'torr': r'Torr',
            'M': r'M',
            'N': r'N',
            'm': r'm',
            'molal': r'molal',
            'ppm': r'ppm',
            'ppb': r'ppb',
            '%m/m': r'%m/m',
            '%v/v': r'%v/v',
            '%m/v': r'%m/v',
        }
    
    def format_chemical_formulas(self, text: str) -> str:
        """Formata fórmulas químicas no texto"""
        formatted_text = text
        
        # Ordena por comprimento decrescente para evitar substituições parciais
        sorted_formulas = sorted(self.chemical_formulas.items(), key=lambda x: len(x[0]), reverse=True)
        
        for formula, formatted_formula in sorted_formulas:
            # Usa word boundaries para evitar substituições parciais
            pattern = r'\b' + re.escape(formula) + r'\b'
            formatted_text = re.sub(pattern, formatted_formula, formatted_text)
        
        return formatted_text
    
    def format_chemical_equations(self, text: str) -> str:
        """Formata equações químicas no texto"""
        formatted_text = text
        
        # Padrões para detectar equações químicas
        equation_patterns = [
            # Padrão básico: A + B → C + D
            r'([A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)\s*\+\s*([A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)\s*→\s*([A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)\s*\+\s*([A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)',
            # Padrão com coeficientes: 2A + 3B → C + 4D
            r'(\d*[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)\s*\+\s*(\d*[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)\s*→\s*(\d*[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)\s*\+\s*(\d*[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)',
        ]
        
        for pattern in equation_patterns:
            matches = re.finditer(pattern, formatted_text)
            for match in matches:
                original = match.group(0)
                # Aplica formatação de fórmulas na equação
                formatted_equation = self.format_chemical_formulas(original)
                formatted_text = formatted_text.replace(original, formatted_equation)
        
        return formatted_text
    
    def format_chemistry_units(self, text: str) -> str:
        """Formata unidades químicas"""
        formatted_text = text
        
        for unit, formatted_unit in self.chemistry_units.items():
            # Usa word boundaries para unidades
            pattern = r'\b' + re.escape(unit) + r'\b'
            formatted_text = re.sub(pattern, formatted_unit, formatted_text)
        
        return formatted_text
    
    def format_chemical_concepts(self, text: str) -> str:
        """Formata conceitos químicos importantes"""
        formatted_text = text
        
        # Conceitos importantes em negrito
        important_concepts = [
            'pH', 'pOH', 'pKa', 'pKb', 'Kw', 'Ka', 'Kb', 'Kc', 'Kp', 'Kps',
            'entalpia', 'entropia', 'energia livre de Gibbs',
            'oxidação', 'redução', 'oxirredução',
            'ácido', 'base', 'sal', 'óxido',
            'cátion', 'ânion', 'eletrólito',
            'molaridade', 'molalidade', 'normalidade',
            'solução', 'soluto', 'solvente',
            'equilíbrio químico', 'constante de equilíbrio',
            'velocidade de reação', 'catalisador',
            'ligação iônica', 'ligação covalente', 'ligação metálica',
            'hibridização', 'geometria molecular',
            'isomeria', 'polímero', 'monômero'
        ]
        
        for concept in important_concepts:
            pattern = r'\b' + re.escape(concept) + r'\b'
            formatted_text = re.sub(pattern, f'**{concept}**', formatted_text, flags=re.IGNORECASE)
        
        return formatted_text
    
    def format_subscripts_superscripts(self, text: str) -> str:
        """Formata subscritos e sobrescritos químicos"""
        formatted_text = text
        
        # Subscritos (números após elementos)
        subscript_map = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', 
                        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}
        
        # Sobrescritos (cargas iônicas)
        superscript_map = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                          '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
                          '+': '⁺', '-': '⁻'}
        
        # Padrão para subscritos em fórmulas químicas
        subscript_pattern = r'([A-Z][a-z]?)(\d+)'
        def replace_subscript(match):
            element = match.group(1)
            number = match.group(2)
            subscript_number = ''.join(subscript_map.get(digit, digit) for digit in number)
            return f'{element}{subscript_number}'
        
        formatted_text = re.sub(subscript_pattern, replace_subscript, formatted_text)
        
        # Padrão para sobrescritos em íons
        superscript_pattern = r'([A-Z][a-z]?\d*)(\d*[+-])'
        def replace_superscript(match):
            base = match.group(1)
            charge = match.group(2)
            superscript_charge = ''.join(superscript_map.get(char, char) for char in charge)
            return f'{base}{superscript_charge}'
        
        formatted_text = re.sub(superscript_pattern, replace_superscript, formatted_text)
        
        return formatted_text
    
    def remove_reasoning_patterns(self, text: str) -> str:
        """Remove padrões de raciocínio interno"""
        reasoning_patterns = [
            r'Vou calcular.*?\.',
            r'Primeiro.*?vamos.*?\.',
            r'Agora.*?vou.*?\.',
            r'Pensando.*?\.',
            r'Analisando.*?\.',
            r'Vamos.*?resolver.*?\.',
            r'Para.*?resolver.*?\.',
            r'Começando.*?\.',
            r'Iniciando.*?\.',
            r'Vou.*?explicar.*?\.',
            r'Preciso.*?calcular.*?\.',
            r'Devo.*?considerar.*?\.',
        ]
        
        cleaned_text = text
        for pattern in reasoning_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove linhas vazias extras
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def format_professor_response(self, text: str) -> str:
        """Aplica todas as formatações para resposta do professor"""
        try:
            # Remove padrões de raciocínio interno
            formatted_text = self.remove_reasoning_patterns(text)
            
            # Aplica formatações químicas
            formatted_text = self.format_chemical_formulas(formatted_text)
            formatted_text = self.format_chemical_equations(formatted_text)
            formatted_text = self.format_chemistry_units(formatted_text)
            formatted_text = self.format_chemical_concepts(formatted_text)
            formatted_text = self.format_subscripts_superscripts(formatted_text)
            
            # Garante que fórmulas estejam em LaTeX quando necessário
            formatted_text = self._ensure_latex_formatting(formatted_text)
            
            return formatted_text
            
        except Exception as e:
            print(f"Erro na formatação de química: {e}")
            return text
    
    def _ensure_latex_formatting(self, text: str) -> str:
        """Garante formatação LaTeX para fórmulas complexas"""
        # Padrões que devem estar em LaTeX
        latex_patterns = [
            (r'([A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*\s*[+\-→⇌]\s*[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\)\d*)*)', r'$\1$'),
            (r'(K[acbpws]?\s*=\s*[\d.,]+)', r'$\1$'),
            (r'(pH\s*=\s*[\d.,]+)', r'$\1$'),
            (r'(\[.*?\]\s*=\s*[\d.,]+)', r'$\1$'),
        ]
        
        formatted_text = text
        for pattern, replacement in latex_patterns:
            formatted_text = re.sub(pattern, replacement, formatted_text)
        
        return formatted_text

# Instância global do formatador
chemistry_formatter = ChemistryFormatter()

def format_chemistry_response(text: str) -> str:
    """Função principal para formatar respostas de química"""
    return chemistry_formatter.format_professor_response(text) 