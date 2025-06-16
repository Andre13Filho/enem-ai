#!/usr/bin/env python3
"""
Teste para verificar o comportamento de pan/zoom no streamlit-markmap
"""

import streamlit as st
from streamlit_markmap import markmap

st.set_page_config(page_title="Teste Markmap Pan", layout="wide")

st.title("🧠 Teste Markmap - Pan e Zoom")

st.markdown("""
## Instruções de Teste:
1. **Zoom**: Use a roda do mouse para zoom in/out
2. **Pan (Arrastar)**: Clique e arraste para mover o mapa
3. **Nível**: Mude o nível e veja se o comportamento muda

Se você **não conseguir arrastar** o mapa, isso indica o problema.
""")

# Controles
col1, col2 = st.columns(2)

with col1:
    pan_enabled = st.checkbox("Habilitar Pan", value=True)
    zoom_enabled = st.checkbox("Habilitar Zoom", value=True)

with col2:
    initial_level = st.selectbox("Nível Inicial de Expansão", [1, 2, 3, -1], index=1)
    max_width = st.slider("Largura Máxima", 0, 500, 300)

# Dados de teste
data = f"""---
markmap:
  pan: {str(pan_enabled).lower()}
  zoom: {str(zoom_enabled).lower()}
  initialExpandLevel: {initial_level}
  maxWidth: {max_width}
  colorFreezeLevel: 2
  duration: 500
---

# 🎯 Matemática ENEM

## 📚 Álgebra
### 🔢 Equações
- Equação do 1º grau: $ax + b = 0$
- Equação do 2º grau: $ax^2 + bx + c = 0$
- Fórmula de Bhaskara: $x = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}$

### 📈 Funções
- Função linear: $f(x) = ax + b$
- Função quadrática: $f(x) = ax^2 + bx + c$
- Domínio e imagem

## 📐 Geometria
### 🔺 Figuras Planas
- Triângulos
- Quadriláteros
- Círculos
- Áreas: $A = \\pi r^2$

### 📦 Geometria Espacial
- Prismas
- Pirâmides
- Cilindros
- Volumes: $V = \\pi r^2 h$

## 📊 Estatística
### 📈 Medidas
- Média: $\\bar{{x}} = \\frac{{\\sum x_i}}{{n}}$
- Mediana
- Moda
- Desvio padrão

### 🎲 Probabilidade
- Espaço amostral
- Eventos
- $P(A) = \\frac{{n(A)}}{{n(\\Omega)}}$

## 🔢 Trigonometria
### 📐 Razões Trigonométricas
- Seno: $\\sin(\\theta) = \\frac{{cateto\\_oposto}}{{hipotenusa}}$
- Cosseno: $\\cos(\\theta) = \\frac{{cateto\\_adjacente}}{{hipotenusa}}$
- Tangente: $\\tan(\\theta) = \\frac{{\\sin(\\theta)}}{{\\cos(\\theta)}}$

### 🌊 Funções Trigonométricas
- Gráfico de seno
- Gráfico de cosseno
- Período e amplitude
"""

st.markdown("---")

# Status das configurações
st.markdown("### ⚙️ Configurações Atuais:")
st.json({
    "pan": pan_enabled,
    "zoom": zoom_enabled,
    "initialExpandLevel": initial_level,
    "maxWidth": max_width
})

st.markdown("---")

# Renderizar o mapa mental
try:
    markmap(data, height=600)
    
    st.success("✅ Mapa mental renderizado com sucesso!")
    
    st.markdown("### 🧪 Instruções de Teste:")
    st.markdown("""
    - **Se você conseguir arrastar**: ✅ Pan está funcionando
    - **Se não conseguir arrastar**: ❌ Problema identificado
    - **Teste zoom**: Use a roda do mouse
    - **Teste expansão**: Clique nos nós para expandir/colapsar
    """)
    
except Exception as e:
    st.error(f"❌ Erro ao renderizar: {str(e)}")
    st.code(data, language="markdown") 