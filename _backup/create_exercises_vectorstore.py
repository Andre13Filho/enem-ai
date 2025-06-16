#!/usr/bin/env python3
"""
Script para criar VectorStore dos exercícios do ENEM
"""

from enem_exercises_rag import ENEMExercisesRAG

def main():
    """Processa exercícios do ENEM e cria VectorStore"""
    
    print("🎯 ENEM Exercises RAG - Processamento de Exercícios")
    print("=" * 60)
    
    # Instancia sistema
    exercises_rag = ENEMExercisesRAG()
    
    # Verifica se já existe VectorStore
    print("🔍 Verificando VectorStore existente...")
    existing = exercises_rag.load_existing_vectorstore()
    
    if existing:
        print("✅ VectorStore de exercícios já existe!")
        stats = exercises_rag.get_stats()
        print(f"📊 Exercícios disponíveis: {stats['total_exercises']}")
        print(f"📅 Anos disponíveis: {', '.join(stats['available_years'])}")
        print(f"📚 Áreas: {', '.join(stats['subject_areas'])}")
        
        choice = input("\n🤔 Deseja reprocessar? (s/N): ").lower().strip()
        if choice != 's':
            print("✅ Mantendo VectorStore existente.")
            return
    
    # Processa documentos
    print("\n🚀 Iniciando processamento dos exercícios do ENEM...")
    success = exercises_rag.process_enem_documents()
    
    if success:
        print("\n🎉 Processamento concluído com sucesso!")
        
        # Mostra estatísticas
        stats = exercises_rag.get_stats()
        print(f"\n📊 Estatísticas finais:")
        print(f"   🎯 Total de exercícios: {stats['total_exercises']}")
        print(f"   📅 Anos processados: {', '.join(stats['available_years'])}")
        print(f"   📚 Áreas identificadas: {', '.join(stats['subject_areas'])}")
        print(f"   🏷️ Tópicos encontrados: {', '.join(stats['topics'][:10])}...")
        
        # Testa busca
        print(f"\n🔍 Testando busca...")
        test_results = exercises_rag.search_exercises_by_topic("função quadrática", "Matemática", k=2)
        if test_results:
            print(f"✅ Busca funcionando! Encontrados {len(test_results)} exercícios sobre função quadrática")
            for i, doc in enumerate(test_results, 1):
                year = doc.metadata.get("year", "N/A")
                question_num = doc.metadata.get("question_number", "N/A")
                print(f"   📝 {i}. ENEM {year} - Questão {question_num}")
        else:
            print("⚠️ Nenhum exercício encontrado no teste")
        
    else:
        print("❌ Falha no processamento dos exercícios")

if __name__ == "__main__":
    main() 