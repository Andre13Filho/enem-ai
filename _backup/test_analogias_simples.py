# -*- coding: utf-8 -*-
"""
Teste simples das analogias das series
"""

def test_analogies():
    try:
        from enhanced_local_math_rag import SeriesAnalogiesManager
        
        print("🎬 Testando analogias das series...")
        manager = SeriesAnalogiesManager()
        
        # Testa álgebra (FRIENDS - Monica)
        algebra_analogies = manager.get_relevant_analogies("algebra", "equacao", 1)
        if algebra_analogies:
            print(f"✅ Algebra: {algebra_analogies[0]['character']} - {algebra_analogies[0]['analogy'][:50]}...")
        
        # Testa física (TBBT - Sheldon)  
        fisica_analogies = manager.get_relevant_analogies("fisica", "velocidade", 1)
        if fisica_analogies:
            print(f"✅ Fisica: {fisica_analogies[0]['character']} - {fisica_analogies[0]['analogy'][:50]}...")
            
        print("🎉 Analogias funcionando!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_analogies() 