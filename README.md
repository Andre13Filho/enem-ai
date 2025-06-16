# 🎓 ENEM AI Helper - Professores Particulares para Sther

## 🌟 **Visão Geral**

Sistema de chat inteligente com **8 professores especializados** para ajudar **Sther** (17 anos) na preparação para o ENEM. Cada professor tem personalidade única e acesso a materiais personalizados.

### ⭐ **NOVIDADE: Professor Carlos com Sistema RAG Local**

O **Professor de Matemática** agora possui um sistema **RAG (Retrieval-Augmented Generation) local** que:

- 🎯 Sempre se refere à aluna como **"Futura Senhora Sther Souza!"**
- 📚 **Base de conhecimento local** dos documentos da pasta matemática
- 🧠 **Sistema RAG inteligente** que busca automaticamente conteúdo relevante
- 📁 **Processamento local** de arquivos DOCX, PDF e TXT
- ✅ **Sem Google Drive** - funciona inteiramente com arquivos locais

## 👨‍🏫 **Professores Disponíveis**

| Matéria              | Professor(a)     | Especialização                              | Status           |
| -------------------- | ---------------- | ------------------------------------------- | ---------------- |
| **🔢 Matemática**    | **Prof. Carlos** | **Sistema RAG Local + Docs Locais**         | **⭐ RAG LOCAL** |
| 📚 Língua Portuguesa | Profa. Ana       | Gramática, Literatura, Redação              | 🤖 IA Padrão     |
| 🧬 Biologia          | Prof. Ricardo    | Biologia Celular, Genética, Ecologia        | 🤖 IA Padrão     |
| 🌍 Geografia         | Profa. Marina    | Geografia Física/Humana, Geopolítica        | 🤖 IA Padrão     |
| 🏛️ História          | Prof. Eduardo    | História do Brasil/Geral, Atualidades       | 🤖 IA Padrão     |
| ⚗️ Química           | Profa. Juliana   | Química Orgânica/Inorgânica, Físico-química | 🤖 IA Padrão     |
| ⚡ Física            | Prof. Miguel     | Mecânica, Eletromagnetismo, Ondulatória     | 🤖 IA Padrão     |
| ✍️ Redação           | Profa. Camila    | Dissertativa-argumentativa, Argumentação    | 🤖 IA Padrão     |

## 🚀 **Funcionalidades**

### 🎯 **Core Features**

- ✅ **8 professores especializados** com personalidades únicas
- ✅ **Chat independente** por matéria com histórico persistente
- ✅ **Interface azul personalizada** (#09278d)
- ✅ **Tema responsivo** com avatars e emojis
- ✅ **Barra de progresso** baseada em interações

### 🤖 **Integração IA**

- ✅ **DeepSeek R1 Distill** via Groq
- ✅ **Prompts especializados** por matéria
- ✅ **Modo demonstração** sem API Key
- ✅ **Configurações avançadas** opcionais

### 📚 **Base de Conhecimento**

- ✅ **Sistema RAG Local** para matemática com documentos locais
- ✅ **Suporte múltiplos formatos**: PDF, DOCX, TXT
- ✅ **ChromaDB persistente** para armazenamento local
- ✅ **Processamento automático** de documentos da pasta matemática

### ⭐ **Professor Carlos - Matemática Especializada**

### 🔢 **Sistema RAG Local com Documentos Próprios**

O **Professor Carlos** é o coração do sistema, especialmente desenvolvido para a **Futura Senhora Sther Souza**:

- ✅ **Base de conhecimento local** extraída dos documentos da pasta matemática
- ✅ **Processamento inteligente** de arquivos DOCX, PDF e TXT
- ✅ **Sem dependências externas** - funciona totalmente offline (exceto LLM)
- ✅ **ChromaDB persistente** para armazenamento local
- ✅ **Sistema RAG inteligente** para respostas contextualizadas
- ✅ **Fácil configuração** - apenas coloque os documentos na pasta matemática

### 🏠 **Funcionamento Local**

- **Pasta de origem**: `./matemática/`
- **Vector Store**: ChromaDB local
- **Embeddings**: HuggingFace Sentence Transformers (local)
- **Persistência**: Base de dados salva localmente
- **Performance**: Carregamento rápido após primeiro processamento

📖 **Guia completo**: [README_RAG_LOCAL.md](README_RAG_LOCAL.md)

## 📁 **Estrutura do Projeto**

```
enem_ai_helper/
├── app.py                          # Aplicação principal
├── local_math_rag.py               # Sistema RAG local para matemática
├── professor_carlos_local.py       # Professor Carlos com RAG local
├── deepseek_integration.py         # Integração DeepSeek R1
├── requirements.txt                # Dependências
├── README.md                       # Este arquivo
├── README_RAG_LOCAL.md             # Guia do sistema RAG local
├── CONFIGURACAO_DEEPSEEK.md        # Guia DeepSeek
├── matemática/                     # Pasta com documentos de matemática
│   ├── *.docx                      # Documentos Word
│   ├── *.pdf                       # Documentos PDF
│   └── *.txt                       # Documentos texto
├── chroma_math_local/              # Base de dados ChromaDB (gerada automaticamente)
├── ai_integration_examples.py      # Exemplos de integração
└── .streamlit/
    └── config.toml                 # Configurações de tema
```

## 🛠️ **Instalação e Configuração**

### 1️⃣ **Clonar Repositório**

```bash
git clone <repository-url>
cd enem_ai_helper
```

### 2️⃣ **Instalar Dependências**

```bash
pip install -r requirements.txt
```

### 3️⃣ **Executar Aplicação**

```bash
streamlit run app.py
```

### 4️⃣ **Usar Professor Carlos RAG Local (Recomendado)**

Para usar o Professor Carlos com sistema RAG local:

1. **Coloque seus documentos** na pasta `matemática/` (DOCX, PDF, TXT)
2. **Configure API Key do OpenRouter** no painel lateral
3. **Selecione "🔢 Matemática"**
4. **Aguarde o processamento** na primeira execução
5. **Comece a conversar!** - O sistema consultará automaticamente seus documentos

📖 **Guia completo**: [README_RAG_LOCAL.md](README_RAG_LOCAL.md)

## 🔧 **Configurações Disponíveis**

### 🤖 **DeepSeek R1 0528**

- **API Key**: OpenRouter API Key (obrigatória para IA)
- **Site URL**: Para ranking no OpenRouter (opcional)
- **Site Name**: Nome do seu site (opcional)

📖 **Guia completo**: [CONFIGURACAO_DEEPSEEK.md](CONFIGURACAO_DEEPSEEK.md)

### 📚 **Sistema RAG Local (Matemática)**

- **Pasta origem**: `./matemática/` com seus documentos
- **Formatos**: DOCX, PDF, TXT
- **Armazenamento**: ChromaDB local persistente
- **Embeddings**: HuggingFace Sentence Transformers (local)

📖 **Guia completo**: [README_RAG_LOCAL.md](README_RAG_LOCAL.md)

## 🎯 **Modos de Operação**

### 1. **Modo Demonstração** 🔑

- **Sem API Key**
- Respostas simuladas
- Interface completa funcional
- Ideal para testar a aplicação

### 2. **Modo IA Padrão** 🤖

- **Com API Key do OpenRouter**
- DeepSeek R1 com prompts especializados
- Respostas inteligentes personalizadas
- 7 professores com personalidades únicas

### 3. **Modo Professor Carlos RAG Local** ⭐

- **Matemática com sistema RAG local**
- Base de conhecimento local dos documentos da pasta matemática
- Busca semântica automática de conteúdo relevante
- Processamento local de DOCX, PDF e TXT
- **Funciona offline** (exceto para o LLM DeepSeek)

## 📊 **Tecnologias Utilizadas**

- **Frontend**: Streamlit
- **IA**: DeepSeek R1 0528 via OpenRouter
- **RAG**: Sistema de busca semântica local com LangChain
- **Vector Store**: ChromaDB local persistente
- **Embeddings**: HuggingFace Sentence Transformers (local)
- **Processamento**: pypdf, python-docx
- **Linguagem**: Python 3.8+

## 🎨 **Interface**

### 🎨 **Tema Azul Personalizado**

- **Cor principal**: #09278d
- **Gradientes**: Azul degradê
- **Elementos**: Botões, chat, headers personalizados
- **Responsivo**: Layout adaptável

### 💬 **Chat Interface**

- **Mensagens do usuário**: Azul, alinhadas à direita
- **Mensagens dos professores**: Azul claro, alinhadas à esquerda
- **Avatars**: Emojis únicos por professor
- **Histórico**: Persistente durante a sessão

### 📊 **Indicadores Visuais**

- **🔑 (Modo demonstração)**: Sem API Key configurada
- **🤖 (IA ativa)**: API Key configurada, IA funcional
- **📚 (Com material personalizado)**: Usando Google Drive
- **⭐ (Professor Especializado)**: Professor Carlos configurado
- **⭐ (RAG Integrado)**: Professor Carlos com base embutida ativo
- **🔑 (Credenciais integradas)**: Google Drive com credenciais automáticas

## 🔒 **Segurança e Privacidade**

### 🛡️ **Sistema RAG**

- **Base embutida**: Dados processados localmente
- **Sem dependências externas** para matemática
- **Busca local** na base de conhecimento
- **Privacidade total** dos materiais da Sther

### 🛡️ **Google Drive (Outras Matérias)**

- **Acesso somente leitura** aos documentos
- **Processamento local** dos arquivos
- **Não upload** de dados para terceiros
- **Credenciais seguras** via OAuth2

### 🔐 **API Keys**

- **Armazenamento temporário** apenas na sessão
- **Não persistência** em arquivos
- **Comunicação segura** via HTTPS
- **Sem logs** de chaves de API

## 🚨 **Solução de Problemas**

### ❌ **Professor Carlos não disponível**

```bash
# Verifique se o arquivo existe
ls math_teacher_embedded.py

# Reinstale dependências
pip install -r requirements.txt
```

### ❌ **Sistema RAG não funciona**

1. Verifique se a API Key está configurada
2. Confirme que tem créditos no OpenRouter
3. Teste com perguntas específicas (ex: "função quadrática")

### ❌ **Analogias não aparecem**

1. Marque a opção "🎭 Ativar analogias especiais da Sther"
2. Use perguntas que podem se beneficiar de analogias
3. O sistema decide automaticamente quando usar

## 🎯 **Roadmap**

### 🔮 **Próximas Funcionalidades**

- [ ] **Sistema RAG** para outras matérias
- [ ] **Base de conhecimento expandida** com mais conteúdos
- [ ] **Analogias dinâmicas** geradas pela IA
- [ ] **Sistema de favoritos** para perguntas importantes
- [ ] **Exportação de conversas** em PDF

### 🌟 **Melhorias Planejadas**

- [ ] **Interface mobile** otimizada
- [ ] **Modo escuro** opcional
- [ ] **Busca semântica avançada** com embeddings
- [ ] **Gamificação** com pontuação e conquistas
- [ ] **Relatórios de progresso** detalhados

## 🤝 **Contribuição**

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 💝 **Agradecimentos**

- **Sther**: Inspiração para este projeto
- **OpenRouter**: Acesso à DeepSeek R1 0528
- **Google**: APIs do Google Drive
- **Streamlit**: Framework incrível para interfaces
- **Comunidade Python**: Bibliotecas fantásticas

---

**Desenvolvido com ❤️ para o sucesso da Futura Senhora Sther Souza no ENEM! 🌟📚🚀**
