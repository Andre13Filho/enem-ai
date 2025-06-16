#!/usr/bin/env python3
"""
Formatador específico para Geografia - ENEM AI Helper
"""

import re
from typing import Dict, List

class GeographyFormatter:
    """Formatador para conteúdo de geografia"""
    
    def __init__(self):
        self.geography_terms = self._load_geography_terms()
        
    def _load_geography_terms(self) -> Dict[str, str]:
        """Carrega termos geográficos importantes"""
        return {
            # Conceitos físicos
            'latitude': '**latitude**',
            'longitude': '**longitude**',
            'equador': '**Equador**',
            'trópicos': '**trópicos**',
            'meridiano': '**meridiano**',
            'paralelo': '**paralelo**',
            
            # Clima
            'tropical': '**tropical**',
            'subtropical': '**subtropical**',
            'equatorial': '**equatorial**',
            'semiárido': '**semiárido**',
            'temperado': '**temperado**',
            
            # Relevo
            'planalto': '**planalto**',
            'planície': '**planície**',
            'depressão': '**depressão**',
            'serra': '**serra**',
            'chapada': '**chapada**',
            
            # Hidrografia
            'bacia hidrográfica': '**bacia hidrográfica**',
            'divisor de águas': '**divisor de águas**',
            'afluente': '**afluente**',
            'nascente': '**nascente**',
            'foz': '**foz**',
            
            # Urbano
            'urbanização': '**urbanização**',
            'metropolização': '**metropolização**',
            'conurbação': '**conurbação**',
            'megalópole': '**megalópole**',
            
            # Econômico
            'globalização': '**globalização**',
            'industrialização': '**industrialização**',
            'agronegócio': '**agronegócio**',
            'PIB': '**PIB**',
            'IDH': '**IDH**',
        }
    
    def format_geography_terms(self, text: str) -> str:
        """Formata termos geográficos"""
        formatted_text = text
        
        for term, formatted_term in self.geography_terms.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            formatted_text = re.sub(pattern, formatted_term, formatted_text, flags=re.IGNORECASE)
        
        return formatted_text
    
    def format_coordinates(self, text: str) -> str:
        """Formata coordenadas geográficas"""
        # Padrão para coordenadas (ex: 23°S, 45°W)
        coord_pattern = r'(\d+)°([NS]|[EW])'
        formatted_text = re.sub(coord_pattern, r'**\1°\2**', text)
        
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
            formatted_text = self.format_geography_terms(formatted_text)
            formatted_text = self.format_coordinates(formatted_text)
            return formatted_text
        except Exception as e:
            print(f"Erro na formatação de geografia: {e}")
            return text

# Instância global
geography_formatter = GeographyFormatter()

def format_geography_response(text: str) -> str:
    """Função principal para formatar respostas de geografia"""
    return geography_formatter.format_professor_response(text) 