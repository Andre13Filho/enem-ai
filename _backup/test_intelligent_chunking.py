#!/usr/bin/env python3
"""
Testes do Sistema de Chunking Inteligente
Demonstra semantic chunking, chunks por questão e overlapping contextual
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligent_chunker import (
    IntelligentChunker, ChunkingStrategy, intelligent_chunk_text,
    QuestionChunk, ChunkMetadata
)
import json

def test_question_based_chunking():
    """Teste de chunking baseado em questões"""
    print("🔍 TESTE 1: Chunking Baseado em Questões")
    print("=" * 60)
    
    texto_multiplas_questoes = """
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
    
    QUESTÃO 93
    
    O movimento retilíneo uniforme (MRU) é caracterizado por velocidade constante
    e aceleração nula.
    
    Marque a opção correta:
    
    A) No MRU, a velocidade varia com o tempo.
    B) No MRU, existe aceleração constante.
    C) No MRU, a distância percorrida é proporcional ao tempo.
    D) No MRU, a velocidade é sempre zero.
    E) No MRU, o objeto sempre volta ao ponto de partida.
    """
    
    chunks = intelligent_chunk_text(texto_multiplas_questoes, ChunkingStrategy.QUESTION_BASED)
    
    print(f"📊 RESULTADOS:")
    print(f"   Total de chunks: {len(chunks)}")
    print(f"   Estratégia: {ChunkingStrategy.QUESTION_BASED.value}")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n📝 Chunk {i}:")
        print(f"   🆔 ID: {chunk.metadata.chunk_id}")
        print(f"   📏 Tamanho: {chunk.chunk_size} caracteres")
        print(f"   🔢 Questões: {chunk.metadata.question_numbers}")
        print(f"   🔤 Alternativas: {len(chunk.alternatives)}")
        print(f"   📋 Comandos: {len(chunk.commands)}")
        print(f"   ⭐ Qualidade: {chunk.quality_score:.1%}")
        
        # Mostra preview do conteúdo
        preview = chunk.clean_content[:100] + "..." if len(chunk.clean_content) > 100 else chunk.clean_content
        print(f"   📄 Preview: {preview}")
    
    return chunks

def test_semantic_groups_chunking():
    """Teste de chunking por grupos semânticos"""
    print("\n🔍 TESTE 2: Chunking por Grupos Semânticos")
    print("=" * 60)
    
    texto_temas_mistos = """
    MATEMÁTICA E SUAS TECNOLOGIAS
    
    QUESTÃO 45
    
    Uma função quadrática f(x) = ax² + bx + c tem discriminante positivo.
    
    Isso significa que a função:
    A) não possui raízes reais.
    B) possui duas raízes reais e distintas.
    C) possui uma raiz real dupla.
    D) é sempre positiva.
    E) é sempre negativa.
    
    QUESTÃO 46
    
    O teorema de Pitágoras estabelece que em um triângulo retângulo,
    o quadrado da hipotenusa é igual à soma dos quadrados dos catetos.
    
    Em um triângulo com catetos de 3 cm e 4 cm, a hipotenusa mede:
    A) 5 cm
    B) 6 cm
    C) 7 cm
    D) 25 cm
    E) 49 cm
    
    CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS
    
    QUESTÃO 47
    
    A fotossíntese é o processo pelo qual as plantas convertem luz solar
    em energia química.
    
    Assinale a equação correta da fotossíntese:
    A) 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂
    B) C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O
    C) 6O₂ + C₆H₁₂O₆ → 6CO₂ + 6H₂O
    D) CO₂ + H₂O → C₆H₁₂O₆ + O₂
    E) 2H₂O → 2H₂ + O₂
    """
    
    chunks = intelligent_chunk_text(texto_temas_mistos, ChunkingStrategy.SEMANTIC_GROUPS)
    
    print(f"📊 RESULTADOS:")
    print(f"   Total de chunks: {len(chunks)}")
    print(f"   Estratégia: {ChunkingStrategy.SEMANTIC_GROUPS.value}")
    
    # Analisa agrupamento por temas
    themes = {}
    for chunk in chunks:
        theme = chunk.metadata.subject_area or "Geral"
        if theme not in themes:
            themes[theme] = []
        themes[theme].append(chunk)
    
    print(f"\n🏷️ AGRUPAMENTO POR TEMAS:")
    for theme, theme_chunks in themes.items():
        print(f"   📚 {theme}: {len(theme_chunks)} chunks")
        for chunk in theme_chunks:
            questions = ", ".join(map(str, chunk.metadata.question_numbers))
            print(f"      📝 Questões {questions} ({chunk.chunk_size} chars)")
    
    return chunks

def test_contextual_overlap_chunking():
    """Teste de chunking com sobreposição contextual"""
    print("\n🔍 TESTE 3: Chunking com Sobreposição Contextual")
    print("=" * 60)
    
    texto_sequencial = """
    QUESTÃO 88
    
    O aquecimento global é um fenômeno climático caracterizado pelo aumento
    da temperatura média do planeta Terra. Este processo tem sido intensificado
    pelas atividades humanas, especialmente a emissão de gases do efeito estufa.
    
    A principal causa do aquecimento global atual é:
    A) a variação natural do clima.
    B) a atividade solar intensa.
    C) a emissão de gases do efeito estufa.
    D) as erupções vulcânicas.
    E) a mudança na órbita terrestre.
    
    QUESTÃO 89
    
    Com base no contexto anterior sobre aquecimento global, sabemos que
    os gases do efeito estufa são os principais responsáveis por este fenômeno.
    Entre esses gases, o dióxido de carbono (CO₂) é o mais abundante.
    
    Qual atividade humana mais contribui para a emissão de CO₂?
    A) agricultura intensiva.
    B) queima de combustíveis fósseis.
    C) desmatamento das florestas.
    D) criação de gado bovino.
    E) uso de fertilizantes químicos.
    
    QUESTÃO 90
    
    Continuando a discussão sobre mudanças climáticas, é importante considerar
    as consequências do aumento das emissões de CO₂. Uma das principais
    consequências é o derretimento das geleiras polares.
    
    O derretimento das geleiras pode causar:
    A) diminuição do nível dos oceanos.
    B) aumento do nível dos oceanos.
    C) estabilização do clima global.
    D) redução da temperatura global.
    E) eliminação dos gases do efeito estufa.
    """
    
    chunks = intelligent_chunk_text(texto_sequencial, ChunkingStrategy.CONTEXTUAL_OVERLAP)
    
    print(f"📊 RESULTADOS:")
    print(f"   Total de chunks: {len(chunks)}")
    print(f"   Estratégia: {ChunkingStrategy.CONTEXTUAL_OVERLAP.value}")
    
    print(f"\n🔗 ANÁLISE DE SOBREPOSIÇÃO CONTEXTUAL:")
    for i, chunk in enumerate(chunks, 1):
        print(f"   📝 Chunk {i} (Questão {chunk.metadata.question_numbers}):")
        
        if chunk.context_before:
            print(f"      ⬅️ Contexto anterior: {len(chunk.context_before)} caracteres")
            preview_before = chunk.context_before[:60] + "..." if len(chunk.context_before) > 60 else chunk.context_before
            print(f"         Preview: {preview_before}")
        
        if chunk.context_after:
            print(f"      ➡️ Contexto posterior: {len(chunk.context_after)} caracteres")
            preview_after = chunk.context_after[:60] + "..." if len(chunk.context_after) > 60 else chunk.context_after
            print(f"         Preview: {preview_after}")
        
        # Analisa metadados de sobreposição
        overlap_info = chunk.metadata.overlapping_context
        if overlap_info:
            print(f"      📊 Sobreposição:")
            print(f"         Tem contexto anterior: {overlap_info.get('has_before', False)}")
            print(f"         Tem contexto posterior: {overlap_info.get('has_after', False)}")
    
    return chunks

def test_adaptive_size_chunking():
    """Teste de chunking com tamanho adaptativo"""
    print("\n🔍 TESTE 4: Chunking com Tamanho Adaptativo")
    print("=" * 60)
    
    texto_tamanhos_variados = """
    QUESTÃO 100
    
    Questão curta.
    
    A) A
    B) B
    
    QUESTÃO 101
    
    Esta é uma questão significativamente mais longa que requer uma análise 
    mais detalhada do conteúdo. O texto é extenso e contém múltiplas informações
    que devem ser consideradas em conjunto para uma compreensão adequada.
    A questão aborda conceitos complexos que se inter-relacionam e formam
    um conjunto coeso de conhecimentos. É importante manter toda esta
    informação junta para preservar o contexto semântico completo.
    
    Considerando todo o contexto apresentado, assinale a alternativa correta:
    
    A) Primeira alternativa com texto mais longo que explica detalhadamente
       os conceitos envolvidos na questão apresentada.
    B) Segunda alternativa que também contém informações extensas sobre
       o tema abordado na questão.
    C) Terceira opção com explicação completa e detalhada dos elementos
       relevantes para a resolução do problema proposto.
    D) Quarta alternativa apresentando uma análise aprofundada dos aspectos
       teóricos e práticos relacionados ao assunto.
    E) Quinta e última opção com considerações finais sobre o tema
       e suas implicações no contexto geral da disciplina.
    
    QUESTÃO 102
    
    Questão média.
    
    Texto explicativo de tamanho moderado.
    
    A) Opção A
    B) Opção B
    C) Opção C
    D) Opção D
    E) Opção E
    """
    
    chunks = intelligent_chunk_text(texto_tamanhos_variados, ChunkingStrategy.ADAPTIVE_SIZE)
    
    print(f"📊 RESULTADOS:")
    print(f"   Total de chunks: {len(chunks)}")
    print(f"   Estratégia: {ChunkingStrategy.ADAPTIVE_SIZE.value}")
    
    print(f"\n📏 ANÁLISE DE TAMANHOS ADAPTATIVOS:")
    sizes = []
    for i, chunk in enumerate(chunks, 1):
        size = chunk.chunk_size
        sizes.append(size)
        
        # Classifica tamanho
        if size < 200:
            size_class = "Pequeno"
        elif size < 800:
            size_class = "Médio"
        else:
            size_class = "Grande"
        
        print(f"   📝 Chunk {i}: {size} chars ({size_class})")
        print(f"      Questões: {chunk.metadata.question_numbers}")
        print(f"      Qualidade: {chunk.quality_score:.1%}")
    
    if sizes:
        avg_size = sum(sizes) / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        
        print(f"\n📊 ESTATÍSTICAS DE TAMANHO:")
        print(f"   Média: {avg_size:.0f} caracteres")
        print(f"   Mínimo: {min_size} caracteres")
        print(f"   Máximo: {max_size} caracteres")
        print(f"   Variação: {max_size - min_size} caracteres")
    
    return chunks

def test_mixed_strategy_chunking():
    """Teste de estratégia mista de chunking"""
    print("\n🔍 TESTE 5: Estratégia Mista de Chunking")
    print("=" * 60)
    
    texto_complexo = """
    LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS
    
    Texto base para as questões 61 a 63
    
    A comunicação digital transformou significativamente as relações sociais
    no século XXI. As redes sociais, aplicativos de mensagens e plataformas
    de compartilhamento de conteúdo criaram novas formas de interação humana.
    
    QUESTÃO 61
    
    Com base no texto, a principal transformação das comunicações digitais foi:
    A) o fim das comunicações presenciais.
    B) a criação de novas formas de interação.
    C) a substituição completa da escrita.
    D) a eliminação das diferenças culturais.
    E) o aumento da velocidade de internet.
    
    QUESTÃO 62
    
    As redes sociais mencionadas no texto representam:
    A) apenas entretenimento para jovens.
    B) ferramentas exclusivas de marketing.
    C) plataformas de interação social digital.
    D) substitutos para a educação formal.
    E) sistemas de controle governamental.
    
    QUESTÃO 63
    
    O impacto das comunicações digitais nas relações sociais pode ser considerado:
    A) insignificante para a sociedade atual.
    B) limitado apenas ao ambiente profissional.
    C) restrito à população mais jovem.
    D) significativo para toda a sociedade.
    E) prejudicial em todos os aspectos.
    
    MATEMÁTICA E SUAS TECNOLOGIAS
    
    QUESTÃO 64
    
    Uma nova área de conhecimento requer análise diferente.
    Calcule a área de um círculo com raio 5 cm.
    
    A) 25π cm²
    B) 10π cm²
    C) 5π cm²
    D) 15π cm²
    E) 20π cm²
    """
    
    chunks = intelligent_chunk_text(texto_complexo, ChunkingStrategy.MIXED_STRATEGY)
    
    print(f"📊 RESULTADOS:")
    print(f"   Total de chunks: {len(chunks)}")
    print(f"   Estratégia: {ChunkingStrategy.MIXED_STRATEGY.value}")
    
    print(f"\n🎯 ANÁLISE DA ESTRATÉGIA MISTA:")
    
    # Analisa tipos de chunks criados
    chunk_types = {}
    for chunk in chunks:
        chunk_type = chunk.metadata.chunk_type
        if chunk_type not in chunk_types:
            chunk_types[chunk_type] = 0
        chunk_types[chunk_type] += 1
    
    print(f"   📊 Tipos de chunks criados:")
    for chunk_type, count in chunk_types.items():
        print(f"      {chunk_type}: {count} chunks")
    
    # Analisa agrupamentos de questões
    print(f"\n   📝 Agrupamento de questões:")
    for i, chunk in enumerate(chunks, 1):
        questions = chunk.metadata.question_numbers
        if questions:
            if len(questions) == 1:
                print(f"      Chunk {i}: Questão individual {questions[0]}")
            else:
                print(f"      Chunk {i}: Questões agrupadas {questions}")
        else:
            print(f"      Chunk {i}: Conteúdo base/contextual")
    
    return chunks

def test_chunking_quality_metrics():
    """Teste de métricas de qualidade do chunking"""
    print("\n🔍 TESTE 6: Métricas de Qualidade do Chunking")
    print("=" * 60)
    
    texto_qualidade = """
    QUESTÃO 75
    
    Questão completa e bem estruturada com todos os elementos necessários
    para uma análise adequada. Possui enunciado claro, contexto relevante
    e alternativas bem definidas.
    
    Assinale a alternativa correta:
    
    A) Alternativa A com conteúdo adequado.
    B) Alternativa B com informação relevante.
    C) Alternativa C com explicação clara.
    D) Alternativa D com detalhes importantes.
    E) Alternativa E com conclusão apropriada.
    
    QUESTÃO 76
    
    Questão incompleta sem alter
    
    QUESTÃO 77
    
    A) Apenas alternativas sem enunciado
    B) Sem contexto adequado
    C) Estrutura problemática
    """
    
    # Testa diferentes estratégias para comparar qualidade
    strategies = [
        ChunkingStrategy.QUESTION_BASED,
        ChunkingStrategy.SEMANTIC_GROUPS,
        ChunkingStrategy.CONTEXTUAL_OVERLAP
    ]
    
    strategy_results = {}
    
    for strategy in strategies:
        chunker = IntelligentChunker(strategy)
        chunks = chunker.chunk_text(texto_qualidade)
        stats = chunker.get_chunking_stats()
        
        strategy_results[strategy.value] = {
            "chunks_count": len(chunks),
            "avg_quality": stats.get("avg_quality_score", 0),
            "avg_size": stats.get("avg_chunk_size", 0),
            "chunks": chunks
        }
    
    print(f"📊 COMPARAÇÃO DE QUALIDADE POR ESTRATÉGIA:")
    print(f"{'Estratégia':<20} {'Chunks':<8} {'Qualidade':<12} {'Tam. Médio':<12}")
    print("-" * 60)
    
    for strategy_name, results in strategy_results.items():
        print(f"{strategy_name:<20} {results['chunks_count']:<8} "
              f"{results['avg_quality']:<12.1%} {results['avg_size']:<12.0f}")
    
    # Analisa qualidade individual dos chunks
    print(f"\n🔍 ANÁLISE DETALHADA DE QUALIDADE:")
    
    best_strategy = max(strategy_results.items(), key=lambda x: x[1]["avg_quality"])
    best_chunks = best_strategy[1]["chunks"]
    
    print(f"   🥇 Melhor estratégia: {best_strategy[0]}")
    print(f"   📊 Qualidade média: {best_strategy[1]['avg_quality']:.1%}")
    
    for i, chunk in enumerate(best_chunks, 1):
        print(f"\n   📝 Chunk {i} (Qualidade: {chunk.quality_score:.1%}):")
        print(f"      Questões: {chunk.metadata.question_numbers}")
        print(f"      Alternativas: {len(chunk.alternatives)}")
        print(f"      Comandos: {len(chunk.commands)}")
        print(f"      Tamanho: {chunk.chunk_size} chars")
    
    return strategy_results

def demonstrate_chunking_export():
    """Demonstra exportação de chunks estruturados"""
    print("\n🔍 TESTE 7: Exportação de Chunks Estruturados")
    print("=" * 60)
    
    texto_exemplo = """
    QUESTÃO 50
    
    O sistema solar é composto por oito planetas que orbitam o Sol.
    
    Qual é o planeta mais próximo do Sol?
    A) Mercúrio
    B) Vênus
    C) Terra
    D) Marte
    E) Júpiter
    """
    
    chunks = intelligent_chunk_text(texto_exemplo, ChunkingStrategy.QUESTION_BASED)
    
    # Converte chunks para formato exportável
    export_data = {
        "chunking_metadata": {
            "strategy": ChunkingStrategy.QUESTION_BASED.value,
            "total_chunks": len(chunks),
            "processing_timestamp": chunks[0].metadata.processing_timestamp if chunks else None
        },
        "chunks": []
    }
    
    for chunk in chunks:
        chunk_data = {
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
        }
        export_data["chunks"].append(chunk_data)
    
    # Salva em arquivo JSON
    output_file = "chunks_inteligentes_exemplo.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"📁 Chunks exportados para: {output_file}")
    print(f"📊 Total de chunks: {len(chunks)}")
    
    # Mostra preview da estrutura
    print(f"\n📄 PREVIEW DA ESTRUTURA EXPORTADA:")
    print("```json")
    preview = {
        "chunking_metadata": export_data["chunking_metadata"],
        "chunks_count": len(export_data["chunks"]),
        "first_chunk_preview": {
            "chunk_id": export_data["chunks"][0]["chunk_id"] if export_data["chunks"] else None,
            "question_numbers": export_data["chunks"][0]["question_numbers"] if export_data["chunks"] else None,
            "alternatives_count": len(export_data["chunks"][0]["alternatives"]) if export_data["chunks"] else 0,
            "quality_score": export_data["chunks"][0]["quality_score"] if export_data["chunks"] else 0
        }
    }
    print(json.dumps(preview, indent=2, ensure_ascii=False))
    print("```")

def run_all_chunking_tests():
    """Executa todos os testes de chunking inteligente"""
    print("🚀 SISTEMA DE CHUNKING INTELIGENTE - TESTES COMPLETOS")
    print("=" * 80)
    print("🎯 Semantic chunking, chunks por questão e overlapping contextual")
    print()
    
    # Executa todos os testes
    test_question_based_chunking()
    test_semantic_groups_chunking()
    test_contextual_overlap_chunking()
    test_adaptive_size_chunking()
    test_mixed_strategy_chunking()
    test_chunking_quality_metrics()
    demonstrate_chunking_export()
    
    print("\n" + "=" * 80)
    print("✅ TODOS OS TESTES DE CHUNKING CONCLUÍDOS!")
    print()
    print("🎉 PRINCIPAIS FUNCIONALIDADES DEMONSTRADAS:")
    print("   • 📝 Chunking por questão (preserva integridade)")
    print("   • 🏷️ Agrupamento semântico (por tema/área)")
    print("   • 🔗 Sobreposição contextual (contexto entre chunks)")
    print("   • 📏 Tamanho adaptativo (baseado no conteúdo)")
    print("   • 🎯 Estratégia mista (combinação inteligente)")
    print("   • 📊 Métricas de qualidade (scores de confiança)")
    print("   • 📁 Exportação estruturada (JSON completo)")
    print()
    print("🏆 RESULTADO: Chunks semanticamente coerentes e contextualizados!")

if __name__ == "__main__":
    run_all_chunking_tests() 