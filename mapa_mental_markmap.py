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
**AMBIENTE:** Streamlit Cloud (usar conhecimento direto)

**CONTEÚDO ESPECÍFICO:**
{rag_content}

**REGRAS OBRIGATÓRIAS:**

1. **MÁXIMO 4 NÍVEIS HIERÁRQUICOS** (# → ## → ### → ####)
2. **SEM PERGUNTAS** - apenas EXPLICAÇÕES diretas
3. **SEM MENÇÕES VAGAS** - explique sempre os conceitos
4. **LINGUAGEM CLARA** para estudante de 17 anos
5. **INFORMAÇÕES ESPECÍFICAS** baseadas no seu conhecimento especializado

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

**FOCO ESPECIAL:**
Para FOTOSSÍNTESE: Explique as duas fases (clara e escura), cloroplastos, equação química completa.
Para outros tópicos: Use seu conhecimento especializado em {current_subject}.

**EXEMPLO DO QUE FAZER:**
✅ "## Respiração Celular
- Processo que transforma glicose em energia (ATP)
- Ocorre nas mitocôndrias das células
- Fórmula: $C_6H_{12}O_6 + 6O_2 → 6CO_2 + 6H_2O + ATP$"

**EXEMPLO DO QUE NÃO FAZER:**
❌ "## O que é respiração celular?"
❌ "## Contexto histórico" (sem explicar qual contexto)

Agora crie o mapa explicativo focado especificamente em {topico_especifico}:
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
        
        # Não mostrar erros de importação FAISS no Streamlit Cloud
        if "faiss" in error_msg.lower() or "no such file" in error_msg.lower():
            st.info("🌐 Usando modo cloud - gerando mapa mental específico...")
        elif "decommissioned" in error_msg or "model_decommissioned" in error_msg:
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
    """Extrai o tópico específico da pergunta com detecção avançada para TODAS as matérias do ENEM"""
    pergunta_lower = pergunta.lower()
    
    # MATEMÁTICA - Cobertura completa dos tópicos ENEM
    if current_subject == 'Matemática':
        # Álgebra
        if any(palavra in pergunta_lower for palavra in ['equação', 'equacao', 'primeiro grau', 'linear']):
            return 'Equações do 1º Grau'
        elif any(palavra in pergunta_lower for palavra in ['segundo grau', 'bhaskara', 'quadrática', 'parábola']):
            return 'Equações do 2º Grau'
        elif any(palavra in pergunta_lower for palavra in ['sistema', 'linear', 'substituição', 'eliminação']):
            return 'Sistemas de Equações'
        elif any(palavra in pergunta_lower for palavra in ['inequação', 'inequacao', 'desigualdade']):
            return 'Inequações'
        
        # Funções
        elif any(palavra in pergunta_lower for palavra in ['função', 'funcao', 'domínio', 'imagem']):
            return 'Funções'
        elif any(palavra in pergunta_lower for palavra in ['afim', 'linear', 'coeficiente angular']):
            return 'Função Afim'
        elif any(palavra in pergunta_lower for palavra in ['quadrática', 'parabola', 'vértice']):
            return 'Função Quadrática'
        elif any(palavra in pergunta_lower for palavra in ['exponencial', 'crescimento', 'decaimento']):
            return 'Função Exponencial'
        elif any(palavra in pergunta_lower for palavra in ['logaritmo', 'log', 'logarítmica']):
            return 'Logaritmos'
        
        # Trigonometria
        elif any(palavra in pergunta_lower for palavra in ['trigonometria', 'seno', 'cosseno', 'tangente']):
            return 'Trigonometria'
        elif any(palavra in pergunta_lower for palavra in ['círculo trigonométrico', 'radianos', 'graus']):
            return 'Círculo Trigonométrico'
        
        # Geometria
        elif any(palavra in pergunta_lower for palavra in ['área', 'perímetro', 'geometria plana']):
            return 'Geometria Plana'
        elif any(palavra in pergunta_lower for palavra in ['volume', 'prisma', 'pirâmide', 'cilindro', 'cone', 'esfera']):
            return 'Geometria Espacial'
        elif any(palavra in pergunta_lower for palavra in ['triângulo', 'teorema de pitágoras', 'pitagoras']):
            return 'Triângulos'
        elif any(palavra in pergunta_lower for palavra in ['circunferência', 'círculo', 'pi']):
            return 'Círculo e Circunferência'
        
        # Álgebra Linear
        elif any(palavra in pergunta_lower for palavra in ['matriz', 'matrizes', 'determinante']):
            return 'Matrizes e Determinantes'
        
        # Estatística
        elif any(palavra in pergunta_lower for palavra in ['média', 'mediana', 'moda', 'estatística']):
            return 'Estatística'
        elif any(palavra in pergunta_lower for palavra in ['probabilidade', 'chance', 'evento']):
            return 'Probabilidade'
        elif any(palavra in pergunta_lower for palavra in ['combinação', 'arranjo', 'permutação']):
            return 'Análise Combinatória'
        
        # Progressões
        elif any(palavra in pergunta_lower for palavra in ['progressão aritmética', 'pa']):
            return 'Progressão Aritmética'
        elif any(palavra in pergunta_lower for palavra in ['progressão geométrica', 'pg']):
            return 'Progressão Geométrica'
    
    # FÍSICA - Cobertura completa dos tópicos ENEM
    elif current_subject == 'Física':
        # Mecânica
        if any(palavra in pergunta_lower for palavra in ['velocidade', 'aceleração', 'movimento uniforme']):
            return 'Cinemática'
        elif any(palavra in pergunta_lower for palavra in ['força', 'newton', 'dinâmica', 'leis de newton']):
            return 'Dinâmica'
        elif any(palavra in pergunta_lower for palavra in ['trabalho', 'energia', 'potência', 'conservação']):
            return 'Energia e Trabalho'
        elif any(palavra in pergunta_lower for palavra in ['impulso', 'quantidade de movimento', 'colisão']):
            return 'Impulso e Quantidade de Movimento'
        elif any(palavra in pergunta_lower for palavra in ['gravitação', 'gravidade', 'kepler']):
            return 'Gravitação Universal'
        elif any(palavra in pergunta_lower for palavra in ['estática', 'equilíbrio', 'alavanca']):
            return 'Estática'
        
        # Termologia
        elif any(palavra in pergunta_lower for palavra in ['temperatura', 'calor', 'termômetro']):
            return 'Temperatura e Calor'
        elif any(palavra in pergunta_lower for palavra in ['dilatação', 'expansão térmica']):
            return 'Dilatação Térmica'
        elif any(palavra in pergunta_lower for palavra in ['calorimetria', 'capacidade térmica']):
            return 'Calorimetria'
        elif any(palavra in pergunta_lower for palavra in ['termodinâmica', 'máquina térmica', 'ciclo']):
            return 'Termodinâmica'
        elif any(palavra in pergunta_lower for palavra in ['mudança de estado', 'fusão', 'vaporização']):
            return 'Mudanças de Estado'
        
        # Óptica
        elif any(palavra in pergunta_lower for palavra in ['luz', 'reflexão', 'refração']):
            return 'Óptica Geométrica'
        elif any(palavra in pergunta_lower for palavra in ['espelho', 'lente', 'imagem']):
            return 'Espelhos e Lentes'
        
        # Ondulatória
        elif any(palavra in pergunta_lower for palavra in ['onda', 'ondas', 'frequência', 'amplitude']):
            return 'Ondulatória'
        elif any(palavra in pergunta_lower for palavra in ['som', 'acústica', 'eco']):
            return 'Acústica'
        
        # Eletricidade
        elif any(palavra in pergunta_lower for palavra in ['corrente', 'tensão', 'resistência', 'ohm']):
            return 'Eletricidade Básica'
        elif any(palavra in pergunta_lower for palavra in ['circuito', 'lei de ohm', 'resistor']):
            return 'Circuitos Elétricos'
        elif any(palavra in pergunta_lower for palavra in ['campo elétrico', 'carga', 'coulomb']):
            return 'Campo Elétrico'
        elif any(palavra in pergunta_lower for palavra in ['campo magnético', 'ímã', 'magnetismo']):
            return 'Magnetismo'
        elif any(palavra in pergunta_lower for palavra in ['indução', 'gerador', 'motor']):
            return 'Indução Eletromagnética'
        
        # Física Moderna
        elif any(palavra in pergunta_lower for palavra in ['relatividade', 'einstein', 'quântica']):
            return 'Física Moderna'
    
    # QUÍMICA - Cobertura completa dos tópicos ENEM
    elif current_subject == 'Química':
        # Química Geral
        if any(palavra in pergunta_lower for palavra in ['átomo', 'atomo', 'próton', 'nêutron', 'elétron']):
            return 'Estrutura Atômica'
        elif any(palavra in pergunta_lower for palavra in ['tabela periódica', 'elemento', 'propriedades periódicas']):
            return 'Tabela Periódica'
        elif any(palavra in pergunta_lower for palavra in ['ligação', 'ligacao', 'iônica', 'covalente', 'metálica']):
            return 'Ligações Químicas'
        elif any(palavra in pergunta_lower for palavra in ['geometria molecular', 'hibridização', 'polaridade']):
            return 'Geometria Molecular'
        
        # Físico-Química
        elif any(palavra in pergunta_lower for palavra in ['mol', 'massa molar', 'avogadro']):
            return 'Quantidade de Matéria'
        elif any(palavra in pergunta_lower for palavra in ['solução', 'soluçao', 'concentração', 'molaridade']):
            return 'Soluções'
        elif any(palavra in pergunta_lower for palavra in ['termoquímica', 'entalpia', 'calor de reação']):
            return 'Termoquímica'
        elif any(palavra in pergunta_lower for palavra in ['cinética', 'velocidade de reação', 'catalisador']):
            return 'Cinética Química'
        elif any(palavra in pergunta_lower for palavra in ['equilíbrio', 'equilibrio', 'constante', 'le chatelier']):
            return 'Equilíbrio Químico'
        elif any(palavra in pergunta_lower for palavra in ['eletroquímica', 'pilha', 'eletrólise']):
            return 'Eletroquímica'
        
        # Química Inorgânica
        elif any(palavra in pergunta_lower for palavra in ['ácido', 'base', 'ph', 'neutralização']):
            return 'Ácidos e Bases'
        elif any(palavra in pergunta_lower for palavra in ['sal', 'óxido', 'hidreto']):
            return 'Funções Inorgânicas'
        elif any(palavra in pergunta_lower for palavra in ['reação', 'reacao', 'balanceamento', 'estequiometria']):
            return 'Reações Químicas'
        
        # Química Orgânica
        elif any(palavra in pergunta_lower for palavra in ['carbono', 'orgânica', 'organica', 'cadeia carbônica']):
            return 'Química Orgânica'
        elif any(palavra in pergunta_lower for palavra in ['hidrocarboneto', 'alcano', 'alceno', 'alcino']):
            return 'Hidrocarbonetos'
        elif any(palavra in pergunta_lower for palavra in ['álcool', 'aldeído', 'cetona', 'ácido carboxílico']):
            return 'Funções Orgânicas'
        elif any(palavra in pergunta_lower for palavra in ['isomeria', 'isômero']):
            return 'Isomeria'
        elif any(palavra in pergunta_lower for palavra in ['polímero', 'plástico', 'polimerização']):
            return 'Polímeros'
        
        # Bioquímica
        elif any(palavra in pergunta_lower for palavra in ['proteína', 'aminoácido', 'enzima']):
            return 'Bioquímica'
    
    # BIOLOGIA - Cobertura completa dos tópicos ENEM
    elif current_subject == 'Biologia':
        # Citologia
        if any(palavra in pergunta_lower for palavra in ['célula', 'celula', 'membrana', 'organela']):
            return 'Citologia'
        elif any(palavra in pergunta_lower for palavra in ['mitose', 'meiose', 'divisão celular']):
            return 'Divisão Celular'
        elif any(palavra in pergunta_lower for palavra in ['fotossíntese', 'fotossintese', 'cloroplasto']):
            return 'Fotossíntese'
        elif any(palavra in pergunta_lower for palavra in ['respiração celular', 'mitocôndria', 'atp']):
            return 'Respiração Celular'
        
        # Genética
        elif any(palavra in pergunta_lower for palavra in ['dna', 'rna', 'gene', 'cromossomo']):
            return 'Genética Molecular'
        elif any(palavra in pergunta_lower for palavra in ['mendel', 'dominante', 'recessivo', 'hereditariedade']):
            return 'Genética Clássica'
        elif any(palavra in pergunta_lower for palavra in ['mutação', 'evolução', 'seleção natural']):
            return 'Evolução'
        
        # Fisiologia
        elif any(palavra in pergunta_lower for palavra in ['sistema nervoso', 'neurônio', 'impulso']):
            return 'Sistema Nervoso'
        elif any(palavra in pergunta_lower for palavra in ['sistema circulatório', 'coração', 'sangue']):
            return 'Sistema Circulatório'
        elif any(palavra in pergunta_lower for palavra in ['sistema digestório', 'digestão', 'enzima digestiva']):
            return 'Sistema Digestório'
        elif any(palavra in pergunta_lower for palavra in ['sistema respiratório', 'pulmão', 'respiração']):
            return 'Sistema Respiratório'
        elif any(palavra in pergunta_lower for palavra in ['sistema reprodutor', 'reprodução', 'hormônio']):
            return 'Sistema Reprodutor'
        
        # Ecologia
        elif any(palavra in pergunta_lower for palavra in ['ecologia', 'ecosystem', 'cadeia alimentar', 'teia']):
            return 'Ecologia'
        elif any(palavra in pergunta_lower for palavra in ['população', 'comunidade', 'bioma']):
            return 'Ecossistemas'
        elif any(palavra in pergunta_lower for palavra in ['poluição', 'aquecimento global', 'sustentabilidade']):
            return 'Impactos Ambientais'
        
        # Botânica
        elif any(palavra in pergunta_lower for palavra in ['planta', 'flor', 'fruto', 'semente']):
            return 'Botânica'
        
        # Zoologia
        elif any(palavra in pergunta_lower for palavra in ['animal', 'vertebrado', 'invertebrado']):
            return 'Zoologia'
        
        # Microbiologia
        elif any(palavra in pergunta_lower for palavra in ['bactéria', 'vírus', 'fungo', 'protozoário']):
            return 'Microbiologia'
    
    # GEOGRAFIA - Cobertura completa dos tópicos ENEM
    elif current_subject == 'Geografia':
        # Geografia Física
        if any(palavra in pergunta_lower for palavra in ['clima', 'temperatura', 'chuva', 'precipitação']):
            return 'Climatologia'
        elif any(palavra in pergunta_lower for palavra in ['relevo', 'montanha', 'planície', 'planalto']):
            return 'Geomorfologia'
        elif any(palavra in pergunta_lower for palavra in ['solo', 'erosão', 'intemperismo']):
            return 'Pedologia'
        elif any(palavra in pergunta_lower for palavra in ['rio', 'bacia hidrográfica', 'água']):
            return 'Hidrografia'
        elif any(palavra in pergunta_lower for palavra in ['vegetação', 'bioma', 'floresta', 'cerrado']):
            return 'Biogeografia'
        
        # Geografia Humana
        elif any(palavra in pergunta_lower for palavra in ['população', 'demografia', 'migração', 'natalidade']):
            return 'Geografia da População'
        elif any(palavra in pergunta_lower for palavra in ['cidade', 'urbano', 'metrópole', 'urbanização']):
            return 'Geografia Urbana'
        elif any(palavra in pergunta_lower for palavra in ['agricultura', 'rural', 'agropecuária']):
            return 'Geografia Agrária'
        elif any(palavra in pergunta_lower for palavra in ['indústria', 'industrial', 'produção']):
            return 'Geografia Industrial'
        
        # Geografia Regional
        elif any(palavra in pergunta_lower for palavra in ['brasil', 'região', 'nordeste', 'sudeste']):
            return 'Geografia do Brasil'
        elif any(palavra in pergunta_lower for palavra in ['globalização', 'mundial', 'internacional']):
            return 'Geografia Mundial'
        
        # Cartografia
        elif any(palavra in pergunta_lower for palavra in ['mapa', 'escala', 'coordenada', 'gps']):
            return 'Cartografia'
        
        # Geopolítica
        elif any(palavra in pergunta_lower for palavra in ['fronteira', 'território', 'geopolítica']):
            return 'Geopolítica'
    
    # HISTÓRIA - Cobertura completa dos tópicos ENEM
    elif current_subject == 'História':
        # História Antiga
        if any(palavra in pergunta_lower for palavra in ['grécia', 'roma', 'antiguidade']):
            return 'História Antiga'
        
        # História Medieval
        elif any(palavra in pergunta_lower for palavra in ['idade média', 'feudalismo', 'medieval']):
            return 'Idade Média'
        
        # História Moderna
        elif any(palavra in pergunta_lower for palavra in ['renascimento', 'reforma protestante', 'absolutismo']):
            return 'História Moderna'
        elif any(palavra in pergunta_lower for palavra in ['grandes navegações', 'descobrimento', 'colonização']):
            return 'Grandes Navegações'
        elif any(palavra in pergunta_lower for palavra in ['revolução francesa', 'iluminismo', 'robespierre']):
            return 'Revolução Francesa'
        elif any(palavra in pergunta_lower for palavra in ['revolução industrial', 'máquina a vapor']):
            return 'Revolução Industrial'
        
        # História Contemporânea
        elif any(palavra in pergunta_lower for palavra in ['primeira guerra', 'guerra mundial']):
            return 'Primeira Guerra Mundial'
        elif any(palavra in pergunta_lower for palavra in ['segunda guerra', 'nazismo', 'hitler']):
            return 'Segunda Guerra Mundial'
        elif any(palavra in pergunta_lower for palavra in ['guerra fria', 'capitalismo', 'socialismo', 'urss']):
            return 'Guerra Fria'
        
        # História do Brasil
        elif any(palavra in pergunta_lower for palavra in ['brasil colônia', 'colonial', 'capitanias']):
            return 'Brasil Colonial'
        elif any(palavra in pergunta_lower for palavra in ['independência', 'dom pedro', '1822']):
            return 'Independência do Brasil'
        elif any(palavra in pergunta_lower for palavra in ['império', 'dom pedro ii', 'monarquia']):
            return 'Brasil Império'
        elif any(palavra in pergunta_lower for palavra in ['república', 'proclamação da república']):
            return 'República Brasileira'
        elif any(palavra in pergunta_lower for palavra in ['getúlio vargas', 'era vargas', 'estado novo']):
            return 'Era Vargas'
        elif any(palavra in pergunta_lower for palavra in ['ditadura militar', 'golpe de 64', 'ai-5']):
            return 'Ditadura Militar'
        elif any(palavra in pergunta_lower for palavra in ['redemocratização', 'constituição de 88']):
            return 'Nova República'
        
        # Escravidão
        elif any(palavra in pergunta_lower for palavra in ['escravidão', 'abolição', 'lei áurea', 'quilombo']):
            return 'Escravidão no Brasil'
    
    # LÍNGUA PORTUGUESA - Cobertura completa dos tópicos ENEM
    elif current_subject == 'Língua Portuguesa':
        # Gramática
        if any(palavra in pergunta_lower for palavra in ['sintaxe', 'sujeito', 'predicado', 'complemento']):
            return 'Sintaxe'
        elif any(palavra in pergunta_lower for palavra in ['morfologia', 'substantivo', 'adjetivo', 'verbo']):
            return 'Morfologia'
        elif any(palavra in pergunta_lower for palavra in ['crase', 'acento', 'ortografia']):
            return 'Ortografia e Acentuação'
        elif any(palavra in pergunta_lower for palavra in ['concordância', 'verbal', 'nominal']):
            return 'Concordância'
        elif any(palavra in pergunta_lower for palavra in ['regência', 'preposição']):
            return 'Regência'
        elif any(palavra in pergunta_lower for palavra in ['pontuação', 'vírgula', 'ponto']):
            return 'Pontuação'
        
        # Estilística
        elif any(palavra in pergunta_lower for palavra in ['figura de linguagem', 'metáfora', 'metonímia']):
            return 'Figuras de Linguagem'
        elif any(palavra in pergunta_lower for palavra in ['função da linguagem', 'emotiva', 'referencial']):
            return 'Funções da Linguagem'
        
        # Literatura
        elif any(palavra in pergunta_lower for palavra in ['literatura', 'movimento literário']):
            return 'Literatura Brasileira'
        elif any(palavra in pergunta_lower for palavra in ['barroco', 'gregório de matos']):
            return 'Barroco'
        elif any(palavra in pergunta_lower for palavra in ['arcadismo', 'árcade']):
            return 'Arcadismo'
        elif any(palavra in pergunta_lower for palavra in ['romantismo', 'josé de alencar', 'gonçalves dias']):
            return 'Romantismo'
        elif any(palavra in pergunta_lower for palavra in ['realismo', 'machado de assis']):
            return 'Realismo'
        elif any(palavra in pergunta_lower for palavra in ['parnasianismo', 'olavo bilac']):
            return 'Parnasianismo'
        elif any(palavra in pergunta_lower for palavra in ['simbolismo', 'cruz e sousa']):
            return 'Simbolismo'
        elif any(palavra in pergunta_lower for palavra in ['modernismo', 'semana de arte moderna', 'mário de andrade']):
            return 'Modernismo'
        
        # Interpretação
        elif any(palavra in pergunta_lower for palavra in ['interpretação', 'texto', 'leitura', 'compreensão']):
            return 'Interpretação de Textos'
        elif any(palavra in pergunta_lower for palavra in ['gênero textual', 'crônica', 'artigo']):
            return 'Gêneros Textuais'
    
    # REDAÇÃO - Tópicos específicos
    elif current_subject == 'Redação':
        if any(palavra in pergunta_lower for palavra in ['dissertação', 'argumentação', 'enem']):
            return 'Dissertação Argumentativa'
        elif any(palavra in pergunta_lower for palavra in ['introdução', 'tese', 'contextualização']):
            return 'Introdução'
        elif any(palavra in pergunta_lower for palavra in ['desenvolvimento', 'argumento', 'fundamentação']):
            return 'Desenvolvimento'
        elif any(palavra in pergunta_lower for palavra in ['conclusão', 'proposta', 'intervenção']):
            return 'Conclusão'
        elif any(palavra in pergunta_lower for palavra in ['coesão', 'coerência', 'conectivo']):
            return 'Coesão e Coerência'
    
    # Fallback inteligente: extrair palavras-chave da pergunta
    palavras = pergunta.split()
    if len(palavras) > 1:
        # Pegar palavras importantes (substantivos geralmente)
        palavras_importantes = []
        for palavra in palavras[:3]:  # Primeiras 3 palavras
            palavra_limpa = palavra.lower().strip('.,?!')
            if len(palavra_limpa) > 3 and palavra_limpa not in ['como', 'qual', 'onde', 'quando', 'quem', 'para', 'sobre']:
                palavras_importantes.append(palavra_limpa.title())
        
        if palavras_importantes:
            return ' '.join(palavras_importantes[:2])
    
    return current_subject

def buscar_conteudo_rag(pergunta: str, current_subject: str, api_key: str) -> str:
    """Busca conteúdo específico usando o sistema RAG dos professores"""
    try:
        # No ambiente Streamlit Cloud, usar sempre o fallback específico
        # para evitar erros de carregamento dos índices FAISS
        if hasattr(st, 'secrets'):  # Detecta ambiente Streamlit Cloud
            return f"TÓPICO ESPECÍFICO: {extrair_topico_especifico(pergunta, current_subject)} - Conteúdo direcionado para ENEM"
        
        # Importar o sistema RAG apropriado baseado na matéria (apenas local)
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
            # Inicializar o sistema RAG com timeout curto
            success = rag_system.initialize(api_key)
            if success:
                # Buscar conteúdo relevante
                docs = rag_system.search_relevant_content(pergunta, k=3)
                if docs:
                    # Concatenar conteúdo dos documentos encontrados
                    conteudo = "\n\n".join([doc.page_content[:500] for doc in docs])
                    return f"CONTEÚDO ESPECÍFICO ENCONTRADO:\n{conteudo}"
        
        # Fallback se não conseguir usar RAG
        return f"TÓPICO ESPECÍFICO: {extrair_topico_especifico(pergunta, current_subject)} - Conteúdo direcionado para ENEM"
        
    except Exception as e:
        # Fallback silencioso em caso de erro (sem logs desnecessários)
        return f"TÓPICO ESPECÍFICO: {extrair_topico_especifico(pergunta, current_subject)} - Conteúdo direcionado para ENEM"

def validar_especificidade_mapa(markdown_content: str, topico_especifico: str) -> bool:
    """Valida se o mapa mental é específico ao tópico identificado"""
    if not markdown_content or not topico_especifico:
        return False
    return topico_especifico.lower() in markdown_content.lower()

def criar_mapa_mental_especifico(pergunta: str, topico_especifico: str, nivel: str, current_subject: str) -> str:
    """Cria um mapa mental específico e explicativo para qualquer tópico de qualquer matéria do ENEM"""
    
    # Emojis por matéria
    emoji_materia = {
        'Matemática': '🧮', 'Física': '⚡', 'Química': '⚗️', 'Biologia': '🧬',
        'Geografia': '🌍', 'História': '🏛️', 'Língua Portuguesa': '📚', 'Redação': '✍️'
    }
    emoji = emoji_materia.get(current_subject, '📚')
    
    # Sistema universal: usar o template genérico melhorado para QUALQUER tópico
    conceitos_basicos = criar_template_universal(topico_especifico, nivel, current_subject, emoji, pergunta)
    
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

def criar_template_universal(topico_especifico: str, nivel: str, current_subject: str, emoji: str, pergunta: str) -> str:
    """Cria template universal explicativo para QUALQUER tópico de QUALQUER matéria"""
    
    # Banco de conhecimento específico por tópico e matéria
    conteudo_especifico = obter_conteudo_especifico(topico_especifico, current_subject, pergunta)
    
    if nivel == "Básico":
        return f"""
# {emoji} {topico_especifico}

## 📚 Definição
{conteudo_especifico['definicao']}

## 🔍 Características Principais
{conteudo_especifico['caracteristicas']}

## 💡 Como Identificar no ENEM
{conteudo_especifico['enem_basico']}
"""
    elif nivel == "Intermediário":
        return f"""
# {emoji} {topico_especifico}

## 📚 Definição Completa
{conteudo_especifico['definicao']}

## 🔍 Como Funciona
{conteudo_especifico['funcionamento']}

## 🎯 Estratégias de Resolução
{conteudo_especifico['estrategias']}

## 💡 No ENEM
{conteudo_especifico['enem_intermediario']}
"""
    else:  # Avançado
        return f"""
# {emoji} {topico_especifico}

## 📚 Fundamento Teórico
{conteudo_especifico['definicao']}

## 🔬 Análise Detalhada
{conteudo_especifico['analise_detalhada']}

## 🎯 Aplicações Avançadas
{conteudo_especifico['aplicacoes_avancadas']}

## 💡 Domínio Completo ENEM
{conteudo_especifico['enem_avancado']}
"""

def obter_conteudo_especifico(topico: str, materia: str, pergunta: str) -> dict:
    """Obtém conteúdo específico para qualquer tópico de qualquer matéria"""
    
    # Banco de conhecimento específico do ENEM
    if materia == 'Matemática':
        return gerar_conteudo_matematica(topico, pergunta)
    elif materia == 'Física':
        return gerar_conteudo_fisica(topico, pergunta)
    elif materia == 'Química':
        return gerar_conteudo_quimica(topico, pergunta)
    elif materia == 'Biologia':
        return gerar_conteudo_biologia(topico, pergunta)
    elif materia == 'Geografia':
        return gerar_conteudo_geografia(topico, pergunta)
    elif materia == 'História':
        return gerar_conteudo_historia(topico, pergunta)
    elif materia == 'Língua Portuguesa':
        return gerar_conteudo_portugues(topico, pergunta)
    elif materia == 'Redação':
        return gerar_conteudo_redacao(topico, pergunta)
    else:
        return gerar_conteudo_generico(topico, materia, pergunta)

def gerar_conteudo_matematica(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de Matemática"""
    
    conteudos = {
        'Equações do 2º Grau': {
            'definicao': '- Equações da forma $ax^2 + bx + c = 0$, onde $a ≠ 0$\n- Representam parábolas no plano cartesiano\n- Podem ter 0, 1 ou 2 soluções reais',
            'caracteristicas': '- Grau máximo 2 (expoente do x)\n- Coeficiente "a" determina concavidade da parábola\n- Discriminante $\\Delta = b^2 - 4ac$ indica número de raízes',
            'funcionamento': '### Resolução por Fatoração\n- Encontrar dois números que multiplicados dão "ac" e somados dão "b"\n### Fórmula de Bhaskara\n- $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$\n- Aplicável para qualquer equação do 2º grau',
            'estrategias': '- Verificar se é possível fatorar antes de usar Bhaskara\n- Calcular discriminante para saber quantas raízes existem\n- Usar soma e produto das raízes: $S = -\\frac{b}{a}$ e $P = \\frac{c}{a}$',
            'analise_detalhada': '### Estudo do Discriminante\n- $\\Delta > 0$: duas raízes reais distintas\n- $\\Delta = 0$: uma raiz real (raiz dupla)\n- $\\Delta < 0$: não há raízes reais\n### Análise Gráfica\n- Vértice da parábola: $V = (-\\frac{b}{2a}, -\\frac{\\Delta}{4a})$',
            'aplicacoes_avancadas': '### Problemas de Otimização\n- Máximos e mínimos de funções quadráticas\n- Problemas de área e perímetro\n### Inequações do 2º Grau\n- Análise de sinais da função quadrática',
            'enem_basico': '- Palavras-chave: "quadrática", "parábola", "duas soluções"\n- Identificar coeficientes a, b e c\n- Saber que tem formato de parábola',
            'enem_intermediario': '- Questões sobre área máxima/mínima\n- Problemas contextualizados (física, economia)\n- Tempo médio: 3-4 minutos por questão',
            'enem_avancado': '- Problemas interdisciplinares complexos\n- Análise de funções compostas\n- Demonstrações envolvendo propriedades das raízes'
        },
        'Trigonometria': {
            'definicao': '- Estudo das relações entre ângulos e lados de triângulos\n- Funções: seno, cosseno, tangente\n- Base para ondas, oscilações e fenômenos periódicos',
            'caracteristicas': '- Seno: cateto oposto / hipotenusa\n- Cosseno: cateto adjacente / hipotenusa\n- Tangente: cateto oposto / cateto adjacente',
            'funcionamento': '### Círculo Trigonométrico\n- Raio = 1, centro na origem\n- Ângulos em radianos: $180° = \\pi$ rad\n### Identidades Fundamentais\n- $\\sin^2 x + \\cos^2 x = 1$\n- $\\tan x = \\frac{\\sin x}{\\cos x}$',
            'estrategias': '- Memorizar ângulos notáveis (30°, 45°, 60°)\n- Usar identidades para simplificar expressões\n- Desenhar triângulos para visualizar relações',
            'analise_detalhada': '### Funções Trigonométricas\n- Período do seno e cosseno: $2\\pi$\n- Período da tangente: $\\pi$\n### Transformações\n- $f(x) = A\\sin(Bx + C) + D$\n- A: amplitude, B: frequência, C: fase, D: deslocamento vertical',
            'aplicacoes_avancadas': '### Equações Trigonométricas\n- Resolução de $\\sin x = a$, $\\cos x = b$\n### Lei dos Senos e Cossenos\n- Triângulos quaisquer, não apenas retângulos',
            'enem_basico': '- Triângulo retângulo com ângulos 30°, 45°, 60°\n- Calcular lados usando seno, cosseno, tangente\n- Reconhecer situações que envolvem triângulos',
            'enem_intermediario': '- Problemas de altura e distância\n- Questões envolvendo rampas e inclinações\n- Aplicações em física (movimento harmônico)',
            'enem_avancado': '- Equações trigonométricas complexas\n- Análise de funções periódicas\n- Demonstrações usando identidades'
        },
        'Probabilidade': {
            'definicao': '- Medida da chance de um evento ocorrer\n- Valor entre 0 (impossível) e 1 (certo)\n- Fórmula básica: $P(E) = \\frac{\\text{casos favoráveis}}{\\text{casos possíveis}}$',
            'caracteristicas': '- Espaço amostral: conjunto de todos os resultados possíveis\n- Evento: subconjunto do espaço amostral\n- Probabilidade complementar: $P(A^c) = 1 - P(A)$',
            'funcionamento': '### Regra da Adição\n- $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$\n### Regra da Multiplicação\n- Eventos independentes: $P(A \\cap B) = P(A) \\times P(B)$\n- Eventos dependentes: $P(A \\cap B) = P(A) \\times P(B|A)$',
            'estrategias': '- Identificar se eventos são independentes ou dependentes\n- Usar diagramas de árvore para eventos sequenciais\n- Calcular probabilidade complementar quando mais fácil',
            'analise_detalhada': '### Probabilidade Condicional\n- $P(A|B) = \\frac{P(A \\cap B)}{P(B)}$\n### Teorema de Bayes\n- Atualização de probabilidades com nova informação',
            'aplicacoes_avancadas': '### Distribuições de Probabilidade\n- Distribuição binomial\n- Distribuição normal (Gaussiana)\n### Teste de Hipóteses\n- Análise estatística de dados',
            'enem_basico': '- Problemas com dados, moedas, cartas\n- Calcular probabilidade simples\n- Reconhecer quando usar probabilidade complementar',
            'enem_intermediario': '- Probabilidade condicional em contextos reais\n- Problemas com extração sem reposição\n- Interpretação de gráficos probabilísticos',
            'enem_avancado': '- Análise crítica de pesquisas estatísticas\n- Problemas envolvendo múltiplas variáveis\n- Tomada de decisão baseada em probabilidade'
        }
    }
    
    # Se o tópico específico não estiver no banco, usar conteúdo genérico
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'Matemática', pergunta)

def gerar_conteudo_biologia(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de Biologia"""
    
    conteudos = {
        'Fotossíntese': {
            'definicao': '- Processo que converte energia luminosa em energia química\n- Plantas produzem glicose usando CO₂ e água\n- Libera oxigênio como produto secundário\n- Equação: $6CO_2 + 6H_2O \\xrightarrow{luz} C_6H_{12}O_6 + 6O_2$',
            'caracteristicas': '- Ocorre nos cloroplastos das células vegetais\n- Pigmento clorofila capta energia luminosa\n- Processo anabólico (constrói moléculas complexas)',
            'funcionamento': '### Fase Clara (Fotoquímica)\n- Ocorre nos tilacoides\n- Capta energia solar e produz ATP e NADPH\n- Fotólise da água libera oxigênio\n### Fase Escura (Ciclo de Calvin)\n- Ocorre no estroma do cloroplasto\n- Fixa CO₂ em moléculas orgânicas\n- Não depende diretamente da luz',
            'estrategias': '- Memorizar a equação global da fotossíntese\n- Distinguir entre fase clara e escura\n- Relacionar com respiração celular (processo inverso)',
            'analise_detalhada': '### Fotossistemas I e II\n- Complexos proteicos que captam luz\n- Transporte de elétrons gera ATP\n### Ciclo de Calvin-Benson\n- Fixação: CO₂ + RuBP → compostos de 3C\n- Redução: NADPH reduz 3-fosfoglicerato\n- Regeneração: RuBP é regenerada',
            'aplicacoes_avancadas': '### Tipos de Fotossíntese\n- Plantas C3: fixam CO₂ diretamente\n- Plantas C4: adaptação a climas quentes\n- Plantas CAM: adaptação a climas áridos\n### Fatores Limitantes\n- Intensidade luminosa, CO₂, temperatura',
            'enem_basico': '- Identificar que plantas fazem fotossíntese\n- Saber que produz oxigênio e glicose\n- Reconhecer importância para vida na Terra',
            'enem_intermediario': '- Questões sobre equação química\n- Relação com cadeia alimentar\n- Impacto ambiental e aquecimento global',
            'enem_avancado': '- Eficiência energética em diferentes biomas\n- Biotecnologia e plantas transgênicas\n- Análise de experimentos sobre fotossíntese'
        },
        'Genética Clássica': {
            'definicao': '- Estudo da hereditariedade baseado nas leis de Mendel\n- Transmissão de características dos pais para filhos\n- Genes dominantes e recessivos determinam fenótipo',
            'caracteristicas': '- Genótipo: constituição genética (AA, Aa, aa)\n- Fenótipo: características observáveis\n- Dominância: alelo que se expressa em heterozigose',
            'funcionamento': '### 1ª Lei de Mendel (Segregação)\n- Cada característica é determinada por par de fatores\n- Na formação dos gametas, fatores se separam\n### 2ª Lei de Mendel (Segregação Independente)\n- Genes para características diferentes segregam independentemente',
            'estrategias': '- Fazer quadrados de Punnett para cruzamentos\n- Identificar padrões de herança (dominante/recessivo)\n- Calcular probabilidades de descendência',
            'analise_detalhada': '### Tipos de Herança\n- Dominância completa: $A > a$\n- Codominância: ambos alelos se expressam\n- Herança ligada ao sexo: genes no cromossomo X\n### Análise de Pedigree\n- Rastreamento de características em famílias',
            'aplicacoes_avancadas': '### Aconselhamento Genético\n- Predição de riscos para doenças hereditárias\n### Melhoramento Genético\n- Seleção artificial em plantas e animais\n### Testes de Paternidade\n- Análise de marcadores genéticos',
            'enem_basico': '- Identificar características dominantes e recessivas\n- Fazer cruzamentos simples (monoibridismo)\n- Calcular proporções fenotípicas básicas',
            'enem_intermediario': '- Problemas envolvendo diibridismo\n- Herança ligada ao sexo\n- Interpretação de heredogramas simples',
            'enem_avancado': '- Análise de heredogramas complexos\n- Cálculo de probabilidades em múltiplas gerações\n- Aplicações em biotecnologia e medicina'
        },
        'Ecologia': {
            'definicao': '- Estudo das relações entre seres vivos e ambiente\n- Fluxo de energia e ciclo de matéria nos ecossistemas\n- Organização: indivíduo → população → comunidade → ecossistema',
            'caracteristicas': '- Produtores: fazem fotossíntese (plantas)\n- Consumidores: dependem de outros organismos\n- Decompositores: reciclam matéria orgânica',
            'funcionamento': '### Cadeias e Teias Alimentares\n- Transferência de energia entre níveis tróficos\n- Apenas 10% da energia passa para próximo nível\n### Ciclos Biogeoquímicos\n- Carbono, nitrogênio, fósforo, água\n- Reciclagem de elementos químicos',
            'estrategias': '- Identificar níveis tróficos em cadeias alimentares\n- Analisar fluxo de energia (sempre unidirecional)\n- Relacionar atividades humanas com impactos ambientais',
            'analise_detalhada': '### Dinâmica Populacional\n- Crescimento exponencial vs. logístico\n- Fatores limitantes: competição, predação\n### Sucessão Ecológica\n- Sucessão primária e secundária\n- Comunidade clímax',
            'aplicacoes_avancadas': '### Conservação da Biodiversidade\n- Hotspots de biodiversidade\n- Fragmentação de habitats\n### Mudanças Climáticas\n- Efeito estufa e aquecimento global\n- Impactos nos ecossistemas',
            'enem_basico': '- Identificar produtores, consumidores e decompositores\n- Reconhecer impactos da ação humana\n- Saber conceitos básicos de poluição',
            'enem_intermediario': '- Análise de cadeias alimentares complexas\n- Problemas de poluição e suas consequências\n- Relacionar atividade humana com degradação ambiental',
            'enem_avancado': '- Análise crítica de políticas ambientais\n- Sustentabilidade e desenvolvimento\n- Interpretação de dados sobre mudanças climáticas'
        }
    }
    
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'Biologia', pergunta)

def gerar_conteudo_fisica(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de Física"""
    
    conteudos = {
        'Cinemática': {
            'definicao': '- Estuda o movimento sem considerar suas causas\n- Grandezas: posição, velocidade, aceleração\n- Base para compreender qualquer tipo de movimento',
            'caracteristicas': '- Movimento uniforme: velocidade constante\n- Movimento uniformemente variado: aceleração constante\n- Movimento relativo: depende do referencial',
            'funcionamento': '### Movimento Uniforme (MU)\n- $v = \\frac{\\Delta s}{\\Delta t}$ (velocidade constante)\n- $s = s_0 + vt$ (função horária)\n### Movimento Uniformemente Variado (MUV)\n- $v = v_0 + at$ (velocidade)\n- $s = s_0 + v_0t + \\frac{1}{2}at^2$ (posição)',
            'estrategias': '- Identificar tipo de movimento pelo enunciado\n- Fazer gráficos de posição e velocidade vs tempo\n- Usar equações de Torricelli quando não há tempo',
            'analise_detalhada': '### Análise Gráfica\n- Gráfico s×t: inclinação = velocidade\n- Gráfico v×t: inclinação = aceleração, área = deslocamento\n### Lançamento de Projéteis\n- Movimento parabólico: composição de MU + MUV',
            'aplicacoes_avancadas': '### Movimento Circular\n- Velocidade angular e linear\n- Aceleração centrípeta\n### Movimento Harmônico Simples\n- Oscilações: pêndulo, mola',
            'enem_basico': '- Calcular velocidade média\n- Converter unidades (km/h ↔ m/s)\n- Interpretar gráficos simples de movimento',
            'enem_intermediario': '- Problemas de encontro de móveis\n- Lançamento vertical e queda livre\n- Análise de gráficos complexos',
            'enem_avancado': '- Movimento de projéteis bidimensional\n- Análise vetorial de velocidade\n- Problemas contextualizados (trânsito, esportes)'
        },
        'Dinâmica': {
            'definicao': '- Estuda as causas do movimento (forças)\n- Leis de Newton explicam relação força-movimento\n- Base da mecânica clássica',
            'caracteristicas': '- 1ª Lei: Inércia (objeto em repouso tende a continuar em repouso)\n- 2ª Lei: F = ma (força é proporcional à aceleração)\n- 3ª Lei: Ação e reação (forças aparecem aos pares)',
            'funcionamento': '### Aplicação das Leis de Newton\n- Identificar todas as forças que atuam\n- Desenhar diagrama de corpo livre\n- Aplicar $\\sum F = ma$\n### Tipos de Força\n- Peso: $P = mg$\n- Atrito: $f = \\mu N$\n- Normal: perpendicular à superfície',
            'estrategias': '- Sempre desenhar diagrama de forças\n- Escolher sistema de coordenadas adequado\n- Aplicar as leis de Newton para cada direção',
            'analise_detalhada': '### Forças de Atrito\n- Estático: impede movimento\n- Cinético: opõe-se ao movimento\n### Força Centrípeta\n- $F_c = \\frac{mv^2}{r}$ (movimento circular)',
            'aplicacoes_avancadas': '### Sistemas de Partículas\n- Múltiplos corpos conectados\n- Polias e planos inclinados\n### Aplicações em Engenharia\n- Projeto de estruturas\n- Dinâmica veicular',
            'enem_basico': '- Identificar forças em situações simples\n- Aplicar F = ma em problemas diretos\n- Reconhecer pares ação-reação',
            'enem_intermediario': '- Problemas com atrito e planos inclinados\n- Sistemas de polias\n- Movimento circular uniforme',
            'enem_avancado': '- Análise de sistemas complexos\n- Aplicações em tecnologia e engenharia\n- Problemas interdisciplinares'
        }
    }
    
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'Física', pergunta)

def gerar_conteudo_quimica(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de Química"""
    
    conteudos = {
        'Ácidos e Bases': {
            'definicao': '- Ácidos: substâncias que liberam H⁺ em solução aquosa\n- Bases: substâncias que liberam OH⁻ em solução aquosa\n- pH mede acidez: 0-7 ácido, 7 neutro, 7-14 básico',
            'caracteristicas': '- Ácidos: sabor azedo, conduzem eletricidade, corrosivos\n- Bases: sabor amargo, escorregadias, também conduzem eletricidade\n- Indicadores: papel tornassol, fenolftaleína',
            'funcionamento': '### Teoria de Arrhenius\n- Ácido: $HCl \\rightarrow H^+ + Cl^-$\n- Base: $NaOH \\rightarrow Na^+ + OH^-$\n### Escala de pH\n- $pH = -\\log[H^+]$\n- $pOH = -\\log[OH^-]$\n- $pH + pOH = 14$ (a 25°C)',
            'estrategias': '- Memorizar fórmulas de ácidos e bases comuns\n- Usar escala de pH para classificar substâncias\n- Balancear reações de neutralização',
            'analise_detalhada': '### Força de Ácidos e Bases\n- Ácidos fortes: HCl, HNO₃, H₂SO₄\n- Bases fortes: NaOH, KOH, Ca(OH)₂\n### Constantes de Ionização\n- $K_a$ para ácidos, $K_b$ para bases',
            'aplicacoes_avancadas': '### Soluções Tampão\n- Resistem a mudanças de pH\n- Importantes em sistemas biológicos\n### Titulação\n- Determinação de concentração',
            'enem_basico': '- Identificar substâncias ácidas e básicas do cotidiano\n- Usar escala de pH para classificar\n- Reconhecer reações de neutralização',
            'enem_intermediario': '- Cálculos envolvendo pH e pOH\n- Problemas de neutralização\n- Aplicações industriais e ambientais',
            'enem_avancado': '- Análise de sistemas tampão\n- Cálculos de constantes de equilíbrio\n- Interpretação de curvas de titulação'
        }
    }
    
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'Química', pergunta)

def gerar_conteudo_geografia(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de Geografia"""
    
    conteudos = {
        'Climatologia': {
            'definicao': '- Estuda os fenômenos atmosféricos em longo prazo\n- Diferença entre tempo (momentâneo) e clima (padrão)\n- Fatores: latitude, altitude, maritimidade, correntes',
            'caracteristicas': '- Elementos: temperatura, umidade, pressão, ventos\n- Fatores: latitude, altitude, maritimidade, relevo\n- Tipos climáticos: equatorial, tropical, temperado, polar',
            'funcionamento': '### Circulação Atmosférica\n- Células de Hadley, Ferrel e Polar\n- Ventos alísios, contra-alísios\n### Massas de Ar\n- Massas quentes e frias\n- Frentes frias e quentes',
            'estrategias': '- Relacionar latitude com temperatura\n- Associar altitude com temperatura (gradiente térmico)\n- Analisar climogramas',
            'analise_detalhada': '### Fenômenos Climáticos\n- El Niño e La Niña\n- Monções\n- Furacões e ciclones\n### Mudanças Climáticas\n- Aquecimento global\n- Efeito estufa intensificado',
            'aplicacoes_avancadas': '### Impactos Socioeconômicos\n- Agricultura e clima\n- Migração climática\n### Políticas Ambientais\n- Protocolo de Kyoto\n- Acordo de Paris',
            'enem_basico': '- Identificar tipos climáticos do Brasil\n- Relacionar clima com vegetação\n- Reconhecer fatores que influenciam o clima',
            'enem_intermediario': '- Interpretar climogramas\n- Analisar fenômenos como El Niño\n- Relacionar clima com atividades humanas',
            'enem_avancado': '- Análise crítica das mudanças climáticas\n- Impactos socioeconômicos do clima\n- Políticas públicas e acordos internacionais'
        }
    }
    
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'Geografia', pergunta)

def gerar_conteudo_historia(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de História"""
    
    conteudos = {
        'Guerra Fria': {
            'definicao': '- Conflito ideológico entre EUA (capitalismo) e URSS (socialismo)\n- Período: 1947-1991\n- Guerra "fria" = sem confronto militar direto',
            'caracteristicas': '- Bipolarização mundial\n- Corrida armamentista nuclear\n- Disputas por zonas de influência',
            'funcionamento': '### Principais Eventos\n- Plano Marshall (reconstrução da Europa)\n- Construção e queda do Muro de Berlim\n- Crise dos Mísseis de Cuba\n### Conflitos Indiretos\n- Guerra da Coreia, Vietnã\n- Revolução Cubana',
            'estrategias': '- Relacionar eventos à disputa EUA vs URSS\n- Identificar características de cada bloco\n- Analisar consequências para países periféricos',
            'analise_detalhada': '### Doutrinas e Estratégias\n- Doutrina Truman (contenção do comunismo)\n- Coexistência pacífica\n- Détente (distensão)\n### Fim da Guerra Fria\n- Glasnost e Perestroika\n- Queda do Muro de Berlim (1989)',
            'aplicacoes_avancadas': '### Legado\n- Unipolaridade americana\n- Nova ordem mundial\n### Comparações\n- Tensões atuais EUA-China/Rússia',
            'enem_basico': '- Identificar os dois blocos antagônicos\n- Reconhecer principais eventos\n- Saber período de duração',
            'enem_intermediario': '- Analisar impactos na América Latina\n- Relacionar com ditaduras militares no Brasil\n- Compreender conceito de bipolaridade',
            'enem_avancado': '- Análise geopolítica complexa\n- Comparação com tensões contemporâneas\n- Interpretação de documentos históricos'
        }
    }
    
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'História', pergunta)

def gerar_conteudo_portugues(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de Língua Portuguesa"""
    
    conteudos = {
        'Figuras de Linguagem': {
            'definicao': '- Recursos expressivos que conferem maior expressividade ao texto\n- Desviam da linguagem literal para criar efeitos\n- Dividem-se em: som, palavra, construção, pensamento',
            'caracteristicas': '- Metáfora: comparação implícita\n- Metonímia: substituição por proximidade\n- Hipérbole: exagero intencional',
            'funcionamento': '### Figuras de Palavra\n- Metáfora: "Vida é sonho"\n- Metonímia: "Ler Machado" (obras de Machado)\n### Figuras de Construção\n- Anáfora: repetição no início\n- Hipérbato: inversão da ordem',
            'estrategias': '- Identificar o efeito pretendido\n- Distinguir metáfora de comparação\n- Reconhecer figuras em diferentes gêneros textuais',
            'analise_detalhada': '### Classificação Completa\n- Som: aliteração, assonância\n- Palavra: metáfora, metonímia, catacrese\n- Construção: elipse, zeugma, pleonasmo\n- Pensamento: ironia, antítese, paradoxo',
            'aplicacoes_avancadas': '### Análise Literária\n- Figuras na poesia romântica\n- Simbolismo e suas metáforas\n### Aplicação em Textos\n- Redação criativa\n- Análise de discursos políticos',
            'enem_basico': '- Identificar metáforas simples\n- Reconhecer hipérboles em textos\n- Distinguir linguagem literal de figurada',
            'enem_intermediario': '- Analisar efeitos expressivos das figuras\n- Identificar figuras em textos literários\n- Relacionar figuras com intenção comunicativa',
            'enem_avancado': '- Análise estilística complexa\n- Interpretação de textos multissemióticos\n- Comparação entre diferentes estilos literários'
        }
    }
    
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'Língua Portuguesa', pergunta)

def gerar_conteudo_redacao(topico: str, pergunta: str) -> dict:
    """Gera conteúdo específico para tópicos de Redação"""
    
    conteudos = {
        'Dissertação Argumentativa': {
            'definicao': '- Texto que defende um ponto de vista com argumentos\n- Estrutura: introdução, desenvolvimento, conclusão\n- Objetivo: convencer o leitor sobre uma tese',
            'caracteristicas': '- Linguagem formal e impessoal\n- Argumentos consistentes e bem fundamentados\n- Proposta de intervenção detalhada',
            'funcionamento': '### Introdução\n- Contextualização do tema\n- Apresentação da tese\n### Desenvolvimento\n- Argumentos com fundamentação\n- Exemplos e dados\n### Conclusão\n- Retomada da tese\n- Proposta de intervenção',
            'estrategias': '- Ler e interpretar bem o tema\n- Fazer esquema antes de escrever\n- Usar conectivos para articular ideias\n- Propor intervenção viável e detalhada',
            'analise_detalhada': '### Competências ENEM\n1. Norma padrão da língua\n2. Compreensão do tema\n3. Seleção de argumentos\n4. Coesão e coerência\n5. Proposta de intervenção\n### Tipos de Argumento\n- Autoridade, exemplificação, causa/consequência',
            'aplicacoes_avancadas': '### Estratégias Argumentativas\n- Contra-argumentação\n- Concessão\n### Repertório Sociocultural\n- Citações, dados, referências\n- Interdisciplinaridade',
            'enem_basico': '- Compreender a estrutura básica\n- Identificar tema e tese\n- Escrever parágrafos organizados',
            'enem_intermediario': '- Desenvolver argumentos consistentes\n- Usar repertório sociocultural\n- Articular bem as ideias',
            'enem_avancado': '- Proposta de intervenção detalhada e viável\n- Argumentação sofisticada\n- Excelência em todas as competências'
        }
    }
    
    if topico in conteudos:
        return conteudos[topico]
    else:
        return gerar_conteudo_generico(topico, 'Redação', pergunta)

def gerar_conteudo_generico(topico: str, materia: str, pergunta: str) -> dict:
    """Gera conteúdo genérico para qualquer tópico não mapeado especificamente"""
    
    return {
        'definicao': f'- Conceito fundamental de {materia} relacionado a {topico.lower()}\n- Tópico importante para o ENEM\n- Base para compreensão de temas mais avançados',
        'caracteristicas': f'- Propriedades específicas de {topico.lower()}\n- Aplicações práticas no cotidiano\n- Relação com outros conceitos da matéria',
        'funcionamento': f'### Processo Principal\n- Etapas fundamentais de {topico.lower()}\n- Mecanismos envolvidos\n### Aplicações\n- Uso em situações reais\n- Exemplos práticos',
        'estrategias': f'- Identificar {topico.lower()} em questões\n- Aplicar conceitos básicos\n- Relacionar com conhecimentos prévios',
        'analise_detalhada': f'### Aspectos Avançados\n- Análise aprofundada de {topico.lower()}\n- Relações complexas\n### Variações\n- Diferentes contextos de aplicação',
        'aplicacoes_avancadas': f'### Aplicações Complexas\n- Uso em problemas multidisciplinares\n- Conexões com tecnologia atual\n### Pesquisa\n- Desenvolvimentos recentes',
        'enem_basico': f'- Reconhecer {topico.lower()} em contextos simples\n- Aplicar definições básicas\n- Identificar características principais',
        'enem_intermediario': f'- Resolver problemas envolvendo {topico.lower()}\n- Analisar aplicações práticas\n- Fazer conexões entre conceitos',
        'enem_avancado': f'- Análise crítica de situações complexas\n- Aplicação em contextos interdisciplinares\n- Avaliação de implicações sociais/ambientais'
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