#!/usr/bin/env python3
"""
Formatador específico para Língua Portuguesa - A.T.E.N.A.
"""

import re
from typing import Dict, List

class PortugueseFormatter:
    """Formatador para conteúdo de português"""
    
    def __init__(self):
        self.portuguese_terms = self._load_portuguese_terms()
        
    def _load_portuguese_terms(self) -> Dict[str, str]:
        """Carrega termos de português importantes"""
        return {
            # Gramática
            'sujeito': '**sujeito**',
            'predicado': '**predicado**',
            'objeto direto': '**objeto direto**',
            'objeto indireto': '**objeto indireto**',
            'adjunto adverbial': '**adjunto adverbial**',
            'aposto': '**aposto**',
            'vocativo': '**vocativo**',
            
            # Classes de palavras
            'substantivo': '**substantivo**',
            'adjetivo': '**adjetivo**',
            'verbo': '**verbo**',
            'advérbio': '**advérbio**',
            'preposição': '**preposição**',
            'conjunção': '**conjunção**',
            'pronome': '**pronome**',
            'artigo': '**artigo**',
            'numeral': '**numeral**',
            'interjeição': '**interjeição**',
            
            # Literatura
            'Barroco': '**Barroco**',
            'Arcadismo': '**Arcadismo**',
            'Romantismo': '**Romantismo**',
            'Realismo': '**Realismo**',
            'Naturalismo': '**Naturalismo**',
            'Parnasianismo': '**Parnasianismo**',
            'Simbolismo': '**Simbolismo**',
            'Modernismo': '**Modernismo**',
            
            # Figuras de linguagem
            'metáfora': '**metáfora**',
            'metonímia': '**metonímia**',
            'hipérbole': '**hipérbole**',
            'ironia': '**ironia**',
            'antítese': '**antítese**',
            'paradoxo': '**paradoxo**',
            'eufemismo': '**eufemismo**',
            'prosopopeia': '**prosopopeia**',
            'aliteração': '**aliteração**',
            'assonância': '**assonância**',
        }
    
    def format_portuguese_terms(self, text: str) -> str:
        """Formata termos de português"""
        formatted_text = text
        
        for term, formatted_term in self.portuguese_terms.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            formatted_text = re.sub(pattern, formatted_term, formatted_text, flags=re.IGNORECASE)
        
        return formatted_text
    
    def format_literary_quotes(self, text: str) -> str:
        """Formata citações literárias"""
        # Padrão para citações entre aspas
        quote_pattern = r'"([^"]+)"'
        formatted_text = re.sub(quote_pattern, r'*"\1"*', text)
        
        return formatted_text
    
    def remove_reasoning_patterns(self, text: str) -> str:
        """Remove padrões de raciocínio interno"""
        reasoning_patterns = [
            r'Vou explicar.*?\.',
            r'Primeiro.*?vamos.*?\.',
            r'Agora.*?vou.*?\.',
            r'Pensando.*?\.',
            r'Analisando.*?\.',
            r'Vamos.*?entender.*?\.',
            r'Para.*?entender.*?\.',
            r'Começando.*?\.',
            r'Iniciando.*?\.',
        ]
        
        cleaned_text = text
        for pattern in reasoning_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
        
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
        return cleaned_text.strip()
    
    def format_professor_response(self, text: str) -> str:
        """Aplica todas as formatações para resposta do professor"""
        try:
            formatted_text = self.remove_reasoning_patterns(text)
            formatted_text = self.format_portuguese_terms(formatted_text)
            formatted_text = self.format_literary_quotes(formatted_text)
            return formatted_text
        except Exception as e:
            print(f"Erro na formatação de português: {e}")
            return text

# Instância global
portuguese_formatter = PortugueseFormatter()

def format_portuguese_response(text: str) -> str:
    """Função principal para formatar respostas de português"""
    return portuguese_formatter.format_professor_response(text) 