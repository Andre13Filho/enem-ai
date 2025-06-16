#!/usr/bin/env python3
"""
Sistema Integrado do ENEM - Combina Extração Avançada de PDF + Parser Melhorado
Versão final que resolve completamente os problemas de alternativas bagunçadas
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
import streamlit as st

# Imports dos sistemas desenvolvidos
from advanced_pdf_extractor import AdvancedPDFExtractor, extract_pdf_advanced
from improved_exercise_parser import ImprovedExerciseParser, ExerciseQuestion
from improved_exercise_display import ImprovedExerciseDisplay, display_exercises_list

# LangChain para vectorstore
from langchain.schema import Document
from langchain_chroma import Chroma
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

class IntegratedENEMSystem:
    """
    Sistema integrado que combina:
    1. Extração avançada de PDF (PyMuPDF + OCR)
    2. Parser melhorado com estruturação JSON
    3. RAG otimizado
    4. Interface moderna
    """
    
    def __init__(self, enem_folder_path: str = "./Segundo dia"):
        self.enem_folder_path = Path(enem_folder_path)
        self.persist_directory = "./chroma_enem_integrated"
        
        # Componentes do sistema
        self.pdf_extractor = AdvancedPDFExtractor()
        self.exercise_parser = ImprovedExerciseParser()
        self.exercise_display = ImprovedExerciseDisplay()
        
        # Configurações RAG
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        
        # Cache de exercícios processados
        self.structured_exercises = []
        self.processing_stats = {}
        
        self._setup_embeddings()
    
    def _setup_embeddings(self):
        """Configura embeddings para RAG"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            logger.error(f"Erro ao configurar embeddings: {e}")
    
    def process_enem_documents_advanced(self) -> bool:
        """
        Processamento completo usando o pipeline integrado:
        PDF Avançado → Parser Melhorado → RAG Otimizado
        """
        logger.info("🚀 Iniciando processamento integrado do ENEM")
        
        if not self.enem_folder_path.exists():
            logger.error(f"Pasta do ENEM não encontrada: {self.enem_folder_path}")
            return False
        
        try:
            total_exercises = 0
            processing_details = {
                "files_processed": 0,
                "extraction_methods": {},
                "ocr_pages": 0,
                "parsing_quality": {},
                "errors": []
            }
            
            # Busca todos os anos
            year_folders = [f for f in self.enem_folder_path.iterdir() if f.is_dir()]
            year_folders.sort(key=lambda x: x.name, reverse=True)
            
            for year_folder in year_folders:
                year = year_folder.name
                logger.info(f"📅 Processando ano {year}...")
                
                # Busca PDFs de prova
                pdf_files = [f for f in year_folder.glob("*.pdf") 
                           if "gabarito" not in f.name.lower() and "gb" not in f.name.lower()]
                
                for pdf_file in pdf_files:
                    logger.info(f"   📄 Processando: {pdf_file.name}")
                    
                    try:
                        # ETAPA 1: Extração avançada de PDF
                        structured_text, extraction_stats = extract_pdf_advanced(pdf_file)
                        
                        # Atualiza estatísticas de extração
                        method = extraction_stats["extraction_method"]
                        processing_details["extraction_methods"][method] = \
                            processing_details["extraction_methods"].get(method, 0) + 1
                        
                        if extraction_stats.get("ocr_enabled", False):
                            processing_details["ocr_pages"] += extraction_stats.get("total_pages", 0)
                        
                        # ETAPA 2: Parser melhorado com estruturação JSON
                        exercises = self.exercise_parser.parse_pdf_text_to_exercises(
                            structured_text, year, pdf_file.name
                        )
                        
                        if exercises:
                            self.structured_exercises.extend(exercises)
                            total_exercises += len(exercises)
                            processing_details["files_processed"] += 1
                            
                            # Calcula qualidade do parsing
                            quality_scores = [self._calculate_exercise_quality(ex) for ex in exercises]
                            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
                            processing_details["parsing_quality"][pdf_file.name] = avg_quality
                            
                            logger.info(f"   ✅ {len(exercises)} exercícios estruturados extraídos (qualidade: {avg_quality:.1f}%)")
                        else:
                            logger.warning(f"   ⚠️ Nenhum exercício extraído de {pdf_file.name}")
                    
                    except Exception as e:
                        error_msg = f"Erro ao processar {pdf_file.name}: {str(e)}"
                        logger.error(f"   ❌ {error_msg}")
                        processing_details["errors"].append(error_msg)
            
            # ETAPA 3: Criação do RAG otimizado
            if self.structured_exercises:
                self._create_integrated_vectorstore()
                self._save_processing_cache()
                
                self.processing_stats = processing_details
                self.processing_stats["total_exercises"] = total_exercises
                
                logger.info(f"✅ Processamento integrado concluído: {total_exercises} exercícios")
                return True
            else:
                logger.warning("❌ Nenhum exercício foi extraído")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no processamento integrado: {e}")
            return False
    
    def _calculate_exercise_quality(self, exercise: ExerciseQuestion) -> float:
        """Calcula qualidade de um exercício (0-100)"""
        score = 0
        
        # Enunciado (40 pontos)
        if len(exercise.enunciado) >= 100:
            score += 40
        elif len(exercise.enunciado) >= 50:
            score += 20
        
        # Alternativas (40 pontos)
        if len(exercise.alternativas) >= 5:
            score += 20
        elif len(exercise.alternativas) >= 3:
            score += 10
        
        valid_alternatives = sum(1 for alt in exercise.alternativas if alt.is_valid)
        if valid_alternatives >= 4:
            score += 20
        elif valid_alternatives >= 3:
            score += 15
        elif valid_alternatives >= 2:
            score += 10
        
        # Metadados (20 pontos)
        if exercise.topicos_chave:
            score += 10
        if exercise.dificuldade_estimada and exercise.dificuldade_estimada != "":
            score += 10
        
        return min(100, score)
    
    def _create_integrated_vectorstore(self):
        """Cria vectorstore otimizado com dados estruturados"""
        try:
            documents = []
            
            for exercise in self.structured_exercises:
                # Conteúdo otimizado para busca
                search_content = self._create_enhanced_search_content(exercise)
                
                # Metadados super enriquecidos
                metadata = {
                    "id_questao": exercise.id_questao,
                    "year": exercise.ano,
                    "question_number": exercise.numero_questao,
                    "subject_area": exercise.area_conhecimento,
                    "topics": exercise.topicos_chave,
                    "difficulty": exercise.dificuldade_estimada,
                    "skill": exercise.habilidade_associada,
                    "source_file": exercise.fonte_arquivo,
                    "document_type": "integrated_exercise",
                    "quality_score": self._calculate_exercise_quality(exercise),
                    "num_alternatives": len(exercise.alternativas),
                    "valid_alternatives": sum(1 for alt in exercise.alternativas if alt.is_valid),
                    "avg_confidence": sum(alt.confidence for alt in exercise.alternativas) / len(exercise.alternativas) if exercise.alternativas else 0,
                    "has_structured_data": True
                }
                
                doc = Document(page_content=search_content, metadata=metadata)
                documents.append(doc)
            
            # Cria vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            logger.info(f"✅ Vectorstore integrado criado com {len(documents)} exercícios")
            
        except Exception as e:
            logger.error(f"Erro ao criar vectorstore integrado: {e}")
    
    def _create_enhanced_search_content(self, exercise: ExerciseQuestion) -> str:
        """Cria conteúdo super otimizado para busca semântica"""
        content_parts = []
        
        # Metadados para busca
        content_parts.append(f"QUESTÃO {exercise.numero_questao} ENEM {exercise.ano}")
        content_parts.append(f"ÁREA: {exercise.area_conhecimento}")
        
        if exercise.topicos_chave:
            content_parts.append(f"TÓPICOS: {' '.join(exercise.topicos_chave)}")
        
        content_parts.append(f"DIFICULDADE: {exercise.dificuldade_estimada}")
        content_parts.append(f"HABILIDADE: {exercise.habilidade_associada}")
        
        # Enunciado limpo
        content_parts.append("ENUNCIADO:")
        cleaned_statement = exercise.enunciado.replace("QUESTÃO", "").strip()
        content_parts.append(cleaned_statement)
        
        # Alternativas válidas apenas
        valid_alternatives = [alt for alt in exercise.alternativas if alt.is_valid and alt.texto.strip()]
        if valid_alternatives:
            content_parts.append("ALTERNATIVAS:")
            for alt in valid_alternatives:
                content_parts.append(f"{alt.letra}) {alt.texto}")
        
        # Palavras-chave para busca
        keywords = []
        for topic in exercise.topicos_chave:
            keywords.extend(topic.split())
        
        if keywords:
            content_parts.append(f"PALAVRAS-CHAVE: {' '.join(set(keywords))}")
        
        return "\n".join(content_parts)
    
    def _save_processing_cache(self):
        """Salva cache do processamento integrado"""
        try:
            cache_file = Path(self.persist_directory) / "integrated_cache.json"
            cache_file.parent.mkdir(exist_ok=True)
            
            cache_data = {
                "exercises": [ex.to_dict() for ex in self.structured_exercises],
                "processing_stats": self.processing_stats,
                "version": "integrated_v1.0"
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Cache integrado salvo: {len(self.structured_exercises)} exercícios")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache integrado: {e}")
    
    def load_existing_system(self) -> bool:
        """Carrega sistema integrado existente"""
        try:
            if Path(self.persist_directory).exists():
                # Carrega vectorstore
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                self.retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
                
                # Carrega cache
                cache_file = Path(self.persist_directory) / "integrated_cache.json"
                if cache_file.exists():
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Reconstrói exercícios
                    self.structured_exercises = []
                    for ex_data in cache_data.get("exercises", []):
                        exercise = self._rebuild_exercise_from_dict(ex_data)
                        if exercise:
                            self.structured_exercises.append(exercise)
                    
                    self.processing_stats = cache_data.get("processing_stats", {})
                    
                    logger.info(f"✅ Sistema integrado carregado: {len(self.structured_exercises)} exercícios")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao carregar sistema integrado: {e}")
            return False
    
    def _rebuild_exercise_from_dict(self, data: Dict) -> Optional[ExerciseQuestion]:
        """Reconstrói ExerciseQuestion a partir do cache"""
        try:
            from improved_exercise_parser import Alternative
            
            alternatives = [Alternative(**alt_data) for alt_data in data.get('alternativas', [])]
            
            exercise = ExerciseQuestion(
                id_questao=data['id_questao'],
                area_conhecimento=data['area_conhecimento'],
                enunciado=data['enunciado'],
                alternativas=alternatives,
                alternativa_correta=data.get('alternativa_correta'),
                topicos_chave=data.get('topicos_chave', []),
                ano=data.get('ano', ''),
                numero_questao=data.get('numero_questao', ''),
                fonte_arquivo=data.get('fonte_arquivo', ''),
                habilidade_associada=data.get('habilidade_associada', ''),
                dificuldade_estimada=data.get('dificuldade_estimada', ''),
                tipo_questao=data.get('tipo_questao', 'múltipla escolha')
            )
            
            return exercise
            
        except Exception as e:
            logger.error(f"Erro ao reconstruir exercício: {e}")
            return None
    
    def search_exercises_advanced(self, query: str, filters: Dict[str, Any] = None, k: int = 5) -> List[ExerciseQuestion]:
        """
        Busca avançada de exercícios com filtros múltiplos
        """
        if not self.retriever:
            return []
        
        try:
            # Busca base
            docs = self.retriever.get_relevant_documents(query)
            
            # Aplica filtros
            if filters:
                filtered_docs = []
                for doc in docs:
                    metadata = doc.metadata
                    
                    # Filtros disponíveis
                    if filters.get("subject_area") and filters["subject_area"].lower() not in metadata.get("subject_area", "").lower():
                        continue
                    
                    if filters.get("difficulty") and filters["difficulty"].lower() != metadata.get("difficulty", "").lower():
                        continue
                    
                    if filters.get("year") and str(filters["year"]) != str(metadata.get("year", "")):
                        continue
                    
                    if filters.get("min_quality") and metadata.get("quality_score", 0) < filters["min_quality"]:
                        continue
                    
                    if filters.get("topics"):
                        doc_topics = metadata.get("topics", [])
                        if not any(topic.lower() in [t.lower() for t in doc_topics] for topic in filters["topics"]):
                            continue
                    
                    filtered_docs.append(doc)
                
                docs = filtered_docs
            
            # Limita resultados
            docs = docs[:k]
            
            # Mapeia para exercícios estruturados
            results = []
            for doc in docs:
                question_id = doc.metadata.get("id_questao", "")
                exercise = self._find_exercise_by_id(question_id)
                if exercise:
                    results.append(exercise)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca avançada: {e}")
            return []
    
    def _find_exercise_by_id(self, question_id: str) -> Optional[ExerciseQuestion]:
        """Encontra exercício pelo ID"""
        for exercise in self.structured_exercises:
            if exercise.id_questao == question_id:
                return exercise
        return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Estatísticas completas do sistema integrado"""
        base_stats = {
            "total_exercises": len(self.structured_exercises),
            "processing_stats": self.processing_stats,
            "system_version": "integrated_v1.0"
        }
        
        if self.structured_exercises:
            # Estatísticas por área
            areas = {}
            difficulties = {}
            years = {}
            
            for ex in self.structured_exercises:
                areas[ex.area_conhecimento] = areas.get(ex.area_conhecimento, 0) + 1
                difficulties[ex.dificuldade_estimada] = difficulties.get(ex.dificuldade_estimada, 0) + 1
                years[ex.ano] = years.get(ex.ano, 0) + 1
            
            # Qualidade média
            quality_scores = [self._calculate_exercise_quality(ex) for ex in self.structured_exercises]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            base_stats.update({
                "by_area": areas,
                "by_difficulty": difficulties,
                "by_year": years,
                "average_quality": avg_quality,
                "high_quality_exercises": sum(1 for score in quality_scores if score >= 80),
                "components": {
                    "pdf_extractor": "AdvancedPDFExtractor",
                    "exercise_parser": "ImprovedExerciseParser", 
                    "display_system": "ImprovedExerciseDisplay",
                    "vectorstore": "Chroma + HuggingFace"
                }
            })
        
        return base_stats
    
    def display_exercises_with_advanced_ui(self, exercises: List[ExerciseQuestion], title: str = "📝 Exercícios Encontrados"):
        """Exibe exercícios usando a interface moderna"""
        display_exercises_list(exercises, title)

# Instância global do sistema integrado
integrated_enem_system = IntegratedENEMSystem()

if __name__ == "__main__":
    # Teste do sistema integrado
    print("🚀 Testando Sistema Integrado do ENEM")
    print("=" * 60)
    
    system = IntegratedENEMSystem()
    
    # Tenta carregar sistema existente
    if system.load_existing_system():
        print("✅ Sistema integrado carregado do cache")
        stats = system.get_system_stats()
        print(f"📊 Estatísticas: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # Teste de busca
        results = system.search_exercises_advanced("energia cinética", k=2)
        if results:
            print(f"\n🔍 Teste de busca: {len(results)} exercícios encontrados")
            for ex in results:
                print(f"   📝 {ex.id_questao} - {ex.area_conhecimento}")
    else:
        print("⚠️ Sistema integrado não encontrado. Execute o processamento primeiro.")
        print("💡 Use: system.process_enem_documents_advanced()") 