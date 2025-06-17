"""
Teste para verificar se o sistema de download do Google Drive está funcionando
"""

import requests
import streamlit as st
from cloud_documents import cloud_doc_loader

def test_google_drive_download():
    """Testa o download de um documento do Google Drive"""
    print("🔧 Testando sistema de download do Google Drive...")
    
    # Testa o primeiro documento
    doc_info = cloud_doc_loader.document_urls["matematica_pdf_1.pdf"]
    url = doc_info["url"]
    
    print(f"📥 Testando download de: {doc_info['local_name']}")
    print(f"🔗 URL: {url}")
    
    try:
        # Faz uma requisição HEAD para verificar se o arquivo existe
        response = requests.head(url, allow_redirects=True)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            # Verifica o tamanho do arquivo
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                print(f"📏 Tamanho: {size_mb:.1f} MB")
            
            print("✅ Arquivo acessível!")
            return True
        else:
            print("❌ Arquivo não acessível")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

def test_all_documents():
    """Testa todos os documentos"""
    print("\n🔍 Testando todos os documentos...")
    
    results = {}
    for doc_key, doc_info in cloud_doc_loader.document_urls.items():
        url = doc_info["url"]
        
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            success = response.status_code == 200
            results[doc_key] = success
            status = "✅" if success else "❌"
            print(f"{status} {doc_key}: {response.status_code}")
            
        except Exception as e:
            results[doc_key] = False
            print(f"❌ {doc_key}: {str(e)}")
    
    # Resumo
    successful = sum(results.values())
    total = len(results)
    print(f"\n📊 Resultado: {successful}/{total} documentos acessíveis")
    
    return results

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de download...")
    
    # Teste básico
    test_google_drive_download()
    
    # Teste completo
    results = test_all_documents()
    
    if all(results.values()):
        print("\n🎉 Todos os documentos estão acessíveis!")
    else:
        print("\n⚠️ Alguns documentos podem não estar acessíveis.")
        print("💡 Verifique se os arquivos no Google Drive estão com permissão pública.") 