#!/usr/bin/env python3
"""
Professora Letícia - Sistema RAG Local para Língua Portuguesa e Redação
A.T.E.N.A. - Interface integrada com Streamlit
"""

import streamlit as st
import time
from typing import Dict, Any, List
import os

# Importa sistema RAG de português
try:
    from local_portuguese_rag import local_portuguese_rag
    PORTUGUESE_RAG_AVAILABLE = True
except ImportError:
    PORTUGUESE_RAG_AVAILABLE = False

# Importa sistema RAG de redação
try:
    from local_redacao_rag import RedacaoRAG
    REDACAO_RAG_AVAILABLE = True
except ImportError:
    REDACAO_RAG_AVAILABLE = False

def setup_professor_leticia_local_ui():
    """Configura interface da Professora Letícia"""
    
    st.markdown("### ✍️ Correção de Redação (Critérios ENEM)")
    
    if not REDACAO_RAG_AVAILABLE:
        st.error("❌ Sistema de Correção de Redação não disponível. Verifique as dependências.")
    else:
        # File uploader para a redação
        uploaded_file = st.file_uploader(
            "Envie sua redação em formato PDF ou TXT:",
            type=['pdf', 'txt'],
            help="A Professora Letícia irá corrigir sua redação com base nos critérios do ENEM."
        )
        
        if uploaded_file:
            # Botão para iniciar a correção
            if st.button("Corrigir Redação", key="corrigir_redacao", type="primary"):
                api_key = os.environ.get("GROQ_API_KEY")
                if not api_key:
                    st.error("🔑 Chave da API Groq não encontrada. Configure-a para continuar.")
                else:
                    with st.spinner("Extraindo texto do arquivo..."):
                        if uploaded_file.type == "application/pdf":
                            text = RedacaoRAG.extract_text_from_pdf(uploaded_file.read())
                        else:
                            text = uploaded_file.read().decode("utf-8")
                    
                    if "não foi possível extrair" in text.lower() or not text.strip():
                        st.error(f"❌ Erro ao ler o arquivo: {text}")
                    else:
                        # Armazena o texto e dispara a correção
                        st.session_state.redacao_text = text
                        # Limpa correção antiga
                        if 'redacao_correction' in st.session_state:
                            del st.session_state['redacao_correction']

            # Se o texto da redação está no estado da sessão, mostra e permite corrigir
            if 'redacao_text' in st.session_state:
                with st.expander("👀 Ver texto da redação enviada", expanded=False):
                    st.text_area("", st.session_state.redacao_text, height=250)

                # Gera a correção se ainda não foi gerada
                if 'redacao_correction' not in st.session_state:
                    corrector = RedacaoRAG(api_key=os.environ.get("GROQ_API_KEY"))
                    correction = corrector.get_correction(st.session_state.redacao_text)
                    st.session_state.redacao_correction = correction
                
                # Exibe a correção
                st.markdown("---")
                st.markdown("#### Análise da Professora Letícia:")
                st.markdown(st.session_state.redacao_correction)

    st.markdown("---")
    st.markdown("### 📚 Dúvidas sobre Língua Portuguesa")

    if not PORTUGUESE_RAG_AVAILABLE:
        st.error("❌ Sistema RAG Local de Língua Portuguesa não disponível. Verifique as dependências.")
        return
    
    # Botão para processar documentos de Português
    if st.button("🔄 Processar Materiais de Português", key="process_portuguese"):
        with st.spinner("Processando materiais..."):
            success = local_portuguese_rag.process_portuguese_documents()
            if success:
                st.success("✅ Materiais de português processados!")
            else:
                st.error("❌ Erro ao processar materiais de português.")
    
    # Estatísticas
    stats = local_portuguese_rag.get_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documentos (Português)", stats["total_documentos"])
    with col2:
        st.metric("VectorStore (Português)", "✅" if stats["vectorstore_inicializado"] else "❌")
    with col3:
        st.metric("RAG Chain (Português)", "✅" if stats["rag_chain_configurada"] else "❌")

def get_professor_leticia_local_response(question: str, api_key: str) -> str:
    """Gera resposta da Professora Letícia para dúvidas de português"""
    
    # Esta função agora lida apenas com as perguntas gerais de português.
    # A correção de redação é tratada na UI.
    
    if not PORTUGUESE_RAG_AVAILABLE:
        return "❌ Sistema RAG Local de Língua Portuguesa não está disponível."
    
    if not api_key:
        return "🔑 Por favor, configure sua chave da API Groq."
    
    try:
        # Garante que o RAG de português esteja pronto
        if not local_portuguese_rag.vectorstore:
            if not local_portuguese_rag.load_existing_vectorstore():
                if not local_portuguese_rag.process_portuguese_documents():
                    return "❌ Erro ao processar materiais de português."
        
        if not local_portuguese_rag.rag_chain:
            local_portuguese_rag.create_rag_chain(api_key)
        
        # Gera a resposta para a pergunta de português
        result = local_portuguese_rag.get_response(question)
        response = result["answer"]
        
        # Limpa memória
        local_portuguese_rag.clear_memory()
        
        return response
        
    except Exception as e:
        return f"❌ Erro ao gerar resposta de português: {str(e)}" 