#!/usr/bin/env python3
"""
Mapa Mental Simples de Matemática - Versão Funcional
"""

import streamlit as st

def display_mapa_mental():
    """Versão mínima funcional do mapa mental"""
    
    st.markdown("# 🧠 Mapa Mental - Matemática ENEM")
    st.markdown("Explore os tópicos de matemática de forma visual e interativa!")
    
    # Estado simples
    if 'mm_topic' not in st.session_state:
        st.session_state.mm_topic = "inicio"
    
    # Menu principal
    if st.session_state.mm_topic == "inicio":
        st.markdown("## 📚 Escolha um tópico:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔢 Álgebra", use_container_width=True):
                st.session_state.mm_topic = "algebra"
                st.rerun()
        
        with col2:
            if st.button("📐 Geometria", use_container_width=True):
                st.session_state.mm_topic = "geometria"
                st.rerun()
        
        with col3:
            if st.button("📏 Trigonometria", use_container_width=True):
                st.session_state.mm_topic = "trigonometria"
                st.rerun()
        
        # Segunda linha
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Estatística", use_container_width=True):
                st.session_state.mm_topic = "estatistica"
                st.rerun()
        
        with col2:
            if st.button("🔢 Matrizes", use_container_width=True):
                st.session_state.mm_topic = "matrizes"
                st.rerun()
        
        with col3:
            if st.button("📈 Progressões", use_container_width=True):
                st.session_state.mm_topic = "progressoes"
                st.rerun()
    
    else:
        # Mostrar tópico específico
        mostrar_topico(st.session_state.mm_topic)

def mostrar_topico(topico):
    """Mostra detalhes de um tópico específico"""
    
    # Botão voltar
    if st.button("🏠 Voltar ao Início"):
        st.session_state.mm_topic = "inicio"
        st.rerun()
    
    st.markdown("---")
    
    # Conteúdo baseado no tópico
    topicos_info = {
        "algebra": {
            "titulo": "🔢 Álgebra",
            "descricao": "Funções, equações e expressões algébricas",
            "formulas": [
                "Função do 1º grau: $f(x) = ax + b$",
                "Função do 2º grau: $f(x) = ax^2 + bx + c$",
                "Fórmula de Bhaskara: $x = \\frac{-b \\pm \\sqrt{\\Delta}}{2a}$"
            ]
        },
        "geometria": {
            "titulo": "📐 Geometria",
            "descricao": "Formas, áreas, volumes e propriedades geométricas",
            "formulas": [
                "Área do triângulo: $A = \\frac{base \\times altura}{2}$",
                "Área do círculo: $A = \\pi r^2$",
                "Volume do cilindro: $V = \\pi r^2 h$"
            ]
        },
        "trigonometria": {
            "titulo": "📏 Trigonometria",
            "descricao": "Relações trigonométricas e funções circulares",
            "formulas": [
                "Lei dos senos: $\\frac{a}{\\sin A} = \\frac{b}{\\sin B} = \\frac{c}{\\sin C}$",
                "Lei dos cossenos: $c^2 = a^2 + b^2 - 2ab\\cos C$",
                "Identidade fundamental: $\\sin^2 x + \\cos^2 x = 1$"
            ]
        },
        "estatistica": {
            "titulo": "📊 Estatística e Probabilidade",
            "descricao": "Análise de dados, médias e probabilidades",
            "formulas": [
                "Média aritmética: $\\bar{x} = \\frac{\\sum x_i}{n}$",
                "Probabilidade: $P(A) = \\frac{\\text{casos favoráveis}}{\\text{casos possíveis}}$",
                "Desvio padrão: $\\sigma = \\sqrt{\\frac{\\sum (x_i - \\bar{x})^2}{n}}$"
            ]
        },
        "matrizes": {
            "titulo": "🔢 Matrizes e Determinantes",
            "descricao": "Operações com matrizes e sistemas lineares",
            "formulas": [
                "Determinante 2×2: $\\det(A) = ad - bc$",
                "Matriz inversa: $A^{-1} = \\frac{1}{\\det(A)} \\cdot \\text{adj}(A)$",
                "Produto de matrizes: $(AB)_{ij} = \\sum_{k} a_{ik} b_{kj}$"
            ]
        },
        "progressoes": {
            "titulo": "📈 Progressões",
            "descricao": "Progressões aritméticas e geométricas",
            "formulas": [
                "PA - termo geral: $a_n = a_1 + (n-1)r$",
                "PA - soma: $S_n = \\frac{n(a_1 + a_n)}{2}$",
                "PG - termo geral: $a_n = a_1 \\cdot q^{n-1}$"
            ]
        }
    }
    
    info = topicos_info.get(topico, {
        "titulo": f"📝 {topico.title()}",
        "descricao": "Tópico em desenvolvimento",
        "formulas": ["Em breve..."]
    })
    
    st.markdown(f"## {info['titulo']}")
    st.markdown(f"*{info['descricao']}*")
    
    st.markdown("### 📐 Fórmulas Principais")
    for formula in info['formulas']:
        st.markdown(f"- {formula}")
    
    # Botão para explicação (simplificado)
    if st.button(f"🤖 Pedir Explicação sobre {info['titulo']}"):
        api_key = getattr(st.session_state, 'api_key', '')
        
        if not api_key:
            st.warning("""
🔑 **Configure sua API Key da Groq primeiro!**

1. Vá para a aba "💬 Chat"
2. Configure sua API Key na barra lateral  
3. Volte aqui e clique novamente

💡 **Dica:** Você já pode estudar as fórmulas mostradas acima!
""")
        else:
            with st.spinner("Professor Carlos preparando explicação..."):
                try:
                    from professor_carlos_local import professor_carlos_local
                    
                    pergunta = f"Explique de forma didática sobre {info['titulo']} para o ENEM, incluindo dicas importantes e exemplos práticos."
                    
                    resposta = professor_carlos_local.get_response(pergunta, api_key)
                    
                    st.markdown("### 👨‍🏫 Explicação do Professor Carlos")
                    st.markdown(f'<div class="arithmatex">{resposta}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar explicação: {str(e)}")
                    st.info("💡 Tente usar a aba 'Chat' para conversar diretamente com o Professor Carlos!")

# Versão simplificada - o mapa mental agora funciona diretamente
if __name__ == "__main__":
    # Para teste direto
    import streamlit as st
    try:
        st.set_page_config(page_title="Mapa Mental", page_icon="🧠")
    except st.errors.StreamlitAPIException:
        # Já foi configurado pelo app principal, ignora
        pass
    display_mapa_mental() 