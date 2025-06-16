"""
Sistema de Analogias para Sther - Baseado nas séries fornecidas
Usa Friends, Grey's Anatomy, Stranger Things, Big Bang Theory, Young Sheldon e WandaVision
"""

import json
import re

class StherAnalogiesSystem:
    def __init__(self):
        self.confusion_patterns = [
            r"não entend[ieu]", r"não consig[ou]", r"complicado", r"difícil", 
            r"confuso", r"não sei", r"ajuda", r"explicar melhor",
            r"não entendeu", r"não entendi", r"muito bem", r"está difícil",
            r"preciso de ajuda", r"não compreend[ieu]"
        ]
        
        # Analogias organizadas por tópico matemático
        self.analogies = {
            "determinantes": {
                "serie": "Stranger Things",
                "content": """
🔮 **DETERMINANTES = STRANGER THINGS**

Imagine uma matriz 2x2 como um portal entre mundos:
```
| a  b |
| c  d |
```

**Mike e Eleven (diagonal principal: a×d)**:
- São a força que mantém Hawkins seguro
- Quando unidos, o portal permanece estável

**O Devorador de Mentes (diagonal secundária: b×c)**:
- Representa as forças do caos
- Quer destruir o equilíbrio e abrir portais

**Determinante = (a×d) - (b×c)**:
- **Positivo**: Mike e Eleven vencem! Portal seguro ✅
- **Zero**: Empate perigoso - portal instável ⚠️
- **Negativo**: Devorador vence - portal se abre! ❌

Quanto maior o determinante, mais estável é Hawkins!
                """
            },
            
            "matrizes": {
                "serie": "Friends",
                "content": """
☕ **MATRIZES = FRIENDS NO CENTRAL PERK**

Uma matriz é como o grupo dos 6 amigos organizados:
```
| Rachel  Monica |
| Phoebe  Ross   |
| Joey    Chandler|
```

**Elementos**: Cada posição é um amigo com sua personalidade
**Linhas**: Como eles se sentam no sofá do Central Perk
**Colunas**: Como se organizam para atividades

**Multiplicação de Matrizes**:
Como combinar dois grupos de amigos:
- Cada encontro cria novas dinâmicas
- A ordem importa: jantar na casa da Monica ≠ pizza no Joey's

**Matriz Identidade**: Como o Central Perk - o lugar onde tudo volta ao normal!
                """
            },
            
            "probabilidade": {
                "serie": "Grey's Anatomy",
                "content": """
🏥 **PROBABILIDADE = CIRURGIAS NO GREY SLOAN**

**Eventos**: Como casos médicos que chegam
- **Evento Certo**: Meredith vai salvar vidas (P = 1)
- **Evento Impossível**: Derek voltando (P = 0)
- **Eventos Prováveis**: Cristina fazendo cirurgia perfeita

**Probabilidade Condicional**:
"Se Derek está operando, qual a chance de salvar o paciente?"
Como Meredith analisando: "Dado que é caso impossível, qual nossa chance?"

**Distribuição Normal**: Como batimentos cardíacos
- Maioria fica na faixa normal
- Valores extremos são emergências!

Bailey sempre diz: "Os números não mentem" - isso é probabilidade pura!
                """
            },
            
            "funcoes": {
                "serie": "Friends",
                "content": """
☕ **FUNÇÕES = RELACIONAMENTOS EM FRIENDS**

**Entrada → Função → Saída**:
- **Entrada**: Rachel chegando ao Central Perk
- **Função**: A dinâmica do grupo (como reagem)
- **Saída**: O resultado (risadas, drama, romance)

**Função Injetora**: Como Ross falando "We were on a break!"
- Sempre gera a MESMA reação específica

**Função Sobrejetora**: Como Monica cozinhando
- Sempre tem resultado para qualquer situação

**Função Bijetora**: Como piadas do Chandler
- Uma piada única para cada situação, e vice-versa

O padrão de como as coisas sempre acontecem no grupo!
                """
            },
            
            "trigonometria": {
                "serie": "The Big Bang Theory",
                "content": """
🔬 **TRIGONOMETRIA = TEORIAS DO SHELDON**

**Seno e Cosseno**: Como ondas cerebrais do Sheldon pensando
- **Seno**: Sobe e desce como humor do Sheldon
- **Cosseno**: Seno deslocado, como Leonard sempre um passo atrás

**Círculo Trigonométrico**: Como Sheldon girando na cadeira
- 360° = uma volta completa de "Bazinga!"
- 90° = quando fica perpendicular à lógica normal

**Ângulos Notáveis**:
- 30°: Um pouco de sarcasmo
- 45°: Meio caminho para o "Bazinga!"
- 90°: Sheldon totalmente confuso

As funções se repetem, assim como as manias do Sheldon!
                """
            },
            
            "algebra": {
                "serie": "Young Sheldon",
                "content": """
🧮 **ÁLGEBRA = PROBLEMAS DO SHELDON CRIANÇA**

**Variáveis (x, y)**: Como mistérios que Sheldon tenta desvendar
- x = quantos livros ele leu hoje
- y = quantas vezes corrigiu a professora

**Equação**: Como Sheldon organizando sua rotina
- Tempo de estudo + Tempo de TV = Dia perfeito
- Se uma parte muda, ajusta a outra

**Resolver para x**: Como Sheldon descobrindo respostas
- Ele sempre quer saber o "porquê"
- Isola a variável como isola os fatos

Sheldon sempre diz: "Isso é elementar!" - assim funciona álgebra!
                """
            },
            
            "integrais": {
                "serie": "WandaVision",
                "content": """
✨ **INTEGRAIS = REALIDADE ALTERADA DA WANDA**

**Integral**: Wanda "somando" todos os momentos felizes para criar Westview
**Função**: Cada dia vivido com Vision
**Área sob a curva**: Todo o amor acumulado ao longo do tempo

**Integral Definida**: Período específico que Wanda viveu com Vision
- Limites = início e fim da ilusão
- Resultado = toda felicidade concentrada

**Integral Indefinite**: Como amor de Wanda - não tem fim
- "+C" = constante do amor eterno

A integral junta todos os pedacinhos, assim como Wanda juntou as memórias!
                """
            }
        }
    
    def detect_confusion(self, message: str) -> bool:
        """Detecta se usuário está confuso"""
        message_lower = message.lower()
        for pattern in self.confusion_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def identify_math_topic(self, message: str) -> str:
        """Identifica tópico matemático na mensagem"""
        message_lower = message.lower()
        
        topic_keywords = {
            "determinantes": ["determinante", "det", "matriz quadrada", "regra de cramer", "sarrus"],
            "matrizes": ["matriz", "matrizes", "matrix", "linhas e colunas"],
            "probabilidade": ["probabilidade", "chance", "prob", "evento", "distribuição"],
            "funcoes": ["função", "funções", "function", "domínio", "contradomínio", "f(x)"],
            "trigonometria": ["trigonometria", "seno", "coseno", "tangente", "trig", "ângulo"],
            "algebra": ["álgebra", "algebra", "equação", "variável", "incógnita"],
            "integrais": ["integral", "integrais", "integração", "área sob a curva"]
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return topic
        
        return None
    
    def get_analogy(self, topic: str) -> str:
        """Retorna analogia para o tópico"""
        if topic in self.analogies:
            return self.analogies[topic]["content"]
        return ""
    
    def detect_topic_from_context(self, user_message: str, professor_response: str = "") -> str:
        """Detecta tópico matemático a partir do contexto da resposta do professor"""
        if professor_response:
            # Busca tópicos na resposta do professor
            combined_text = f"{user_message} {professor_response}".lower()
        else:
            combined_text = user_message.lower()
        
        topic_keywords = {
            "determinantes": ["determinante", "det", "matriz quadrada", "regra de cramer", "sarrus"],
            "matrizes": ["matriz", "matrizes", "matrix", "linhas e colunas", "array"],
            "probabilidade": ["probabilidade", "chance", "evento", "distribuição"],
            "funcoes": ["função", "funções", "domínio", "contradomínio", "f(x)"],
            "trigonometria": ["trigonometria", "seno", "coseno", "tangente", "ângulo"],
            "algebra": ["álgebra", "algebra", "equação", "variável", "incógnita"],
            "integrais": ["integral", "integrais", "integração", "área sob a curva"]
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return topic
        
        return None
    
    def process_message(self, user_message: str, professor_response: str = "") -> str:
        """Processa mensagem e adiciona analogia se necessário"""
        if not self.detect_confusion(user_message):
            return professor_response
        
        # Primeiro tenta identificar tópico na mensagem do usuário
        topic = self.identify_math_topic(user_message)
        
        # Se não encontrou, tenta identificar pelo contexto (resposta do professor)
        if not topic:
            topic = self.detect_topic_from_context(user_message, professor_response)
        
        if not topic:
            return professor_response
        
        analogy = self.get_analogy(topic)
        if not analogy:
            return professor_response
        
        if professor_response:
            return f"{professor_response}\n\n🎬 **ANALOGIA ESPECIAL PARA VOCÊ**:\n{analogy}"
        else:
            return f"🎬 **ANALOGIA ESPECIAL PARA VOCÊ**:\n{analogy}"

# Função para integração fácil
def add_analogy_if_confused(user_message: str, professor_response: str) -> str:
    """Adiciona analogia se usuário estiver confuso"""
    system = StherAnalogiesSystem()
    return system.process_message(user_message, professor_response)

# Teste do sistema
if __name__ == "__main__":
    system = StherAnalogiesSystem()
    
    test_cases = [
        "Não entendi determinantes",
        "Matrizes são muito difíceis",
        "Probabilidade está confuso",
        "Não consigo entender funções",
        "Trigonometria é complicado"
    ]
    
    print("🎬 SISTEMA DE ANALOGIAS STHER")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\n📝 TESTE: {test}")
        print("-" * 40)
        response = system.process_message(test)
        print(response)
        print("=" * 50) 