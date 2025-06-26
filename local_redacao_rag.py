#!/usr/bin/env python3
"""
Sistema RAG Local para Professora Carla - Redação
Utiliza índices FAISS pré-construídos e baixados do Hugging Face.
"""

import streamlit as st
import os
import requests
from typing import Dict, List, Any, Optional

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
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
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
        
        # Arquivos principais de redação
        index_file = os.path.join(FAISS_INDEX_DIR, "index_redacao.faiss")
        pkl_file = os.path.join(FAISS_INDEX_DIR, "index_redacao.pkl")
        
        # Arquivos de casos de sucesso
        success_index_file = os.path.join(FAISS_SUCCESS_INDEX_DIR, "index_success_red.faiss")
        success_pkl_file = os.path.join(FAISS_SUCCESS_INDEX_DIR, "index_success_red.pkl")

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

        # Baixa os arquivos principais
        faiss_success = self._download_file(faiss_url, index_file)
        pkl_success = self._download_file(pkl_url, pkl_file)
        
        # Baixa os arquivos de casos de sucesso
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
                allow_dangerous_deserialization=True # Necessário para pkl
            )
            
            # Configura retrievers
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            self.success_retriever = self.success_vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            st.success("✅ Base de conhecimento carregada.")
            print("✅ Base de conhecimento carregada.")
        except Exception as e:
            st.error(f"Erro ao carregar os índices FAISS: {e}")
            print(f"❌ Erro ao carregar os índices FAISS: {e}")
            return False
    
        # 3. Criar a cadeia RAG
        try:
            st.info("🔗 Criando a cadeia de conversação RAG...")
            print("🔗 Criando a cadeia de conversação RAG...")
            
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            llm = GroqLLM(api_key=api_key)

            self.rag_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.retriever,
                memory=self.memory,
                return_source_documents=True,
                output_key="answer",
            )
            
            # Adiciona o prompt personalizado para Redação
            prompt_template = """Você é a Professora Carla, especialista em redação do ENEM. Responda como uma professora para uma estudante de 17 anos chamada Sther.

🔥 REGRAS DE FORMATAÇÃO DE REDAÇÃO (CRÍTICO - SEMPRE SEGUIR):

1. **DELIMITADORES OBRIGATÓRIOS:**
   - Conceitos no meio do texto: $seu-conceito-aqui$
   - Estruturas em destaque: $$sua-estrutura-aqui$$
   - NUNCA use \\text{Argumentação} sozinho - sempre use $\\text{Argumentação}$

2. **EXEMPLOS CORRETOS:**
   ✅ A argumentação é essencial: $\\text{desenvolvimento lógico}$
   ✅ Estrutura da redação: $$introdução + desenvolvimento + conclusão$$
   ✅ Para conectivos: $$coesão textual = fluidez$$

3. **COMANDOS LATEX ESSENCIAIS:**
   - Frações: $\\frac{numerador}{denominador}$
   - Raízes: $\\sqrt{x}$ ou $\\sqrt[n]{x}$
   - Texto em fórmulas: $\\text{Redação} = \\text{dissertação}$
   - Potências: $nota^{1000}$, $pontos^5$
   - Índices: $comp_1$, $comp_2$

4. **SEMPRE INCLUIR:**
   - Explicação passo-a-passo
   - Exemplos práticos de redação
   - Dicas para o ENEM
   - Analogias do cotidiano

5. **ESTILO DA PROFESSORA CARLA:**
   - Use analogias das séries que a Sther gosta (FRIENDS, Big Bang Theory, etc.)
   - Seja didática e paciente
   - Conecte conceitos de redação com exemplos práticos
   - Explique como Monica organizaria uma redação perfeita

6. **ANALOGIAS DAS SÉRIES POR TÓPICO:**
   - **Estrutura**: "Como Monica organizava seus álbuns - cada parágrafo tem seu lugar específico!"
   - **Argumentação**: "Como Sheldon explicava: 'Bazinga! A argumentação segue uma lógica perfeita!'"
   - **Coesão**: "Pense na coesão como quando o grupo se reunia no Central Perk - tudo conectado!"
   - **Proposta de Intervenção**: "Lembra quando Chandler fazia planos? 'Could this BE more estruturado?'"

7. **CRITÉRIOS DO ENEM (SEMPRE MENCIONAR):**
   - **Competência 1**: Estrutura dissertativo-argumentativa
   - **Competência 2**: Desenvolvimento do tema e argumentação
   - **Competência 3**: Coesão e coerência
   - **Competência 4**: Repertório sociocultural
   - **Competência 5**: Proposta de intervenção

Com base no CONTEXTO abaixo, responda à PERGUNTA do aluno.
Se a resposta não estiver no contexto, use seu conhecimento em redação, mas mantenha o estilo.

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA (com conceitos bem formatados e estilo da Professora Carla):
"""
            # Atualiza o prompt da cadeia
            if hasattr(self.rag_chain.combine_docs_chain, "llm_chain"):
                self.rag_chain.combine_docs_chain.llm_chain.prompt.template = prompt_template
            
            self.is_initialized = True
            st.success("✅ Cadeia RAG criada e pronta para uso!")
            print("✅ Cadeia RAG criada e pronta para uso!")
            return True

        except Exception as e:
            st.error(f"Erro ao criar a cadeia RAG: {e}")
            print(f"❌ Erro ao criar a cadeia RAG: {e}")
            return False
    
    def get_response(self, question: str) -> Dict[str, Any]:
        """Obtém uma resposta do sistema RAG."""
        if not self.rag_chain:
            return {"answer": "O sistema RAG não foi inicializado corretamente."}
        
        try:
            return self.rag_chain({"question": question})
        except Exception as e:
            return {"answer": f"Erro ao processar a pergunta: {str(e)}"}
    
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