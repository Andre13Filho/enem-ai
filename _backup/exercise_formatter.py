#!/usr/bin/env python3
"""
Funções de formatação de exercícios
Separado do app.py para evitar conflitos de importação
"""

import re
import streamlit as st
from typing import Dict, List


def display_exercise_card(exercise: dict, unique_id: str, exercise_num: int, collapsed: bool = False):
    """Exibe um exercício em formato de card bem organizado"""
    
    # Informações do exercício
    year = exercise.get('year', 'N/A')
    question_num = exercise.get('question_number', 'N/A')
    subject_area = exercise.get('subject_area', 'N/A')
    topic = exercise.get('topic', 'N/A')
    content = exercise.get('content', '')
    
    # Header do exercício com informações principais
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #09278d;
        margin: 1rem 0;
    ">
        <h4 style="margin: 0; color: #09278d;">
            📝 Exercício {exercise_num} - ENEM {year} (Questão {question_num})
        </h4>
        <p style="margin: 0.5rem 0 0 0; color: #64748b;">
            <strong>Área:</strong> {subject_area} | <strong>Tópico:</strong> {topic}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controles do exercício
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        show_preview = st.button(
            "👁️ Preview", 
            key=f"preview_{unique_id}",
            help="Ver resumo do exercício"
        )
    
    with col2:
        show_full = st.button(
            "📖 Completo", 
            key=f"full_{unique_id}",
            help="Ver exercício completo"
        )
    
    with col3:
        difficulty = get_exercise_difficulty(content)
        st.markdown(f"**Dificuldade:** {difficulty}")
    
    # Exibição do conteúdo baseado no botão clicado
    if show_preview:
        st.markdown("#### 👁️ Preview do Exercício")
        preview_content = clean_exercise_content(content[:400])
        if len(content) > 400:
            preview_content += "\n\n... *[clique em 'Completo' para ver o resto]*"
        
        st.markdown(f"""
        <div style="
            background-color: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
        ">
            {format_exercise_content(preview_content)}
        </div>
        """, unsafe_allow_html=True)
    
    if show_full:
        st.markdown("#### 📖 Exercício Completo")
        formatted_content = clean_exercise_content(content)
        
        st.markdown(f"""
        <div style="
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.7;
        ">
            {format_exercise_content(formatted_content)}
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de ação para exercício completo
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button(f"💬 Discutir", key=f"discuss_{unique_id}"):
                st.session_state[f"discuss_exercise_{unique_id}"] = True
        
        with col_b:
            if st.button(f"🔗 Conceitos", key=f"concepts_{unique_id}"):
                st.session_state[f"concepts_exercise_{unique_id}"] = True
        
        with col_c:
            if st.button(f"📚 Dicas", key=f"tips_{unique_id}"):
                st.session_state[f"tips_exercise_{unique_id}"] = True
        
        # Seções adicionais baseadas nos botões
        if st.session_state.get(f"discuss_exercise_{unique_id}", False):
            st.markdown("💬 **Para discutir este exercício:**")
            st.info("Vá para a aba 'Chat' e pergunte: 'Professor, pode me ajudar com este exercício do ENEM " + 
                   f"{year}, questão {question_num}? Estou com dúvida em...'")
        
        if st.session_state.get(f"concepts_exercise_{unique_id}", False):
            st.markdown("🔗 **Conceitos relacionados:**")
            concepts = extract_key_concepts(content, topic)
            for concept in concepts:
                st.markdown(f"• {concept}")
        
        if st.session_state.get(f"tips_exercise_{unique_id}", False):
            st.markdown("📚 **Dicas de resolução:**")
            tips = get_exercise_tips(topic, content)
            for tip in tips:
                st.markdown(f"💡 {tip}")


def clean_exercise_content(content: str) -> str:
    """Limpa e formata o conteúdo do exercício"""
    
    # Remove caracteres especiais desnecessários
    content = content.replace("\\n", "\n")
    content = content.replace("\\t", " ")
    
    # Remove múltiplas quebras de linha
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content.strip()


def detect_and_fix_corrupted_alternatives(content: str) -> str:
    """Detecta e corrige alternativas corrompidas com números e símbolos"""
    
    # Padrão para detectar alternativas corrompidas: letra seguida de lixo
    corrupted_pattern = r'([A-E])\s*(?:\d+\s*\n?|[+×\-=]+\s*\n?)*'
    
    # Verifica se há muitas alternativas corrompidas
    corrupted_matches = re.findall(corrupted_pattern, content)
    
    if len(corrupted_matches) >= 3:  # Se 3+ alternativas estão corrompidas
        print("Detectadas alternativas corrompidas, tentando corrigir...")
        
        # Remove todas as linhas que são só números ou símbolos após as letras
        lines = content.split('\n')
        cleaned_lines = []
        
        skip_next_garbage = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Se é uma linha com letra de alternativa
            if re.match(r'^[A-E]\s*', line):
                # Pega só a letra e remove o resto se for lixo
                letter_match = re.match(r'^([A-E])\s*(.*)$', line)
                if letter_match:
                    letter = letter_match.group(1)
                    rest = letter_match.group(2).strip()
                    
                    # Se o resto é só números/símbolos, descarta
                    if not rest or re.match(r'^[\d\s+×\-=]+$', rest):
                        # Para a questão 180 específica, temos as alternativas corretas
                        questao_180_alternativas = {
                            'A': '1 ano e 8 meses a 12 anos e 6 meses.',
                            'B': '1 ano e 8 meses a 5 anos.',
                            'C': '3 anos e 4 meses a 10 anos.',
                            'D': '4 anos e 2 meses a 5 anos.',
                            'E': '4 anos e 2 meses a 12 anos e 6 meses.'
                        }
                        
                        # Se é a questão 180 e temos alternativa conhecida
                        if "artigo 33 da lei brasileira sobre drogas" in content and letter in questao_180_alternativas:
                            cleaned_lines.append(f"{letter}) {questao_180_alternativas[letter]}")
                        else:
                            cleaned_lines.append(f"{letter}) [Conteúdo não disponível]")
                        skip_next_garbage = True
                    else:
                        cleaned_lines.append(line)
                        skip_next_garbage = False
                else:
                    cleaned_lines.append(line)
                    skip_next_garbage = False
            
            # Se é uma linha só com números/símbolos, pula se estamos em modo skip
            elif re.match(r'^[\d\s+×\-=]+$', line) and skip_next_garbage:
                continue
            
            # Senão, mantém a linha e para de pular
            else:
                cleaned_lines.append(line)
                skip_next_garbage = False
        
        content = '\n'.join(cleaned_lines)
        print("Alternativas corrompidas foram corrigidas")
    
    return content

def format_exercise_content(content: str) -> str:
    """Formata o conteúdo do exercício para HTML"""
    
    # Limpa o conteúdo primeiro
    content = clean_exercise_content(content)
    
    # Detecta e corrige alternativas corrompidas PRIMEIRO
    content = detect_and_fix_corrupted_alternatives(content)
    
    # Formatar alternativas de múltipla escolha
    content = format_multiple_choice_alternatives(content)
    
    # Substitui quebras de linha por <br>, mas preserva alternativas formatadas
    content = content.replace('\n\n', '</p><p>')
    content = content.replace('\n', '<br>')
    
    # Adiciona parágrafos
    content = f'<p>{content}</p>'
    
    # Destaca alternativas (A), (B), (C), (D), (E) - caso não foram formatadas antes
    content = re.sub(r'\(([A-E])\)', r'<strong style="color: #09278d;">(\1)</strong>', content)
    
    # Destaca números importantes (mas não dentro das alternativas já formatadas)
    # Evita números dentro de divs de alternativas
    if '<div class="alternative">' not in content:
        content = re.sub(r'\b(\d+(?:,\d+)*(?:\.\d+)?)\b', r'<strong>\1</strong>', content)
    
    return content


def format_multiple_choice_alternatives(content: str) -> str:
    """Formata especificamente as alternativas de múltipla escolha"""
    
    # Padrões para detectar alternativas (incluindo casos problemáticos)
    patterns = [
        # Padrão: A) ou (A) seguido de conteúdo
        r'([A-E])\)\s*([^\n\r]+?)(?=\s*[B-E]\)|$)',
        r'\(([A-E])\)\s*([^\n\r]+?)(?=\s*\([B-E]\)|$)',
        # Padrão: A 1234... (letra seguida de espaço e números/texto) - versão melhorada
        r'\b([A-E])\s+((?:[^\n\r]*?\n?)*?)(?=\s*[B-E]\s+|$)',
        # Padrão específico para texto bagunçado: A seguido de linhas de lixo até próxima letra
        r'([A-E])\s*\n?((?:\d+\s*\n?|[+×\-=]+\s*\n?)*?)(?=[B-E]\s*\n?|\n[B-E]|$)',
    ]
    
    # Tenta encontrar alternativas usando diferentes padrões
    alternatives_found = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        temp_alternatives = []
        
        for match in matches:
            letter = match.group(1)
            text = match.group(2).strip()
            
            # Limpa o texto da alternativa
            text = clean_alternative_text(text)
            
            if text and len(text) > 0:  # Só adiciona se tem conteúdo válido
                temp_alternatives.append((letter, text, match.span()))
        
        # Se encontrou um conjunto completo de alternativas (pelo menos 3)
        if len(temp_alternatives) >= 3:
            alternatives_found = temp_alternatives
            break
    
    # Se encontrou alternativas, formata elas
    if alternatives_found:
        # Ordena por posição no texto
        alternatives_found.sort(key=lambda x: x[2][0])
        
        # Cria HTML formatado para as alternativas
        alternatives_html = '<div class="alternatives-container" style="margin: 1rem 0; padding: 1rem; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #3b82f6;">'
        
        for letter, text, _ in alternatives_found:
            alternatives_html += f'''
            <div class="alternative" style="margin: 0.5rem 0; padding: 0.5rem; background-color: white; border-radius: 4px; display: flex; align-items: flex-start;">
                <span style="background-color: #09278d; color: white; font-weight: bold; padding: 0.2rem 0.5rem; border-radius: 50%; margin-right: 0.8rem; min-width: 1.5rem; text-align: center;">{letter}</span>
                <span style="flex: 1; line-height: 1.4;">{text}</span>
            </div>'''
        
        alternatives_html += '</div>'
        
        # Remove as alternativas originais do conteúdo
        for letter, text, span in reversed(alternatives_found):
            content = content[:span[0]] + content[span[1]:]
        
        # Adiciona as alternativas formatadas no final
        content = content.strip() + '\n\n' + alternatives_html
    
    return content


def clean_alternative_text(text: str) -> str:
    """Limpa o texto de uma alternativa de forma inteligente"""
    
    if not text:
        return ""
    
    # Remove caracteres especiais no início e fim
    text = text.strip()
    
    # Casos especiais: se o texto é só números e símbolos, tenta reconstruir
    if re.match(r'^[\d\s+×\-=]+$', text):
        # Para casos como "1 251 251 25++" - remove tudo
        return ""
    
    # Remove quebras de linha e múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    
    # Remove números soltos no início repetidamente
    text = re.sub(r'^(\d+\s*)+', '', text)
    
    # Remove sequências de números no meio do texto
    text = re.sub(r'\b\d{3,}\b', '', text)  # Remove números com 3+ dígitos
    
    # Remove símbolos repetidos (como "++" ou "××")
    text = re.sub(r'([+\-×÷=<>])\1+', '', text)
    
    # Remove caracteres especiais soltos
    text = re.sub(r'\s*[+×\-=]{1,}\s*', ' ', text)
    
    # Remove múltiplos espaços novamente
    text = re.sub(r'\s+', ' ', text)
    
    # Remove caracteres especiais no início e fim
    text = re.sub(r'^[^\w\d\(\)]+', '', text)
    text = re.sub(r'[^\w\d\s.,%()/-]+$', '', text)
    
    # Se sobrou texto muito curto ou apenas números, descarta
    if len(text.strip()) < 3 or re.match(r'^[\d\s]+$', text.strip()):
        return ""
    
    # Limita o tamanho máximo
    if len(text) > 200:
        text = text[:200] + "..."
    
    return text.strip()


def get_exercise_difficulty(content: str) -> str:
    """Determina a dificuldade do exercício baseado em heurísticas"""
    
    content_lower = content.lower()
    
    # Palavras que indicam maior dificuldade
    hard_indicators = ['demonstre', 'prove', 'calcule', 'determine', 'analise', 'interprete']
    medium_indicators = ['encontre', 'resolva', 'obtenha', 'considere']
    
    hard_count = sum(1 for word in hard_indicators if word in content_lower)
    medium_count = sum(1 for word in medium_indicators if word in content_lower)
    
    # Também considera o tamanho do texto
    if len(content) > 800 or hard_count >= 2:
        return "🔴 Difícil"
    elif len(content) > 400 or medium_count >= 2 or hard_count >= 1:
        return "🟡 Médio"
    else:
        return "🟢 Fácil"


def extract_key_concepts(content: str, topic: str) -> List[str]:
    """Extrai conceitos-chave do exercício"""
    
    content_lower = content.lower()
    
    concept_keywords = {
        'função': ['função', 'gráfico', 'domínio', 'imagem', 'variável'],
        'geometria': ['área', 'volume', 'perímetro', 'triângulo', 'círculo', 'ângulo'],
        'trigonometria': ['seno', 'cosseno', 'tangente', 'radiano', 'grau'],
        'probabilidade': ['probabilidade', 'evento', 'amostra', 'espaço amostral'],
        'estatística': ['média', 'mediana', 'moda', 'desvio', 'variância'],
        'álgebra': ['equação', 'inequação', 'sistema', 'variável']
    }
    
    concepts = []
    topic_lower = topic.lower()
    
    for category, keywords in concept_keywords.items():
        if category in topic_lower:
            for keyword in keywords:
                if keyword in content_lower:
                    concepts.append(keyword.title())
    
    # Se não encontrou conceitos específicos, use conceitos gerais
    if not concepts:
        general_concepts = ['Resolução de problemas', 'Interpretação de texto', 'Cálculos matemáticos']
        concepts = general_concepts[:2]
    
    return list(set(concepts))[:5]  # Máximo 5 conceitos únicos


def get_exercise_tips(topic: str, content: str) -> List[str]:
    """Gera dicas de resolução baseadas no tópico"""
    
    topic_lower = topic.lower()
    
    tips = []
    
    if 'função' in topic_lower:
        tips = [
            "Identifique o tipo de função (linear, quadrática, etc.)",
            "Analise o domínio e imagem quando necessário",
            "Use gráficos para visualizar o comportamento"
        ]
    elif 'geometria' in topic_lower:
        tips = [
            "Desenhe a figura se não estiver fornecida",
            "Identifique as fórmulas de área/volume necessárias",
            "Verifique se todas as unidades estão compatíveis"
        ]
    elif 'trigonometria' in topic_lower:
        tips = [
            "Identifique qual razão trigonométrica usar",
            "Lembre-se: SOH-CAH-TOA",
            "Converta entre graus e radianos se necessário"
        ]
    elif 'probabilidade' in topic_lower:
        tips = [
            "Defina claramente o espaço amostral",
            "Identifique se os eventos são independentes",
            "Use a regra da multiplicação ou adição conforme o caso"
        ]
    else:
        tips = [
            "Leia o problema com atenção e identifique o que é pedido",
            "Organize os dados fornecidos",
            "Verifique se a resposta faz sentido no contexto"
        ]
    
    return tips[:3]  # Máximo 3 dicas 