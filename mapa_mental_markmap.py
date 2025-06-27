#!/usr/bin/env python3
"""
Sistema de Mapa Mental com Streamlit-Markmap
Gera mapas mentais interativos baseados nas dúvidas da Sther
"""

import streamlit as st
import re
import os  # Adicionado para acessar variáveis de ambiente
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
        'Matemática': 'Como resolver equações do 2º grau?',
        'Física': 'Como calcular a velocidade de um objeto?',
        'Química': 'Como funciona uma reação de combustão?',
        'Biologia': 'Como ocorre a fotossíntese?',
        'Geografia': 'Como se formam as chuvas?',
        'História': 'Quais foram as causas da Revolução Francesa?',
        'Português': 'Quais são as figuras de linguagem?',
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
        'Português': '- Estrutura: Sujeito + Predicado',
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
        'Português': '- Figuras de linguagem e sintaxe',
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
        'Português': "Você é um especialista em educação de português e mapas mentais, com foco em ENEM.",
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
            'Português': '📚',
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
    
    # Verificar API key usando a nova função
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
        if st.button("🔄 Regenerar", help="Gerar nova versão do mapa mental"):
            cache_key = f"markmap_{hash(ultima_pergunta)}_{nivel_detalhamento}_{current_subject}"
            first_render_key = f"first_render_{cache_key}"
            
            # Limpar cache do mapa mental
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            
            # Limpar cache de primeira renderização
            if first_render_key in st.session_state:
                del st.session_state[first_render_key]
            
            # Limpar qualquer container de renderização anterior
            container_keys = [k for k in st.session_state.keys() if k.startswith("mindmap_container_")]
            for key in container_keys:
                del st.session_state[key]
            
            st.success("🔄 Mapa mental será regenerado!")
            st.rerun()
    
    # Controles de debug (em expander para não poluir a interface)
    with st.expander("🔧 Configurações Avançadas (Debug)", expanded=False):
        col_debug1, col_debug2 = st.columns(2)
        
        with col_debug1:
            show_debug = st.checkbox("Mostrar informações de debug", value=False)
            test_pan = st.checkbox("Forçar configurações de Pan/Zoom", value=True)
        
        with col_debug2:
            if st.button("🧪 Testar Mapa Simple"):
                st.info("📝 Execute: streamlit run teste_markmap_pan.py --server.port 8502")
            if st.button("🗑️ Limpar Cache"):
                if hasattr(st.session_state, 'markmap_cache'):
                    del st.session_state.markmap_cache
                st.success("Cache limpo!")
        
        if show_debug:
            st.markdown("**Diagnóstico:**")
            st.write(f"- streamlit-markmap versão: 1.0.1")
            st.write(f"- Cache keys: {len([k for k in st.session_state.keys() if 'markmap' in k])}")
            st.write(f"- Pergunta hash: {hash(ultima_pergunta)}")
            st.write(f"- Matéria atual: {current_subject}")
            
        if test_pan:
            st.info("🔧 Configurações de Pan/Zoom serão forçadas no mapa mental")
    
    # Gerar e exibir mapa mental
    debug_options = {
        'show_debug': st.session_state.get('show_debug', False),
        'test_pan': st.session_state.get('test_pan', True)
    }
    
    # Salvar configurações de debug no session_state
    if 'show_debug' in locals():
        st.session_state.show_debug = show_debug
    if 'test_pan' in locals():
        st.session_state.test_pan = test_pan
    
    exibir_mapa_mental_markmap(ultima_pergunta, api_key, nivel_detalhamento, debug_options, current_subject)

def obter_ultima_pergunta(chat_history: List[Any]) -> Optional[str]:
    """Obtém a última pergunta feita pelo usuário a partir de uma lista de objetos."""
    
    # Itera sobre o histórico de trás para frente
    for mensagem in reversed(chat_history):
        # Verifica se a mensagem é uma instância de HumanMessage
        if hasattr(mensagem, '__class__') and mensagem.__class__.__name__ == 'HumanMessage':
            return getattr(mensagem, 'content', '')
            
    return None

def garantir_configuracoes_interatividade(markdown_content: str) -> str:
    """Garante que o markdown tenha todas as configurações de interatividade necessárias"""
    
    # Configurações padrão de interatividade
    config_padrao = """---
markmap:
  pan: true
  zoom: true
  initialExpandLevel: 2
  maxWidth: 300
  colorFreezeLevel: 2
  duration: 500
  spacingHorizontal: 80
  spacingVertical: 5
  autoFit: true
  zoomInButton: true
  zoomOutButton: true
  resetButton: true
---"""
    
    # Se não tem frontmatter, adicionar
    if not markdown_content.startswith('---'):
        return config_padrao + "\n\n" + markdown_content
    
    # Se tem frontmatter, verificar e adicionar configurações faltantes
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
        
        # Verificar e adicionar configurações essenciais
        configuracoes_essenciais = [
            'pan: true',
            'zoom: true',
            'autoFit: true',
            'zoomInButton: true',
            'zoomOutButton: true',
            'resetButton: true'
        ]
        
        for config in configuracoes_essenciais:
            if config not in yaml_content:
                yaml_content += f'\n  {config}'
        
        # Reconstruir markdown
        return f"""---
markmap:
{yaml_content}
---

{remaining_content}"""
    
    # Fallback: adicionar configurações padrão
    return config_padrao + "\n\n" + markdown_content

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
        
        # Renderizar mapa mental com key única para garantir interatividade
        container_key = f"mindmap_container_{hash(pergunta)}_{nivel}_{current_subject}"
        markmap(markdown_content, height=600, key=container_key)
    else:
        st.error("❌ Erro ao gerar mapa mental. Tente novamente.")

def gerar_markdown_mapa_mental(pergunta: str, api_key: str, nivel: str, current_subject: str) -> str:
    """Gera o conteúdo markdown do mapa mental usando IA"""
    
    try:
        client = Groq(api_key=api_key)
        
        # Configurações por nível
        nivel_config = {
            "Básico": {
                "conceitos": "5-7 conceitos fundamentais",
                "profundidade": "2-3 níveis de hierarquia",
                "detalhes": "explicações simples e diretas"
            },
            "Intermediário": {
                "conceitos": "8-12 conceitos relacionados",
                "profundidade": "3-4 níveis de hierarquia",
                "detalhes": "fórmulas principais e exemplos"
            },
            "Avançado": {
                "conceitos": "12-15 conceitos e subdivisões",
                "profundidade": "4-5 níveis de hierarquia",
                "detalhes": "fórmulas completas, demonstrações e aplicações"
            }
        }
        
        config = nivel_config.get(nivel, nivel_config["Intermediário"])
        
        # Prompt melhorado e mais específico para as dúvidas da Sther
        prompt = f"""
Você é um especialista em mapas mentais educacionais do ENEM. A aluna Sther (17 anos, cursando 3º ano) fez esta pergunta específica sobre {current_subject}:

**Pergunta da Sther:** "{pergunta}"
**Matéria:** {current_subject}
**Nível:** {nivel}

**OBJETIVO:** Criar um mapa mental ESPECÍFICO que responda diretamente à dúvida da Sther, não um mapa genérico da matéria.

**CONFIGURAÇÃO:** {config['conceitos']}, {config['profundidade']}, {config['detalhes']}

**INSTRUÇÕES CRÍTICAS:**
1. Responda APENAS com o código Markdown do mapa mental
2. SEMPRE comece com as configurações YAML frontmatter
3. O título principal deve ser EXATAMENTE sobre a pergunta da Sther
4. Cada seção deve contribuir para responder a pergunta específica
5. Para fórmulas: use $formula$ (inline) ou $$formula$$ (display)
6. Use emojis relevantes para {current_subject}
7. Foque no que cai no ENEM para {current_subject}
8. Organize do conceito central para subtópicos relacionados

**ESTRUTURA OBRIGATÓRIA:**
```markdown
---
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

# 🎯 [RESPOSTA DIRETA À PERGUNTA DA STHER]

## 📚 Conceito Central
### 🔍 Definição
- Resposta direta à pergunta
- Por que é importante

### 📐 Como Funciona
- Mecanismo/processo principal
- {get_formula_example(current_subject)}

## 🧮 Resolução Prática
### ⚡ Passo a Passo
- Método 1: [específico para a pergunta]
- Método 2: [alternativo]

### 🎯 Dicas ENEM
- Como identificar no exame
- Pegadinhas comuns
- {get_advanced_formula_example(current_subject)}

## 📊 Exemplos Relacionados
### 🔢 Exemplo Básico
- Situação similar
- Resolução step-by-step

### 🏆 Exemplo ENEM
- Questão típica do exame
- Estratégia de resolução
```

IMPORTANTE: Adapte o conteúdo para responder ESPECIFICAMENTE à pergunta "{pergunta}" da Sther em {current_subject}.

GERE O MAPA MENTAL AGORA:"""
        
        # Modelo atualizado (llama-3.3-70b-versatile está obsoleto)
        response = client.chat.completions.create(
            model="llama-3.2-90b-text-preview",  # Modelo estável da Groq
            messages=[
                {"role": "system", "content": f"{get_subject_system_prompt(current_subject)} Você está ajudando Sther, uma estudante de 17 anos que vai prestar ENEM. Seja didático e específico."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,  # Aumentado para mapas mais detalhados
            temperature=0.3   # Reduzido para respostas mais consistentes
        )
        
        markdown_content = response.choices[0].message.content.strip()
        
        # Limpar e validar o markdown
        markdown_content = limpar_markdown(markdown_content)
        
        # Se não conseguiu gerar via IA, criar estrutura básica específica
        if not markdown_content or len(markdown_content) < 100:
            markdown_content = criar_mapa_mental_basico(pergunta, nivel, current_subject)
        
        return markdown_content
        
    except Exception as e:
        # Melhor tratamento de erro
        error_msg = str(e)
        
        # Se for erro de modelo obsoleto, informar claramente
        if "decommissioned" in error_msg or "model_decommissioned" in error_msg:
            st.error("🔧 **Modelo de IA atualizado necessário** - usando mapa mental básico")
        else:
            st.warning(f"⚠️ Erro na geração via IA: {error_msg[:100]}... - usando mapa mental básico")
        
        return criar_mapa_mental_basico(pergunta, nivel, current_subject)

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

def criar_mapa_mental_basico(pergunta: str, nivel: str, current_subject: str) -> str:
    """Cria um mapa mental básico quando a IA falha"""
    
    # Detectar tópico principal
    topico = detectar_topico_principal(pergunta, current_subject)
    
    if nivel == "Básico":
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

# 🎯 {topico}

## 📚 Conceitos Fundamentais
### 🔢 Definição
- O que é {topico.lower()}
- Importância no ENEM

### 📐 Propriedades Básicas
- Características principais
- {get_formula_example(current_subject)}

## 🧮 Resolução
### 🎯 Método Principal
- Passo 1: Identificar
- Passo 2: Aplicar
- Passo 3: Resolver

### 📊 Exemplo ENEM
- Tipo de questão comum
- Estratégia de resolução
"""
    
    elif nivel == "Intermediário":
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

# 🎯 {topico}

## 📚 Fundamentos
### 🔢 Conceitos Base
- Definições essenciais
- {get_formula_example(current_subject)}

### 📐 Propriedades
- Características importantes
- {get_advanced_formula_example(current_subject)}

## 🧮 Métodos de Resolução
### 🎯 Método Algébrico
- Manipulação de equações
- Isolamento de variáveis

### 📊 Método Gráfico
- Interpretação visual
- Pontos importantes

## 🔗 Aplicações
### 📈 Problemas Práticos
- Situações reais
- Modelagem matemática

### 🎓 Questões ENEM
- Padrões frequentes
- Dicas de resolução
"""
    
    else:  # Avançado
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

# 🎯 {topico}

## 📚 Teoria Fundamental
### 🔢 Axiomas e Definições
- Base teórica sólida
- {get_formula_example(current_subject)}

### 📐 Teoremas Principais
- Demonstrações importantes
- {get_advanced_formula_example(current_subject)}

## 🧮 Métodos Avançados
### 🎯 Resolução Analítica
- Técnicas algébricas
- {get_formula_example(current_subject)}

### 📊 Resolução Gráfica
- Interpretação geométrica
- {get_advanced_formula_example(current_subject)}

## 🔗 Conexões Interdisciplinares
### 🌐 Outras Áreas da Matemática
- Álgebra ↔ Geometria
- Cálculo ↔ Funções

### 🎓 Aplicações Avançadas
- Física matemática
- Engenharias

## 📈 Estratégias ENEM
### 🎯 Reconhecimento de Padrões
- Tipos de questões
- Armadilhas comuns

### ⚡ Técnicas Rápidas
- Métodos de estimativa
- Eliminação de alternativas
"""

def detectar_topico_principal(pergunta: str, current_subject: str) -> str:
    """Detecta o tópico principal da pergunta baseado na matéria"""
    
    pergunta_lower = pergunta.lower()
    
    # Tópicos por matéria
    topicos_por_materia = {
        'Matemática': {
            'Equação': ['equacao', 'equaçao', 'resolver', 'raiz', 'solução'],
            'Função': ['funcao', 'função', 'grafico', 'gráfico', 'domínio', 'imagem'],
            'Geometria': ['geometria', 'área', 'volume', 'perímetro', 'triângulo', 'círculo'],
            'Trigonometria': ['trigonometria', 'seno', 'cosseno', 'tangente', 'ângulo'],
            'Probabilidade': ['probabilidade', 'estatística', 'média', 'chances'],
            'Análise Combinatória': ['combinação', 'permutação', 'arranjo', 'fatorial'],
            'Progressões': ['progressão', 'PA', 'PG', 'sequência', 'série'],
            'Logaritmo': ['logaritmo', 'log', 'exponencial', 'potência'],
            'Matriz': ['matriz', 'determinante', 'sistema linear'],
            'Derivada': ['derivada', 'limite', 'taxa', 'variação']
        },
        'Física': {
            'Mecânica': ['força', 'movimento', 'velocidade', 'aceleração', 'newton'],
            'Termodinâmica': ['calor', 'temperatura', 'energia térmica', 'dilatação'],
            'Eletricidade': ['corrente', 'tensão', 'resistência', 'circuito', 'elétrica'],
            'Óptica': ['luz', 'espelho', 'lente', 'refração', 'reflexão'],
            'Ondulatória': ['onda', 'som', 'frequência', 'amplitude', 'oscilação'],
            'Relatividade': ['relatividade', 'einstein', 'velocidade da luz']
        },
        'Química': {
            'Átomo': ['átomo', 'elétron', 'próton', 'núcleo', 'orbital'],
            'Ligações': ['ligação', 'covalente', 'iônica', 'metálica'],
            'Reações': ['reação', 'combustão', 'síntese', 'decomposição'],
            'Termoquímica': ['energia', 'entalpia', 'calor', 'exotérmica', 'endotérmica'],
            'Cinética': ['velocidade', 'catalisador', 'concentração'],
            'Equilíbrio': ['equilíbrio', 'constante', 'le chatelier']
        },
        'Biologia': {
            'Citologia': ['célula', 'membrana', 'núcleo', 'organela'],
            'Genética': ['gene', 'DNA', 'hereditariedade', 'mutação'],
            'Evolução': ['evolução', 'seleção natural', 'darwin', 'especiação'],
            'Ecologia': ['ecossistema', 'cadeia alimentar', 'população'],
            'Fisiologia': ['respiração', 'circulação', 'digestão', 'sistema']
        },
        'Geografia': {
            'Geologia': ['relevo', 'rocha', 'solo', 'erosão', 'tectônica'],
            'Climatologia': ['clima', 'chuva', 'temperatura', 'vento'],
            'Hidrografia': ['rio', 'bacia', 'água', 'oceano'],
            'Demografia': ['população', 'migração', 'densidade', 'crescimento'],
            'Geopolítica': ['território', 'fronteira', 'conflito', 'globalização']
        },
        'História': {
            'Brasil Colônia': ['colonial', 'escravidão', 'bandeirantes', 'jesuítas'],
            'Brasil República': ['república', 'vargas', 'ditadura', 'redemocratização'],
            'Idade Média': ['feudalismo', 'igreja', 'cruzadas', 'peste'],
            'Idade Moderna': ['renascimento', 'reforma', 'descobrimentos'],
            'Idade Contemporânea': ['revolução industrial', 'guerra mundial', 'imperialismo']
        },
        'Português': {
            'Gramática': ['verbo', 'substantivo', 'sintaxe', 'concordância'],
            'Literatura': ['romantismo', 'realismo', 'modernismo', 'poesia'],
            'Redação': ['dissertação', 'argumentação', 'introdução', 'conclusão'],
            'Interpretação': ['texto', 'significado', 'contexto', 'inferência']
        },
        'Redação': {
            'Estrutura': ['introdução', 'desenvolvimento', 'conclusão', 'parágrafo'],
            'Argumentação': ['argumento', 'tese', 'exemplo', 'dados'],
            'Coesão': ['conectivo', 'coesão', 'coerência', 'articulação'],
            'Proposta': ['intervenção', 'solução', 'problema', 'sociedade']
        }
    }
    
    topicos = topicos_por_materia.get(current_subject, {})
    
    for topico, palavras_chave in topicos.items():
        if any(palavra in pergunta_lower for palavra in palavras_chave):
            return topico
    
    # Se não encontrou tópico específico, extrair da pergunta
    palavras = pergunta.split()
    if len(palavras) > 2:
        return ' '.join(palavras[:3]).title()
    
    return current_subject

def analisar_markdown_stats(markdown: str) -> Dict[str, int]:
    """Analisa estatísticas do markdown do mapa mental"""
    
    linhas = markdown.split('\n')
    
    stats = {
        'conceitos': len([l for l in linhas if l.strip().startswith('#')]),
        'conexoes': len([l for l in linhas if '↔' in l or '→' in l or '←' in l]),
        'niveis': len(set([len(l) - len(l.lstrip('#')) for l in linhas if l.strip().startswith('#') and l.strip() != ''])),
        'formulas': len(re.findall(r'\$[^$]+\$', markdown)) + len(re.findall(r'\$\$[^$]+\$\$', markdown))
    }
    
    return stats

def display_mapa_mental_wrapper():
    """Wrapper para compatibilidade com o app principal"""
    display_mapa_mental_markmap()

if __name__ == "__main__":
    # Só configura página se executado diretamente
    try:
        st.set_page_config(
            page_title="Mapa Mental Markmap",
            page_icon="🧠",
            layout="wide"
        )
    except st.errors.StreamlitAPIException:
        # Já foi configurado pelo app principal, ignora
        pass
    display_mapa_mental_markmap() 