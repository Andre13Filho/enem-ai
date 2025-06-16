"""
Sistema de Analogias Sther v2.0
Baseado no conteúdo dos documentos fornecidos:
- Friends
- Grey's Anatomy
- Stranger Things
- The Big Bang Theory
- WandaVision
- Young Sheldon
"""

import json
import re
import random
from typing import Dict, List, Tuple, Optional

class StherAnalogiesSystemV2:
    def __init__(self):
        self.content_data = self._load_content_data()
        self.confusion_patterns = [
            r"não entend[iu]",
            r"não consig[ou]",
            r"complicado",
            r"difícil",
            r"confuso",
            r"não sei",
            r"ajuda",
            r"explicar melhor",
            r"não compreend[ou]",
            r"muito complicado"
        ]
        
        # Mapeamento de tópicos matemáticos para conceitos das séries
        self.topic_mapping = {
            "determinantes": "stranger_things",
            "matrizes": "friends",
            "probabilidade": "grey_anatomy",
            "função": "friends",
            "funções": "friends",
            "geometria": "friends",
            "trigonometria": "big_bang_theory",
            "álgebra": "young_sheldon",
            "derivadas": "grey_anatomy",
            "integrais": "wandavision",
            "limites": "big_bang_theory",
            "estatística": "grey_anatomy"
        }
    
    def _load_content_data(self) -> Dict:
        """Carrega os dados do arquivo JSON"""
        try:
            with open('friends_content.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def detect_confusion(self, message: str) -> bool:
        """Detecta se o usuário está confuso"""
        message_lower = message.lower()
        for pattern in self.confusion_patterns:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def identify_math_topic(self, message: str) -> Optional[str]:
        """Identifica o tópico matemático na mensagem"""
        message_lower = message.lower()
        for topic in self.topic_mapping:
            if topic in message_lower:
                return topic
        return None
    
    def get_friends_analogy(self, topic: str) -> str:
        """Gera analogia usando Friends"""
        analogies = {
            "matrizes": """
Pense numa matriz como o grupo de Friends! 🎭

É como se cada posição da matriz fosse um personagem:
- **Rachel (1,1)**: A primeira posição sempre chama atenção
- **Monica (2,1)**: Organizada e controladora, mantém tudo no lugar
- **Phoebe (3,2)**: Única e especial, pode ser diferente dos outros

Quando você multiplica matrizes, é como combinar os grupos:
- Ross tentando organizar um jantar com todos
- Cada combinação cria uma nova dinâmica
- O Central Perk é onde tudo acontece (resultado final)

**Ordem importa**: Assim como Ross e Rachel "dando um tempo" vs "terminando" são coisas diferentes, AB ≠ BA!
            """,
            
            "função": """
Funções são como os relacionamentos em Friends! 💕

**Entrada → Função → Saída**:
- **Entrada**: Rachel chegando ao Central Perk
- **Função**: A dinâmica do grupo (como eles reagem)
- **Saída**: O resultado (risadas, drama, romance)

**Injetora**: Como Ross falando "We were on a break!" - sempre gera a MESMA reação
**Sobrejetora**: Como Monica cozinhando - sempre tem um resultado para qualquer situação
**Bijetora**: Como Chandler e suas piadas - uma piada única para cada situação, e vice-versa

A função é o padrão de como as coisas sempre acontecem no grupo!
            """,
            
            "geometria": """
Geometria é como o apartamento de Monica! 🏠

**Área**: O espaço do apartamento (onde todos se reúnem)
**Perímetro**: As paredes que definem onde termina o espaço dos Friends
**Volume**: Quando eles estão todos juntos, o "volume" de risadas e drama

**Círculo**: Como eles se sentam ao redor da mesa do Central Perk
**Ângulos**: As diferentes perspectivas de cada amigo sobre a mesma situação
**Paralelismo**: Rachel e Monica crescendo juntas, sempre no mesmo ritmo

O apartamento tem suas regras de espaço, assim como a geometria tem suas fórmulas!
            """
        }
        
        return analogies.get(topic, self._generate_generic_friends_analogy(topic))
    
    def get_stranger_things_analogy(self, topic: str) -> str:
        """Gera analogia usando Stranger Things"""
        analogies = {
            "determinantes": """
Determinantes são como a estabilidade do Mundo Invertido! 🔮

Imagine uma matriz 2x2 como um portal:
```
| a  b |
| c  d |
```

**Mike e Eleven (diagonal principal: a×d)**:
- Representam a força que mantém Hawkins seguro
- Quando eles estão unidos, o portal permanece estável

**O Devorador de Mentes (diagonal secundária: b×c)**:
- Representa as forças do caos tentando abrir portais
- Quer destruir o equilíbrio de Hawkins

**Determinante = (a×d) - (b×c)**:
- **Positivo**: Mike e Eleven vencem! Portal seguro ✅
- **Zero**: Empate perigoso - portal instável ⚠️
- **Negative**: Devorador de Mentes vence - portal se abre! ❌

Quanto maior o determinante, mais estável é Hawkins. Quanto menor (ou negativo), mais perigoso fica!

**Sistema Linear**: Como reunir todos os heróis de Hawkins - o determinante mostra se é possível salvar a cidade!
            """
        }
        
        return analogies.get(topic, self._generate_generic_stranger_things_analogy(topic))
    
    def get_greys_anatomy_analogy(self, topic: str) -> str:
        """Gera analogia usando Grey's Anatomy"""
        analogies = {
            "probabilidade": """
Probabilidade é como as cirurgias em Grey's Anatomy! 🏥

**Eventos**: Como casos médicos que chegam ao hospital
- **Evento Certo**: Meredith vai salvar vidas (probabilidade = 1)
- **Evento Impossível**: Derek voltando (probabilidade = 0)
- **Eventos Prováveis**: Christina fazendo uma cirurgia perfeita (alta probabilidade)

**Probabilidade Condicional**: 
"Se Derek está operando, qual a chance de salvar o paciente?"
Como Meredith analisando: "Dado que é um caso impossível, qual nossa chance?"

**Distribuição Normal**: Como os batimentos cardíacos
- A maioria fica na faixa normal
- Valores extremos são emergências!

**Amostragem**: Como escolher residentes para uma cirurgia
- Cada residente tem suas habilidades
- A "amostra" representa o resultado da operação

Meredith sempre diz: "É um bom dia para salvar vidas" - isso é probabilidade otimista!
            """,
            
            "derivadas": """
Derivadas são como o ritmo cardíaco dos pacientes! 💓

**Função**: A condição do paciente ao longo do tempo
**Derivada**: A velocidade com que está melhorando ou piorando

- **Derivada Positiva**: Paciente melhorando (como Meredith se recuperando)
- **Derivada Negativa**: Paciente piorando (código vermelho!)
- **Derivada Zero**: Estável (monitoramento constante)
- **Segunda Derivada**: Se a melhora está acelerando ou desacelerando

**Ponto Crítico**: O momento decisivo da cirurgia
**Máximo**: Momento de maior esperança
**Mínimo**: Momento crítico que exige ação

Os médicos são como matemáticos - sempre calculando as taxas de mudança para salvar vidas!
            """,
            
            "estatística": """
Estatística é como analisar os casos de Grey Sloan! 📊

**Média**: Taxa de sucesso típica das cirurgias
**Mediana**: O caso "do meio" - nem fácil, nem impossível
**Moda**: O tipo de caso mais comum que chega

**Desvio Padrão**: O quanto os casos variam
- Baixo: Casos previsíveis (como consultas de rotina)
- Alto: Casos dramáticos (como os acidentes de avião!)

**Amostra**: Os pacientes desta semana
**População**: Todos os pacientes que já passaram pelo hospital

**Hipótese**: "Este tratamento funciona melhor"
**Teste**: Como Meredith testando novos procedimentos

Bailey sempre diz: "Os números não mentem" - isso é estatística pura!
            """
        }
        
        return analogies.get(topic, self._generate_generic_greys_analogy(topic))
    
    def get_big_bang_theory_analogy(self, topic: str) -> str:
        """Gera analogia usando The Big Bang Theory"""
        analogies = {
            "trigonometria": """
Trigonometria é como as teorias de Sheldon! 🔬

**Seno e Cosseno**: Como as ondas cerebrais de Sheldon pensando
- **Seno**: Sobe e desce como o humor de Sheldon
- **Cosseno**: Seno deslocado, como Leonard sempre um passo atrás

**Círculo Trigonométrico**: Como Sheldon girando na cadeira
- 360° = uma volta completa de "Bazinga!"
- 90° = quando ele fica perpendicular à lógica normal

**Período**: Como os episódios semanais de "Fun with Flags" 
**Amplitude**: O quanto Sheldon consegue ser dramático
**Frequência**: Quantas vezes por dia ele corrige os outros

**Ângulos Notáveis**:
- 30°: Um pouco de sarcasmo do Sheldon
- 45°: Meio caminho para o "Bazinga!"
- 90°: Sheldon totalmente confuso

As funções se repetem, assim como as manias do Sheldon!
            """,
            
            "limites": """
Limites são como a paciência dos amigos com Sheldon! 😤

**Limite**: O ponto onde a paciência de Leonard com Sheldon chega ao máximo
**Aproximação**: Leonard se aproximando do limite da sua sanidade
**Infinito**: A capacidade de Sheldon de falar sobre trens

**Limite Lateral**:
- Pela direita: Leonard voltando do trabalho (ainda com energia)
- Pela esquerda: Leonard após ouvir Sheldon o dia todo (esgotado)

**Continuidade**: Como a amizade deles - mesmo nos momentos difíceis, continua

**Indeterminação**: Como quando ninguém entende uma piada do Sheldon
**L'Hôpital**: A regra especial para situações impossíveis (como entender o Sheldon)

O limite existe quando Leonard consegue aguentar Sheldon... na teoria!
            """
        }
        
        return analogies.get(topic, self._generate_generic_bigbang_analogy(topic))
    
    def get_young_sheldon_analogy(self, topic: str) -> str:
        """Gera analogia usando Young Sheldon"""
        analogies = {
            "álgebra": """
Álgebra é como os problemas que o Sheldon criança resolve! 🧮

**Variáveis (x, y)**: Como os mistérios que Sheldon tenta desvendar
- x = quantos livros ele leu hoje
- y = quantas vezes corrigiu a professora

**Equação**: Como Sheldon organizando sua rotina diária
- Tempo de estudo + Tempo de TV = Dia perfeito
- Se uma parte muda, ele precisa ajustar a outra

**Resolver para x**: Como Sheldon descobrindo a resposta
- Ele sempre quer saber o "porquê" de tudo
- Isola a variável como isola os fatos

**Sistema de Equações**: Como equilibrar escola e família
- Duas situações acontecendo ao mesmo tempo
- Sheldon precisa encontrar a solução que funciona para ambas

**Fatoração**: Como Sheldon quebrando problemas complexos em partes menores
- Um problema grande = vários problemas pequenos
- Mais fácil de resolver!

Sheldon sempre diz: "Isso é elementar!" - e é assim que a álgebra funciona!
            """
        }
        
        return analogies.get(topic, self._generate_generic_sheldon_analogy(topic))
    
    def get_wandavision_analogy(self, topic: str) -> str:
        """Gera analogia usando WandaVision"""
        analogies = {
            "integrais": """
Integrais são como a realidade alterada de Wanda! ✨

**Integral**: Wanda "somando" todos os momentos felizes para criar Westview
**Função**: Cada dia vivido com Vision
**Área sob a curva**: Todo o amor acumulado ao longo do tempo

**Integral Definida**: O período específico que Wanda conseguiu viver com Vision
- Limites = início e fim da ilusão
- Resultado = toda a felicidade concentrada

**Integral Indefinida**: Como o amor de Wanda - não tem fim
- "+C" = a constante do amor eterno

**Substituição**: Como Wanda mudando a realidade para se adequar aos seus desejos
**Partes**: Quebrando a dor em pedaços menores para conseguir lidar

**Teorema Fundamental**: 
A conexão entre derivada e integral = A conexão entre perda e cura
Wanda precisou aceitar a derivada da perda para integrar a cura

A integral junta todos os pedacinhos, assim como Wanda juntou todas as memórias!
            """
        }
        
        return analogies.get(topic, self._generate_generic_wandavision_analogy(topic))
    
    def _generate_generic_friends_analogy(self, topic: str) -> str:
        """Gera analogia genérica usando Friends"""
        return f"""
Vamos pensar em {topic} como uma situação no Central Perk! ☕

Imagine que {topic} é como quando os seis amigos se reúnem:
- Cada elemento tem seu papel (como cada amigo)
- As interações seguem padrões (como suas personalidades)
- O resultado depende de como eles se combinam

Ross diria: "Isso é como paleontologia - você precisa entender cada peça!"
Monica organizaria tudo perfeitamente.
E Chandler faria uma piada sobre como a matemática é mais confusa que seus pais! 😄
        """
    
    def _generate_generic_stranger_things_analogy(self, topic: str) -> str:
        """Gera analogia genérica usando Stranger Things"""
        return f"""
{topic} é como combater o Mundo Invertido! 🔮

Assim como Eleven usa seus poderes para equilibrar forças:
- Cada número/elemento é como um aliado em Hawkins
- As operações são como estratégias de batalha
- O resultado mostra se conseguimos salvar a cidade

Mike diria: "Precisamos calcular isso direito ou Hawkins está perdida!"
Dustin adicionaria: "É estatisticamente impossível errar se seguirmos a fórmula!"
        """
    
    def _generate_generic_greys_analogy(self, topic: str) -> str:
        """Gera analogia genérica usando Grey's Anatomy"""
        return f"""
{topic} é como uma cirurgia complexa! 🏥

Meredith encararia assim:
- Cada variável é como um sinal vital do paciente
- Os cálculos são como o procedimento cirúrgico
- O resultado determina se salvamos a vida

"É um bom dia para salvar vidas... e resolver {topic}!"
Bailey diria: "Vocês são residentes, não podem errar os cálculos básicos!"
        """
    
    def _generate_generic_bigbang_analogy(self, topic: str) -> str:
        """Gera analogia genérica usando The Big Bang Theory"""
        return f"""
{topic} é como uma das teorias de Sheldon! 🔬

Sheldon explicaria:
- Cada elemento segue leis universais (como física quântica)
- Os padrões são previsíveis (como seu cronograma diário)
- A precisão é fundamental

Leonard adicionaria: "É mais simples do que parece, Sheldon só complica!"
Raj sussurraria: "Até eu entendo isso..."
        """
    
    def _generate_generic_sheldon_analogy(self, topic: str) -> str:
        """Gera analogia genérica usando Young Sheldon"""
        return f"""
{topic} é como um dos projetos de ciência do Sheldon criança! 🧮

O pequeno gênio do Texas pensaria:
- Preciso entender cada parte do problema
- Vou usar lógica pura para resolver
- A resposta está bem na minha frente!

Sua vó Meemaw diria: "Moon-pie, você torna tudo mais complicado que é!"
Mas Sheldon provaria que está certo... como sempre!
        """
    
    def _generate_generic_wandavision_analogy(self, topic: str) -> str:
        """Gera analogia genérica usando WandaVision"""
        return f"""
{topic} é como a magia da realidade de Wanda! ✨

Assim como Wanda moldava Westview:
- Cada elemento pode ser transformado
- As regras seguem uma lógica própria
- O resultado reflete nossa intenção

Vision diria: "Mas como isso funciona exatamente?"
Wanda responderia: "Não importa como, importa que funciona!"
        """
    
    def generate_analogy(self, topic: str, series_preference: str = None) -> str:
        """Gera analogia baseada no tópico e preferência de série"""
        if not topic:
            return ""
        
        # Se não há preferência, usa o mapeamento padrão
        if not series_preference:
            series_preference = self.topic_mapping.get(topic, "friends")
        
        series_methods = {
            "friends": self.get_friends_analogy,
            "stranger_things": self.get_stranger_things_analogy,
            "grey_anatomy": self.get_greys_anatomy_analogy,
            "big_bang_theory": self.get_big_bang_theory_analogy,
            "young_sheldon": self.get_young_sheldon_analogy,
            "wandavision": self.get_wandavision_analogy
        }
        
        method = series_methods.get(series_preference, self.get_friends_analogy)
        return method(topic)
    
    def process_user_message(self, user_message: str, professor_response: str = "") -> str:
        """Processa mensagem do usuário e retorna analogia se necessário"""
        if not self.detect_confusion(user_message):
            return professor_response
        
        topic = self.identify_math_topic(user_message)
        if not topic:
            return professor_response
        
        analogy = self.generate_analogy(topic)
        
        if professor_response:
            return f"{professor_response}\n\n🎬 **ANALOGIA STHER**:\n{analogy}"
        else:
            return f"🎬 **ANALOGIA STHER**:\n{analogy}"

# Função para integração com o sistema existente
def get_sther_analogy(user_message: str, professor_response: str = "") -> str:
    """Função para integração fácil com o sistema existente"""
    system = StherAnalogiesSystemV2()
    return system.process_user_message(user_message, professor_response)

# Teste do sistema
if __name__ == "__main__":
    system = StherAnalogiesSystemV2()
    
    # Exemplos de teste
    test_cases = [
        "Não entendi determinantes, muito complicado",
        "Matrizes são difíceis, pode explicar melhor?",
        "Probabilidade está confuso",
        "Não consigo entender funções",
        "Trigonometria é muito complicado"
    ]
    
    print("🎬 SISTEMA DE ANALOGIAS STHER V2.0")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\n📝 TESTE: {test}")
        print("─" * 40)
        response = system.process_user_message(test)
        print(response)
        print("=" * 50)