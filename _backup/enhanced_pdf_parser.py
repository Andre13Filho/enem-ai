"""
🚀 ENHANCED PDF PARSER - TECNOLOGIAS COMPLEMENTARES
===================================================
Sistema avançado com Unstructured.io e LlamaIndex para PDFs educacionais do ENEM

Funcionalidades:
- Unstructured.io: parsing de documentos complexos
- LlamaIndex: parsers específicos para conteúdo educacional
- Integração com sistema existente
- Fallbacks inteligentes
"""

import logging
import tempfile
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedParsingResult:
    """Resultado do parsing melhorado"""
    content: str
    metadata: Dict[str, Any]
    parsing_method: str
    confidence_score: float
    structured_elements: List[Dict[str, Any]]
    processing_time: float
    error_info: Optional[str] = None

class UnstructuredParser:
    """Parser usando Unstructured.io para documentos complexos"""
    
    def __init__(self):
        self._available = self._check_availability()
        if self._available:
            logger.info("✅ Unstructured.io disponível")
        else:
            logger.warning("⚠️ Unstructured.io não disponível")
    
    def _check_availability(self) -> bool:
        """Verifica se Unstructured.io está disponível"""
        try:
            from unstructured.partition.pdf import partition_pdf
            from unstructured.staging.base import dict_to_elements
            return True
        except ImportError:
            return False
    
    def parse_pdf(self, pdf_path: str) -> EnhancedParsingResult:
        """Parser PDF usando Unstructured.io"""
        start_time = time.time()
        
        if not self._available:
            return EnhancedParsingResult(
                content="",
                metadata={},
                parsing_method="unstructured",
                confidence_score=0.0,
                structured_elements=[],
                processing_time=0.0,
                error_info="Unstructured.io não disponível"
            )
        
        try:
            from unstructured.partition.pdf import partition_pdf
            
            logger.info(f"🔄 Iniciando parsing com Unstructured.io: {pdf_path}")
            
            # Configurações otimizadas para ENEM
            elements = partition_pdf(
                filename=pdf_path,
                strategy="hi_res",  # Alta resolução para textos complexos
                infer_table_structure=True,  # Detectar tabelas
                extract_images_in_pdf=False,  # Focar no texto
                include_page_breaks=True,  # Preservar quebras de página
                chunking_strategy="by_title",  # Agrupar por títulos
                max_characters=4000,  # Chunks otimizados
                new_after_n_chars=3800,  # Quebra preventiva
                overlap=200  # Sobreposição contextual
            )
            
            # Processar elementos estruturados
            structured_elements = []
            content_parts = []
            
            for element in elements:
                element_dict = {
                    "type": str(type(element).__name__),
                    "text": str(element),
                    "metadata": element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                }
                
                # Identificar elementos específicos do ENEM
                text = str(element).strip()
                if text:
                    # Detectar questões
                    if any(pattern in text.upper() for pattern in ["QUESTÃO", "QUESTAO"]):
                        element_dict["enem_type"] = "question_header"
                        element_dict["confidence"] = 0.95
                    
                    # Detectar alternativas
                    elif text.startswith(('A)', 'B)', 'C)', 'D)', 'E)')):
                        element_dict["enem_type"] = "alternative"
                        element_dict["confidence"] = 0.90
                    
                    # Detectar comandos
                    elif any(cmd in text.lower() for cmd in ["assinale", "marque", "indique"]):
                        element_dict["enem_type"] = "command"
                        element_dict["confidence"] = 0.85
                    
                    # Detectar áreas de conhecimento
                    elif "TECNOLOGIAS" in text.upper():
                        element_dict["enem_type"] = "subject_area"
                        element_dict["confidence"] = 0.95
                    
                    structured_elements.append(element_dict)
                    content_parts.append(text)
            
            content = "\n\n".join(content_parts)
            processing_time = time.time() - start_time
            
            # Calcular score de confiança baseado na estrutura
            confidence_score = self._calculate_confidence(structured_elements)
            
            metadata = {
                "total_elements": len(elements),
                "structured_elements": len(structured_elements),
                "has_questions": any(el.get("enem_type") == "question_header" for el in structured_elements),
                "has_alternatives": any(el.get("enem_type") == "alternative" for el in structured_elements),
                "parsing_strategy": "hi_res_chunked"
            }
            
            logger.info(f"✅ Unstructured.io concluído: {len(elements)} elementos em {processing_time:.2f}s")
            
            return EnhancedParsingResult(
                content=content,
                metadata=metadata,
                parsing_method="unstructured",
                confidence_score=confidence_score,
                structured_elements=structured_elements,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Erro no Unstructured.io: {str(e)}")
            
            return EnhancedParsingResult(
                content="",
                metadata={},
                parsing_method="unstructured",
                confidence_score=0.0,
                structured_elements=[],
                processing_time=processing_time,
                error_info=str(e)
            )
    
    def _calculate_confidence(self, elements: List[Dict[str, Any]]) -> float:
        """Calcula confiança baseada na estrutura detectada"""
        if not elements:
            return 0.0
        
        enem_elements = [el for el in elements if "enem_type" in el]
        if not enem_elements:
            return 0.5  # Texto extraído mas sem estrutura ENEM
        
        confidence_sum = sum(el.get("confidence", 0.5) for el in enem_elements)
        return min(confidence_sum / len(elements), 1.0)

class LlamaIndexParser:
    """Parser usando LlamaIndex para PDFs educacionais"""
    
    def __init__(self):
        self._available = self._check_availability()
        if self._available:
            logger.info("✅ LlamaIndex disponível")
        else:
            logger.warning("⚠️ LlamaIndex não disponível")
    
    def _check_availability(self) -> bool:
        """Verifica se LlamaIndex está disponível"""
        try:
            from llama_index.readers.file import PDFReader
            from llama_index.core import Document
            return True
        except ImportError:
            return False
    
    def parse_pdf(self, pdf_path: str) -> EnhancedParsingResult:
        """Parser PDF usando LlamaIndex"""
        start_time = time.time()
        
        if not self._available:
            return EnhancedParsingResult(
                content="",
                metadata={},
                parsing_method="llamaindex",
                confidence_score=0.0,
                structured_elements=[],
                processing_time=0.0,
                error_info="LlamaIndex não disponível"
            )
        
        try:
            from llama_index.readers.file import PDFReader
            from llama_index.core import Document
            
            logger.info(f"🔄 Iniciando parsing com LlamaIndex: {pdf_path}")
            
            # Configurar reader otimizado para conteúdo educacional
            pdf_reader = PDFReader(
                return_full_document=False  # Separar por páginas
            )
            
            # Carregar documento
            documents = pdf_reader.load_data(file=Path(pdf_path))
            
            # Processar documentos
            structured_elements = []
            content_parts = []
            
            for i, doc in enumerate(documents):
                content = doc.text
                metadata = doc.metadata or {}
                
                # Análise específica para ENEM
                enem_analysis = self._analyze_enem_content(content)
                
                element = {
                    "type": "document_page",
                    "text": content,
                    "page_number": i + 1,
                    "metadata": metadata,
                    "enem_analysis": enem_analysis
                }
                
                structured_elements.append(element)
                content_parts.append(content)
            
            full_content = "\n\n".join(content_parts)
            processing_time = time.time() - start_time
            
            # Análise global do documento
            global_analysis = self._global_enem_analysis(structured_elements)
            confidence_score = global_analysis.get("confidence_score", 0.5)
            
            metadata = {
                "total_pages": len(documents),
                "total_characters": len(full_content),
                "enem_analysis": global_analysis,
                "parsing_algorithm": "llamaindex_educational"
            }
            
            logger.info(f"✅ LlamaIndex concluído: {len(documents)} páginas em {processing_time:.2f}s")
            
            return EnhancedParsingResult(
                content=full_content,
                metadata=metadata,
                parsing_method="llamaindex",
                confidence_score=confidence_score,
                structured_elements=structured_elements,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Erro no LlamaIndex: {str(e)}")
            
            return EnhancedParsingResult(
                content="",
                metadata={},
                parsing_method="llamaindex",
                confidence_score=0.0,
                structured_elements=[],
                processing_time=processing_time,
                error_info=str(e)
            )
    
    def _analyze_enem_content(self, content: str) -> Dict[str, Any]:
        """Analisa conteúdo específico do ENEM"""
        analysis = {
            "questions_detected": 0,
            "alternatives_detected": 0,
            "commands_detected": 0,
            "subject_areas": [],
            "confidence_indicators": []
        }
        
        # Detectar questões
        import re
        question_patterns = [
            r'QUESTÃO\s+\d+',
            r'Questão\s+\d+',
            r'\d+\.\s+',
            r'\d+\)\s+'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis["questions_detected"] += len(matches)
            if matches:
                analysis["confidence_indicators"].append(f"question_pattern_{pattern}")
        
        # Detectar alternativas
        alt_patterns = [
            r'[A-E]\)\s+[^\n]+',
            r'\([A-E]\)\s+[^\n]+',
            r'[A-E]\.\s+[^\n]+'
        ]
        
        for pattern in alt_patterns:
            matches = re.findall(pattern, content)
            analysis["alternatives_detected"] += len(matches)
            if matches:
                analysis["confidence_indicators"].append(f"alternative_pattern")
        
        # Detectar comandos
        command_patterns = [
            r'assinale\s+a\s+alternativa',
            r'marque\s+a\s+opção',
            r'indique\s+a\s+alternativa'
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis["commands_detected"] += len(matches)
            if matches:
                analysis["confidence_indicators"].append(f"command_pattern")
        
        # Detectar áreas de conhecimento
        subject_areas = [
            "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS",
            "MATEMÁTICA E SUAS TECNOLOGIAS",
            "CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS",
            "CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS"
        ]
        
        for area in subject_areas:
            if area in content.upper():
                analysis["subject_areas"].append(area)
                analysis["confidence_indicators"].append("subject_area_detected")
        
        return analysis
    
    def _global_enem_analysis(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Análise global do documento ENEM"""
        total_questions = sum(el["enem_analysis"]["questions_detected"] for el in elements)
        total_alternatives = sum(el["enem_analysis"]["alternatives_detected"] for el in elements)
        total_commands = sum(el["enem_analysis"]["commands_detected"] for el in elements)
        
        all_subject_areas = []
        for el in elements:
            all_subject_areas.extend(el["enem_analysis"]["subject_areas"])
        
        unique_subject_areas = list(set(all_subject_areas))
        
        # Calcular confiança baseada na estrutura
        confidence_score = 0.0
        
        if total_questions > 0:
            confidence_score += 0.3
        if total_alternatives > 0:
            confidence_score += 0.3
        if total_commands > 0:
            confidence_score += 0.2
        if unique_subject_areas:
            confidence_score += 0.2
        
        # Bonus para estrutura bem formada
        if total_questions > 0 and total_alternatives > 0:
            expected_alternatives = total_questions * 5  # 5 alternativas por questão
            ratio = min(total_alternatives / expected_alternatives, 1.0) if expected_alternatives > 0 else 0
            confidence_score += ratio * 0.1
        
        return {
            "total_questions": total_questions,
            "total_alternatives": total_alternatives,
            "total_commands": total_commands,
            "subject_areas": unique_subject_areas,
            "confidence_score": min(confidence_score, 1.0),
            "structure_quality": "good" if confidence_score > 0.7 else "medium" if confidence_score > 0.4 else "poor"
        }

class EnhancedPDFParser:
    """Parser principal integrando todas as tecnologias"""
    
    def __init__(self):
        self.unstructured = UnstructuredParser()
        self.llamaindex = LlamaIndexParser()
        logger.info("✅ Enhanced PDF Parser inicializado")
    
    def parse_pdf(self, pdf_path: str, preferred_method: str = "auto") -> EnhancedParsingResult:
        """
        Parser PDF com múltiplas tecnologias
        
        Args:
            pdf_path: Caminho para o PDF
            preferred_method: 'auto', 'unstructured', 'llamaindex', 'all'
        """
        
        if not os.path.exists(pdf_path):
            return EnhancedParsingResult(
                content="",
                metadata={},
                parsing_method="none",
                confidence_score=0.0,
                structured_elements=[],
                processing_time=0.0,
                error_info="Arquivo não encontrado"
            )
        
        logger.info(f"🚀 Iniciando parsing melhorado: {pdf_path}")
        
        results = []
        
        if preferred_method in ["auto", "unstructured", "all"]:
            result = self.unstructured.parse_pdf(pdf_path)
            if result.confidence_score > 0:
                results.append(result)
        
        if preferred_method in ["auto", "llamaindex", "all"]:
            result = self.llamaindex.parse_pdf(pdf_path)
            if result.confidence_score > 0:
                results.append(result)
        
        if not results:
            return EnhancedParsingResult(
                content="",
                metadata={},
                parsing_method="none",
                confidence_score=0.0,
                structured_elements=[],
                processing_time=0.0,
                error_info="Nenhuma tecnologia disponível"
            )
        
        # Selecionar melhor resultado ou combinar
        if preferred_method == "all":
            return self._combine_results(results)
        else:
            return max(results, key=lambda x: x.confidence_score)
    
    def _combine_results(self, results: List[EnhancedParsingResult]) -> EnhancedParsingResult:
        """Combina resultados de múltiplas tecnologias"""
        if not results:
            return EnhancedParsingResult(
                content="",
                metadata={},
                parsing_method="combined",
                confidence_score=0.0,
                structured_elements=[],
                processing_time=0.0
            )
        
        # Combinar conteúdo
        contents = [r.content for r in results if r.content]
        combined_content = "\n\n--- COMBINED PARSING ---\n\n".join(contents)
        
        # Combinar elementos estruturados
        all_elements = []
        for result in results:
            for element in result.structured_elements:
                element["source_method"] = result.parsing_method
                all_elements.append(element)
        
        # Combinar metadata
        combined_metadata = {
            "parsing_methods": [r.parsing_method for r in results],
            "individual_confidences": [r.confidence_score for r in results],
            "processing_times": [r.processing_time for r in results]
        }
        
        # Calcular confiança combinada
        confidence_scores = [r.confidence_score for r in results if r.confidence_score > 0]
        combined_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        # Tempo total
        total_time = sum(r.processing_time for r in results)
        
        return EnhancedParsingResult(
            content=combined_content,
            metadata=combined_metadata,
            parsing_method="combined",
            confidence_score=combined_confidence,
            structured_elements=all_elements,
            processing_time=total_time
        )
    
    def export_result(self, result: EnhancedParsingResult, output_path: str):
        """Exporta resultado para JSON"""
        export_data = {
            "parsing_result": {
                "method": result.parsing_method,
                "confidence_score": result.confidence_score,
                "processing_time": result.processing_time,
                "content_length": len(result.content),
                "structured_elements_count": len(result.structured_elements)
            },
            "metadata": result.metadata,
            "content": result.content,
            "structured_elements": result.structured_elements,
            "error_info": result.error_info
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Resultado exportado: {output_path}")

# Função de demonstração
def main():
    """Demonstração do Enhanced PDF Parser"""
    print("🚀 ENHANCED PDF PARSER - DEMONSTRAÇÃO")
    print("="*70)
    print("🔧 Tecnologias: Unstructured.io + LlamaIndex")
    print("🎯 Especializado em PDFs educacionais do ENEM")
    print()
    
    parser = EnhancedPDFParser()
    
    # Exemplo com arquivo fictício
    example_path = "exemplo_enem.pdf"
    print(f"📄 Exemplo de uso com: {example_path}")
    print()
    
    # Testar diferentes métodos
    methods = ["unstructured", "llamaindex", "all"]
    
    for method in methods:
        print(f"🔍 Testando método: {method}")
        result = parser.parse_pdf(example_path, preferred_method=method)
        
        print(f"   📊 Confiança: {result.confidence_score:.2f}")
        print(f"   ⏱️ Tempo: {result.processing_time:.3f}s")
        print(f"   📝 Elementos: {len(result.structured_elements)}")
        
        if result.error_info:
            print(f"   ⚠️ Erro: {result.error_info}")
        
        print()
    
    print("✅ Demonstração concluída!")
    print("🎉 Enhanced PDF Parser pronto para uso!")

if __name__ == "__main__":
    main() 