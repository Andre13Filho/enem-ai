#!/usr/bin/env python3
"""
Professora Luciana - Sistema RAG Local para Química
A.T.E.N.A. - Interface integrada com Streamlit
"""

import streamlit as st
import time
from typing import Dict, Any, List
import os

# Importa sistema RAG de química
try:
    from local_chemistry_rag import local_chemistry_rag
    CHEMISTRY_RAG_AVAILABLE = True
except ImportError:
    CHEMISTRY_RAG_AVAILABLE = False

def setup_professor_luciana_local_ui():
    """Configura interface da Professora Luciana com RAG local"""
    
    st.markdown("""
    <div class="teacher-intro">
        <h3>⚗️ Professora Luciana - Química ENEM</h3>
        <p>Sistema RAG Local com seus documentos de química</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not CHEMISTRY_RAG_AVAILABLE:
        st.error("❌ Sistema RAG Local de Química Indisponível")
        st.info("Verifique se as dependências estão instaladas: langchain, chromadb, sentence-transformers")
        return None
    
    # Verifica se há documentos processados
    if not local_chemistry_rag.documents:
        st.warning("⚠️ Nenhum documento de química foi processado ainda.")
        
        # Botão para processar documentos
        if st.button("📁 Processar Documentos de Química"):
            with st.spinner("Processando documentos de química..."):
                success = local_chemistry_rag.process_chemistry_documents()
                if success:
                    st.success("✅ Documentos de química processados com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao processar documentos de química")
        return None
    
    # Mostra estatísticas da base de conhecimento
    stats = local_chemistry_rag.get_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📚 Documentos",
            value=stats["total_documentos"]
        )
    
    with col2:
        st.metric(
            label="🎯 Tópicos",
            value=stats["topicos_unicos"]
        )
    
    with col3:
        st.metric(
            label="💾 RAG Status",
            value="✅ Ativo" if stats["vectorstore_inicializado"] else "❌ Inativo"
        )
    
    # Mostra lista de tópicos disponíveis
    if stats["lista_topicos"]:
        with st.expander("📋 Tópicos de Química Disponíveis"):
            topics_per_row = 3
            topic_chunks = [stats["lista_topicos"][i:i+topics_per_row] 
                          for i in range(0, len(stats["lista_topicos"]), topics_per_row)]
            
            for chunk in topic_chunks:
                cols = st.columns(topics_per_row)
                for i, topic in enumerate(chunk):
                    with cols[i]:
                        st.info(f"⚗️ {topic}")
    
    # Área de busca rápida
    with st.expander("🔍 Busca Rápida nos Materiais"):
        search_query = st.text_input("Buscar conceito específico:", placeholder="Ex: ácidos, bases, reações")
        
        if search_query:
            with st.spinner("Buscando..."):
                docs = local_chemistry_rag.search_relevant_content(search_query, k=3)
                
                if docs:
                    st.success(f"✅ Encontrados {len(docs)} resultados relevantes:")
                    
                    for i, doc in enumerate(docs, 1):
                        with st.container():
                            st.markdown(f"**📄 Resultado {i}:**")
                            st.markdown(f"*Fonte: {doc.metadata.get('filename', 'N/A')}*")
                            st.markdown(f"*Tópico: {doc.metadata.get('topic', 'N/A')}*")
                            
                            # Mostra trecho do conteúdo
                            content_preview = doc.page_content[:300]
                            if len(doc.page_content) > 300:
                                content_preview += "..."
                            
                            st.markdown(f"```\n{content_preview}\n```")
                            st.markdown("---")
                else:
                    st.warning("🔍 Nenhum resultado encontrado para sua busca")
    
    return local_chemistry_rag

def get_professor_luciana_local_response(user_message: str, api_key: str) -> str:
    """Gera resposta da Professora Luciana usando RAG local"""
    
    if not CHEMISTRY_RAG_AVAILABLE:
        return "❌ Sistema RAG Local de Química não está disponível. Verifique as dependências."
    
    if not api_key:
        return "🔑 Por favor, configure sua chave da API Groq para continuar."
    
    try:
        # Configura chain RAG se necessário
        if not local_chemistry_rag.rag_chain:
            with st.spinner("Configurando sistema de IA..."):
                local_chemistry_rag.create_rag_chain(api_key)
        
        # Gera resposta
        with st.spinner("⚗️ Professora Luciana analisando sua pergunta..."):
            result = local_chemistry_rag.get_response(user_message)
            
            response = result.get("answer", "Desculpe, não consegui gerar uma resposta.")
            
            # Aplica formatação específica de química
            try:
                from chemistry_formatter import format_chemistry_response
                response = format_chemistry_response(response)
            except ImportError:
                pass
            
            # Adiciona informação sobre fontes se disponível
            source_docs = result.get("source_documents", [])
            if source_docs:
                sources = set()
                for doc in source_docs:
                    filename = doc.metadata.get("filename", "N/A")
                    topic = doc.metadata.get("topic", "N/A")
                    sources.add(f"{topic} ({filename})")
                
                if sources:
                    sources_text = "\n".join([f"- {source}" for source in sorted(sources)])
                    response += f"\n\n**📚 Fontes consultadas:**\n{sources_text}"
            
            return response
            
    except Exception as e:
        error_msg = f"Erro no sistema RAG de Química: {str(e)}"
        st.error(error_msg)
        return f"❌ {error_msg}"

def clear_chemistry_conversation():
    """Limpa histórico da conversa de química"""
    if CHEMISTRY_RAG_AVAILABLE and local_chemistry_rag.memory:
        local_chemistry_rag.clear_memory()
