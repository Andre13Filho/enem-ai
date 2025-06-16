#!/usr/bin/env python3
"""
Teste do Sistema de Detecção de Pedidos de Exercícios da Sther
================================================================

Este script testa se o Professor Carlos consegue detectar automaticamente
quando a Sther pede exercícios e buscar na base de dados ENEM.
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from professor_carlos_local import professor_carlos_local
except ImportError:
    print("❌ Erro: Não foi possível importar professor_carlos_local")
    sys.exit(1)

def teste_deteccao_exercicios():
    """Testa diferentes tipos de pedidos da Sther"""
    
    print("🧪 TESTE: Sistema de Detecção de Exercícios da Sther")
    print("="*60)
    
    # Lista de mensagens de teste da Sther
    mensagens_teste = [
        # Pedidos explícitos de exercícios
        "Professor, me dê exercícios de Geometria",
        "Quero exercícios sobre funções quadráticas", 
        "Tem questões de probabilidade?",
        "Preciso de exercícios do ENEM 2024",
        "Me dê questões sobre triângulos",
        "Quero praticar álgebra",
        
        # Pedidos mais sutis
        "Posso resolver alguns exercícios?",
        "Tem atividades sobre matemática financeira?",
        "Quero treinar progressões",
        
        # Perguntas normais (não devem ativar exercícios completos)
        "Como resolve equação do segundo grau?",
        "Explique o teorema de Pitágoras",
        "O que é uma função quadrática?",
    ]
    
    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"\n📝 TESTE {i}: '{mensagem}'")
        print("-" * 50)
        
        # Testa detecção de palavras-chave
        user_lower = mensagem.lower()
        exercise_keywords = [
            'exercício', 'exercicios', 'questão', 'questões', 'questao', 'questoes',
            'praticar', 'treinar', 'resolver', 'fazer exercício', 'atividade',
            'me dê', 'me de', 'quero', 'preciso', 'tem exercício', 'tem questão'
        ]
        
        is_asking = any(keyword in user_lower for keyword in exercise_keywords)
        
        print(f"🔍 Detectou pedido de exercícios: {'✅ SIM' if is_asking else '❌ NÃO'}")
        
        # Testa busca de exercícios
        try:
            exercises = professor_carlos_local.search_exercises_by_message(mensagem, k=2)
            print(f"📚 Exercícios encontrados: {len(exercises)}")
            
            if exercises:
                for j, ex in enumerate(exercises, 1):
                    print(f"   {j}. ENEM {ex['year']} Q{ex['question_number']} - {ex['topic']}")
        
        except Exception as e:
            print(f"❌ Erro na busca: {str(e)}")

def teste_resposta_completa():
    """Testa uma resposta completa do Professor Carlos"""
    
    print("\n\n🎯 TESTE: Resposta Completa do Professor Carlos")
    print("="*60)
    
    # Simula API key (substitua por uma real se quiser testar completamente)
    api_key_teste = "test_key_123"
    
    mensagem_sther = "Professor, me dê exercícios de Geometria sobre triângulos"
    
    print(f"📨 Mensagem da Sther: '{mensagem_sther}'")
    print("\n🤖 Resposta do Professor Carlos:")
    print("-" * 40)
    
    try:
        # Testa apenas a parte de exercícios (sem necessidade de API key real)
        resposta_exercicios = professor_carlos_local._add_recommended_exercises(mensagem_sther)
        print(resposta_exercicios)
        
    except Exception as e:
        print(f"❌ Erro na resposta: {str(e)}")

def teste_estatisticas():
    """Mostra estatísticas da base de dados"""
    
    print("\n\n📊 ESTATÍSTICAS DA BASE DE DADOS")
    print("="*60)
    
    try:
        stats = professor_carlos_local.get_exercises_stats()
        
        if "erro" in stats:
            print(f"❌ {stats['erro']}")
        else:
            print(f"📝 Total de exercícios: {stats.get('total_exercises', 'N/A')}")
            print(f"📅 Anos disponíveis: {stats.get('available_years', 'N/A')}")
            print(f"📚 Tópicos: {stats.get('topics_available', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando Testes do Sistema Sther-Professor Carlos")
    print("🎯 Objetivo: Verificar detecção automática de pedidos de exercícios")
    print("\n")
    
    # Executa os testes
    teste_deteccao_exercicios()
    teste_resposta_completa()
    teste_estatisticas()
    
    print("\n\n✅ Testes concluídos!")
    print("💡 Se tudo funcionou bem, o Professor Carlos já consegue detectar")
    print("   automaticamente quando a Sther pede exercícios!") 