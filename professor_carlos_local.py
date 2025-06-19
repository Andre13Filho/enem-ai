"""
Professor Carlos com Sistema RAG Local
Usa documentos locais da pasta matemática em vez da API do Google Drive
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

# Importa sistema RAG local
try:
    from local_math_rag import LocalMathRAG, local_math_rag
    from enem_exercises_rag import ENEMExercisesRAG
    from math_formatter import format_professor_response
    LOCAL_RAG_AVAILABLE = True
    MATH_FORMATTER_AVAILABLE = True
except ImportError:
    LOCAL_RAG_AVAILABLE = False
    MATH_FORMATTER_AVAILABLE = False

# Importa sistema de analogias da Sther V2
try:
    from new_analogies_system import add_analogy_if_confused
    ANALOGIES_AVAILABLE = True
    print("✅ Sistema de analogias V2 baseado nas séries carregado")
except ImportError:
    ANALOGIES_AVAILABLE = False
    print("⚠️ Sistema de analogias da Sther não disponível")

class ProfessorCarlosLocal:
    """Professor Carlos especializado usando documentos locais"""
    
    def __init__(self):
        self.rag_system = None
        self.exercises_rag = None
        self.current_api_key = None
        self.is_initialized = False
        
        if LOCAL_RAG_AVAILABLE:
            self.rag_system = local_math_rag
            self.exercises_rag = ENEMExercisesRAG()
    
    def initialize_system(self, api_key: str) -> bool:
        """
        Inicializa o sistema RAG baixando o índice FAISS remoto e configurando a cadeia.
        """
        if not LOCAL_RAG_AVAILABLE:
            st.error("O arquivo 'local_math_rag.py' é essencial e não foi encontrado.")
            return False
        
        if self.is_initialized and self.current_api_key == api_key:
            st.success("✅ Sistema de Matemática já inicializado.")
            return True

        st.info("🔄 Inicializando sistema de matemática (Professor Carlos)...")
        
        try:
            # A nova função `initialize` cuida de tudo: download, carregamento e criação da cadeia.
            success = self.rag_system.initialize(api_key)
            
            if success:
                self.current_api_key = api_key
                self.is_initialized = True
                st.success("✅ Professor Carlos (Matemática) pronto!")
                # Atualiza o estado da sessão para refletir a inicialização bem-sucedida
                st.session_state.rag_initialized_carlos = True
                return True
            else:
                st.error("❌ Falha ao inicializar o sistema de Matemática.")
                st.warning("O Professor Carlos pode não responder corretamente.")
                self.is_initialized = False
                st.session_state.rag_initialized_carlos = False
                return False
                    
        except Exception as e:
            st.error(f"❌ Ocorreu um erro crítico durante a inicialização: {str(e)}")
            self.is_initialized = False
            st.session_state.rag_initialized_carlos = False
            return False
    
    def get_response(self, user_message: str, api_key: str) -> str:
        """Gera uma resposta para a mensagem do usuário, assumindo que o sistema já está inicializado."""
        
        if not self.is_initialized:
            # Esta mensagem de erro agora indica um problema de fluxo no app.py
            return "❌ **Erro Crítico:** O sistema RAG foi chamado sem ter sido inicializado. Verifique a lógica de inicialização no `app.py`."

        if not self.rag_system or not self.rag_system.rag_chain:
            return "❌ **Erro Crítico:** O `rag_chain` não está disponível mesmo após a inicialização."

        try:
            # Gera resposta usando RAG
            result = self.rag_system.get_response(user_message)
            answer = result.get("answer", "Desculpe, não consegui gerar uma resposta.")
            
            # Formata a resposta final
            formatted_answer = format_professor_response(answer)
            
            # Adiciona analogia se a IA parecer confusa
            if ANALOGIES_AVAILABLE and ("não sei" in answer.lower() or "não tenho certeza" in answer.lower()):
                formatted_answer = add_analogy_if_confused(formatted_answer)
                
            return formatted_answer
            
        except Exception as e:
            return f"❌ **Erro durante a geração da resposta RAG:** {str(e)}"
    
    def get_relevant_content_preview(self, query: str) -> str:
        """Retorna uma prévia do conteúdo relevante da base de conhecimento."""
        if not self.rag_system or not self.is_initialized:
            return "Sistema não inicializado"
        
        try:
            docs = self.rag_system.search_relevant_content(query, k=3)
            if not docs:
                return "Nenhum conteúdo relevante encontrado"
            
            preview = "**Conteúdo relevante encontrado:**\n\n"
            for i, doc in enumerate(docs, 1):
                content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                source = doc.metadata.get("source", "Documento")
                topic = doc.metadata.get("topic", "Geral")
                
                preview += f"📚 **Fonte {i}** ({topic}):\n*{source}*\n{content_preview}\n\n"
            
            return preview
            
        except Exception as e:
            return f"Erro ao buscar conteúdo: {str(e)}"
    
    def _add_recommended_exercises(self, user_message: str) -> str:
        """Adiciona exercícios recomendados baseados na mensagem do usuário"""
        try:
            user_lower = user_message.lower()
            
            # Detecta se Sther está EXPLICITAMENTE pedindo exercícios
            exercise_request_keywords = [
                'exercício', 'exercicios', 'questão', 'questões', 'questao', 'questoes',
                'praticar', 'treinar', 'resolver', 'fazer exercício', 'atividade',
                'me dê', 'me de', 'quero', 'preciso', 'tem exercício', 'tem questão'
            ]
            
            is_asking_for_exercises = any(keyword in user_lower for keyword in exercise_request_keywords)
            
            if is_asking_for_exercises:
                # Sther está pedindo exercícios - busca com mais prioridade
                exercises = self.search_exercises_by_message(user_message, k=3)
                
                if exercises:
                    exercises_text = """

---

📚 **Exercícios ENEM - Conforme solicitado!**

Perfeito, Sther! Aqui estão os exercícios que você pediu:

"""
                    
                    for i, exercise in enumerate(exercises, 1):
                        year = exercise["year"] 
                        question_num = exercise["question_number"]
                        topic = exercise["topic"]
                        
                        # Limita o conteúdo para não sobrecarregar
                        content = exercise["content"].strip()
                        if len(content) > 800:
                            content = content[:800] + "\n\n[...continua - me peça para ver o resto se precisar!]"
                        
                        exercises_text += f"""
**📝 Exercício {i} - ENEM {year} (Questão {question_num})**
*Tópico: {topic}*

{content}

*💬 Quer que eu explique alguma parte? É só perguntar!*

---
"""
                    
                    exercises_text += """
🎯 **Dica:** Leia com calma, tente resolver primeiro e depois me pergunte se tiver dúvidas! 💪
"""
                    
                    return exercises_text
                
                else:
                    # Sther pediu exercícios mas não encontrou nada específico
                    return """

---

❌ **Não encontrei exercícios específicos**

Desculpe, Sther! Não encontrei exercícios exatos sobre esse tópico na base ENEM.

💡 **Tente reformular assim:**
- "Exercícios de Geometria"
- "Questões de Funções" 
- "Exercícios do ENEM 2024"
- "Problemas de Probabilidade"

📚 **Ou me pergunte sobre a teoria primeiro** que eu explico e depois trago exercícios relacionados!
"""
            
            else:
                # Pergunta normal - apenas sugere exercícios sutilmente
                exercises = self.search_exercises_by_message(user_message, k=1)
                
                if exercises:
                    exercise = exercises[0]
                    year = exercise["year"]
                    topic = exercise["topic"]
                    
                    return f"""

---

💡 **Sugestão de Prática**

Para fixar esse conteúdo, que tal resolver um exercício do ENEM {year} sobre {topic}? 
Se quiser, é só me pedir: "Professor, me dê exercícios sobre {topic.lower()}"! 

🚀 Prática é fundamental!
"""
                
                else:
                    return """

---

💡 **Sugestão de Prática**

Para fixar bem esse conteúdo, sempre recomendo praticar com exercícios! 
Me peça exercícios específicos quando quiser treinar! 🚀
"""
                
        except Exception as e:
            # Em caso de erro, retorna sugestão simples
            return """

---

💡 **Prática recomendada**

Para fixar o conteúdo, sempre recomendo exercícios! Me pergunte quando quiser praticar! 💪
"""