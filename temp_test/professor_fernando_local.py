"""
Professor Fernando com Sistema RAG Local
Usa índice FAISS para física em vez de processar documentos locais
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

# Importa sistema RAG local
try:
    from local_physics_rag_fixed import get_local_physics_rag_instance
    from enem_exercises_rag import ENEMExercisesRAG
    LOCAL_RAG_AVAILABLE = True
except ImportError:
    LOCAL_RAG_AVAILABLE = False
    print("❌ Erro ao importar local_physics_rag_fixed.py")

# Importa sistema de analogias da Sther V2
try:
    from new_analogies_system import add_analogy_if_confused
    ANALOGIAS_AVAILABLE = True
    print("✅ Sistema de analogias V2 baseado nas séries carregado")
except ImportError:
    ANALOGIAS_AVAILABLE = False
    print("⚠️ Sistema de analogias da Sther não disponível")

class ProfessorFernandoLocal:
    """Professor Fernando especializado usando índice FAISS de física"""
    
    def __init__(self):
        self.rag_system = None
        self.exercises_rag = None
        self.current_api_key = None
        self.is_initialized = False
        
        if LOCAL_RAG_AVAILABLE:
            self.rag_system = get_local_physics_rag_instance()
            self.exercises_rag = ENEMExercisesRAG()
            print("✅ RAG System para física inicializado")
    
    def initialize_system(self, api_key: str) -> bool:
        """
        Inicializa o sistema RAG baixando o índice FAISS remoto e configurando a cadeia.
        """
        if not LOCAL_RAG_AVAILABLE:
            st.error("O arquivo 'local_physics_rag_fixed.py' é essencial e não foi encontrado.")
            return False
        
        if self.is_initialized and self.current_api_key == api_key:
            st.success("✅ Sistema de Física já inicializado.")
            return True

        st.info("🔄 Inicializando sistema de física (Professor Fernando)...")
        
        try:
            # A função `initialize` cuida de tudo: download, carregamento e criação da cadeia.
            success = self.rag_system.initialize(api_key)
            
            if success:
                self.current_api_key = api_key
                self.is_initialized = True
                st.success("✅ Professor Fernando (Física) pronto!")
                # Atualiza o estado da sessão para refletir a inicialização bem-sucedida
                st.session_state.rag_initialized_fernando = True
                return True
            else:
                st.error("❌ Falha ao inicializar o sistema de Física.")
                st.warning("O Professor Fernando pode não responder corretamente.")
                self.is_initialized = False
                st.session_state.rag_initialized_fernando = False
                return False
                    
        except Exception as e:
            st.error(f"❌ Ocorreu um erro crítico durante a inicialização: {str(e)}")
            self.is_initialized = False
            st.session_state.rag_initialized_fernando = False
            return False
    
    def get_response(self, user_message: str, api_key: str) -> str:
        """Gera uma resposta para a mensagem do usuário."""
        
        if not LOCAL_RAG_AVAILABLE:
            return """
🚧 **Sistema RAG Local Indisponível**

O sistema RAG local não está disponível. Verifique:
1. Arquivo local_physics_rag_fixed.py presente
2. Dependências instaladas: `pip install -r requirements.txt`

💡 O sistema funciona com um índice FAISS pré-construído!
"""
        
        if not api_key or api_key.strip() == "":
            return """
🔑 **API Key da Groq Necessária**

Para ativar o Professor Fernando com RAG Local:
1. Configure a secret GROQ_API_KEY no Streamlit Cloud
2. O sistema baixará o índice FAISS e inicializará automaticamente!

📚 **Recursos do Sistema RAG Local:**
- Índice FAISS pré-construído (baixado automaticamente)
- Busca semântica inteligente com respostas formatadas
- Memória conversacional
- Modelo DeepSeek R1 Distill 70B
"""
        
        # Inicializa sistema se necessário
        if not self.is_initialized:
            try:
                st.info("🔧 Iniciando processo de inicialização...")
                init_success = self.initialize_system(api_key)
                
                if not init_success:
                    st.error("❌ Falha na inicialização - detalhes:")
                    st.error(f"• RAG System: {self.rag_system is not None}")
                    st.error(f"• Sistema inicializado: {self.is_initialized}")
                    
                    # Tenta reinicializar com força
                    st.warning("🔄 Tentando reinicializar o sistema...")
                    
                    # Força limpeza e reinicialização
                    try:
                        # Limpa a pasta FAISS_INDEX_DIR para forçar um novo download
                        import shutil
                        from local_physics_rag_fixed import FAISS_INDEX_DIR
                        
                        if os.path.exists(FAISS_INDEX_DIR):
                            try:
                                shutil.rmtree(FAISS_INDEX_DIR)
                                st.info("📥 Pasta do índice FAISS excluída. Baixando novamente...")
                            except Exception as e:
                                st.error(f"❌ Erro ao excluir pasta do índice: {str(e)}")
                        
                        # Tenta inicializar novamente
                        second_try = self.initialize_system(api_key)
                        
                        if second_try:
                            st.success("✅ Sistema inicializado com sucesso na segunda tentativa!")
                            return self.get_response(user_message, api_key)
                    except Exception as retry_error:
                        st.error(f"❌ Falha na segunda tentativa: {str(retry_error)}")
                    
                    return f"""
❌ **Falha na Inicialização do Sistema RAG**

O sistema não conseguiu acessar o índice de física. Por favor, tente novamente mais tarde ou entre em contato com o suporte.

**Detalhes técnicos:**
- Não foi possível baixar ou carregar o índice FAISS
- Verifique sua conexão com a internet
- Tente reiniciar a aplicação

Para ajuda imediata com sua pergunta sobre física, por favor reformule sua pergunta com mais detalhes ou consulte um dos outros professores disponíveis.
"""
                else:
                    st.success("✅ Inicialização concluída com sucesso!")
                    
            except Exception as init_error:
                st.error(f"❌ Erro crítico na inicialização: {str(init_error)}")
                import traceback
                st.error(f"Stack trace: {traceback.format_exc()}")
                
                # Tenta reinicializar com força
                st.warning("🔄 Tentando reinicializar após erro crítico...")
                
                # Força limpeza e reinicialização
                try:
                    # Limpa a pasta FAISS_INDEX_DIR para forçar um novo download
                    import shutil
                    from local_physics_rag_fixed import FAISS_INDEX_DIR
                    
                    if os.path.exists(FAISS_INDEX_DIR):
                        try:
                            shutil.rmtree(FAISS_INDEX_DIR)
                            st.info("📥 Pasta do índice FAISS excluída. Baixando novamente...")
                        except Exception as e:
                            st.error(f"❌ Erro ao excluir pasta do índice: {str(e)}")
                    
                    # Tenta inicializar novamente com delay
                    import time
                    time.sleep(2)
                    second_try = self.initialize_system(api_key)
                    
                    if second_try:
                        st.success("✅ Sistema recuperado com sucesso após erro crítico!")
                        return self.get_response(user_message, api_key)
                except Exception as retry_error:
                    st.error(f"❌ Falha na recuperação: {str(retry_error)}")
                
                return f"""
❌ **Erro Crítico na Inicialização**

Ocorreu um erro durante a inicialização do sistema. Por favor, tente novamente mais tarde ou entre em contato com o suporte.

**Detalhes técnicos:**
- Erro: {str(init_error)}
- Não foi possível acessar o índice FAISS
- Verifique sua conexão com a internet
- Tente reiniciar a aplicação

Para ajuda imediata com sua pergunta sobre física, por favor consulte um dos outros professores disponíveis ou tente novamente mais tarde.
"""
        
        try:
            # Gera resposta usando RAG
            result = self.rag_system.get_response(user_message)
            
            answer = result.get("answer", "Desculpe, não consegui gerar uma resposta.")
            source_docs = result.get("source_documents", [])
            
            # Verifica se há problemas na resposta
            if ("Erro na API" in answer or "Error code: 401" in answer or "Invalid API Key" in answer or 
                "Sistema RAG não inicializado" in answer):
                
                # Tenta reinicializar o sistema
                st.warning("🔄 Detectado problema com a API. Tentando reinicializar...")
                self.is_initialized = False
                
                # Tenta inicializar novamente
                try:
                    init_success = self.initialize_system(api_key)
                    if init_success:
                        # Tenta novamente com o sistema reinicializado
                        result = self.rag_system.get_response(user_message)
                        new_answer = result.get("answer", "")
                        
                        # Verifica se a nova resposta não tem erros
                        if not any(err in new_answer for err in ["Erro na API", "Error code: 401", "Invalid API Key"]):
                            source_docs = result.get("source_documents", [])
                            answer = new_answer
                        else:
                            # Se ainda houver erro, retorna mensagem de erro técnico
                            return f"""
🔑 **Problema com a API Key da Groq**

Não foi possível conectar à API do Groq. Por favor, verifique se sua API Key está correta e tente novamente.

**Detalhes técnicos:**
- Erro: {answer}
- Verifique se a API Key está configurada corretamente
- Tente novamente mais tarde

Para ajuda imediata, entre em contato com o suporte.
"""
                except Exception:
                    # Se falhar a reinicialização, retorna mensagem de erro
                    return f"""
🔑 **Problema com a API Key da Groq**

Não foi possível conectar à API do Groq. Por favor, verifique se sua API Key está correta e tente novamente.

**Detalhes técnicos:**
- Erro: {answer}
- Verifique se a API Key está configurada corretamente
- Tente novamente mais tarde

Para ajuda imediata, entre em contato com o suporte.
"""
            
            # Resposta formatada
            response = f"""
{answer}

---

📚 **Materiais Consultados:**
"""
            
            # Adiciona informações das fontes
            sources_added = set()
            for doc in source_docs[:3]:  # Máximo 3 fontes
                source_name = doc.metadata.get("source", "Documento desconhecido")
                topic = doc.metadata.get("topic", "Tópico geral")
                
                if source_name not in sources_added:
                    response += f"\n• {topic} - {source_name}"
                    sources_added.add(source_name)
            
            if not sources_added:
                response += "\n• Base de conhecimento geral de física"
            
            # SEMPRE adiciona exercícios recomendados
            response += self._add_recommended_exercises(user_message)
            
            # SISTEMA DE ANALOGIAS V2 - SÉRIES PERSONALIZADAS
            # SEMPRE tenta adicionar analogias, mesmo se houve erro na API
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
            # Registra o erro para debugging
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Erro ao processar resposta: {error_details}")
            
            # Tenta reinicializar o sistema
            try:
                st.warning("🔄 Ocorreu um erro. Tentando reinicializar o sistema...")
                self.is_initialized = False
                
                # Força reinicialização
                init_success = self.initialize_system(api_key)
                if init_success:
                    # Tenta novamente com o sistema reinicializado
                    try:
                        result = self.rag_system.get_response(user_message)
                        answer = result.get("answer", "")
                        source_docs = result.get("source_documents", [])
                        
                        # Constrói resposta normal
                        response = f"""
{answer}

---

📚 **Materiais Consultados:**
"""
                        # Adiciona fontes e exercícios
                        sources_added = set()
                        for doc in source_docs[:3]:
                            source_name = doc.metadata.get("source", "Documento desconhecido")
                            topic = doc.metadata.get("topic", "Tópico geral")
                            if source_name not in sources_added:
                                response += f"\n• {topic} - {source_name}"
                                sources_added.add(source_name)
                        
                        if not sources_added:
                            response += "\n• Base de conhecimento geral de física"
                        
                        response += self._add_recommended_exercises(user_message)
                        
                        return response
                    except:
                        pass
            except:
                pass
            
            # Se todas as tentativas falharem, retorna mensagem de erro técnico
            error_response = f"""
❌ **Erro Técnico**

Ocorreu um erro ao processar sua pergunta. Por favor, tente novamente mais tarde.

**Detalhes técnicos:**
- Erro: {str(e)}
- Verifique sua conexão com a internet
- Tente reiniciar a aplicação

Para ajuda imediata, entre em contato com o suporte.
"""
            
            # MESMO COM ERRO, tenta aplicar analogias se usuário está confuso
            if ANALOGIAS_AVAILABLE:
                try:
                    enhanced_error_response = add_analogy_if_confused(user_message, error_response)
                    if enhanced_error_response != error_response:
                        error_response = enhanced_error_response
                        error_response += "\n\n🎬 *Pelo menos as analogias funcionam! 😊*"
                except Exception as analogy_error:
                    print(f"⚠️ Erro no sistema de analogias: {analogy_error}")
            
            return error_response
    
    def get_relevant_content_preview(self, query: str) -> str:
        """Mostra prévia do conteúdo que seria recuperado"""
        if not self.rag_system or not self.is_initialized:
            return "Sistema não inicializado"
        
        try:
            docs = self.rag_system.search_relevant_content(query, k=3)
            
            if not docs:
                return "Nenhum conteúdo relevante encontrado"
                
            preview = f"**Prévia de conteúdo relevante para:** '{query}'\n\n"
            
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get("source", "Desconhecido")
                preview += f"**Documento {i} - {source}:**\n"
                preview += f"{doc.page_content[:150]}...\n\n"
                
            return preview
            
        except Exception as e:
            return f"Erro ao buscar conteúdo: {str(e)}"
    
    def _add_recommended_exercises(self, user_message: str) -> str:
        """Adiciona exercícios do ENEM recomendados"""
        if not self.exercises_rag:
            return "\n\n💡 Sistema de exercícios não disponível."
            
        try:
            # Tenta extrair tópico da mensagem
            message_lower = user_message.lower()
            
            # Mapeia palavras-chave de física para tópicos
            physics_keywords = {
                # Mecânica
                "cinemática": "Mecânica",
                "movimento": "Mecânica",
                "velocidade": "Mecânica",
                "aceleração": "Mecânica",
                "queda livre": "Mecânica",
                "mru": "Mecânica",
                "mruv": "Mecânica",
                "força": "Mecânica",
                "newton": "Mecânica",
                "atrito": "Mecânica",
                "impulso": "Mecânica",
                "quantidade de movimento": "Mecânica",
                "trabalho": "Mecânica",
                "potência": "Mecânica",
                "energia": "Mecânica",
                "cinética": "Mecânica",
                "potencial": "Mecânica",
                "conservação": "Mecânica",
                
                # Termodinâmica
                "termodinâmica": "Termodinâmica",
                "calor": "Termodinâmica",
                "temperatura": "Termodinâmica",
                "dilatação": "Termodinâmica",
                "gases": "Termodinâmica",
                "máquina térmica": "Termodinâmica",
                
                # Eletricidade e Magnetismo
                "eletricidade": "Eletromagnetismo",
                "carga": "Eletromagnetismo",
                "corrente": "Eletromagnetismo",
                "resistência": "Eletromagnetismo",
                "tensão": "Eletromagnetismo",
                "voltagem": "Eletromagnetismo",
                "circuito": "Eletromagnetismo",
                "potência elétrica": "Eletromagnetismo",
                "campo elétrico": "Eletromagnetismo",
                "magnetismo": "Eletromagnetismo",
                "campo magnético": "Eletromagnetismo",
                "indução": "Eletromagnetismo",
                
                # Ondulatória
                "onda": "Ondulatória",
                "frequência": "Ondulatória",
                "comprimento de onda": "Ondulatória",
                "som": "Ondulatória",
                "acústica": "Ondulatória",
                "óptica": "Ondulatória",
                "reflexão": "Ondulatória",
                "refração": "Ondulatória",
                "espelho": "Ondulatória",
                "lente": "Ondulatória",
                
                # Física Moderna
                "relatividade": "Física Moderna",
                "quântica": "Física Moderna",
                "dualidade": "Física Moderna",
                "fóton": "Física Moderna",
                "efeito fotoelétrico": "Física Moderna",
            }
            
            # Busca tópicos identificados
            identified_topics = []
            for keyword, topic in physics_keywords.items():
                if keyword in message_lower:
                    identified_topics.append(topic)
            
            # Remove duplicatas
            identified_topics = list(set(identified_topics))
            
            # Se não identificou tópicos, tenta extrair do conteúdo
            if not identified_topics:
                identified_topics = ["Física Geral"]
            
            # Busca exercícios para cada tópico
            exercises_content = "\n\n📝 **Exercícios Relacionados do ENEM:**\n"
            exercises_found = False
            
            for topic in identified_topics[:2]:  # Máximo 2 tópicos
                try:
                    exercises = self.exercises_rag.search_exercises_by_topic(topic, "Ciências da Natureza", k=1)
                    
                    if exercises:
                        exercises_found = True
                        exercise = exercises[0]
                        year = exercise.metadata.get("year", "Ano desconhecido")
                        question_num = exercise.metadata.get("question_number", "")
                        
                        # Limita o comprimento do exercício
                        content = exercise.page_content
                        if len(content) > 300:
                            content = content[:300] + "..."
                            
                        exercises_content += f"""
**Exercício ENEM {year} - Questão {question_num} ({topic})**
{content}

"""
                except Exception as ex_error:
                    print(f"Erro ao buscar exercício para {topic}: {str(ex_error)}")
            
            if not exercises_found:
                exercises_content = "\n\n💡 **Quer praticar?** Me peça exercícios específicos sobre este assunto do ENEM!"
                
            return exercises_content
            
        except Exception as e:
            print(f"Erro ao adicionar exercícios: {str(e)}")
            return "\n\n💡 **Quer praticar?** Me peça exercícios específicos sobre este assunto do ENEM!"
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da base de conhecimento"""
        if not self.rag_system:
            return {"status": "não disponível"}
        
        try:
            return self.rag_system.get_stats()
        except Exception as e:
            return {"erro": str(e)}
    
    def clear_memory(self):
        """Limpa memória conversacional"""
        if self.rag_system and hasattr(self.rag_system, "clear_memory"):
            self.rag_system.clear_memory()
    
    def reprocess_documents(self, api_key: str) -> bool:
        """Força reinicialização do sistema RAG"""
        if not self.rag_system:
            return False
        
        try:
            st.info("🔄 Forçando reinicialização do sistema...")
            
            # Limpa a pasta FAISS_INDEX_DIR para forçar um novo download
            import shutil
            from local_physics_rag_fixed import FAISS_INDEX_DIR
            
            if os.path.exists(FAISS_INDEX_DIR):
                try:
                    shutil.rmtree(FAISS_INDEX_DIR)
                    st.info("📥 Pasta do índice FAISS excluída. Baixando novamente...")
                except Exception as e:
                    st.error(f"❌ Erro ao excluir pasta do índice: {str(e)}")
            
            # Reinicializa o sistema
            self.is_initialized = False
            self.rag_system.is_initialized = False
            self.rag_system.vectorstore = None
            self.rag_system.retriever = None
            self.rag_system.rag_chain = None
            self.rag_system.embeddings = None
            
            # Tenta inicializar novamente
            success = self.initialize_system(api_key)
            
            if success:
                self.current_api_key = api_key
                st.success("✅ Sistema reinicializado com sucesso!")
                return True
            else:
                st.error("❌ Falha na reinicialização")
                return False
                
        except Exception as e:
            st.error(f"Erro na reinicialização: {str(e)}")
            return False
            
    def search_exercises(self, topic: str, subject_area: str = None, k: int = 3) -> List[Dict[str, Any]]:
        """Busca exercícios do ENEM relacionados ao tópico"""
        if not self.exercises_rag:
            return []
        
        try:
            # Carrega vectorstore de exercícios se necessário
            if not self.exercises_rag.vectorstore:
                self.exercises_rag.load_existing_vectorstore()
            
            # Busca exercícios
            docs = self.exercises_rag.search_exercises_by_topic(topic, subject_area, k)
            
            exercises = []
            for doc in docs:
                exercise = {
                    "content": doc.page_content,
                    "year": doc.metadata.get("year", "N/A"),
                    "question_number": doc.metadata.get("question_number", "N/A"),
                    "subject_area": doc.metadata.get("subject_area", "N/A"),
                    "topic": doc.metadata.get("topic", "N/A"),
                    "source_file": doc.metadata.get("source_file", "N/A")
                }
                exercises.append(exercise)
            
            return exercises
            
        except Exception as e:
            print(f"Erro ao buscar exercícios: {str(e)}")
            return []

# Instância global do Professor Fernando Local
professor_fernando_local = ProfessorFernandoLocal()

def setup_professor_fernando_local_ui():
    """Configura UI específica do Professor Fernando Local (barra lateral)"""
    pass

def get_professor_fernando_local_response(user_message: str, api_key: str) -> str:
    """Função para obter resposta do Professor Fernando Local"""
    return professor_fernando_local.get_response(user_message, api_key)

def preview_local_search(query: str) -> str:
    """Preview do conteúdo que seria recuperado"""
    return professor_fernando_local.get_relevant_content_preview(query) 