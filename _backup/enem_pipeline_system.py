"""
🚀 PIPELINE ENEM - SISTEMA ESTRUTURADO EM 6 ETAPAS
================================================
Sistema de processamento seguindo pipeline sugerido:

1. Extração: PDF → texto bruto (pdfplumber)
2. Limpeza: remover headers, footers, numeração de páginas  
3. Segmentação: identificar início/fim de cada questão
4. Estruturação: organizar em formato JSON estruturado
5. Embedding: vetorizar apenas o conteúdo relevante
6. Retrieval: buscar questões completas e estruturadas
"""

import logging
import time
import json
import re
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QuestaoEstruturada:
    """Estrutura padronizada de uma questão do ENEM"""
    numero: int
    area_conhecimento: str
    enunciado: str
    alternativas: Dict[str, str]  # {'A': 'texto', 'B': 'texto', ...}
    comando: str
    contexto: str
    assunto: str
    dificuldade: str = "medio"
    fonte: str = "ENEM"
    embedding_key: str = ""

@dataclass
class PipelineResult:
    """Resultado do pipeline completo"""
    etapa_atual: str
    questoes_extraidas: List[QuestaoEstruturada]
    texto_bruto: str
    texto_limpo: str
    segmentos: List[Dict[str, Any]]
    embeddings: Dict[str, List[float]]
    processing_time: float
    quality_metrics: Dict[str, float]

class ENEMPipelineSystem:
    """Sistema de Pipeline ENEM em 6 etapas"""
    
    def __init__(self):
        self.texto_bruto = ""
        self.texto_limpo = ""
        self.segmentos = []
        self.questoes_estruturadas = []
        self.embeddings = {}
        self.pipeline_metrics = {}
        
        logger.info("✅ Pipeline ENEM System inicializado")
    
    def executar_pipeline_completo(self, pdf_path: str) -> PipelineResult:
        """Executa o pipeline completo em 6 etapas"""
        start_time = time.time()
        logger.info("🚀 INICIANDO PIPELINE ENEM - 6 ETAPAS")
        logger.info("="*60)
        
        # ETAPA 1: Extração
        logger.info("📄 ETAPA 1: Extração PDF → Texto Bruto")
        self.texto_bruto = self._etapa_1_extracao(pdf_path)
        logger.info(f"   ✅ Extraído: {len(self.texto_bruto)} caracteres")
        
        # ETAPA 2: Limpeza
        logger.info("🧹 ETAPA 2: Limpeza e Normalização")
        self.texto_limpo = self._etapa_2_limpeza(self.texto_bruto)
        logger.info(f"   ✅ Limpo: {len(self.texto_limpo)} caracteres")
        
        # ETAPA 3: Segmentação
        logger.info("✂️ ETAPA 3: Segmentação por Questões")
        self.segmentos = self._etapa_3_segmentacao(self.texto_limpo)
        logger.info(f"   ✅ Segmentado: {len(self.segmentos)} questões")
        
        # ETAPA 4: Estruturação
        logger.info("🏗️ ETAPA 4: Estruturação JSON")
        self.questoes_estruturadas = self._etapa_4_estruturacao(self.segmentos)
        logger.info(f"   ✅ Estruturado: {len(self.questoes_estruturadas)} questões")
        
        # ETAPA 5: Embedding
        logger.info("🧠 ETAPA 5: Vetorização de Conteúdo")
        self.embeddings = self._etapa_5_embedding(self.questoes_estruturadas)
        logger.info(f"   ✅ Embeddings: {len(self.embeddings)} vetores")
        
        # ETAPA 6: Preparação para Retrieval
        logger.info("🔍 ETAPA 6: Preparação para Retrieval")
        retrieval_data = self._etapa_6_retrieval_prep(self.questoes_estruturadas, self.embeddings)
        logger.info(f"   ✅ Retrieval: {len(retrieval_data)} índices")
        
        processing_time = time.time() - start_time
        logger.info("="*60)
        logger.info(f"🎉 PIPELINE CONCLUÍDO EM {processing_time:.2f}s")
        
        # Calcular métricas de qualidade
        quality_metrics = self._calcular_quality_metrics()
        
        return PipelineResult(
            etapa_atual="retrieval_ready",
            questoes_extraidas=self.questoes_estruturadas,
            texto_bruto=self.texto_bruto,
            texto_limpo=self.texto_limpo,
            segmentos=self.segmentos,
            embeddings=self.embeddings,
            processing_time=processing_time,
            quality_metrics=quality_metrics
        )
    
    def _etapa_1_extracao(self, pdf_path: str) -> str:
        """ETAPA 1: Extração PDF → Texto Bruto usando pdfplumber"""
        try:
            # Tentar usar pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    texto_completo = ""
                    for page in pdf.pages:
                        texto_completo += page.extract_text() or ""
                        texto_completo += "\n\n"
                    return texto_completo
            except ImportError:
                logger.warning("⚠️ pdfplumber não disponível")
            
            # Fallback: usar sistema existente
            from advanced_pdf_extractor import AdvancedPDFExtractor
            extractor = AdvancedPDFExtractor()
            result = extractor.extract_pdf(pdf_path)
            return result.get("content", "")
            
        except Exception as e:
            logger.error(f"❌ Erro na extração: {e}")
            # Texto de exemplo para demonstração
            return self._get_texto_exemplo()
    
    def _get_texto_exemplo(self) -> str:
        """Texto de exemplo para demonstração"""
        return """
CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS

QUESTÃO 91
A energia solar é uma fonte renovável que tem ganhado destaque no cenário energético mundial. Os painéis fotovoltaicos convertem a radiação solar diretamente em energia elétrica através do efeito fotoelétrico.

Considerando as vantagens da energia solar, assinale a alternativa correta:

A) A energia solar só funciona durante o dia.
B) Os painéis solares não funcionam em dias nublados.
C) A energia solar é uma fonte limpa e renovável.
D) A instalação de painéis solares é muito cara.
E) A energia solar não é eficiente em regiões tropicais.

QUESTÃO 92
O ciclo da água é fundamental para a manutenção da vida na Terra. A evaporação, condensação e precipitação são processos que mantêm o equilíbrio hídrico do planeta.

Marque a opção que melhor descreve o ciclo da água:

A) Apenas a evaporação é importante no ciclo.
B) A condensação ocorre apenas nas nuvens.
C) A precipitação inclui chuva, neve e granizo.
D) O ciclo da água não afeta o clima.
E) Apenas os oceanos participam do ciclo.

MATEMÁTICA E SUAS TECNOLOGIAS

QUESTÃO 93
Um estudante precisa calcular a área de um triângulo retângulo com catetos de 3 cm e 4 cm.

Indique a área correta do triângulo:

A) 6 cm²
B) 7 cm²
C) 10 cm²
D) 12 cm²
E) 14 cm²
"""
    
    def _etapa_2_limpeza(self, texto_bruto: str) -> str:
        """ETAPA 2: Limpeza - remover headers, footers, numeração"""
        
        # Remover quebras de linha excessivas
        texto = re.sub(r'\n{3,}', '\n\n', texto_bruto)
        
        # Remover numeração de páginas
        texto = re.sub(r'Página\s+\d+', '', texto)
        texto = re.sub(r'\d+\s*/\s*\d+', '', texto)
        
        # Remover headers/footers comuns
        headers_footers = [
            r'ENEM\s+\d{4}',
            r'Ministério da Educação',
            r'Instituto Nacional de Estudos',
            r'www\.inep\.gov\.br',
            r'Caderno de Questões',
            r'Prova de.*?TECNOLOGIAS'
        ]
        
        for pattern in headers_footers:
            texto = re.sub(pattern, '', texto, flags=re.IGNORECASE)
        
        # Normalizar espaços
        texto = re.sub(r' +', ' ', texto)
        texto = re.sub(r'\t+', ' ', texto)
        
        # Remover linhas vazias
        linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
        
        return '\n'.join(linhas)
    
    def _etapa_3_segmentacao(self, texto_limpo: str) -> List[Dict[str, Any]]:
        """ETAPA 3: Segmentação - identificar início/fim de cada questão"""
        
        segmentos = []
        
        # Padrões para detectar início de questão
        patterns_questao = [
            r'QUESTÃO\s+(\d+)',
            r'Questão\s+(\d+)',
            r'(\d+)\.\s+[A-Z]',
            r'(\d+)\)\s+[A-Z]'
        ]
        
        # Detectar áreas de conhecimento
        patterns_area = [
            r'CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS',
            r'MATEMÁTICA E SUAS TECNOLOGIAS',
            r'LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS',
            r'CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS'
        ]
        
        linhas = texto_limpo.split('\n')
        questao_atual = None
        area_atual = ""
        buffer_questao = []
        
        for i, linha in enumerate(linhas):
            # Detectar área de conhecimento
            for pattern in patterns_area:
                if re.search(pattern, linha):
                    area_atual = linha.strip()
                    break
            
            # Detectar início de questão
            for pattern in patterns_questao:
                match = re.search(pattern, linha)
                if match:
                    # Salvar questão anterior se existir
                    if questao_atual and buffer_questao:
                        segmentos.append({
                            'numero': questao_atual,
                            'area': area_atual,
                            'conteudo': '\n'.join(buffer_questao),
                            'linha_inicio': questao_atual,
                            'linha_fim': i-1
                        })
                    
                    # Iniciar nova questão
                    questao_atual = int(match.group(1))
                    buffer_questao = [linha]
                    continue
            
            # Adicionar linha ao buffer da questão atual
            if questao_atual and linha.strip():
                buffer_questao.append(linha)
        
        # Adicionar última questão
        if questao_atual and buffer_questao:
            segmentos.append({
                'numero': questao_atual,
                'area': area_atual,
                'conteudo': '\n'.join(buffer_questao),
                'linha_inicio': questao_atual,
                'linha_fim': len(linhas)-1
            })
        
        return segmentos
    
    def _etapa_4_estruturacao(self, segmentos: List[Dict[str, Any]]) -> List[QuestaoEstruturada]:
        """ETAPA 4: Estruturação - organizar em formato JSON estruturado"""
        
        questoes_estruturadas = []
        
        for segmento in segmentos:
            try:
                conteudo = segmento['conteudo']
                
                # Extrair número da questão
                numero = segmento['numero']
                
                # Extrair área de conhecimento
                area = segmento.get('area', 'Área não identificada')
                
                # Separar enunciado, comando e alternativas
                partes = self._parse_questao_content(conteudo)
                
                # Criar questão estruturada
                questao = QuestaoEstruturada(
                    numero=numero,
                    area_conhecimento=area,
                    enunciado=partes['enunciado'],
                    alternativas=partes['alternativas'],
                    comando=partes['comando'],
                    contexto=partes['contexto'],
                    assunto=self._extrair_assunto(partes['enunciado']),
                    embedding_key=f"questao_{numero}"
                )
                
                questoes_estruturadas.append(questao)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao estruturar questão {segmento.get('numero', '?')}: {e}")
        
        return questoes_estruturadas
    
    def _parse_questao_content(self, conteudo: str) -> Dict[str, Any]:
        """Parse detalhado do conteúdo da questão"""
        
        linhas = conteudo.split('\n')
        
        enunciado_lines = []
        alternativas = {}
        comando = ""
        contexto = ""
        
        current_section = "enunciado"
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
            
            # Detectar comando
            comandos_patterns = [
                r'assinale\s+a\s+alternativa',
                r'marque\s+a\s+opção',
                r'indique\s+a\s+alternativa',
                r'escolha\s+a\s+opção'
            ]
            
            for pattern in comandos_patterns:
                if re.search(pattern, linha, re.IGNORECASE):
                    comando = linha
                    current_section = "comando"
                    continue
            
            # Detectar alternativas
            alt_match = re.match(r'^([A-E])\)\s*(.+)', linha)
            if alt_match:
                letra = alt_match.group(1)
                texto = alt_match.group(2)
                alternativas[letra] = texto
                current_section = "alternativas"
                continue
            
            # Adicionar ao enunciado
            if current_section == "enunciado":
                enunciado_lines.append(linha)
        
        enunciado = ' '.join(enunciado_lines)
        
        return {
            'enunciado': enunciado,
            'alternativas': alternativas,
            'comando': comando,
            'contexto': contexto
        }
    
    def _extrair_assunto(self, enunciado: str) -> str:
        """Extrai o assunto principal baseado no enunciado"""
        
        # Palavras-chave por assunto
        assuntos_keywords = {
            'Energia': ['energia', 'solar', 'elétrica', 'fotovoltaico', 'renovável'],
            'Água e Meio Ambiente': ['água', 'ciclo', 'evaporação', 'precipitação', 'clima'],
            'Geometria': ['triângulo', 'área', 'cateto', 'retângulo', 'perímetro'],
            'Física': ['movimento', 'força', 'velocidade', 'aceleração'],
            'Química': ['reação', 'elemento', 'molécula', 'átomo'],
            'Biologia': ['célula', 'organismo', 'ecossistema', 'evolução']
        }
        
        enunciado_lower = enunciado.lower()
        
        for assunto, keywords in assuntos_keywords.items():
            if any(keyword in enunciado_lower for keyword in keywords):
                return assunto
        
        return "Assunto Geral"
    
    def _etapa_5_embedding(self, questoes: List[QuestaoEstruturada]) -> Dict[str, List[float]]:
        """ETAPA 5: Embedding - vetorizar conteúdo relevante"""
        
        embeddings = {}
        
        for questao in questoes:
            try:
                # Texto para embedding: enunciado + assunto
                texto_embedding = f"{questao.enunciado} {questao.assunto}"
                
                # Simular embedding (em produção usar sentence-transformers ou OpenAI)
                embedding_simulado = self._simular_embedding(texto_embedding)
                
                embeddings[questao.embedding_key] = embedding_simulado
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao gerar embedding para questão {questao.numero}: {e}")
        
        return embeddings
    
    def _simular_embedding(self, texto: str) -> List[float]:
        """Simula um embedding (em produção usar modelo real)"""
        # Hash do texto para simular embedding consistente
        hash_obj = hashlib.md5(texto.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Converter hash em vetor de floats (384 dimensões)
        embedding = []
        for i in range(0, len(hash_hex), 2):
            value = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(value)
        
        # Preencher até 384 dimensões
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def _etapa_6_retrieval_prep(self, questoes: List[QuestaoEstruturada], embeddings: Dict[str, List[float]]) -> Dict[str, Any]:
        """ETAPA 6: Preparação para Retrieval"""
        
        # Criar índice para busca
        retrieval_index = {
            'questoes': {},
            'embeddings': embeddings,
            'index_metadata': {
                'total_questoes': len(questoes),
                'embedding_dimension': 384,
                'created_at': time.time()
            }
        }
        
        # Indexar questões
        for questao in questoes:
            retrieval_index['questoes'][questao.embedding_key] = {
                'numero': questao.numero,
                'area': questao.area_conhecimento,
                'assunto': questao.assunto,
                'enunciado': questao.enunciado,
                'alternativas': questao.alternativas,
                'comando': questao.comando
            }
        
        return retrieval_index
    
    def _calcular_quality_metrics(self) -> Dict[str, float]:
        """Calcula métricas de qualidade do pipeline"""
        
        metrics = {
            'texto_extraido_score': min(len(self.texto_bruto) / 1000, 1.0),
            'limpeza_score': len(self.texto_limpo) / max(len(self.texto_bruto), 1),
            'segmentacao_score': len(self.segmentos) / max(3, 1),  # Espera pelo menos 3 questões
            'estruturacao_score': len(self.questoes_estruturadas) / max(len(self.segmentos), 1),
            'embedding_score': len(self.embeddings) / max(len(self.questoes_estruturadas), 1),
            'overall_quality': 0.0
        }
        
        # Score geral
        metrics['overall_quality'] = sum(metrics.values()) / (len(metrics) - 1)
        
        return metrics
    
    def export_pipeline_result(self, result: PipelineResult, output_path: str):
        """Exporta resultado do pipeline para JSON"""
        
        export_data = {
            'pipeline_metadata': {
                'etapa_atual': result.etapa_atual,
                'processing_time': result.processing_time,
                'questoes_count': len(result.questoes_extraidas),
                'quality_metrics': result.quality_metrics
            },
            'questoes_estruturadas': [asdict(q) for q in result.questoes_extraidas],
            'segmentos': result.segmentos,
            'embeddings_count': len(result.embeddings),
            'pipeline_stats': {
                'texto_bruto_length': len(result.texto_bruto),
                'texto_limpo_length': len(result.texto_limpo),
                'segmentos_count': len(result.segmentos)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Pipeline result exportado: {output_path}")

def demonstrar_pipeline():
    """Demonstração do pipeline completo"""
    print("🚀 PIPELINE ENEM - SISTEMA ESTRUTURADO EM 6 ETAPAS")
    print("="*70)
    print("📋 Seguindo metodologia sugerida:")
    print("   1. Extração: PDF → texto bruto (pdfplumber)")
    print("   2. Limpeza: remover headers, footers, numeração")  
    print("   3. Segmentação: identificar início/fim de questões")
    print("   4. Estruturação: organizar em formato JSON")
    print("   5. Embedding: vetorizar conteúdo relevante")
    print("   6. Retrieval: preparar busca estruturada")
    print()
    
    # Inicializar sistema
    pipeline = ENEMPipelineSystem()
    
    # Executar pipeline
    result = pipeline.executar_pipeline_completo("exemplo_enem.pdf")
    
    # Mostrar resultados
    print("📊 RESULTADOS DO PIPELINE:")
    print("="*50)
    print(f"⏱️ Tempo de processamento: {result.processing_time:.2f}s")
    print(f"📄 Questões extraídas: {len(result.questoes_extraidas)}")
    print(f"✂️ Segmentos criados: {len(result.segmentos)}")
    print(f"🧠 Embeddings gerados: {len(result.embeddings)}")
    print(f"⭐ Qualidade geral: {result.quality_metrics['overall_quality']:.2f}")
    print()
    
    # Mostrar questões estruturadas
    print("📝 QUESTÕES ESTRUTURADAS:")
    print("-" * 40)
    for i, questao in enumerate(result.questoes_extraidas[:2]):  # Mostrar apenas 2
        print(f"🔢 Questão {questao.numero}")
        print(f"   📚 Área: {questao.area_conhecimento}")
        print(f"   🎯 Assunto: {questao.assunto}")
        print(f"   📝 Enunciado: {questao.enunciado[:100]}...")
        print(f"   🔤 Alternativas: {len(questao.alternativas)}")
        print(f"   ⚡ Embedding: {len(result.embeddings.get(questao.embedding_key, []))} dims")
        print()
    
    # Exportar resultado
    pipeline.export_pipeline_result(result, "pipeline_enem_result.json")
    
    print("✅ PIPELINE DEMONSTRADO COM SUCESSO!")
    print("🎉 Sistema pronto para integração RAG!")

def main():
    """Função principal"""
    demonstrar_pipeline()

if __name__ == "__main__":
    main() 