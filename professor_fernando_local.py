"""
Professor Fernando com Sistema RAG Local
Usa documentos locais da pasta Física em vez da API do Google Drive
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from physics_formatter import format_professor_response

# Importa sistema RAG local
try:
    from local_physics_rag import get_local_physics_rag_instance
    from enem_exercises_rag import ENEMExercisesRAG
    from physics_formatter import format_professor_response
    LOCAL_RAG_AVAILABLE = True
    physics_FORMATTER_AVAILABLE = True
except ImportError:
    LOCAL_RAG_AVAILABLE = False
    physics_FORMATTER_AVAILABLE = False

# Importa sistema de analogias da Sther V2
try:
    from new_analogies_system import add_analogy_if_confused
    ANALOGIES_AVAILABLE = True
    print("✅ Sistema de analogias V2 baseado nas séries carregado")
except ImportError:
    ANALOGIES_AVAILABLE = False
    print("⚠️ Sistema de analogias da Sther não disponível")

class ProfessorFernandoLocal:
    """Professor Fernando especializado usando documentos locais"""
    
    def __init__(self):
        self.rag_system = None
        self.exercises_rag = None
        self.current_api_key = None
        self.is_initialized = False
        
    def initialize_system(self, api_key: str) -> bool:
        """
        Inicializa o sistema RAG e o cliente Groq
        
        Args:
            api_key: API key da Groq
            
        Returns:
            True se a inicialização for bem-sucedida, False caso contrário
        """
        if not LOCAL_RAG_AVAILABLE:
            st.error("O arquivo 'local_physics_rag.py' é essencial e não foi encontrado.")
            return False
        
        if self.is_initialized and self.current_api_key == api_key:
            st.success("✅ Sistema de Física já inicializado.")
            return True

        st.info("🔄 Inicializando sistema de Física (Professor Fernando)...")
        
        try:
            # A nova função `initialize` cuida de tudo: download, carregamento e criação da cadeia.
            success = self.rag_system.initialize(api_key)
            
            if success:
                self.current_api_key = api_key
                self.is_initialized = True
                self.client = OpenAI(api_key=api_key)
                st.success("✅ Professor Fernando (Física) pronto!")
                # Atualiza o estado da sessão para refletir a inicialização bem-sucedida
                st.session_state.rag_initialized_Fernando = True
                return True
            else:
                st.error("❌ Falha ao inicializar o sistema de Física.")
                st.warning("O Professor Fernando pode não responder corretamente.")
                self.is_initialized = False
                st.session_state.rag_initialized_Fernando = False
                return False
                    
        except Exception as e:
            st.error(f"❌ Ocorreu um erro crítico durante a inicialização: {str(e)}")
            self.is_initialized = False
            st.session_state.rag_initialized_Fernando = False
            return False
    
    def get_response(self, query: str, api_key: str = None, temperature: float = 0.2) -> str:
        """
        Obtém resposta do Professor Fernando para uma consulta
        
        Args:
            query: A consulta do usuário
            api_key: API key da Groq (opcional)
            temperature: Temperatura para geração de texto
            
        Returns:
            A resposta formatada do Professor Fernando
        """
        # Se uma nova API key for fornecida e for diferente da atual, reinicializa
        if api_key and api_key != self.current_api_key:
            self.initialize_system(api_key)
        
        if not self.is_initialized:
            return "⚠️ Sistema não inicializado. Por favor, configure a API key primeiro."
        
        try:
            # Usa o sistema RAG para obter a resposta
            result = self.rag_system.get_response(query)
            raw_response = result.get("answer", "")
            
            # Formata a resposta
            formatted_response = format_professor_response(raw_response)
            
            # Adiciona analogia se o sistema estiver disponível
            if ANALOGIAS_AVAILABLE:
                try:
                    enhanced_response = add_analogy_if_confused(user_message, response)
                    if enhanced_response != response:  # Se analogia foi adicionada
                        response = enhanced_response
                        response += "\n\n🎬 *Sistema de analogias com suas séries favoritas ativo! Friends, Grey's Anatomy, Stranger Things e mais...*"
                except Exception as analogy_error:
                    print(f"⚠️ Erro no sistema de analogias: {analogy_error}")
            
            return response
            
        except Exception as e:
            print(f"Erro ao obter resposta do Professor Fernando: {e}")
            return f"Desculpe, não consegui processar sua consulta no momento. Erro: {str(e)}"

# Instância global do Professor Fernando Local
professor_fernando_local = ProfessorFernandoLocal()

def setup_professor_fernando_local_ui():
    """Configura UI específica do Professor Fernando Local (barra lateral)"""
    st.title("Professor Fernando - Física")
    st.markdown("""
    ### 👨‍🔬 Professor Fernando
    
    Especialista em Física para o ENEM com mais de 20 anos de experiência.
    
    **Áreas de especialidade:**
    - Mecânica
    - Termodinâmica
    - Eletromagnetismo
    - Óptica
    - Física Moderna
    - Ondulatória
    
    Faça perguntas sobre conceitos físicos, resolução de problemas ou dúvidas sobre o ENEM.
    """)
    
    # Verifica se o sistema já está inicializado
    if "rag_initialized_fernando" not in st.session_state:
        st.session_state.rag_initialized_fernando = False
    
    # Campo para a pergunta do usuário
    query = st.text_area("Digite sua pergunta sobre Física:", height=100, key="query_fernando")
    
    if st.button("Enviar pergunta ao Professor Fernando", key="send_fernando"):
        if not query:
            st.warning("Por favor, digite uma pergunta.")
            return
        
        if not st.session_state.rag_initialized_fernando:
            st.error("⚠️ Sistema não inicializado. Configure a API key primeiro.")
            return
        
        with st.spinner("Professor Fernando está elaborando a resposta..."):
            api_key = st.session_state.get("api_key_fernando", None)
            response = professor_fernando_local.get_response(query, api_key)
            
        st.markdown("### Resposta do Professor Fernando:")
        st.markdown(response)

def get_professor_fernando_local_response(query: str, api_key: str = None) -> str:
    """Função para obter resposta do Professor Fernando para uso em outros módulos"""
    # Verifica se o sistema está inicializado
    if not professor_fernando_local.is_initialized:
        # Usa a API key fornecida ou tenta obter da sessão
        if api_key:
            professor_fernando_local.initialize_system(api_key)
        else:
            # Tenta inicializar com a API key da sessão
            session_api_key = st.session_state.get("openai_api_key", None)
            if session_api_key:
                professor_fernando_local.initialize_system(session_api_key)
            else:
                return "⚠️ Sistema não inicializado. Por favor, configure a API key primeiro."
    
    # Retorna a resposta
    return professor_fernando_local.get_response(query, api_key)

# Para teste direto
if __name__ == "__main__":
    # Configura a página Streamlit
    st.set_page_config(page_title="Professor Fernando - Física", layout="wide")
    
    # Configura a UI
    setup_professor_fernando_local_ui() 