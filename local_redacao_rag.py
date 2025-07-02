#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema RAG para Correção de Redação - Professora Letícia
Utiliza RAG com base em redações de sucesso e critérios do ENEM.
"""

import os
from pathlib import Path
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.retrievers import create_merger_retriever
from langchain_community.embeddings import HuggingFaceEmbeddings
import tempfile
import PyPDF2

class RedacaoRAG:
    """Sistema RAG para correção de redações."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_redacao_path = Path("faiss_index_redacao/")
        self.success_cases_path = Path("faiss_index_cases_sucesso_redacao/")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        self.redacao_retriever = None
        self.success_cases_retriever = None
        self.combined_retriever = None
        self.rag_chain = None

        self._load_vector_stores()
        self._create_rag_chain()

    def _load_vector_stores(self):
        """Carrega os FAISS indexes do disco."""
        try:
            if not self.base_redacao_path.exists() or not self.success_cases_path.exists():
                st.error("Pastas de índice FAISS não encontradas. Verifique a estrutura do projeto.")
                return

            # Carregar o índice de redação geral
            redacao_vs = FAISS.load_local(str(self.base_redacao_path), self.embeddings, allow_dangerous_deserialization=True)
            self.redacao_retriever = redacao_vs.as_retriever(search_kwargs={"k": 5})

            # Carregar o índice de casos de sucesso
            success_vs = FAISS.load_local(str(self.success_cases_path), self.embeddings, allow_dangerous_deserialization=True)
            self.success_cases_retriever = success_vs.as_retriever(search_kwargs={"k": 5})

            # Combina os retrievers
            self.combined_retriever = create_merger_retriever(
                [self.redacao_retriever, self.success_cases_retriever]
            )
            st.info("✅ Índices de redação carregados com sucesso!")

        except Exception as e:
            st.error(f"❌ Erro ao carregar os FAISS indexes: {e}")
            print(f"Erro detalhado ao carregar FAISS: {e}")

    def _create_rag_chain(self):
        """Cria a RAG chain com um prompt detalhado para correção."""
        if not self.combined_retriever:
            return

        try:
            llm = ChatGroq(api_key=self.api_key, model_name="llama3-70b-8192", temperature=0.2)
            
            system_prompt = """
            Você é a Professora Letícia, uma especialista em correção de redações do ENEM. Sua tarefa é analisar a redação de um aluno, fornecer uma análise detalhada e uma nota estimada, baseando-se nos critérios do ENEM e em exemplos de redações nota 1000.

            **Contexto Fornecido:**
            - Critérios de avaliação do ENEM e técnicas de escrita (contexto 1).
            - Exemplos de redações que alcançaram a nota 1000 (contexto 2).

            **Sua Resposta Deve Incluir:**

            1.  **Nota Estimada (de 0 a 1000):** Apresente uma nota geral baseada nas 5 competências do ENEM.

            2.  **Análise por Competência (200 pontos cada):**
                *   **C1: Domínio da norma culta:** Avalie a gramática, ortografia, pontuação e sintaxe.
                *   **C2: Compreensão do tema e estrutura dissertativa-argumentativa:** Verifique se o texto atende ao tema, usa repertório sociocultural e segue a estrutura de introdução, desenvolvimento e conclusão.
                *   **C3: Seleção e organização de informações:** Analise a coerência, a coesão e a progressão das ideias.
                *   **C4: Conhecimento dos mecanismos linguísticos:** Avalie o uso de conectivos e a articulação entre parágrafos e frases.
                *   **C5: Proposta de intervenção:** Verifique se a proposta é completa (agente, ação, meio/modo, finalidade, detalhamento), concreta e relacionada à discussão.

            3.  **Pontos Fortes:** Elogie os acertos do aluno, como bons argumentos, uso correto de repertório ou uma proposta de intervenção bem estruturada.

            4.  **Pontos a Melhorar:** Aponte de forma construtiva os desvios e as áreas que precisam de mais atenção, explicando o porquê.

            5.  **Sugestões para Nota 1000:** Dê conselhos práticos e direcionados para que o aluno possa evoluir e alcançar a nota máxima na próxima redação.

            **Formato da Resposta:**
            Use Markdown para estruturar sua resposta. Seja didática, encorajadora e precisa.

            ---
            **INICIE A ANÁLISE ABAIXO:**
            """

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "Por favor, analise esta redação:\n\n{input}"),
                ]
            )

            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            self.rag_chain = create_retrieval_chain(self.combined_retriever, question_answer_chain)
            
        except Exception as e:
            st.error(f"❌ Erro ao criar a RAG chain: {e}")
            print(f"Erro detalhado ao criar RAG chain: {e}")

    def get_correction(self, essay_text: str) -> str:
        """Gera a correção da redação usando a RAG chain."""
        if not self.rag_chain:
            return "❌ A cadeia de correção não foi inicializada. Verifique os erros anteriores."
        
        try:
            with st.spinner("A Professora Letícia está corrigindo sua redação... ✍️"):
                response = self.rag_chain.invoke({"input": essay_text})
                return response.get("answer", "Não foi possível gerar a correção.")
        except Exception as e:
            st.error(f"❌ Erro durante a correção: {e}")
            return f"Erro ao gerar a correção: {e}"

    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> str:
        """Extrai texto de um conteúdo de PDF em bytes."""
        text = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name

            with open(temp_file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\\n"
            
            os.remove(temp_file_path)
            return text.strip() if text.strip() else "Não foi possível extrair texto do PDF. O arquivo pode conter apenas imagens."

        except Exception as e:
            print(f"Erro ao extrair texto do PDF: {e}")
            return "Erro ao processar o arquivo PDF."

# Função para ser chamada pela UI do Streamlit
def get_redacao_correction(essay_text: str, api_key: str) -> str:
    """Função de alto nível para obter a correção de uma redação."""
    if not api_key:
        return "🔑 A chave da API Groq não foi configurada."
    
    try:
        corrector = RedacaoRAG(api_key=api_key)
        correction = corrector.get_correction(essay_text)
        return correction
    except Exception as e:
        return f"❌ Ocorreu um erro geral no processo de correção: {e}"

def setup_redacao_ui():
    """
    Função de placeholder para compatibilidade com app.py.
    A UI de redação agora é gerenciada dentro de 'professor_leticia_local.py'.
    """
    pass

def analyze_redacao_pdf(pdf_content: bytes, filename: str) -> str:
    """
    Função de placeholder para compatibilidade com app.py.
    A análise agora é chamada diretamente pela UI da Professora Letícia.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "🔑 Chave da API Groq não encontrada."
        
    text = RedacaoRAG.extract_text_from_pdf(pdf_content)
    if "não foi possível extrair" in text.lower() or not text.strip():
        return f"❌ Erro ao ler o arquivo: {text}"
    
    return get_redacao_correction(text, api_key) 