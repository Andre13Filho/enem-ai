#!/usr/bin/env python3
"""
Sistema RAG Melhorado para Exercícios do ENEM
Integra o parser avançado com estruturação JSON robusta
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import streamlit as st

# Document processing
from pypdf import PdfReader

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Import do parser melhorado
from improved_exercise_parser import ImprovedExerciseParser, ExerciseQuestion, Alternative

class ImprovedENEMRAG:
    """Sistema RAG melhorado para exercícios do ENEM com parsing estruturado"""
    
    def __init__(self, enem_folder_path: str = "./Segundo dia"):
        self.enem_folder_path = Path(enem_folder_path)
        self.persist_directory = "./chroma_enem_exercises_improved"
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.structured_exercises = []  # Lista de ExerciseQuestion
        self.parser = ImprovedExerciseParser()
        
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
        """Processa todos os documentos do ENEM com parsing melhorado"""
        if not self.enem_folder_path.exists():
            st.error(f"Pasta do ENEM não encontrada: {self.enem_folder_path}")
            return False
        
        try:
            print("🎯 Processando exercícios do ENEM com parser melhorado...")
            
            # Busca todos os anos
            year_folders = [f for f in self.enem_folder_path.iterdir() if f.is_dir()]
            year_folders.sort(key=lambda x: x.name, reverse=True)
            
            processed_files = 0
            total_exercises = 0
            
            for year_folder in year_folders:
                year = year_folder.name
                print(f"📅 Processando ano {year}...")
                
                # Busca arquivos PDF de prova
                pdf_files = [f for f in year_folder.glob("*.pdf") 
                           if "gabarito" not in f.name.lower() and "gb" not in f.name.lower()]
                
                for pdf_file in pdf_files:
                    print(f"   📄 Processando: {pdf_file.name}")
                    
                    # Extrai exercícios usando parser melhorado
                    exercises = self._extract_structured_exercises(pdf_file, year)
                    
                    if exercises:
                        self.structured_exercises.extend(exercises)
                        total_exercises += len(exercises)
                        processed_files += 1
                        print(f"   ✅ {len(exercises)} exercícios estruturados extraídos")
                    else:
                        print(f"   ⚠️ Nenhum exercício encontrado")
            
            print(f"\n📊 Processamento concluído:")
            print(f"   📁 {processed_files} arquivos processados")
            print(f"   🎯 {total_exercises} exercícios estruturados extraídos")
            
            if self.structured_exercises:
                # Cria vectorstore com dados estruturados
                self._create_improved_vectorstore()
                # Salva cache JSON dos exercícios estruturados
                self._save_exercises_cache()
                return True
            else:
                st.warning("Nenhum exercício foi extraído dos documentos")
                return False
                
        except Exception as e:
            st.error(f"Erro ao processar documentos do ENEM: {str(e)}")
            return False
    
    def _extract_structured_exercises(self, pdf_path: Path, year: str) -> List[ExerciseQuestion]:
        """Extrai exercícios estruturados usando o parser melhorado"""
        try:
            reader = PdfReader(str(pdf_path))
            full_text = ""
            
            # Extrai todo o texto do PDF
            for page in reader.pages:
                text = page.extract_text()
                if text.strip():
                    full_text += text + "\n"
            
            # Usa parser melhorado para extrair exercícios estruturados
            exercises = self.parser.parse_pdf_text_to_exercises(
                full_text, year, pdf_path.name
            )
            
            return exercises
            
        except Exception as e:
            print(f"Erro ao processar PDF {pdf_path}: {e}")
            return []

# Instância global para uso no app
improved_enem_rag = ImprovedENEMRAG()
