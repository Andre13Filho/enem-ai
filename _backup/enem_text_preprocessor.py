#!/usr/bin/env python3
"""
Sistema de Pré-processamento Estruturado para Textos do ENEM
Aplica regex patterns avançados para identificar e estruturar padrões específicos do ENEM
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ENEMPatternType(Enum):
    """Tipos de padrões identificados no ENEM"""
    QUESTION_NUMBER = "question_number"
    ALTERNATIVE = "alternative"
    COMMAND = "command"
    SUBJECT_AREA = "subject_area"
    INSTRUCTION = "instruction"
    REFERENCE = "reference"
    UNKNOWN = "unknown"

@dataclass
class ENEMPattern:
    """Representa um padrão identificado no texto"""
    pattern_type: ENEMPatternType
    text: str
    original_text: str
    position: Tuple[int, int]  # start, end
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class ProcessedSegment:
    """Segmento de texto processado"""
    original_text: str
    cleaned_text: str
    patterns: List[ENEMPattern]
    segment_type: str
    confidence: float

class ENEMTextPreprocessor:
    """
    Sistema avançado de pré-processamento para textos do ENEM
    Identifica e estrutura padrões específicos usando regex
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.stats = {
            "total_processed": 0,
            "patterns_found": {},
            "cleaning_applied": {}
        }
    
    def _initialize_patterns(self) -> Dict[ENEMPatternType, List[Dict]]:
        """Inicializa todos os regex patterns para o ENEM"""
        
        return {
            # === NÚMEROS DAS QUESTÕES ===
            ENEMPatternType.QUESTION_NUMBER: [
                {
                    "pattern": r'(?i)QUESTÃO\s+(\d+)',
                    "description": "Questão N (formato oficial)",
                    "extract_number": True,
                    "confidence": 0.95
                },
                {
                    "pattern": r'(?i)Questão\s+(\d+)',
                    "description": "Questão N (variação)",
                    "extract_number": True,
                    "confidence": 0.90
                },
                {
                    "pattern": r'^(\d+)\s*[\.\)]\s*',
                    "description": "Número seguido de ponto ou parêntese",
                    "extract_number": True,
                    "confidence": 0.85
                },
                {
                    "pattern": r'\b(\d+)\s*-\s*',
                    "description": "Número seguido de hífen",
                    "extract_number": True,
                    "confidence": 0.80
                },
                {
                    "pattern": r'(?i)QUESTAO\s+(\d+)',
                    "description": "QUESTAO sem acento",
                    "extract_number": True,
                    "confidence": 0.75
                }
            ],
            
            # === ALTERNATIVAS ===
            ENEMPatternType.ALTERNATIVE: [
                {
                    "pattern": r'^([A-E])\)\s*(.+?)(?=\n[A-E]\)|$)',
                    "description": "A) texto (formato padrão)",
                    "extract_letter": True,
                    "extract_content": True,
                    "confidence": 0.95
                },
                {
                    "pattern": r'^\(([A-E])\)\s*(.+?)(?=\n\([A-E]\)|$)',
                    "description": "(A) texto (formato alternativo)",
                    "extract_letter": True,
                    "extract_content": True,
                    "confidence": 0.90
                },
                {
                    "pattern": r'^([A-E])\.\s*(.+?)(?=\n[A-E]\.|$)',
                    "description": "A. texto (formato com ponto)",
                    "extract_letter": True,
                    "extract_content": True,
                    "confidence": 0.85
                },
                {
                    "pattern": r'^([A-E])\s+([A-Z].+?)(?=\n[A-E]\s|$)',
                    "description": "A texto (sem pontuação)",
                    "extract_letter": True,
                    "extract_content": True,
                    "confidence": 0.75
                },
                {
                    "pattern": r'\b([A-E])[\)\.\-\s]\s*(.{10,}?)(?=\n|$)',
                    "description": "Alternativas com separadores variados",
                    "extract_letter": True,
                    "extract_content": True,
                    "confidence": 0.70
                }
            ],
            
            # === COMANDOS TÍPICOS ===
            ENEMPatternType.COMMAND: [
                {
                    "pattern": r'(?i)assinale\s+a\s+alternativa\s+correta',
                    "description": "Assinale a alternativa correta",
                    "confidence": 0.95
                },
                {
                    "pattern": r'(?i)marque\s+a\s+op[çc][ãa]o\s+correta',
                    "description": "Marque a opção correta",
                    "confidence": 0.95
                },
                {
                    "pattern": r'(?i)assinale\s+a\s+op[çc][ãa]o\s+correta',
                    "description": "Assinale a opção correta",
                    "confidence": 0.90
                },
                {
                    "pattern": r'(?i)indique\s+a\s+alternativa\s+correta',
                    "description": "Indique a alternativa correta",
                    "confidence": 0.90
                },
                {
                    "pattern": r'(?i)escolha\s+a\s+alternativa\s+que',
                    "description": "Escolha a alternativa que",
                    "confidence": 0.85
                },
                {
                    "pattern": r'(?i)assinale\s+a\s+única\s+alternativa',
                    "description": "Assinale a única alternativa",
                    "confidence": 0.85
                },
                {
                    "pattern": r'(?i)marque\s+\w+\s+item\s+correto',
                    "description": "Marque o item correto",
                    "confidence": 0.80
                },
                {
                    "pattern": r'(?i)a\s+resposta\s+correta\s+é',
                    "description": "A resposta correta é",
                    "confidence": 0.75
                }
            ],
            
            # === ÁREAS DE CONHECIMENTO ===
            ENEMPatternType.SUBJECT_AREA: [
                {
                    "pattern": r'(?i)LINGUAGENS,?\s*CÓDIGOS\s*E\s*SUAS\s*TECNOLOGIAS',
                    "description": "Linguagens, Códigos e suas Tecnologias",
                    "confidence": 0.95
                },
                {
                    "pattern": r'(?i)MATEMÁTICA\s*E\s*SUAS\s*TECNOLOGIAS',
                    "description": "Matemática e suas Tecnologias",
                    "confidence": 0.95
                },
                {
                    "pattern": r'(?i)CIÊNCIAS\s*DA\s*NATUREZA\s*E\s*SUAS\s*TECNOLOGIAS',
                    "description": "Ciências da Natureza e suas Tecnologias",
                    "confidence": 0.95
                },
                {
                    "pattern": r'(?i)CIÊNCIAS\s*HUMANAS\s*E\s*SUAS\s*TECNOLOGIAS',
                    "description": "Ciências Humanas e suas Tecnologias",
                    "confidence": 0.95
                }
            ],
            
            # === INSTRUÇÕES ESPECÍFICAS ===
            ENEMPatternType.INSTRUCTION: [
                {
                    "pattern": r'(?i)leia\s+atentamente\s+as\s+instruções',
                    "description": "Leia atentamente as instruções",
                    "confidence": 0.90
                },
                {
                    "pattern": r'(?i)atenção:\s*transcreva',
                    "description": "Atenção: transcreva",
                    "confidence": 0.90
                },
                {
                    "pattern": r'(?i)tempo\s+de\s+prova:\s*\d+',
                    "description": "Tempo de prova",
                    "confidence": 0.85
                },
                {
                    "pattern": r'(?i)cartão[\-\s]resposta',
                    "description": "Cartão-resposta",
                    "confidence": 0.80
                }
            ]
        }

    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """Aplica pré-processamento estruturado completo ao texto"""
        logger.info("🔄 Iniciando pré-processamento estruturado")
        
        # Etapa 1: Limpeza básica
        cleaned_text = self._basic_cleaning(text)
        
        # Etapa 2: Identificação de padrões
        patterns = self._identify_patterns(cleaned_text)
        
        # Etapa 3: Análise estrutural
        structured_result = self._analyze_structure(cleaned_text, patterns)
        
        logger.info(f"✅ Pré-processamento concluído: {len(patterns)} padrões identificados")
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "patterns": patterns,
            "structured_content": structured_result,
            "stats": self._get_processing_stats(patterns)
        }
    
    def _basic_cleaning(self, text: str) -> str:
        """Limpeza básica do texto"""
        cleaned = text
        
        # Remove caracteres de controle
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
        
        # Normaliza espaços
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        # Remove espaços no início e fim de linhas
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n'))
        
        return cleaned.strip()
    
    def _identify_patterns(self, text: str) -> List[ENEMPattern]:
        """Identifica todos os padrões no texto"""
        all_patterns = []
        
        for pattern_type, pattern_configs in self.patterns.items():
            for config in pattern_configs:
                matches = list(re.finditer(config["pattern"], text, re.MULTILINE))
                
                for match in matches:
                    pattern = self._create_pattern(pattern_type, match, config, text)
                    if pattern:
                        all_patterns.append(pattern)
        
        # Ordena por posição no texto
        all_patterns.sort(key=lambda p: p.position[0])
        
        return all_patterns
    
    def _create_pattern(self, pattern_type: ENEMPatternType, match: re.Match, 
                       config: Dict, full_text: str) -> Optional[ENEMPattern]:
        """Cria um objeto ENEMPattern a partir de um match"""
        try:
            metadata = {}
            original_text = match.group(0)
            cleaned_text = original_text.strip()
            
            # Extrai informações específicas
            if pattern_type == ENEMPatternType.QUESTION_NUMBER:
                if config.get("extract_number") and match.groups():
                    metadata["question_number"] = int(match.group(1))
                    cleaned_text = f"QUESTÃO {metadata['question_number']}"
            
            elif pattern_type == ENEMPatternType.ALTERNATIVE:
                if config.get("extract_letter") and match.groups():
                    metadata["letter"] = match.group(1)
                    if config.get("extract_content") and len(match.groups()) > 1:
                        metadata["content"] = match.group(2).strip()
                        cleaned_text = f"{metadata['letter']}) {metadata['content']}"
            
            return ENEMPattern(
                pattern_type=pattern_type,
                text=cleaned_text,
                original_text=original_text,
                position=(match.start(), match.end()),
                confidence=config["confidence"],
                metadata=metadata
            )
            
        except Exception as e:
            logger.warning(f"Erro ao criar padrão: {e}")
            return None
    
    def _analyze_structure(self, text: str, patterns: List[ENEMPattern]) -> Dict[str, Any]:
        """Analisa a estrutura do texto baseado nos padrões"""
        structure = {
            "questions": [],
            "total_patterns": len(patterns),
            "quality_score": 0.0
        }
        
        # Identifica questões
        question_patterns = [p for p in patterns if p.pattern_type == ENEMPatternType.QUESTION_NUMBER]
        alternative_patterns = [p for p in patterns if p.pattern_type == ENEMPatternType.ALTERNATIVE]
        command_patterns = [p for p in patterns if p.pattern_type == ENEMPatternType.COMMAND]
        
        for q_pattern in question_patterns:
            question_data = {
                "number": q_pattern.metadata.get("question_number"),
                "alternatives": [],
                "commands": [],
                "confidence": q_pattern.confidence
            }
            
            # Encontra alternativas desta questão
            for alt_pattern in alternative_patterns:
                if alt_pattern.position[0] > q_pattern.position[0]:
                    question_data["alternatives"].append({
                        "letter": alt_pattern.metadata.get("letter"),
                        "content": alt_pattern.metadata.get("content"),
                        "confidence": alt_pattern.confidence
                    })
            
            # Encontra comandos desta questão
            for cmd_pattern in command_patterns:
                if cmd_pattern.position[0] > q_pattern.position[0]:
                    question_data["commands"].append(cmd_pattern.text)
            
            structure["questions"].append(question_data)
        
        # Calcula qualidade geral
        if patterns:
            structure["quality_score"] = sum(p.confidence for p in patterns) / len(patterns)
        
        return structure
    
    def _get_processing_stats(self, patterns: List[ENEMPattern]) -> Dict[str, Any]:
        """Gera estatísticas do processamento"""
        stats = {
            "total_patterns": len(patterns),
            "by_type": {},
            "quality_indicators": {}
        }
        
        for pattern in patterns:
            pattern_name = pattern.pattern_type.value
            stats["by_type"][pattern_name] = stats["by_type"].get(pattern_name, 0) + 1
        
        # Indicadores de qualidade
        question_patterns = [p for p in patterns if p.pattern_type == ENEMPatternType.QUESTION_NUMBER]
        alternative_patterns = [p for p in patterns if p.pattern_type == ENEMPatternType.ALTERNATIVE]
        
        stats["quality_indicators"] = {
            "has_question_numbers": len(question_patterns) > 0,
            "has_alternatives": len(alternative_patterns) > 0,
            "alternatives_per_question": len(alternative_patterns) / max(len(question_patterns), 1),
            "avg_confidence": sum(p.confidence for p in patterns) / len(patterns) if patterns else 0
        }
        
        return stats

# Função de conveniência
def preprocess_enem_text(text: str) -> Dict[str, Any]:
    """Função principal para pré-processamento de texto do ENEM"""
    preprocessor = ENEMTextPreprocessor()
    return preprocessor.preprocess_text(text)

if __name__ == "__main__":
    # Teste do preprocessor
    sample_text = """
    QUESTÃO 91
    
    Muitas pessoas ainda se espantam com o fato de um passageiro sair ileso de um 
    acidente de carro enquanto o veículo onde estava teve perda total.
    
    A função do cinto de segurança é:
    
    A) acionar os airbags do veículo.
    B) absorver a energia cinética do sistema.
    C) reduzir a velocidade do veículo.
    D) aumentar o tempo de colisão.
    E) diminuir a força média de impacto.
    """
    
    print("🧪 Testando Pré-processador Estruturado do ENEM")
    print("=" * 60)
    
    result = preprocess_enem_text(sample_text)
    
    print(f"📊 Padrões encontrados: {result['stats']['total_patterns']}")
    print(f"📋 Por tipo: {result['stats']['by_type']}")
    print(f"✅ Qualidade: {result['stats']['quality_indicators']}")
    
    if result["structured_content"]["questions"]:
        question = result["structured_content"]["questions"][0]
        print(f"\n📝 Questão {question['number']}:")
        print(f"   Alternativas: {len(question['alternatives'])}")
        print(f"   Comandos: {len(question['commands'])}")
        print(f"   Confiança: {question['confidence']:.1%}") 