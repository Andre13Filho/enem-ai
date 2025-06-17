# 🚨 **SOLUÇÃO RÁPIDA** - Erro de Inicialização dos Professores

## ⚠️ **PROBLEMA:**
```
❌ Falha na inicialização do sistema. Verifique sua API key e documentos.
```

## 🔧 **SOLUÇÃO EM 3 PASSOS:**

### **Passo 1: Obter API Key da Groq (GRATUITO)**
1. 🌐 Acesse: https://console.groq.com/
2. 📝 Faça login ou crie conta gratuita
3. 🔑 Vá em **"API Keys"**
4. ➕ Clique em **"Create API Key"**
5. 📋 **Copie** a chave (começa com `gsk_...`)

### **Passo 2: Configurar no Sistema**
1. 📁 Abra o arquivo: `.streamlit/secrets.toml`
2. 🔍 Encontre a linha:
   ```toml
   GROQ_API_KEY = "sua_chave_groq_aqui"
   ```
3. ✏️ **Substitua** `"sua_chave_groq_aqui"` pela sua chave real
4. 💾 **Salve** o arquivo

### **Passo 3: Testar**
1. 🔄 Reinicie a aplicação
2. ✅ Teste uma pergunta para qualquer professor
3. 🎉 Os professores devem funcionar normalmente!

---

## 📋 **EXEMPLO DE CONFIGURAÇÃO CORRETA:**

```toml
# ✅ ASSIM ESTÁ CORRETO:
GROQ_API_KEY = "gsk_1234567890abcdef..."

# ❌ ASSIM ESTÁ ERRADO:
GROQ_API_KEY = "sua_chave_groq_aqui"
```

---

## 🆘 **SE AINDA DER ERRO:**

### **Verificações:**
- ✅ API key começa com `gsk_`?
- ✅ Não há espaços extras?
- ✅ Arquivo foi salvo?
- ✅ Aplicação foi reiniciada?

### **Erro comum:**
```
# ❌ ERRO - Aspas erradas:
GROQ_API_KEY = 'gsk_...'

# ✅ CORRETO - Aspas duplas:
GROQ_API_KEY = "gsk_..."
```

---

## 🎯 **APÓS CONFIGURAR:**

Os professores especialistas ficarão disponíveis:
- 🧮 **Professor Carlos** (Matemática)
- 🧪 **Professora Luciana** (Química)  
- 🧬 **Professor Roberto** (Biologia)
- 📚 **Professor Eduardo** (História)
- 🌍 **Professora Marina** (Geografia)
- ⚡ **Professor Fernando** (Física)
- 📖 **Professora Letícia** (Português)

**Boa sorte, Sther! 🚀** 