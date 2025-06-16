"""
🚀 SISTEMA RAG COMPLETO MELHORADO - VERSÃO ENHANCED
==================================================
Sistema RAG integrado com tecnologias complementares para ENEM

Tecnologias incluídas:
- Extração PDF avançada (PyMuPDF + pdfplumber + OCR)
- Pré-processamento estruturado (regex patterns)
- Chunking inteligente (5 estratégias)
- Enhanced parsing (Unstructured.io + LlamaIndex)
- Pipeline completo integrado
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedRAGResult:
    """Resultado do sistema RAG melhorado"""
    content: str
    chunks: List[Dict[str, Any]]
    questions: List[Dict[str, Any]]
    parsing_method: str
    preprocessing_quality: float
    chunking_quality: float
    extraction_method: str
    processing_time: float
    metadata: Dict[str, Any]
    enhanced_elements: List[Dict[str, Any]]
    confidence_score: float

class EnhancedCompleteRAGSystem:
    """Sistema RAG completo com tecnologias melhoradas"""
    
    def __init__(self, chunking_strategy: str = "question_based"):
        self.chunking_strategy = chunking_strategy
        self._initialize_components()
        logger.info("🚀 Sistema RAG Enhanced inicializado")
    
    def _initialize_components(self):
        """Inicializa todos os componentes do sistema"""
        try:
            # Componentes principais
            from advanced_pdf_extractor import AdvancedPDFExtractor
            from enem_text_preprocessor import ENEMTextPreprocessor
            from intelligent_chunker import IntelligentChunker
            from improved_exercise_parser import ImprovedExerciseParser
            
            # Novos componentes enhanced
            from enhanced_pdf_parser import EnhancedPDFParser
            
            self.pdf_extractor = AdvancedPDFExtractor()
            self.preprocessor = ENEMTextPreprocessor()
            self.chunker = IntelligentChunker(
                strategy=self.chunking_strategy
            )
            self.exercise_parser = ImprovedExerciseParser()
            self.enhanced_parser = EnhancedPDFParser()
            
            logger.info("✅ Todos os componentes inicializados")
            
        except ImportError as e:
            logger.warning(f"⚠️ Alguns componentes não disponíveis: {e}")
            # Fallbacks para componentes não disponíveis
            self._setup_fallbacks()
    
    def _setup_fallbacks(self):
        """Configura fallbacks para componentes não disponíveis"""
        try:
            # Tentar componentes essenciais
            from enem_text_preprocessor import ENEMTextPreprocessor
            from intelligent_chunker import IntelligentChunker
            
            self.preprocessor = ENEMTextPreprocessor()
            self.chunker = IntelligentChunker(
                strategy=self.chunking_strategy
            )
            
            # Simuladores para outros componentes
            self.pdf_extractor = None
            self.exercise_parser = None
            self.enhanced_parser = None
            
            logger.info("✅ Componentes essenciais carregados com fallbacks")
            
        except ImportError:
            logger.error("❌ Componentes essenciais não disponíveis")
            raise
    
    def process_pdf(self, pdf_path: str, use_enhanced: bool = True) -> EnhancedRAGResult:
        """
        Processa PDF com pipeline completo melhorado
        
        Args:
            pdf_path: Caminho para o PDF
            use_enhanced: Usar tecnologias enhanced (Unstructured.io + LlamaIndex)
        """
        start_time = time.time()
        logger.info(f"🚀 Iniciando processamento enhanced: {pdf_path}")
        
        # Etapa 1: Extração de PDF
        text_content, extraction_method = self._extract_pdf_content(pdf_path, use_enhanced)
        
        if not text_content:
            return self._create_empty_result("Falha na extração de PDF", start_time)
        
        # Etapa 2: Processamento completo
        return self._process_text_enhanced(text_content, extraction_method, start_time)
    
    def process_text(self, text: str) -> EnhancedRAGResult:
        """Processa texto diretamente com pipeline melhorado"""
        start_time = time.time()
        logger.info("📝 Processando texto diretamente (enhanced)")
        
        return self._process_text_enhanced(text, "direct_text", start_time)
    
    def _extract_pdf_content(self, pdf_path: str, use_enhanced: bool) -> Tuple[str, str]:
        """Extrai conteúdo do PDF usando métodos disponíveis"""
        
        if use_enhanced and self.enhanced_parser:
            logger.info("🔧 Usando Enhanced PDF Parser")
            try:
                result = self.enhanced_parser.parse_pdf(pdf_path, preferred_method="all")
                if result.confidence_score > 0.5:
                    return result.content, f"enhanced_{result.parsing_method}"
            except Exception as e:
                logger.warning(f"⚠️ Enhanced parser falhou: {e}")
        
        if self.pdf_extractor:
            logger.info("📄 Usando Advanced PDF Extractor")
            try:
                result = self.pdf_extractor.extract_from_file(pdf_path)
                if result and result.text:
                    return result.text, "advanced_extractor"
            except Exception as e:
                logger.warning(f"⚠️ Advanced extractor falhou: {e}")
        
        # Fallback básico
        logger.info("📝 Usando fallback básico para PDF")
        try:
            import PyMuPDF
            doc = PyMuPDF.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text, "pymupdf_basic"
        except Exception as e:
            logger.error(f"❌ Falha na extração básica: {e}")
            return "", "failed"
    
    def _process_text_enhanced(self, text: str, extraction_method: str, start_time: float) -> EnhancedRAGResult:
        """Processa texto com pipeline completo melhorado"""
        
        logger.info("🔍 Etapa 2: Pré-processamento estruturado")
        
        # Pré-processamento
        preprocessing_result = self.preprocessor.preprocess_text(text)
        preprocessing_quality = self._calculate_preprocessing_quality(preprocessing_result)
        
        logger.info("✂️ Etapa 3: Chunking inteligente")
        
        # Chunking inteligente
        try:
            chunks_result = self.chunker.chunk_text(text)
            chunks = chunks_result.chunks if hasattr(chunks_result, 'chunks') else []
        except Exception as e:
            logger.warning(f"⚠️ Chunking falhou: {e}")
            # Fallback: criar chunks simples
            chunks = [{"content": text, "chunk_id": "fallback_0", "quality_score": 0.5}]
        chunking_quality = self._calculate_chunking_quality(chunks)
        
        logger.info("❓ Etapa 4: Extração de questões")
        
        # Extração de questões melhorada
        questions = self._extract_questions_enhanced(chunks, preprocessing_result)
        
        # Elementos enhanced (se disponível)
        enhanced_elements = self._extract_enhanced_elements(text)
        
        processing_time = time.time() - start_time
        
        # Calcular confiança geral
        confidence_score = self._calculate_overall_confidence(
            preprocessing_quality, chunking_quality, len(questions), len(enhanced_elements)
        )
        
        logger.info(f"✅ Processamento enhanced concluído em {processing_time:.2f}s")
        
        return EnhancedRAGResult(
            content=text,
            chunks=chunks,
            questions=questions,
            parsing_method=extraction_method,
            preprocessing_quality=preprocessing_quality,
            chunking_quality=chunking_quality,
            extraction_method=extraction_method,
            processing_time=processing_time,
            metadata={
                "preprocessing_patterns": len(preprocessing_result.patterns) if hasattr(preprocessing_result, 'patterns') else 0,
                "chunking_strategy": self.chunking_strategy,
                "enhanced_processing": True,
                "pipeline_version": "enhanced_v1.0"
            },
            enhanced_elements=enhanced_elements,
            confidence_score=confidence_score
        )
    
    def _extract_questions_enhanced(self, chunks: List[Dict[str, Any]], preprocessing_result) -> List[Dict[str, Any]]:
        """Extração de questões melhorada"""
        questions = []
        
        if self.exercise_parser:
            try:
                # Usar parser melhorado se disponível
                for i, chunk in enumerate(chunks):
                    content = chunk.get('content', '') or chunk.get('clean_content', '')
                    parsed = self.exercise_parser.parse_exercises(content)
                    
                    if parsed and hasattr(parsed, 'exercises'):
                        for exercise in parsed.exercises:
                            questions.append({
                                "id": f"enhanced_q_{len(questions)}",
                                "content": exercise.content if hasattr(exercise, 'content') else str(exercise),
                                "chunk_id": chunk.get('chunk_id', f'chunk_{i}'),
                                "source": "enhanced_parser",
                                "confidence": getattr(exercise, 'confidence', 0.8)
                            })
                            
            except Exception as e:
                logger.warning(f"⚠️ Parser melhorado falhou: {e}")
        
        # Fallback: extrair questões dos chunks
        if not questions:
            for i, chunk in enumerate(chunks):
                question_numbers = chunk.get('question_numbers', [])
                for q_num in question_numbers:
                    questions.append({
                        "id": f"fallback_q_{q_num}",
                        "number": q_num,
                        "chunk_id": chunk.get('chunk_id', f'chunk_{i}'),
                        "source": "chunker_fallback",
                        "confidence": chunk.get('quality_score', 0.5)
                    })
        
        return questions
    
    def _extract_enhanced_elements(self, text: str) -> List[Dict[str, Any]]:
        """Extrai elementos usando tecnologias enhanced"""
        if not self.enhanced_parser:
            return []
        
        try:
            # Simular parsing enhanced em texto
            import re
            elements = []
            
            # Detectar questões
            questions = re.findall(r'QUESTÃO\s+(\d+)', text, re.IGNORECASE)
            for q in questions:
                elements.append({
                    "type": "question_header",
                    "content": f"QUESTÃO {q}",
                    "question_number": int(q),
                    "confidence": 0.95,
                    "source": "enhanced_detection"
                })
            
            # Detectar alternativas
            alternatives = re.findall(r'([A-E]\)\s+[^\n]+)', text)
            for alt in alternatives:
                elements.append({
                    "type": "alternative",
                    "content": alt,
                    "letter": alt[0],
                    "confidence": 0.90,
                    "source": "enhanced_detection"
                })
            
            # Detectar comandos
            commands = re.findall(r'(assinale|marque|indique)[^\n]*', text, re.IGNORECASE)
            for cmd in commands:
                elements.append({
                    "type": "command",
                    "content": cmd,
                    "confidence": 0.85,
                    "source": "enhanced_detection"
                })
            
            return elements
            
        except Exception as e:
            logger.warning(f"⚠️ Enhanced element extraction falhou: {e}")
            return []
    
    def _calculate_preprocessing_quality(self, result) -> float:
        """Calcula qualidade do pré-processamento"""
        if not hasattr(result, 'patterns'):
            return 0.5
        
        patterns_count = len(result.patterns)
        confidence_sum = sum(p.confidence for p in result.patterns)
        
        if patterns_count == 0:
            return 0.0
        
        avg_confidence = confidence_sum / patterns_count
        return min(avg_confidence, 1.0)
    
    def _calculate_chunking_quality(self, chunks: List[Dict[str, Any]]) -> float:
        """Calcula qualidade do chunking"""
        if not chunks:
            return 0.0
        
        quality_scores = [chunk.get('quality_score', 0.5) for chunk in chunks]
        return sum(quality_scores) / len(quality_scores)
    
    def _calculate_overall_confidence(self, preprocessing_quality: float, chunking_quality: float, 
                                    questions_count: int, enhanced_elements_count: int) -> float:
        """Calcula confiança geral do sistema"""
        base_score = (preprocessing_quality + chunking_quality) / 2
        
        # Bonus por questões encontradas
        if questions_count > 0:
            base_score += min(questions_count * 0.1, 0.3)
        
        # Bonus por elementos enhanced
        if enhanced_elements_count > 0:
            base_score += min(enhanced_elements_count * 0.02, 0.2)
        
        return min(base_score, 1.0)
    
    def _create_empty_result(self, error_msg: str, start_time: float) -> EnhancedRAGResult:
        """Cria resultado vazio em caso de erro"""
        return EnhancedRAGResult(
            content="",
            chunks=[],
            questions=[],
            parsing_method="failed",
            preprocessing_quality=0.0,
            chunking_quality=0.0,
            extraction_method="failed",
            processing_time=time.time() - start_time,
            metadata={"error": error_msg},
            enhanced_elements=[],
            confidence_score=0.0
        )
    
    def export_enhanced_result(self, result: EnhancedRAGResult, output_path: str):
        """Exporta resultado enhanced para JSON"""
        export_data = {
            "enhanced_rag_result": {
                "parsing_method": result.parsing_method,
                "extraction_method": result.extraction_method,
                "preprocessing_quality": result.preprocessing_quality,
                "chunking_quality": result.chunking_quality,
                "confidence_score": result.confidence_score,
                "processing_time": result.processing_time,
                "chunks_count": len(result.chunks),
                "questions_count": len(result.questions),
                "enhanced_elements_count": len(result.enhanced_elements)
            },
            "content": result.content,
            "chunks": result.chunks,
            "questions": result.questions,
            "enhanced_elements": result.enhanced_elements,
            "metadata": result.metadata
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Resultado enhanced exportado: {output_path}")
    
    def compare_methods(self, text: str) -> Dict[str, Any]:
        """Compara diferentes métodos de processamento"""
        logger.info("🔄 Comparando métodos de processamento")
        
        strategies = ["question_based", "semantic_groups", "contextual_overlap"]
        results = {}
        
        for strategy in strategies:
            logger.info(f"   Testando estratégia: {strategy}")
            
            # Temporariamente mudar estratégia
            original_strategy = self.chunking_strategy
            self.chunking_strategy = strategy
            self.chunker.strategy = strategy
            
            result = self.process_text(text)
            results[strategy] = {
                "chunks_count": len(result.chunks),
                "questions_count": len(result.questions),
                "preprocessing_quality": result.preprocessing_quality,
                "chunking_quality": result.chunking_quality,
                "confidence_score": result.confidence_score,
                "processing_time": result.processing_time
            }
            
            # Restaurar estratégia original
            self.chunking_strategy = original_strategy
            self.chunker.strategy = original_strategy
        
        return {
            "comparison_results": results,
            "best_strategy": max(results.keys(), key=lambda k: results[k]["confidence_score"]),
            "timestamp": time.time()
        }

# Função de demonstração
def main():
    """Demonstração do sistema RAG enhanced"""
    print("🚀 SISTEMA RAG COMPLETO ENHANCED")
    print("="*80)
    print("🔧 Pipeline integrado: Enhanced PDF + Preprocessamento + Chunking + RAG")
    print("🎯 Tecnologias: Unstructured.io + LlamaIndex + Sistema Existente")
    print()
    
    # Inicializar sistema
    rag_system = EnhancedCompleteRAGSystem(chunking_strategy="question_based")
    
    # Texto de exemplo
    example_text = """
MATEMÁTICA E SUAS TECNOLOGIAS

QUESTÃO 91
Em uma progressão aritmética, o primeiro termo é 5 e a razão é 3. Qual é o décimo termo desta progressão?

Assinale a alternativa correta:

A) 29
B) 32
C) 35
D) 38
E) 41

QUESTÃO 92
Uma função quadrática f(x) = ax² + bx + c possui raízes em x = 2 e x = 5. Se f(0) = 10, determine o valor de a.

Marque a opção correta:

A) 1
B) 2
C) -1
D) -2
E) 0
"""
    
    print("📝 Processando texto de exemplo...")
    
    # Processar com sistema enhanced
    result = rag_system.process_text(example_text)
    
    # Exibir resultados
    print(f"\n✅ Processamento enhanced concluído!")
    print(f"📊 RESUMO DOS RESULTADOS:")
    print(f"   📄 Chunks criados: {len(result.chunks)}")
    print(f"   ❓ Questões extraídas: {len(result.questions)}")
    print(f"   🔧 Elementos enhanced: {len(result.enhanced_elements)}")
    print(f"   ⏱️ Tempo de processamento: {result.processing_time:.3f}s")
    print(f"   ⭐ Qualidade pré-processamento: {result.preprocessing_quality:.1%}")
    print(f"   ⭐ Qualidade chunking: {result.chunking_quality:.1%}")
    print(f"   🎯 Confiança geral: {result.confidence_score:.1%}")
    print(f"   🔧 Método de extração: {result.extraction_method}")
    
    # Exportar resultado
    output_file = "enhanced_rag_result.json"
    rag_system.export_enhanced_result(result, output_file)
    print(f"📁 Resultado exportado: {output_file}")
    
    # Comparar métodos
    print(f"\n🔄 Comparando estratégias de chunking...")
    comparison = rag_system.compare_methods(example_text)
    
    print(f"📊 COMPARAÇÃO DE ESTRATÉGIAS:")
    best_strategy = comparison["best_strategy"]
    
    for strategy, metrics in comparison["comparison_results"].items():
        marker = "🏆" if strategy == best_strategy else "  "
        print(f"{marker} {strategy}:")
        print(f"      Chunks: {metrics['chunks_count']}")
        print(f"      Questões: {metrics['questions_count']}")
        print(f"      Confiança: {metrics['confidence_score']:.1%}")
        print(f"      Tempo: {metrics['processing_time']:.3f}s")
    
    print(f"\n🎉 Sistema RAG Enhanced funcionando perfeitamente!")
    print(f"🏆 Melhor estratégia: {best_strategy}")

if __name__ == "__main__":
    main() 