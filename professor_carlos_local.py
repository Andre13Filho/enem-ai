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
        """Inicializa o sistema RAG local com melhor tratamento de erros"""
        if not LOCAL_RAG_AVAILABLE:
            st.error("Sistema RAG local não disponível. Verifique local_math_rag.py")
            return False
        
        try:
            st.info("🔄 Inicializando sistema RAG...")
            
            # Debug: Verifica se a pasta matemática existe
            pasta_existe = os.path.exists(self.rag_system.math_folder_path)
            st.info(f"📁 Pasta matemática ({self.rag_system.math_folder_path}): {'✅ Existe' if pasta_existe else '❌ Não existe'}")
            
            if not pasta_existe:
                st.warning("Criando pasta matemática...")
                os.makedirs(self.rag_system.math_folder_path, exist_ok=True)
            
            # Tenta carregar vectorstore existente primeiro
            st.info("📚 Tentando carregar base de conhecimento existente...")
            vectorstore_carregado = self.rag_system.load_existing_vectorstore()
            
            if vectorstore_carregado:
                st.success("✅ Base de conhecimento carregada!")
                try:
                    self.rag_system.create_rag_chain(api_key)
                    self.current_api_key = api_key
                    self.is_initialized = True
                    st.success("✅ Sistema RAG inicializado com sucesso!")
                    return True
                except Exception as chain_error:
                    st.error(f"❌ Erro ao criar cadeia RAG: {str(chain_error)}")
                    return self._try_emergency_initialization(api_key)
            else:
                # Se load_existing_vectorstore falhou, tenta processar documentos
                st.info("📚 Processando documentos de matemática...")
                
                # Verifica se há arquivos na pasta
                arquivos = []
                try:
                    for root, dirs, files in os.walk(self.rag_system.math_folder_path):
                        for file in files:
                            if file.lower().endswith(('.pdf', '.docx', '.txt')):
                                arquivos.append(file)
                    
                    st.info(f"📄 Encontrados {len(arquivos)} arquivos: {', '.join(arquivos[:3])}{'...' if len(arquivos) > 3 else ''}")
                except Exception as e:
                    st.warning(f"Erro ao listar arquivos: {str(e)}")
                
                if len(arquivos) == 0:
                    st.warning("⚠️ Nenhum arquivo encontrado. Usando modo de emergência...")
                    return self._try_emergency_initialization(api_key)
                
                with st.spinner("Processando documentos da pasta matemática..."):
                    try:
                        success = self.rag_system.process_math_documents()
                        if success:
                            # Força criação do vectorstore após processamento
                            self.rag_system._create_vectorstore()
                            self.rag_system.create_rag_chain(api_key)
                            self.current_api_key = api_key
                            self.is_initialized = True
                            st.success("✅ Sistema RAG inicializado com sucesso!")
                            return True
                        else:
                            st.error("❌ Falha ao processar documentos")
                            return self._try_emergency_initialization(api_key)
                    except Exception as processing_error:
                        st.error(f"❌ Erro no processamento: {str(processing_error)}")
                        # Tenta fallback com documentos básicos
                        return self._try_emergency_initialization(api_key)
                    
        except Exception as e:
            st.error(f"❌ Erro na inicialização: {str(e)}")
            return self._try_emergency_initialization(api_key)
    
    def _try_emergency_initialization(self, api_key: str) -> bool:
        """Inicialização de emergência com conteúdo básico"""
        try:
            st.warning("🚨 Tentando inicialização de emergência...")
            
            # Cria documento básico de matemática
            from langchain.schema import Document
            
            basic_content = """
# Matemática - Guia ENEM 2024

## Funções Quadráticas
A função quadrática tem a forma: f(x) = ax² + bx + c, onde a ≠ 0

### Fórmula de Bhaskara
Para resolver equações do tipo ax² + bx + c = 0:
x = (-b ± √(b² - 4ac)) / 2a

### Discriminante (Δ)
Δ = b² - 4ac
- Se Δ > 0: duas raízes reais distintas
- Se Δ = 0: uma raiz real (raiz dupla)
- Se Δ < 0: não há raízes reais

## Geometria Plana

### Áreas
- Retângulo: A = base × altura
- Triângulo: A = (base × altura) / 2
- Círculo: A = πr²
- Trapézio: A = ((B + b) × h) / 2

### Perímetros
- Retângulo: P = 2(base + altura)
- Círculo: P = 2πr
- Triângulo: P = a + b + c

## Geometria Espacial

### Volumes
- Cubo: V = a³
- Paralelepípedo: V = a × b × c
- Cilindro: V = πr²h
- Cone: V = (πr²h) / 3
- Esfera: V = (4πr³) / 3

## Trigonometria

### Relações Fundamentais
- sen²θ + cos²θ = 1
- tan θ = sen θ / cos θ

### Ângulos Notáveis
- 30°: sen = 1/2, cos = √3/2, tan = √3/3
- 45°: sen = √2/2, cos = √2/2, tan = 1
- 60°: sen = √3/2, cos = 1/2, tan = √3

## Progressões

### Progressão Aritmética (PA)
- Termo geral: an = a1 + (n-1)r
- Soma dos n primeiros termos: Sn = n(a1 + an)/2

### Progressão Geométrica (PG)
- Termo geral: an = a1 × q^(n-1)
- Soma dos n primeiros termos: Sn = a1(q^n - 1)/(q - 1)

## Estatística

### Medidas de Tendência Central
- Média: M = (x1 + x2 + ... + xn) / n
- Mediana: valor central dos dados ordenados
- Moda: valor que mais se repete

### Probabilidade
- P(A) = número de casos favoráveis / número total de casos
- P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
- P(A ∩ B) = P(A) × P(B|A)

## Análise Combinatória

### Arranjos
- A(n,p) = n! / (n-p)!

### Combinações
- C(n,p) = n! / (p! × (n-p)!)

### Permutações
- P(n) = n!

## Logaritmos

### Propriedades
- log(a × b) = log a + log b
- log(a / b) = log a - log b
- log(a^n) = n × log a
- log_a(a) = 1
- log_a(1) = 0

## Funções

### Função Afim
f(x) = ax + b
- Coeficiente angular: a
- Coeficiente linear: b

### Função Exponencial
f(x) = a^x (a > 0, a ≠ 1)

### Função Logarítmica
f(x) = log_a(x) (a > 0, a ≠ 1, x > 0)
"""
            
            basic_doc = Document(
                page_content=basic_content,
                metadata={"source": "conteudo_emergencia_enem", "topic": "matemática_completa"}
            )
            
            # Configura sistema com documento básico
            self.rag_system.documents = [basic_doc]
            self.rag_system._create_vectorstore()
            self.rag_system.create_rag_chain(api_key)
            
            self.current_api_key = api_key
            self.is_initialized = True
            
            st.success("🚨 Sistema inicializado em modo EMERGÊNCIA - funcionando com conteúdo básico do ENEM")
            st.info("📚 O Professor Carlos está pronto com os principais tópicos de matemática do ENEM!")
            return True
            
        except Exception as fallback_error:
            st.error(f"❌ Falha total na inicialização: {str(fallback_error)}")
            return False
    
    def get_response(self, user_message: str, api_key: str) -> str:
        """Gera resposta usando RAG local"""
        
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
                if not self.initialize_system(api_key):
                    return f"""
❌ **Falha na Inicialização do Sistema RAG**

O sistema não conseguiu inicializar corretamente.

**Debug Info:**
- API Key recebida: {api_key_preview}
- RAG System disponível: {self.rag_system is not None}
- Pasta matemática: {self.rag_system.math_folder_path if self.rag_system else 'N/A'}

**Modo de Emergência Ativado:**

Olá, Sther! Sou o Professor Carlos, especialista em matemática do ENEM. 

Infelizmente, meu sistema RAG local está com problemas técnicos, mas ainda posso te ajudar!

Sobre sua pergunta: "{user_message}"

**Resposta básica de matemática:**
Para questões de matemática do ENEM, geralmente envolvem:
- Funções (1º e 2º grau, exponencial, logarítmica)
- Geometria (áreas, volumes, trigonometria)
- Estatística e probabilidade
- Razão e proporção

💡 **Dica:** Reformule sua pergunta de forma mais específica que posso tentar te ajudar melhor!

🔧 **Para administradores:** Verifique a configuração da API key da Groq no Streamlit Cloud.
"""
            except Exception as init_error:
                return f"""
❌ **Erro Crítico na Inicialização**

Ocorreu um erro durante a inicialização do sistema:

```
{str(init_error)}
```

**Modo Professor Básico Ativado:**

Olá, Sther! Mesmo com problemas técnicos, vou te ajudar com matemática!

Sobre: "{user_message}"

**Orientações gerais de matemática para o ENEM:**

1. **Funções Quadráticas:** Use a fórmula de Bhaskara: x = (-b ± √(b²-4ac))/2a
2. **Geometria:** Lembre das fórmulas básicas de área e volume
3. **Trigonometria:** sen²θ + cos²θ = 1
4. **Estatística:** Média = Soma/Quantidade

💪 Pode refazer sua pergunta de forma mais específica que vou tentar ajudar melhor!
"""
        
        try:
            # Gera resposta usando RAG
            result = self.rag_system.get_response(user_message)
            
            answer = result.get("answer", "Desculpe, não consegui gerar uma resposta.")
            source_docs = result.get("source_documents", [])
            
            # Verifica se a resposta contém erro de API
            if "Erro na API" in answer or "Error code: 401" in answer or "Invalid API Key" in answer:
                return f"""
🔑 **Problema com a API Key da Groq**

Detectei um problema de autenticação com a API da Groq.

**Modo Professor Básico Ativado:**

Olá, Sther! Sou o Professor Carlos de Matemática. Mesmo com limitações técnicas, vou te ajudar!

**Sobre sua pergunta:** "{user_message}"

**Resposta baseada no conhecimento geral:**

Para questões de matemática do ENEM, é importante focar em:

**🎯 Tópicos Principais:**
- **Funções:** f(x) = ax² + bx + c (quadráticas), exponenciais, logarítmicas
- **Geometria:** Áreas, volumes, teorema de Pitágoras
- **Trigonometria:** seno, cosseno, tangente e suas relações
- **Estatística:** média, mediana, moda, probabilidade
- **Razão e Proporção:** regra de três, porcentagem

**💡 Dicas de Estudo:**
1. Pratique muito com exercícios do ENEM
2. Memorize as fórmulas principais
3. Faça resumos visuais
4. Resolva questões por etapas

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
    
    def _extract_math_topic_from_context(self, user_message: str, response_content: str) -> str:
        """Extrai o tópico matemático principal da conversa"""
        combined_text = (user_message + " " + response_content).lower()
        
        # Mapeia palavras-chave para tópicos principais
        topic_priority = [
            ("função", "Funções"),
            ("quadrática", "Funções"),
            ("parábola", "Funções"),
            ("geometria", "Geometria"),
            ("triângulo", "Geometria"),
            ("círculo", "Geometria"),
            ("área", "Geometria"),
            ("volume", "Geometria"),
            ("álgebra", "Álgebra"),
            ("equação", "Álgebra"),
            ("sistema", "Álgebra"),
            ("probabilidade", "Estatística e Probabilidade"),
            ("estatística", "Estatística e Probabilidade"),
            ("dados", "Estatística e Probabilidade"),
            ("juros", "Matemática Financeira"),
            ("porcentagem", "Matemática Financeira"),
            ("progressão", "Progressões"),
            ("sequência", "Progressões")
        ]
        
        # Retorna o primeiro tópico encontrado (ordem de prioridade)
        for keyword, topic in topic_priority:
            if keyword in combined_text:
                return topic
        
        return "Geral"
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da base de conhecimento"""
        if not self.rag_system:
            return {"erro": "Sistema não disponível"}
        
        return self.rag_system.get_stats()
    
    def clear_memory(self):
        """Limpa memória da conversa"""
        if self.rag_system:
            self.rag_system.clear_memory()
    
    def reprocess_documents(self, api_key: str) -> bool:
        """Força reprocessamento dos documentos"""
        if not self.rag_system:
            return False
        
        try:
            st.info("🔄 Reprocessando documentos...")
            success = self.rag_system.process_math_documents()
            
            if success and api_key:
                self.rag_system.create_rag_chain(api_key)
                self.current_api_key = api_key
                self.is_initialized = True
                st.success("✅ Documentos reprocessados com sucesso!")
                return True
            
            return success
            
        except Exception as e:
            st.error(f"Erro no reprocessamento: {str(e)}")
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
            st.error(f"Erro ao buscar exercícios: {str(e)}")
            return []
    
    def search_exercises_by_message(self, user_message: str, k: int = 3) -> List[Dict[str, Any]]:
        """Busca exercícios baseados na mensagem do usuário"""
        if not self.exercises_rag:
            return []
        
        try:
            # Carrega vectorstore se necessário
            if not self.exercises_rag.vectorstore:
                self.exercises_rag.load_existing_vectorstore()
            
            # Identifica tópicos na mensagem
            message_lower = user_message.lower()
            
            # Mapeia palavras-chave para tópicos (expandido para melhor detecção)
            topic_keywords = {
                # Funções
                "função": "Funções",
                "funções": "Funções",
                "quadrática": "Funções", 
                "parábola": "Funções",
                "gráfico": "Funções",
                "vértice": "Funções",
                "raiz": "Funções",
                "coeficiente": "Funções",
                
                # Geometria
                "geometria": "Geometria",
                "triângulo": "Geometria",
                "área": "Geometria",
                "círculo": "Geometria",
                "retângulo": "Geometria",
                "quadrado": "Geometria",
                "polígono": "Geometria",
                "volume": "Geometria",
                "perímetro": "Geometria",
                "ângulo": "Geometria",
                "teorema": "Geometria",
                "pitágoras": "Geometria",
                "circunferência": "Geometria",
                "raio": "Geometria",
                "diâmetro": "Geometria",
                
                # Trigonometria
                "trigonometria": "Geometria",
                "seno": "Geometria",
                "cosseno": "Geometria",
                "tangente": "Geometria",
                "sen": "Geometria",
                "cos": "Geometria",
                "tan": "Geometria",
                
                # Estatística e Probabilidade
                "probabilidade": "Estatística e Probabilidade",
                "chance": "Estatística e Probabilidade",
                "estatística": "Estatística e Probabilidade",
                "média": "Estatística e Probabilidade",
                "mediana": "Estatística e Probabilidade",
                "moda": "Estatística e Probabilidade",
                "dados": "Estatística e Probabilidade",
                "amostra": "Estatística e Probabilidade",
                "frequência": "Estatística e Probabilidade",
                
                # Álgebra
                "álgebra": "Álgebra",
                "algebra": "Álgebra",
                "equação": "Álgebra",
                "inequação": "Álgebra",
                "sistema": "Álgebra",
                "determinante": "Álgebra",
                "matriz": "Álgebra",
                
                # Matemática Financeira
                "juros": "Matemática Financeira",
                "porcentagem": "Matemática Financeira",
                "desconto": "Matemática Financeira",
                "financeira": "Matemática Financeira",
                "capital": "Matemática Financeira",
                "montante": "Matemática Financeira",
                "taxa": "Matemática Financeira",
                
                # Progressões
                "progressão": "Progressões",
                "sequência": "Progressões",
                "pa": "Progressões",
                "pg": "Progressões",
                "aritmética": "Progressões",
                "geométrica": "Progressões",
                
                # Análise Combinatória
                "combinação": "Análise Combinatória",
                "permutação": "Análise Combinatória",
                "arranjo": "Análise Combinatória",
                "combinatória": "Análise Combinatória",
                "fatorial": "Análise Combinatória",
                
                # Geometria Analítica
                "reta": "Geometria Analítica",
                "ponto": "Geometria Analítica",
                "coordenadas": "Geometria Analítica",
                "cartesiano": "Geometria Analítica",
                "distância": "Geometria Analítica",
                
                # Logaritmo
                "logaritmo": "Outros",
                "log": "Outros",
                "exponencial": "Outros"
            }
            
            # Busca tópicos identificados
            identified_topics = []
            for keyword, topic in topic_keywords.items():
                if keyword in message_lower:
                    identified_topics.append(topic)
            
            # Remove duplicatas
            identified_topics = list(set(identified_topics))
            
            all_exercises = []
            
            # Busca exercícios para cada tópico identificado
            if identified_topics:
                for topic in identified_topics:
                    # Determina área baseada no tópico
                    if topic in ["Física", "Química", "Biologia"]:
                        subject_area = "Ciências da Natureza"
                    else:
                        subject_area = "Matemática"
                    
                    docs = self.exercises_rag.search_exercises_by_topic(topic, subject_area, k=2)
                    
                    for doc in docs:
                        exercise = {
                            "content": doc.page_content,
                            "year": doc.metadata.get("year", "N/A"),
                            "question_number": doc.metadata.get("question_number", "N/A"),
                            "subject_area": doc.metadata.get("subject_area", "N/A"),
                            "topic": doc.metadata.get("topic", "N/A"),
                            "source_file": doc.metadata.get("source_file", "N/A"),
                            "identified_from": topic
                        }
                        all_exercises.append(exercise)
            
            # Se não identificou tópicos específicos, busca pela mensagem diretamente
            if not all_exercises:
                docs = self.exercises_rag.search_exercises_by_topic(user_message, "Matemática", k)
                
                for doc in docs:
                    exercise = {
                        "content": doc.page_content,
                        "year": doc.metadata.get("year", "N/A"),
                        "question_number": doc.metadata.get("question_number", "N/A"),
                        "subject_area": doc.metadata.get("subject_area", "N/A"),
                        "topic": doc.metadata.get("topic", "N/A"),
                        "source_file": doc.metadata.get("source_file", "N/A"),
                        "identified_from": "busca_geral"
                    }
                    all_exercises.append(exercise)
            
            # Remove duplicatas baseado no ano e número da questão
            unique_exercises = []
            seen = set()
            for ex in all_exercises:
                key = (ex["year"], ex["question_number"])
                if key not in seen:
                    seen.add(key)
                    unique_exercises.append(ex)
            
            return unique_exercises[:k]
            
        except Exception as e:
            print(f"Erro ao buscar exercícios por mensagem: {str(e)}")
            return []
    
    def get_exercises_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos exercícios disponíveis"""
        if not self.exercises_rag:
            return {"erro": "Sistema de exercícios não disponível"}
        
        try:
            # Carrega vectorstore se necessário
            if not self.exercises_rag.vectorstore:
                self.exercises_rag.load_existing_vectorstore()
            
            return self.exercises_rag.get_stats()
            
        except Exception as e:
            return {"erro": f"Erro ao obter estatísticas: {str(e)}"}
    
    def suggest_exercises_for_question(self, user_question: str, api_key: str) -> str:
        """Sugere exercícios relevantes baseados na pergunta do usuário"""
        if not self.exercises_rag or not api_key:
            return "Sistema de exercícios não disponível ou API key não configurada."
        
        try:
            # Extrai tópicos da pergunta do usuário
            topic_keywords = {
                "função": "Função Quadrática",
                "quadrática": "Função Quadrática", 
                "parábola": "Função Quadrática",
                "geometria": "Geometria",
                "triângulo": "Geometria",
                "área": "Geometria",
                "trigonometria": "Trigonometria",
                "seno": "Trigonometria",
                "probabilidade": "Probabilidade",
                "estatística": "Estatística",
                "média": "Estatística",
                "logaritmo": "Logaritmo",
                "progressão": "Progressão",
                "física": "Física",
                "força": "Física",
                "energia": "Física",
                "química": "Química",
                "biologia": "Biologia"
            }
            
            # Identifica tópico principal
            user_question_lower = user_question.lower()
            identified_topic = "matemática"  # default
            subject_area = None
            
            for keyword, topic in topic_keywords.items():
                if keyword in user_question_lower:
                    identified_topic = topic
                    if topic in ["Física", "Química", "Biologia"]:
                        subject_area = "Ciências da Natureza"
                    else:
                        subject_area = "Matemática"
                    break
            
            # Busca exercícios relacionados
            exercises = self.search_exercises(identified_topic, subject_area, k=3)
            
            if not exercises:
                exercises = self.search_exercises(user_question, None, k=3)
            
            if exercises:
                response = f"""
🎯 **Exercícios Recomendados sobre "{identified_topic}"**

Baseado na sua pergunta, encontrei estes exercícios do ENEM que podem te ajudar:

"""
                
                for i, exercise in enumerate(exercises, 1):
                    year = exercise["year"]
                    question_num = exercise["question_number"]
                    content_preview = exercise["content"][:300] + "..." if len(exercise["content"]) > 300 else exercise["content"]
                    
                    response += f"""
**📝 Exercício {i} - ENEM {year} (Questão {question_num})**
*Área: {exercise["subject_area"]} | Tópico: {exercise["topic"]}*

{content_preview}

---
"""
                
                response += """
💡 **Dica:** Tente resolver estes exercícios e me pergunte se tiver dúvidas sobre algum passo específico!
"""
                
                return response
            else:
                return f"""
🔍 **Nenhum exercício específico encontrado**

Não encontrei exercícios diretamente relacionados ao tópico "{identified_topic}" na base do ENEM.

💡 **Sugestões:**
- Reformule sua pergunta com termos mais específicos
- Posso ajudar com teoria e explicações sobre o assunto
- Tente buscar por tópicos relacionados

📚 **Tópicos disponíveis:** Função Quadrática, Geometria, Trigonometria, Probabilidade, Estatística, Física, Química, Biologia
"""
                
        except Exception as e:
            return f"Erro ao sugerir exercícios: {str(e)}"

# Instância global do Professor Carlos Local
professor_carlos_local = ProfessorCarlosLocal()

def setup_professor_carlos_local_ui():
    """Configura UI específica do Professor Carlos Local (barra lateral)"""
    pass

def get_professor_carlos_local_response(user_message: str, api_key: str) -> str:
    """Função para obter resposta do Professor Carlos Local"""
    return professor_carlos_local.get_response(user_message, api_key)

# Função de busca prévia (opcional)
def preview_local_search(query: str) -> str:
    """Preview do conteúdo que seria recuperado"""
    return professor_carlos_local.get_relevant_content_preview(query) 