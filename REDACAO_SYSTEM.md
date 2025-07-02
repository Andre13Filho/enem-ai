# 📝 Sistema de Correção de Redação - Professora Carla

## ✨ Funcionalidades Implementadas

### 🎯 Correção Completa de Redação

- **Análise baseada nos 5 critérios do ENEM**
- **Pontuação de 0 a 1000 pontos**
- **Feedback detalhado por competência**
- **Sugestões específicas de melhoria**
- **Comparação com redações nota 1000**

### 📤 Múltiplas Formas de Envio

#### 1. **Upload de PDF (Aba "Correção de Redação")**

- Faça upload do arquivo PDF com sua redação
- Sistema extrai automaticamente o texto
- Gera correção completa instantaneamente
- Suporta PDFs gerados por texto (não apenas imagens)

#### 2. **Análise via Chat**

- Cole sua redação diretamente no chat
- Use frases como: "Professora Carla, poderia analisar minha redação:"
- Sistema detecta automaticamente que é uma redação
- Fornece correção completa no formato chat

## 🧠 Base de Conhecimento

### 📚 Materiais Pedagógicos

- **Critérios oficiais do ENEM**
- **Técnicas de redação dissertativo-argumentativa**
- **Métodos de argumentação**
- **Estruturação textual**
- **Coesão e coerência**

### 🏆 Redações Nota 1000

- **Exemplos reais de redações perfeitas**
- **Análise comparativa automática**
- **Padrões de excelência identificados**
- **Modelos para inspiração**

## 🎯 Critérios de Avaliação

### **Competência 1** - Domínio da Escrita Formal (0-200 pts)

- Estrutura dissertativo-argumentativa
- Registro formal da língua
- Organização textual

### **Competência 2** - Compreensão do Tema (0-200 pts)

- Desenvolvimento do tema proposto
- Repertório sociocultural relevante
- Argumentação consistente

### **Competência 3** - Organização das Informações (0-200 pts)

- Seleção e organização de argumentos
- Defesa consistente de ponto de vista
- Progressão textual

### **Competência 4** - Mecanismos Linguísticos (0-200 pts)

- Conectivos e operadores argumentativos
- Coesão textual
- Articulação entre parágrafos

### **Competência 5** - Proposta de Intervenção (0-200 pts)

- **Agente:** Quem executará a ação
- **Ação:** O que será feito
- **Meio:** Como será implementado
- **Finalidade:** Objetivo da proposta
- **Detalhamento:** Especificidade da solução

## 📊 Relatório de Correção

### 📋 Conteúdo do Relatório

- **Nota final (0-1000)**
- **Pontuação por competência**
- **Análise detalhada de cada critério**
- **Pontos fortes identificados**
- **Áreas para melhoria**
- **Plano de ação específico**
- **Comparação com redações nota 1000**

### 💡 Feedback Personalizado

- **Sugestões específicas** para cada competência
- **Exemplos práticos** de como melhorar
- **Dicas da Professora Carla** baseadas na personalidade da Sther
- **Estratégias para alcançar nota 1000**

## 🚀 Como Usar

### **Método 1: Upload de PDF**

1. Vá para a aba "✍️ Correção de Redação"
2. Clique em "Escolha um arquivo PDF"
3. Selecione sua redação em PDF
4. Clique em "🔍 Analisar Redação"
5. Aguarde a análise completa

### **Método 2: Chat Direto**

1. Vá para a aba "💬 Chat"
2. Digite: "Professora Carla, poderia analisar minha redação:"
3. Cole o texto completo da sua redação
4. Envie a mensagem
5. Receba a correção no chat

## ⚙️ Tecnologias Utilizadas

### 🧠 Inteligência Artificial

- **Groq API** com modelo DeepSeek R1 Distill
- **Sistema RAG** (Retrieval-Augmented Generation)
- **Embeddings** multilíngues avançados
- **Raciocínio suprimido** - apenas resposta final
- **Otimizado para clareza** - sem thinking interno

### 📊 Base de Dados Vetorial

- **FAISS** para busca semântica
- **Hugging Face** para embeddings
- **Indices pré-construídos** com materiais do ENEM

### 📄 Processamento de PDF

- **PyPDF2** para extração de texto
- **PyMuPDF** como fallback avançado
- **Múltiplas estratégias** de extração

## 🔧 Configuração Técnica

### ✅ Dependências Instaladas

```bash
pip install PyPDF2 PyMuPDF
pip install langchain langchain-community
pip install sentence-transformers
pip install faiss-cpu
pip install groq
```

### 🔑 API Key Necessária

- **Groq API Key** configurada em:
  - Streamlit Secrets: `GROQ_API_KEY`
  - Variável de ambiente: `GROQ_API_KEY`

### 🎯 Configuração da IA

- **Modelo**: DeepSeek R1 Distill Llama 70B
- **Temperatura**: 0.7 (equilíbrio criatividade/precisão)
- **Max tokens**: 2048 (análises detalhadas)
- **Show reasoning**: False (sem raciocínio interno)
- **Reasoning effort**: Low (foco na resposta final)
- **Resposta**: Direta como Professora Carla

### 📁 Arquivos Principais

- `local_redacao_rag.py` - Sistema principal
- `app.py` - Interface integrada
- Indices FAISS baixados automaticamente do Hugging Face

### ☁️ Compatibilidade Streamlit Cloud

- ✅ **Sistema totalmente compatível** com Streamlit Cloud
- ✅ **Correções aplicadas** para evitar erros de validação Pydantic
- ✅ **Prompt template** integrado ao sistema LLM
- ✅ **Nomes de arquivos FAISS** padronizados para `index.faiss` e `index.pkl`
- ✅ **Teste completo** executado com sucesso (5/5 testes passaram)
- ✅ **Download automático** das bases de dados na primeira execução

## 🎯 Resultados Esperados

### ✨ Para a Sther

- **Correção precisa** baseada nos critérios oficiais
- **Feedback construtivo** para melhoria
- **Caminho claro** para nota 1000
- **Confiança** na preparação para o ENEM

### 📈 Melhorias Contínuas

- **Aprendizado** com cada correção
- **Evolução** nas próximas redações
- **Domínio** das técnicas dissertativo-argumentativas
- **Preparação completa** para o ENEM

---

## 🌟 Mensagem da Professora Carla

> "Sther, agora tenho tudo que preciso para te ajudar a conquistar a nota 1000 na redação! Seja enviando PDF ou escrevendo diretamente no chat, vou analisar cada detalhe da sua redação com o carinho e a precisão que você merece. Juntas, vamos transformar suas ideias em textos perfeitos! 💪✨"

**🎯 Objetivo: Redação Nota 1000 no ENEM**  
**📚 Método: Correção científica + Motivação personalizada**  
**✨ Resultado: Confiança e excelência na escrita**
