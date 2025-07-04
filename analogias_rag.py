#!/usr/bin/env python3
"""
Sistema RAG para Analogias - Baseado em Séries de TV
Utiliza índices FAISS pré-construídos e baixados do Hugging Face.
"""

import streamlit as st
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

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

# Diretório para armazenar os índices FAISS de analogias
FAISS_ANALOGIAS_DIR = "faiss_index_analogias"

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
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro na API: {str(e)}"

class AnalogiasRAG:
    """Sistema RAG que carrega índices FAISS remotos para analogias baseadas em séries."""
    
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.memory = None
        self.rag_chain = None
        self.embeddings = None
        self.is_initialized = False
        self.analogias_folder_path = FAISS_ANALOGIAS_DIR

    def _setup_embeddings(self, model_name: str):
        """Configura o modelo de embeddings do Hugging Face."""
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
        os.makedirs(FAISS_ANALOGIAS_DIR, exist_ok=True)
        
        # Arquivos de analogias
        index_file = os.path.join(FAISS_ANALOGIAS_DIR, "index_analogias.faiss")
        pkl_file = os.path.join(FAISS_ANALOGIAS_DIR, "index_analogias.pkl")

        # Verifica se todos os arquivos já existem
        if os.path.exists(index_file) and os.path.exists(pkl_file):
            print("✅ Índices FAISS de analogias já existem localmente.")
            return True

        st.info("📥 Baixando índices de analogias do Hugging Face...")
        print("📥 Baixando índices de analogias do Hugging Face...")

        # URLs dos arquivos no Hugging Face
        faiss_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_analogias.faiss"
        pkl_url = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_analogias.pkl"

        # Baixa os arquivos
        faiss_success = self._download_file(faiss_url, index_file)
        pkl_success = self._download_file(pkl_url, pkl_file)

        if faiss_success and pkl_success:
            st.success("✅ Índices de analogias baixados com sucesso!")
            return True
        else:
            st.error("❌ Falha ao baixar os arquivos dos índices de analogias.")
            # Limpa arquivos parciais em caso de falha
            for file_path in [index_file, pkl_file]:
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
            
        # 2. Carregar os Vectorstores FAISS
        try:
            st.info("📚 Carregando base de conhecimento de analogias (FAISS)...")
            print("📚 Carregando base de conhecimento de analogias (FAISS)...")
            
            # Configurar embeddings ANTES de carregar o FAISS
            self._setup_embeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v1")
            if not self.embeddings:
                st.error("Embeddings não foram inicializadas. Abortando.")
                return False

            # Carrega o vectorstore de analogias
            self.vectorstore = FAISS.load_local(
                FAISS_ANALOGIAS_DIR, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Configura retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            st.success("✅ Base de conhecimento de analogias carregada.")
            print("✅ Base de conhecimento de analogias carregada.")
        except Exception as e:
            st.error(f"Erro ao carregar os índices FAISS de analogias: {e}")
            print(f"❌ Erro ao carregar os índices FAISS de analogias: {e}")
            return False
    
        # 3. Criar a cadeia RAG
        try:
            st.info("🔗 Criando a cadeia de analogias RAG...")
            print("🔗 Criando a cadeia de analogias RAG...")
            
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
            
            # Adiciona o prompt personalizado para Analogias
            prompt_template = """Você é um especialista em criar analogias educacionais baseadas em séries de TV populares. 
Sua missão é ajudar professores a explicar conceitos complexos usando referências das séries que a Sther (17 anos) conhece.

🎬 **SÉRIES DISPONÍVEIS:**
- FRIENDS (Central Perk, apartamento de Monica, etc.)
- The Big Bang Theory (apartamento de Sheldon, Caltech, etc.)
- Greys Anatomy (Grey Sloan Memorial Hospital)
- Stranger Things (Hawkins, laboratório, etc.)
- Jovem Sheldon (Texas, família Cooper)
- Wandavision (Westview, WandaVision, etc.)

📚 **OBJETIVO:** Criar analogias específicas e relevantes que:
1. Conectem conceitos acadêmicos com situações das séries
2. Sejam fáceis de entender para uma estudante de 17 anos
3. Tornem o aprendizado mais divertido e memorável
4. Usem personagens e situações específicas das séries

🔍 **CONTEXTO DAS SÉRIES:**
{context}

❓ **PERGUNTA:** {question}

💡 **RESPOSTA:** Crie uma analogia específica usando as informações das séries fornecidas. 
Seja criativo, mas mantenha a precisão acadêmica. Use emojis e seja didático!

**FORMATO DA RESPOSTA:**
🎬 **Analogia da Série:** [Nome da série e situação específica]
📚 **Conceito:** [Explicação do conceito acadêmico]
🔗 **Conexão:** [Como a situação da série se conecta ao conceito]
💡 **Dica:** [Dica prática para memorizar]
"""
            # Atualiza o prompt da cadeia
            if hasattr(self.rag_chain.combine_docs_chain, "llm_chain"):
                self.rag_chain.combine_docs_chain.llm_chain.prompt.template = prompt_template
            
            self.is_initialized = True
            st.success("✅ Cadeia RAG de analogias criada e pronta para uso!")
            print("✅ Cadeia RAG de analogias criada e pronta para uso!")
            return True

        except Exception as e:
            st.error(f"Erro ao criar a cadeia RAG de analogias: {e}")
            print(f"❌ Erro ao criar a cadeia RAG de analogias: {e}")
            return False
    
    def get_analogia(self, conceito: str, materia: str) -> str:
        """Obtém uma analogia específica para um conceito e matéria."""
        if not self.rag_chain:
            return "O sistema RAG de analogias não foi inicializado corretamente."
        
        try:
            # Cria uma pergunta específica para buscar analogias
            pergunta = f"Crie uma analogia baseada em séries de TV para explicar o conceito '{conceito}' na matéria de {materia} para uma estudante de 17 anos"
            
            response = self.rag_chain({"question": pergunta})
            return response.get("answer", "Não foi possível gerar uma analogia no momento.")
        except Exception as e:
            return f"Erro ao processar a analogia: {str(e)}"
    
    def search_analogias(self, query: str, k: int = 3) -> List[Document]:
        """Busca por analogias relevantes no vectorstore."""
        if not self.vectorstore:
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Erro na busca de analogias: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas detalhadas do sistema RAG de analogias.
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
            print(f"Erro ao obter estatísticas do RAG de analogias: {e}")
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

def get_analogias_rag_instance():
    """
    Retorna uma instância única (singleton) do AnalogiasRAG.
    """
    global _singleton_instance
    if _singleton_instance is None:
        _singleton_instance = AnalogiasRAG()
    return _singleton_instance

def get_analogia_para_conceito(conceito: str, materia: str, api_key: str) -> str:
    """
    Função wrapper para obter analogia de um conceito específico.
    """
    try:
        analogias_rag = get_analogias_rag_instance()
        
        # Inicializa se necessário
        if not analogias_rag.is_initialized:
            if not analogias_rag.initialize(api_key):
                return "❌ Erro ao inicializar o sistema de analogias."
        
        # Obtém a analogia
        analogia = analogias_rag.get_analogia(conceito, materia)
        return analogia
        
    except Exception as e:
        return f"❌ Erro ao gerar analogia: {str(e)}"
