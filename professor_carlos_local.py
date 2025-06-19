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
        """Gera uma resposta para a mensagem do usuário."""
        
        if not LOCAL_RAG_AVAILABLE:
            return """
🚧 **Sistema RAG Local Indisponível**

O sistema RAG local não está disponível. Verifique:
1. Arquivo local_math_rag.py presente
2. Dependências instaladas: `pip install -r requirements.txt`

💡 O sistema funciona com documentos locais da pasta matemática!
"""
        
        if not api_key or api_key.strip() == "":
            return """
🔑 **API Key da Groq Necessária**

Para ativar o Professor Carlos com RAG Local:
1. Configure a secret GROQ_API_KEY no Streamlit Cloud
2. O sistema processará seus documentos locais automaticamente!

📚 **Recursos do Sistema RAG Local:**
- Processa documentos DOCX e PDF
- Busca semântica inteligente
- Memória conversacional
- Base totalmente local (sem Google Drive)
"""
        
        # Debug: Mostra informações da API key (apenas os primeiros caracteres)
        api_key_preview = api_key[:10] + "..." if len(api_key) > 10 else api_key
        
        # Inicializa sistema se necessário
        if not self.is_initialized or api_key != self.current_api_key:
            try:
                st.info("🔧 Iniciando processo de inicialização...")
                init_success = self.initialize_system(api_key)
                
                if not init_success:
                    st.error("❌ Falha na inicialização - detalhes:")
                    st.error(f"• RAG System: {self.rag_system is not None}")
                    st.error(f"• Pasta matemática: {self.rag_system.math_folder_path if self.rag_system else 'N/A'}")
                    st.error(f"• Sistema inicializado: {self.is_initialized}")
                    
                    return f"""
❌ **Falha na Inicialização do Sistema RAG**

O sistema não conseguiu inicializar corretamente.

**Debug Info:**
- API Key recebida: {api_key_preview}
- RAG System disponível: {self.rag_system is not None}
- Pasta matemática: {self.rag_system.math_folder_path if self.rag_system else 'N/A'}
- Sistema inicializado: {self.is_initialized}

**🚨 ATIVANDO MODO DE EMERGÊNCIA AVANÇADO:**

Olá, Sther! Sou o Professor Carlos, especialista em matemática do ENEM. 

Mesmo com problemas técnicos no sistema RAG, vou te ajudar com sua pergunta: "{user_message}"

**📚 Resposta baseada em conhecimento geral de matemática:**

Para determinar como resolver sua questão, preciso de mais detalhes específicos. Posso ajudar com:

**🧮 Funções e Equações:**
- Função quadrática: f(x) = ax² + bx + c
- Bhaskara: x = (-b ± √(b² - 4ac)) / 2a
- Função exponencial e logarítmica

**📐 Geometria:**
- Áreas e volumes
- Trigonometria (seno, cosseno, tangente)
- Teorema de Pitágoras

**📊 Estatística e Probabilidade:**
- Média, mediana, moda
- Análise combinatória
- Probabilidade básica

**💡 Sobre determinantes:**
Se sua pergunta é sobre determinantes de matrizes:
- Determinante 2x2: |A| = ad - bc
- Para matriz [[a,b], [c,d]]
- Usado para resolver sistemas lineares

**🎯 Reformule sua pergunta com mais detalhes** que posso te dar uma resposta mais específica!

**Que tal praticar com alguns exercícios do ENEM sobre este tópico, Sther?**
"""
                else:
                    st.success("✅ Inicialização concluída com sucesso!")
                    
            except Exception as init_error:
                st.error(f"❌ Erro crítico na inicialização: {str(init_error)}")
                import traceback
                st.error(f"Stack trace: {traceback.format_exc()}")
                
                return f"""
❌ **Erro Crítico na Inicialização**

Ocorreu um erro durante a inicialização do sistema:

```
{str(init_error)}
```

**Modo Professor Básico Ativado:**

Olá! Sou o Professor Carlos de Matemática. Mesmo com limitações técnicas, vou te ajudar!

**Sobre sua pergunta:** "{user_message}"

**Resposta baseada no conhecimento geral:**

Para questões de matemática do ENEM, é importante focar em:

**🎯 Tópicos Principais:**
- **Funções:** f(x) = ax² + bx + c (quadráticas), exponenciais, logarítmicas
- **Geometria:** Áreas, volumes, teorema de Pitágoras
- **Trigonometria:** seno, cosseno, tangente e suas relações
- **Estatística:** média, mediana, moda, probabilidade
- **Razão e Proporção:** regra de três, porcentagem

Pode me fazer uma pergunta mais específica sobre algum desses tópicos que eu posso ajudar melhor!

🔧 **Nota técnica:** Sistema RAG temporariamente indisponível, mas estou aqui para ajudar!
"""
        
        try:
            # Gera resposta usando RAG
            result = self.rag_system.get_response(user_message)
            
            answer = result.get("answer", "Desculpe, não consegui gerar uma resposta.")
            source_docs = result.get("source_documents", [])
            
            # Verifica se há problemas na resposta
            if ("Erro na API" in answer or "Error code: 401" in answer or "Invalid API Key" in answer or 
                "Sistema RAG não inicializado" in answer):
                return f"""
🔑 **Problema com a API Key da Groq ou com a Inicialização do RAG**

Detectei um problema de autenticação ou inicialização.

**Mensagem do Sistema:**
`{answer}`

**Modo Professor Básico Ativado:**

Olá! Sou o Professor Carlos de Matemática. Mesmo com limitações técnicas, vou te ajudar!

**Sobre sua pergunta:** "{user_message}"

**Resposta baseada no conhecimento geral:**

Para questões de matemática do ENEM, é importante focar em:

**🎯 Tópicos Principais:**
- **Funções:** f(x) = ax² + bx + c (quadráticas), exponenciais, logarítmicas
- **Geometria:** Áreas, volumes, teorema de Pitágoras
- **Trigonometria:** seno, cosseno, tangente e suas relações
- **Estatística:** média, mediana, moda, probabilidade
- **Razão e Proporção:** regra de três, porcentagem

Pode me fazer uma pergunta mais específica sobre algum desses tópicos que eu posso ajudar melhor!

🔧 **Nota técnica:** Sistema RAG temporariamente indisponível, mas estou aqui para ajudar!
"""
            
            # Aplica formatação matemática melhorada
            if MATH_FORMATTER_AVAILABLE:
                answer = format_professor_response(answer)
            
            # Monta resposta formatada
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
                response += "\n• Base de conhecimento geral de matemática"
            
            # SEMPRE adiciona exercícios recomendados
            response += self._add_recommended_exercises(user_message)
            
            # SISTEMA DE ANALOGIAS V2 - SÉRIES PERSONALIZADAS
            # SEMPRE tenta adicionar analogias, mesmo se houve erro na API
            if ANALOGIES_AVAILABLE:
                try:
                    enhanced_response = add_analogy_if_confused(user_message, response)
                    if enhanced_response != response:  # Se analogia foi adicionada
                        response = enhanced_response
                        response += "\n\n🎬 *Sistema de analogias com suas séries favoritas ativo! Friends, Grey's Anatomy, Stranger Things e mais...*"
                except Exception as analogy_error:
                    print(f"⚠️ Erro no sistema de analogias: {analogy_error}")
            
            return response
            
        except Exception as e:
            error_response = f"""
❌ **Erro no Sistema RAG Local**

Detalhes: {str(e)}

💡 **Soluções:**
1. Verifique se a pasta 'matemática' existe
2. Confirme se há documentos válidos (.docx, .pdf)
3. Verifique sua conexão com a internet (para DeepSeek)
4. Confirme se a API Key está correta

🔧 Se o problema persistir, tente reprocessar os documentos.
"""
            
            # MESMO COM ERRO, tenta aplicar analogias se usuário está confuso
            if ANALOGIES_AVAILABLE:
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