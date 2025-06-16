#!/usr/bin/env python3
"""
Mapa Mental Dinâmico - Gerado automaticamente com base nas dúvidas da Sther
"""

import streamlit as st
import json
import re
from typing import Dict, List, Any

def display_mapa_mental():
    """Interface do mapa mental dinâmico baseado nas dúvidas da Sther"""
    
    st.markdown("# 🧠 Mapa Mental Dinâmico")
    st.markdown("Mapa mental gerado automaticamente com base na sua última dúvida!")
    
    # Verificar se há histórico de chat da matemática
    chat_history = st.session_state.get('chat_history', {}).get('Matemática', [])
    
    if not chat_history:
        st.info("""
        📝 **Como funciona:**
        
        1. **Faça uma pergunta** na aba "💬 Chat" para o Professor Carlos
        2. **Volte para esta aba** e verá um mapa mental automático
        3. **Explore os conceitos** relacionados à sua dúvida
        4. **Clique nos nós** para mais detalhes
        
        🎯 **Exemplo:** Pergunte "Como resolver equações do 2º grau?" e volte aqui!
        """)
        return
    
    # Pegar última interação (pergunta + resposta)
    ultima_pergunta = None
    ultima_resposta = None
    
    for i in range(len(chat_history) - 1, -1, -1):
        msg = chat_history[i]
        if msg['role'] == 'user' and not ultima_pergunta:
            ultima_pergunta = msg['content']
        elif msg['role'] == 'assistant' and not ultima_resposta:
            ultima_resposta = msg['content']
        
        if ultima_pergunta and ultima_resposta:
            break
    
    if not ultima_pergunta:
        st.warning("💬 Faça uma pergunta na aba Chat primeiro!")
        return
    
    # Mostrar contexto da dúvida
    with st.expander("🔍 Contexto da sua dúvida", expanded=False):
        st.markdown(f"**Sua pergunta:** {ultima_pergunta}")
        if ultima_resposta:
            st.markdown(f"**Resposta do Professor:** {ultima_resposta[:200]}...")
    
    st.markdown("---")
    
    # Gerar mapa mental baseado na pergunta
    api_key = getattr(st.session_state, 'api_key', '')
    
    if not api_key:
        st.warning("""
        🔑 **Configure sua API Key da Groq primeiro!**
        
        Vá para a aba "💬 Chat" e configure sua API Key na barra lateral.
        """)
        return
    
    # Botão para gerar/regenerar mapa mental
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🗺️ Mapa Mental da sua Dúvida")
    with col2:
        if st.button("🔄 Regenerar"):
            if 'mapa_mental_cache' in st.session_state:
                del st.session_state.mapa_mental_cache
            st.rerun()
    
    # Cache do mapa mental para evitar regerar constantemente
    cache_key = f"mapa_{hash(ultima_pergunta)}"
    
    if cache_key not in st.session_state.get('mapa_mental_cache', {}):
        with st.spinner("🧠 Gerando mapa mental personalizado..."):
            mapa_data = gerar_mapa_mental_ia(ultima_pergunta, ultima_resposta, api_key)
            
            if 'mapa_mental_cache' not in st.session_state:
                st.session_state.mapa_mental_cache = {}
            st.session_state.mapa_mental_cache[cache_key] = mapa_data
    else:
        mapa_data = st.session_state.mapa_mental_cache[cache_key]
    
    if mapa_data:
        renderizar_mapa_mental(mapa_data, api_key)
    else:
        st.error("❌ Erro ao gerar mapa mental. Tente novamente.")

def gerar_mapa_mental_ia(pergunta: str, resposta: str, api_key: str) -> Dict:
    """Gera estrutura do mapa mental usando IA"""
    
    try:
        from professor_carlos_local import professor_carlos_local
        
        prompt_mapa = f"""
Baseado na pergunta da aluna Sther: "{pergunta}"

Crie um mapa mental estruturado em JSON com os conceitos matemáticos relacionados.

IMPORTANTE: Responda APENAS com um JSON válido, sem texto adicional.

Estrutura esperada:
{{
    "conceito_central": "Nome do conceito principal",
    "nos": [
        {{
            "id": "conceito1",
            "titulo": "Título do conceito",
            "descricao": "Breve descrição",
            "formulas": ["f(x) = ax + b", "Δ = b² - 4ac"],
            "conecta_com": ["conceito2", "conceito3"],
            "nivel": 1
        }}
    ]
}}

Inclua 5-8 conceitos relacionados com diferentes níveis de profundidade.
Use LaTeX para fórmulas matemáticas.
"""
        
        resposta_ia = professor_carlos_local.get_response(prompt_mapa, api_key)
        
        # Extrair JSON da resposta
        json_match = re.search(r'\{.*\}', resposta_ia, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                mapa_data = json.loads(json_str)
                return mapa_data
            except json.JSONDecodeError:
                pass
        
        # Se não conseguiu extrair JSON válido, criar estrutura básica
        return criar_mapa_basico(pergunta)
        
    except Exception as e:
        st.error(f"Erro ao gerar mapa: {str(e)}")
        return criar_mapa_basico(pergunta)

def criar_mapa_basico(pergunta: str) -> Dict:
    """Cria mapa mental básico baseado em palavras-chave da pergunta"""
    
    # Detectar tópicos com base em palavras-chave
    topicos_map = {
        'equacao': ['Equações', 'Resolução', 'Raízes', 'Métodos'],
        'funcao': ['Funções', 'Gráficos', 'Domínio', 'Imagem'],
        'geometria': ['Geometria', 'Áreas', 'Volumes', 'Teoremas'],
        'trigonometria': ['Trigonometria', 'Seno', 'Cosseno', 'Identidades'],
        'derivada': ['Derivadas', 'Limites', 'Taxa de variação', 'Regras'],
        'integral': ['Integrais', 'Área sob curva', 'Primitivas', 'Cálculo']
    }
    
    pergunta_lower = pergunta.lower()
    conceitos_detectados = []
    
    for chave, conceitos in topicos_map.items():
        if chave in pergunta_lower:
            conceitos_detectados.extend(conceitos)
    
    if not conceitos_detectados:
        conceitos_detectados = ['Matemática', 'ENEM', 'Resolução', 'Fórmulas']
    
    # Criar estrutura básica
    nos = []
    for i, conceito in enumerate(conceitos_detectados[:6]):
        nos.append({
            "id": f"conceito{i+1}",
            "titulo": conceito,
            "descricao": f"Conceito relacionado à sua dúvida sobre: {pergunta[:50]}...",
            "formulas": [],
            "conecta_com": [f"conceito{j+1}" for j in range(len(conceitos_detectados[:6])) if j != i][:2],
            "nivel": 1 if i < 3 else 2
        })
    
    return {
        "conceito_central": conceitos_detectados[0] if conceitos_detectados else "Matemática",
        "nos": nos
    }

def renderizar_mapa_mental(mapa_data: Dict, api_key: str):
    """Renderiza o mapa mental de forma visual e interativa"""
    
    conceito_central = mapa_data.get('conceito_central', 'Matemática')
    nos = mapa_data.get('nos', [])
    
    # Título do mapa mental
    st.markdown(f"## 🎯 {conceito_central}")
    
    # Renderizar conceito central
    st.markdown("### 🏠 Conceito Central")
    
    col_central1, col_central2, col_central3 = st.columns([1, 2, 1])
    with col_central2:
        st.markdown(f"""
        <div style="
            text-align: center; 
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 20px; 
            border-radius: 15px; 
            font-size: 1.2em;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            🎯 {conceito_central}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Renderizar nós por nível
    st.markdown("### 🌐 Conceitos Relacionados")
    
    # Agrupar por nível
    nos_nivel_1 = [no for no in nos if no.get('nivel', 1) == 1]
    nos_nivel_2 = [no for no in nos if no.get('nivel', 1) == 2]
    
    # Nível 1 - Conceitos principais
    if nos_nivel_1:
        st.markdown("#### 🔵 Conceitos Fundamentais")
        cols = st.columns(min(len(nos_nivel_1), 3))
        
        for i, no in enumerate(nos_nivel_1):
            with cols[i % 3]:
                renderizar_no_conceito(no, api_key, cor="primary")
    
    # Nível 2 - Conceitos secundários
    if nos_nivel_2:
        st.markdown("#### 🟢 Conceitos Complementares")
        cols = st.columns(min(len(nos_nivel_2), 4))
        
        for i, no in enumerate(nos_nivel_2):
            with cols[i % 4]:
                renderizar_no_conceito(no, api_key, cor="secondary")
    
    # Área de exploração detalhada
    st.markdown("---")
    st.markdown("### 🔍 Exploração Detalhada")
    
    # Selectbox para escolher conceito para explorar
    conceitos_disponiveis = [no['titulo'] for no in nos]
    if conceitos_disponiveis:
        conceito_selecionado = st.selectbox(
            "Escolha um conceito para explorar em detalhes:",
            ["Selecione..."] + conceitos_disponiveis
        )
        
        if conceito_selecionado != "Selecione...":
            no_selecionado = next((no for no in nos if no['titulo'] == conceito_selecionado), None)
            if no_selecionado:
                explorar_conceito_detalhado(no_selecionado, api_key)

def renderizar_no_conceito(no: Dict, api_key: str, cor: str = "primary"):
    """Renderiza um nó individual do mapa mental"""
    
    titulo = no.get('titulo', 'Conceito')
    descricao = no.get('descricao', '')
    formulas = no.get('formulas', [])
    
    # Cor baseada no tipo
    cor_map = {
        "primary": "#667eea",
        "secondary": "#48bb78"
    }
    cor_hex = cor_map.get(cor, "#667eea")
    
    # Card do conceito
    st.markdown(f"""
    <div style="
        border: 2px solid {cor_hex};
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, {cor_hex}15, {cor_hex}05);
    ">
        <h4 style="color: {cor_hex}; margin: 0 0 10px 0;">📖 {titulo}</h4>
        <p style="margin: 5px 0; font-size: 0.9em;">{descricao}</p>
    """, unsafe_allow_html=True)
    
    # Fórmulas se houver
    if formulas:
        st.markdown("**Fórmulas:**")
        for formula in formulas[:2]:  # Máximo 2 fórmulas por card
            st.markdown(f"- ${formula}$")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Botão para explicação
    if st.button(f"🤖 Explicar {titulo}", key=f"explain_{no.get('id', titulo)}"):
        with st.spinner(f"Professor Carlos explicando {titulo}..."):
            try:
                from professor_carlos_local import professor_carlos_local
                
                pergunta = f"Explique de forma didática o conceito de {titulo} para uma aluna do ENEM. Inclua exemplos práticos e fórmulas importantes."
                
                resposta = professor_carlos_local.get_response(pergunta, api_key)
                
                st.markdown(f"### 👨‍🏫 Professor Carlos explica: {titulo}")
                st.markdown(f'<div class="arithmatex">{resposta}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar explicação: {str(e)}")

def explorar_conceito_detalhado(no: Dict, api_key: str):
    """Explora um conceito em detalhes com informações da base RAG"""
    
    titulo = no.get('titulo', 'Conceito')
    
    st.markdown(f"#### 🔬 Explorando: {titulo}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Informações Básicas**")
        st.info(no.get('descricao', 'Descrição não disponível'))
        
        formulas = no.get('formulas', [])
        if formulas:
            st.markdown("**📐 Fórmulas Principais**")
            for formula in formulas:
                st.markdown(f"- ${formula}$")
    
    with col2:
        st.markdown("**🔗 Conceitos Relacionados**")
        conecta_com = no.get('conecta_com', [])
        if conecta_com:
            for conexao in conecta_com:
                st.markdown(f"- 🔸 {conexao}")
        else:
            st.markdown("- *Nenhuma conexão definida*")
    
    # Busca na base RAG
    if st.button(f"🔍 Buscar na Base de Conhecimento", key=f"search_{no.get('id', titulo)}"):
        with st.spinner("Buscando informações relacionadas..."):
            try:
                from professor_carlos_local import professor_carlos_local
                
                # Buscar documentos relacionados
                docs_relacionados = professor_carlos_local.search_documents(titulo, k=3)
                
                if docs_relacionados:
                    st.markdown("#### 📚 Informações da Base de Conhecimento")
                    
                    for i, doc in enumerate(docs_relacionados, 1):
                        with st.expander(f"📄 Documento {i}"):
                            st.markdown(doc['content'][:500] + "...")
                            
                            if 'metadata' in doc and 'source' in doc['metadata']:
                                st.caption(f"Fonte: {doc['metadata']['source']}")
                else:
                    st.warning("Nenhum documento relacionado encontrado na base de conhecimento.")
                    
            except Exception as e:
                st.error(f"❌ Erro ao buscar na base: {str(e)}")

# Função para ser chamada pelo app principal
def display_mapa_mental_wrapper():
    """Wrapper para ser chamado pelo app principal"""
    try:
        display_mapa_mental()
    except Exception as e:
        st.error(f"❌ Erro no mapa mental: {str(e)}")
        st.info("💡 Faça uma pergunta na aba Chat primeiro!")

if __name__ == "__main__":
    # Para teste direto
    try:
        st.set_page_config(page_title="Mapa Mental Dinâmico", page_icon="🧠", layout="wide")
    except st.errors.StreamlitAPIException:
        # Já foi configurado pelo app principal, ignora
        pass
    
    # Mock data para teste
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {
            'Matemática': [
                {'role': 'user', 'content': 'Como resolver equações do segundo grau?'},
                {'role': 'assistant', 'content': 'Para resolver equações do segundo grau, você pode usar a fórmula de Bhaskara...'}
            ]
        }
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = st.sidebar.text_input("API Key:", type="password")
    
    display_mapa_mental() 