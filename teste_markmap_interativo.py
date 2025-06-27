#!/usr/bin/env python3
"""
Teste simples para verificar a interatividade do mapa mental
"""

import streamlit as st
from mapa_mental_markmap import garantir_configuracoes_interatividade

# Configuração da página
st.set_page_config(
    page_title="Teste Mapa Mental Interativo",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Teste de Mapa Mental Interativo")

# Teste com markdown simples
markdown_teste = """# 🎯 Teste de Interatividade

## 📚 Conceito 1
### 🔍 Definição
- Item 1
- Item 2

### 📐 Propriedades
- Propriedade A
- Propriedade B

## 🧮 Conceito 2
### ⚡ Aplicações
- Aplicação 1
- Aplicação 2

### 🎯 Exemplos
- Exemplo 1
- Exemplo 2
"""

# Aplicar configurações de interatividade
markdown_com_config = garantir_configuracoes_interatividade(markdown_teste)

st.markdown("### 📋 Markdown Original:")
st.code(markdown_teste, language="markdown")

st.markdown("### 🔧 Markdown com Configurações:")
st.code(markdown_com_config, language="markdown")

# Renderizar o mapa mental
try:
    from streamlit_markmap import markmap
    st.markdown("### 🗺️ Mapa Mental Renderizado:")
    markmap(markdown_com_config, height=600)
    st.success("✅ Mapa mental renderizado com sucesso!")
except ImportError:
    st.error("❌ streamlit-markmap não instalado. Execute: pip install streamlit-markmap==1.0.1")
except Exception as e:
    st.error(f"❌ Erro ao renderizar: {str(e)}")

# Informações de debug
with st.expander("🔍 Debug Info"):
    st.write("Configurações aplicadas:")
    st.write("- pan: true")
    st.write("- zoom: true")
    st.write("- autoFit: true")
    st.write("- zoomInButton: true")
    st.write("- zoomOutButton: true")
    st.write("- resetButton: true") 