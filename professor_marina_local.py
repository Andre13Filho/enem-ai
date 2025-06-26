#!/usr/bin/env python3
"""
Professora Marina - Sistema RAG Local para Geografia
A.T.E.N.A. - Interface integrada com Streamlit
"""

import streamlit as st
import time
from typing import Dict, Any, List
import os

# Importa sistema RAG de geografia
try:
    from local_geography_rag import local_geography_rag
    GEOGRAPHY_RAG_AVAILABLE = True
except ImportError:
    GEOGRAPHY_RAG_AVAILABLE = False

def setup_professor_marina_local_ui():
    """Configura interface da Professora Marina"""
    
    if not GEOGRAPHY_RAG_AVAILABLE:
        st.error("❌ Sistema RAG Local de Geografia não disponível. Verifique as dependências.")
        return
    
    st.markdown("### 📚 Materiais de Geografia")
    
    # Verifica se a pasta existe
    if not os.path.exists("./geografia"):
        st.warning("⚠️ Pasta 'geografia' não encontrada. Crie a pasta e adicione seus materiais.")
        return
    
    # Botão para processar documentos
    if st.button("🔄 Processar Materiais", key="process_geography"):
        with st.spinner("Processando materiais de geografia..."):
            success = local_geography_rag.process_geography_documents()
            if success:
                st.success("✅ Materiais processados com sucesso!")
            else:
                st.error("❌ Erro ao processar materiais")
    
    # Estatísticas
    stats = local_geography_rag.get_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documentos", stats["total_documentos"])
    with col2:
        st.metric("VectorStore", "✅" if stats["vectorstore_inicializado"] else "❌")
    with col3:
        st.metric("RAG Chain", "✅" if stats["rag_chain_configurada"] else "❌")

def get_professor_marina_local_response(question: str, api_key: str) -> str:
    """Gera resposta da Professora Marina usando RAG local"""
    
    if not GEOGRAPHY_RAG_AVAILABLE:
        return "❌ Sistema RAG Local de Geografia não está disponível. Verifique as dependências."
    
    if not api_key:
        return "🔑 Por favor, configure sua chave da API Groq para continuar."
    
    try:
        # Tenta carregar vectorstore existente
        if not local_geography_rag.vectorstore:
            if not local_geography_rag.load_existing_vectorstore():
                # Se não existir, processa documentos
                if not local_geography_rag.process_geography_documents():
                    return "❌ Erro ao processar materiais de geografia. Verifique se a pasta 'geografia' existe e contém documentos."
        
        # Configura RAG chain se necessário
        if not local_geography_rag.rag_chain:
            local_geography_rag.create_rag_chain(api_key)
        
        # Gera resposta
        result = local_geography_rag.get_response(question)
        response = result["answer"]
        
        # Aplica formatação específica de geografia
        try:
            from geography_formatter import format_geography_response
            response = format_geography_response(response)
        except ImportError:
            pass
        
        # Limpa memória após cada resposta
        local_geography_rag.clear_memory()
        
        return response
        
    except Exception as e:
        return f"❌ Erro ao gerar resposta: {str(e)}" 