"""
Demonstração do Novo Sistema de Analogias
Baseado exclusivamente no conteúdo dos documentos fornecidos
"""

from new_analogies_system import StherAnalogiesSystem, add_analogy_if_confused

def main():
    print("🎬" + "="*60)
    print("  DEMONSTRAÇÃO DO NOVO SISTEMA DE ANALOGIAS STHER")
    print("  Baseado em: Friends, Grey's Anatomy, Stranger Things,")
    print("  The Big Bang Theory, Young Sheldon e WandaVision")
    print("="*62)
    
    system = StherAnalogiesSystem()
    
    # Casos de teste que simulam interações reais
    test_scenarios = [
        {
            "name": "Estudante confuso com Determinantes",
            "user_msg": "Professor, não entendi determinantes. Está muito complicado!",
            "prof_response": "O determinante é calculado como ad - bc para uma matriz 2x2. É fundamental para verificar se um sistema linear tem solução única."
        },
        {
            "name": "Dificuldade com Matrizes", 
            "user_msg": "Essas matrizes são muito difíceis de entender, não consigo",
            "prof_response": "Matrizes são tabelas de números organizados em linhas e colunas. Podemos somar, subtrair e multiplicar seguindo regras específicas."
        },
        {
            "name": "Confusão com Probabilidade",
            "user_msg": "Probabilidade está muito confuso, pode me ajudar?",
            "prof_response": "Probabilidade mede a chance de um evento ocorrer, variando de 0 (impossível) a 1 (certo). É calculada como casos favoráveis dividido por casos possíveis."
        },
        {
            "name": "Dúvida sobre Funções",
            "user_msg": "Não consigo entender funções, é muito complicado",
            "prof_response": "Uma função é uma relação que associa cada elemento do domínio a exatamente um elemento do contradomínio. Representamos como f(x) = y."
        },
        {
            "name": "Trigonometria Difícil",
            "user_msg": "Trigonometria é muito complicado, preciso de ajuda",
            "prof_response": "Trigonometria estuda as relações entre ângulos e lados dos triângulos. As principais funções são seno, cosseno e tangente."
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 CENÁRIO {i}: {scenario['name']}")
        print("-" * 50)
        print(f"👤 ESTUDANTE: {scenario['user_msg']}")
        print(f"👨‍🏫 PROFESSOR: {scenario['prof_response']}")
        
        # Aplica o sistema de analogias
        enhanced_response = add_analogy_if_confused(
            scenario['user_msg'], 
            scenario['prof_response']
        )
        
        # Verifica se analogia foi adicionada
        if enhanced_response != scenario['prof_response']:
            print("\n🎬 SISTEMA DE ANALOGIAS ATIVADO!")
            print("─" * 40)
            # Mostra apenas a parte da analogia
            analogy_part = enhanced_response.replace(scenario['prof_response'], "").strip()
            print(analogy_part)
        else:
            print("\n💭 Nenhuma confusão detectada ou tópico não reconhecido")
        
        print("\n" + "="*60)
    
    print("\n🎊 DEMONSTRAÇÃO CONCLUÍDA!")
    print("\nO sistema agora:")
    print("✅ Detecta confusão automaticamente")
    print("✅ Identifica tópicos matemáticos") 
    print("✅ Usa analogias das séries fornecidas")
    print("✅ Integra perfeitamente com Professor Carlos")
    print("\n🎬 Séries disponíveis: Friends, Grey's Anatomy, Stranger Things,")
    print("   The Big Bang Theory, Young Sheldon, WandaVision")

if __name__ == "__main__":
    main() 