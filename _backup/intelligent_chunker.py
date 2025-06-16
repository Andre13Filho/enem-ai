#!/usr/bin/env python3
"""
Sistema de Chunking Inteligente para o ENEM
Implementa semantic chunking, chunks por questão e overlapping contextual
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Imports dos sistemas desenvolvidos
try:
    from enem_text_preprocessor import ENEMTextPreprocessor, ENEMPattern, ENEMPatternType
    from advanced_pdf_extractor import AdvancedPDFExtractor, TextBlock
except ImportError as e:
    print(f"⚠️ Aviso: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChunkingStrategy(Enum):
    """Estratégias de chunking disponíveis"""
    QUESTION_BASED = "question_based"        # Um chunk por questão
    SEMANTIC_GROUPS = "semantic_groups"      # Agrupa questões por tema
    CONTEXTUAL_OVERLAP = "contextual_overlap" # Chunks com sobreposição
    ADAPTIVE_SIZE = "adaptive_size"          # Tamanho adaptativo baseado em conteúdo
    MIXED_STRATEGY = "mixed_strategy"        # Combinação de estratégias

@dataclass
class ChunkMetadata:
    """Metadados de um chunk"""
    chunk_id: str
    chunk_type: str
    question_numbers: List[int]
    subject_area: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    difficulty_estimate: Optional[float] = None
    confidence_score: float = 0.0
    semantic_boundaries: List[int] = field(default_factory=list)
    overlapping_context: Dict[str, Any] = field(default_factory=dict)
    original_position: Tuple[int, int] = (0, 0)
    processing_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class QuestionChunk:
    """Representa um chunk inteligente baseado em questões"""
    content: str
    clean_content: str
    metadata: ChunkMetadata
    patterns_found: List[ENEMPattern] = field(default_factory=list)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    context_before: str = ""
    context_after: str = ""
    semantic_similarity: float = 0.0
    chunk_size: int = 0
    quality_score: float = 0.0

class SemanticBoundaryDetector:
    """Detecta limites semânticos no texto"""
    
    def __init__(self):
        self.boundary_patterns = self._initialize_boundary_patterns()
    
    def _initialize_boundary_patterns(self) -> Dict[str, List[Dict]]:
        """Inicializa padrões para detecção de limites semânticos"""
        return {
            "strong_boundaries": [
                {
                    "pattern": r'(?i)QUESTÃO\s+(\d+)',
                    "description": "Início de nova questão",
                    "strength": 0.95
                },
                {
                    "pattern": r'(?i)(?:MATEMÁTICA|FÍSICA|QUÍMICA|BIOLOGIA|PORTUGUÊS|HISTÓRIA|GEOGRAFIA)\s+E\s+SUAS\s+TECNOLOGIAS',
                    "description": "Mudança de área de conhecimento",
                    "strength": 0.90
                },
                {
                    "pattern": r'(?i)(?:PROVA|CADERNO|EXAME)\s+(?:DE|DO)',
                    "description": "Seção de prova",
                    "strength": 0.85
                }
            ],
            "medium_boundaries": [
                {
                    "pattern": r'(?i)(?:TEXTO|GRÁFICO|FIGURA|IMAGEM)\s+(?:PARA|DAS?)\s+(?:QUESTÕES?|PRÓXIMAS?)',
                    "description": "Texto base para múltiplas questões",
                    "strength": 0.75
                },
                {
                    "pattern": r'(?i)(?:CONSIDERE|ANALISE|OBSERVE)\s+(?:O|A|OS|AS)',
                    "description": "Início de contexto",
                    "strength": 0.70
                }
            ],
            "weak_boundaries": [
                {
                    "pattern": r'\.(?:\s*\n){2,}',
                    "description": "Parágrafos separados",
                    "strength": 0.50
                },
                {
                    "pattern": r'(?i)(?:PORTANTO|ASSIM|DESSA FORMA)',
                    "description": "Conectivos conclusivos",
                    "strength": 0.40
                }
            ]
        }
    
    def detect_boundaries(self, text: str) -> List[Dict[str, Any]]:
        """Detecta limites semânticos no texto"""
        boundaries = []
        
        for boundary_type, patterns in self.boundary_patterns.items():
            for pattern_config in patterns:
                pattern = pattern_config["pattern"]
                matches = list(re.finditer(pattern, text, re.MULTILINE))
                
                for match in matches:
                    boundaries.append({
                        "position": match.start(),
                        "text": match.group(0),
                        "type": boundary_type,
                        "strength": pattern_config["strength"],
                        "description": pattern_config["description"]
                    })
        
        # Ordena por posição no texto
        boundaries.sort(key=lambda x: x["position"])
        
        return boundaries

class ContextualOverlapManager:
    """Gerencia sobreposição contextual entre chunks"""
    
    def __init__(self, overlap_size: int = 200):
        self.overlap_size = overlap_size
        self.context_strategies = {
            "previous_conclusion": self._extract_previous_conclusion,
            "next_introduction": self._extract_next_introduction,
            "thematic_connection": self._extract_thematic_connection
        }
    
    def add_contextual_overlap(self, chunks: List[QuestionChunk]) -> List[QuestionChunk]:
        """Adiciona sobreposição contextual aos chunks"""
        logger.info("🔗 Adicionando sobreposição contextual")
        
        for i, chunk in enumerate(chunks):
            # Contexto anterior
            if i > 0:
                previous_chunk = chunks[i-1]
                chunk.context_before = self._extract_overlap_context(
                    previous_chunk.content, "before", chunk
                )
            
            # Contexto posterior
            if i < len(chunks) - 1:
                next_chunk = chunks[i+1]
                chunk.context_after = self._extract_overlap_context(
                    next_chunk.content, "after", chunk
                )
            
            # Atualiza metadados de sobreposição
            chunk.metadata.overlapping_context = {
                "has_before": bool(chunk.context_before),
                "has_after": bool(chunk.context_after),
                "before_length": len(chunk.context_before),
                "after_length": len(chunk.context_after),
                "overlap_strategies_used": list(self.context_strategies.keys())
            }
        
        return chunks
    
    def _extract_overlap_context(self, source_content: str, direction: str, 
                                target_chunk: QuestionChunk) -> str:
        """Extrai contexto de sobreposição"""
        if direction == "before":
            # Pega final do chunk anterior
            words = source_content.split()
            overlap_words = words[-self.overlap_size//10:] if len(words) > self.overlap_size//10 else words
            return " ".join(overlap_words)
        
        elif direction == "after":
            # Pega início do próximo chunk
            words = source_content.split()
            overlap_words = words[:self.overlap_size//10] if len(words) > self.overlap_size//10 else words
            return " ".join(overlap_words)
        
        return ""
    
    def _extract_previous_conclusion(self, content: str) -> str:
        """Extrai conclusão do conteúdo anterior"""
        # Busca por padrões conclusivos
        conclusion_patterns = [
            r'(?i)(?:portanto|assim|dessa forma|concluindo).+?\.(?:\s|$)',
            r'(?i)(?:logo|por isso|consequentemente).+?\.(?:\s|$)'
        ]
        
        for pattern in conclusion_patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[-1].strip()  # Última conclusão encontrada
        
        return ""
    
    def _extract_next_introduction(self, content: str) -> str:
        """Extrai introdução do próximo conteúdo"""
        # Busca por padrões introdutórios
        intro_patterns = [
            r'(?i)(?:considere|analise|observe|seja).+?\.(?:\s|$)',
            r'(?i)(?:dado|sabendo que|supondo).+?\.(?:\s|$)'
        ]
        
        for pattern in intro_patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[0].strip()  # Primeira introdução encontrada
        
        return ""
    
    def _extract_thematic_connection(self, content: str) -> str:
        """Extrai conexões temáticas"""
        # Identifica temas e conectivos
        thematic_patterns = [
            r'(?i)(?:relacionado a|referente a|sobre).+?\.(?:\s|$)',
            r'(?i)(?:tema|assunto|tópico).+?\.(?:\s|$)'
        ]
        
        connections = []
        for pattern in thematic_patterns:
            matches = re.findall(pattern, content)
            connections.extend(matches)
        
        return " ".join(connections)

class IntelligentChunker:
    """
    Sistema principal de chunking inteligente
    Implementa estratégias avançadas de segmentação semântica
    """
    
    def __init__(self, strategy: ChunkingStrategy = ChunkingStrategy.QUESTION_BASED):
        self.strategy = strategy
        self.preprocessor = None
        self.boundary_detector = SemanticBoundaryDetector()
        self.overlap_manager = ContextualOverlapManager()
        
        # Configurações de chunking
        self.config = {
            "max_chunk_size": 2000,
            "min_chunk_size": 100,
            "overlap_size": 200,
            "preserve_question_integrity": True,
            "include_contextual_overlap": True,
            "adaptive_sizing": True
        }
        
        # Inicializa preprocessor se disponível
        try:
            self.preprocessor = ENEMTextPreprocessor()
            logger.info("✅ Pré-processador integrado ao chunker")
        except:
            logger.warning("⚠️ Pré-processador não disponível")
        
        self.chunking_stats = {
            "total_chunks_created": 0,
            "strategy_usage": {},
            "avg_chunk_size": 0,
            "quality_scores": []
        }
    
    def chunk_text(self, text: str, **kwargs) -> List[QuestionChunk]:
        """
        Método principal para chunking inteligente
        """
        logger.info(f"🔄 Iniciando chunking inteligente com estratégia: {self.strategy.value}")
        
        # Aplica pré-processamento se disponível
        preprocessed_data = None
        if self.preprocessor:
            preprocessed_data = self.preprocessor.preprocess_text(text)
            text = preprocessed_data["cleaned_text"]
        
        # Detecta limites semânticos
        boundaries = self.boundary_detector.detect_boundaries(text)
        
        # Executa estratégia de chunking
        chunks = self._execute_chunking_strategy(text, boundaries, preprocessed_data, **kwargs)
        
        # Adiciona sobreposição contextual se configurado
        if self.config["include_contextual_overlap"]:
            chunks = self.overlap_manager.add_contextual_overlap(chunks)
        
        # Calcula métricas de qualidade
        chunks = self._calculate_chunk_quality(chunks)
        
        # Atualiza estatísticas
        self._update_chunking_stats(chunks)
        
        logger.info(f"✅ Chunking concluído: {len(chunks)} chunks criados")
        
        return chunks
    
    def _execute_chunking_strategy(self, text: str, boundaries: List[Dict], 
                                  preprocessed_data: Optional[Dict], **kwargs) -> List[QuestionChunk]:
        """Executa a estratégia de chunking especificada"""
        
        if self.strategy == ChunkingStrategy.QUESTION_BASED:
            return self._chunk_by_questions(text, boundaries, preprocessed_data)
        
        elif self.strategy == ChunkingStrategy.SEMANTIC_GROUPS:
            return self._chunk_by_semantic_groups(text, boundaries, preprocessed_data)
        
        elif self.strategy == ChunkingStrategy.CONTEXTUAL_OVERLAP:
            return self._chunk_with_contextual_overlap(text, boundaries, preprocessed_data)
        
        elif self.strategy == ChunkingStrategy.ADAPTIVE_SIZE:
            return self._chunk_adaptive_size(text, boundaries, preprocessed_data)
        
        elif self.strategy == ChunkingStrategy.MIXED_STRATEGY:
            return self._chunk_mixed_strategy(text, boundaries, preprocessed_data)
        
        else:
            # Fallback para estratégia por questões
            return self._chunk_by_questions(text, boundaries, preprocessed_data)
    
    def _chunk_by_questions(self, text: str, boundaries: List[Dict], 
                           preprocessed_data: Optional[Dict]) -> List[QuestionChunk]:
        """Estratégia: um chunk por questão completa"""
        logger.info("📝 Executando chunking por questões")
        
        chunks = []
        
        # Identifica questões através de padrões ou preprocessamento
        if preprocessed_data and preprocessed_data.get("structured_content"):
            questions_data = preprocessed_data["structured_content"].get("questions", [])
            patterns = preprocessed_data.get("patterns", [])
        else:
            # Fallback para regex direto
            questions_data = self._extract_questions_direct(text)
            patterns = []
        
        # Identifica posições das questões
        question_boundaries = [b for b in boundaries if b["type"] == "strong_boundaries" 
                             and "QUESTÃO" in b["text"].upper()]
        
        if not question_boundaries:
            # Se não encontrou questões, cria chunks por tamanho
            return self._chunk_by_size(text, boundaries)
        
        # Cria chunks para cada questão
        for i, boundary in enumerate(question_boundaries):
            start_pos = boundary["position"]
            end_pos = question_boundaries[i + 1]["position"] if i + 1 < len(question_boundaries) else len(text)
            
            question_text = text[start_pos:end_pos].strip()
            
            if len(question_text) >= self.config["min_chunk_size"]:
                chunk = self._create_question_chunk(
                    question_text, i, patterns, questions_data, start_pos, end_pos
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_semantic_groups(self, text: str, boundaries: List[Dict], 
                                 preprocessed_data: Optional[Dict]) -> List[QuestionChunk]:
        """Estratégia: agrupa questões por tema/área"""
        logger.info("🏷️ Executando chunking por grupos semânticos")
        
        # Primeiro, aplica chunking por questões
        question_chunks = self._chunk_by_questions(text, boundaries, preprocessed_data)
        
        # Agrupa por área de conhecimento ou tema
        semantic_groups = {}
        
        for chunk in question_chunks:
            # Identifica tema/área
            theme = self._identify_chunk_theme(chunk)
            
            if theme not in semantic_groups:
                semantic_groups[theme] = []
            
            semantic_groups[theme].append(chunk)
        
        # Combina chunks do mesmo grupo se necessário
        combined_chunks = []
        
        for theme, group_chunks in semantic_groups.items():
            if len(group_chunks) == 1:
                combined_chunks.extend(group_chunks)
            else:
                # Combina múltiplos chunks do mesmo tema
                combined_chunk = self._combine_chunks(group_chunks, theme)
                combined_chunks.append(combined_chunk)
        
        return combined_chunks
    
    def _chunk_with_contextual_overlap(self, text: str, boundaries: List[Dict], 
                                      preprocessed_data: Optional[Dict]) -> List[QuestionChunk]:
        """Estratégia: chunks com sobreposição contextual inteligente"""
        logger.info("🔗 Executando chunking com sobreposição contextual")
        
        # Inicia com chunks por questões
        base_chunks = self._chunk_by_questions(text, boundaries, preprocessed_data)
        
        # Adiciona sobreposição inteligente baseada em conteúdo
        overlapped_chunks = []
        
        for i, chunk in enumerate(base_chunks):
            # Cria nova versão do chunk com contexto expandido
            expanded_chunk = self._expand_chunk_with_context(
                chunk, base_chunks, i
            )
            overlapped_chunks.append(expanded_chunk)
        
        return overlapped_chunks
    
    def _chunk_adaptive_size(self, text: str, boundaries: List[Dict], 
                            preprocessed_data: Optional[Dict]) -> List[QuestionChunk]:
        """Estratégia: tamanho adaptativo baseado no conteúdo"""
        logger.info("📏 Executando chunking com tamanho adaptativo")
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Determina tamanho ideal para este trecho
            ideal_size = self._calculate_ideal_chunk_size(
                text[current_pos:], boundaries, preprocessed_data
            )
            
            # Encontra próximo limite semântico apropriado
            end_pos = self._find_next_semantic_boundary(
                text, current_pos, ideal_size, boundaries
            )
            
            chunk_text = text[current_pos:end_pos].strip()
            
            if len(chunk_text) >= self.config["min_chunk_size"]:
                chunk = self._create_adaptive_chunk(
                    chunk_text, len(chunks), current_pos, end_pos
                )
                chunks.append(chunk)
            
            current_pos = end_pos
        
        return chunks
    
    def _chunk_mixed_strategy(self, text: str, boundaries: List[Dict], 
                             preprocessed_data: Optional[Dict]) -> List[QuestionChunk]:
        """Estratégia: combinação inteligente de múltiplas estratégias"""
        logger.info("🎯 Executando estratégia mista de chunking")
        
        # Analisa características do texto
        text_characteristics = self._analyze_text_characteristics(text, preprocessed_data)
        
        # Escolhe estratégia baseada nas características
        if text_characteristics["question_density"] > 0.8:
            return self._chunk_by_questions(text, boundaries, preprocessed_data)
        
        elif text_characteristics["thematic_coherence"] > 0.7:
            return self._chunk_by_semantic_groups(text, boundaries, preprocessed_data)
        
        elif text_characteristics["context_dependency"] > 0.6:
            return self._chunk_with_contextual_overlap(text, boundaries, preprocessed_data)
        
        else:
            return self._chunk_adaptive_size(text, boundaries, preprocessed_data)
    
    def _create_question_chunk(self, content: str, chunk_index: int, 
                              patterns: List, questions_data: List, 
                              start_pos: int, end_pos: int) -> QuestionChunk:
        """Cria um chunk baseado em questão"""
        
        # Extrai número da questão
        question_number = self._extract_question_number(content)
        
        # Identifica alternativas
        alternatives = self._extract_alternatives_from_content(content)
        
        # Identifica comandos
        commands = self._extract_commands_from_content(content)
        
        # Cria metadados
        metadata = ChunkMetadata(
            chunk_id=f"question_chunk_{chunk_index}",
            chunk_type="question_based",
            question_numbers=[question_number] if question_number else [],
            original_position=(start_pos, end_pos)
        )
        
        # Cria chunk
        chunk = QuestionChunk(
            content=content,
            clean_content=self._clean_content(content),
            metadata=metadata,
            alternatives=alternatives,
            commands=commands,
            chunk_size=len(content)
        )
        
        return chunk
    
    def _extract_question_number(self, content: str) -> Optional[int]:
        """Extrai número da questão do conteúdo"""
        pattern = r'(?i)QUESTÃO\s+(\d+)'
        match = re.search(pattern, content)
        return int(match.group(1)) if match else None
    
    def _extract_alternatives_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extrai alternativas do conteúdo"""
        alternatives = []
        
        # Padrões de alternativas
        patterns = [
            r'^([A-E])\)\s*(.+?)(?=\n[A-E]\)|$)',
            r'^\(([A-E])\)\s*(.+?)(?=\n\([A-E]\)|$)',
            r'^([A-E])\.\s*(.+?)(?=\n[A-E]\.|$)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                alternatives.append({
                    "letter": match.group(1),
                    "content": match.group(2).strip(),
                    "confidence": 0.8  # Confiança padrão
                })
        
        return alternatives
    
    def _extract_commands_from_content(self, content: str) -> List[str]:
        """Extrai comandos do conteúdo"""
        command_patterns = [
            r'(?i)assinale\s+a\s+alternativa\s+correta',
            r'(?i)marque\s+a\s+op[çc][ãa]o\s+correta',
            r'(?i)indique\s+a\s+alternativa\s+correta'
        ]
        
        commands = []
        for pattern in command_patterns:
            matches = re.findall(pattern, content)
            commands.extend(matches)
        
        return commands
    
    def _clean_content(self, content: str) -> str:
        """Limpa o conteúdo do chunk"""
        cleaned = content
        
        # Remove quebras de linha excessivas
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Remove espaços desnecessários
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        # Remove caracteres de controle
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
        
        return cleaned.strip()
    
    def _calculate_chunk_quality(self, chunks: List[QuestionChunk]) -> List[QuestionChunk]:
        """Calcula qualidade dos chunks"""
        for chunk in chunks:
            quality_factors = {
                "completeness": self._assess_completeness(chunk),
                "coherence": self._assess_coherence(chunk),
                "size_appropriateness": self._assess_size_appropriateness(chunk),
                "context_quality": self._assess_context_quality(chunk)
            }
            
            # Calcula score geral
            chunk.quality_score = sum(quality_factors.values()) / len(quality_factors)
            
            # Adiciona fatores aos metadados
            chunk.metadata.confidence_score = chunk.quality_score
        
        return chunks
    
    def _assess_completeness(self, chunk: QuestionChunk) -> float:
        """Avalia completude do chunk"""
        score = 0.0
        
        # Verifica se tem questão
        if chunk.metadata.question_numbers:
            score += 0.3
        
        # Verifica se tem alternativas
        if len(chunk.alternatives) >= 4:
            score += 0.4
        elif len(chunk.alternatives) > 0:
            score += 0.2
        
        # Verifica se tem comandos
        if chunk.commands:
            score += 0.3
        
        return min(score, 1.0)
    
    def _assess_coherence(self, chunk: QuestionChunk) -> float:
        """Avalia coerência do chunk"""
        # Score básico baseado na estrutura
        return 0.8 if chunk.alternatives and chunk.metadata.question_numbers else 0.5
    
    def _assess_size_appropriateness(self, chunk: QuestionChunk) -> float:
        """Avalia adequação do tamanho"""
        size = chunk.chunk_size
        min_size = self.config["min_chunk_size"]
        max_size = self.config["max_chunk_size"]
        
        if min_size <= size <= max_size:
            return 1.0
        elif size < min_size:
            return size / min_size
        else:
            return max_size / size
    
    def _assess_context_quality(self, chunk: QuestionChunk) -> float:
        """Avalia qualidade do contexto"""
        score = 0.5  # Score base
        
        if chunk.context_before:
            score += 0.25
        
        if chunk.context_after:
            score += 0.25
        
        return score
    
    def _update_chunking_stats(self, chunks: List[QuestionChunk]):
        """Atualiza estatísticas do chunking"""
        self.chunking_stats["total_chunks_created"] += len(chunks)
        
        strategy_name = self.strategy.value
        self.chunking_stats["strategy_usage"][strategy_name] = \
            self.chunking_stats["strategy_usage"].get(strategy_name, 0) + 1
        
        if chunks:
            avg_size = sum(chunk.chunk_size for chunk in chunks) / len(chunks)
            self.chunking_stats["avg_chunk_size"] = avg_size
            
            quality_scores = [chunk.quality_score for chunk in chunks]
            self.chunking_stats["quality_scores"].extend(quality_scores)
    
    def get_chunking_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do chunking"""
        stats = self.chunking_stats.copy()
        
        if stats["quality_scores"]:
            stats["avg_quality_score"] = sum(stats["quality_scores"]) / len(stats["quality_scores"])
        else:
            stats["avg_quality_score"] = 0.0
        
        return stats
    
    # Métodos auxiliares para outras estratégias (implementação simplificada)
    def _chunk_by_size(self, text: str, boundaries: List[Dict]) -> List[QuestionChunk]:
        """Fallback: chunking por tamanho"""
        chunks = []
        chunk_size = self.config["max_chunk_size"]
        
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i + chunk_size]
            if len(chunk_text) >= self.config["min_chunk_size"]:
                chunk = QuestionChunk(
                    content=chunk_text,
                    clean_content=self._clean_content(chunk_text),
                    metadata=ChunkMetadata(
                        chunk_id=f"size_chunk_{len(chunks)}",
                        chunk_type="size_based",
                        question_numbers=[]
                    ),
                    chunk_size=len(chunk_text)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _extract_questions_direct(self, text: str) -> List[Dict]:
        """Extração direta de questões sem preprocessor"""
        # Implementação simplificada
        return []
    
    def _identify_chunk_theme(self, chunk: QuestionChunk) -> str:
        """Identifica tema do chunk"""
        # Implementação simplificada
        return "general"
    
    def _combine_chunks(self, chunks: List[QuestionChunk], theme: str) -> QuestionChunk:
        """Combina múltiplos chunks"""
        # Implementação simplificada
        combined_content = "\n\n".join(chunk.content for chunk in chunks)
        return QuestionChunk(
            content=combined_content,
            clean_content=self._clean_content(combined_content),
            metadata=ChunkMetadata(
                chunk_id=f"combined_{theme}",
                chunk_type="semantic_group",
                question_numbers=[]
            ),
            chunk_size=len(combined_content)
        )
    
    def _expand_chunk_with_context(self, chunk: QuestionChunk, 
                                  all_chunks: List[QuestionChunk], index: int) -> QuestionChunk:
        """Expande chunk com contexto"""
        # Implementação simplificada
        return chunk
    
    def _calculate_ideal_chunk_size(self, text: str, boundaries: List[Dict], 
                                   preprocessed_data: Optional[Dict]) -> int:
        """Calcula tamanho ideal do chunk"""
        # Implementação simplificada
        return self.config["max_chunk_size"]
    
    def _find_next_semantic_boundary(self, text: str, start_pos: int, 
                                    ideal_size: int, boundaries: List[Dict]) -> int:
        """Encontra próxima fronteira semântica"""
        # Implementação simplificada
        return min(start_pos + ideal_size, len(text))
    
    def _create_adaptive_chunk(self, content: str, index: int, 
                              start_pos: int, end_pos: int) -> QuestionChunk:
        """Cria chunk adaptativo"""
        # Implementação simplificada
        return QuestionChunk(
            content=content,
            clean_content=self._clean_content(content),
            metadata=ChunkMetadata(
                chunk_id=f"adaptive_chunk_{index}",
                chunk_type="adaptive_size",
                question_numbers=[]
            ),
            chunk_size=len(content)
        )
    
    def _analyze_text_characteristics(self, text: str, 
                                     preprocessed_data: Optional[Dict]) -> Dict[str, float]:
        """Analisa características do texto"""
        # Implementação simplificada
        return {
            "question_density": 0.5,
            "thematic_coherence": 0.5,
            "context_dependency": 0.5
        }

# Função de conveniência para uso direto
def intelligent_chunk_text(text: str, strategy: ChunkingStrategy = ChunkingStrategy.QUESTION_BASED, 
                          **kwargs) -> List[QuestionChunk]:
    """
    Função principal para chunking inteligente
    """
    chunker = IntelligentChunker(strategy)
    return chunker.chunk_text(text, **kwargs)

if __name__ == "__main__":
    # Teste do chunker
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
    
    QUESTÃO 92
    
    A energia cinética de um objeto depende de sua massa e velocidade.
    
    Assinale a alternativa correta:
    
    A) Energia cinética é independente da massa.
    B) Energia cinética varia linearmente com a velocidade.
    C) Energia cinética é proporcional ao quadrado da velocidade.
    D) Energia cinética não depende da velocidade.
    E) Energia cinética é sempre constante.
    """
    
    print("🧪 Testando Chunking Inteligente")
    print("=" * 60)
    
    chunks = intelligent_chunk_text(sample_text, ChunkingStrategy.QUESTION_BASED)
    
    print(f"📊 Chunks criados: {len(chunks)}")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n📝 Chunk {i}:")
        print(f"   ID: {chunk.metadata.chunk_id}")
        print(f"   Tipo: {chunk.metadata.chunk_type}")
        print(f"   Questões: {chunk.metadata.question_numbers}")
        print(f"   Tamanho: {chunk.chunk_size} caracteres")
        print(f"   Qualidade: {chunk.quality_score:.1%}")
        print(f"   Alternativas: {len(chunk.alternatives)}")
        print(f"   Comandos: {len(chunk.commands)}")
        
        if chunk.context_before:
            print(f"   📄 Contexto anterior: {len(chunk.context_before)} chars")
        if chunk.context_after:
            print(f"   📄 Contexto posterior: {len(chunk.context_after)} chars") 