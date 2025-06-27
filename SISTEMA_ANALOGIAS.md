# 🎬 Sistema de Analogias - Séries de TV

## 📋 Visão Geral

O sistema de analogias foi completamente reformulado para usar um sistema RAG (Retrieval-Augmented Generation) baseado em índices FAISS hospedados no Hugging Face. Agora os professores consultam automaticamente os resumos das séries de TV para criar analogias educacionais relevantes.

## 🔄 Mudanças Implementadas

### ❌ **Sistema Anterior (Removido):**

- Analogias hardcoded no código
- Referências genéricas às séries
- Sem consulta a base de conhecimento específica

### ✅ **Sistema Novo (Implementado):**

- Sistema RAG completo para analogias
- Consulta automática aos índices FAISS do Hugging Face
- Base de conhecimento com resumos detalhados das séries
- Integração automática nas respostas dos professores

## 🏗️ Arquitetura do Sistema

### 📁 **Arquivos Principais:**

- `analogias_rag.py` - Sistema RAG principal
- `app.py` - Integração com professores
- Índices FAISS no Hugging Face: `index_analogias.faiss` e `index_analogias.pkl`

### 🔗 **Fluxo de Funcionamento:**

1. **Usuário faz pergunta** → Professor responde
2. **Sistema extrai conceito** → Identifica tópico principal
3. **Consulta RAG** → Busca analogias relevantes nas séries
4. **Gera analogia** → Cria explicação baseada nas séries
5. **Integra resposta** → Adiciona analogia à resposta do professor

## 🎬 **Séries Disponíveis:**

### 📺 **FRIENDS**

- **Localização:** Central Perk, apartamento de Monica
- **Personagens:** Monica, Chandler, Joey, Rachel, Phoebe, Ross
- **Temas:** Organização, relacionamentos, trabalho, amizade

### 🔬 **The Big Bang Theory**

- **Localização:** Apartamento de Sheldon, Caltech
- **Personagens:** Sheldon, Leonard, Penny, Howard, Raj, Amy, Bernadette
- **Temas:** Ciência, lógica, geek culture, relacionamentos

### 🏥 **Greys Anatomy**

- **Localização:** Grey Sloan Memorial Hospital
- **Personagens:** Meredith, Derek, Cristina, Alex, Bailey
- **Temas:** Medicina, emergências, relacionamentos profissionais

### 🌌 **Stranger Things**

- **Localização:** Hawkins, laboratório, Upside Down
- **Personagens:** Eleven, Mike, Dustin, Lucas, Will, Hopper
- **Temas:** Mistério, amizade, poderes, investigação

### 👨‍👩‍👧‍👦 **Jovem Sheldon**

- **Localização:** Texas, família Cooper
- **Personagens:** Sheldon, Mary, George, Missy, Georgie
- **Temas:** Família, inteligência, infância, educação

### 🎭 **Wandavision**

- **Localização:** Westview, WandaVision
- **Personagens:** Wanda, Vision, Monica, Agatha
- **Temas:** Realidade, poder, perda, televisão

## 🔧 **Como Funciona:**

### 1. **Extração de Conceito**

```python
def extract_conceito_principal(user_message: str, subject: str) -> str:
    # Identifica palavras-chave por matéria
    # Extrai conceito principal da pergunta
    # Retorna conceito para busca de analogia
```

### 2. **Consulta RAG**

```python
def get_analogia_para_conceito(conceito: str, materia: str, api_key: str) -> str:
    # Inicializa sistema RAG
    # Busca analogias relevantes
    # Gera explicação baseada nas séries
```

### 3. **Integração Automática**

```python
def get_teacher_response(subject: str, user_message: str, api_key: str) -> str:
    # Resposta base do professor
    # + Analogia automática
    # = Resposta completa
```

## 📊 **Exemplo de Uso:**

### **Pergunta do Usuário:**

"Como resolver equações do 2º grau?"

### **Processo:**

1. **Professor responde** sobre equações do 2º grau
2. **Sistema extrai** conceito: "Equação"
3. **Consulta RAG** busca analogias sobre equações
4. **Gera analogia** baseada em FRIENDS ou TBBT
5. **Integra resposta** com analogia da série

### **Resultado:**

```
[Resposta do Professor sobre equações do 2º grau]

---

🎬 **Analogia da Série para Equação:**
🎬 **Analogia da Série:** The Big Bang Theory - Sheldon explicando física
📚 **Conceito:** Equação do 2º grau é como uma fórmula matemática
🔗 **Conexão:** Como Sheldon organiza suas teorias, cada parte da equação tem seu lugar
💡 **Dica:** Pense na equação como Sheldon organizando seus experimentos!
```

## 🎯 **Benefícios:**

### ✅ **Para o Aprendizado:**

- Explicações mais memoráveis
- Conexões com cultura pop
- Aprendizado mais divertido
- Analogias específicas e relevantes

### ✅ **Para o Sistema:**

- Base de conhecimento escalável
- Analogias sempre atualizadas
- Consulta inteligente a séries
- Integração automática

## 🔍 **Configuração:**

### **Dependências:**

```bash
pip install langchain-community
pip install faiss-cpu
pip install sentence-transformers
pip install groq
```

### **Arquivos Necessários:**

- `analogias_rag.py` - Sistema principal
- Índices FAISS no Hugging Face
- API Key da Groq configurada

### **URLs dos Índices:**

- FAISS: `https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_analogias.faiss`
- PKL: `https://huggingface.co/Andre13Filho/rag_enem/resolve/main/index_analogias.pkl`

## 🚀 **Próximos Passos:**

1. **Testar integração** com todos os professores
2. **Expandir base** de conhecimento das séries
3. **Adicionar mais séries** se necessário
4. **Otimizar prompts** para analogias mais precisas
5. **Criar interface** dedicada para analogias

## 📝 **Notas Técnicas:**

- **Cache automático** dos índices FAISS
- **Fallback graceful** se sistema falhar
- **Integração não-intrusiva** nas respostas
- **Extração inteligente** de conceitos
- **Prompts otimizados** para analogias educacionais

---

**🎬 O sistema agora usa IA para criar analogias baseadas em séries de TV, tornando o aprendizado mais divertido e memorável para a Sther!**
