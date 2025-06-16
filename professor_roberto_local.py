import streamlit as st
from local_biology_rag import biology_rag_system
import os
from encoding_utils import safe_str

def setup_professor_roberto_local_ui():
    """Configura interface do Professor Roberto (Biologia Local)"""
    
    st.markdown("### 🧬 Professor Roberto - Biologia")
    st.markdown("**Sistema RAG Local com base de conhecimento em Biologia**")
    
    # Status do sistema RAG
    with st.expander("📊 Status do Sistema", expanded=False):
        if biology_rag_system.embeddings is None:
            st.error("❌ Sistema de embeddings não inicializado")
            return
        
        # Informações sobre documentos
        docs_path = biology_rag_system.biology_folder_path
        if os.path.exists(docs_path):
            if os.listdir(docs_path):
                st.success(f"✅ Pasta de biologia encontrada com {len(os.listdir(docs_path))} arquivos")
            else:
                st.warning("⚠️ Pasta de biologia está vazia")
        else:
            st.error("❌ Pasta 'biologia' não encontrada")
        
        # Status do vectorstore
        vectorstore_path = biology_rag_system.persist_directory
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
                    success = biology_rag_system.process_biology_documents()
                    if success:
                        st.success("✅ Base recriada com sucesso!")
                    else:
                        st.error("❌ Erro ao recriar base")
        
        with col2:
            if st.button("🧪 Testar Sistema", help="Testa uma consulta simples"):
                with st.spinner("Testando sistema..."):
                    test_query = "O que é uma célula?"
                    try:
                        # Inicializa vectorstore se necessário
                        if not biology_rag_system.vectorstore:
                            biology_rag_system.load_existing_vectorstore()
                        
                        docs = biology_rag_system.search_relevant_content(test_query, k=1)
                        if docs:
                            st.success(f"✅ Sistema funcionando! Encontrou {len(docs)} documento(s)")
                        else:
                            st.warning("⚠️ Sistema funcionando, mas nenhum documento encontrado")
                    except Exception as e:
                        st.error(f"❌ Erro no teste: {safe_str(e)}")
    
    # Dicas de uso
    with st.expander("💡 Dicas de Uso", expanded=False):
        st.markdown("""
        **Professor Roberto - Especialista em Biologia:**
        - 🧬 Acesso direto aos seus materiais de biologia
        - 🎬 Usa analogias das suas séries favoritas (FRIENDS, Big Bang Theory, etc.)
        - 📚 Baseado nos documentos da pasta `/biologia`
        - 🎯 Foco total no ENEM
        - 💬 Linguagem adequada para jovens de 17 anos
        
        **Exemplos de perguntas:**
        - "Como funciona a fotossíntese?"
        - "Explique a divisão celular"
        - "O que é genética mendeliana?"
        - "Como funciona o sistema circulatório?"
        """)

def get_professor_roberto_local_response(user_message: str, api_key: str) -> str:
    """Gera resposta do Professor Roberto usando RAG local"""
    
    try:
        # Verifica se RAG chain existe, se não, cria
        if not biology_rag_system.rag_chain:
            # Carrega vectorstore se necessário
            if not biology_rag_system.vectorstore:
                success = biology_rag_system.load_existing_vectorstore()
                if not success:
                    # Se não existe, processa documentos
                    success = biology_rag_system.process_biology_documents()
                    if not success:
                        return """
❌ **Erro ao inicializar sistema de biologia**

Não foi possível carregar a base de conhecimento. Verifique:
1. Se a pasta `biologia` existe e contém documentos
2. Se as dependências estão instaladas
3. Se há espaço em disco suficiente

💡 Use os controles na barra lateral para diagnóstico.
"""
            
            # Cria chain RAG
            biology_rag_system.create_rag_chain(api_key)
        
        # Gera resposta usando RAG
        result = biology_rag_system.get_response(user_message)
        response = result.get("answer", "❌ Erro ao gerar resposta")
        
        # Aplica formatação específica de biologia
        try:
            from biology_formatter import format_biology_response
            response = format_biology_response(response)
        except ImportError:
            pass
            
        return response
        
    except Exception as e:
        error_msg = safe_str(e)
        return f"""
❌ **Erro no Professor Roberto**

Detalhes do erro: {error_msg}

💡 **Possíveis soluções:**
1. Verifique se a pasta `biologia` contém documentos
2. Reinstale as dependências: `pip install langchain chromadb sentence-transformers`
3. Verifique sua conexão com a internet
4. Tente recriar a base de conhecimento na barra lateral
""" 