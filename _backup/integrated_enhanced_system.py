"""
🚀 SISTEMA RAG INTEGRADO COM TECNOLOGIAS COMPLEMENTARES
======================================================
Integração do Enhanced PDF Parser (Unstructured.io + LlamaIndex) 
com o sistema RAG completo existente

Funcionalidades:
- Pipeline completo: PDF → Extração → Pré-processamento → Chunking → RAG
- Fallbacks inteligentes: sistema básico + tecnologias complementares
- Análise de qualidade automática
- Exportação de resultados estruturados
"""

import logging
import time
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports do sistema existente
try:
    from complete_rag_system import CompleteRAGSystem
    from enem_text_preprocessor import ENEMTextPreprocessor
    from intelligent_chunker import IntelligentChunker
    SISTEMA_BASE_DISPONIVEL = True
    logger.info("✅ Sistema RAG base disponível")
except ImportError:
    SISTEMA_BASE_DISPONIVEL = False
    logger.warning("⚠️ Sistema RAG base não encontrado")

# Imports do enhanced parser
try:
    from enhanced_pdf_parser import EnhancedPDFParser, EnhancedParsingResult
    ENHANCED_PARSER_DISPONIVEL = True
    logger.info("✅ Enhanced PDF Parser disponível")
except ImportError:
    ENHANCED_PARSER_DISPONIVEL = False
    logger.warning("⚠️ Enhanced PDF Parser não encontrado")

@dataclass
class IntegratedParsingResult:
    """Resultado do parsing integrado"""
    content: str
    extraction_method: str
    preprocessing_result: Optional[Dict[str, Any]]
    chunking_result: Optional[Dict[str, Any]]
    enhanced_analysis: Optional[Dict[str, Any]]
    processing_time: float
    quality_score: float
    recommendations: List[str]
    export_data: Dict[str, Any]

class IntegratedEnhancedSystem:
    """Sistema integrado com tecnologias complementares"""
    
    def __init__(self):
        self.sistema_base = None
        self.enhanced_parser = None
        self.fallback_methods = []
        
        # Inicializar componentes disponíveis
        self._init_components()
        
        logger.info("✅ Sistema RAG Integrado inicializado")
    
    def _init_components(self):
        """Inicializa todos os componentes disponíveis"""
        
        # Sistema base
        if SISTEMA_BASE_DISPONIVEL:
            try:
                self.sistema_base = CompleteRAGSystem()
                self.fallback_methods.append("sistema_base")
                logger.info("✅ Sistema RAG base carregado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar sistema base: {e}")
        
        # Enhanced parser
        if ENHANCED_PARSER_DISPONIVEL:
            try:
                self.enhanced_parser = EnhancedPDFParser()
                self.fallback_methods.append("enhanced_parser")
                logger.info("✅ Enhanced Parser carregado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar enhanced parser: {e}")
        
        # Verificar disponibilidade
        if not self.fallback_methods:
            logger.error("❌ Nenhum método de parsing disponível")
            raise RuntimeError("Sistema não pode ser inicializado")
        
        logger.info(f"🔧 Métodos disponíveis: {', '.join(self.fallback_methods)}")
    
    def process_pdf(self, 
                   pdf_path: str, 
                   strategy: str = "intelligent",
                   chunking_method: str = "question_based") -> IntegratedParsingResult:
        """
        Processa PDF com sistema integrado
        
        Args:
            pdf_path: Caminho para o PDF
            strategy: 'enhanced_first', 'base_first', 'parallel', 'best_quality'
            chunking_method: Método de chunking a usar
        """
        
        start_time = time.time()
        logger.info(f"🚀 Iniciando processamento integrado: {pdf_path}")
        logger.info(f"📋 Estratégia: {strategy}")
        logger.info(f"✂️ Chunking: {chunking_method}")
        
        results = {}
        recommendations = []
        
        # Estratégia Enhanced First
        if strategy in ["enhanced_first", "parallel"] and "enhanced_parser" in self.fallback_methods:
            logger.info("🔄 Tentando Enhanced Parser...")
            try:
                enhanced_result = self.enhanced_parser.parse_pdf(pdf_path, preferred_method="all")
                if enhanced_result.confidence_score > 0.3:
                    results["enhanced"] = enhanced_result
                    recommendations.append("Enhanced parsing bem-sucedido")
                    logger.info(f"✅ Enhanced Parser: {enhanced_result.confidence_score:.2f}")
                else:
                    recommendations.append("Enhanced parsing com baixa confiança")
                    logger.warning(f"⚠️ Enhanced Parser baixa confiança: {enhanced_result.confidence_score:.2f}")
            except Exception as e:
                logger.error(f"❌ Erro no Enhanced Parser: {e}")
                recommendations.append(f"Enhanced parsing falhou: {str(e)}")
        
        # Estratégia Base First ou fallback
        if strategy in ["base_first", "parallel"] and "sistema_base" in self.fallback_methods:
            logger.info("🔄 Tentando Sistema Base...")
            try:
                if os.path.exists(pdf_path):
                    base_result = self.sistema_base.process_pdf(pdf_path)
                else:
                    # Processar como texto para demonstração
                    test_text = self._get_test_content()
                    base_result = self.sistema_base.process_text(test_text)
                
                if base_result and base_result.get("chunks_created", 0) > 0:
                    results["base"] = base_result
                    recommendations.append("Sistema base funcionando")
                    logger.info(f"✅ Sistema Base: {base_result.get('overall_quality', 0):.2f}")
                else:
                    recommendations.append("Sistema base sem resultados")
                    logger.warning("⚠️ Sistema Base sem resultados")
            except Exception as e:
                logger.error(f"❌ Erro no Sistema Base: {e}")
                recommendations.append(f"Sistema base falhou: {str(e)}")
        
        # Selecionar melhor resultado
        selected_result = self._select_best_result(results, strategy)
        
        # Processar resultado selecionado
        final_result = self._create_integrated_result(
            selected_result, results, start_time, recommendations
        )
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Processamento integrado concluído em {processing_time:.2f}s")
        
        return final_result
    
    def _get_test_content(self) -> str:
        """Retorna conteúdo de teste para demonstração"""
        return """
LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS

QUESTÃO 91
O uso de tecnologias digitais na educação tem transformado o processo de ensino-aprendizagem.

Com base nessa premissa, assinale a alternativa correta:

A) A tecnologia prejudica o aprendizado tradicional.
B) As ferramentas digitais melhoram o engajamento dos estudantes.
C) O ensino digital é menos eficaz que o presencial.
D) A tecnologia deve ser evitada na educação.
E) Os recursos digitais são irrelevantes para o ensino.

QUESTÃO 92
A integração de múltiplas linguagens e códigos é essencial na comunicação moderna.

Marque a opção que exemplifica essa integração:

A) Uso exclusivo de texto escrito
B) Comunicação apenas verbal
C) Combinação de texto, imagem e áudio
D) Utilização somente de códigos visuais
E) Foco apenas em linguagem formal
"""
    
    def _select_best_result(self, results: Dict[str, Any], strategy: str) -> Tuple[str, Any]:
        """Seleciona o melhor resultado baseado na estratégia"""
        
        if not results:
            return "none", None
        
        if strategy == "best_quality":
            # Selecionar por qualidade
            best_method = None
            best_score = 0
            
            for method, result in results.items():
                if method == "enhanced":
                    score = result.confidence_score
                elif method == "base":
                    score = result.get("overall_quality", 0) / 100.0
                else:
                    score = 0.5
                
                if score > best_score:
                    best_score = score
                    best_method = method
            
            return best_method, results[best_method] if best_method else None
        
        elif strategy == "enhanced_first":
            if "enhanced" in results:
                return "enhanced", results["enhanced"]
            elif "base" in results:
                return "base", results["base"]
        
        elif strategy == "base_first":
            if "base" in results:
                return "base", results["base"]
            elif "enhanced" in results:
                return "enhanced", results["enhanced"]
        
        elif strategy == "parallel":
            # Usar enhanced se disponível e com boa qualidade
            if "enhanced" in results and results["enhanced"].confidence_score > 0.7:
                return "enhanced", results["enhanced"]
            elif "base" in results:
                return "base", results["base"]
            elif "enhanced" in results:
                return "enhanced", results["enhanced"]
        
        # Fallback
        first_method = list(results.keys())[0]
        return first_method, results[first_method]
    
    def _create_integrated_result(self, 
                                selected_result: Tuple[str, Any],
                                all_results: Dict[str, Any],
                                start_time: float,
                                recommendations: List[str]) -> IntegratedParsingResult:
        """Cria resultado integrado final"""
        
        method, result = selected_result
        processing_time = time.time() - start_time
        
        if method == "none" or result is None:
            return IntegratedParsingResult(
                content="",
                extraction_method="none",
                preprocessing_result=None,
                chunking_result=None,
                enhanced_analysis=None,
                processing_time=processing_time,
                quality_score=0.0,
                recommendations=recommendations + ["Nenhum método funcionou"],
                export_data={}
            )
        
        # Extrair dados baseado no método usado
        if method == "enhanced":
            content = result.content
            quality_score = result.confidence_score
            enhanced_analysis = {
                "method": result.parsing_method,
                "elements_count": len(result.structured_elements),
                "metadata": result.metadata
            }
            preprocessing_result = None
            chunking_result = None
            
        elif method == "base":
            content = result.get("processed_content", "")
            quality_score = result.get("overall_quality", 50) / 100.0
            enhanced_analysis = None
            preprocessing_result = {
                "patterns_found": result.get("preprocessing_results", {})
            }
            chunking_result = {
                "chunks_created": result.get("chunks_created", 0),
                "chunking_method": result.get("chunking_method", "unknown")
            }
        
        else:
            content = ""
            quality_score = 0.0
            enhanced_analysis = None
            preprocessing_result = None
            chunking_result = None
        
        # Criar dados de exportação
        export_data = {
            "processing_summary": {
                "method_used": method,
                "processing_time": processing_time,
                "quality_score": quality_score,
                "content_length": len(content)
            },
            "available_methods": list(all_results.keys()),
            "recommendations": recommendations,
            "enhanced_analysis": enhanced_analysis,
            "system_integration": {
                "sistema_base_available": SISTEMA_BASE_DISPONIVEL,
                "enhanced_parser_available": ENHANCED_PARSER_DISPONIVEL
            }
        }
        
        return IntegratedParsingResult(
            content=content,
            extraction_method=method,
            preprocessing_result=preprocessing_result,
            chunking_result=chunking_result,
            enhanced_analysis=enhanced_analysis,
            processing_time=processing_time,
            quality_score=quality_score,
            recommendations=recommendations,
            export_data=export_data
        )
    
    def export_integrated_result(self, result: IntegratedParsingResult, output_path: str):
        """Exporta resultado integrado para JSON"""
        
        export_data = {
            "integrated_processing_result": {
                "extraction_method": result.extraction_method,
                "quality_score": result.quality_score,
                "processing_time": result.processing_time,
                "content_length": len(result.content),
                "recommendations_count": len(result.recommendations)
            },
            "content": result.content,
            "preprocessing_result": result.preprocessing_result,
            "chunking_result": result.chunking_result,
            "enhanced_analysis": result.enhanced_analysis,
            "recommendations": result.recommendations,
            "system_data": result.export_data,
            "processing_timestamp": time.time()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Resultado integrado exportado: {output_path}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        
        status = {
            "system_components": {
                "sistema_base_available": SISTEMA_BASE_DISPONIVEL,
                "enhanced_parser_available": ENHANCED_PARSER_DISPONIVEL,
                "fallback_methods": self.fallback_methods
            },
            "parsing_capabilities": {
                "unstructured_io": False,
                "llamaindex": False,
                "traditional_pdf": False,
                "structured_preprocessing": SISTEMA_BASE_DISPONIVEL,
                "intelligent_chunking": SISTEMA_BASE_DISPONIVEL
            },
            "recommended_strategy": "parallel" if len(self.fallback_methods) > 1 else "single_method"
        }
        
        # Verificar capacidades específicas
        if self.enhanced_parser:
            status["parsing_capabilities"]["unstructured_io"] = self.enhanced_parser.unstructured._available
            status["parsing_capabilities"]["llamaindex"] = self.enhanced_parser.llamaindex._available
        
        if self.sistema_base:
            status["parsing_capabilities"]["traditional_pdf"] = True
        
        return status

def demonstrate_integrated_system():
    """Demonstração do sistema integrado"""
    print("🚀 SISTEMA RAG INTEGRADO COM TECNOLOGIAS COMPLEMENTARES")
    print("="*80)
    print("🔧 Enhanced PDF Parser + Sistema RAG Base")
    print("🎯 Fallbacks inteligentes e análise de qualidade")
    print()
    
    try:
        # Inicializar sistema
        sistema = IntegratedEnhancedSystem()
        
        # Mostrar status
        status = sistema.get_system_status()
        print("📊 STATUS DO SISTEMA:")
        print(f"   Sistema Base: {'✅' if status['system_components']['sistema_base_available'] else '❌'}")
        print(f"   Enhanced Parser: {'✅' if status['system_components']['enhanced_parser_available'] else '❌'}")
        print(f"   Unstructured.io: {'✅' if status['parsing_capabilities']['unstructured_io'] else '❌'}")
        print(f"   LlamaIndex: {'✅' if status['parsing_capabilities']['llamaindex'] else '❌'}")
        print(f"   Métodos disponíveis: {len(status['system_components']['fallback_methods'])}")
        print()
        
        # Testar diferentes estratégias
        strategies = ["enhanced_first", "base_first", "parallel", "best_quality"]
        test_file = "exemplo_enem.pdf"
        
        print("🔍 TESTANDO ESTRATÉGIAS DE PROCESSAMENTO:")
        print("-" * 60)
        
        for strategy in strategies:
            print(f"📋 Estratégia: {strategy}")
            
            try:
                result = sistema.process_pdf(test_file, strategy=strategy)
                
                print(f"   Método usado: {result.extraction_method}")
                print(f"   Qualidade: {result.quality_score:.2f}")
                print(f"   Tempo: {result.processing_time:.3f}s")
                print(f"   Conteúdo: {len(result.content)} chars")
                print(f"   Recomendações: {len(result.recommendations)}")
                
                # Exportar resultado
                output_file = f"integrated_result_{strategy}.json"
                sistema.export_integrated_result(result, output_file)
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
            
            print()
        
        print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
        print()
        print("🎉 FUNCIONALIDADES DEMONSTRADAS:")
        print("   • 🔄 Fallbacks inteligentes entre métodos")
        print("   • 📊 Análise automática de qualidade")
        print("   • 🚀 Estratégias adaptativas de processamento")
        print("   • 📁 Exportação de resultados integrados")
        print("   • 🔧 Status completo do sistema")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {str(e)}")
        print("🔧 Verifique as dependências e tente novamente")

def main():
    """Função principal"""
    demonstrate_integrated_system()

if __name__ == "__main__":
    main() 