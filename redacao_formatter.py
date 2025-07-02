# Arquivo: redacao_formatter.py
import re

def remove_reasoning_tags(text: str) -> str:
    """
    Remove as tags <think> e seu conteúdo, que representam o raciocínio interno da IA.
    """
    # Usa re.DOTALL para que o '.' também corresponda a quebras de linha
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()

def format_redacao_response(text: str) -> str:
    """
    Função principal para limpar e formatar a resposta da análise de redação.
    """
    # Remove o raciocínio da IA
    formatted_text = remove_reasoning_tags(text)
    
    # Remove quebras de linha em excesso que podem ter sido deixadas para trás
    formatted_text = re.sub(r'\n\s*\n', '\n\n', formatted_text)
    
    return formatted_text.strip()