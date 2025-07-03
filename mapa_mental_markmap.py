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
    """Retorna exemplo de fórmula básica explicativa para cada matéria"""
    examples = {
        'Matemática': '- Função linear: $f(x) = ax + b$ (onde "a" é coeficiente angular)',
        'Física': '- Velocidade média: $v = \\frac{\\Delta s}{\\Delta t}$ (distância/tempo)',
        'Química': '- Concentração molar: $C = \\frac{n}{V}$ (mol/litro)',
        'Biologia': '- Respiração: $C_6H_{12}O_6 + 6O_2 \\rightarrow 6CO_2 + 6H_2O + ATP$',
        'Geografia': '- Densidade demográfica = População total / Área territorial',
        'História': '- Periodização: Antecedentes → Evento → Consequências',
        'Língua Portuguesa': '- Estrutura frasal: Sujeito + Predicado + Complementos',
        'Redação': '- Estrutura: Introdução (tese) + Desenvolvimento + Conclusão'
    }
    return examples.get(subject, '- Princípio fundamental da área')

def get_advanced_formula_example(subject: str) -> str:
    """Retorna exemplo de fórmula avançada explicativa para cada matéria"""
    examples = {
        'Matemática': '- Fórmula de Bhaskara: $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$ (resolve equações 2º grau)',
        'Física': '- Segunda Lei de Newton: $F = ma$ (força = massa × aceleração)',
        'Química': '- Potencial hidrogeniônico: $pH = -\\log[H^+]$ (mede acidez)',
        'Biologia': '- Fotossíntese: $6CO_2 + 6H_2O \\xrightarrow{luz} C_6H_{12}O_6 + 6O_2$ (produz glicose)',
        'Geografia': '- Taxa de crescimento populacional: $TC = \\frac{P_f - P_i}{P_i} \\times 100$',
        'História': '- Análise multicausal: Fatores econômicos + sociais + políticos',
        'Língua Portuguesa': '- Análise sintática: Períodos compostos por coordenação/subordinação',
        'Redação': '- Estratégias argumentativas: Dados + exemplos + autoridade'
    }
    return examples.get(subject, '- Aplicação avançada do conceito')

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
    """Gera o conteúdo markdown do mapa mental usando IA com RAG"""
    
    try:
        # Detectar tópico específico da pergunta ANTES de gerar o prompt
        topico_especifico = extrair_topico_especifico(pergunta, current_subject)
        
        # INTEGRAÇÃO COM RAG - Buscar conteúdo real do Hugging Face
        rag_content = buscar_conteudo_rag(pergunta, current_subject, api_key)
        
        # Configurações por nível com diferenças REAIS
        nivel_config = {
            "Básico": {
                "conceitos": 3,
                "profundidade": 2,
                "detalhes": "definições básicas",
                "expansion": "initialExpandLevel: 1",
                "style": "conceitos fundamentais apenas"
            },
            "Intermediário": {
                "conceitos": 6,
                "profundidade": 3,
                "detalhes": "fórmulas e aplicações",
                "expansion": "initialExpandLevel: 2", 
                "style": "métodos e estratégias"
            },
            "Avançado": {
                "conceitos": 12,
                "profundidade": 4,
                "detalhes": "demonstrações e conexões profundas",
                "expansion": "initialExpandLevel: 3",
                "style": "análise completa e aplicações complexas"
            }
        }
        
        config = nivel_config.get(nivel, nivel_config["Intermediário"])
        
        client = Groq(api_key=api_key)
        
        # Prompt completamente reformulado para ser OBJETIVO e EXPLICATIVO
        prompt = f"""
Você é um especialista em educação para ENEM. Crie um mapa mental EXPLICATIVO sobre "{topico_especifico}" para uma estudante de 17 anos.

**PERGUNTA DA ESTUDANTE:** "{pergunta}"
**TÓPICO:** {topico_especifico}
**NÍVEL:** {nivel}

**CONTEÚDO RAG:**
{rag_content}

**REGRAS OBRIGATÓRIAS:**

1. **MÁXIMO 4 NÍVEIS HIERÁRQUICOS** (# → ## → ### → ####)
2. **SEM PERGUNTAS** - apenas EXPLICAÇÕES diretas
3. **SEM MENÇÕES VAGAS** - explique sempre os conceitos
4. **LINGUAGEM CLARA** para estudante de 17 anos
5. **INFORMAÇÕES ESPECÍFICAS** baseadas no RAG

**ESTRUTURA OBRIGATÓRIA:**

```
---
markmap:
  initialExpandLevel: 2
  maxWidth: 300
---

# 🎯 {topico_especifico}

## 📚 Definição
- [Explicação clara do que é o conceito]
- [Por que é importante no ENEM]

## 🔍 Características Principais  
- [Característica 1 explicada]
- [Característica 2 explicada]
- [Fórmula se aplicável: $formula$]

## 🎯 Como Funciona
### [Processo/Etapa 1]
- [Explicação detalhada]
### [Processo/Etapa 2] 
- [Explicação detalhada]

## 💡 Aplicações no ENEM
- [Tipo de questão 1 + exemplo]
- [Tipo de questão 2 + exemplo]
- [Dica específica para resolver]
```

**EXEMPLO DO QUE FAZER:**
✅ "## Respiração Celular
- Processo que transforma glicose em energia (ATP)
- Ocorre nas mitocôndrias das células
- Fórmula: $C_6H_{12}O_6 + 6O_2 → 6CO_2 + 6H_2O + ATP$"

**EXEMPLO DO QUE NÃO FAZER:**
❌ "## O que é respiração celular?"
❌ "## Contexto histórico" (sem explicar qual contexto)

Agora crie o mapa explicativo:
"""
        
        # Usar modelo mais recente e estável
        response = client.chat.completions.create(
            model="llama-3.2-90b-text-preview",
            messages=[
                {"role": "system", "content": f"{get_subject_system_prompt(current_subject)} Você está criando um mapa mental explicativo para Sther, de 17 anos, que vai prestar ENEM. Seja preciso e direcionado ao tópico da pergunta."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.1   # Muito baixo para máxima consistência e foco
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
    """Extrai o tópico específico da pergunta com detecção avançada"""
    pergunta_lower = pergunta.lower()
    
    # MATEMÁTICA - Tópicos específicos
    if current_subject == 'Matemática':
        if any(palavra in pergunta_lower for palavra in ['matriz', 'matrizes', 'determinante']):
            return 'Matrizes e Determinantes'
        elif any(palavra in pergunta_lower for palavra in ['segundo grau', 'bhaskara', 'quadrática']):
            return 'Equações do 2º Grau'
        elif any(palavra in pergunta_lower for palavra in ['trigonometria', 'seno', 'cosseno', 'tangente']):
            return 'Trigonometria'
        elif any(palavra in pergunta_lower for palavra in ['função', 'funcao', 'linear', 'afim']):
            return 'Funções'
        elif any(palavra in pergunta_lower for palavra in ['logaritmo', 'log', 'exponencial']):
            return 'Logaritmos e Exponenciais'
        elif any(palavra in pergunta_lower for palavra in ['geometria', 'área', 'volume', 'perímetro']):
            return 'Geometria'
        elif any(palavra in pergunta_lower for palavra in ['probabilidade', 'estatística', 'média']):
            return 'Estatística e Probabilidade'
    
    # FÍSICA - Tópicos específicos
    elif current_subject == 'Física':
        if any(palavra in pergunta_lower for palavra in ['força', 'newton', 'dinâmica', 'dinamica']):
            return 'Dinâmica'
        elif any(palavra in pergunta_lower for palavra in ['termodinâmica', 'termodinamica', 'calor', 'temperatura']):
            return 'Termodinâmica'
        elif any(palavra in pergunta_lower for palavra in ['eletricidade', 'circuito', 'corrente', 'voltagem']):
            return 'Eletricidade'
        elif any(palavra in pergunta_lower for palavra in ['onda', 'ondas', 'som', 'luz']):
            return 'Ondulatória'
        elif any(palavra in pergunta_lower for palavra in ['velocidade', 'aceleração', 'movimento']):
            return 'Cinemática'
        elif any(palavra in pergunta_lower for palavra in ['energia', 'trabalho', 'potência']):
            return 'Energia e Trabalho'
    
    # QUÍMICA - Tópicos específicos
    elif current_subject == 'Química':
        if any(palavra in pergunta_lower for palavra in ['átomo', 'atomo', 'estrutura atômica']):
            return 'Estrutura Atômica'
        elif any(palavra in pergunta_lower for palavra in ['ligação', 'ligacao', 'iônica', 'covalente']):
            return 'Ligações Químicas'
        elif any(palavra in pergunta_lower for palavra in ['reação', 'reacao', 'equação química']):
            return 'Reações Químicas'
        elif any(palavra in pergunta_lower for palavra in ['solução', 'soluçao', 'concentração']):
            return 'Soluções'
        elif any(palavra in pergunta_lower for palavra in ['ácido', 'base', 'ph']):
            return 'Ácidos e Bases'
        elif any(palavra in pergunta_lower for palavra in ['orgânica', 'organica', 'carbono']):
            return 'Química Orgânica'
    
    # BIOLOGIA - Tópicos específicos
    elif current_subject == 'Biologia':
        if any(palavra in pergunta_lower for palavra in ['célula', 'celula', 'membrana']):
            return 'Citologia'
        elif any(palavra in pergunta_lower for palavra in ['dna', 'gene', 'genética', 'genetica']):
            return 'Genética'
        elif any(palavra in pergunta_lower for palavra in ['fotossíntese', 'fotossintese', 'respiração']):
            return 'Metabolismo Celular'
        elif any(palavra in pergunta_lower for palavra in ['evolução', 'evoluçao', 'darwin']):
            return 'Evolução'
        elif any(palavra in pergunta_lower for palavra in ['ecologia', 'ecosystem', 'cadeia alimentar']):
            return 'Ecologia'
        elif any(palavra in pergunta_lower for palavra in ['corpo humano', 'sistema', 'anatomia']):
            return 'Anatomia e Fisiologia'
    
    # GEOGRAFIA - Tópicos específicos
    elif current_subject == 'Geografia':
        if any(palavra in pergunta_lower for palavra in ['clima', 'temperatura', 'chuva']):
            return 'Climatologia'
        elif any(palavra in pergunta_lower for palavra in ['relevo', 'montanha', 'planície']):
            return 'Geomorfologia'
        elif any(palavra in pergunta_lower for palavra in ['população', 'demografia', 'migração']):
            return 'Geografia da População'
        elif any(palavra in pergunta_lower for palavra in ['urbano', 'cidade', 'metrópole']):
            return 'Geografia Urbana'
        elif any(palavra in pergunta_lower for palavra in ['brasil', 'região', 'território']):
            return 'Geografia do Brasil'
    
    # HISTÓRIA - Tópicos específicos
    elif current_subject == 'História':
        if any(palavra in pergunta_lower for palavra in ['guerra fria', 'capitalismo', 'socialismo']):
            return 'Guerra Fria'
        elif any(palavra in pergunta_lower for palavra in ['revolução francesa', 'iluminismo']):
            return 'Revolução Francesa'
        elif any(palavra in pergunta_lower for palavra in ['brasil colônia', 'colonização']):
            return 'Brasil Colonial'
        elif any(palavra in pergunta_lower for palavra in ['primeira guerra', 'segunda guerra']):
            return 'Guerras Mundiais'
        elif any(palavra in pergunta_lower for palavra in ['república', 'ditadura', 'democracia']):
            return 'História Política do Brasil'
    
    # LÍNGUA PORTUGUESA - Tópicos específicos
    elif current_subject == 'Língua Portuguesa':
        if any(palavra in pergunta_lower for palavra in ['figura de linguagem', 'metáfora', 'metonímia']):
            return 'Figuras de Linguagem'
        elif any(palavra in pergunta_lower for palavra in ['sintaxe', 'sujeito', 'predicado']):
            return 'Sintaxe'
        elif any(palavra in pergunta_lower for palavra in ['interpretação', 'texto', 'leitura']):
            return 'Interpretação de Textos'
        elif any(palavra in pergunta_lower for palavra in ['literatura', 'modernismo', 'romantismo']):
            return 'Literatura Brasileira'
    
    # Fallback: extrair palavras-chave da pergunta
    palavras = pergunta.split()
    if len(palavras) > 1:
        # Pegar palavras importantes (substantivos geralmente)
        palavras_importantes = []
        for palavra in palavras[:3]:  # Primeiras 3 palavras
            palavra_limpa = palavra.lower().strip('.,?!')
            if len(palavra_limpa) > 3 and palavra_limpa not in ['como', 'qual', 'onde', 'quando', 'quem']:
                palavras_importantes.append(palavra_limpa.title())
        
        if palavras_importantes:
            return ' '.join(palavras_importantes[:2])
    
    return current_subject

def buscar_conteudo_rag(pergunta: str, current_subject: str, api_key: str) -> str:
    """Busca conteúdo específico usando o sistema RAG dos professores"""
    try:
        # Importar o sistema RAG apropriado baseado na matéria
        rag_system = None
        
        if current_subject == 'Matemática':
            from local_math_rag import get_local_math_rag_instance
            rag_system = get_local_math_rag_instance()
        elif current_subject == 'Física':
            from local_physics_rag import LocalphysicsRAG
            rag_system = LocalphysicsRAG()
        elif current_subject == 'Química':
            from local_chemistry_rag import LocalChemistryRAG
            rag_system = LocalChemistryRAG()
        elif current_subject == 'Biologia':
            from local_biology_rag import LocalBiologyRAG
            rag_system = LocalBiologyRAG()
        elif current_subject == 'Geografia':
            from local_geography_rag import LocalGeographyRAG
            rag_system = LocalGeographyRAG()
        elif current_subject == 'História':
            from local_history_rag import LocalHistoryRAG
            rag_system = LocalHistoryRAG()
        elif current_subject == 'Língua Portuguesa':
            from local_portuguese_rag import LocalPortugueseRAG
            rag_system = LocalPortugueseRAG()
        
        if rag_system:
            # Inicializar o sistema RAG
            success = rag_system.initialize(api_key)
            if success:
                # Buscar conteúdo relevante
                docs = rag_system.search_relevant_content(pergunta, k=3)
                if docs:
                    # Concatenar conteúdo dos documentos encontrados
                    conteudo = "\n\n".join([doc.page_content[:500] for doc in docs])
                    return f"CONTEÚDO ESPECÍFICO ENCONTRADO:\n{conteudo}"
        
        # Fallback se não conseguir usar RAG
        return f"TÓPICO: {extrair_topico_especifico(pergunta, current_subject)} da matéria {current_subject}"
        
    except Exception as e:
        # Fallback em caso de erro
        return f"TÓPICO: {extrair_topico_especifico(pergunta, current_subject)} da matéria {current_subject}"

def validar_especificidade_mapa(markdown_content: str, topico_especifico: str) -> bool:
    """Valida se o mapa mental é específico ao tópico identificado"""
    if not markdown_content or not topico_especifico:
        return False
    return topico_especifico.lower() in markdown_content.lower()

def criar_mapa_mental_especifico(pergunta: str, topico_especifico: str, nivel: str, current_subject: str) -> str:
    """Cria um mapa mental específico e explicativo para o tópico identificado"""
    
    # Emojis por matéria
    emoji_materia = {
        'Matemática': '🧮', 'Física': '⚡', 'Química': '⚗️', 'Biologia': '🧬',
        'Geografia': '🌍', 'História': '🏛️', 'Língua Portuguesa': '📚', 'Redação': '✍️'
    }
    emoji = emoji_materia.get(current_subject, '📚')
    
    # Configurar níveis com conteúdo específico para FOTOSSÍNTESE como exemplo
    if "fotossíntese" in topico_especifico.lower() or "fotossintese" in pergunta.lower():
        if nivel == "Básico":
            conceitos_basicos = f"""
# {emoji} Fotossíntese

## 📚 Definição
- Processo que transforma luz solar em energia química
- Plantas produzem glicose usando CO₂ e água
- Libera oxigênio como produto secundário

## 🔍 Onde Acontece
- Ocorre nas folhas das plantas
- Estrutura: cloroplastos (organelas verdes)
- Pigmento: clorofila capta a luz solar

## 🎯 Importância
- Produz oxigênio que respiramos
- Base da cadeia alimentar
- Remove CO₂ da atmosfera
"""
        elif nivel == "Intermediário":
            conceitos_basicos = f"""
# {emoji} Fotossíntese

## 📚 Definição Completa
- Processo anabólico que converte energia luminosa em química
- Transforma matéria inorgânica em orgânica
- Equação: $6CO_2 + 6H_2O \\rightarrow C_6H_{12}O_6 + 6O_2$

## 🔍 Estruturas Envolvidas
### Cloroplastos
- Organelas das células vegetais
- Contêm clorofila (pigmento verde)
- Tilacoide: onde ocorre a fase clara
### Estroma
- Fluido interno do cloroplasto
- Local da fase escura (Ciclo de Calvin)

## ⚡ Duas Etapas Principais
### Fase Clara (Fotoquímica)
- Ocorre nos tilacoides
- Capta energia solar
- Produz ATP e NADPH
### Fase Escura (Ciclo de Calvin)
- Ocorre no estroma
- Fixa CO₂ em glicose
- Não depende diretamente da luz

## 💡 Aplicações no ENEM
- Questões sobre equação química
- Relação com respiração celular
- Impacto ambiental e aquecimento global
"""
        else:  # Avançado
            conceitos_basicos = f"""
# {emoji} Fotossíntese

## 📚 Definição Científica
- Processo anabólico endergônico
- Converte energia radiante em energia química
- Equação global: $6CO_2 + 6H_2O \\xrightarrow{luz} C_6H_{12}O_6 + 6O_2$
- ΔG positivo (requer energia)

## 🔬 Aspectos Bioquímicos
### Fase Fotoquímica
- Fotossistemas I e II
- Transporte de elétrons
- Fotofosforilação: $ADP + Pi \\rightarrow ATP$
- Fotólise da água: $2H_2O \\rightarrow 4H^+ + 4e^- + O_2$
### Ciclo de Calvin-Benson
- Fixação: CO₂ + RuBP → compostos de 3C
- Redução: NADPH reduz 3-fosfoglicerato
- Regeneração: RuBP é regenerada

## 🌍 Tipos de Fotossíntese
### Plantas C3
- Fixam CO₂ diretamente no Ciclo de Calvin
- Maioria das plantas (arroz, trigo)
### Plantas C4
- Primeiro fixam CO₂ em compostos de 4 carbonos
- Adaptação a climas quentes (milho, cana)
### Plantas CAM
- Abrem estômatos à noite
- Adaptação a climas áridos (cactos)

## 💡 Conexões ENEM
- Relação inversa com respiração celular
- Impacto das mudanças climáticas
- Eficiência energética em diferentes biomas
- Biotecnologia e plantas transgênicas
"""
    
    # Template genérico para outros tópicos
    else:
        conceitos_basicos = criar_template_generico(topico_especifico, nivel, current_subject, emoji)
    
    # Configurar expansão baseada no nível (máximo 4 níveis)
    expansion_level = 1 if nivel == "Básico" else 2 if nivel == "Intermediário" else 3
    
    return f"""---
markmap:
  pan: true
  zoom: true
  initialExpandLevel: {expansion_level}
  maxWidth: 300
  colorFreezeLevel: 2
  duration: 500
  spacingHorizontal: 80
  spacingVertical: 5
---

{conceitos_basicos}
"""

def criar_template_generico(topico_especifico: str, nivel: str, current_subject: str, emoji: str) -> str:
    """Cria template genérico explicativo para qualquer tópico"""
    
    # Conteúdo específico por matéria
    definicoes_especificas = {
        'Matemática': {
            'Equações do 2º Grau': 'Equações da forma ax² + bx + c = 0, onde a ≠ 0',
            'Trigonometria': 'Estudo das relações entre ângulos e lados de triângulos',
            'Funções': 'Relação entre dois conjuntos onde cada elemento tem uma imagem única',
            'Logaritmos': 'Operação inversa da potenciação, usado para resolver equações exponenciais'
        },
        'Física': {
            'Cinemática': 'Estudo do movimento sem considerar suas causas',
            'Dinâmica': 'Estudo das forças que causam o movimento',
            'Termodinâmica': 'Estudo das relações entre calor, trabalho e energia',
            'Eletricidade': 'Estudo dos fenômenos relacionados a cargas elétricas'
        },
        'Química': {
            'Ligações Químicas': 'Forças que mantêm átomos unidos formando compostos',
            'Reações Químicas': 'Processos de transformação de substâncias químicas',
            'Soluções': 'Misturas homogêneas de duas ou mais substâncias',
            'Ácidos e Bases': 'Substâncias que doam ou recebem prótons (H⁺)'
        },
        'Biologia': {
            'Respiração Celular': 'Processo que transforma glicose em energia (ATP) nas células',
            'Fotossíntese': 'Processo que converte luz solar em energia química nas plantas',
            'Genética': 'Estudo da hereditariedade e variação dos seres vivos',
            'Ecologia': 'Estudo das relações entre seres vivos e o ambiente'
        }
    }
    
    # Buscar definição específica ou usar genérica
    definicao = ""
    if current_subject in definicoes_especificas:
        for topico, desc in definicoes_especificas[current_subject].items():
            if topico.lower() in topico_especifico.lower():
                definicao = desc
                break
    
    if not definicao:
        definicao = f"Conceito fundamental de {current_subject} relacionado a {topico_especifico.lower()}"
    
    if nivel == "Básico":
        return f"""
# {emoji} {topico_especifico}

## 📚 Definição
- {definicao}
- Conceito importante para o ENEM
- {get_formula_example(current_subject)}

## 🔍 Características Principais
- Propriedade fundamental do conceito
- Aplicação prática básica
- Exemplo simples de uso

## 💡 Como Identificar no ENEM
- Palavras-chave típicas nas questões
- Sinais que indicam esse tema
- Estratégia básica de resolução
"""
    elif nivel == "Intermediário":
        return f"""
# {emoji} {topico_especifico}

## 📚 Definição Completa
- {definicao}
- Importância no contexto da matéria
- Relação com outros conceitos

## 🔍 Como Funciona
### Processo Principal
- Etapa 1: descrição detalhada
- Etapa 2: desenvolvimento
- {get_formula_example(current_subject)}
### Aplicações Práticas
- Uso em situações reais
- Exemplos do cotidiano

## 🎯 Estratégias de Resolução
- Método 1: abordagem sistemática
- Método 2: técnica alternativa
- Dicas para evitar erros comuns

## 💡 No ENEM
- Tipos de questão mais frequentes
- Competências avaliadas
- Tempo médio de resolução
"""
    else:  # Avançado
        return f"""
# {emoji} {topico_especifico}

## 📚 Fundamento Teórico
- {definicao}
- Base científica do conceito
- Desenvolvimento histórico relevante
- {get_advanced_formula_example(current_subject)}

## 🔬 Análise Detalhada
### Aspectos Fundamentais
- Princípio 1: explicação aprofundada
- Princípio 2: relações complexas
- Demonstração matemática quando aplicável
### Variações e Casos Especiais
- Situação específica 1
- Situação específica 2
- Exceções importantes

## 🎯 Aplicações Avançadas
### Resolução Complexa
- Técnica especializada 1
- Técnica especializada 2
- Análise de casos limites
### Interdisciplinaridade
- Conexão com outras matérias
- Aplicações tecnológicas
- Relevância científica atual

## 💡 Domínio Completo ENEM
- Questões de alta complexidade
- Análise crítica e interpretação
- Estratégias de otimização de tempo
- Armadilhas comuns e como evitá-las
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