"""
Sistema para carregar documentos de URLs externas no Streamlit Cloud
"""

import os
import requests
import streamlit as st
from pathlib import Path
from typing import List, Dict, Optional
import hashlib

class CloudDocumentLoader:
    """Carrega documentos de URLs externas para o Streamlit Cloud"""
    
    def __init__(self, local_folder: str = "./matemática"):
        self.local_folder = local_folder
        self.cache_folder = "./cached_documents"
        
        # URLs dos documentos - SEUS PDFs DO GOOGLE DRIVE
        self.document_urls = {
            "matematica_pdf_1.pdf": {
                "url": "https://drive.google.com/uc?export=download&id=15KNvGd80Uk70-TghEXo4-NKXMh2P01sE",
                "local_name": "matematica_documento_1.pdf"
            },
            "matematica_pdf_2.pdf": {
                "url": "https://drive.google.com/uc?export=download&id=1i9mrr7colqYfcD3_FHx0PQWY_hXWWaeJ", 
                "local_name": "matematica_documento_2.pdf"
            },
            "matematica_pdf_3.pdf": {
                "url": "https://drive.google.com/uc?export=download&id=12feEEALSPVKnjWkQh2rtu4mihoTdzzrY",
                "local_name": "matematica_documento_3.pdf"
            }
        }
    
    def setup_folders(self):
        """Cria pastas necessárias"""
        os.makedirs(self.local_folder, exist_ok=True)
        os.makedirs(self.cache_folder, exist_ok=True)
    
    def download_document(self, doc_key: str) -> bool:
        """Baixa um documento específico"""
        if doc_key not in self.document_urls:
            return False
            
        doc_info = self.document_urls[doc_key]
        url = doc_info["url"]
        local_path = os.path.join(self.local_folder, doc_info["local_name"])
        
        # Se arquivo já existe, não precisa baixar novamente
        if os.path.exists(local_path):
            return True
            
        try:
            st.info(f"📥 Baixando {doc_info['local_name']}...")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            st.success(f"✅ {doc_info['local_name']} baixado com sucesso!")
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao baixar {doc_info['local_name']}: {str(e)}")
            return False
    
    def download_all_documents(self) -> bool:
        """Baixa todos os documentos"""
        self.setup_folders()
        
        success_count = 0
        total_docs = len(self.document_urls)
        
        progress_bar = st.progress(0)
        
        for i, doc_key in enumerate(self.document_urls.keys()):
            if self.download_document(doc_key):
                success_count += 1
            progress_bar.progress((i + 1) / total_docs)
        
        if success_count == total_docs:
            st.success(f"🎉 Todos os {total_docs} documentos foram baixados!")
            return True
        else:
            st.warning(f"⚠️ {success_count}/{total_docs} documentos baixados com sucesso")
            return success_count > 0
    
    def check_documents_available(self) -> Dict[str, bool]:
        """Verifica quais documentos estão disponíveis"""
        status = {}
        
        for doc_key, doc_info in self.document_urls.items():
            local_path = os.path.join(self.local_folder, doc_info["local_name"])
            status[doc_key] = os.path.exists(local_path)
        
        return status
    
    def ensure_documents_loaded(self) -> bool:
        """Garante que os documentos estejam carregados"""
        # Verifica se todos os documentos estão disponíveis
        status = self.check_documents_available()
        
        missing_docs = [key for key, available in status.items() if not available]
        
        if not missing_docs:
            st.success("📚 Todos os documentos já estão disponíveis!")
            return True
        
        st.info(f"📥 Faltam {len(missing_docs)} documentos. Iniciando download...")
        return self.download_all_documents()

# Instância global
cloud_doc_loader = CloudDocumentLoader()


def setup_cloud_documents():
    """Interface para configurar documentos no Streamlit Cloud"""
    st.sidebar.markdown("### 📁 Documentos")
    
    # Verifica status dos documentos
    status = cloud_doc_loader.check_documents_available()
    total_docs = len(status)
    available_docs = sum(status.values())
    
    if available_docs == total_docs:
        st.sidebar.success(f"📚 {available_docs}/{total_docs} documentos disponíveis")
    else:
        st.sidebar.warning(f"⚠️ {available_docs}/{total_docs} documentos disponíveis")
        
        if st.sidebar.button("📥 Baixar Documentos Faltantes"):
            cloud_doc_loader.ensure_documents_loaded()
            st.rerun()
    
    # Mostra detalhes
    with st.sidebar.expander("📄 Detalhes dos Documentos"):
        for doc_key, available in status.items():
            icon = "✅" if available else "❌"
            doc_name = cloud_doc_loader.document_urls[doc_key]["local_name"]
            st.write(f"{icon} {doc_name}")


# INSTRUÇÕES PARA USAR:
"""
1. Hospede seus PDFs em algum lugar público (Google Drive, Dropbox, GitHub LFS, etc.)
2. Substitua as URLs em document_urls acima
3. Adicione setup_cloud_documents() na sua sidebar
4. O sistema baixará automaticamente os PDFs quando necessário
""" 