# 📚 Sistema de Base de Dados de Exercícios de Matemática ENEM

## 🎯 Objetivo

Este sistema foi desenvolvido para organizar todos os exercícios de matemática do ENEM (2015-2024) em uma base de dados estruturada, facilitando o acesso do Professor Carlos e o envio organizado para a Sther.

## 📊 Estatísticas da Base de Dados

- **Total de exercícios:** 557 exercícios de matemática
- **Anos cobertos:** 2015 a 2024 (10 anos)
- **Exercícios por tópico:**
  - Outros: 163 exercícios
  - Geometria: 146 exercícios
  - Funções: 103 exercícios
  - Estatística e Probabilidade: 60 exercícios
  - Álgebra: 34 exercícios
  - Geometria Analítica: 22 exercícios
  - Matemática Financeira: 15 exercícios
  - Progressões: 13 exercícios
  - Análise Combinatória: 1 exercício

## 🗃️ Arquivos Principais

### 1. `math_exercises_database_creator.py`

- **Função:** Processa os PDFs do "Segundo dia" e extrai exercícios de matemática
- **Saída:** Base de dados SQLite (`enem_math_exercises.db`)
- **Como usar:**

```bash
python math_exercises_database_creator.py
```

### 2. `professor_math_interface.py`

- **Função:** Interface Streamlit para o Professor Carlos navegar e buscar exercícios
- **Como usar:**

```bash
streamlit run professor_math_interface.py
```

### 3. `sther_integration.py`

- **Função:** Cria pacotes organizados de exercícios para enviar à Sther
- **Como usar:**

```bash
python sther_integration.py
```

## 🔍 Funcionalidades do Sistema

### Para o Professor Carlos:

#### 1. **Dashboard Principal**

- Visão geral dos exercícios disponíveis
- Estatísticas por ano e tópico
- Exercícios recentes

#### 2. **Busca por Tópico**

- Filtrar exercícios por área da matemática
- Visualizar enunciados e alternativas
- Exportar seleções para a Sther

#### 3. **Busca por Ano**

- Encontrar exercícios de anos específicos
- Análise temporal dos temas abordados
- Comparação entre edições do ENEM

#### 4. **Estatísticas Detalhadas**

- Gráficos interativos
- Distribuição de exercícios
- Tendências por ano

### Para Envio à Sther:

#### 1. **Pacotes por Tópico**

- Exercícios organizados por área matemática
- Metadados educacionais incluídos
- Dicas de ensino personalizadas

#### 2. **Pacotes por Ano**

- Coleções completas por edição do ENEM
- Contexto histórico das questões
- Evolução dos temas

#### 3. **Pacotes Personalizados**

- Seleção manual de critérios
- Combinação de anos e tópicos
- Quantidade customizada

## 📝 Formato dos Exercícios para a Sther

Cada exercício é estruturado com:

```json
{
  "id": "ENEM_2024_Q136",
  "source_info": {
    "exam": "ENEM",
    "year": 2024,
    "question_number": 136,
    "day": 2,
    "subject": "Matemática"
  },
  "content": {
    "statement": "Enunciado da questão...",
    "alternatives": [
      { "letter": "A", "text": "Alternativa A" },
      { "letter": "B", "text": "Alternativa B" }
    ],
    "correct_answer": "A"
  },
  "classification": {
    "topic": "Geometria",
    "difficulty": "Médio",
    "skills_required": ["Cálculo de Área", "Interpretação Gráfica"]
  },
  "teaching_notes": {
    "solution_explanation": "Explicação da solução...",
    "teaching_tips": [
      "Desenhe a figura para visualizar melhor",
      "Identifique as fórmulas necessárias"
    ],
    "common_mistakes": ["Confundir fórmulas de área e perímetro"]
  }
}
```

## 🚀 Como Usar o Sistema

### Passo 1: Criar a Base de Dados

```bash
python math_exercises_database_creator.py
```

### Passo 2: Usar a Interface do Professor

```bash
streamlit run professor_math_interface.py
```

### Passo 3: Gerar Pacotes para a Sther

```bash
python sther_integration.py
```

## 📋 Opções de Pacotes para a Sther

### 1. Pacotes por Tópico

- `sther_geometria.json` - 20 exercícios de geometria
- `sther_funções.json` - 20 exercícios de funções
- `sther_estatística_e_probabilidade.json` - 20 exercícios de estatística
- E outros tópicos...

### 2. Pacotes por Ano

- `sther_enem_2024.json` - 25 exercícios do ENEM 2024
- `sther_enem_2023.json` - 25 exercícios do ENEM 2023
- E todos os anos de 2015 a 2024...

### 3. Pacotes Personalizados

- Critérios definidos pelo professor
- Combinação de filtros
- Quantidade específica de exercícios

## 🎓 Recursos Educacionais Incluídos

### Para Cada Exercício:

- **Classificação por tópico:** Organização pedagógica clara
- **Nível de dificuldade:** Baseado no padrão ENEM
- **Habilidades necessárias:** Competências matemáticas requeridas
- **Dicas de ensino:** Estratégias pedagógicas específicas
- **Erros comuns:** Alertas sobre dificuldades típicas dos estudantes

### Metadados dos Pacotes:

- **Informações do pacote:** Nome, data de criação, total de exercícios
- **Filtros aplicados:** Critérios usados na seleção
- **Tópicos incluídos:** Lista de áreas matemáticas
- **Anos cobertos:** Período temporal dos exercícios
- **Níveis de dificuldade:** Distribuição de complexidade

## 🔧 Manutenção e Atualizações

### Adicionando Novos PDFs:

1. Coloque os novos PDFs na pasta `Segundo dia/ANO/`
2. Execute: `python math_exercises_database_creator.py`
3. O sistema identificará e processará automaticamente os novos arquivos

### Melhorando a Classificação:

- Edite as palavras-chave nos métodos `_identify_topic()` e `_identify_skills()`
- Adicione novos tópicos no enum `MathTopic`
- Customize as dicas de ensino em `_generate_teaching_tips()`

## 📈 Benefícios do Sistema

### Para o Professor Carlos:

- ✅ Acesso rápido a 557 exercícios organizados
- ✅ Busca eficiente por tópico ou ano
- ✅ Interface intuitiva e visual
- ✅ Estatísticas para análise pedagógica

### Para a Sther:

- ✅ Exercícios estruturados e categorizados
- ✅ Metadados educacionais ricos
- ✅ Formato JSON padronizado
- ✅ Facilita implementação de algoritmos de recomendação

### Para os Estudantes (através da Sther):

- ✅ Exercícios autênticos do ENEM
- ✅ Progressão organizada por tópicos
- ✅ Dicas de resolução incluídas
- ✅ Identificação de erros comuns

## 🔄 Fluxo de Trabalho Recomendado

1. **Professor identifica necessidade:** "Preciso de exercícios de geometria para os alunos"

2. **Usa a interface:** Acessa `professor_math_interface.py` → Busca por tópico → Seleciona "Geometria"

3. **Revisa exercícios:** Visualiza os exercícios encontrados, verifica adequação

4. **Gera pacote para Sther:** Usa "Enviar para Sther" → Arquivo JSON é criado automaticamente

5. **Sther recebe e processa:** O arquivo JSON contém tudo necessário para a IA processar e recomendar

## 📞 Suporte e Melhorias

Este sistema pode ser expandido com:

- Integração com mais fontes de exercícios
- Análise automática de dificuldade usando IA
- Sistema de tags mais granular
- Interface web mais avançada
- API REST para integração direta com a Sther

## ✨ Próximos Passos

1. **Testes com a Sther:** Validar formato e integração
2. **Feedback do Professor:** Ajustar interface conforme necessidades
3. **Melhorias na extração:** Refinar parsing dos PDFs
4. **Gabaritos:** Integrar respostas corretas dos exercícios
5. **Expansão:** Adicionar outras disciplinas do ENEM

---

**Sistema desenvolvido para otimizar o ensino de matemática através da organização inteligente de exercícios do ENEM e integração com IA educacional.**
