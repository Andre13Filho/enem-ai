#!/usr/bin/env python3
"""
Professora Letícia - Sistema RAG Local para Língua Portuguesa
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

def setup_professor_leticia_local_ui():
    """Configura interface da Professora Letícia"""
    
    if not PORTUGUESE_RAG_AVAILABLE:
        st.error("❌ Sistema RAG Local de Língua Portuguesa não disponível. Verifique as dependências.")
        return
    
    st.markdown("### 📚 Materiais de Língua Portuguesa")
    
    # Verifica se a pasta existe
    if not os.path.exists("./Língua Portuguesa"):
        st.warning("⚠️ Pasta 'Língua Portuguesa' não encontrada. Crie a pasta e adicione seus materiais.")
        return
    
    # Botão para processar documentos
    if st.button("🔄 Processar Materiais", key="process_portuguese"):
        with st.spinner("Processando materiais de português..."):
            success = local_portuguese_rag.process_portuguese_documents()
            if success:
                st.success("✅ Materiais processados com sucesso!")
            else:
                st.error("❌ Erro ao processar materiais")
    
    # Estatísticas
    stats = local_portuguese_rag.get_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documentos", stats["total_documentos"])
    with col2:
        st.metric("VectorStore", "✅" if stats["vectorstore_inicializado"] else "❌")
    with col3:
        st.metric("RAG Chain", "✅" if stats["rag_chain_configurada"] else "❌")

def get_professor_leticia_local_response(question: str, api_key: str) -> str:
    """Gera resposta da Professora Letícia usando RAG local"""
    
    if not PORTUGUESE_RAG_AVAILABLE:
        return "❌ Sistema RAG Local de Língua Portuguesa não está disponível. Verifique as dependências."
    
    if not api_key:
        return "🔑 Por favor, configure sua chave da API Groq para continuar."
    
    try:
        # Tenta carregar vectorstore existente
        if not local_portuguese_rag.vectorstore:
            if not local_portuguese_rag.load_existing_vectorstore():
                # Se não existir, processa documentos
                if not local_portuguese_rag.process_portuguese_documents():
                    return "❌ Erro ao processar materiais de português. Verifique se a pasta 'Língua Portuguesa' existe e contém documentos."
        
        # Configura RAG chain se necessário
        if not local_portuguese_rag.rag_chain:
            local_portuguese_rag.create_rag_chain(api_key)
        
        # Gera resposta
        result = local_portuguese_rag.get_response(question)
        response = result["answer"]
        
        # Aplica formatação específica de português
        try:
            from portuguese_formatter import format_portuguese_response
            response = format_portuguese_response(response)
        except ImportError:
            pass
        
        # Limpa memória após cada resposta
        local_portuguese_rag.clear_memory()
        
        return response
        
    except Exception as e:
        return f"❌ Erro ao gerar resposta: {str(e)}" 