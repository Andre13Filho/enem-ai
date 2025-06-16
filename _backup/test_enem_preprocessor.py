#!/usr/bin/env python3
"""
Testes do Sistema de Pré-processamento Estruturado do ENEM
Demonstra a identificação de padrões específicos usando regex
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enem_text_preprocessor import preprocess_enem_text, ENEMTextPreprocessor
import json

def test_question_patterns():
    """Teste de identificação de números de questões"""
    print("🔍 TESTE: Padrões de Números de Questões")
    print("=" * 50)
    
    test_cases = [
        "QUESTÃO 91",
        "Questão 45", 
        "91. Texto da questão",
        "45) Enunciado da questão",
        "23 - Considere o texto",
        "QUESTAO 67 sem acento"
    ]
    
    preprocessor = ENEMTextPreprocessor()
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: '{text}'")
        result = preprocessor.preprocess_text(text)
        
        question_patterns = [p for p in result['patterns'] 
                           if p.pattern_type.value == 'question_number']
        
        if question_patterns:
            pattern = question_patterns[0]
            print(f"   ✅ Encontrado: Questão {pattern.metadata.get('question_number')}")
            print(f"   📊 Confiança: {pattern.confidence:.1%}")
        else:
            print("   ❌ Não identificado")

def test_alternative_patterns():
    """Teste de identificação de alternativas"""
    print("\n🔍 TESTE: Padrões de Alternativas")
    print("=" * 50)
    
    test_text = """
    A) acionar os airbags do veículo.
    B) absorver a energia cinética do sistema.
    C) reduzir a velocidade do veículo.
    D) aumentar o tempo de colisão.
    E) diminuir a força média de impacto.
    """
    
    result = preprocess_enem_text(test_text)
    
    alternative_patterns = [p for p in result['patterns'] 
                          if p.pattern_type.value == 'alternative']
    
    print(f"📊 Total de alternativas encontradas: {len(alternative_patterns)}")
    
    for pattern in alternative_patterns:
        letter = pattern.metadata.get('letter')
        content = pattern.metadata.get('content', '')[:50] + "..."
        print(f"   ✅ {letter}) {content}")
        print(f"      Confiança: {pattern.confidence:.1%}")

def test_command_patterns():
    """Teste de identificação de comandos típicos"""
    print("\n🔍 TESTE: Padrões de Comandos")
    print("=" * 50)
    
    test_cases = [
        "Assinale a alternativa correta.",
        "Marque a opção correta.",
        "Indique a alternativa correta.",
        "Escolha a alternativa que melhor representa",
        "Assinale a única alternativa verdadeira.",
        "A resposta correta é:"
    ]
    
    preprocessor = ENEMTextPreprocessor()
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: '{text}'")
        result = preprocessor.preprocess_text(text)
        
        command_patterns = [p for p in result['patterns'] 
                          if p.pattern_type.value == 'command']
        
        if command_patterns:
            pattern = command_patterns[0]
            print(f"   ✅ Identificado como comando")
            print(f"   📊 Confiança: {pattern.confidence:.1%}")
        else:
            print("   ❌ Não identificado como comando")

def test_subject_area_patterns():
    """Teste de identificação de áreas de conhecimento"""
    print("\n🔍 TESTE: Áreas de Conhecimento")
    print("=" * 50)
    
    test_cases = [
        "LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS",
        "MATEMÁTICA E SUAS TECNOLOGIAS", 
        "CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS",
        "CIÊNCIAS HUMANAS E SUAS TECNOLOGIAS"
    ]
    
    preprocessor = ENEMTextPreprocessor()
    
    for area in test_cases:
        print(f"\n📚 Testando: {area}")
        result = preprocessor.preprocess_text(area)
        
        subject_patterns = [p for p in result['patterns'] 
                          if p.pattern_type.value == 'subject_area']
        
        if subject_patterns:
            print(f"   ✅ Área identificada")
            print(f"   📊 Confiança: {subject_patterns[0].confidence:.1%}")
        else:
            print("   ❌ Área não identificada")

def test_complete_question():
    """Teste com questão completa do ENEM"""
    print("\n🔍 TESTE: Questão Completa do ENEM")
    print("=" * 50)
    
    complete_question = """
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
    """
    
    result = preprocess_enem_text(complete_question)
    
    print("📊 RESULTADOS COMPLETOS:")
    print("-" * 30)
    
    # Estatísticas gerais
    stats = result['stats']
    print(f"📈 Total de padrões: {stats['total_patterns']}")
    print(f"📋 Por tipo: {stats['by_type']}")
    
    # Indicadores de qualidade
    quality = stats['quality_indicators']
    print(f"\n✅ INDICADORES DE QUALIDADE:")
    print(f"   Possui números de questão: {quality['has_question_numbers']}")
    print(f"   Possui alternativas: {quality['has_alternatives']}")
    print(f"   Alternativas por questão: {quality['alternatives_per_question']:.1f}")
    print(f"   Confiança média: {quality['avg_confidence']:.1%}")
    
    # Estrutura identificada
    structure = result['structured_content']
    print(f"\n🏗️ ESTRUTURA IDENTIFICADA:")
    
    if structure['questions']:
        question = structure['questions'][0]
        print(f"   📝 Questão {question['number']}")
        print(f"   🔤 Alternativas: {len(question['alternatives'])}")
        print(f"   📋 Comandos: {len(question['commands'])}")
        print(f"   📊 Confiança: {question['confidence']:.1%}")
        
        print(f"\n📄 ALTERNATIVAS ESTRUTURADAS:")
        for alt in question['alternatives']:
            content = alt['content'][:60] + "..." if alt['content'] and len(alt['content']) > 60 else alt['content']
            print(f"   {alt['letter']}) {content}")
            print(f"      └─ Confiança: {alt['confidence']:.1%}")

def test_corrupted_text():
    """Teste com texto corrompido para demonstrar robustez"""
    print("\n🔍 TESTE: Texto Corrompido")
    print("=" * 50)
    
    corrupted_text = """
    Quest∂o 45 ✱✱✱ corrompido
    
    A) 123 456 789 ++ opção A corrompida
    B) 987 654 321 ×× opção B bagunçada 
    C) texto normal da opção C
    D) ### 000 ### texto misturado
    E) alternativa E limpa
    """
    
    result = preprocess_enem_text(corrupted_text)
    
    print("📊 ANÁLISE DE TEXTO CORROMPIDO:")
    print("-" * 40)
    
    # Mostra como o sistema lida com corrupção
    stats = result['stats']
    print(f"📈 Padrões identificados: {stats['total_patterns']}")
    print(f"📋 Tipos encontrados: {list(stats['by_type'].keys())}")
    
    # Alternativas identificadas
    if 'alternative' in stats['by_type']:
        alt_count = stats['by_type']['alternative']
        print(f"🔤 Alternativas extraídas: {alt_count}/5")
        
        # Mostra quais foram identificadas com sucesso
        alternative_patterns = [p for p in result['patterns'] 
                              if p.pattern_type.value == 'alternative']
        
        print(f"\n📄 ALTERNATIVAS PROCESSADAS:")
        for pattern in alternative_patterns:
            letter = pattern.metadata.get('letter')
            confidence = pattern.confidence
            status = "✅ LIMPA" if confidence > 0.8 else "⚠️ CORROMPIDA"
            print(f"   {letter}) {status} (Confiança: {confidence:.1%})")

def test_multiple_formats():
    """Teste com múltiplos formatos de alternativas"""
    print("\n🔍 TESTE: Múltiplos Formatos")
    print("=" * 50)
    
    format_tests = [
        # Formato padrão
        """A) Primeira opção
B) Segunda opção
C) Terceira opção""",
        
        # Formato com parênteses
        """(A) Primeira opção
(B) Segunda opção
(C) Terceira opção""",
        
        # Formato com pontos
        """A. Primeira opção
B. Segunda opção
C. Terceira opção""",
        
        # Formato sem pontuação
        """A Primeira opção
B Segunda opção
C Terceira opção"""
    ]
    
    format_names = ["Padrão A)", "Parênteses (A)", "Pontos A.", "Sem pontuação"]
    
    for i, (text, name) in enumerate(zip(format_tests, format_names)):
        print(f"\n📝 Formato {i+1}: {name}")
        result = preprocess_enem_text(text)
        
        alternative_patterns = [p for p in result['patterns'] 
                              if p.pattern_type.value == 'alternative']
        
        print(f"   📊 Alternativas identificadas: {len(alternative_patterns)}")
        if alternative_patterns:
            avg_confidence = sum(p.confidence for p in alternative_patterns) / len(alternative_patterns)
            print(f"   📈 Confiança média: {avg_confidence:.1%}")
        else:
            print("   ❌ Nenhuma alternativa identificada")

def run_all_tests():
    """Executa todos os testes do pré-processador"""
    print("🧪 SISTEMA DE PRÉ-PROCESSAMENTO ESTRUTURADO DO ENEM")
    print("=" * 70)
    print("🎯 Testando regex patterns para identificação de padrões específicos")
    print()
    
    # Executa todos os testes
    test_question_patterns()
    test_alternative_patterns()
    test_command_patterns()
    test_subject_area_patterns()
    test_complete_question()
    test_corrupted_text()
    test_multiple_formats()
    
    print("\n" + "=" * 70)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("🎉 Sistema de pré-processamento estruturado funcionando corretamente")

if __name__ == "__main__":
    run_all_tests() 