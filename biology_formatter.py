#!/usr/bin/env python3
"""
Formatador específico para Biologia - A.T.E.N.A.
"""

import re
from typing import Dict, List

class BiologyFormatter:
    """Formatador para conteúdo de biologia"""
    
    def __init__(self):
        self.biology_terms = self._load_biology_terms()
        
    def _load_biology_terms(self) -> Dict[str, str]:
        """Carrega termos biológicos importantes"""
        return {
            # Genética
            'DNA': '**DNA**',
            'RNA': '**RNA**',
            'mRNA': '**mRNA**',
            'tRNA': '**tRNA**',
            'rRNA': '**rRNA**',
            'ATP': '**ATP**',
            'ADP': '**ADP**',
            'NADH': '**NADH**',
            'FADH2': '**FADH₂**',
            'CO2': 'CO₂',
            'O2': 'O₂',
            'H2O': 'H₂O',
            'C6H12O6': 'C₆H₁₂O₆',
            
            # Processos
            'fotossíntese': '**fotossíntese**',
            'respiração celular': '**respiração celular**',
            'mitose': '**mitose**',
            'meiose': '**meiose**',
            'transcrição': '**transcrição**',
            'tradução': '**tradução**',
            'replicação': '**replicação**',
        }
    
    def format_biology_terms(self, text: str) -> str:
        """Formata termos biológicos"""
        formatted_text = text
        
        for term, formatted_term in self.biology_terms.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            formatted_text = re.sub(pattern, formatted_term, formatted_text, flags=re.IGNORECASE)
        
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
            formatted_text = self.format_biology_terms(formatted_text)
            return formatted_text
        except Exception as e:
            print(f"Erro na formatação de biologia: {e}")
            return text

# Instância global
biology_formatter = BiologyFormatter()

def format_biology_response(text: str) -> str:
    """Função principal para formatar respostas de biologia"""
    return biology_formatter.format_professor_response(text) 