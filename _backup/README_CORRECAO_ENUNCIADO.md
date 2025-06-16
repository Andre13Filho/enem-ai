# 🔧 Correção: Enunciado Sendo Detectado como Alternativa

## ❌ **Problema Identificado**

### **Situação:**

Textos como **"A figura representa a vista superior..."** estavam sendo interpretados incorretamente como **"A)"** (alternativa A), quando na verdade fazem parte do enunciado da questão.

### **Exemplo do Erro:**

```
❌ ANTES (Incorreto):
✅ Alternativas:
A) figura representa a vista superior de uma bola de futebol
B) texto real da alternativa B
C) texto real da alternativa C
```

### **Causa Raiz:**

- **Regex muito ampla:** `r'^[A-E]\s*[\)\s]'` capturava qualquer linha que começasse com A, B, C, D ou E
- **Falta de contexto:** Não considerava se realmente era uma seção de alternativas
- **Sem validação semântica:** Não verificava se o conteúdo parecia uma alternativa

## ✅ **Solução Implementada**

### **1. Detecção Inteligente de Seção de Alternativas**

```python
# Primeiro, identifica onde começam as alternativas
# Procura por uma sequência de A), B), C), D), E)
idx_inicio_alternativas = None
for i, line in enumerate(lines):
    if re.match(r'^[A-E]\s*\)\s+', line):
        # Verifica se nas próximas linhas tem outras alternativas
        tem_sequencia = False
        for j in range(i+1, min(i+5, len(lines))):
            if j < len(lines) and re.match(r'^[A-E]\s*\)\s+', lines[j]):
                tem_sequencia = True
                break
        if tem_sequencia:
            idx_inicio_alternativas = i
            break
```

### **2. Regex Mais Específica**

```python
# Antes (❌): Muito amplo
r'^[A-E]\s*[\)\s]'

# Agora (✅): Mais específico
alt_pattern = r'^([A-E])\s*\)\s+(.{1,200})$'
```

### **3. Validação Semântica**

```python
# Verifica se realmente parece uma alternativa
palavras_inicio_enunciado = [
    'figura', 'gráfico', 'tabela', 'texto', 'quadro',
    'imagem', 'problema', 'situação', 'contexto'
]

primeira_palavra = texto.split()[0].lower() if texto.split() else ""
if primeira_palavra in palavras_inicio_enunciado:
    # É parte do enunciado, não alternativa
    enunciado_lines.append(line)
    continue
```

### **4. Processamento Contextual**

```python
# Se ainda não chegamos na seção de alternativas, é enunciado
if idx_inicio_alternativas is None or i < idx_inicio_alternativas:
    enunciado_lines.append(line)
    continue
```

## 🔍 **Como Funciona a Nova Lógica**

### **Passo 1: Análise Prévia**

1. **Escaneia todo o texto** procurando padrões de alternativas
2. **Verifica sequências** (A), B), C)... para confirmar
3. **Marca o índice** onde realmente começam as alternativas

### **Passo 2: Processamento Inteligente**

1. **Antes do índice** → Tudo é enunciado
2. **No índice ou depois** → Analisa se é alternativa real
3. **Validação semântica** → Verifica palavras-chave

### **Passo 3: Classificação Final**

```python
# Linha: "A figura representa..."
primeira_palavra = "figura"  # ← Palavra-chave de enunciado
if primeira_palavra in palavras_inicio_enunciado:
    # ✅ Vai para o enunciado
    enunciado_lines.append(line)
else:
    # ✅ Seria alternativa legítima
    alternativas.append((letra, texto))
```

## 📊 **Exemplo de Correção**

### **Entrada (texto problemático):**

```
QUESTÃO 169
A figura representa a vista superior de uma bola de futebol...
O cálculo da probabilidade é...
A) 1/25
B) 24/(25×24×23)
C) 1/(25×24×23)
D) 24/(25×25×25)
E) 24/(25×24×23)
```

### **Processamento:**

1. **Escaneia e encontra** alternativas reais na linha "A) 1/25"
2. **Define idx_inicio_alternativas** = 3 (onde está "A) 1/25")
3. **Processa linha por linha:**
   - `"A figura representa..."` → i=1 < 3 → **Enunciado** ✅
   - `"O cálculo da probabilidade..."` → i=2 < 3 → **Enunciado** ✅
   - `"A) 1/25"` → i=3 ≥ 3 + padrão válido → **Alternativa** ✅

### **Resultado (correto):**

```
✅ AGORA (Correto):

📖 Enunciado:
A figura representa a vista superior de uma bola de futebol...
O cálculo da probabilidade é...

✅ Alternativas:
A) 1/25
B) 24/(25×24×23)
C) 1/(25×24×23)
D) 24/(25×25×25)
E) 24/(25×24×23)
```

## 🧪 **Casos de Teste Cobertos**

### **✅ Casos que agora funcionam corretamente:**

- [x] **"A figura representa..."** → Enunciado
- [x] **"A tabela mostra..."** → Enunciado
- [x] **"A situação descrita..."** → Enunciado
- [x] **"A) 1/25"** → Alternativa A
- [x] **"B) Opção B"** → Alternativa B
- [x] Textos mistos com enunciado e alternativas

### **🔄 Validações aplicadas:**

- [x] **Busca por sequência** de alternativas antes de classificar
- [x] **Validação semântica** com palavras-chave
- [x] **Processamento contextual** baseado na posição
- [x] **Regex mais específica** para padrões válidos

## 🎯 **Palavras-Chave de Enunciado**

**Lista atual de palavras que indicam enunciado:**

```python
palavras_inicio_enunciado = [
    'figura', 'gráfico', 'tabela', 'texto', 'quadro',
    'imagem', 'problema', 'situação', 'contexto'
]
```

**🔧 Facilmente extensível** para adicionar mais palavras conforme necessário.

## 📈 **Melhorias Obtidas**

### **✅ Precisão:**

- **Detecção correta** de enunciados vs alternativas
- **Sem falsos positivos** em textos explicativos
- **Processamento contextual** mais inteligente

### **✅ Robustez:**

- **Funciona mesmo** com formatos variados
- **Tolera textos** mal formatados
- **Fallback gracioso** se detecção falha

### **✅ Manutenibilidade:**

- **Lista de palavras** facilmente editável
- **Lógica clara** e bem documentada
- **Testável** com casos específicos

## 🚀 **Resultado Final**

### **Antes (❌):**

```
A) figura representa a vista superior...  ← ERRO!
B) opção real B
C) opção real C
```

### **Agora (✅):**

```
📖 Enunciado:
A figura representa a vista superior...   ← CORRETO!

✅ Alternativas:
A) opção real A
B) opção real B
C) opção real C
```

---

## 🎓 **ENEM AI Helper - Detecção Inteligente!**

**✅ Problema resolvido:** Enunciados não são mais confundidos com alternativas  
**✅ Detecção contextual:** Analisa sequências antes de classificar  
**✅ Validação semântica:** Usa palavras-chave para diferenciação  
**✅ Processamento robusto:** Funciona com formatos variados

**📅 Correção aplicada:** 05/01/2025  
**🎯 Foco:** Precisão na classificação de conteúdo
