# 🧠 Sistema de Mapa Mental com Streamlit-Markmap

## 📋 Visão Geral

O **Sistema de Mapa Mental com Streamlit-Markmap** é uma evolução revolucionária do sistema anterior, oferecendo visualizações interativas e dinâmicas dos conceitos matemáticos baseados nas dúvidas da Sther.

### 🎯 Principais Características

- ✅ **Visualização Interativa**: Mapas mentais navegáveis e interativos
- ✅ **Geração Automática**: Baseado nas perguntas da Sther no chat
- ✅ **Múltiplos Níveis**: Básico, Intermediário e Avançado
- ✅ **Fórmulas LaTeX**: Renderização matemática perfeita
- ✅ **Cache Inteligente**: Evita regeneração desnecessária
- ✅ **Estatísticas em Tempo Real**: Análise do conteúdo do mapa

---

## 🚀 Instalação

### 1. Dependência Principal

```bash
pip install streamlit-markmap==1.0.1
```

### 2. Verificar Instalação

Execute o teste:

```bash
streamlit run test_mapa_mental_markmap.py
```

---

## 🎮 Como Usar

### 1. **Faça uma Pergunta** 💬

Na aba "Chat", faça uma pergunta matemática para o Professor Carlos:

```
Exemplo: "Como resolver equações do segundo grau?"
```

### 2. **Acesse o Mapa Mental** 🧠

- Vá para a aba "🧠 Mapa Mental"
- O sistema gerará automaticamente um mapa baseado na sua pergunta

### 3. **Explore Interativamente** 🔍

- **Clique nos nós** para expandir/colapsar
- **Zoom** para ver detalhes
- **Navegue** pelos conceitos relacionados

### 4. **Personalize** ⚙️

- **Nível de Detalhamento**: Básico, Intermediário, Avançado
- **Regenerar**: Obtenha novas perspectivas do mesmo tópico

---

## 🛠️ Estrutura Técnica

### Arquivos Principais

```
📁 enem_ai_helper/
├── 🧠 mapa_mental_markmap.py      # Sistema principal
├── 🧪 test_mapa_mental_markmap.py # Testes
├── 📋 requirements.txt            # Dependências
└── 📱 app.py                      # Integração principal
```

### Componentes Técnicos

#### 1. **Geração Inteligente**

```python
def gerar_markdown_mapa_mental(pergunta, api_key, nivel):
    # Usa IA Groq para gerar estrutura em Markdown
    # Configurações específicas por nível
    # Fallback para estrutura básica
```

#### 2. **Renderização Visual**

```python
from streamlit_markmap import markmap

markmap(markdown_content, height=600)
```

#### 3. **Cache Inteligente**

```python
cache_key = f"markmap_{hash(pergunta)}_{nivel}"
st.session_state[cache_key] = markdown_content
```

---

## 📊 Níveis de Detalhamento

### 🟢 **Básico**

- **5-7 conceitos** fundamentais
- **2-3 níveis** de hierarquia
- Explicações **simples e diretas**

### 🟡 **Intermediário** (Padrão)

- **8-12 conceitos** relacionados
- **3-4 níveis** de hierarquia
- **Fórmulas principais** e exemplos

### 🔴 **Avançado**

- **12-15 conceitos** e subdivisões
- **4-5 níveis** de hierarquia
- **Fórmulas completas**, demonstrações e aplicações

---

## 🧮 Exemplo de Mapa Mental

### Pergunta: "Como resolver equações do 2º grau?"

```markdown
# 🎯 Equação do 2º Grau

## 📚 Conceitos Fundamentais

### 🔢 Definição

- Equação da forma $ax^2 + bx + c = 0$
- Onde $a \neq 0$

### 📐 Elementos

- $a$: coeficiente do termo quadrático
- $b$: coeficiente do termo linear
- $c$: termo independente

## 🧮 Resolução

### 🎯 Fórmula de Bhaskara

- $$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$
- Discriminante: $\Delta = b^2 - 4ac$

### 📊 Análise do Discriminante

- $\Delta > 0$: duas raízes reais distintas
- $\Delta = 0$: uma raiz real (dupla)
- $\Delta < 0$: não há raízes reais

## 🔗 Aplicações

### 📈 Problemas Práticos

- Movimento uniformemente variado
- Área máxima de retângulos
- Problemas de otimização

### 🎓 ENEM

- Interpretação de gráficos
- Modelagem de situações
- Cálculo de máximos e mínimos
```

---

## 📈 Estatísticas do Mapa

O sistema exibe automaticamente:

- **📊 Conceitos**: Número total de tópicos
- **🔗 Conexões**: Ligações entre conceitos
- **📚 Níveis**: Profundidade da hierarquia
- **🧮 Fórmulas**: Quantidade de expressões matemáticas

---

## 🔧 Integração com o Sistema

### No app.py:

```python
with tab_mindmap:
    try:
        from mapa_mental_markmap import display_mapa_mental_wrapper
        display_mapa_mental_wrapper()
    except ImportError:
        st.error("Execute: pip install streamlit-markmap==1.0.1")
```

### Fluxo de Dados:

1. **Chat** → Pergunta armazenada em `st.session_state`
2. **IA Groq** → Gera estrutura Markdown
3. **Streamlit-Markmap** → Renderiza mapa interativo
4. **Cache** → Evita regeneração desnecessária

---

## ✨ Vantagens vs Sistema Anterior

| Aspecto              | Sistema Anterior | Sistema Markmap          |
| -------------------- | ---------------- | ------------------------ |
| **Visualização**     | HTML estático    | Interativo navegável     |
| **Performance**      | Lento            | Rápido e responsivo      |
| **Fórmulas**         | Limitado         | LaTeX completo           |
| **Interatividade**   | Mínima           | Zoom, cliques, navegação |
| **Manutenibilidade** | Complexo         | Simples Markdown         |

---

## 🐛 Solução de Problemas

### Erro: "streamlit-markmap não encontrado"

```bash
pip install streamlit-markmap==1.0.1
streamlit run test_mapa_mental_markmap.py
```

### Mapa não renderiza

1. Verificar se API Key está configurada
2. Verificar se há histórico de chat
3. Testar com pergunta simples

### Cache não funciona

```python
# Limpar cache manualmente
if 'markmap_cache' in st.session_state:
    del st.session_state['markmap_cache']
```

---

## 🚀 Próximos Passos

### Melhorias Planejadas:

- 🎨 **Temas personalizados** para diferentes matérias
- 🔄 **Sincronização** com sistema de exercícios
- 📱 **Layout responsivo** otimizado
- 🧪 **Modo avançado** com simulações interativas

### Expansão:

- Suporte para outras matérias além de Matemática
- Exportação de mapas em PDF/PNG
- Compartilhamento de mapas mentais

---

## 📞 Suporte

### Teste o Sistema:

```bash
streamlit run test_mapa_mental_markmap.py
```

### Sistema Principal:

```bash
streamlit run app.py
```

**🎯 O sistema está pronto para revolucionar o aprendizado da Sther com mapas mentais interativos e dinâmicos!**
