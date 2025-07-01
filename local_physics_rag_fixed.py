#!/usr/bin/env python3
"""
Sistema RAG Local para Professor Fernando - Física
Utiliza um índice FAISS pré-construído e baixado do Hugging Face.
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

# Diretório para armazenar o índice FAISS
FAISS_INDEX_DIR = "faiss_index_physics"

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
                max_tokens=2048,
                stop=stop if stop else None
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro na API: {str(e)}"

class LocalPhysicsRAG:
    """Sistema RAG que carrega um índice FAISS remoto para Física."""
    
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.memory = None
        self.rag_chain = None
        self.embeddings = None
        self.is_initialized = False
        self.physics_folder_path = FAISS_INDEX_DIR
        
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
        Garante que o índice FAISS esteja disponível, baixando-o se necessário.
        """
        os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
        
        index_file = os.path.join(FAISS_INDEX_DIR, "index_physics.faiss")
        pkl_file = os.path.join(FAISS_INDEX_DIR, "index_physics.pkl")

        # Verifica se os dois arquivos já existem
        if os.path.exists(index_file) and os.path.exists(pkl_file):
            print("✅ Índice FAISS de física já existe localmente.")
            return True

        st.info("📥 Baixando índice de física do Hugging Face...")
        print("📥 Baixando índice de física do Hugging Face...")

        # URLs dos arquivos no Hugging Face
        faiss_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_physics.faiss"
        pkl_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_physics.pkl"

        # Baixa os dois arquivos
        faiss_success = self._download_file(faiss_url, index_file)
        pkl_success = self._download_file(pkl_url, pkl_file)

        if faiss_success and pkl_success:
            st.success("✅ Índice de física baixado com sucesso!")
            return True
        else:
            st.error("❌ Falha ao baixar os arquivos do índice de física.")
            # Limpa arquivos parciais em caso de falha
            if os.path.exists(index_file): 
                os.remove(index_file)
            if os.path.exists(pkl_file): 
                os.remove(pkl_file)
            return False
            
    def initialize(self, api_key: str) -> bool:
        """
        Inicializa o sistema: baixa o índice, carrega o vectorstore e cria a cadeia RAG.
        """
        # Armazena a API key para uso posterior
        self.api_key = api_key
        
        if self.is_initialized:
            return True
            
        # 1. Garantir que o índice FAISS está disponível
        if not self._ensure_faiss_index_is_ready():
            return False
            
        # 2. Carregar o Vectorstore FAISS (e configurar embeddings aqui)
        try:
            st.info("📚 Carregando base de conhecimento de física (FAISS)...")
            print("📚 Carregando base de conhecimento de física (FAISS)...")
            
            # Passo 2.1: Configurar embeddings ANTES de carregar o FAISS
            self._setup_embeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v1")
            if not self.embeddings:
                st.error("Embeddings não foram inicializadas. Abortando.")
                return False

            # Define nomes dos arquivos para compatibilidade
            index_file = os.path.join(FAISS_INDEX_DIR, "index_physics.faiss")
            pkl_file = os.path.join(FAISS_INDEX_DIR, "index_physics.pkl")
            
            self.vectorstore = FAISS.load_local(
                folder_path=FAISS_INDEX_DIR, 
                embeddings=self.embeddings,
                index_name="index_physics", 
                allow_dangerous_deserialization=True # Necessário para pkl
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            st.success("✅ Base de conhecimento carregada.")
            print("✅ Base de conhecimento carregada.")
        except Exception as e:
            st.error(f"Erro ao carregar o índice FAISS: {e}")
            print(f"❌ Erro ao carregar o índice FAISS: {e}")
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
            
            # Adiciona o prompt personalizado para Física
            prompt_template = """Você é o Professor Fernando, especialista em física do ENEM. Responda como um professor para uma estudante de 17 anos chamada Sther.

🔥 REGRAS DE FORMATAÇÃO FÍSICA (CRÍTICO - SEMPRE SEGUIR):

1. **DELIMITADORES OBRIGATÓRIOS:**
   - Fórmulas no meio do texto: $sua-formula-aqui$
   - Fórmulas em destaque: $$sua-formula-aqui$$
   - NUNCA use \\text{força} sozinho - sempre use $\\text{força}$

2. **EXEMPLOS CORRETOS:**
   ✅ A velocidade é calculada por $v = \\frac{\\Delta s}{\\Delta t}$
   ✅ A Segunda Lei de Newton: $$F = ma$$
   ✅ Para energia cinética: $$E_c = \\frac{mv^2}{2}$$

3. **COMANDOS LATEX ESSENCIAIS:**
   - Frações: $\\frac{numerador}{denominador}$
   - Raízes: $\\sqrt{x}$ ou $\\sqrt[n]{x}$
   - Texto em fórmulas: $\\text{força} = massa \\times aceleração$
   - Potências: $v^2$, $e^{-x}$
   - Índices: $v_0$, $a_{max}$

4. **SEMPRE INCLUIR:**
   - Explicação passo-a-passo
   - Exemplos práticos
   - Dicas para o ENEM
   - Analogias do cotidiano

5. **ESTILO DO PROFESSOR FERNANDO:**
   - Use analogias das séries que a Sther gosta (FRIENDS, Big Bang Theory, etc.)
   - Seja didático e paciente
   - Conecte conceitos com exemplos práticos

Com base no CONTEXTO abaixo, responda à PERGUNTA do aluno.
Se a resposta não estiver no contexto, use seu conhecimento em física, mas mantenha o estilo.

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA (com fórmulas bem formatadas e estilo do Professor Fernando):
"""
            # Atualiza o prompt da cadeia
            try:
                if hasattr(self.rag_chain.combine_docs_chain, "llm_chain"):
                    self.rag_chain.combine_docs_chain.llm_chain.prompt = prompt_template
                elif hasattr(self.rag_chain, "combine_docs_chain"):
                    from langchain.prompts import PromptTemplate
                    prompt = PromptTemplate(
                        input_variables=["context", "question"],
                        template=prompt_template
                    )
                    self.rag_chain.combine_docs_chain.llm_chain.prompt = prompt
            except Exception as prompt_error:
                print(f"Aviso: Não foi possível atualizar o prompt: {prompt_error}")
            
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
            return {"answer": "O sistema RAG não foi inicializado corretamente.", "source_documents": []}
        
        try:
            # Busca por documentos relevantes
            docs = self.retriever.get_relevant_documents(question)
            
            if not docs:
                # Fallback para casos onde não encontramos documentos relevantes
                return {
                    "answer": "Não encontrei informações específicas sobre isso na base de dados de física, mas posso tentar responder com conhecimento geral.",
                    "source_documents": []
                }
            
            # Forma o contexto a partir dos documentos
            context = "\n\n".join([doc.page_content for doc in docs[:5]])
            
            # Usa o LLM para gerar uma resposta
            prompt = f"""Você é o Professor Fernando, especialista em física do ENEM. Responda como um professor para uma estudante de 17 anos chamada Sther.

Com base no contexto a seguir, responda à pergunta da forma mais didática possível.
Se a resposta não estiver no contexto, use seu conhecimento geral em física do ENEM.

CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA:"""
            
            if hasattr(self.rag_chain, "llm") and self.rag_chain.llm:
                llm = self.rag_chain.llm
            else:
                # Caso a cadeia RAG não tenha sido configurada corretamente
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    # Tenta usar a API KEY armazenada como atributo
                    if hasattr(self, "api_key") and self.api_key:
                        api_key = self.api_key
                    else:
                        return {"answer": "API Key não disponível. Não é possível gerar resposta.", "source_documents": []}
                
                llm = GroqLLM(api_key=api_key)
            
            answer = llm.invoke(prompt)
            
            # Atualiza memória conversacional
            if self.memory:
                self.memory.save_context(
                    {"question": question}, 
                    {"answer": answer}
                )
                
            return {
                "answer": answer,
                "source_documents": docs
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro ao processar resposta: {error_details}")
            return {"answer": f"Erro ao processar a pergunta: {str(e)}", "source_documents": []}
    
    def search_relevant_content(self, query: str, k: int = 3) -> List[Document]:
        """Busca por conteúdo relevante no vectorstore."""
        if not self.vectorstore:
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Erro na busca de similaridade: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas detalhadas do sistema RAG, incluindo uma amostra de documentos.
        """
        if not self.is_initialized or not self.vectorstore:
            return {
                "status": "Não Carregado",
                "total_documents": 0,
                "sample_documents": []
            }

        try:
            total_documents = self.vectorstore.index.ntotal
            
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
                "sample_documents": sample_files
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas do RAG: {e}")
            return {
                "status": "Erro na Leitura",
                "total_documents": 0,
                "sample_documents": [str(e)]
            }
    
    def clear_memory(self):
        """Limpa a memória da conversa."""
        if self.memory:
            self.memory.clear()

_singleton_instance = None

def get_local_physics_rag_instance():
    """
    Retorna uma instância única (singleton) do LocalPhysicsRAG.
    Isso evita a inicialização no momento da importação.
    """
    global _singleton_instance
    if _singleton_instance is None:
        _singleton_instance = LocalPhysicsRAG()
    return _singleton_instance 