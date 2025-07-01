#!/usr/bin/env python3
"""
Script para testar o download dos índices FAISS do Hugging Face
"""

import os
import shutil
from local_physics_rag_fixed import LocalPhysicsRAG, FAISS_INDEX_DIR

# Limpa o diretório FAISS se existir
if os.path.exists(FAISS_INDEX_DIR):
    print(f"Removendo diretório FAISS existente: {FAISS_INDEX_DIR}")
    shutil.rmtree(FAISS_INDEX_DIR)
    print("✅ Diretório removido com sucesso")

# Cria uma instância do RAG
print("Criando instância do RAG...")
rag = LocalPhysicsRAG()

# Testa o método _ensure_faiss_index_is_ready
print("\n🔄 Testando download do índice FAISS...")
success = rag._ensure_faiss_index_is_ready()

if success:
    print("✅ Índice FAISS baixado com sucesso!")
    
    # Verifica se os arquivos existem
    index_file = os.path.join(FAISS_INDEX_DIR, "index_physics.faiss")
    pkl_file = os.path.join(FAISS_INDEX_DIR, "index_physics.pkl")
    
    if os.path.exists(index_file):
        print(f"✅ Arquivo FAISS encontrado: {index_file}")
        print(f"   Tamanho: {os.path.getsize(index_file)/1024/1024:.2f} MB")
    else:
        print(f"❌ Arquivo FAISS não encontrado: {index_file}")
    
    if os.path.exists(pkl_file):
        print(f"✅ Arquivo PKL encontrado: {pkl_file}")
        print(f"   Tamanho: {os.path.getsize(pkl_file)/1024/1024:.2f} MB")
    else:
        print(f"❌ Arquivo PKL não encontrado: {pkl_file}")
else:
    print("❌ Falha ao baixar o índice FAISS")

print("\n📋 Teste concluído!") 