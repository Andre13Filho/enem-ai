import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import time

def main():
    """
    Carrega documentos PDF de um diretório, os processa em pedaços (chunks),
    gera embeddings usando um modelo da HuggingFace e cria um índice FAISS
    que é salvo localmente.
    """
    pdf_directory = "Língua Portuguesa/"
    faiss_index_path = "faiss_index_portuguese"
    
    # 1. Carregar os documentos PDF
    print("Iniciando o carregamento dos documentos PDF...")
    start_time = time.time()
    
    pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))
    if not pdf_files:
        print("Nenhum arquivo PDF encontrado no diretório 'cases_sucesso_portuguese/'.")
        return

    print(f"Arquivos PDF encontrados: {pdf_files}")
    
    all_docs = []
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            all_docs.extend(docs)
            print(f"  - Carregado: {os.path.basename(pdf_path)} ({len(docs)} páginas)")
        except Exception as e:
            print(f"Erro ao carregar o arquivo {pdf_path}: {e}")
            
    if not all_docs:
        print("Nenhum documento pode ser carregado. Encerrando.")
        return

    end_time = time.time()
    print(f"Carregamento concluído em {end_time - start_time:.2f} segundos.\n")

    # 2. Dividir os documentos em chunks
    print("Dividindo os documentos em chunks...")
    start_time = time.time()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150
    )
    splits = text_splitter.split_documents(all_docs)
    
    end_time = time.time()
    print(f"Divisão concluída em {end_time - start_time:.2f} segundos. Total de {len(splits)} chunks gerados.\n")

    # 3. Gerar Embeddings
    print("Gerando embeddings com HuggingFace (pode levar vários minutos)...")
    print("Este processo fará o download do modelo na primeira execução.")
    start_time = time.time()
    
    # Usando um modelo popular e eficiente para embeddings em português/multilíngue
    model_name = "sentence-transformers/distiluse-base-multilingual-cased-v1"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    end_time = time.time()
    print(f"Modelo de embeddings carregado em {end_time - start_time:.2f} segundos.\n")

    # 4. Criar e salvar o índice FAISS
    print("Criando e vetorizando o índice FAISS...")
    start_time = time.time()
    
    try:
        # Garante que o diretório de destino exista
        os.makedirs(faiss_index_path, exist_ok=True)
        
        vectorstore = FAISS.from_documents(splits, embeddings)
        vectorstore.save_local(faiss_index_path)
        
        end_time = time.time()
        print(f"Vetorização concluída em {end_time - start_time:.2f} segundos.")
        print(f"Índice FAISS salvo com sucesso em: '{faiss_index_path}'")
        
    except Exception as e:
        print(f"Ocorreu um erro durante a criação do índice FAISS: {e}")

if __name__ == "__main__":
    main() 