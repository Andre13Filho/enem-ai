#!/usr/bin/env python3
"""
Utilitário para correção de problemas de encoding
Garante que textos sejam tratados corretamente em UTF-8
"""

import sys
import os
from typing import Any, Union

def safe_str(obj: Any, fallback: str = "Erro de codificação") -> str:
    """
    Converte qualquer objeto para string de forma segura em UTF-8
    
    Args:
        obj: Objeto a ser convertido
        fallback: String padrão em caso de erro
    
    Returns:
        String em UTF-8 ou fallback
    """
    try:
        # Se já é string, verifica encoding
        if isinstance(obj, str):
            # Tenta encode/decode para garantir UTF-8
            return obj.encode('utf-8', errors='replace').decode('utf-8')
        
        # Se é bytes, decodifica
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')
        
        # Para outros tipos, converte para string primeiro
        else:
            str_obj = str(obj)
            return str_obj.encode('utf-8', errors='replace').decode('utf-8')
            
    except Exception:
        return fallback

def safe_api_error(exception: Exception) -> str:
    """
    Formata erro de API de forma segura
    
    Args:
        exception: Exceção capturada
    
    Returns:
        Mensagem de erro formatada em UTF-8
    """
    error_msg = safe_str(exception, "Erro desconhecido na API")
    
    # Limpa caracteres problemáticos comuns
    error_msg = error_msg.replace('\x00', '')  # Remove null bytes
    error_msg = error_msg.replace('\ufffd', '?')  # Replace replacement characters
    
    return f"Erro na API: {error_msg}"

def setup_encoding():
    """
    Configura encoding padrão do sistema
    """
    # Force UTF-8 encoding
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')
    
    # Set environment variables for consistent encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['LANG'] = 'pt_BR.UTF-8'
    os.environ['LC_ALL'] = 'pt_BR.UTF-8'

def normalize_text(text: str) -> str:
    """
    Normaliza texto para evitar problemas de encoding
    
    Args:
        text: Texto a ser normalizado
    
    Returns:
        Texto normalizado em UTF-8
    """
    if not isinstance(text, str):
        text = safe_str(text)
    
    # Remove caracteres de controle problemáticos
    normalized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Garante encoding UTF-8
    return normalized.encode('utf-8', errors='replace').decode('utf-8')

def safe_format_response(template: str, *args, **kwargs) -> str:
    """
    Formata string de forma segura
    
    Args:
        template: Template de string
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
    
    Returns:
        String formatada em UTF-8
    """
    try:
        # Normaliza todos os argumentos
        safe_args = [safe_str(arg) for arg in args]
        safe_kwargs = {k: safe_str(v) for k, v in kwargs.items()}
        
        # Formata de forma segura
        result = template.format(*safe_args, **safe_kwargs)
        return normalize_text(result)
        
    except Exception:
        return safe_str(template)

# Configura encoding na importação
setup_encoding() 