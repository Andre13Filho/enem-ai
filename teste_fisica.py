#!/usr/bin/env python3
"""
Script de teste para o professor de física
"""

import os
import sys
from dotenv import load_dotenv
import time

# Carrega variáveis de ambiente (API_KEY)
load_dotenv()

# Configuração básica
print("📋 Teste do Professor Fernando (Física)")
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

# Tenta inicializar o sistema
print("\n🔄 Inicializando o sistema...")
try:
    init_success = professor_fernando_local.initialize_system(api_key)
    if init_success:
        print("✅ Sistema inicializado com sucesso!")
    else:
        print("❌ Falha na inicialização. Pulando para o teste com resposta de fallback...")
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")
    print("⚠️ Pulando para o teste com resposta de fallback...")

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

print("\n📋 Teste concluído!") 