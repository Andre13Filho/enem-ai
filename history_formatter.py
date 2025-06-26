#!/usr/bin/env python3
"""
Formatador específico para História - A.T.E.N.A.
"""

import re
from typing import Dict, List

class HistoryFormatter:
    """Formatador para conteúdo de história"""
    
    def __init__(self):
        self.historical_terms = self._load_historical_terms()
        
    def _load_historical_terms(self) -> Dict[str, str]:
        """Carrega termos históricos importantes"""
        return {
            # Períodos históricos
            'Idade Média': '**Idade Média**',
            'Renascimento': '**Renascimento**',
            'Iluminismo': '**Iluminismo**',
            'Revolução Industrial': '**Revolução Industrial**',
            'Primeira Guerra Mundial': '**Primeira Guerra Mundial**',
            'Segunda Guerra Mundial': '**Segunda Guerra Mundial**',
            'Guerra Fria': '**Guerra Fria**',
            
            # Brasil
            'Brasil Colônia': '**Brasil Colônia**',
            'Brasil Império': '**Brasil Império**',
            'República Velha': '**República Velha**',
            'Era Vargas': '**Era Vargas**',
            'Ditadura Militar': '**Ditadura Militar**',
            'Nova República': '**Nova República**',
            
            # Conceitos
            'absolutismo': '**absolutismo**',
            'liberalismo': '**liberalismo**',
            'socialismo': '**socialismo**',
            'capitalismo': '**capitalismo**',
            'imperialismo': '**imperialismo**',
            'colonialismo': '**colonialismo**',
        }
    
    def format_historical_terms(self, text: str) -> str:
        """Formata termos históricos"""
        formatted_text = text
        
        for term, formatted_term in self.historical_terms.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            formatted_text = re.sub(pattern, formatted_term, formatted_text, flags=re.IGNORECASE)
        
        return formatted_text
    
    def format_dates(self, text: str) -> str:
        """Formata datas históricas"""
        # Padrão para anos (1500-2023)
        date_pattern = r'\b(1[5-9]\d{2}|20[0-2]\d)\b'
        formatted_text = re.sub(date_pattern, r'**\1**', text)
        
        # Padrão para séculos (século XV, XVI, etc.)
        century_pattern = r'\b(século\s+[IVX]+)\b'
        formatted_text = re.sub(century_pattern, r'**\1**', formatted_text, flags=re.IGNORECASE)
        
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
            formatted_text = self.format_historical_terms(formatted_text)
            formatted_text = self.format_dates(formatted_text)
            return formatted_text
        except Exception as e:
            print(f"Erro na formatação de história: {e}")
            return text

# Instância global
history_formatter = HistoryFormatter()

def format_history_response(text: str) -> str:
    """Função principal para formatar respostas de história"""
    return history_formatter.format_professor_response(text) 