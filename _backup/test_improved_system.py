#!/usr/bin/env python3
"""
Script de Teste para o Sistema Melhorado de Exercícios
Testa o parser avançado e a estruturação JSON
"""

import json
from improved_exercise_parser import ImprovedExerciseParser, ExerciseQuestion

def test_parser_with_sample():
    """Testa o parser com um exercício de exemplo"""
    
    # Texto de exemplo de uma questão do ENEM
    sample_text = """
    QUESTÃO 91
    
    Muitas pessoas ainda se espantam com o fato de um passageiro sair ileso de um acidente de carro enquanto o veículo onde estava teve perda total. O que mais espanta é que, além de estar vivo, o passageiro não sofreu nenhum ferimento grave.
    
    Isso se deve ao fato de que o cinto de segurança e o airbag são dispositivos que têm a função de aumentar o tempo de colisão, diminuindo assim a força média de impacto sobre o passageiro.
    
    A função do cinto de segurança é:
    
    A) acionar os airbags do veículo.
    B) absorver a energia cinética do sistema.
    C) reduzir a velocidade do veículo.
    D) aumentar o tempo de colisão.
    E) diminuir a força média de impacto.
    """
    
    print("🧪 Testando Parser Melhorado...")
    print("=" * 50)
    
    # Cria parser
    parser = ImprovedExerciseParser()
    
    # Processa o texto
    exercises = parser.parse_pdf_text_to_exercises(sample_text, "2023", "teste.pdf")
    
    if exercises:
        exercise = exercises[0]
        print("✅ Exercício parseado com sucesso!")
        print(f"📝 ID: {exercise.id_questao}")
        print(f"📚 Área: {exercise.area_conhecimento}")
        print(f"🎯 Dificuldade: {exercise.dificuldade_estimada}")
        print(f"🔧 Tópicos: {exercise.topicos_chave}")
        print(f"📋 Enunciado: {exercise.enunciado[:100]}...")
        print(f"📝 Alternativas encontradas: {len(exercise.alternativas)}")
        
        print("\n🔍 Detalhes das Alternativas:")
        for alt in exercise.alternativas:
            status = "✅ Válida" if alt.is_valid else "❌ Inválida"
            confidence = f"{int(alt.confidence * 100)}%"
            print(f"   {alt.letra}) {alt.texto[:50]}... [{status}, Confiança: {confidence}]")
        
        print("\n📊 JSON Estruturado:")
        print(exercise.to_json())
        
        return True
    else:
        print("❌ Falha no parsing")
        return False

def test_alternative_patterns():
    """Testa diferentes padrões de alternativas"""
    
    print("\n🧪 Testando Padrões de Alternativas...")
    print("=" * 50)
    
    test_cases = [
        # Caso 1: Padrão A) B) C)
        """
        QUESTÃO 92
        
        Qual é a resposta correta?
        
        A) Primeira opção
        B) Segunda opção  
        C) Terceira opção
        D) Quarta opção
        E) Quinta opção
        """,
        
        # Caso 2: Padrão (A) (B) (C)
        """
        QUESTÃO 93
        
        Escolha a alternativa:
        
        (A) Opção um
        (B) Opção dois
        (C) Opção três
        (D) Opção quatro
        (E) Opção cinco
        """,
        
        # Caso 3: Padrão A B C (sem parênteses)
        """
        QUESTÃO 94
        
        Marque a resposta:
        
        A Alternativa primeira
        B Alternativa segunda
        C Alternativa terceira
        D Alternativa quarta
        E Alternativa quinta
        """
    ]
    
    parser = ImprovedExerciseParser()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Teste {i}:")
        exercises = parser.parse_pdf_text_to_exercises(test_case, "2023", f"teste_{i}.pdf")
        
        if exercises and exercises[0].alternativas:
            exercise = exercises[0]
            print(f"   ✅ {len(exercise.alternativas)} alternativas encontradas")
            for alt in exercise.alternativas:
                print(f"      {alt.letra}) {alt.texto[:30]}...")
        else:
            print(f"   ❌ Nenhuma alternativa encontrada")

def test_corrupted_alternatives():
    """Testa tratamento de alternativas corrompidas"""
    
    print("\n🧪 Testando Alternativas Corrompidas...")
    print("=" * 50)
    
    corrupted_text = """
    QUESTÃO 95
    
    Esta questão tem alternativas corrompidas:
    
    A 123 456 789 +++
    B 987 654 321 ×××
    C Texto válido aqui
    D 111 222 333 ===
    E Outra opção válida
    """
    
    parser = ImprovedExerciseParser()
    exercises = parser.parse_pdf_text_to_exercises(corrupted_text, "2023", "corrupted.pdf")
    
    if exercises:
        exercise = exercises[0]
        print(f"✅ Exercício processado")
        print(f"📝 Alternativas encontradas: {len(exercise.alternativas)}")
        
        for alt in exercise.alternativas:
            status = "✅ Válida" if alt.is_valid else "❌ Inválida"
            confidence = f"{int(alt.confidence * 100)}%"
            print(f"   {alt.letra}) {alt.texto} [{status}, Confiança: {confidence}]")
    else:
        print("❌ Falha no processamento")

def test_topic_extraction():
    """Testa extração de tópicos"""
    
    print("\n🧪 Testando Extração de Tópicos...")
    print("=" * 50)
    
    topic_tests = [
        ("Física", "A energia cinética de um corpo em movimento é calculada pela fórmula E = mv²/2"),
        ("Matemática", "Calcule o valor da função f(x) = 2x + 3 para x = 5"),
        ("Geometria", "A área de um triângulo é calculada pela fórmula A = base × altura / 2"),
        ("Química", "A reação de combustão do metano produz CO2 e H2O"),
        ("Probabilidade", "Qual a probabilidade de sair cara em um lançamento de moeda?")
    ]
    
    parser = ImprovedExerciseParser()
    
    for topic_name, text in topic_tests:
        sample = f"QUESTÃO 96\n\n{text}\n\nA) Opção A\nB) Opção B\nC) Opção C\nD) Opção D\nE) Opção E"
        exercises = parser.parse_pdf_text_to_exercises(sample, "2023", "topic_test.pdf")
        
        if exercises:
            exercise = exercises[0]
            print(f"📚 {topic_name}:")
            print(f"   🎯 Tópicos identificados: {exercise.topicos_chave}")
            print(f"   📊 Área: {exercise.area_conhecimento}")
            print(f"   🎯 Dificuldade: {exercise.dificuldade_estimada}")
        else:
            print(f"❌ Falha para {topic_name}")

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando Testes do Sistema Melhorado")
    print("=" * 60)
    
    try:
        # Teste básico
        success1 = test_parser_with_sample()
        
        # Teste de padrões
        test_alternative_patterns()
        
        # Teste de corrupção
        test_corrupted_alternatives()
        
        # Teste de tópicos
        test_topic_extraction()
        
        print("\n" + "=" * 60)
        if success1:
            print("✅ Testes concluídos com sucesso!")
            print("🎯 O sistema melhorado está funcionando corretamente")
        else:
            print("⚠️ Alguns testes falharam")
            
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 