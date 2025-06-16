#!/usr/bin/env python3
"""
Sistema Integrado: Extração Avançada + Pré-processamento Estruturado
Combina o melhor dos dois mundos para processamento completo do ENEM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List, Any, Optional
import json
import logging
from dataclasses import dataclass
from datetime import datetime

# Imports dos sistemas desenvolvidos
try:
    from advanced_pdf_extractor import AdvancedPDFExtractor, TextBlock
    from enem_text_preprocessor import ENEMTextPreprocessor, ENEMPattern
    from improved_exercise_parser import ImprovedExerciseParser
except ImportError as e:
    print(f"⚠️ Aviso: {e}")
    print("📝 Alguns módulos podem não estar disponíveis")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedQuestion:
    """Questão processada com todas as informações estruturadas"""
    question_number: Optional[int]
    original_text: str
    cleaned_text: str
    alternatives: List[Dict[str, Any]]
    commands: List[str]
    subject_area: Optional[str]
    confidence_score: float
    extraction_method: str
    patterns_found: List[str]
    metadata: Dict[str, Any]

class IntegratedENEMProcessor:
    """
    Sistema integrado que combina:
    1. Extração avançada de PDF
    2. Pré-processamento estruturado com regex
    3. Parser melhorado para exercícios
    """
    
    def __init__(self):
        self.pdf_extractor = None
        self.text_preprocessor = None
        self.exercise_parser = None
        
        # Inicializa componentes disponíveis
        self._initialize_components()
        
        self.processing_stats = {
            "total_processed": 0,
            "extraction_methods_used": {},
            "patterns_identified": {},
            "quality_scores": []
        }
    
    def _initialize_components(self):
        """Inicializa componentes do sistema"""
        try:
            self.pdf_extractor = AdvancedPDFExtractor()
            logger.info("✅ Extrator avançado de PDF carregado")
        except:
            logger.warning("⚠️ Extrator avançado de PDF não disponível")
        
        try:
            self.text_preprocessor = ENEMTextPreprocessor()
            logger.info("✅ Pré-processador estruturado carregado")
        except:
            logger.warning("⚠️ Pré-processador estruturado não disponível")
        
        try:
            self.exercise_parser = ImprovedExerciseParser()
            logger.info("✅ Parser melhorado carregado")
        except:
            logger.warning("⚠️ Parser melhorado não disponível")
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Processa PDF completo com pipeline integrado
        """
        logger.info(f"🔄 Iniciando processamento integrado: {pdf_path}")
        
        results = {
            "source_file": pdf_path,
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_results": None,
            "structured_questions": [],
            "global_stats": {},
            "quality_metrics": {}
        }
        
        # Etapa 1: Extração avançada de PDF
        if self.pdf_extractor:
            extraction_results = self._extract_with_advanced_methods(pdf_path)
            results["extraction_results"] = extraction_results
            text_blocks = extraction_results.get("text_blocks", [])
        else:
            # Fallback para extração básica
            text_blocks = self._basic_pdf_extraction(pdf_path)
        
        # Etapa 2: Processamento estruturado de cada bloco
        for block in text_blocks:
            if self._is_question_block(block):
                processed_question = self._process_question_block(block)
                if processed_question:
                    results["structured_questions"].append(processed_question)
        
        # Etapa 3: Análise global e métricas
        results["global_stats"] = self._calculate_global_stats(results["structured_questions"])
        results["quality_metrics"] = self._calculate_quality_metrics(results["structured_questions"])
        
        # Atualiza estatísticas
        self._update_processing_stats(results)
        
        logger.info(f"✅ Processamento concluído: {len(results['structured_questions'])} questões estruturadas")
        
        return results
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Processa texto diretamente com pipeline estruturado
        """
        logger.info("🔄 Processando texto com pipeline estruturado")
        
        # Etapa 1: Pré-processamento estruturado
        if self.text_preprocessor:
            preprocessing_result = self.text_preprocessor.preprocess_text(text)
        else:
            preprocessing_result = {"cleaned_text": text, "patterns": [], "stats": {}}
        
        # Etapa 2: Parser melhorado
        structured_questions = []
        if self.exercise_parser:
            try:
                parsed_exercises = self.exercise_parser.parse_text(preprocessing_result["cleaned_text"])
                for exercise in parsed_exercises:
                    structured_question = self._convert_to_processed_question(
                        exercise, preprocessing_result, "text_direct"
                    )
                    structured_questions.append(structured_question)
            except Exception as e:
                logger.warning(f"Erro no parser: {e}")
        
        # Etapa 3: Análise estrutural direta
        if not structured_questions and preprocessing_result.get("structured_content"):
            for question_data in preprocessing_result["structured_content"].get("questions", []):
                structured_question = self._convert_from_preprocessor(question_data, text)
                structured_questions.append(structured_question)
        
        return {
            "source_type": "text_direct",
            "processing_timestamp": datetime.now().isoformat(),
            "preprocessing_result": preprocessing_result,
            "structured_questions": structured_questions,
            "global_stats": self._calculate_global_stats(structured_questions),
            "quality_metrics": self._calculate_quality_metrics(structured_questions)
        }
    
    def _extract_with_advanced_methods(self, pdf_path: str) -> Dict[str, Any]:
        """Extração usando métodos avançados"""
        try:
            return self.pdf_extractor.extract_pdf(pdf_path)
        except Exception as e:
            logger.error(f"Erro na extração avançada: {e}")
            return {"text_blocks": [], "error": str(e)}
    
    def _basic_pdf_extraction(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extração básica como fallback"""
        try:
            import PyPDF2
            text_blocks = []
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_blocks.append({
                            "text": text,
                            "page": page_num + 1,
                            "confidence": 0.7,
                            "extraction_method": "basic_pypdf2"
                        })
            
            return text_blocks
        except Exception as e:
            logger.error(f"Erro na extração básica: {e}")
            return []
    
    def _is_question_block(self, block) -> bool:
        """Verifica se bloco contém uma questão"""
        if isinstance(block, dict):
            text = block.get("text", "")
        else:
            text = str(block)
        
        # Verifica padrões de questão
        question_indicators = [
            r'(?i)questão\s+\d+',
            r'^\d+\s*[\.\)]\s*',
            r'(?i)assinale\s+a\s+alternativa',
            r'[A-E]\)\s*.{10,}'
        ]
        
        import re
        for pattern in question_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _process_question_block(self, block) -> Optional[ProcessedQuestion]:
        """Processa um bloco identificado como questão"""
        try:
            if isinstance(block, dict):
                text = block.get("text", "")
                extraction_method = block.get("extraction_method", "unknown")
            else:
                text = str(block)
                extraction_method = "direct_text"
            
            # Aplica pré-processamento estruturado
            if self.text_preprocessor:
                preprocessing_result = self.text_preprocessor.preprocess_text(text)
            else:
                preprocessing_result = {
                    "cleaned_text": text,
                    "patterns": [],
                    "structured_content": {"questions": []},
                    "stats": {}
                }
            
            # Extrai informações estruturadas
            question_info = self._extract_question_info(preprocessing_result)
            
            # Cria objeto ProcessedQuestion
            processed_question = ProcessedQuestion(
                question_number=question_info.get("number"),
                original_text=text,
                cleaned_text=preprocessing_result["cleaned_text"],
                alternatives=question_info.get("alternatives", []),
                commands=question_info.get("commands", []),
                subject_area=question_info.get("subject_area"),
                confidence_score=question_info.get("confidence", 0.5),
                extraction_method=extraction_method,
                patterns_found=[p.pattern_type.value for p in preprocessing_result["patterns"]],
                metadata={
                    "preprocessing_stats": preprocessing_result["stats"],
                    "block_info": block if isinstance(block, dict) else {}
                }
            )
            
            return processed_question
            
        except Exception as e:
            logger.error(f"Erro ao processar bloco de questão: {e}")
            return None
    
    def _extract_question_info(self, preprocessing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai informações estruturadas da questão"""
        info = {
            "number": None,
            "alternatives": [],
            "commands": [],
            "subject_area": None,
            "confidence": 0.5
        }
        
        patterns = preprocessing_result.get("patterns", [])
        
        # Extrai número da questão
        for pattern in patterns:
            if pattern.pattern_type.value == "question_number":
                info["number"] = pattern.metadata.get("question_number")
                break
        
        # Extrai alternativas
        for pattern in patterns:
            if pattern.pattern_type.value == "alternative":
                info["alternatives"].append({
                    "letter": pattern.metadata.get("letter"),
                    "content": pattern.metadata.get("content"),
                    "confidence": pattern.confidence
                })
        
        # Extrai comandos
        for pattern in patterns:
            if pattern.pattern_type.value == "command":
                info["commands"].append(pattern.text)
        
        # Extrai área de conhecimento
        for pattern in patterns:
            if pattern.pattern_type.value == "subject_area":
                info["subject_area"] = pattern.metadata.get("subject")
                break
        
        # Calcula confiança
        if patterns:
            info["confidence"] = sum(p.confidence for p in patterns) / len(patterns)
        
        return info
    
    def _convert_to_processed_question(self, exercise, preprocessing_result, method) -> ProcessedQuestion:
        """Converte exercício parseado para ProcessedQuestion"""
        return ProcessedQuestion(
            question_number=getattr(exercise, 'id_questao', None),
            original_text=getattr(exercise, 'enunciado', ''),
            cleaned_text=preprocessing_result["cleaned_text"],
            alternatives=[{
                "letter": alt.letra,
                "content": alt.texto,
                "confidence": alt.confidence
            } for alt in getattr(exercise, 'alternativas', [])],
            commands=[],
            subject_area=getattr(exercise, 'area_conhecimento', None),
            confidence_score=getattr(exercise, 'confidence', 0.5),
            extraction_method=method,
            patterns_found=[p.pattern_type.value for p in preprocessing_result["patterns"]],
            metadata={
                "topico": getattr(exercise, 'topico_relevante', None),
                "habilidade": getattr(exercise, 'habilidade_associada', None)
            }
        )
    
    def _convert_from_preprocessor(self, question_data: Dict, original_text: str) -> ProcessedQuestion:
        """Converte dados do preprocessor para ProcessedQuestion"""
        return ProcessedQuestion(
            question_number=question_data.get("number"),
            original_text=original_text,
            cleaned_text=original_text,
            alternatives=question_data.get("alternatives", []),
            commands=question_data.get("commands", []),
            subject_area=None,
            confidence_score=question_data.get("confidence", 0.5),
            extraction_method="preprocessor_direct",
            patterns_found=["question_number", "alternative"] if question_data.get("alternatives") else [],
            metadata=question_data
        )
    
    def _calculate_global_stats(self, questions: List[ProcessedQuestion]) -> Dict[str, Any]:
        """Calcula estatísticas globais do processamento"""
        if not questions:
            return {}
        
        return {
            "total_questions": len(questions),
            "questions_with_number": sum(1 for q in questions if q.question_number),
            "questions_with_alternatives": sum(1 for q in questions if q.alternatives),
            "avg_alternatives_per_question": sum(len(q.alternatives) for q in questions) / len(questions),
            "avg_confidence": sum(q.confidence_score for q in questions) / len(questions),
            "extraction_methods": list(set(q.extraction_method for q in questions)),
            "subjects_identified": list(set(q.subject_area for q in questions if q.subject_area))
        }
    
    def _calculate_quality_metrics(self, questions: List[ProcessedQuestion]) -> Dict[str, Any]:
        """Calcula métricas de qualidade"""
        if not questions:
            return {}
        
        high_confidence = sum(1 for q in questions if q.confidence_score > 0.8)
        complete_questions = sum(1 for q in questions 
                               if q.question_number and len(q.alternatives) >= 4)
        
        return {
            "high_confidence_questions": high_confidence,
            "high_confidence_percentage": high_confidence / len(questions) * 100,
            "complete_questions": complete_questions,
            "complete_questions_percentage": complete_questions / len(questions) * 100,
            "quality_score": (high_confidence + complete_questions) / (2 * len(questions)) * 100
        }
    
    def _update_processing_stats(self, results: Dict[str, Any]):
        """Atualiza estatísticas de processamento"""
        self.processing_stats["total_processed"] += 1
        
        # Atualiza métodos de extração
        for question in results.get("structured_questions", []):
            method = question.extraction_method
            self.processing_stats["extraction_methods_used"][method] = \
                self.processing_stats["extraction_methods_used"].get(method, 0) + 1
        
        # Atualiza padrões identificados
        for question in results.get("structured_questions", []):
            for pattern in question.patterns_found:
                self.processing_stats["patterns_identified"][pattern] = \
                    self.processing_stats["patterns_identified"].get(pattern, 0) + 1
        
        # Atualiza scores de qualidade
        quality_score = results.get("quality_metrics", {}).get("quality_score", 0)
        self.processing_stats["quality_scores"].append(quality_score)
    
    def export_results(self, results: Dict[str, Any], output_path: str):
        """Exporta resultados estruturados"""
        # Converte ProcessedQuestion para dict para serialização JSON
        serializable_results = results.copy()
        serializable_results["structured_questions"] = [
            {
                "question_number": q.question_number,
                "original_text": q.original_text,
                "cleaned_text": q.cleaned_text,
                "alternatives": q.alternatives,
                "commands": q.commands,
                "subject_area": q.subject_area,
                "confidence_score": q.confidence_score,
                "extraction_method": q.extraction_method,
                "patterns_found": q.patterns_found,
                "metadata": q.metadata
            } for q in results.get("structured_questions", [])
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 Resultados exportados para: {output_path}")
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Retorna resumo do processamento"""
        avg_quality = sum(self.processing_stats["quality_scores"]) / len(self.processing_stats["quality_scores"]) if self.processing_stats["quality_scores"] else 0
        
        return {
            "total_files_processed": self.processing_stats["total_processed"],
            "extraction_methods_used": self.processing_stats["extraction_methods_used"],
            "patterns_identified": self.processing_stats["patterns_identified"],
            "average_quality_score": avg_quality,
            "system_components": {
                "pdf_extractor_available": self.pdf_extractor is not None,
                "text_preprocessor_available": self.text_preprocessor is not None,
                "exercise_parser_available": self.exercise_parser is not None
            }
        }

# Função principal de conveniência
def process_enem_content(source, output_path=None):
    """
    Função principal para processar conteúdo do ENEM
    
    Args:
        source: Caminho do PDF ou texto direto
        output_path: Caminho para salvar resultados (opcional)
    
    Returns:
        Dict com resultados estruturados
    """
    processor = IntegratedENEMProcessor()
    
    if os.path.isfile(source) and source.endswith('.pdf'):
        results = processor.process_pdf(source)
    else:
        results = processor.process_text(source)
    
    if output_path:
        processor.export_results(results, output_path)
    
    return results

if __name__ == "__main__":
    # Demonstração do sistema integrado
    print("🚀 SISTEMA INTEGRADO DE PROCESSAMENTO DO ENEM")
    print("=" * 60)
    
    # Teste com texto de exemplo
    sample_text = """
    QUESTÃO 91
    
    Muitas pessoas ainda se espantam com o fato de um passageiro sair ileso de um 
    acidente de carro enquanto o veículo onde estava teve perda total.
    
    Assinale a alternativa correta sobre o cinto de segurança:
    
    A) acionar os airbags do veículo.
    B) absorver a energia cinética do sistema.
    C) reduzir a velocidade do veículo.
    D) aumentar o tempo de colisão.
    E) diminuir a força média de impacto.
    """
    
    print("📝 Processando texto de exemplo...")
    results = process_enem_content(sample_text)
    
    print(f"✅ Processamento concluído!")
    print(f"📊 Questões estruturadas: {len(results['structured_questions'])}")
    print(f"📈 Score de qualidade: {results['quality_metrics'].get('quality_score', 0):.1f}%")
    
    if results['structured_questions']:
        question = results['structured_questions'][0]
        print(f"\n📝 Questão {question.question_number}:")
        print(f"   🔤 Alternativas: {len(question.alternatives)}")
        print(f"   📋 Comandos: {len(question.commands)}")
        print(f"   📊 Confiança: {question.confidence_score:.1%}")
        print(f"   🔍 Padrões: {question.patterns_found}")
    
    print("\n🎉 Sistema integrado funcionando corretamente!") 