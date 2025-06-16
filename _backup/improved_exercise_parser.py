#!/usr/bin/env python3
"""
Parser Melhorado de Exercícios do ENEM - Sistema RAG Avançado
Sistema robusto para extração e estruturação de questões do ENEM
Implementa parsing semântico e estruturação JSON conforme sugerido
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Alternative:
    """Estrutura para uma alternativa de questão"""
    letra: str
    texto: str
    is_valid: bool = True
    confidence: float = 1.0

@dataclass 
class ExerciseQuestion:
    """Estrutura completa para uma questão do ENEM"""
    id_questao: str
    area_conhecimento: str
    enunciado: str
    alternativas: List[Alternative]
    alternativa_correta: Optional[str] = None
    topicos_chave: List[str] = None
    ano: str = ""
    numero_questao: str = ""
    fonte_arquivo: str = ""
    habilidade_associada: str = ""
    dificuldade_estimada: str = ""
    tipo_questao: str = "múltipla escolha"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        result = asdict(self)
        result['alternativas'] = [asdict(alt) for alt in self.alternativas]
        return result
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class ImprovedExerciseParser:
    """Parser melhorado para exercícios do ENEM"""
    
    def __init__(self):
        # Padrões regex melhorados para diferentes formatos de questão
        self.question_patterns = [
            r'QUESTÃO\s+(\d+)',  # QUESTÃO 91
            r'(?:^|\n)(\d+)\s*\.?\s*(?=[A-Z])',  # 91. seguido de texto
            r'(?:^|\n)(\d+)\s+(?=\w)',  # 91 seguido de palavra
            r'(?:^|\n)(\d+)\s*(?=\n)',  # Número seguido de quebra de linha
        ]
        
        # Padrões para identificação de alternativas - mais robustos
        self.alternative_patterns = [
            # Padrão A) texto
            r'([A-E])\)\s*([^\n\r]+?)(?=\s*[B-E]\)|$)',
            # Padrão (A) texto  
            r'\(([A-E])\)\s*([^\n\r]+?)(?=\s*\([B-E]\)|$)',
            # Padrão A texto (sem parênteses)
            r'\b([A-E])\s+([^\n\r]*?)(?=\s*[B-E]\s+|$)',
            # Padrão A. texto
            r'([A-E])\.?\s*([^\n\r]+?)(?=\s*[B-E]\.|\n[B-E]\.|$)',
        ]
        
        # Áreas de conhecimento do ENEM
        self.areas_conhecimento = [
            "CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS",
            "MATEMÁTICA E SUAS TECNOLOGIAS", 
            "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS",
            "CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS"
        ]
        
        # Palavras-chave para identificação de tópicos
        self.topicos_keywords = {
            'física': ['energia', 'força', 'movimento', 'eletricidade', 'óptica', 'termodinâmica'],
            'química': ['reação', 'elemento', 'composto', 'mol', 'concentração', 'pH'],
            'biologia': ['célula', 'gene', 'evolução', 'ecossistema', 'organismo'],
            'matemática': ['função', 'equação', 'geometria', 'probabilidade', 'estatística'],
            'trigonometria': ['seno', 'cosseno', 'tangente', 'ângulo', 'radiano'],
            'álgebra': ['variável', 'sistema', 'inequação', 'matriz'],
            'geometria': ['área', 'volume', 'perímetro', 'triângulo', 'círculo']
        }

    def parse_pdf_text_to_exercises(self, full_text: str, year: str, filename: str) -> List[ExerciseQuestion]:
        """
        Parse principal que converte texto do PDF em lista de exercícios estruturados
        """
        logger.info(f"Iniciando parse do arquivo {filename} ({year})")
        
        exercises = []
        
        # 1. Identificar questões individuais
        question_boundaries = self._find_question_boundaries(full_text)
        
        if not question_boundaries:
            logger.warning(f"Nenhuma questão identificada em {filename}")
            return self._fallback_chunk_parsing(full_text, year, filename)
        
        logger.info(f"Encontradas {len(question_boundaries)} questões em {filename}")
        
        # 2. Processar cada questão individualmente
        for i, (question_num, start_pos, end_pos) in enumerate(question_boundaries):
            question_text = full_text[start_pos:end_pos].strip()
            
            if len(question_text) < 100:  # Filtrar questões muito curtas
                continue
                
            # 3. Extrair estrutura da questão
            exercise = self._parse_single_exercise(
                question_text, question_num, year, filename
            )
            
            if exercise and self._validate_exercise(exercise):
                exercises.append(exercise)
                logger.info(f"Questão {question_num} parseada com sucesso")
            else:
                logger.warning(f"Questão {question_num} falhou na validação")
        
        logger.info(f"Parse concluído: {len(exercises)} exercícios válidos extraídos")
        return exercises

    def _find_question_boundaries(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Identifica os limites de cada questão no texto
        Retorna lista de (numero_questao, posicao_inicio, posicao_fim)
        """
        question_matches = []
        
        # Tenta diferentes padrões até encontrar um que funcione bem
        for pattern in self.question_patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE))
            
            if len(matches) >= 1:  # Se encontrou pelo menos uma questão
                question_matches = matches
                break
        
        if not question_matches:
            return []
        
        # Determina limites de cada questão
        boundaries = []
        for i, match in enumerate(question_matches):
            question_num = match.group(1)
            start_pos = match.start()
            
            # Fim da questão = início da próxima questão ou fim do texto
            if i + 1 < len(question_matches):
                end_pos = question_matches[i + 1].start()
            else:
                end_pos = len(text)
            
            boundaries.append((question_num, start_pos, end_pos))
        
        return boundaries

    def _parse_single_exercise(self, question_text: str, question_num: str, year: str, filename: str) -> Optional[ExerciseQuestion]:
        """
        Parse de uma única questão em estrutura ExerciseQuestion
        """
        try:
            # 1. Identificar área de conhecimento
            area_conhecimento = self._identify_subject_area(question_text)
            
            # 2. Separar enunciado e alternativas
            enunciado, alternatives_text = self._separate_statement_and_alternatives(question_text)
            
            # 3. Extrair alternativas estruturadas
            alternativas = self._extract_structured_alternatives(alternatives_text)
            
            if len(alternativas) < 3:  # Mínimo de alternativas esperadas
                logger.warning(f"Questão {question_num}: apenas {len(alternativas)} alternativas encontradas")
                return None
            
            # 4. Identificar tópicos-chave
            topicos_chave = self._extract_key_topics(question_text)
            
            # 5. Estimar dificuldade
            dificuldade = self._estimate_difficulty(question_text)
            
            # 6. Criar objeto estruturado
            exercise = ExerciseQuestion(
                id_questao=f"QUESTÃO {question_num}",
                area_conhecimento=area_conhecimento,
                enunciado=enunciado.strip(),
                alternativas=alternativas,
                topicos_chave=topicos_chave,
                ano=year,
                numero_questao=question_num,
                fonte_arquivo=filename,
                dificuldade_estimada=dificuldade,
                habilidade_associada=self._map_topic_to_skill(topicos_chave[0] if topicos_chave else "")
            )
            
            return exercise
            
        except Exception as e:
            logger.error(f"Erro ao processar questão {question_num}: {e}")
            return None

    def _separate_statement_and_alternatives(self, question_text: str) -> Tuple[str, str]:
        """
        Separa o enunciado das alternativas de forma inteligente
        """
        # Procura pelo primeiro padrão de alternativa
        first_alternative_match = None
        for pattern in self.alternative_patterns:
            match = re.search(pattern, question_text, re.MULTILINE | re.DOTALL)
            if match:
                first_alternative_match = match
                break
        
        if first_alternative_match:
            # Divide no início da primeira alternativa
            split_pos = first_alternative_match.start()
            enunciado = question_text[:split_pos]
            alternatives_text = question_text[split_pos:]
        else:
            # Se não encontrou alternativas claras, assume que tudo é enunciado
            enunciado = question_text
            alternatives_text = ""
        
        return enunciado, alternatives_text

    def _extract_structured_alternatives(self, alternatives_text: str) -> List[Alternative]:
        """
        Extrai alternativas em formato estruturado com validação
        """
        alternatives = []
        
        if not alternatives_text.strip():
            return alternatives
        
        # Tenta cada padrão de alternativa
        for pattern in self.alternative_patterns:
            matches = re.findall(pattern, alternatives_text, re.MULTILINE | re.DOTALL)
            
            if len(matches) >= 3:  # Se encontrou múltiplas alternativas
                for letra, texto in matches:
                    cleaned_text = self._clean_alternative_text(texto)
                    
                    if cleaned_text:  # Só adiciona se o texto é válido
                        alt = Alternative(
                            letra=letra.upper(),
                            texto=cleaned_text,
                            is_valid=len(cleaned_text) > 5,
                            confidence=self._calculate_alternative_confidence(cleaned_text)
                        )
                        alternatives.append(alt)
                
                # Se encontrou alternativas válidas, para de tentar outros padrões
                if alternatives:
                    break
        
        # Ordena por letra para garantir ordem A, B, C, D, E
        alternatives.sort(key=lambda x: x.letra)
        
        return alternatives

    def _clean_alternative_text(self, text: str) -> str:
        """
        Limpa o texto de uma alternativa de forma robusta
        """
        if not text:
            return ""
        
        # Remove quebras de linha desnecessárias
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove números isolados no início (lixo de OCR)
        text = re.sub(r'^[\d\s+×\-=]+', '', text)
        
        # Remove caracteres de lixo comuns
        text = re.sub(r'[+×\-=]{2,}', '', text)
        
        # Remove números muito longos (provavelmente lixo)
        text = re.sub(r'\b\d{4,}\b', '', text)
        
        # Limpa espaços duplos
        text = re.sub(r'\s+', ' ', text)
        
        text = text.strip()
        
        # Validações finais
        if len(text) < 3:
            return ""
        
        if re.match(r'^[\d\s+×\-=]+$', text):  # Só números e símbolos
            return ""
        
        return text

    def _calculate_alternative_confidence(self, text: str) -> float:
        """
        Calcula nível de confiança na qualidade de uma alternativa
        """
        if not text:
            return 0.0
        
        confidence = 1.0
        
        # Penaliza textos muito curtos
        if len(text) < 10:
            confidence -= 0.3
        
        # Penaliza textos com muitos números
        num_count = len(re.findall(r'\d+', text))
        if num_count > 3:
            confidence -= 0.2
        
        # Penaliza textos com caracteres especiais demais
        special_count = len(re.findall(r'[+×\-=]', text))
        if special_count > 2:
            confidence -= 0.2
        
        # Bonifica textos com palavras completas
        word_count = len(re.findall(r'\b\w{3,}\b', text))
        if word_count >= 3:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))

    def _identify_subject_area(self, text: str) -> str:
        """
        Identifica a área de conhecimento baseada no conteúdo
        """
        text_lower = text.lower()
        
        # Palavras-chave por área
        area_keywords = {
            "MATEMÁTICA E SUAS TECNOLOGIAS": [
                'função', 'equação', 'geometria', 'trigonometria', 'probabilidade',
                'estatística', 'logaritmo', 'matriz', 'derivada', 'integral'
            ],
            "CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS": [
                'energia', 'força', 'velocidade', 'reação', 'elemento', 'composto',
                'célula', 'gene', 'evolução', 'ph', 'concentração'
            ]
        }
        
        # Conta ocorrências por área
        area_scores = {}
        for area, keywords in area_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            area_scores[area] = score
        
        # Retorna área com maior score, ou genérica se empate
        if area_scores:
            best_area = max(area_scores, key=area_scores.get)
            if area_scores[best_area] > 0:
                return best_area
        
        return "CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS"  # Default

    def _extract_key_topics(self, text: str) -> List[str]:
        """
        Extrai tópicos-chave do texto da questão
        """
        text_lower = text.lower()
        topics_found = []
        
        for topic, keywords in self.topicos_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if topic not in topics_found:
                        topics_found.append(topic)
                    break
        
        # Se não encontrou tópicos específicos, tenta identificar por contexto
        if not topics_found:
            if any(word in text_lower for word in ['calcul', 'determin', 'encontr']):
                topics_found.append('resolução de problemas')
            if any(word in text_lower for word in ['gráfico', 'figura', 'desenho']):
                topics_found.append('interpretação gráfica')
        
        return topics_found[:3]  # Máximo 3 tópicos

    def _estimate_difficulty(self, text: str) -> str:
        """
        Estima dificuldade baseada em heurísticas
        """
        text_lower = text.lower()
        
        # Indicadores de dificuldade
        hard_indicators = ['demonstre', 'prove', 'justifique', 'analise detalhadamente']
        medium_indicators = ['calcule', 'determine', 'encontre', 'resolva']
        easy_indicators = ['identifique', 'indique', 'marque', 'assinale']
        
        hard_count = sum(1 for word in hard_indicators if word in text_lower)
        medium_count = sum(1 for word in medium_indicators if word in text_lower)
        easy_count = sum(1 for word in easy_indicators if word in text_lower)
        
        # Considera também tamanho do texto
        text_length = len(text)
        
        if hard_count >= 1 or text_length > 1000:
            return "Difícil"
        elif medium_count >= 1 or text_length > 500:
            return "Médio"
        else:
            return "Fácil"

    def _map_topic_to_skill(self, topic: str) -> str:
        """
        Mapeia tópico para habilidade do ENEM
        """
        skill_mapping = {
            'função': 'Analisar e interpretar gráficos de funções',
            'geometria': 'Resolver problemas geométricos utilizando propriedades',
            'probabilidade': 'Calcular probabilidades em situações-problema',
            'trigonometria': 'Aplicar relações trigonométricas',
            'física': 'Compreender fenômenos físicos',
            'química': 'Analisar transformações químicas',
            'biologia': 'Compreender processos biológicos'
        }
        
        return skill_mapping.get(topic, 'Resolver problemas contextualizados')

    def _validate_exercise(self, exercise: ExerciseQuestion) -> bool:
        """
        Valida se o exercício foi parseado corretamente
        """
        if not exercise:
            return False
        
        # Validações básicas
        if len(exercise.enunciado) < 50:
            return False
        
        if len(exercise.alternativas) < 3:
            return False
        
        # Verifica se alternativas têm conteúdo válido
        valid_alternatives = sum(1 for alt in exercise.alternativas if alt.is_valid and len(alt.texto) > 5)
        
        if valid_alternatives < 3:
            return False
        
        return True

    def _fallback_chunk_parsing(self, text: str, year: str, filename: str) -> List[ExerciseQuestion]:
        """
        Método de fallback quando não consegue identificar questões individuais
        """
        logger.info("Usando método de fallback - divisão por chunks")
        
        # Divide texto em chunks e tenta extrair exercícios
        chunks = self._split_text_semantically(text)
        exercises = []
        
        for i, chunk in enumerate(chunks):
            if len(chunk) > 200:  # Só processa chunks substanciais
                # Tenta encontrar padrões de exercício no chunk
                exercise = self._parse_single_exercise(chunk, f"CHUNK_{i+1}", year, filename)
                if exercise and self._validate_exercise(exercise):
                    exercises.append(exercise)
        
        return exercises

    def _split_text_semantically(self, text: str, chunk_size: int = 1500) -> List[str]:
        """
        Divide texto em chunks semanticamente coerentes
        """
        # Prioriza quebras em pontos naturais
        separators = ['\n\n\n', '\n\n', '. ', '? ', '! ', ': ', '; ', '\n']
        
        chunks = []
        current_chunk = ""
        
        for paragraph in text.split('\n\n'):
            if len(current_chunk) + len(paragraph) < chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

# Função de conveniência para uso externo
def parse_enem_exercises(pdf_text: str, year: str, filename: str) -> List[Dict[str, Any]]:
    """
    Função principal para parsing de exercícios - retorna lista de dicionários
    """
    parser = ImprovedExerciseParser()
    exercises = parser.parse_pdf_text_to_exercises(pdf_text, year, filename)
    
    return [exercise.to_dict() for exercise in exercises]

# Exemplo de uso
if __name__ == "__main__":
    # Teste do parser
    sample_text = """
    QUESTÃO 91
    
    Muitas pessoas ainda se espantam com o fato de um passageiro sair ileso de um acidente de carro enquanto o veículo onde estava teve perda total. O que mais espanta é que, além de estar vivo, o passageiro não sofreu nenhum ferimento grave.
    
    A) aciona os airbags do veículo.
    B) absorve a energia cinética do sistema.
    C) reduz a velocidade do veículo.
    D) aumenta o tempo de colisão.
    E) diminui a força média de impacto.
    """
    
    parser = ImprovedExerciseParser()
    exercises = parser.parse_pdf_text_to_exercises(sample_text, "2023", "teste.pdf")
    
    if exercises:
        print("✅ Exercício parseado com sucesso!")
        print(exercises[0].to_json())
    else:
        print("❌ Falha no parsing") 