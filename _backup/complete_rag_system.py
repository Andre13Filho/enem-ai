#!/usr/bin/env python3
"""
Sistema RAG Completo para o ENEM
Integra extração avançada, pré-processamento estruturado e chunking inteligente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Imports dos sistemas desenvolvidos
try:
    from advanced_pdf_extractor import AdvancedPDFExtractor
    from enem_text_preprocessor import ENEMTextPreprocessor
    from intelligent_chunker import IntelligentChunker, ChunkingStrategy, QuestionChunk
    from improved_exercise_parser import ImprovedExerciseParser
except ImportError as e:
    print(f"⚠️ Aviso: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteENEMRAGSystem:
    """
    Sistema RAG Completo para o ENEM
    
    Pipeline integrado:
    1. Extração Avançada de PDF (PyMuPDF + pdfplumber + OCR)
    2. Pré-processamento Estruturado (regex patterns específicos)
    3. Chunking Inteligente (semantic chunking + contextual overlap)
    4. Indexação Vetorial Aprimorada
    5. Busca Semântica Avançada
    """
    
    def __init__(self, chunking_strategy: ChunkingStrategy = ChunkingStrategy.QUESTION_BASED):
        self.pdf_extractor = None
        self.text_preprocessor = None
        self.intelligent_chunker = None
        self.exercise_parser = None
        
        # Inicializa componentes
        self._initialize_components(chunking_strategy)
        
        # Configurações do sistema
        self.config = {
            "enable_advanced_extraction": True,
            "enable_structured_preprocessing": True,
            "enable_intelligent_chunking": True,
            "preserve_question_integrity": True,
            "include_contextual_overlap": True,
            "max_chunk_size": 2000,
            "min_chunk_size": 100,
            "overlap_percentage": 0.1
        }
        
        # Estatísticas do sistema
        self.system_stats = {
            "total_documents_processed": 0,
            "total_chunks_created": 0,
            "total_questions_extracted": 0,
            "average_extraction_quality": 0.0,
            "processing_times": [],
            "error_count": 0
        }
    
    def _initialize_components(self, chunking_strategy: ChunkingStrategy):
        """Inicializa componentes do sistema"""
        try:
            self.pdf_extractor = AdvancedPDFExtractor()
            logger.info("✅ Extrator avançado de PDF inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Extrator avançado não disponível: {e}")
        
        try:
            self.text_preprocessor = ENEMTextPreprocessor()
            logger.info("✅ Pré-processador estruturado inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Pré-processador não disponível: {e}")
        
        try:
            self.intelligent_chunker = IntelligentChunker(chunking_strategy)
            logger.info(f"✅ Chunker inteligente inicializado ({chunking_strategy.value})")
        except Exception as e:
            logger.warning(f"⚠️ Chunker inteligente não disponível: {e}")
        
        try:
            self.exercise_parser = ImprovedExerciseParser()
            logger.info("✅ Parser melhorado inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Parser melhorado não disponível: {e}")
    
    def process_document(self, document_path: str, **kwargs) -> Dict[str, Any]:
        """
        Processa um documento completo através do pipeline integrado
        """
        start_time = datetime.now()
        logger.info(f"🚀 Iniciando processamento completo: {document_path}")
        
        results = {
            "document_path": document_path,
            "processing_start": start_time.isoformat(),
            "pipeline_stages": {},
            "final_chunks": [],
            "extracted_questions": [],
            "quality_metrics": {},
            "processing_summary": {}
        }
        
        try:
            # Etapa 1: Extração Avançada de PDF
            extraction_result = self._stage_1_advanced_extraction(document_path)
            results["pipeline_stages"]["extraction"] = extraction_result
            
            # Etapa 2: Pré-processamento Estruturado
            if extraction_result.get("success"):
                preprocessing_result = self._stage_2_structured_preprocessing(
                    extraction_result["extracted_text"]
                )
                results["pipeline_stages"]["preprocessing"] = preprocessing_result
            else:
                preprocessing_result = {"success": False, "error": "Extraction failed"}
                results["pipeline_stages"]["preprocessing"] = preprocessing_result
            
            # Etapa 3: Chunking Inteligente
            if preprocessing_result.get("success"):
                chunking_result = self._stage_3_intelligent_chunking(
                    preprocessing_result["processed_text"], 
                    preprocessing_result.get("structured_data")
                )
                results["pipeline_stages"]["chunking"] = chunking_result
                results["final_chunks"] = chunking_result.get("chunks", [])
            else:
                chunking_result = {"success": False, "error": "Preprocessing failed"}
                results["pipeline_stages"]["chunking"] = chunking_result
            
            # Etapa 4: Extração de Questões
            if chunking_result.get("success"):
                question_extraction_result = self._stage_4_question_extraction(
                    results["final_chunks"]
                )
                results["pipeline_stages"]["question_extraction"] = question_extraction_result
                results["extracted_questions"] = question_extraction_result.get("questions", [])
            
            # Etapa 5: Métricas de Qualidade
            quality_metrics = self._calculate_quality_metrics(results)
            results["quality_metrics"] = quality_metrics
            
            # Finalização
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            results["processing_end"] = end_time.isoformat()
            results["processing_time_seconds"] = processing_time
            results["processing_summary"] = self._generate_processing_summary(results)
            
            # Atualiza estatísticas do sistema
            self._update_system_stats(results, processing_time)
            
            logger.info(f"✅ Processamento concluído em {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {e}")
            results["error"] = str(e)
            self.system_stats["error_count"] += 1
        
        return results
    
    def _stage_1_advanced_extraction(self, document_path: str) -> Dict[str, Any]:
        """Etapa 1: Extração avançada de PDF"""
        logger.info("📄 Etapa 1: Extração avançada de PDF")
        
        if not self.pdf_extractor:
            return {
                "success": False,
                "method": "fallback",
                "error": "Advanced extractor not available",
                "extracted_text": self._fallback_text_extraction(document_path)
            }
        
        try:
            extraction_result = self.pdf_extractor.extract_pdf(document_path)
            
            # Combina texto de todos os blocos
            text_blocks = extraction_result.get("text_blocks", [])
            combined_text = "\n\n".join([
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in text_blocks
            ])
            
            return {
                "success": True,
                "method": "advanced",
                "extracted_text": combined_text,
                "text_blocks_count": len(text_blocks),
                "extraction_stats": extraction_result.get("extraction_stats", {}),
                "pages_processed": extraction_result.get("pages_processed", 0)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Extração avançada falhou: {e}")
            return {
                "success": False,
                "method": "fallback",
                "error": str(e),
                "extracted_text": self._fallback_text_extraction(document_path)
            }
    
    def _stage_2_structured_preprocessing(self, text: str) -> Dict[str, Any]:
        """Etapa 2: Pré-processamento estruturado"""
        logger.info("🔍 Etapa 2: Pré-processamento estruturado")
        
        if not self.text_preprocessor:
            return {
                "success": False,
                "method": "basic",
                "processed_text": text,
                "error": "Structured preprocessor not available"
            }
        
        try:
            preprocessing_result = self.text_preprocessor.preprocess_text(text)
            
            return {
                "success": True,
                "method": "structured",
                "processed_text": preprocessing_result["cleaned_text"],
                "structured_data": preprocessing_result,
                "patterns_found": len(preprocessing_result.get("patterns", [])),
                "quality_score": preprocessing_result.get("stats", {}).get("quality_indicators", {}).get("avg_confidence", 0)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Pré-processamento estruturado falhou: {e}")
            return {
                "success": False,
                "method": "basic",
                "processed_text": text,
                "error": str(e)
            }
    
    def _stage_3_intelligent_chunking(self, text: str, structured_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Etapa 3: Chunking inteligente"""
        logger.info("✂️ Etapa 3: Chunking inteligente")
        
        if not self.intelligent_chunker:
            return {
                "success": False,
                "method": "basic",
                "chunks": self._basic_chunking(text),
                "error": "Intelligent chunker not available"
            }
        
        try:
            chunks = self.intelligent_chunker.chunk_text(text)
            chunking_stats = self.intelligent_chunker.get_chunking_stats()
            
            return {
                "success": True,
                "method": "intelligent",
                "chunks": chunks,
                "chunks_count": len(chunks),
                "chunking_stats": chunking_stats,
                "average_chunk_size": chunking_stats.get("avg_chunk_size", 0),
                "average_quality": chunking_stats.get("avg_quality_score", 0)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Chunking inteligente falhou: {e}")
            return {
                "success": False,
                "method": "basic",
                "chunks": self._basic_chunking(text),
                "error": str(e)
            }
    
    def _stage_4_question_extraction(self, chunks: List[QuestionChunk]) -> Dict[str, Any]:
        """Etapa 4: Extração de questões"""
        logger.info("❓ Etapa 4: Extração de questões")
        
        extracted_questions = []
        
        for chunk in chunks:
            # Extrai informações da questão do chunk
            if chunk.metadata.question_numbers:
                for question_number in chunk.metadata.question_numbers:
                    question_data = {
                        "question_number": question_number,
                        "content": chunk.clean_content,
                        "alternatives": chunk.alternatives,
                        "commands": chunk.commands,
                        "subject_area": chunk.metadata.subject_area,
                        "chunk_id": chunk.metadata.chunk_id,
                        "quality_score": chunk.quality_score,
                        "context_before": chunk.context_before,
                        "context_after": chunk.context_after
                    }
                    extracted_questions.append(question_data)
        
        return {
            "success": True,
            "questions": extracted_questions,
            "questions_count": len(extracted_questions),
            "questions_with_alternatives": sum(1 for q in extracted_questions if q["alternatives"]),
            "average_question_quality": sum(q["quality_score"] for q in extracted_questions) / len(extracted_questions) if extracted_questions else 0
        }
    
    def _calculate_quality_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de qualidade do processamento"""
        metrics = {
            "overall_quality_score": 0.0,
            "extraction_quality": 0.0,
            "preprocessing_quality": 0.0,
            "chunking_quality": 0.0,
            "question_extraction_quality": 0.0,
            "completeness_score": 0.0,
            "consistency_score": 0.0
        }
        
        # Qualidade da extração
        extraction_stage = results.get("pipeline_stages", {}).get("extraction", {})
        if extraction_stage.get("success"):
            metrics["extraction_quality"] = 0.9 if extraction_stage.get("method") == "advanced" else 0.6
        
        # Qualidade do pré-processamento
        preprocessing_stage = results.get("pipeline_stages", {}).get("preprocessing", {})
        if preprocessing_stage.get("success"):
            metrics["preprocessing_quality"] = preprocessing_stage.get("quality_score", 0.5)
        
        # Qualidade do chunking
        chunking_stage = results.get("pipeline_stages", {}).get("chunking", {})
        if chunking_stage.get("success"):
            metrics["chunking_quality"] = chunking_stage.get("average_quality", 0.5)
        
        # Qualidade da extração de questões
        question_stage = results.get("pipeline_stages", {}).get("question_extraction", {})
        if question_stage.get("success"):
            metrics["question_extraction_quality"] = question_stage.get("average_question_quality", 0.5)
        
        # Score geral
        metrics["overall_quality_score"] = sum([
            metrics["extraction_quality"],
            metrics["preprocessing_quality"],
            metrics["chunking_quality"],
            metrics["question_extraction_quality"]
        ]) / 4
        
        # Completude (quantas etapas foram bem-sucedidas)
        successful_stages = sum(1 for stage in results.get("pipeline_stages", {}).values() 
                               if stage.get("success", False))
        total_stages = len(results.get("pipeline_stages", {}))
        metrics["completeness_score"] = successful_stages / total_stages if total_stages > 0 else 0
        
        # Consistência (baseada na qualidade uniforme entre etapas)
        quality_scores = [v for k, v in metrics.items() if k.endswith("_quality") and v > 0]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            variance = sum((q - avg_quality) ** 2 for q in quality_scores) / len(quality_scores)
            metrics["consistency_score"] = max(0, 1 - variance)
        
        return metrics
    
    def _generate_processing_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo do processamento"""
        # Trata caso onde document_path pode não existir (processamento direto de texto)
        document_name = "direct_text_processing"
        if "document_path" in results:
            document_name = os.path.basename(results["document_path"])
        elif "source_type" in results:
            document_name = results["source_type"]
            
        return {
            "document": document_name,
            "total_chunks": len(results["final_chunks"]),
            "total_questions": len(results["extracted_questions"]),
            "processing_time": results.get("processing_time_seconds", 0),
            "overall_quality": results.get("quality_metrics", {}).get("overall_quality_score", 0),
            "pipeline_success": all(
                stage.get("success", False) 
                for stage in results.get("pipeline_stages", {}).values()
            ),
            "successful_stages": [
                stage_name for stage_name, stage_data in results.get("pipeline_stages", {}).items()
                if stage_data.get("success", False)
            ]
        }
    
    def _update_system_stats(self, results: Dict[str, Any], processing_time: float):
        """Atualiza estatísticas do sistema"""
        self.system_stats["total_documents_processed"] += 1
        self.system_stats["total_chunks_created"] += len(results["final_chunks"])
        self.system_stats["total_questions_extracted"] += len(results["extracted_questions"])
        self.system_stats["processing_times"].append(processing_time)
        
        # Atualiza qualidade média
        current_quality = results["quality_metrics"]["overall_quality_score"]
        total_docs = self.system_stats["total_documents_processed"]
        
        self.system_stats["average_extraction_quality"] = (
            (self.system_stats["average_extraction_quality"] * (total_docs - 1) + current_quality) / total_docs
        )
    
    def _fallback_text_extraction(self, document_path: str) -> str:
        """Extração de texto básica como fallback"""
        try:
            import PyPDF2
            with open(document_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except:
            return ""
    
    def _basic_chunking(self, text: str) -> List[QuestionChunk]:
        """Chunking básico como fallback"""
        from intelligent_chunker import QuestionChunk, ChunkMetadata
        
        chunk_size = 1000
        chunks = []
        
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i + chunk_size]
            if len(chunk_text) > 50:
                metadata = ChunkMetadata(
                    chunk_id=f"basic_chunk_{len(chunks)}",
                    chunk_type="basic_size",
                    question_numbers=[]
                )
                
                chunk = QuestionChunk(
                    content=chunk_text,
                    clean_content=chunk_text.strip(),
                    metadata=metadata,
                    chunk_size=len(chunk_text)
                )
                chunks.append(chunk)
        
        return chunks
    
    def export_results(self, results: Dict[str, Any], output_path: str):
        """Exporta resultados completos do processamento"""
        # Serializa chunks para exportação
        serializable_results = results.copy()
        
        if "final_chunks" in serializable_results:
            serializable_results["final_chunks"] = [
                {
                    "chunk_id": chunk.metadata.chunk_id,
                    "chunk_type": chunk.metadata.chunk_type,
                    "content": chunk.content,
                    "clean_content": chunk.clean_content,
                    "question_numbers": chunk.metadata.question_numbers,
                    "alternatives": chunk.alternatives,
                    "commands": chunk.commands,
                    "context_before": chunk.context_before,
                    "context_after": chunk.context_after,
                    "chunk_size": chunk.chunk_size,
                    "quality_score": chunk.quality_score,
                    "metadata": {
                        "subject_area": chunk.metadata.subject_area,
                        "topics": chunk.metadata.topics,
                        "confidence_score": chunk.metadata.confidence_score,
                        "original_position": chunk.metadata.original_position
                    }
                } for chunk in results["final_chunks"]
            ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 Resultados exportados para: {output_path}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        stats = self.system_stats.copy()
        
        if stats["processing_times"]:
            stats["average_processing_time"] = sum(stats["processing_times"]) / len(stats["processing_times"])
            stats["total_processing_time"] = sum(stats["processing_times"])
        else:
            stats["average_processing_time"] = 0
            stats["total_processing_time"] = 0
        
        return stats
    
    def process_text_directly(self, text: str) -> Dict[str, Any]:
        """Processa texto diretamente (sem PDF)"""
        logger.info("📝 Processando texto diretamente")
        
        start_time = datetime.now()
        
        results = {
            "source_type": "direct_text",
            "processing_start": start_time.isoformat(),
            "pipeline_stages": {},
            "final_chunks": [],
            "extracted_questions": [],
            "quality_metrics": {},
            "processing_summary": {}
        }
        
        try:
            # Pula extração de PDF, vai direto para pré-processamento
            preprocessing_result = self._stage_2_structured_preprocessing(text)
            results["pipeline_stages"]["preprocessing"] = preprocessing_result
            
            # Chunking inteligente
            if preprocessing_result.get("success"):
                chunking_result = self._stage_3_intelligent_chunking(
                    preprocessing_result["processed_text"], 
                    preprocessing_result.get("structured_data")
                )
                results["pipeline_stages"]["chunking"] = chunking_result
                results["final_chunks"] = chunking_result.get("chunks", [])
            
            # Extração de questões
            if results["final_chunks"]:
                question_extraction_result = self._stage_4_question_extraction(
                    results["final_chunks"]
                )
                results["pipeline_stages"]["question_extraction"] = question_extraction_result
                results["extracted_questions"] = question_extraction_result.get("questions", [])
            
            # Métricas de qualidade
            quality_metrics = self._calculate_quality_metrics(results)
            results["quality_metrics"] = quality_metrics
            
            # Finalização
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            results["processing_end"] = end_time.isoformat()
            results["processing_time_seconds"] = processing_time
            results["processing_summary"] = self._generate_processing_summary(results)
            
            logger.info(f"✅ Processamento de texto concluído em {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento de texto: {e}")
            results["error"] = str(e)
        
        return results

# Função de conveniência para uso direto
def process_enem_document(document_path: str, 
                         chunking_strategy: ChunkingStrategy = ChunkingStrategy.QUESTION_BASED,
                         output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Função principal para processar documentos do ENEM
    
    Args:
        document_path: Caminho para o PDF ou texto
        chunking_strategy: Estratégia de chunking a usar
        output_path: Caminho para salvar resultados (opcional)
    
    Returns:
        Dict com resultados completos do processamento
    """
    system = CompleteENEMRAGSystem(chunking_strategy)
    
    if document_path.endswith('.pdf'):
        results = system.process_document(document_path)
    else:
        # Assume que é texto direto
        with open(document_path, 'r', encoding='utf-8') as f:
            text = f.read()
        results = system.process_text_directly(text)
    
    if output_path:
        system.export_results(results, output_path)
    
    return results

if __name__ == "__main__":
    # Demonstração do sistema completo
    print("🚀 SISTEMA RAG COMPLETO PARA O ENEM")
    print("=" * 70)
    print("🔧 Pipeline integrado: Extração + Pré-processamento + Chunking + RAG")
    print()
    
    # Teste com texto de exemplo
    sample_text = """
    CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS
    
    QUESTÃO 91
    
    Muitas pessoas ainda se espantam com o fato de um passageiro sair ileso de um 
    acidente de carro enquanto o veículo onde estava teve perda total. Isso só é 
    possível devido ao funcionamento adequado dos dispositivos de segurança do veículo.
    
    A função do cinto de segurança é:
    
    A) acionar os airbags do veículo.
    B) absorver a energia cinética do sistema.
    C) reduzir a velocidade do veículo.
    D) aumentar o tempo de colisão.
    E) diminuir a força média de impacto.
    
    QUESTÃO 92
    
    A energia cinética de um objeto em movimento é dada pela fórmula E = mv²/2, 
    onde m é a massa e v é a velocidade do objeto.
    
    Assinale a alternativa correta sobre energia cinética:
    
    A) Energia cinética é independente da massa do objeto.
    B) Energia cinética varia linearmente com a velocidade.
    C) Energia cinética é proporcional ao quadrado da velocidade.
    D) Energia cinética não depende da velocidade do objeto.
    E) Energia cinética é sempre constante durante o movimento.
    """
    
    print("📝 Processando texto de exemplo...")
    
    system = CompleteENEMRAGSystem(ChunkingStrategy.QUESTION_BASED)
    results = system.process_text_directly(sample_text)
    
    print(f"✅ Processamento concluído!")
    print()
    print(f"📊 RESUMO DOS RESULTADOS:")
    print(f"   📄 Chunks criados: {len(results['final_chunks'])}")
    print(f"   ❓ Questões extraídas: {len(results['extracted_questions'])}")
    print(f"   ⏱️ Tempo de processamento: {results['processing_time_seconds']:.2f}s")
    print(f"   ⭐ Qualidade geral: {results['quality_metrics']['overall_quality_score']:.1%}")
    print(f"   ✅ Pipeline completo: {results['processing_summary']['pipeline_success']}")
    
    print(f"\n🔧 ETAPAS EXECUTADAS:")
    for stage_name, stage_data in results["pipeline_stages"].items():
        status = "✅" if stage_data.get("success") else "❌"
        method = stage_data.get("method", "unknown")
        print(f"   {status} {stage_name.title()}: {method}")
    
    if results["final_chunks"]:
        print(f"\n📦 CHUNKS CRIADOS:")
        for i, chunk in enumerate(results["final_chunks"], 1):
            print(f"   📝 Chunk {i}:")
            print(f"      🆔 ID: {chunk.metadata.chunk_id}")
            print(f"      🔢 Questões: {chunk.metadata.question_numbers}")
            print(f"      📏 Tamanho: {chunk.chunk_size} chars")
            print(f"      ⭐ Qualidade: {chunk.quality_score:.1%}")
    
    if results["extracted_questions"]:
        print(f"\n❓ QUESTÕES EXTRAÍDAS:")
        for question in results["extracted_questions"]:
            print(f"   📝 Questão {question['question_number']}:")
            print(f"      🔤 Alternativas: {len(question['alternatives'])}")
            print(f"      📋 Comandos: {len(question['commands'])}")
            print(f"      ⭐ Qualidade: {question['quality_score']:.1%}")
    
    print("\n🎉 Sistema RAG completo funcionando perfeitamente!")
    print("🏆 Todos os componentes integrados com sucesso!") 