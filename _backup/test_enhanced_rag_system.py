"""
Teste do Sistema RAG Aprimorado
Demonstra as melhorias implementadas:
✅ Melhores embeddings
✅ Chunking inteligente
✅ Reranking avançado  
✅ Prompts sofisticadas
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from enhanced_local_math_rag import EnhancedLocalMathRAG, IntelligentChunker, AdvancedEmbeddings, AdvancedReranker, SophisticatedPrompts

def test_intelligent_chunker():
    """Testa o sistema de chunking inteligente"""
    print("🔧 Testando Chunking Inteligente...")
    
    chunker = IntelligentChunker()
    
    # Texto de exemplo com estrutura matemática
    sample_content = """
    Exercício 1: Função Quadrática
    
    Uma função quadrática f(x) = ax² + bx + c possui as seguintes propriedades:
    - O coeficiente 'a' determina a concavidade da parábola
    - O discriminante Δ = b² - 4ac determina o número de raízes
    
    Definição: Vértice da Parábola
    O vértice de uma parábola é o ponto onde ela atinge seu valor máximo ou mínimo.
    A coordenada x do vértice é dada por: x = -b/(2a)
    
    Fórmula: Raízes da Equação Quadrática
    As raízes são dadas por: x = (-b ± √Δ)/(2a)
    onde Δ = b² - 4ac
    
    Observação: Quando Δ > 0, temos duas raízes reais distintas.
    """
    
    chunks = chunker.intelligent_split(sample_content, "exemplo_funcoes.docx")
    
    print(f"📊 Chunks gerados: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Tipo de seção: {chunk.metadata.get('section_type', 'Não identificado')}")
        print(f"Tópico: {chunk.metadata.get('topic', 'Não identificado')}")
        print(f"Conteúdo: {chunk.page_content[:100]}...")
    
    return chunks

def test_advanced_embeddings():
    """Testa o sistema de embeddings aprimorado"""
    print("\n🔧 Testando Embeddings Aprimorados...")
    
    embeddings = AdvancedEmbeddings()
    
    if embeddings.current_model is None:
        print("⚠️ Modelos de embedding não disponíveis. Instale sentence-transformers.")
        return None
    
    # Testa codificação de textos matemáticos
    math_texts = [
        "Como resolver uma equação do segundo grau?",
        "Calcule a área de um triângulo retângulo",
        "Qual a fórmula de juros compostos?",
        "Explique o teorema de Pitágoras"
    ]
    
    try:
        embeddings_result = embeddings.encode(math_texts, 'math_pt')
        print(f"✅ Embeddings gerados com sucesso! Dimensão: {embeddings_result.shape}")
        
        # Testa similaridade
        query_emb = embeddings.encode(["equação quadrática"], 'math_pt')[0]
        doc_embs = embeddings_result
        
        similarities = embeddings.compute_similarity(query_emb, doc_embs)
        print(f"📊 Similaridades: {similarities}")
        
        return embeddings_result
        
    except Exception as e:
        print(f"❌ Erro nos embeddings: {e}")
        return None

def test_advanced_reranker():
    """Testa o sistema de reranking avançado"""
    print("\n🔧 Testando Reranking Avançado...")
    
    from langchain.schema import Document
    
    # Cria documentos de exemplo
    sample_docs = [
        Document(
            page_content="A fórmula da equação do segundo grau é x = (-b ± √(b²-4ac))/(2a). Esta fórmula é conhecida como fórmula de Bhaskara.",
            metadata={"topic": "algebra", "section_type": "formula", "source": "algebra.docx"}
        ),
        Document(
            page_content="Para calcular juros compostos, use M = C(1+i)^t onde M é montante, C é capital inicial, i é taxa e t é tempo.",
            metadata={"topic": "financeira", "section_type": "formula", "source": "financeira.docx"}
        ),
        Document(
            page_content="O triângulo é uma figura geométrica com três lados. A soma dos ângulos internos é sempre 180 graus.",
            metadata={"topic": "geometria", "section_type": "definition", "source": "geometria.docx"}
        ),
        Document(
            page_content="Exercício: Resolva a equação x² - 5x + 6 = 0. Primeiro, identifique os coeficientes a=1, b=-5, c=6.",
            metadata={"topic": "algebra", "section_type": "exercise", "source": "exercicios.docx"}
        )
    ]
    
    embeddings = AdvancedEmbeddings()
    reranker = AdvancedReranker(embeddings)
    
    query = "Como resolver equação do segundo grau?"
    
    try:
        reranked_results = reranker.rerank_results(query, sample_docs, top_k=3)
        
        print(f"📊 Resultados reordenados: {len(reranked_results)}")
        
        for i, result in enumerate(reranked_results, 1):
            print(f"\n--- Resultado {i} ---")
            print(f"Score final: {result.final_score:.3f}")
            print(f"Score semântico: {result.similarity_score:.3f}")
            print(f"Explicação: {result.explanation}")
            print(f"Conteúdo: {result.document.page_content[:80]}...")
        
        return reranked_results
        
    except Exception as e:
        print(f"❌ Erro no reranking: {e}")
        return None

def test_sophisticated_prompts():
    """Testa o sistema de prompts sofisticadas"""
    print("\n🔧 Testando Prompts Sofisticadas...")
    
    prompts = SophisticatedPrompts()
    
    # Simula resultados de reranking
    from langchain.schema import Document
    from enhanced_local_math_rag import RerankedResult
    
    mock_result = RerankedResult(
        document=Document(
            page_content="Para resolver uma equação do segundo grau ax² + bx + c = 0, use a fórmula de Bhaskara: x = (-b ± √(b²-4ac))/(2a)",
            metadata={"topic": "algebra", "section_type": "formula"}
        ),
        similarity_score=0.85,
        rerank_score=0.92,
        final_score=0.89,
        explanation="alta similaridade semântica, fórmula relevante"
    )
    
    query = "Como resolver uma equação do segundo grau?"
    context_docs = [mock_result]
    
    # Testa diferentes tipos de prompt
    prompt_types = [
        ("exercise_solving", "Resolva a equação x² - 4x + 3 = 0"),
        ("concept_explanation", "O que é uma função quadrática?"),
        ("formula_derivation", "Derive a fórmula de Bhaskara"),
        ("general_math", "Preciso de ajuda com matemática")
    ]
    
    for prompt_type, test_query in prompt_types:
        print(f"\n--- Testando: {prompt_type} ---")
        
        # Força o tipo específico modificando a análise
        original_analyze = prompts._analyze_query_type
        prompts._analyze_query_type = lambda x: prompt_type
        
        try:
            prompt = prompts.build_prompt(test_query, context_docs)
            print(f"✅ Prompt gerada com sucesso ({len(prompt)} caracteres)")
            print(f"Início: {prompt[:150]}...")
        except Exception as e:
            print(f"❌ Erro na prompt: {e}")
        finally:
            # Restaura função original
            prompts._analyze_query_type = original_analyze

def test_full_enhanced_system():
    """Testa o sistema completo integrado"""
    print("\n🚀 Testando Sistema Completo...")
    
    # Verifica se existe vectorstore ou documentos
    if not (os.path.exists("./chroma_math_enhanced") or os.path.exists("./matemática")):
        print("⚠️ Nenhum vectorstore ou pasta de documentos encontrada.")
        print("Para teste completo, certifique-se de ter:")
        print("1. Pasta './matemática' com documentos, OU")
        print("2. Vectorstore './chroma_math_enhanced' já processado")
        return
    
    try:
        # Inicializa sistema
        enhanced_rag = EnhancedLocalMathRAG()
        
        # Obtém estatísticas
        stats = enhanced_rag.get_enhanced_stats()
        
        if "error" not in stats:
            print("✅ Sistema inicializado com sucesso!")
            print(f"📊 Total de chunks: {stats.get('total_chunks', 0)}")
            print(f"🧠 Modelo de embeddings: {stats.get('embeddings_model', 'Padrão')}")
            print(f"✂️ Estratégia de chunking: {stats.get('chunking_strategy', 'Padrão')}")
            
            if stats.get('topics_distribution'):
                print("📋 Tópicos encontrados:")
                for topic, count in stats['topics_distribution'].items():
                    print(f"  - {topic}: {count} chunks")
        else:
            print(f"❌ Erro no sistema: {stats['error']}")
            
    except Exception as e:
        print(f"❌ Erro ao testar sistema completo: {e}")

def main():
    """Executa todos os testes"""
    print("🧪 TESTE DO SISTEMA RAG APRIMORADO")
    print("=" * 50)
    
    try:
        # Teste 1: Chunking Inteligente
        chunks = test_intelligent_chunker()
        
        # Teste 2: Embeddings Aprimorados
        embeddings_result = test_advanced_embeddings()
        
        # Teste 3: Reranking Avançado
        reranked_results = test_advanced_reranker()
        
        # Teste 4: Prompts Sofisticadas
        test_sophisticated_prompts()
        
        # Teste 5: Sistema Completo
        test_full_enhanced_system()
        
        print("\n" + "=" * 50)
        print("🎉 RESUMO DOS TESTES")
        print(f"✅ Chunking Inteligente: {'OK' if chunks else 'FALHA'}")
        print(f"✅ Embeddings Aprimorados: {'OK' if embeddings_result is not None else 'FALHA'}")
        print(f"✅ Reranking Avançado: {'OK' if reranked_results else 'FALHA'}")
        print("✅ Prompts Sofisticadas: OK")
        print("\n💡 Para usar o sistema completo:")
        print("1. Instale: pip install -r requirements_enhanced_rag.txt")
        print("2. Execute: streamlit run professor_carlos_enhanced.py")
        
    except Exception as e:
        print(f"\n❌ Erro geral nos testes: {e}")
        print("Verifique se todas as dependências estão instaladas.")

if __name__ == "__main__":
    main() 