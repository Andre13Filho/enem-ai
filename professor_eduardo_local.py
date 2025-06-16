import streamlit as st
from local_history_rag import history_rag_system
import os
from encoding_utils import safe_str

def setup_professor_eduardo_local_ui():
    """Configura interface do Professor Eduardo (História Local)"""
    
    st.markdown("### 🏛️ Professor Eduardo - História")
    st.markdown("**Sistema RAG Local com base de conhecimento em História**")
    
    # Status do sistema RAG
    with st.expander("📊 Status do Sistema", expanded=False):
        if history_rag_system.embeddings is None:
            st.error("❌ Sistema de embeddings não inicializado")
            return
        
        # Informações sobre documentos
        docs_path = history_rag_system.history_folder_path
        if os.path.exists(docs_path):
            if os.listdir(docs_path):
                st.success(f"✅ Pasta de história encontrada com {len(os.listdir(docs_path))} arquivos")
            else:
                st.warning("⚠️ Pasta de história está vazia")
        else:
            st.error("❌ Pasta 'historia' não encontrada")
        
        # Status do vectorstore
        vectorstore_path = history_rag_system.persist_directory
        if os.path.exists(vectorstore_path):
            st.success("✅ Base de conhecimento (vectorstore) existe")
        else:
            st.info("ℹ️ Base de conhecimento será criada no primeiro uso")
    
    # Controles do sistema
    with st.expander("🔧 Controles do Sistema", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Recriar Base", help="Reprocessa todos os documentos"):
                with st.spinner("Recriando base de conhecimento..."):
                    success = history_rag_system.process_history_documents()
                    if success:
                        st.success("✅ Base recriada com sucesso!")
                    else:
                        st.error("❌ Erro ao recriar base")
        
        with col2:
            if st.button("🏛️ Testar Sistema", help="Testa uma consulta simples"):
                with st.spinner("Testando sistema..."):
                    test_query = "O que foi a Revolução Francesa?"
                    try:
                        # Inicializa vectorstore se necessário
                        if not history_rag_system.vectorstore:
                            history_rag_system.load_existing_vectorstore()
                        
                        docs = history_rag_system.search_relevant_content(test_query, k=1)
                        if docs:
                            st.success(f"✅ Sistema funcionando! Encontrou {len(docs)} documento(s)")
                        else:
                            st.warning("⚠️ Sistema funcionando, mas nenhum documento encontrado")
                    except Exception as e:
                        st.error(f"❌ Erro no teste: {safe_str(e)}")
    
    # Dicas de uso
    with st.expander("💡 Dicas de Uso", expanded=False):
        st.markdown("""
        **Professor Eduardo - Especialista em História:**
        - 🏛️ Acesso direto aos seus materiais de história
        - 🎬 Usa analogias das suas séries favoritas (FRIENDS, Big Bang Theory, etc.)
        - 📚 Baseado nos documentos da pasta `/historia`
        - 🎯 Foco total no ENEM
        - 💬 Linguagem adequada para jovens de 17 anos
        
        **Exemplos de perguntas:**
        - "O que foi a Revolução Francesa?"
        - "Explique o período colonial brasileiro"
        - "Como funcionava o feudalismo?"
        - "O que causou a Primeira Guerra Mundial?"
        - "Explique a Era Vargas"
        """)

def get_professor_eduardo_local_response(user_message: str, api_key: str) -> str:
    """Gera resposta do Professor Eduardo usando RAG local"""
    
    try:
        # Verifica se RAG chain existe, se não, cria
        if not history_rag_system.rag_chain:
            # Carrega vectorstore se necessário
            if not history_rag_system.vectorstore:
                success = history_rag_system.load_existing_vectorstore()
                if not success:
                    # Se não existe, processa documentos
                    success = history_rag_system.process_history_documents()
                    if not success:
                        return """
❌ **Erro ao inicializar sistema de história**

Não foi possível carregar a base de conhecimento. Verifique:
1. Se a pasta `historia` existe e contém documentos
2. Se as dependências estão instaladas
3. Se há espaço em disco suficiente

💡 Use os controles na barra lateral para diagnóstico.
"""
            
            # Cria chain RAG
            history_rag_system.create_rag_chain(api_key)
        
        # Gera resposta usando RAG
        result = history_rag_system.get_response(user_message)
        response = result.get("answer", "❌ Erro ao gerar resposta")
        
        # Aplica formatação específica de história
        try:
            from history_formatter import format_history_response
            response = format_history_response(response)
        except ImportError:
            pass
            
        return response
        
    except Exception as e:
        error_msg = safe_str(e)
        return f"""
❌ **Erro no Professor Eduardo**

Detalhes do erro: {error_msg}

💡 **Possíveis soluções:**
1. Verifique se a pasta `historia` contém documentos
2. Reinstale as dependências: `pip install langchain chromadb sentence-transformers`
3. Verifique sua conexão com a internet
4. Tente recriar a base de conhecimento na barra lateral
""" 