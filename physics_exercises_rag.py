#!/usr/bin/env python3
"""
Sistema RAG para Exercícios de Física do ENEM
Professor Fernando - ENEM AI Helper

Baseado no sistema de exercícios de matemática, adaptado para física
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PhysicsExercisesRAG:
    """Sistema RAG para exercícios de física do ENEM"""
    
    def __init__(self, exercises_folder: str = "./Segundo dia"):
        self.exercises_folder = exercises_folder
        self.persist_directory = "./chroma_physics_exercises_db"
        self.documents = []
        self.vectorstore = None
        self.retriever = None
        self.embeddings = None
        self.exercises_data = []
        
        # Configura embeddings
        self._setup_embeddings()
        
        # Carrega exercícios
        self._load_physics_exercises()
        
        # Tenta carregar vectorstore existente
        if not self.load_existing_vectorstore():
            if self.exercises_data:
                self._create_vectorstore()

    def _setup_embeddings(self):
        """Configura embeddings multilíngues"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            if 'st' in globals():
                st.error(f"Erro ao configurar embeddings para exercícios de física: {str(e)}")
            else:
                print(f"Erro ao configurar embeddings para exercícios de física: {str(e)}")
            self.embeddings = None

    def _load_physics_exercises(self):
        """Carrega exercícios de física do ENEM"""
        try:
            if not os.path.exists(self.exercises_folder):
                print(f"⚠️ Pasta de exercícios não encontrada: {self.exercises_folder}")
                self._create_sample_physics_exercises()
                return

            # Busca arquivos JSON com exercícios de física
            json_files = []
            for root, dirs, files in os.walk(self.exercises_folder):
                for file in files:
                    if file.endswith('.json'):
                        json_files.append(os.path.join(root, file))

            if not json_files:
                print("⚠️ Nenhum arquivo JSON encontrado, criando exercícios de amostra")
                self._create_sample_physics_exercises()
                return

            # Carrega exercícios dos arquivos JSON
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Extrai exercícios (adapta para diferentes formatos)
                        if isinstance(data, list):
                            exercises = data
                        elif isinstance(data, dict):
                            exercises = data.get('questoes', data.get('exercises', data.get('questions', [])))
                        else:
                            continue
                        
                        # Filtra exercícios de física/ciências da natureza
                        physics_exercises = []
                        for ex in exercises:
                            if self._is_physics_exercise(ex):
                                physics_exercises.append(ex)
                        
                        self.exercises_data.extend(physics_exercises)
                        
                except Exception as e:
                    print(f"Erro ao carregar {json_file}: {e}")
                    continue

            if not self.exercises_data:
                print("⚠️ Nenhum exercício de física encontrado, criando exercícios de amostra")
                self._create_sample_physics_exercises()
            else:
                print(f"✅ Carregados {len(self.exercises_data)} exercícios de física")

        except Exception as e:
            print(f"Erro ao carregar exercícios de física: {e}")
            self._create_sample_physics_exercises()

    def _is_physics_exercise(self, exercise: Dict) -> bool:
        """Verifica se um exercício é de física"""
        
        # Palavras-chave de física
        physics_keywords = [
            'força', 'energia', 'movimento', 'velocidade', 'aceleração',
            'massa', 'newton', 'joule', 'watt', 'volt', 'ampere',
            'campo elétrico', 'campo magnético', 'onda', 'som', 'luz',
            'calor', 'temperatura', 'pressão', 'densidade', 'volume',
            'mecânica', 'cinemática', 'dinâmica', 'termodinâmica',
            'eletromagnetismo', 'óptica', 'ondulatória', 'física moderna',
            'átomo', 'elétron', 'próton', 'radioatividade', 'relatividade',
            'resistência', 'corrente', 'tensão', 'circuito', 'capacitor',
            'indução', 'transformador', 'motor', 'gerador', 'potência',
            'trabalho', 'gravitação', 'orbital', 'satélite', 'planeta'
        ]
        
        # Verifica no enunciado
        text_content = ""
        if isinstance(exercise, dict):
            text_content += exercise.get('enunciado', '') + ' '
            text_content += exercise.get('question', '') + ' '
            text_content += exercise.get('texto', '') + ' '
            
            # Verifica nas alternativas
            alternatives = exercise.get('alternativas', exercise.get('alternatives', exercise.get('opcoes', [])))
            for alt in alternatives:
                if isinstance(alt, dict):
                    text_content += alt.get('texto', '') + ' '
                elif isinstance(alt, str):
                    text_content += alt + ' '
        
        text_content = text_content.lower()
        
        # Conta palavras-chave de física
        physics_count = sum(1 for keyword in physics_keywords if keyword in text_content)
        
        # Verifica se tem pelo menos 2 palavras-chave de física
        return physics_count >= 2

    def _create_sample_physics_exercises(self):
        """Cria exercícios de amostra de física"""
        
        sample_exercises = [
            {
                "id": "physics_001",
                "ano": "2024",
                "prova": "2º dia",
                "area": "Ciências da Natureza",
                "disciplina": "Física",
                "assunto": "Mecânica - Cinemática",
                "enunciado": "Um carro parte do repouso e acelera uniformemente até atingir 72 km/h em 10 segundos. Qual é a aceleração do carro?",
                "alternativas": [
                    {"letra": "A", "texto": "1,0 m/s²"},
                    {"letra": "B", "texto": "2,0 m/s²"},
                    {"letra": "C", "texto": "3,6 m/s²"},
                    {"letra": "D", "texto": "7,2 m/s²"},
                    {"letra": "E", "texto": "20 m/s²"}
                ],
                "resposta_correta": "B",
                "explicacao": "Convertendo 72 km/h para m/s: 72/3,6 = 20 m/s. Usando a = Δv/Δt: a = (20-0)/10 = 2,0 m/s²"
            },
            {
                "id": "physics_002",
                "ano": "2024",
                "prova": "2º dia",
                "area": "Ciências da Natureza",
                "disciplina": "Física",
                "assunto": "Mecânica - Dinâmica",
                "enunciado": "Uma força de 50 N é aplicada sobre um corpo de massa 10 kg, inicialmente em repouso, sobre uma superfície horizontal sem atrito. Qual é a aceleração do corpo?",
                "alternativas": [
                    {"letra": "A", "texto": "0,2 m/s²"},
                    {"letra": "B", "texto": "2,0 m/s²"},
                    {"letra": "C", "texto": "5,0 m/s²"},
                    {"letra": "D", "texto": "40 m/s²"},
                    {"letra": "E", "texto": "500 m/s²"}
                ],
                "resposta_correta": "C",
                "explicacao": "Pela Segunda Lei de Newton: F = ma. Logo: a = F/m = 50/10 = 5,0 m/s²"
            },
            {
                "id": "physics_003",
                "ano": "2024",
                "prova": "2º dia",
                "area": "Ciências da Natureza",
                "disciplina": "Física",
                "assunto": "Energia - Trabalho e Energia Cinética",
                "enunciado": "Um objeto de massa 2 kg está se movendo com velocidade de 10 m/s. Qual é sua energia cinética?",
                "alternativas": [
                    {"letra": "A", "texto": "10 J"},
                    {"letra": "B", "texto": "20 J"},
                    {"letra": "C", "texto": "50 J"},
                    {"letra": "D", "texto": "100 J"},
                    {"letra": "E", "texto": "200 J"}
                ],
                "resposta_correta": "D",
                "explicacao": "Energia cinética: Ec = mv²/2 = (2 × 10²)/2 = (2 × 100)/2 = 100 J"
            },
            {
                "id": "physics_004",
                "ano": "2024",
                "prova": "2º dia",
                "area": "Ciências da Natureza",
                "disciplina": "Física",
                "assunto": "Eletricidade - Lei de Ohm",
                "enunciado": "Um resistor de 20 Ω é percorrido por uma corrente de 3 A. Qual é a tensão aplicada sobre o resistor?",
                "alternativas": [
                    {"letra": "A", "texto": "6,7 V"},
                    {"letra": "B", "texto": "17 V"},
                    {"letra": "C", "texto": "23 V"},
                    {"letra": "D", "texto": "60 V"},
                    {"letra": "E", "texto": "180 V"}
                ],
                "resposta_correta": "D",
                "explicacao": "Pela Lei de Ohm: V = R × I = 20 × 3 = 60 V"
            },
            {
                "id": "physics_005",
                "ano": "2024",
                "prova": "2º dia",
                "area": "Ciências da Natureza",
                "disciplina": "Física",
                "assunto": "Ondas - Velocidade de Propagação",
                "enunciado": "Uma onda sonora se propaga no ar com frequência de 440 Hz e comprimento de onda de 0,75 m. Qual é a velocidade de propagação do som?",
                "alternativas": [
                    {"letra": "A", "texto": "293 m/s"},
                    {"letra": "B", "texto": "330 m/s"},
                    {"letra": "C", "texto": "440 m/s"},
                    {"letra": "D", "texto": "587 m/s"},
                    {"letra": "E", "texto": "750 m/s"}
                ],
                "resposta_correta": "B",
                "explicacao": "Velocidade da onda: v = f × λ = 440 × 0,75 = 330 m/s"
            }
        ]
        
        self.exercises_data = sample_exercises
        print(f"✅ Criados {len(sample_exercises)} exercícios de amostra de física")

    def _create_vectorstore(self):
        """Cria vectorstore a partir dos exercícios"""
        try:
            if not self.embeddings or not self.exercises_data:
                return False

            # Converte exercícios em documentos
            documents = []
            for i, exercise in enumerate(self.exercises_data):
                
                # Constrói texto completo do exercício
                full_text = f"Assunto: {exercise.get('assunto', 'N/A')}\n\n"
                full_text += f"Enunciado: {exercise.get('enunciado', '')}\n\n"
                
                # Adiciona alternativas
                alternatives = exercise.get('alternativas', [])
                if alternatives:
                    full_text += "Alternativas:\n"
                    for alt in alternatives:
                        if isinstance(alt, dict):
                            full_text += f"{alt.get('letra', '')}) {alt.get('texto', '')}\n"
                
                # Adiciona explicação se disponível
                if exercise.get('explicacao'):
                    full_text += f"\nExplicação: {exercise.get('explicacao')}"

                # Cria documento
                doc = Document(
                    page_content=full_text,
                    metadata={
                        "exercise_id": exercise.get('id', f'ex_{i}'),
                        "ano": exercise.get('ano', 'N/A'),
                        "disciplina": "Física",
                        "assunto": exercise.get('assunto', 'N/A'),
                        "resposta_correta": exercise.get('resposta_correta', 'N/A'),
                        "type": "physics_exercise"
                    }
                )
                documents.append(doc)

            # Cria vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )

            # Configura retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )

            self.documents = documents
            print(f"✅ VectorStore de exercícios de física criada com {len(documents)} exercícios")
            return True

        except Exception as e:
            print(f"Erro ao criar vectorstore de exercícios de física: {e}")
            return False

    def load_existing_vectorstore(self) -> bool:
        """Carrega vectorstore existente"""
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
                
                # Testa vectorstore
                try:
                    test_docs = self.retriever.invoke("física")
                    print(f"✅ VectorStore de exercícios de física carregada com {len(test_docs)} docs de teste")
                    
                    sample_docs = self.vectorstore.similarity_search("força energia", k=50)
                    print(f"📊 Amostra de exercícios de física: {len(sample_docs)} questões")
                    
                    return True
                except Exception as e:
                    print(f"⚠️ Erro no teste da VectorStore de exercícios de física: {e}")
                
        except Exception as e:
            print(f"Erro ao carregar vectorstore de exercícios de física: {e}")
        
        return False

    def search_exercises(self, query: str, k: int = 5) -> List[Dict]:
        """Busca exercícios relevantes"""
        try:
            if not self.retriever:
                return []
            
            docs = self.retriever.invoke(query)[:k]
            
            # Converte documentos de volta para exercícios
            exercises = []
            for doc in docs:
                exercise_id = doc.metadata.get('exercise_id')
                
                # Busca exercício original
                original_exercise = None
                for ex in self.exercises_data:
                    if ex.get('id') == exercise_id:
                        original_exercise = ex
                        break
                
                if original_exercise:
                    exercises.append(original_exercise)
                else:
                    # Cria exercício a partir do documento
                    exercises.append({
                        'id': exercise_id,
                        'assunto': doc.metadata.get('assunto', 'N/A'),
                        'content': doc.page_content,
                        'metadata': doc.metadata
                    })
            
            return exercises
            
        except Exception as e:
            print(f"Erro na busca de exercícios de física: {e}")
            return []

    def get_random_exercises(self, count: int = 3) -> List[Dict]:
        """Retorna exercícios aleatórios"""
        import random
        
        if not self.exercises_data:
            return []
        
        return random.sample(
            self.exercises_data, 
            min(count, len(self.exercises_data))
        )

    def get_exercises_by_topic(self, topic: str) -> List[Dict]:
        """Busca exercícios por tópico específico"""
        return self.search_exercises(f"assunto {topic} física", k=10)

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos exercícios"""
        if not self.exercises_data:
            return {"total": 0, "topics": [], "years": []}
        
        topics = set()
        years = set()
        
        for ex in self.exercises_data:
            if ex.get('assunto'):
                topics.add(ex['assunto'])
            if ex.get('ano'):
                years.add(ex['ano'])
        
        return {
            "total": len(self.exercises_data),
            "topics": sorted(list(topics)),
            "years": sorted(list(years)),
            "vectorstore_active": self.vectorstore is not None
        }

# Instância global
physics_exercises_rag = PhysicsExercisesRAG() 