#!/usr/bin/env python3
"""
Sistema de RAG Local para Física (Fixed)
Versão compatível com o sistema de importação do app.py
"""

import os
import pickle
import faiss
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.vectorstores.faiss import FAISS
import requests
from io import BytesIO
import streamlit as st

# URLs para os arquivos FAISS
PHYSICS_INDEX_URL = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_physics.faiss"
PHYSICS_PKL_URL = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_physics.pkl"

# Diretório local para armazenar os arquivos baixados
LOCAL_DIR = "faiss_index_physics"

class LocalPhysicsRAG:
    """Classe para gerenciar o sistema RAG local de física"""
    
    def __init__(self):
        self.physics_faiss = None
        self.is_initialized = False
        self.api_key = None
        
    def ensure_directory_exists(self, directory):
        """Garante que o diretório existe"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def download_file(self, url, local_path):
        """Baixa um arquivo da URL para o caminho local"""
        response = requests.get(url)
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return local_path
    
    def load_or_download_faiss_index(self):
        """
        Carrega o índice FAISS de física do disco local ou baixa se não existir
        """
        self.ensure_directory_exists(LOCAL_DIR)
        
        index_path = os.path.join(LOCAL_DIR, "index_physics.faiss")
        pkl_path = os.path.join(LOCAL_DIR, "index_physics.pkl")
        
        # Verifica se os arquivos existem localmente
        if not (os.path.exists(index_path) and os.path.exists(pkl_path)):
            print("Baixando arquivos FAISS para física...")
            self.download_file(PHYSICS_INDEX_URL, index_path)
            self.download_file(PHYSICS_PKL_URL, pkl_path)
        
        # Carrega o índice FAISS
        index = faiss.read_index(index_path)
        
        # Carrega o pickle com os documentos
        with open(pkl_path, "rb") as f:
            docstore = pickle.load(f)
        
        # Cria o objeto FAISS com o índice e documentos
        embeddings = OpenAIEmbeddings(api_key=self.api_key)
        self.physics_faiss = FAISS(embeddings.embed_query, index, docstore, {})
        
        return True
    
    def initialize(self, api_key):
        """Inicializa o sistema RAG com a API key fornecida"""
        try:
            self.api_key = api_key
            success = self.load_or_download_faiss_index()
            self.is_initialized = success
            return success
        except Exception as e:
            print(f"Erro ao inicializar o sistema RAG de física: {e}")
            self.is_initialized = False
            return False
    
    def get_physics_context(self, query, k=5):
        """
        Obtém o contexto de física para uma consulta
        
        Args:
            query: A consulta do usuário
            k: Número de documentos a serem recuperados
            
        Returns:
            Uma string com o contexto relevante
        """
        if not self.is_initialized or self.physics_faiss is None:
            return "Sistema RAG de física não inicializado."
        
        try:
            # Recupera os documentos relevantes
            docs = self.physics_faiss.similarity_search(query, k=k)
            
            # Formata o contexto
            context_parts = []
            for i, doc in enumerate(docs):
                context_parts.append(f"Documento {i+1}:\n{doc.page_content}\n")
            
            return "\n".join(context_parts)
        
        except Exception as e:
            print(f"Erro ao recuperar contexto de física: {e}")
            return "Não foi possível recuperar o contexto de física."

# Instância global para uso em outros módulos
_physics_rag_instance = None

def get_local_physics_rag_instance():
    """Retorna a instância global do sistema RAG de física"""
    global _physics_rag_instance
    
    if _physics_rag_instance is None:
        _physics_rag_instance = LocalPhysicsRAG()
    
    return _physics_rag_instance

# Para uso direto
if __name__ == "__main__":
    rag = get_local_physics_rag_instance()
    api_key = input("Digite sua API key da OpenAI: ")
    
    if rag.initialize(api_key):
        query = input("Digite sua consulta sobre física: ")
        context = rag.get_physics_context(query)
        print("\nContexto relevante:\n")
        print(context)
    else:
        print("Falha ao inicializar o sistema RAG de física.") 