#!/usr/bin/env python3
"""
Sistema de RAG Local para Física
Baseado no modelo de outros sistemas RAG do projeto
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

# URLs para os arquivos FAISS
PHYSICS_INDEX_URL = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_physics.faiss"
PHYSICS_PKL_URL = "https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_physics.pkl"

# Diretório local para armazenar os arquivos baixados
LOCAL_DIR = "faiss_index_physics"

def ensure_directory_exists(directory):
    """Garante que o diretório existe"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, local_path):
    """Baixa um arquivo da URL para o caminho local"""
    response = requests.get(url)
    with open(local_path, 'wb') as f:
        f.write(response.content)
    return local_path

def load_or_download_faiss_index():
    """
    Carrega o índice FAISS de física do disco local ou baixa se não existir
    """
    ensure_directory_exists(LOCAL_DIR)
    
    index_path = os.path.join(LOCAL_DIR, "index_physics.faiss")
    pkl_path = os.path.join(LOCAL_DIR, "index_physics.pkl")
    
    # Verifica se os arquivos existem localmente
    if not (os.path.exists(index_path) and os.path.exists(pkl_path)):
        print("Baixando arquivos FAISS para física...")
        download_file(PHYSICS_INDEX_URL, index_path)
        download_file(PHYSICS_PKL_URL, pkl_path)
    
    # Carrega o índice FAISS
    index = faiss.read_index(index_path)
    
    # Carrega o pickle com os documentos
    with open(pkl_path, "rb") as f:
        docstore = pickle.load(f)
    
    # Cria o objeto FAISS com o índice e documentos
    embeddings = OpenAIEmbeddings()
    physics_faiss = FAISS(embeddings.embed_query, index, docstore, {})
    
    return physics_faiss

def get_physics_context(query, k=5):
    """
    Obtém o contexto de física para uma consulta
    
    Args:
        query: A consulta do usuário
        k: Número de documentos a serem recuperados
        
    Returns:
        Uma string com o contexto relevante
    """
    try:
        # Carrega o índice FAISS
        physics_faiss = load_or_download_faiss_index()
        
        # Recupera os documentos relevantes
        docs = physics_faiss.similarity_search(query, k=k)
        
        # Formata o contexto
        context_parts = []
        for i, doc in enumerate(docs):
            context_parts.append(f"Documento {i+1}:\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    
    except Exception as e:
        print(f"Erro ao recuperar contexto de física: {e}")
        return "Não foi possível recuperar o contexto de física."

# Função principal para uso em outros módulos
def get_physics_knowledge(query):
    """Função principal para obter conhecimento de física"""
    return get_physics_context(query) 