#!/usr/bin/env python3
"""
Sistema RAG para Exercícios do ENEM - Segundo Dia
Processa e indexa exercícios de matemática e ciências da natureza do ENEM
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import streamlit as st

# Document processing
from pypdf import PdfReader
from docx import Document as DocxDocument

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

class ENEMExercisesRAG:
    """Sistema RAG para exercícios do ENEM"""
    
    def __init__(self, enem_folder_path: str = "./Segundo dia"):
        self.enem_folder_path = Path(enem_folder_path)
        self.persist_directory = "./chroma_enem_exercises"
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.documents = []
        
        # Configurar embeddings
        self._setup_embeddings()
    
    def _setup_embeddings(self):
        """Configura embeddings HuggingFace"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            if 'st' in globals():
                st.error(f"Erro ao configurar embeddings: {str(e)}")
            else:
                print(f"Erro ao configurar embeddings: {str(e)}")
    
    def process_enem_documents(self) -> bool:
        """Processa todos os documentos do ENEM"""
        if not self.enem_folder_path.exists():
            st.error(f"Pasta do ENEM não encontrada: {self.enem_folder_path}")
            return False
        
        try:
            print("🎯 Processando exercícios do ENEM...")
            
            # Busca todos os anos
            year_folders = [f for f in self.enem_folder_path.iterdir() if f.is_dir()]
            year_folders.sort(key=lambda x: x.name, reverse=True)  # Mais recentes primeiro
            
            processed_files = 0
            total_exercises = 0
            
            for year_folder in year_folders:
                year = year_folder.name
                print(f"📅 Processando ano {year}...")
                
                # Busca arquivos PDF de prova (não gabarito)
                pdf_files = [f for f in year_folder.glob("*.pdf") if "gabarito" not in f.name.lower() and "gb" not in f.name.lower()]
                
                for pdf_file in pdf_files:
                    print(f"   📄 Processando: {pdf_file.name}")
                    
                    # Extrai exercícios do PDF
                    exercises = self._extract_exercises_from_pdf(pdf_file, year)
                    
                    if exercises:
                        self.documents.extend(exercises)
                        total_exercises += len(exercises)
                        processed_files += 1
                        print(f"   ✅ {len(exercises)} exercícios extraídos")
                    else:
                        print(f"   ⚠️ Nenhum exercício encontrado")
            
            print(f"\n📊 Processamento concluído:")
            print(f"   📁 {processed_files} arquivos processados")
            print(f"   🎯 {total_exercises} exercícios extraídos")
            
            if self.documents:
                # Cria vectorstore
                self._create_vectorstore()
                return True
            else:
                st.warning("Nenhum exercício foi extraído dos documentos")
                return False
                
        except Exception as e:
            st.error(f"Erro ao processar documentos do ENEM: {str(e)}")
            return False
    
    def _extract_exercises_from_pdf(self, pdf_path: Path, year: str) -> List[Document]:
        """Extrai exercícios individuais de um PDF do ENEM"""
        try:
            reader = PdfReader(str(pdf_path))
            full_text = ""
            
            # Extrai todo o texto do PDF
            for page in reader.pages:
                text = page.extract_text()
                if text.strip():
                    full_text += text + "\n"
            
            # Identifica exercícios por padrões
            exercises = self._parse_exercises_from_text(full_text, year, pdf_path.name)
            
            return exercises
            
        except Exception as e:
            print(f"Erro ao processar PDF {pdf_path}: {e}")
            return []
    
    def _parse_exercises_from_text(self, text: str, year: str, filename: str) -> List[Document]:
        """Identifica e separa exercícios individuais do texto"""
        exercises = []
        
        # Padrões para identificar questões do ENEM
        # O ENEM geralmente usa "QUESTÃO XX" ou números simples
        patterns = [
            r'QUESTÃO\s+(\d+)',  # QUESTÃO 136
            r'(?:^|\n)(\d+)\s*\.?\s*(?:[A-Z]|\()',  # 136. ou 136 seguido de texto
            r'(?:^|\n)(\d+)\s*(?=\w)',  # Número seguido de palavra
        ]
        
        # Tenta diferentes padrões para identificar questões
        question_matches = []
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE))
            if matches and len(matches) > 10:  # Se encontrou muitas questões, usa esse padrão
                question_matches = matches
                break
        
        if not question_matches:
            # Se não encontrou padrão claro, divide por páginas/seções
            return self._split_by_chunks(text, year, filename)
        
        # Extrai questões individuais
        for i, match in enumerate(question_matches):
            question_num = match.group(1)
            start_pos = match.start()
            
            # Determina onde termina a questão (início da próxima ou fim do texto)
            if i + 1 < len(question_matches):
                end_pos = question_matches[i + 1].start()
            else:
                end_pos = len(text)
            
            question_text = text[start_pos:end_pos].strip()
            
            # Filtra questões muito curtas ou muito longas
            if 100 < len(question_text) < 3000:
                # Identifica área (matemática ou ciências)
                area = self._identify_subject_area(question_text)
                
                # Cria documento para a questão
                doc = Document(
                    page_content=question_text,
                    metadata={
                        "year": year,
                        "question_number": question_num,
                        "source_file": filename,
                        "subject_area": area,
                        "document_type": "exercise",
                        "topic": self._extract_topic_from_exercise(question_text)
                    }
                )
                exercises.append(doc)
        
        return exercises
    
    def _split_by_chunks(self, text: str, year: str, filename: str) -> List[Document]:
        """Divide texto em chunks quando não consegue identificar questões individuais"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        documents = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 100:  # Filtra chunks muito pequenos
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "year": year,
                        "chunk_number": i + 1,
                        "source_file": filename,
                        "subject_area": self._identify_subject_area(chunk),
                        "document_type": "exercise_chunk",
                        "topic": self._extract_topic_from_exercise(chunk)
                    }
                )
                documents.append(doc)
        
        return documents
    
    def _identify_subject_area(self, text: str) -> str:
        """Identifica se é matemática ou ciências da natureza"""
        text_lower = text.lower()
        
        # Palavras-chave para matemática
        math_keywords = [
            'função', 'equação', 'gráfico', 'geometria', 'trigonometria',
            'logaritmo', 'progressão', 'probabilidade', 'estatística',
            'derivada', 'integral', 'matriz', 'determinante', 'sistema',
            'polinômio', 'raiz', 'vértice', 'parábola', 'circunferência'
        ]
        
        # Palavras-chave para ciências
        science_keywords = [
            'física', 'química', 'biologia', 'célula', 'átomo', 'molécula',
            'força', 'energia', 'velocidade', 'aceleração', 'movimento',
            'reação', 'elemento', 'organismo', 'genética', 'evolução',
            'ecologia', 'termodinâmica', 'eletricidade', 'magnetismo'
        ]
        
        math_score = sum(1 for keyword in math_keywords if keyword in text_lower)
        science_score = sum(1 for keyword in science_keywords if keyword in text_lower)
        
        if math_score > science_score:
            return "Matemática"
        elif science_score > math_score:
            return "Ciências da Natureza"
        else:
            return "Indeterminado"
    
    def _extract_topic_from_exercise(self, text: str) -> str:
        """Extrai tópico específico do exercício"""
        text_lower = text.lower()
        
        # Tópicos específicos de matemática
        topics = {
            "Função Quadrática": ["função quadrática", "parábola", "vértice", "ax² + bx + c"],
            "Geometria": ["triângulo", "círculo", "área", "volume", "perímetro", "raio"],
            "Trigonometria": ["seno", "cosseno", "tangente", "trigonométric"],
            "Probabilidade": ["probabilidade", "chance", "evento", "aleatório"],
            "Estatística": ["média", "mediana", "moda", "desvio", "gráfico"],
            "Progressão": ["progressão", "aritmética", "geométrica", "sequência"],
            "Logaritmo": ["logaritmo", "log", "exponencial"],
            "Física": ["força", "energia", "velocidade", "movimento", "newton"],
            "Química": ["reação", "mol", "átomo", "elemento", "química"],
            "Biologia": ["célula", "dna", "gene", "evolução", "ecologia"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return "Geral"
    
    def _create_vectorstore(self):
        """Cria vectorstore ChromaDB"""
        try:
            if not self.embeddings:
                raise Exception("Embeddings não configurados")
            
            # Cria vectorstore ChromaDB
            self.vectorstore = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # Configura retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            print(f"✅ VectorStore criada com {len(self.documents)} exercícios")
            
        except Exception as e:
            st.error(f"Erro ao criar vectorstore: {str(e)}")
            raise
    
    def load_existing_vectorstore(self) -> bool:
        """Carrega vectorstore existente se disponível"""
        try:
            if os.path.exists(self.persist_directory) and self.embeddings:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                
                self.retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
                
                # Testa se a vectorstore tem conteúdo
                try:
                    test_docs = self.retriever.invoke("matemática")
                    print(f"✅ VectorStore de exercícios carregada com {len(test_docs)} docs de teste")
                    
                    # Carrega amostra para estatísticas
                    sample_docs = self.vectorstore.similarity_search("questão", k=50)
                    self.documents = sample_docs
                    print(f"📊 Amostra de exercícios: {len(sample_docs)} questões")
                    
                except Exception as e:
                    print(f"⚠️ Erro no teste da VectorStore de exercícios: {e}")
                
                return True
        except Exception as e:
            print(f"Não foi possível carregar vectorstore de exercícios: {str(e)}")
        
        return False
    
    def search_exercises_by_topic(self, topic: str, subject_area: str = None, k: int = 3) -> List[Document]:
        """Busca exercícios por tópico e área"""
        if not self.retriever:
            return []
        
        try:
            # Constrói query
            query = topic
            if subject_area:
                query += f" {subject_area}"
            
            # Busca documentos relevantes
            docs = self.retriever.invoke(query)
            
            # Filtra por área se especificada
            if subject_area:
                filtered_docs = []
                for doc in docs:
                    doc_area = doc.metadata.get("subject_area", "").lower()
                    if subject_area.lower() in doc_area or doc_area in subject_area.lower():
                        filtered_docs.append(doc)
                docs = filtered_docs
            
            return docs[:k]
            
        except Exception as e:
            print(f"Erro na busca de exercícios: {str(e)}")
            return []
    
    def get_exercises_by_year(self, year: str, k: int = 5) -> List[Document]:
        """Busca exercícios de um ano específico"""
        if not self.vectorstore:
            return []
        
        try:
            # Busca por ano nos metadados
            docs = self.vectorstore.similarity_search(
                "questão exercício",
                k=k*3,  # Busca mais para filtrar por ano
                filter={"year": year}
            )
            
            return docs[:k]
            
        except Exception as e:
            print(f"Erro na busca por ano: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos exercícios"""
        stats = {
            "total_exercises": len(self.documents),
            "vectorstore_initialized": self.vectorstore is not None,
            "retriever_configured": self.retriever is not None,
            "enem_folder": str(self.enem_folder_path),
            "persistence_directory": self.persist_directory
        }
        
        # Conta anos disponíveis
        years = set()
        areas = set()
        topics = set()
        
        for doc in self.documents:
            year = doc.metadata.get("year", "Desconhecido")
            area = doc.metadata.get("subject_area", "Desconhecido")
            topic = doc.metadata.get("topic", "Desconhecido")
            
            years.add(year)
            areas.add(area)
            topics.add(topic)
        
        stats["available_years"] = sorted(list(years), reverse=True)
        stats["subject_areas"] = sorted(list(areas))
        stats["topics"] = sorted(list(topics))
        
        return stats

# Instância global
enem_exercises_rag = ENEMExercisesRAG() 