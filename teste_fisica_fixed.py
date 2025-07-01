#!/usr/bin/env python3
"""
Script de teste para o professor de física (versão corrigida)
"""

import os
import sys
from dotenv import load_dotenv
import time

# Carrega variáveis de ambiente (API_KEY)
load_dotenv()

# Configuração básica
print("📋 Teste do Professor Fernando (Física) - Versão Corrigida")
print("🔧 Verificando arquivos necessários...")

required_files = [
    "professor_fernando_local.py",
    "local_physics_rag_fixed.py"
]

for file in required_files:
    if not os.path.exists(file):
        print(f"❌ Arquivo {file} não encontrado!")
        sys.exit(1)
    else:
        print(f"✅ {file} encontrado")

# Importa o professor
try:
    print("🔄 Importando professor_fernando_local...")
    from professor_fernando_local import get_professor_fernando_local_response, professor_fernando_local
    print("✅ Importação bem-sucedida")
except Exception as e:
    print(f"❌ Erro na importação: {e}")
    sys.exit(1)

# Verifica API Key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ API Key não encontrada no ambiente. Defina GROQ_API_KEY")
    sys.exit(1)
print("✅ API Key encontrada")

# Verifica se o diretório FAISS existe
from local_physics_rag_fixed import FAISS_INDEX_DIR
if os.path.exists(FAISS_INDEX_DIR):
    print(f"✅ Diretório FAISS encontrado: {FAISS_INDEX_DIR}")
    
    # Verifica se os arquivos FAISS existem
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
    print(f"⚠️ Diretório FAISS não encontrado: {FAISS_INDEX_DIR}")
    print("   Será criado durante a inicialização")

# Tenta inicializar o sistema
print("\n🔄 Inicializando o sistema...")
try:
    init_success = professor_fernando_local.initialize_system(api_key)
    if init_success:
        print("✅ Sistema inicializado com sucesso!")
    else:
        print("❌ Falha na inicialização.")
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")

# Testa uma pergunta simples
print("\n🔄 Testando pergunta: 'O que é a Segunda Lei de Newton?'")
try:
    start_time = time.time()
    response = get_professor_fernando_local_response("O que é a Segunda Lei de Newton?", api_key)
    elapsed_time = time.time() - start_time
    
    print(f"✅ Resposta recebida em {elapsed_time:.2f} segundos!")
    print("\n----- RESPOSTA -----")
    print(response[:500] + "..." if len(response) > 500 else response)
    print("----- FIM DA RESPOSTA -----\n")
    
    if "Erro" in response or "erro" in response:
        print("⚠️ A resposta contém menção a erros!")
    else:
        print("✅ A resposta não contém erros aparentes")
        
except Exception as e:
    print(f"❌ Erro ao obter resposta: {e}")

# Testa uma pergunta mais complexa
print("\n🔄 Testando pergunta complexa: 'Explique o efeito fotoelétrico e sua importância para a física quântica'")
try:
    start_time = time.time()
    response = get_professor_fernando_local_response("Explique o efeito fotoelétrico e sua importância para a física quântica", api_key)
    elapsed_time = time.time() - start_time
    
    print(f"✅ Resposta recebida em {elapsed_time:.2f} segundos!")
    print("\n----- RESPOSTA -----")
    print(response[:500] + "..." if len(response) > 500 else response)
    print("----- FIM DA RESPOSTA -----\n")
        
except Exception as e:
    print(f"❌ Erro ao obter resposta: {e}")

print("\n�� Teste concluído!") 