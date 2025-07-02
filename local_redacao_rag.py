#!/usr/bin/env python3
"""
Sistema RAG Local para Professora Carla - Redação
Utiliza índices FAISS pré-construídos e baixados do Hugging Face.
"""

import streamlit as st
import os
import requests
import re
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime
from redacao_formatter import format_redacao_response
import time

# Importações para processamento de PDF
try:
    import PyPDF2
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    st.warning("⚠️ Bibliotecas de PDF não instaladas. Execute: pip install PyPDF2 PyMuPDF")

# LangChain imports
from langchain_community.vectorstores import FAISS
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
try:
    from langchain_community.memory import ConversationBufferMemory
except ImportError:
    from langchain.memory import ConversationBufferMemory
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

# Groq para LLM
from groq import Groq

# Diretórios para armazenar os índices FAISS
FAISS_INDEX_DIR = "faiss_index_redacao"
FAISS_SUCCESS_INDEX_DIR = "faiss_index_success_redacao"

class GroqLLM(LLM):
    """LLM personalizado para DeepSeek R1 Distill via Groq"""
    
    api_key: str
    model_name: str = "deepseek-r1-distill-llama-70b"
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, model_name="deepseek-r1-distill-llama-70b", **kwargs)
    
    @property
    def _llm_type(self) -> str:
        return "groq"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            # Cria uma nova instância do cliente a cada chamada para evitar cache corrompido
            client = Groq(api_key=self.api_key)
            
            # Sistema de prompt da Professora Carla
            system_prompt = """Você é a Professora Carla, especialista em redação do ENEM. Você está conversando com Sther, uma estudante de 17 anos que quer muito bem no ENEM.

CARACTERÍSTICAS DA PROFESSORA CARLA:
- Didática e encorajadora
- Usa linguagem clara e acessível
- Sempre específica e construtiva nos feedbacks
- Maternal mas profissional
- Foca nos critérios oficiais do ENEM
- Sempre termina com palavras de encorajamento

SOBRE A STHER:
- Dedicada aos estudos
- Às vezes fica insegura com redação
- Precisa de orientação específica e prática
- Quer alcançar nota 1000 no ENEM

INSTRUÇÕES:
- Use emojis e formatação markdown para clareza
- Organize conteúdo em seções lógicas
- Baseie orientações nos critérios do ENEM
- Seja específica em feedbacks de redação
- Use exemplos práticos e aplicáveis
- Mantenha foco na evolução da estudante"""

            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro na API: {str(e)}"

class LocalRedacaoRAG:
    """Sistema RAG que carrega índices FAISS remotos para Redação."""
    
    def __init__(self):
        self.vectorstore = None
        self.success_vectorstore = None
        self.retriever = None
        self.success_retriever = None
        self.memory = None
        self.rag_chain = None
        self.embeddings = None
        self.is_initialized = False
        self.redacao_folder_path = FAISS_INDEX_DIR
        self.success_folder_path = FAISS_SUCCESS_INDEX_DIR
        
        # O setup de embeddings foi movido para o método initialize()
        # para evitar carregamento pesado durante a importação.

    def _setup_embeddings(self, model_name: str):
        """Configura o modelo de embeddings do Hugging Face."""
        # Se os embeddings já estiverem carregados, não faz nada
        if self.embeddings:
            return
        
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            if 'st' in globals() and hasattr(st, 'error'):
                st.error(f"Falha ao carregar o modelo de embeddings: {e}")
            self.embeddings = None

    def _download_file(self, url: str, local_path: str):
        """Baixa um arquivo de uma URL para um caminho local."""
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"✅ Arquivo baixado: {local_path}")
            return True
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de rede ao baixar {url}: {e}")
            print(f"❌ Erro de rede ao baixar {url}: {e}")
            return False
        
    def _ensure_faiss_index_is_ready(self) -> bool:
        """
        Garante que os índices FAISS estejam disponíveis, baixando-os se necessário.
        """
        os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
        os.makedirs(FAISS_SUCCESS_INDEX_DIR, exist_ok=True)
        
        # Arquivos principais de redação (nomes padrão do FAISS)
        index_file = os.path.join(FAISS_INDEX_DIR, "index.faiss")
        pkl_file = os.path.join(FAISS_INDEX_DIR, "index.pkl")
        
        # Arquivos de casos de sucesso (nomes padrão do FAISS)
        success_index_file = os.path.join(FAISS_SUCCESS_INDEX_DIR, "index.faiss")
        success_pkl_file = os.path.join(FAISS_SUCCESS_INDEX_DIR, "index.pkl")

        # Verifica se todos os arquivos já existem
        if (os.path.exists(index_file) and os.path.exists(pkl_file) and 
            os.path.exists(success_index_file) and os.path.exists(success_pkl_file)):
            print("✅ Índices FAISS de redação já existem localmente.")
            return True

        st.info("📥 Baixando índices de redação do Hugging Face...")
        print("📥 Baixando índices de redação do Hugging Face...")

        # URLs dos arquivos principais no Hugging Face
        faiss_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_redacao.faiss"
        pkl_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_redacao.pkl"
        
        # URLs dos arquivos de casos de sucesso
        success_faiss_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_success_red.faiss"
        success_pkl_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_success_red.pkl"

        # Baixa os arquivos principais com nomes padrão do FAISS
        faiss_success = self._download_file(faiss_url, index_file)
        pkl_success = self._download_file(pkl_url, pkl_file)
        
        # Baixa os arquivos de casos de sucesso com nomes padrão do FAISS
        success_faiss_success = self._download_file(success_faiss_url, success_index_file)
        success_pkl_success = self._download_file(success_pkl_url, success_pkl_file)

        if (faiss_success and pkl_success and success_faiss_success and success_pkl_success):
            st.success("✅ Índices de redação baixados com sucesso!")
            return True
        else:
            st.error("❌ Falha ao baixar os arquivos dos índices de redação.")
            # Limpa arquivos parciais em caso de falha
            for file_path in [index_file, pkl_file, success_index_file, success_pkl_file]:
                if os.path.exists(file_path): 
                    os.remove(file_path)
            return False
            
    def initialize(self, api_key: str) -> bool:
        """
        Inicializa o sistema: baixa os índices, carrega os vectorstores e cria a cadeia RAG.
        """
        if self.is_initialized:
            return True
            
        # 1. Garantir que os índices FAISS estão disponíveis
        if not self._ensure_faiss_index_is_ready():
            return False
            
        # 2. Carregar os Vectorstores FAISS (e configurar embeddings aqui)
        try:
            st.info("📚 Carregando base de conhecimento de redação (FAISS)...")
            print("📚 Carregando base de conhecimento de redação (FAISS)...")
            
            # Passo 2.1: Configurar embeddings ANTES de carregar o FAISS
            self._setup_embeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v1")
            if not self.embeddings:
                st.error("Embeddings não foram inicializadas. Abortando.")
                return False

            # Carrega o vectorstore principal de redação
            self.vectorstore = FAISS.load_local(
                FAISS_INDEX_DIR, 
                self.embeddings,
                allow_dangerous_deserialization=True # Necessário para pkl
            )
            
            # Carrega o vectorstore de casos de sucesso
            self.success_vectorstore = FAISS.load_local(
                FAISS_SUCCESS_INDEX_DIR, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            print(f"✅ Vectorstore principal carregado: {self.vectorstore.index.ntotal} documentos")
            print(f"✅ Vectorstore de sucesso carregado: {self.success_vectorstore.index.ntotal} documentos")
            
            # 3. Criar retriever e RAG chain
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
            self.success_retriever = self.success_vectorstore.as_retriever(search_kwargs={"k": 3})
            
            # Criar LLM personalizado
            llm = GroqLLM(api_key=api_key)
            
            # Configurar memória para conversas
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Criar cadeia RAG conversacional (sem prompt customizado para compatibilidade)
            self.rag_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.retriever,
                memory=self.memory,
                return_source_documents=True,
                verbose=False
            )
            
            st.success("✅ Sistema RAG de redação inicializado com sucesso!")
            self.is_initialized = True
            return True

        except Exception as e:
            st.error(f"❌ Erro ao inicializar o sistema RAG: {str(e)}")
            print(f"❌ Erro ao inicializar o sistema RAG: {str(e)}")
            return False
    
    def get_response(self, question: str) -> Dict[str, Any]:
        """Obtém uma resposta do sistema RAG."""
        if not self.rag_chain:
            return {"answer": "O sistema RAG não foi inicializado corretamente."}
        
        try:
            # Verificar se a pergunta parece ser uma redação para análise
            if self._is_redacao_for_analysis(question):
                # Obter API key com sistema robusto
                api_key = get_api_key_robust()
                
                if api_key and validate_api_key(api_key):
                    # Analisar como redação
                    analysis = self.analyze_redacao_text(question, "Redação via Chat", api_key)
                    return {"answer": analysis}
                else:
                    return {"answer": """
# 🔑 **Erro de Configuração**

A API key não foi encontrada ou não está funcionando. 

**Para resolver:**
1. Verifique a seção de diagnóstico abaixo
2. Configure a GROQ_API_KEY nos Secrets do Streamlit
3. Reinicie o aplicativo

**Precisa de ajuda?** Use o diagnóstico automático na aba de configurações.
"""}
            
            return self.rag_chain({"question": question})
        except Exception as e:
            return {"answer": f"Erro ao processar a pergunta: {str(e)}"}
    
    def _is_redacao_for_analysis(self, text: str) -> bool:
        """Detecta se o texto parece ser uma redação para análise"""
        # Critérios para detectar redação
        words = text.split()
        word_count = len(words)
        
        # Deve ter pelo menos 100 palavras
        if word_count < 100:
            return False
            
        # Procurar por indicadores de redação
        redacao_indicators = [
            "professora carla",
            "poderia analisar",
            "minha redação",
            "redação:",
            "análise da redação",
            "corrija minha redação",
            "avalie minha redação"
        ]
        
        text_lower = text.lower()
        for indicator in redacao_indicators:
            if indicator in text_lower:
                return True
        
        # Verificar estrutura de redação (parágrafos)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3 and word_count > 150:
            # Verificar se tem características de dissertação
            intro_words = ["atualmente", "nos dias de hoje", "na sociedade", "é inegável", "é notório"]
            concl_words = ["portanto", "dessa forma", "assim", "diante disso", "logo"]
            
            has_intro = any(word in text_lower for word in intro_words)
            has_concl = any(word in text_lower for word in concl_words)
            
            if has_intro or has_concl:
                return True
        
        return False
    
    def search_relevant_content(self, query: str, k: int = 3) -> List[Document]:
        """Busca por conteúdo relevante no vectorstore principal."""
        if not self.vectorstore:
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Erro na busca de similaridade: {str(e)}")
            return []
    
    def search_success_cases(self, query: str, k: int = 2) -> List[Document]:
        """Busca por casos de sucesso relevantes."""
        if not self.success_vectorstore:
            return []
        
        try:
            return self.success_vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Erro na busca de casos de sucesso: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas detalhadas do sistema RAG, incluindo uma amostra de documentos.
        """
        if not self.is_initialized or not self.vectorstore:
            return {
                "status": "Não Carregado",
                "total_documents": 0,
                "success_cases": 0,
                "sample_documents": []
            }

        try:
            total_documents = self.vectorstore.index.ntotal
            success_cases = self.success_vectorstore.index.ntotal if self.success_vectorstore else 0
            
            # Pega uma amostra de metadados dos primeiros 5 documentos
            sample_docs_metadata = []
            docstore = self.vectorstore.docstore
            doc_ids = list(docstore._dict.keys())
            
            for i in range(min(5, len(doc_ids))):
                doc = docstore._dict[doc_ids[i]]
                if doc.metadata:
                    sample_docs_metadata.append(doc.metadata)

            # Extrai nomes de arquivos únicos da amostra
            sample_files = sorted(list(set(
                meta.get("source", "Fonte Desconhecida") for meta in sample_docs_metadata
            )))

            return {
                "status": "Carregado",
                "total_documents": total_documents,
                "success_cases": success_cases,
                "sample_documents": sample_files
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas do RAG: {e}")
            return {
                "status": "Erro na Leitura",
                "total_documents": 0,
                "success_cases": 0,
                "sample_documents": [str(e)]
            }
    
    def clear_memory(self):
        """Limpa a memória da conversa."""
        if self.memory:
            self.memory.clear()

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extrai texto do PDF usando múltiplas estratégias"""
        text = ""
        
        if not PDF_AVAILABLE:
            return "Bibliotecas de PDF não estão instaladas. Instale: pip install PyPDF2 PyMuPDF"
        
        # Estratégia 1: PyPDF2 para PDFs com texto
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += page_text + "\n"
                
                os.unlink(tmp_file.name)
                
                if text.strip():
                    return text
        except Exception as e:
            print(f"Erro PyPDF2: {e}")

        # Estratégia 2: PyMuPDF para PDFs mais complexos  
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
            pdf_document.close()
            
            if text.strip():
                return text
        except Exception as e:
            print(f"Erro PyMuPDF: {e}")

        return text if text.strip() else "Não foi possível extrair texto do PDF."

    def analyze_redacao_text(self, texto_redacao: str, filename: str, api_key: str) -> str:
        """Analisa o texto da redação usando RAG e retorna feedback detalhado"""
        
        # Garantir que o sistema está inicializado
        if not self.is_initialized:
            if not self.initialize(api_key):
                return "❌ Erro ao inicializar sistema de análise. Verifique sua conexão com a internet."
        
        # Análises básicas da redação
        palavras = len(texto_redacao.split())
        paragrafos = len([p for p in texto_redacao.split('\n\n') if p.strip()])
        linhas = len([l for l in texto_redacao.split('\n') if l.strip()])
        
        # Buscar material relevante sobre redação
        query_redacao = f"critérios avaliação ENEM redação competências estrutura argumentação"
        redacao_docs = self.search_relevant_content(query_redacao, k=5)
        
        # Buscar casos de sucesso para comparação
        query_sucesso = f"redação nota 1000 exemplos"
        success_docs = self.search_success_cases(query_sucesso, k=3)
        
        # Montar contexto para análise
        context_redacao = "\n\n".join([doc.page_content for doc in redacao_docs])
        context_success = "\n\n".join([doc.page_content for doc in success_docs])
        
        # Prompt específico e detalhado para análise de redação
        analysis_prompt = f"""
PROFESSORA CARLA, ANALISE ESTA REDAÇÃO DA STHER:

📂 **ARQUIVO:** {filename}
📊 **ESTATÍSTICAS:** {palavras} palavras, {paragrafos} parágrafos, {linhas} linhas

📝 **TEXTO DA REDAÇÃO:**
{texto_redacao}

🎯 **MATERIAL DE APOIO DISPONÍVEL:**
**Critérios do ENEM:** {context_redacao[:500]}...
**Exemplos Nota 1000:** {context_success[:500]}...

📋 **TAREFA ESPECÍFICA:**
Como Professora Carla, faça uma análise COMPLETA seguindo os critérios oficiais do ENEM:

🏆 **1. NOTA FINAL (0-1000):** Calcule baseado nas 5 competências

📐 **2. ANÁLISE POR COMPETÊNCIA:**
- **C1 (0-200):** Domínio da escrita formal - gramática, estrutura
- **C2 (0-200):** Compreensão do tema - repertório, argumentação
- **C3 (0-200):** Organização das informações - coerência, progressão
- **C4 (0-200):** Mecanismos linguísticos - coesão, conectivos
- **C5 (0-200):** Proposta de intervenção - agente, ação, meio, finalidade

✅ **3. PONTOS FORTES:** O que Sther fez muito bem

⚠️ **4. PONTOS A MELHORAR:** Específicos e acionáveis

📈 **5. PLANO PARA NOTA 1000:** Passos concretos

🌟 **6. COMPARAÇÃO:** Como se compara aos exemplos de sucesso

💪 **7. MENSAGEM MOTIVACIONAL:** Como Professora Carla carinhosa

**IMPORTANTE:** Seja detalhada, específica e construtiva. Use os materiais de apoio para fundamentar sua análise!
"""

        try:
            # Usar o RAG para gerar análise especializada
            response = self.rag_chain({
                "question": analysis_prompt
            })
            
            analysis_raw = response.get("answer", "Erro na análise")
            analysis = format_redacao_response(analysis_raw) 
            
            # Adicionar cabeçalho formatado
            final_analysis = f"""
# 📝 **CORREÇÃO COMPLETA DA REDAÇÃO**

**📂 Arquivo:** {filename}  
**📅 Data:** {datetime.now().strftime("%d/%m/%Y às %H:%M")}  
**👩‍🏫 Professora:** Carla  

---

{analysis}

---

## 🎯 **PRÓXIMOS PASSOS**

### 📚 **Para sua próxima redação:**
1. **Revise** os pontos destacados acima
2. **Pratique** as competências que precisam de melhoria  
3. **Leia** redações nota 1000 para se inspirar
4. **Escreva** aplicando as correções sugeridas

### 💪 **Mensagem da Professora Carla:**
> "Sther, cada redação é um passo importante na sua jornada rumo ao ENEM! Continue praticando com dedicação. Você tem potencial para alcançar a nota 1000! 🌟"

**✨ A nota 1000 está ao seu alcance! Continue se esforçando! ✨**
"""
            
            return final_analysis
            
        except Exception as e:
            return f"""
# ❌ **Erro na Análise**

Desculpe, Sther! Houve um problema técnico na análise da sua redação.

**Erro:** {str(e)}

## 📞 **O que fazer:**
1. Verifique sua conexão com a internet
2. Tente novamente em alguns minutos
3. Se o problema persistir, fale com o suporte técnico

**Mesmo assim, aqui estão algumas dicas gerais para você:**

### 🎯 **Critérios básicos do ENEM:**
- **Estrutura:** Introdução, desenvolvimento (2-3 parágrafos), conclusão
- **Argumentação:** Use dados, exemplos e repertório sociocultural
- **Coesão:** Conecte ideias com conectivos adequados
- **Linguagem:** Mantenha registro formal
- **Proposta:** Detalhe quem, o que, como e para quê

**Continue praticando! A Professora Carla acredita em você! 💪**
"""

_singleton_instance = None

def get_local_redacao_rag_instance():
    """
    Retorna uma instância única (singleton) do LocalRedacaoRAG.
    Isso evita a inicialização no momento da importação.
    """
    global _singleton_instance
    if _singleton_instance is None:
        _singleton_instance = LocalRedacaoRAG()
    return _singleton_instance

def get_api_key_robust() -> Optional[str]:
    """
    Sistema robusto para obter API key que funciona no Streamlit Cloud.
    Resolve problemas de cache e secrets.
    """
    api_key = None
    
    # Método 1: Streamlit Secrets (preferencial para cloud)
    try:
        if hasattr(st, 'secrets'):
            # Força refresh do cache de secrets
            if hasattr(st.secrets, '_file_change_listener'):
                st.secrets._file_change_listener.check()
            
            # Tentativas múltiplas com nomes diferentes
            possible_keys = ["GROQ_API_KEY", "groq_api_key", "API_KEY", "api_key"]
            
            for key_name in possible_keys:
                try:
                    if key_name in st.secrets:
                        api_key = str(st.secrets[key_name]).strip()
                        if api_key and api_key != "sua_chave_groq_aqui" and len(api_key) > 10:
                            st.write(f"✅ API Key encontrada via secrets: {key_name}")
                            return api_key
                except Exception as e:
                    continue
                    
        st.write("⚠️ Streamlit secrets não encontrados ou vazios")
                    
    except Exception as e:
        st.write(f"❌ Erro ao acessar secrets: {str(e)}")
    
    # Método 2: Variáveis de ambiente
    try:
        possible_env_keys = ["GROQ_API_KEY", "groq_api_key", "API_KEY"]
        for key_name in possible_env_keys:
            env_key = os.environ.get(key_name)
            if env_key and env_key.strip() != "sua_chave_groq_aqui" and len(env_key.strip()) > 10:
                api_key = env_key.strip()
                st.write(f"✅ API Key encontrada via ambiente: {key_name}")
                return api_key
                
        st.write("⚠️ Variáveis de ambiente não encontradas")
                
    except Exception as e:
        st.write(f"❌ Erro ao acessar variáveis de ambiente: {str(e)}")
    
    # Método 3: Session state (cache temporário)
    try:
        if 'groq_api_key' in st.session_state:
            cached_key = st.session_state['groq_api_key']
            if cached_key and len(cached_key) > 10:
                st.write("✅ API Key encontrada no cache da sessão")
                return cached_key
                
    except Exception as e:
        st.write(f"❌ Erro ao acessar session state: {str(e)}")
    
    return None

def validate_api_key(api_key: str) -> bool:
    """Valida se a API key está funcionando"""
    if not api_key or len(api_key) < 10:
        return False
        
    try:
        # Teste rápido com a API Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": "teste"}],
            max_tokens=10
        )
        return True
    except Exception as e:
        st.write(f"❌ Validação da API key falhou: {str(e)}")
        return False

def setup_api_key_debug():
    """Função de debug para diagnosticar problemas de API key"""
    st.markdown("### 🔍 **Diagnóstico da API Key**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Verificações:")
        
        # Check 1: Streamlit secrets
        if hasattr(st, 'secrets'):
            if "GROQ_API_KEY" in st.secrets:
                key_preview = str(st.secrets["GROQ_API_KEY"])[:10] + "..."
                st.write(f"✅ Secret encontrado: {key_preview}")
                
                # Validar a key
                if validate_api_key(st.secrets["GROQ_API_KEY"]):
                    st.write("✅ API Key válida!")
                else:
                    st.write("❌ API Key inválida")
            else:
                st.write("❌ Secret GROQ_API_KEY não encontrado")
                st.write("**Secrets disponíveis:**", list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else "Nenhum")
        else:
            st.write("❌ st.secrets não disponível")
        
        # Check 2: Environment variables
        env_key = os.environ.get("GROQ_API_KEY")
        if env_key:
            env_preview = env_key[:10] + "..."
            st.write(f"✅ Variável de ambiente: {env_preview}")
        else:
            st.write("❌ Variável GROQ_API_KEY não encontrada")
    
    with col2:
        st.markdown("#### Teste Manual:")
        
        manual_key = st.text_input(
            "Cole sua API key aqui para teste:",
            type="password",
            help="Sua key não será salva, apenas testada"
        )
        
        if manual_key and st.button("🧪 Testar API Key"):
            if validate_api_key(manual_key):
                st.success("✅ API Key funcionando!")
                # Salva temporariamente na sessão
                st.session_state['groq_api_key'] = manual_key
                st.rerun()
            else:
                st.error("❌ API Key inválida")
    
    # Check final com função robusta
    st.markdown("#### Resultado Final:")
    final_key = get_api_key_robust()
    
    if final_key:
        st.success(f"✅ API Key obtida com sucesso: {final_key[:10]}...")
        if validate_api_key(final_key):
            st.success("✅ API Key validada e funcionando!")
        else:
            st.error("❌ API Key não está funcionando")
    else:
        st.error("❌ Nenhuma API Key válida encontrada")
        
        # Instruções de correção
        st.markdown("""
        ### 🔧 **Como Corrigir:**
        
        **No Streamlit Cloud:**
        1. Vá em **Settings** → **Secrets**
        2. Adicione:
        ```toml
        GROQ_API_KEY = "sua_chave_aqui"
        ```
        3. Clique em **Save**
        4. **Reinicie o app**
        
        **Localmente:**
        1. Crie arquivo `.env`:
        ```
        GROQ_API_KEY=sua_chave_aqui
        ```
        
        **Obter API Key Grátis:**
        1. Acesse: https://console.groq.com/
        2. Faça login/cadastro
        3. Crie uma nova API key
        4. Copie e cole acima
        """)

def analyze_redacao_pdf(pdf_content: bytes, filename: str) -> str:
    """Função principal para análise completa de redação em PDF"""
    
    # Obter instância do RAG
    rag_instance = get_local_redacao_rag_instance()
    
    # Diagnóstico de API key primeiro
    st.markdown("#### 🔍 Verificando API Key...")
    
    # Obter API key com sistema robusto
    api_key = get_api_key_robust()
    
    if not api_key:
        return """
# 🔑 **API Key Não Encontrada**

Olá, Sther! Para analisar sua redação, preciso que a chave da API Groq seja configurada.

**Diagnóstico realizado:**
- Verificação de Streamlit Secrets: ❌
- Verificação de Variáveis de Ambiente: ❌
- Cache da Sessão: ❌

## 🔧 **Como Resolver no Streamlit Cloud:**

### Passo 1: Obter API Key Grátis
1. Acesse: https://console.groq.com/
2. Faça login (ou crie uma conta)
3. Clique em "API Keys"
4. Clique em "Create API Key"
5. Copie a chave gerada

### Passo 2: Configurar no Streamlit Cloud
1. No seu app do Streamlit Cloud, clique em **"⚙️ Settings"**
2. Vá na aba **"Secrets"**
3. Cole exatamente isto:
```toml
GROQ_API_KEY = "sua_chave_copiada_aqui"
```
4. Clique em **"Save"**
5. **IMPORTANTE:** Reinicie o app clicando em "Reboot"

### Passo 3: Verificar
- Aguarde o app reiniciar
- Tente enviar uma redação novamente
- Use a aba "Diagnóstico" se persistir o problema

**A Professora Carla está ansiosa para te ajudar! 🌟**
"""
    
    # Validar API key
    if not validate_api_key(api_key):
        return f"""
# ⚠️ **API Key Inválida**

A API key foi encontrada, mas não está funcionando.

**Key encontrada:** {api_key[:10]}...

## 🔧 **Possíveis Problemas:**
1. **Key expirada:** Gere uma nova no console da Groq
2. **Key incorreta:** Verifique se copiou completamente
3. **Espaços extras:** Remova espaços antes/depois da key
4. **Cota esgotada:** Verifique seu limite na Groq Console

## 💡 **Solução:**
1. Acesse: https://console.groq.com/
2. Gere uma nova API key
3. Substitua nos Secrets do Streamlit
4. Reinicie o app

**Use a aba "Diagnóstico" para mais detalhes.**
"""
    
    st.success(f"✅ API Key válida: {api_key[:10]}...")
    
    try:
        # Extrair texto do PDF
        texto_redacao = rag_instance.extract_text_from_pdf(pdf_content)
        
        if not texto_redacao or texto_redacao.startswith("Não foi possível") or texto_redacao.startswith("Bibliotecas"):
            return f"""
# ❌ **Problema com o PDF**

**Arquivo:** {filename}

Não consegui extrair o texto do seu PDF. Isso pode acontecer por alguns motivos:

## 🔧 **Possíveis soluções:**
1. **PDF de imagem:** Se sua redação foi escaneada, o PDF contém apenas imagens
2. **PDF protegido:** Alguns PDFs têm proteção que impede extração de texto
3. **Formato incompatível:** Tente salvar novamente como PDF

## 💡 **Como resolver:**
- **Recomendado:** Digite sua redação diretamente no chat para análise
- **Alternativa:** Use um conversor online para transformar imagem em texto
- **OCR:** Use Google Lens ou similar para extrair texto de imagens

## 📝 **Envie por texto:**
Você pode copiar e colar sua redação diretamente no chat com a mensagem:
> "Professora Carla, poderia analisar minha redação: [COLE SEU TEXTO AQUI]"

**A Professora Carla está pronta para te ajudar de qualquer forma! 💪**
"""
        
        # Verificar se o texto extraído é válido
        if len(texto_redacao.split()) < 50:
            return f"""
# ⚠️ **Texto muito curto**

**Arquivo:** {filename}  
**Palavras extraídas:** {len(texto_redacao.split())}

O texto extraído parece muito curto para uma redação ENEM (mínimo ~150 palavras).

**Texto extraído:**
```
{texto_redacao[:500]}...
```

## 💡 **Sugestões:**
1. Verifique se o PDF contém o texto completo da redação
2. Tente enviar sua redação por texto diretamente no chat
3. Certifique-se de que a redação tem pelo menos 150 palavras

**A Professora Carla aguarda sua redação completa para uma análise detalhada! 📝**
"""
        
        # Realizar análise completa
        return rag_instance.analyze_redacao_text(texto_redacao, filename, api_key)
        
    except Exception as e:
        return f"""
# ❌ **Erro Técnico**

**Arquivo:** {filename}  
**Erro:** {str(e)}

Desculpe, Sther! Houve um problema técnico ao processar sua redação.

## 🔄 **Tente:**
1. Enviar o arquivo novamente
2. Verificar se o PDF não está corrompido
3. Enviar a redação por texto no chat

## 🔍 **Debug Info:**
- API Key: ✅ Válida
- Sistema RAG: ✅ Inicializado
- Erro: {str(e)}

## 📱 **Contato:**
Se o problema persistir, relate este erro para o suporte técnico.

**A Professora Carla está aqui para te ajudar! Não desista! 💪**
"""

def setup_redacao_ui():
    """Configura a interface do sistema de redação"""
    st.markdown("""
    <div class="teacher-intro">
        <h3>✍️ Professora Carla - Análise de Redação</h3>
        <p>Sistema completo de análise baseado nos critérios do ENEM</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab para diagnóstico
    tab1, tab2 = st.tabs(["📤 Análise de Redação", "🔍 Diagnóstico da API"])
    
    with tab1:
        st.markdown("### 📤 **Envie sua Redação**")
        
        uploaded_file = st.file_uploader(
            "Escolha um arquivo PDF com sua redação:",
            type=['pdf'],
            help="Envie sua redação em formato PDF para análise completa"
        )
        
        if uploaded_file is not None:
            if st.button("🔍 Analisar Redação", type="primary"):
                with st.spinner("📝 Professora Carla analisando sua redação..."):
                    try:
                        # Lê o conteúdo do arquivo
                        pdf_content = uploaded_file.read()
                        
                        # Analisa a redação
                        analise = analyze_redacao_pdf(pdf_content, uploaded_file.name)
                        
                        # Exibe o resultado
                        st.markdown("### 📋 **Resultado da Análise**")
                        st.markdown(analise)
                        
                        # Botão para download do relatório
                        st.download_button(
                            label="📥 Baixar Relatório Completo",
                            data=analise,
                            file_name=f"analise_redacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao processar a redação: {str(e)}")
                        st.info("💡 Verifique se o arquivo é um PDF válido e tente novamente.")
    
    with tab2:
        setup_api_key_debug()
    
    # Informações adicionais
    with st.expander("ℹ️ Como funciona a análise?"):
        st.markdown("""
        **A Professora Carla analisa sua redação baseada nos 5 critérios do ENEM:**
        
        1. **🏗️ Estrutura Textual** - Organização e formato dissertativo-argumentativo
        2. **💭 Conteúdo** - Argumentação e repertório sociocultural  
        3. **🗣️ Linguagem** - Coesão, registro formal e variedade lexical
        4. **🎯 Argumentação** - Desenvolvimento lógico das ideias
        5. **📋 Proposta de Intervenção** - Detalhamento e viabilidade
        
        **📊 Você receberá:**
        - Nota de 0 a 1000 pontos
        - Feedback detalhado por competência
        - Sugestões específicas de melhoria
        - Dicas personalizadas da Professora Carla
        """)
    
    # Casos de sucesso
    with st.expander("🏆 Exemplos de Redações Nota 1000"):
        st.markdown("**Inspire-se com estes exemplos:**")
        st.markdown("- 📝 Redação sobre tecnologia e sociedade")
        st.markdown("- 📝 Redação sobre meio ambiente")
        st.markdown("- 📝 Redação sobre educação") 