# 🧠 Mapa Mental Interativo - Matemática ENEM

## 📋 Visão Geral

O **Mapa Mental Interativo** é uma nova funcionalidade do ENEM AI Helper que permite à Sther explorar os tópicos de matemática de forma visual e interativa, similar ao mapa mental da imagem fornecida.

## ✨ Características Principais

### 🎯 **Navegação Visual**

- Interface intuitiva com cards clicáveis
- Navegação hierárquica por tópicos
- Breadcrumb para rastreamento da localização atual
- Organização clara dos conteúdos

### 📚 **Estrutura Hierárquica**

```
📖 Matemática ENEM
├── 🔢 Álgebra
│   ├── 📈 Funções
│   │   ├── 📏 Função do 1º Grau
│   │   ├── 📊 Função do 2º Grau
│   │   ├── 📈 Função Exponencial
│   │   └── 📉 Função Logarítmica
│   └── ⚖️ Equações e Inequações
├── 📐 Geometria
│   ├── ⬜ Geometria Plana (Triângulos, Quadriláteros, Círculo)
│   └── 🧊 Geometria Espacial (Prismas, Pirâmides, Cilindros)
├── 📏 Trigonometria
├── 📊 Estatística e Probabilidade
├── 🔢 Matrizes e Determinantes
└── 📈 Progressões
```

### 🤖 **Integração com IA**

- **Botão "🤖 Pedir Explicação"** em cada tópico
- Explicações automáticas do Professor Carlos
- Respostas contextualizadas e personalizadas
- Fórmulas renderizadas com MathJax

## 🚀 Como Funciona

### 1. **Acesso ao Mapa Mental**

```python
# No app principal, selecione "Matemática"
# e clique na aba "🧠 Mapa Mental"
```

### 2. **Navegação**

- **Clique nos cards** para navegar pelos tópicos
- **Botão "🏠 Início"** para voltar ao menu principal
- **Breadcrumb** mostra onde você está

### 3. **Solicitar Explicações**

- **Clique em "🤖 Pedir Explicação"** em qualquer tópico
- O Professor Carlos gerará uma explicação personalizada
- Fórmulas são renderizadas automaticamente

## 📊 Exemplo de Tópico Detalhado

### 📊 Função do 2º Grau

**Fórmulas Principais:**
$$f(x) = ax^2 + bx + c$$

**Discriminante:**
$$\Delta = b^2 - 4ac$$

**Fórmula de Bhaskara:**
$$x = \frac{-b \pm \sqrt{\Delta}}{2a}$$

**Vértice da parábola:**
$$V = \left(-\frac{b}{2a}, -\frac{\Delta}{4a}\right)$$

**Conceitos:**

- 📈 Concavidade (a > 0: para cima, a < 0: para baixo)
- 🎯 Raízes (Δ > 0: duas raízes, Δ = 0: uma raiz, Δ < 0: sem raízes reais)

## 🔧 Implementação Técnica

### **Arquivos Principais**

- `mapa_mental_simples.py` - Sistema de mapa mental
- `app.py` - Integração com interface principal
- `professor_carlos_local.py` - IA para explicações

### **Estrutura de Dados**

```python
def render_topic_card(icon: str, title: str, description: str) -> bool:
    """Renderiza um cartão de tópico clicável"""
    return st.button(
        f"{icon} **{title}**\n{description}",
        use_container_width=True,
        key=f"card_{title}"
    )
```

### **Integração com IA**

```python
def get_ai_explanation(topic: str) -> str:
    """Gera explicação usando Professor Carlos"""
    question = f"""
    Olá Professor Carlos! A Sther está estudando pelo mapa mental
    e clicou em "{topic}".

    Por favor, explique de forma didática:
    1. O que é {topic}
    2. Como aparece no ENEM
    3. Dicas importantes para a Sther
    4. Um exemplo prático
    """

    response = professor_carlos_local.get_response(question, api_key)
    return response
```

## 🎨 Interface Visual

### **Cards de Tópicos**

- **Ícones intuitivos** para cada área
- **Descrições breves** e claras
- **Botões responsivos** em grid layout
- **Design consistente** com o tema do app

### **Páginas de Detalhes**

- **Fórmulas em LaTeX** renderizadas com MathJax
- **Conceitos organizados** em colunas
- **Botões de ação** bem posicionados
- **Navegação intuitiva**

## 🔄 Fluxo de Uso

1. **Sther acessa** a aba "🧠 Mapa Mental"
2. **Visualiza** as áreas principais de matemática
3. **Clica** em uma área de interesse (ex: Álgebra)
4. **Navega** pelos subtópicos (ex: Funções)
5. **Seleciona** tópico específico (ex: Função do 2º Grau)
6. **Visualiza** fórmulas e conceitos
7. **Clica** em "🤖 Pedir Explicação" se tiver dúvidas
8. **Recebe** explicação personalizada do Professor Carlos

## 💡 Vantagens do Sistema

### **Para a Sther:**

- ✅ **Navegação visual** facilita o entendimento
- ✅ **Acesso rápido** a fórmulas importantes
- ✅ **Explicações on-demand** do Professor Carlos
- ✅ **Organização clara** dos conteúdos
- ✅ **Interface intuitiva** e amigável

### **Para o Estudo:**

- 📚 **Visão geral** de todos os tópicos
- 🎯 **Foco dirigido** em áreas específicas
- 🔄 **Revisão eficiente** de conceitos
- 💡 **Descoberta** de conexões entre tópicos
- 📝 **Suporte imediato** para dúvidas

## 🚀 Próximas Melhorias

### **Funcionalidades Planejadas:**

- 🔍 **Busca** por tópicos específicos
- 📊 **Progresso de estudo** por área
- 🎯 **Recomendações** baseadas no histórico
- 📱 **Versão mobile** otimizada
- 🔗 **Links** para exercícios relacionados

### **Expansões Futuras:**

- 🧪 **Mapa de Ciências** da Natureza
- 📖 **Mapa de Humanas**
- 🌍 **Mapas de Geografia**
- 📚 **Literatura** e redação

## 🧪 Como Testar

### **Teste Básico:**

```bash
streamlit run app.py
# 1. Selecione "Matemática"
# 2. Clique na aba "🧠 Mapa Mental"
# 3. Navegue pelos tópicos
# 4. Teste as explicações da IA
```

### **Teste Avançado:**

```bash
streamlit run test_mapa_mental.py --server.port 8503
# Versão independente para testes
```

## 📈 Métricas de Sucesso

- ✅ **Interface responsiva** e intuitiva
- ✅ **Integração perfeita** com Professor Carlos
- ✅ **Navegação fluida** entre tópicos
- ✅ **Renderização correta** de fórmulas LaTeX
- ✅ **Explicações contextualizadas** e úteis

---

🎓 **ENEM AI Helper** - Sistema personalizado para maximizar o aprendizado da Sther através de navegação visual e suporte inteligente!
