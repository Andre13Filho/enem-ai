# 🚀 Guia de Deploy - ENEM AI Helper no Streamlit Cloud

## 📋 Pré-requisitos

### 1. Conta no GitHub

- Repositório público ou privado com o código
- Todos os arquivos commitados (exceto secrets)

### 2. Conta no Streamlit Cloud

- Acesse: https://share.streamlit.io/
- Faça login com GitHub

### 3. Chave da API Groq

- Obtenha em: https://console.groq.com/
- Modelo usado: `deepseek-r1-distill-llama-70b`

## 🔧 Configuração do Repositório

### Arquivos Essenciais

```
enem_ai_helper/
├── app.py                    # Aplicação principal
├── requirements.txt          # Dependências
├── cloud_config.py          # Configuração adaptativa
├── .streamlit/
│   ├── config.toml          # Configuração do Streamlit
│   └── secrets.toml         # Secrets (NÃO commitar)
├── physics_formatter.py     # Formatador de física
├── local_physics_rag.py     # Sistema RAG de física
├── professor_fernando_local.py # Professor de física
└── [outros arquivos RAG]
```

### Dependências Otimizadas

O `requirements.txt` foi otimizado para o cloud:

- Removidas dependências pesadas desnecessárias
- Versões específicas para estabilidade
- Compatibilidade com Streamlit Cloud

## ⚙️ Configuração no Streamlit Cloud

### 1. Criar Nova App

1. Acesse https://share.streamlit.io/
2. Clique em "New app"
3. Conecte seu repositório GitHub
4. Configure:
   - **Repository**: `seu-usuario/enem_ai_helper`
   - **Branch**: `main` (ou sua branch principal)
   - **Main file path**: `app.py`
   - **App URL**: `enem-ai-helper` (ou nome desejado)

### 2. Configurar Secrets

No painel do Streamlit Cloud, vá em "Settings" > "Secrets" e adicione:

```toml
# Chave da API Groq (obrigatória)
GROQ_API_KEY = "sua_chave_groq_aqui"

# Configurações opcionais
[features]
ENABLE_LOCAL_RAG = true
ENABLE_EXERCISES = true
ENABLE_REDACAO = false

[performance]
MAX_TOKENS = 4000
TEMPERATURE = 0.7
MAX_RETRIES = 3
```

## 🏗️ Adaptações Implementadas

### Sistema de Configuração Adaptativa

- **Local**: Usa arquivos `.env` e pastas locais
- **Cloud**: Usa `st.secrets` e documentos de exemplo
- **Detecção automática** do ambiente

### Gerenciamento de Documentos

- **Local**: Carrega documentos das pastas locais
- **Cloud**: Cria documentos de exemplo automaticamente
- **Fallback**: Sistema funciona mesmo sem documentos

### Bancos de Dados

- **Local**: ChromaDB persistente em disco
- **Cloud**: ChromaDB temporário em memória
- **Recriação**: Vectorstores são recriados a cada sessão

### Formatação de Fórmulas

- **LaTeX**: Renderização matemática via MathJax
- **Física**: Formatador específico para fórmulas de física
- **Matemática**: Formatador para expressões matemáticas

## 🚀 Processo de Deploy

### 1. Preparar Repositório

```bash
# Commit todas as mudanças
git add .
git commit -m "Preparar para deploy no Streamlit Cloud"
git push origin main
```

### 2. Deploy Automático

- O Streamlit Cloud detecta mudanças automaticamente
- Build e deploy são feitos automaticamente
- Logs disponíveis no painel

### 3. Verificar Deploy

- Acesse a URL da sua app
- Teste todas as funcionalidades
- Verifique logs em caso de erro

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de API Key

```
❌ Configure GROQ_API_KEY nas secrets do Streamlit Cloud
```

**Solução**: Adicionar `GROQ_API_KEY` nas secrets

#### 2. Erro de Dependências

```
❌ ModuleNotFoundError: No module named 'xxx'
```

**Solução**: Adicionar dependência no `requirements.txt`

#### 3. Erro de Memória

```
❌ Memory limit exceeded
```

**Solução**: Otimizar código, reduzir tamanho dos documentos

#### 4. Timeout

```
❌ App timeout
```

**Solução**: Otimizar carregamento, usar cache do Streamlit

### Logs e Debugging

- **Logs**: Disponíveis no painel do Streamlit Cloud
- **Debug**: Usar `st.write()` para debug temporário
- **Performance**: Monitorar uso de memória e CPU

## 📊 Monitoramento

### Métricas Importantes

- **Tempo de resposta**: < 30 segundos
- **Uso de memória**: < 1GB
- **Uptime**: 99%+
- **Erros**: < 1%

### Otimizações

- **Cache**: Usar `@st.cache_data` para dados estáticos
- **Lazy loading**: Carregar módulos sob demanda
- **Cleanup**: Limpar recursos temporários

## 🔄 Atualizações

### Deploy Contínuo

1. Faça mudanças no código local
2. Commit e push para GitHub
3. Streamlit Cloud atualiza automaticamente
4. Teste a nova versão

### Rollback

- Use branches para versões estáveis
- Mude a branch no painel se necessário
- Mantenha backups dos secrets

## 🎯 Funcionalidades Disponíveis no Cloud

### ✅ Funcionando

- **Professores AI**: Todos os 7 professores
- **Chat**: Interface completa
- **Formatação**: LaTeX e fórmulas
- **RAG**: Sistema com documentos de exemplo
- **Exercícios**: Sistema básico

### ⚠️ Limitações

- **Documentos**: Apenas exemplos (não os arquivos completos)
- **Vectorstore**: Temporário (recriado a cada sessão)
- **Performance**: Limitada pelos recursos do Streamlit Cloud

### 🔮 Melhorias Futuras

- **Banco de dados externo**: PostgreSQL ou MongoDB
- **Storage**: AWS S3 ou Google Cloud Storage
- **Cache**: Redis para vectorstores
- **CDN**: Para arquivos estáticos

## 📞 Suporte

### Recursos

- **Documentação**: https://docs.streamlit.io/streamlit-cloud
- **Comunidade**: https://discuss.streamlit.io/
- **GitHub Issues**: Para bugs específicos

### Contato

- **Email**: suporte@exemplo.com
- **Discord**: #enem-ai-helper
- **GitHub**: Issues no repositório

---

## 🎉 Conclusão

O ENEM AI Helper está agora otimizado para funcionar perfeitamente no Streamlit Cloud, mantendo todas as funcionalidades principais enquanto se adapta às limitações do ambiente cloud.

**URL da Aplicação**: https://enem-ai-helper.streamlit.app/

**Status**: ✅ Pronto para produção
