#!/usr/bin/env python3
"""
Sistema de Mapa Mental com Streamlit-Markmap
Gera mapas mentais interativos baseados nas dúvidas da Sther
"""

import streamlit as st
import re
import os
from typing import Dict, List, Any, Optional
from groq import Groq
import time

try:
    from streamlit_markmap import markmap
    MARKMAP_AVAILABLE = True
except ImportError:
    MARKMAP_AVAILABLE = False
    st.error("❌ streamlit-markmap não instalado. Execute: pip install streamlit-markmap==1.0.1")

def get_example_question(subject: str) -> str:
    """Retorna pergunta de exemplo para cada matéria"""
    examples = {
        'Matemática': 'Como resolver uma equação do segundo grau?',
        'Física': 'Como calcular a velocidade de um objeto?',
        'Química': 'Como funciona uma reação de combustão?',
        'Biologia': 'Como ocorre a fotossíntese?',
        'Geografia': 'Como se formam as chuvas?',
        'História': 'Quais foram as causas da Revolução Francesa?',
        'Língua Portuguesa': 'Quais são as figuras de linguagem?',
        'Redação': 'Como estruturar uma dissertação argumentativa?'
    }
    return examples.get(subject, 'Faça uma pergunta sobre sua dúvida!')

def get_formula_example(subject: str) -> str:
    """Retorna exemplo de fórmula básica para cada matéria"""
    examples = {
        'Matemática': '- $f(x) = ax + b$',
        'Física': '- $v = \\frac{\\Delta s}{\\Delta t}$',
        'Química': '- $C = \\frac{n}{V}$',
        'Biologia': '- Respiração: $C_6H_{12}O_6 + O_2 \\rightarrow CO_2 + H_2O$',
        'Geografia': '- Densidade demográfica = População/Área',
        'História': '- Cronologia de eventos',
        'Língua Portuguesa': '- Estrutura: Sujeito + Predicado',
        'Redação': '- Introdução + Desenvolvimento + Conclusão'
    }
    return examples.get(subject, '- Conceito fundamental')

def get_advanced_formula_example(subject: str) -> str:
    """Retorna exemplo de fórmula avançada para cada matéria"""
    examples = {
        'Matemática': '- $$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$',
        'Física': '- $$F = ma$$\\n- $$E = mc^2$$',
        'Química': '- $$pH = -\\log[H^+]$$',
        'Biologia': '- Fotossíntese: $6CO_2 + 6H_2O \\rightarrow C_6H_{12}O_6 + 6O_2$',
        'Geografia': '- Índices demográficos complexos',
        'História': '- Análise de causas e consequências',
        'Língua Portuguesa': '- Figuras de linguagem e sintaxe',
        'Redação': '- Argumentação e coesão textual'
    }
    return examples.get(subject, '- Conceito avançado')

def get_subject_system_prompt(subject: str) -> str:
    """Retorna prompt de sistema específico para cada matéria"""
    prompts = {
        'Matemática': "Você é um especialista em educação matemática e mapas mentais.",
        'Física': "Você é um especialista em educação de física e mapas mentais, com foco em ENEM.",
        'Química': "Você é um especialista em educação de química e mapas mentais, com foco em ENEM.",
        'Biologia': "Você é um especialista em educação de biologia e mapas mentais, com foco em ENEM.",
        'Geografia': "Você é um especialista em educação de geografia e mapas mentais, com foco em ENEM.",
        'História': "Você é um especialista em educação de história e mapas mentais, com foco em ENEM.",
        'Língua Portuguesa': "Você é um especialista em educação de português e mapas mentais, com foco em ENEM.",
        'Redação': "Você é um especialista em educação de redação e mapas mentais, com foco em ENEM."
    }
    return prompts.get(subject, "Você é um especialista em educação e mapas mentais.")

def get_api_key_for_mindmap():
    """Carrega a chave da API do Streamlit secrets ou variáveis de ambiente."""
    # Tenta Streamlit Secrets (para Cloud)
    if hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        if api_key and isinstance(api_key, str) and api_key.strip():
            return api_key.strip()
    
    # Fallback para variáveis de ambiente (para local)
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key and isinstance(api_key, str) and api_key.strip():
        return api_key.strip()
    
    return None

# Definições de classes para compatibilidade com o histórico de chat
class HumanMessage:
    def __init__(self, content):
        self.content = content

class AIMessage:
    def __init__(self, content):
        self.content = content 

def display_mapa_mental_markmap():
    """Interface principal do mapa mental usando streamlit-markmap"""
    
    st.markdown("# 🧠 Mapa Mental Interativo")
    st.markdown("Visualização dinâmica dos conceitos relacionados à sua dúvida!")
    
    if not MARKMAP_AVAILABLE:
        st.error("""
        📦 **Dependência não encontrada**
        
        Para usar os mapas mentais, instale a dependência:
        ```bash
        pip install streamlit-markmap==1.0.1
        ```
        """)
        return
    
    # Verificar se há histórico de chat da matéria atual
    current_subject = st.session_state.get('current_subject', 'Matemática')
    chat_history_key = f"chat_history_{current_subject}"
    chat_history = st.session_state.get(chat_history_key, [])
    
    if not chat_history:
        # Obtém informações da matéria atual
        subject_icons = {
            'Matemática': '🧮',
            'Física': '⚡',
            'Química': '⚗️',
            'Biologia': '🧬',
            'Geografia': '🌍',
            'História': '🏛️',
            'Língua Portuguesa': '📚',
            'Redação': '✍️'
        }
        
        subject_icon = subject_icons.get(current_subject, '📚')
        
        st.info(f"""
        📝 **Como funciona o Mapa Mental:**
        
        1. **💬 Faça uma pergunta** na aba "Chat" para o professor de {current_subject}
        2. **🧠 Volte para esta aba** e veja o mapa mental automático
        3. **🔍 Explore os conceitos** de forma visual e interativa
        4. **🔄 Regenere** se quiser uma nova perspectiva
        
        {subject_icon} **Exemplo para {current_subject}:** 
        - "{get_example_question(current_subject)}" → Mapa mental automático!
        """)
        return
    
    # Obter última pergunta do usuário
    ultima_pergunta = obter_ultima_pergunta(chat_history)
    
    if not ultima_pergunta:
        st.warning("💬 Faça uma pergunta na aba Chat primeiro para gerar o mapa mental!")
        return
    
    # Verificar API key
    api_key = get_api_key_for_mindmap()
    if not api_key:
        st.warning("""
        🔑 **Configure sua API Key primeiro!**
        
        Sua chave da Groq não foi encontrada. Por favor, configure-a nos Secrets do Streamlit Cloud com o nome `GROQ_API_KEY`.
        """)
        return
    
    # Interface de controle
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"### 🗺️ Mapa Mental de {current_subject}")
        with st.expander("📋 Contexto da pergunta", expanded=False):
            st.markdown(f"**Pergunta:** {ultima_pergunta}")
            st.markdown(f"**Matéria:** {current_subject}")
    
    with col2:
        nivel_detalhamento = st.selectbox(
            "Nível:",
            ["Básico", "Intermediário", "Avançado"],
            index=1,
            help="Nível de detalhamento do mapa mental"
        )
    
    with col3:
        # Botão para gerar/regenerar o mapa mental
        if st.button("🧠 Gerar Mapa Mental", help="Gerar mapa mental baseado na sua pergunta"):
            # Marcar que o mapa mental deve ser gerado
            st.session_state.gerar_mapa_mental = True
            st.session_state.nivel_mapa_mental = nivel_detalhamento
            st.success("🧠 Gerando mapa mental...")
            st.rerun()
    
    # Verificar se o mapa mental deve ser exibido
    if st.session_state.get('gerar_mapa_mental', False):
        # Controles de debug (em expander para não poluir a interface)
        with st.expander("🔧 Configurações Avançadas (Debug)", expanded=False):
            col_debug1, col_debug2 = st.columns(2)
            
            with col_debug1:
                show_debug = st.checkbox("Mostrar Debug", value=False)
                test_pan = st.checkbox("Testar Pan/Zoom", value=True)
            
            with col_debug2:
                if st.button("🗑️ Limpar Cache"):
                    # Limpar caches de mapa mental
                    keys_to_remove = [k for k in st.session_state.keys() if 'markmap_' in k or 'first_render_' in k]
                    for key in keys_to_remove:
                        del st.session_state[key]
                    st.success("Cache limpo!")
                    st.rerun()
        
        debug_options = {
            'show_debug': locals().get('show_debug', False),
            'test_pan': locals().get('test_pan', True)
        }
        
        # Exibir mapa mental
        exibir_mapa_mental_markmap(ultima_pergunta, api_key, nivel_detalhamento, debug_options, current_subject)
        
        # Limpar flag após exibir
        st.session_state.gerar_mapa_mental = False

def obter_ultima_pergunta(chat_history: List[Any]) -> Optional[str]:
    """Obtém a última pergunta feita pelo usuário a partir de uma lista de objetos."""
    
    # Itera sobre o histórico de trás para frente
    for mensagem in reversed(chat_history):
        # Verifica se a mensagem é uma instância de HumanMessage
        if hasattr(mensagem, '__class__') and mensagem.__class__.__name__ == 'HumanMessage':
            return getattr(mensagem, 'content', '')
            
    return None

def garantir_configuracoes_interatividade(markdown_content: str) -> str:
    """Garante que o markdown tenha configurações básicas de interatividade"""
    
    # Configurações básicas e compatíveis
    config_basica = """---
markmap:
  pan: true
  zoom: true
  initialExpandLevel: 2
  maxWidth: 300
  colorFreezeLevel: 2
  duration: 500
  spacingHorizontal: 80
  spacingVertical: 5
---"""
    
    # Se não tem frontmatter, adicionar
    if not markdown_content.startswith('---'):
        return config_basica + "\n\n" + markdown_content
    
    # Se tem frontmatter, verificar se tem configurações básicas
    lines = markdown_content.split('\n')
    yaml_end = -1
    
    # Encontrar o final do YAML
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            yaml_end = i
            break
    
    if yaml_end > 0:
        # Extrair YAML existente
        yaml_content = '\n'.join(lines[1:yaml_end])
        remaining_content = '\n'.join(lines[yaml_end+1:])
        
        # Verificar se tem configurações básicas
        if 'pan: true' not in yaml_content or 'zoom: true' not in yaml_content:
            # Adicionar configurações básicas se faltarem
            yaml_content += '\n  pan: true\n  zoom: true'
        
        # Reconstruir markdown
        return f"""---
markmap:
{yaml_content}
---

{remaining_content}"""
    
    # Fallback: adicionar configurações básicas
    return config_basica + "\n\n" + markdown_content 

def exibir_mapa_mental_markmap(pergunta: str, api_key: str, nivel: str, debug_options: dict = None, current_subject: str = 'Matemática'):
    """Gera e exibe o mapa mental usando streamlit-markmap"""
    
    if debug_options is None:
        debug_options = {'show_debug': False, 'test_pan': True}
    
    # Cache baseado na pergunta, nível e matéria
    cache_key = f"markmap_{hash(pergunta)}_{nivel}_{current_subject}"
    
    # Verificar se é a primeira renderização para esta pergunta
    first_render_key = f"first_render_{cache_key}"
    is_first_render = first_render_key not in st.session_state
    
    # Verificar cache
    if cache_key not in st.session_state:
        with st.spinner("🧠 Gerando mapa mental interativo..."):
            markdown_content = gerar_markdown_mapa_mental(pergunta, api_key, nivel, current_subject)
            st.session_state[cache_key] = markdown_content
            # Marcar que não é mais a primeira renderização
            st.session_state[first_render_key] = False
    else:
        markdown_content = st.session_state[cache_key]
    
    if markdown_content:
        # Exibir estatísticas do mapa
        stats = analisar_markdown_stats(markdown_content)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Conceitos", stats['conceitos'])
        with col2:
            st.metric("🔗 Conexões", stats['conexoes'])
        with col3:
            st.metric("📚 Níveis", stats['niveis'])
        with col4:
            st.metric("🧮 Fórmulas", stats['formulas'])
        
        st.markdown("---")
        
        # Debug info (se habilitado)
        if debug_options.get('show_debug', False):
            with st.expander("🔍 Debug Info - Markdown Gerado", expanded=False):
                st.code(markdown_content, language="markdown")
                
                # Verificar se contém configurações de pan/zoom
                has_pan = 'pan:' in markdown_content
                has_zoom = 'zoom:' in markdown_content
                
                st.write(f"✅ Contém 'pan:': {has_pan}")
                st.write(f"✅ Contém 'zoom:': {has_zoom}")
                st.write(f"🔄 Primeira renderização: {is_first_render}")
                
                if not has_pan or not has_zoom:
                    st.warning("⚠️ Configurações de pan/zoom podem estar faltando!")
        
        # Garantir que as configurações de interatividade estejam presentes
        markdown_content = garantir_configuracoes_interatividade(markdown_content)
        
        # Renderizar mapa mental
        markmap(markdown_content, height=600)
    else:
        st.error("❌ Erro ao gerar mapa mental. Tente novamente.")

def gerar_markdown_mapa_mental(pergunta: str, api_key: str, nivel: str, current_subject: str) -> str:
    """Gera o conteúdo markdown do mapa mental usando IA"""
    
    try:
        client = Groq(api_key=api_key)
        
        # Detectar tópico específico da pergunta ANTES de gerar o prompt
        topico_especifico = extrair_topico_especifico(pergunta, current_subject)
        
        # Configurações por nível
        nivel_config = {
            "Básico": {
                "conceitos": "4-6 conceitos fundamentais",
                "profundidade": "2-3 níveis de hierarquia",
                "detalhes": "explicações simples e diretas",
                "foco": "conceitos básicos essenciais"
            },
            "Intermediário": {
                "conceitos": "7-10 conceitos relacionados",
                "profundidade": "3-4 níveis de hierarquia",
                "detalhes": "fórmulas principais e exemplos práticos",
                "foco": "aplicações e métodos de resolução"
            },
            "Avançado": {
                "conceitos": "10-14 conceitos e subdivisões",
                "profundidade": "4-5 níveis de hierarquia",
                "detalhes": "fórmulas completas, demonstrações e conexões",
                "foco": "análise profunda e aplicações complexas"
            }
        }
        
        config = nivel_config.get(nivel, nivel_config["Intermediário"])
        
        # Prompt completamente reformulado para ser ESPECÍFICO à dúvida
        prompt = f"""
Você é um especialista em educação e mapas mentais, focado em ENEM. Sua tarefa é criar um mapa mental ESPECÍFICO e DIRECIONADO.

**PERGUNTA DA ESTUDANTE:** "{pergunta}"
**MATÉRIA:** {current_subject}
**TÓPICO IDENTIFICADO:** {topico_especifico}
**NÍVEL:** {nivel}

**INSTRUÇÕES CRÍTICAS:**

1. **FOQUE EXCLUSIVAMENTE NO TÓPICO:** O mapa mental deve ser sobre "{topico_especifico}" especificamente, NÃO sobre {current_subject} em geral.

2. **ANALISE A PERGUNTA:** Se a pergunta menciona um conceito específico (ex: "matrizes", "termodinâmica", "função quadrática"), TODO o mapa deve girar em torno DESSE conceito.

3. **ESTRUTURA DIRECIONADA:**
   - Título principal: O tópico específico da pergunta
   - Ramificações: Aspectos diretos desse tópico
   - Subtópicos: Conceitos que ajudam a entender especificamente esse assunto
   - {config['conceitos']} no total
   - {config['profundidade']} máximo
   - Foco: {config['foco']}

4. **EVITE GENERALIDADES:** NÃO inclua conceitos gerais da matéria que não se relacionam diretamente com o tópico da pergunta.

5. **FORMATO DE SAÍDA:**
   - Inclua sempre o frontmatter YAML
   - Use emojis relevantes
   - Fórmulas em LaTeX quando necessário
   - Responda APENAS com o markdown

**EXEMPLO CORRETO:**
Se pergunta = "Como resolver equações do segundo grau?"
Mapa = Foco total em "Equações do Segundo Grau", não em "Matemática geral"

Agora crie o mapa específico para "{topico_especifico}":
"""
        
        # Usar modelo mais recente e estável
        response = client.chat.completions.create(
            model="llama-3.2-90b-text-preview",
            messages=[
                {"role": "system", "content": f"{get_subject_system_prompt(current_subject)} Você está criando um mapa mental específico para Sther, de 17 anos, que vai prestar ENEM. Seja preciso e direcionado ao tópico da pergunta."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.2   # Reduzido para mais foco e consistência
        )
        
        markdown_content = response.choices[0].message.content.strip()
        
        # Limpar e validar o markdown
        markdown_content = limpar_markdown(markdown_content)
        
        # Validar se o conteúdo é específico (verificar se menciona o tópico)
        if not validar_especificidade_mapa(markdown_content, topico_especifico):
            # Se não for específico, usar versão básica específica
            markdown_content = criar_mapa_mental_especifico(pergunta, topico_especifico, nivel, current_subject)
        
        # Se ainda não conseguiu gerar conteúdo adequado, usar fallback
        if not markdown_content or len(markdown_content) < 100:
            markdown_content = criar_mapa_mental_especifico(pergunta, topico_especifico, nivel, current_subject)
        
        return markdown_content
        
    except Exception as e:
        # Melhor tratamento de erro com fallback específico
        error_msg = str(e)
        
        if "decommissioned" in error_msg or "model_decommissioned" in error_msg:
            st.error("🔧 **Modelo de IA atualizado necessário** - usando mapa mental específico")
        else:
            st.warning(f"⚠️ Erro na geração via IA: {error_msg[:100]}... - usando mapa mental específico")
        
        # Fallback que também é específico
        topico_especifico = extrair_topico_especifico(pergunta, current_subject)
        return criar_mapa_mental_especifico(pergunta, topico_especifico, nivel, current_subject)

def limpar_markdown(texto: str) -> str:
    """Limpa e valida o conteúdo markdown"""
    
    # Remover blocos de código markdown se existirem
    texto = re.sub(r'```markdown\n?', '', texto)
    texto = re.sub(r'```\n?', '', texto)
    
    # Garantir que começa com #
    linhas = texto.split('\n')
    if linhas and not linhas[0].strip().startswith('#'):
        # Procurar primeira linha com #
        for i, linha in enumerate(linhas):
            if linha.strip().startswith('#'):
                texto = '\n'.join(linhas[i:])
                break
    
    return texto.strip() 

def extrair_topico_especifico(pergunta: str, current_subject: str) -> str:
    """Extrai o tópico específico da pergunta"""
    pergunta_lower = pergunta.lower()
    
    # Detecção específica para alguns tópicos principais
    if 'matriz' in pergunta_lower:
        return 'Matrizes'
    elif 'segundo grau' in pergunta_lower or 'bhaskara' in pergunta_lower:
        return 'Equações do 2º Grau'
    elif 'trigonometria' in pergunta_lower or 'seno' in pergunta_lower:
        return 'Trigonometria'
    elif 'força' in pergunta_lower or 'newton' in pergunta_lower:
        return 'Dinâmica'
    elif 'termodinamica' in pergunta_lower or 'calor' in pergunta_lower:
        return 'Termodinâmica'
    else:
        # Extrair primeiras palavras como tópico
        palavras = pergunta.split()
        if len(palavras) > 2:
            return ' '.join(palavras[:2]).title()
        return current_subject

def validar_especificidade_mapa(markdown_content: str, topico_especifico: str) -> bool:
    """Valida se o mapa mental é específico ao tópico identificado"""
    if not markdown_content or not topico_especifico:
        return False
    return topico_especifico.lower() in markdown_content.lower()

def criar_mapa_mental_especifico(pergunta: str, topico_especifico: str, nivel: str, current_subject: str) -> str:
    """Cria um mapa mental específico para o tópico identificado"""
    
    # Emojis por matéria
    emoji_materia = {
        'Matemática': '🧮', 'Física': '⚡', 'Química': '⚗️', 'Biologia': '🧬',
        'Geografia': '🌍', 'História': '🏛️', 'Língua Portuguesa': '📚', 'Redação': '✍️'
    }
    emoji = emoji_materia.get(current_subject, '📚')
    
    return f"""---
markmap:
  pan: true
  zoom: true
  initialExpandLevel: 2
  maxWidth: 300
  colorFreezeLevel: 2
  duration: 500
  spacingHorizontal: 80
  spacingVertical: 5
---

# {emoji} {topico_especifico}

## 📚 Conceitos Fundamentais
### 🔍 Definição
- O que é {topico_especifico.lower()}
- Características principais

### 📐 Propriedades
- Elementos essenciais
- {get_formula_example(current_subject)}

## 🎯 Aplicações
### 📝 Como resolver
- Métodos principais
- Estratégias de solução

### 🎓 No ENEM
- Tipos de questão
- Dicas importantes
"""

def detectar_topico_principal(pergunta: str, current_subject: str) -> str:
    """Detecta o tópico principal da pergunta baseado na matéria"""
    palavras = pergunta.split()
    if len(palavras) > 2:
        return ' '.join(palavras[:2]).title()
    return current_subject

def analisar_markdown_stats(markdown: str) -> Dict[str, int]:
    """Analisa estatísticas do markdown do mapa mental"""
    linhas = markdown.split('\n')
    return {
        'conceitos': len([l for l in linhas if l.strip().startswith('#')]),
        'conexoes': len([l for l in linhas if '↔' in l or '→' in l or '←' in l]),
        'niveis': 3,
        'formulas': len(re.findall(r'\$[^$]+\$', markdown))
    }

def display_mapa_mental_wrapper():
    """Wrapper para compatibilidade com o app principal"""
    if 'gerar_mapa_mental' not in st.session_state:
        st.session_state.gerar_mapa_mental = False
    display_mapa_mental_markmap()

if __name__ == "__main__":
    try:
        st.set_page_config(
            page_title="Mapa Mental Markmap",
            page_icon="🧠",
            layout="wide"
        )
    except st.errors.StreamlitAPIException:
        pass
    display_mapa_mental_markmap() 