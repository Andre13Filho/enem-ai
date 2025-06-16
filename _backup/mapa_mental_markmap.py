#!/usr/bin/env python3
"""
Sistema de Mapa Mental com Streamlit-Markmap
Gera mapas mentais interativos baseados nas dúvidas da Sther
"""

import streamlit as st
import re
from typing import Dict, List, Any, Optional
from groq import Groq

try:
    from streamlit_markmap import markmap
    MARKMAP_AVAILABLE = True
except ImportError:
    MARKMAP_AVAILABLE = False
    st.error("❌ streamlit-markmap não instalado. Execute: pip install streamlit-markmap==1.0.1")

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
    
    # Verificar se há histórico de chat da matemática
    chat_history = st.session_state.get('chat_history', {}).get('Matemática', [])
    
    if not chat_history:
        st.info("""
        📝 **Como funciona o Mapa Mental:**
        
        1. **💬 Faça uma pergunta** na aba "Chat" para o Professor Carlos
        2. **🧠 Volte para esta aba** e veja o mapa mental automático
        3. **🔍 Explore os conceitos** de forma visual e interativa
        4. **🔄 Regenere** se quiser uma nova perspectiva
        
        🎯 **Exemplo:** "Como resolver equações do 2º grau?" → Mapa mental automático!
        """)
        return
    
    # Obter última pergunta do usuário
    ultima_pergunta = obter_ultima_pergunta(chat_history)
    
    if not ultima_pergunta:
        st.warning("💬 Faça uma pergunta na aba Chat primeiro para gerar o mapa mental!")
        return
    
    # Verificar API key
    api_key = getattr(st.session_state, 'api_key', '')
    if not api_key:
        st.warning("""
        🔑 **Configure sua API Key primeiro!**
        
        Vá para a aba "💬 Chat" e configure sua API Key da Groq na barra lateral.
        """)
        return
    
    # Interface de controle
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown("### 🗺️ Mapa Mental da sua Dúvida")
        with st.expander("📋 Contexto da pergunta", expanded=False):
            st.markdown(f"**Pergunta:** {ultima_pergunta}")
    
    with col2:
        nivel_detalhamento = st.selectbox(
            "Nível:",
            ["Básico", "Intermediário", "Avançado"],
            index=1,
            help="Nível de detalhamento do mapa mental"
        )
    
    with col3:
        if st.button("🔄 Regenerar", help="Gerar nova versão do mapa mental"):
            cache_key = f"markmap_{hash(ultima_pergunta)}_{nivel_detalhamento}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
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
    
    exibir_mapa_mental_markmap(ultima_pergunta, api_key, nivel_detalhamento, debug_options)

def obter_ultima_pergunta(chat_history: List[Dict]) -> Optional[str]:
    """Obtém a última pergunta feita pelo usuário"""
    
    for mensagem in reversed(chat_history):
        if mensagem.get('role') == 'user':
            return mensagem.get('content', '')
    
    return None

def exibir_mapa_mental_markmap(pergunta: str, api_key: str, nivel: str, debug_options: dict = None):
    """Gera e exibe o mapa mental usando streamlit-markmap"""
    
    if debug_options is None:
        debug_options = {'show_debug': False, 'test_pan': True}
    
    # Cache baseado na pergunta e nível
    cache_key = f"markmap_{hash(pergunta)}_{nivel}"
    
    # Verificar cache
    if cache_key not in st.session_state:
        with st.spinner("🧠 Gerando mapa mental interativo..."):
            markdown_content = gerar_markdown_mapa_mental(pergunta, api_key, nivel)
            st.session_state[cache_key] = markdown_content
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
                
                if not has_pan or not has_zoom:
                    st.warning("⚠️ Configurações de pan/zoom podem estar faltando!")
        
        # Renderizar mapa mental
        try:
            # Garantir que o markdown sempre tenha as configurações de interatividade
            if not markdown_content.startswith('---'):
                # Adicionar configurações de markmap no início
                markdown_content = """---
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

""" + markdown_content
            else:
                # Se já tem frontmatter, verificar se tem as configurações essenciais
                lines = markdown_content.split('\n')
                yaml_end = -1
                for i, line in enumerate(lines):
                    if i > 0 and line.strip() == '---':
                        yaml_end = i
                        break
                
                if yaml_end > 0:
                    # Extrair configurações YAML existentes
                    yaml_content = '\n'.join(lines[1:yaml_end])
                    remaining_content = '\n'.join(lines[yaml_end+1:])
                    
                    # Verificar se pan/zoom estão nas configurações
                    if 'pan:' not in yaml_content:
                        yaml_content += '\n  pan: true'
                    if 'zoom:' not in yaml_content:
                        yaml_content += '\n  zoom: true'
                    
                    # Reconstruir markdown
                    markdown_content = f"""---
markmap:
{yaml_content}
---

{remaining_content}"""
            
            markmap(markdown_content, height=600)
            
        except Exception as e:
            st.error(f"❌ Erro ao renderizar mapa mental: {str(e)}")
            st.code(markdown_content, language="markdown")
    else:
        st.error("❌ Erro ao gerar mapa mental. Tente novamente.")

def gerar_markdown_mapa_mental(pergunta: str, api_key: str, nivel: str) -> str:
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
        
        prompt = f"""
Você é um especialista em mapas mentais educacionais. Crie um mapa mental em formato Markdown sobre a pergunta da aluna Sther:

**Pergunta:** "{pergunta}"

**Configuração:** {config['conceitos']}, {config['profundidade']}, {config['detalhes']}

**INSTRUÇÕES IMPORTANTES:**
1. Responda APENAS com o código Markdown do mapa mental
2. SEMPRE comece com as configurações YAML frontmatter conforme exemplo
3. Use a estrutura hierárquica com # ## ### #### 
4. Inclua fórmulas matemáticas usando LaTeX: $formula$ ou $$formula$$
5. Use emojis relevantes para cada conceito
6. Mantenha foco na matemática do ENEM
7. Organize logicamente do geral para o específico

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

# 🎯 [CONCEITO PRINCIPAL]

## 📚 Fundamentos
### 🔢 Conceito 1
- Definição básica
- $formula_basica$

### 📐 Conceito 2
- Propriedades importantes
- $$formula_completa$$

## 🧮 Aplicações
### 🎯 Resolução de Problemas
- Método 1
- Método 2

### 📊 Exemplos ENEM
- Tipo de questão
- Estratégia de resolução

## 🔗 Conexões
### 🌐 Conceitos Relacionados
- Tópico A
- Tópico B
```

Gere o mapa mental:
"""
        
        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": "Você é um especialista em educação matemática e mapas mentais."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        markdown_content = response.choices[0].message.content.strip()
        
        # Limpar e validar o markdown
        markdown_content = limpar_markdown(markdown_content)
        
        # Se não conseguiu gerar via IA, criar estrutura básica
        if not markdown_content or len(markdown_content) < 100:
            markdown_content = criar_mapa_mental_basico(pergunta, nivel)
        
        return markdown_content
        
    except Exception as e:
        from encoding_utils import safe_str
        error_msg = safe_str(e)
        st.error(f"Erro na geração via IA: {error_msg}")
        return criar_mapa_mental_basico(pergunta, nivel)

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

def criar_mapa_mental_basico(pergunta: str, nivel: str) -> str:
    """Cria um mapa mental básico quando a IA falha"""
    
    # Detectar tópico principal
    topico = detectar_topico_matematico(pergunta)
    
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
- $formula = basica$

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
- $formula_1 = ax + b$

### 📐 Propriedades
- Características importantes
- $$formula_2 = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}$$

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
- $definicao = fundamental$

### 📐 Teoremas Principais
- Demonstrações importantes
- $$teorema = \\sum_{{i=1}}^n a_i$$

## 🧮 Métodos Avançados
### 🎯 Resolução Analítica
- Técnicas algébricas
- $$metodo_1 = \\int f(x) dx$$

### 📊 Resolução Gráfica
- Interpretação geométrica
- $$metodo_2 = \\lim_{{x \\to a}} f(x)$$

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

def detectar_topico_matematico(pergunta: str) -> str:
    """Detecta o tópico matemático principal da pergunta"""
    
    pergunta_lower = pergunta.lower()
    
    topicos = {
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
    }
    
    for topico, palavras_chave in topicos.items():
        if any(palavra in pergunta_lower for palavra in palavras_chave):
            return topico
    
    return 'Matemática'

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