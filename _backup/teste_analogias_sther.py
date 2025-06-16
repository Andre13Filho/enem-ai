#!/usr/bin/env python3
"""
Teste do Sistema de Analogias da Sther
======================================

Testa se o Professor Carlos consegue detectar quando a Sther não entende
e usa analogias apropriadas das séries que ela gosta.
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sther_analogies_system import get_analogy_for_confused_sther, sther_analogies
    from professor_carlos_local import professor_carlos_local
except ImportError as e:
    print(f"❌ Erro: Não foi possível importar módulos necessários: {e}")
    sys.exit(1)

def teste_deteccao_confusao():
    """Testa se o sistema detecta quando a Sther está confusa"""
    
    print("🤔 TESTE: Detecção de Confusão da Sther")
    print("="*50)
    
    mensagens_confusas = [
        "Não entendi essa função quadrática",
        "Essa geometria está muito confusa para mim",
        "Pode explicar de novo sobre probabilidade?",
        "Não consigo entender triângulos",
        "Isso está muito difícil, Professor",
        "Estou perdida com essas equações",
        "Ajuda! Não sei como resolver isso"
    ]
    
    mensagens_normais = [
        "Como calcula área de triângulo?",
        "Qual a fórmula da função quadrática?",
        "Me explique sobre probabilidade",
        "Quero entender melhor geometria"
    ]
    
    print("\n📍 MENSAGENS QUE DEVEM DETECTAR CONFUSÃO:")
    for i, msg in enumerate(mensagens_confusas, 1):
        confused = sther_analogies.detect_confusion(msg)
        status = "✅ DETECTOU" if confused else "❌ NÃO DETECTOU"
        print(f"{i}. '{msg}' → {status}")
    
    print("\n📍 MENSAGENS QUE NÃO DEVEM DETECTAR CONFUSÃO:")
    for i, msg in enumerate(mensagens_normais, 1):
        confused = sther_analogies.detect_confusion(msg)
        status = "❌ DETECTOU (ERRO)" if confused else "✅ NÃO DETECTOU"
        print(f"{i}. '{msg}' → {status}")

def teste_analogias_por_topico():
    """Testa se o sistema encontra analogias por tópico"""
    
    print("\n\n🎬 TESTE: Analogias por Tópico")
    print("="*50)
    
    topicos_teste = [
        "Funções",
        "Geometria", 
        "Álgebra",
        "Estatística e Probabilidade",
        "Matemática Financeira",
        "Geral"
    ]
    
    for topico in topicos_teste:
        analogy = sther_analogies.get_analogy_for_topic(topico)
        if analogy:
            print(f"\n📚 {topico}:")
            print(f"   🎭 Série: {analogy.get('series', 'N/A')}")
            print(f"   📝 Título: {analogy.get('title', 'N/A')[:60]}...")
        else:
            print(f"\n📚 {topico}: ❌ Nenhuma analogia encontrada")

def teste_analogias_com_series_preferidas():
    """Testa analogias com séries específicas"""
    
    print("\n\n📺 TESTE: Analogias por Série Preferida")
    print("="*50)
    
    series_teste = ["FRIENDS", "Grey's Anatomy", "The Big Bang Theory", "Stranger Things"]
    
    for serie in series_teste:
        analogy = sther_analogies.get_analogy_for_topic("Funções", serie)
        if analogy:
            print(f"\n🎬 {serie}:")
            print(f"   📝 {analogy.get('title', 'N/A')}")
        else:
            # Tenta qualquer analogia da série
            analogy = sther_analogies.get_random_analogy(serie)
            if analogy:
                print(f"\n🎬 {serie} (geral):")
                print(f"   📝 {analogy.get('title', 'N/A')}")
            else:
                print(f"\n🎬 {serie}: ❌ Nenhuma analogia disponível")

def teste_resposta_completa_com_analogia():
    """Testa uma resposta completa do Professor Carlos com analogia"""
    
    print("\n\n🎯 TESTE: Resposta Completa com Analogia")
    print("="*60)
    
    # Mensagem da Sther que deveria gerar analogia
    mensagem_confusa = "Não entendi nada sobre função quadrática, está muito confuso isso"
    
    print(f"📨 Sther: '{mensagem_confusa}'")
    print("\n🤖 Testando sistema de analogias...")
    
    # Testa só a parte de analogias
    analogy_response = get_analogy_for_confused_sther(mensagem_confusa, "Funções")
    
    if analogy_response:
        print("✅ ANALOGIA GERADA:")
        print("-" * 40)
        print(analogy_response)
    else:
        print("❌ Nenhuma analogia foi gerada")
        
        # Debug: verifica se detectou confusão
        confused = sther_analogies.detect_confusion(mensagem_confusa)
        print(f"🔍 Detectou confusão: {'SIM' if confused else 'NÃO'}")
        
        # Debug: verifica se tem analogias de Funções
        analogy = sther_analogies.get_analogy_for_topic("Funções")
        print(f"🎭 Tem analogias de Funções: {'SIM' if analogy else 'NÃO'}")

def mostrar_estatisticas():
    """Mostra estatísticas do sistema"""
    
    print("\n\n📊 ESTATÍSTICAS DO SISTEMA")
    print("="*50)
    
    stats = sther_analogies.get_stats()
    
    print(f"📺 Total de séries: {stats['total_series']}")
    print(f"🎭 Total de analogias: {stats['total_analogies']}")
    print(f"📚 Suporte DOCX: {'✅' if stats['docx_support'] else '❌'}")
    
    print(f"\n🎬 SÉRIES DISPONÍVEIS:")
    for serie in stats['series_available']:
        count = stats['analogies_per_series'].get(serie, 0)
        print(f"   • {serie}: {count} analogias")

if __name__ == "__main__":
    print("🎬 SISTEMA DE ANALOGIAS DA STHER - TESTE COMPLETO")
    print("🎯 Objetivo: Verificar se funciona quando Sther não entende")
    print("="*70)
    
    # Executa todos os testes
    teste_deteccao_confusao()
    teste_analogias_por_topico()
    teste_analogias_com_series_preferidas()
    teste_resposta_completa_com_analogia()
    mostrar_estatisticas()
    
    print("\n\n✅ TESTES CONCLUÍDOS!")
    print("💡 Se tudo funcionou, o Professor Carlos agora usa analogias")
    print("   das séries favoritas da Sther quando ela não entender!") 