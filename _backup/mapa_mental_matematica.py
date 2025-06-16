#!/usr/bin/env python3
"""
Mapa Mental Interativo de Matemática
Sistema para navegação visual e interativa dos tópicos de matemática do ENEM
"""

import streamlit as st
from typing import Dict, List, Any
import json

# Estrutura hierárquica dos tópicos de matemática
MAPA_MATEMATICA = {
    "Matemática ENEM": {
        "icon": "🎓",
        "description": "Todos os tópicos de matemática do ENEM",
        "children": {
            "Álgebra": {
                "icon": "🔢",
                "description": "Operações algébricas e equações",
                "children": {
                    "Funções": {
                        "icon": "📈",
                        "description": "Estudo de funções matemáticas",
                        "children": {
                            "Função do 1º Grau": {
                                "icon": "📏",
                                "description": "f(x) = ax + b",
                                "formulas": ["f(x) = ax + b", "coeficiente angular: a", "coeficiente linear: b"],
                                "keywords": ["função linear", "reta", "coeficiente angular", "coeficiente linear"]
                            },
                            "Função do 2º Grau": {
                                "icon": "📊",
                                "description": "f(x) = ax² + bx + c",
                                "formulas": ["f(x) = ax² + bx + c", "Δ = b² - 4ac", "x = (-b ± √Δ)/2a"],
                                "keywords": ["parábola", "vértice", "discriminante", "bhaskara", "delta"]
                            },
                            "Função Exponencial": {
                                "icon": "📈",
                                "description": "f(x) = aˣ",
                                "formulas": ["f(x) = aˣ", "crescimento exponencial", "decaimento exponencial"],
                                "keywords": ["exponencial", "crescimento", "decaimento", "base"]
                            },
                            "Função Logarítmica": {
                                "icon": "📉",
                                "description": "f(x) = log_a(x)",
                                "formulas": ["log_a(x)", "log(xy) = log(x) + log(y)", "log(x/y) = log(x) - log(y)"],
                                "keywords": ["logaritmo", "log", "propriedades logarítmicas"]
                            }
                        }
                    },
                    "Equações e Inequações": {
                        "icon": "⚖️",
                        "description": "Resolução de equações e inequações",
                        "children": {
                            "Equações do 1º Grau": {
                                "icon": "🎯",
                                "description": "ax + b = 0",
                                "formulas": ["ax + b = 0", "x = -b/a"],
                                "keywords": ["equação linear", "solução única"]
                            },
                            "Equações do 2º Grau": {
                                "icon": "🎯",
                                "description": "ax² + bx + c = 0",
                                "formulas": ["ax² + bx + c = 0", "x = (-b ± √Δ)/2a"],
                                "keywords": ["equação quadrática", "duas soluções", "raízes"]
                            },
                            "Sistemas Lineares": {
                                "icon": "🔗",
                                "description": "Sistema de equações lineares",
                                "formulas": ["ax + by = c", "dx + ey = f"],
                                "keywords": ["sistema", "substituição", "adição", "determinante"]
                            }
                        }
                    }
                }
            },
            "Geometria": {
                "icon": "📐",
                "description": "Estudo de formas e espaços",
                "children": {
                    "Geometria Plana": {
                        "icon": "⬜",
                        "description": "Figuras em duas dimensões",
                        "children": {
                            "Triângulos": {
                                "icon": "🔺",
                                "description": "Propriedades dos triângulos",
                                "formulas": ["Área = (b×h)/2", "Lei dos senos", "Lei dos cossenos"],
                                "keywords": ["triângulo", "área", "perímetro", "altura", "hipotenusa"]
                            },
                            "Quadriláteros": {
                                "icon": "🔲",
                                "description": "Quadrados, retângulos, etc.",
                                "formulas": ["Área = b×h", "Perímetro = 2(b+h)"],
                                "keywords": ["quadrado", "retângulo", "paralelogramo", "losango"]
                            },
                            "Círculo e Circunferência": {
                                "icon": "⭕",
                                "description": "Propriedades do círculo",
                                "formulas": ["Área = πr²", "Perímetro = 2πr"],
                                "keywords": ["círculo", "raio", "diâmetro", "pi", "circunferência"]
                            }
                        }
                    },
                    "Geometria Espacial": {
                        "icon": "🧊",
                        "description": "Figuras em três dimensões",
                        "children": {
                            "Prismas": {
                                "icon": "📦",
                                "description": "Prismas e suas propriedades",
                                "formulas": ["Volume = Área_base × altura"],
                                "keywords": ["prisma", "volume", "área superficial", "base"]
                            },
                            "Pirâmides": {
                                "icon": "🔺",
                                "description": "Pirâmides e suas propriedades",
                                "formulas": ["Volume = (1/3) × Área_base × altura"],
                                "keywords": ["pirâmide", "volume", "altura", "apótema"]
                            },
                            "Cilindros": {
                                "icon": "🥫",
                                "description": "Cilindros e suas propriedades",
                                "formulas": ["Volume = πr²h", "Área lateral = 2πrh"],
                                "keywords": ["cilindro", "volume", "área lateral", "raio"]
                            }
                        }
                    }
                }
            },
            "Trigonometria": {
                "icon": "📏",
                "description": "Relações trigonométricas",
                "children": {
                    "Razões Trigonométricas": {
                        "icon": "📐",
                        "description": "Seno, cosseno e tangente",
                        "formulas": ["sen(θ) = cateto oposto/hipotenusa", "cos(θ) = cateto adjacente/hipotenusa", "tan(θ) = cateto oposto/cateto adjacente"],
                        "keywords": ["seno", "cosseno", "tangente", "hipotenusa", "cateto"]
                    },
                    "Círculo Trigonométrico": {
                        "icon": "🔄",
                        "description": "Relações no círculo unitário",
                        "formulas": ["sen²(θ) + cos²(θ) = 1"],
                        "keywords": ["círculo trigonométrico", "radianos", "graus", "período"]
                    }
                }
            },
            "Estatística e Probabilidade": {
                "icon": "📊",
                "description": "Análise de dados e probabilidade",
                "children": {
                    "Medidas de Tendência Central": {
                        "icon": "📈",
                        "description": "Média, mediana e moda",
                        "formulas": ["Média = Σx/n", "Mediana = valor central", "Moda = valor mais frequente"],
                        "keywords": ["média", "mediana", "moda", "dados", "frequência"]
                    },
                    "Probabilidade": {
                        "icon": "🎲",
                        "description": "Cálculo de probabilidades",
                        "formulas": ["P(A) = casos favoráveis/casos possíveis", "P(A∪B) = P(A) + P(B) - P(A∩B)"],
                        "keywords": ["probabilidade", "evento", "espaço amostral", "união", "interseção"]
                    }
                }
            },
            "Matrizes e Determinantes": {
                "icon": "🔢",
                "description": "Álgebra linear básica",
                "children": {
                    "Matrizes": {
                        "icon": "📋",
                        "description": "Operações com matrizes",
                        "formulas": ["A + B", "A × B", "A^(-1)"],
                        "keywords": ["matriz", "soma", "multiplicação", "inversa", "transposta"]
                    },
                    "Determinantes": {
                        "icon": "🎯",
                        "description": "Cálculo de determinantes",
                        "formulas": ["det(A) = ad - bc (2x2)", "Regra de Sarrus (3x3)"],
                        "keywords": ["determinante", "cofator", "regra de sarrus", "menor complementar"]
                    }
                }
            }
        }
    }
}

class MapaMentalMatematica:
    def __init__(self):
        self.current_path = ["Matemática ENEM"]
        self.expanded_nodes = set(["Matemática ENEM"])
        
    def get_current_node(self) -> Dict[str, Any]:
        """Retorna o nó atual baseado no caminho"""
        node = MAPA_MATEMATICA
        for step in self.current_path:
            node = node[step]
        return node
    
    def get_node_by_path(self, path: List[str]) -> Dict[str, Any]:
        """Retorna um nó específico pelo caminho"""
        node = MAPA_MATEMATICA
        for step in path:
            if step in node:
                node = node[step]
            else:
                return None
        return node
    
    def expand_node(self, node_path: List[str]):
        """Expande um nó"""
        path_str = " > ".join(node_path)
        self.expanded_nodes.add(path_str)
    
    def collapse_node(self, node_path: List[str]):
        """Colapsa um nó"""
        path_str = " > ".join(node_path)
        if path_str in self.expanded_nodes:
            self.expanded_nodes.remove(path_str)
    
    def is_expanded(self, node_path: List[str]) -> bool:
        """Verifica se um nó está expandido"""
        path_str = " > ".join(node_path)
        return path_str in self.expanded_nodes
    
    def navigate_to(self, path: List[str]):
        """Navega para um nó específico"""
        self.current_path = path
    
    def get_all_leaf_nodes(self) -> List[Dict[str, Any]]:
        """Retorna todos os nós folha (tópicos finais)"""
        leaf_nodes = []
        
        def traverse(node, path):
            if "children" not in node:
                leaf_nodes.append({
                    "path": path,
                    "node": node,
                    "topic": path[-1]
                })
            else:
                for child_name, child_node in node["children"].items():
                    traverse(child_node, path + [child_name])
        
        traverse(MAPA_MATEMATICA["Matemática ENEM"], ["Matemática ENEM"])
        return leaf_nodes

def render_node_card(node: Dict[str, Any], path: List[str], mapa: MapaMentalMatematica):
    """Renderiza um cartão de nó"""
    node_name = path[-1]
    has_children = "children" in node
    is_expanded = mapa.is_expanded(path)
    path_str = " > ".join(path)
    
    # Estilo do cartão baseado no nível
    level = len(path) - 1
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    color = colors[level % len(colors)]
    
    # Container do cartão
    with st.container():
        col1, col2, col3 = st.columns([1, 6, 1])
        
        with col2:
            # Cartão principal
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}20, {color}10);
                border-left: 4px solid {color};
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">{node.get('icon', '📝')}</span>
                    <strong style="color: {color}; font-size: 1.1rem;">{node_name}</strong>
                    {f'<span style="color: #666; font-size: 0.8rem;">({len(node["children"])} tópicos)</span>' if has_children else ''}
                </div>
                <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">{node.get('description', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botões de ação
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if has_children:
                    if is_expanded:
                        if st.button(f"🔼 Colapsar", key=f"collapse_{path_str}"):
                            mapa.collapse_node(path)
                            st.rerun()
                    else:
                        if st.button(f"🔽 Expandir", key=f"expand_{path_str}"):
                            mapa.expand_node(path)
                            st.rerun()
            
            with col_btn2:
                if st.button(f"🎯 Focar", key=f"focus_{path_str}"):
                    mapa.navigate_to(path)
                    st.rerun()
            
            with col_btn3:
                if st.button(f"❓ Explicar", key=f"explain_{path_str}"):
                    return path  # Sinaliza que deve explicar este tópico
            
            # Fórmulas (se existirem)
            if "formulas" in node:
                st.markdown("**📐 Fórmulas principais:**")
                for formula in node["formulas"]:
                    st.markdown(f'<div class="arithmatex">$${formula}$$</div>', unsafe_allow_html=True)
    
    return None

def render_breadcrumb(path: List[str], mapa: MapaMentalMatematica):
    """Renderiza breadcrumb de navegação"""
    st.markdown("### 🗺️ Navegação")
    
    breadcrumb_items = []
    for i, step in enumerate(path):
        if i == len(path) - 1:
            breadcrumb_items.append(f"**{step}**")
        else:
            # Cria botão clicável para navegar
            if st.button(step, key=f"nav_{i}"):
                mapa.navigate_to(path[:i+1])
                st.rerun()
            breadcrumb_items.append(step)
    
    st.markdown(" > ".join(breadcrumb_items))
    st.markdown("---")

def search_topics(query: str) -> List[Dict[str, Any]]:
    """Busca tópicos por palavra-chave"""
    results = []
    
    def search_in_node(node, path, query_lower):
        # Busca no nome do nó
        if query_lower in path[-1].lower():
            results.append({"path": path, "node": node, "match_type": "name"})
        
        # Busca na descrição
        if query_lower in node.get("description", "").lower():
            results.append({"path": path, "node": node, "match_type": "description"})
        
        # Busca nas keywords
        if "keywords" in node:
            for keyword in node["keywords"]:
                if query_lower in keyword.lower():
                    results.append({"path": path, "node": node, "match_type": "keyword"})
                    break
        
        # Busca nas fórmulas
        if "formulas" in node:
            for formula in node["formulas"]:
                if query_lower in formula.lower():
                    results.append({"path": path, "node": node, "match_type": "formula"})
                    break
        
        # Recursão nos filhos
        if "children" in node:
            for child_name, child_node in node["children"].items():
                search_in_node(child_node, path + [child_name], query_lower)
    
    query_lower = query.lower()
    search_in_node(MAPA_MATEMATICA["Matemática ENEM"], ["Matemática ENEM"], query_lower)
    
    # Remove duplicatas
    unique_results = []
    seen_paths = set()
    for result in results:
        path_str = " > ".join(result["path"])
        if path_str not in seen_paths:
            unique_results.append(result)
            seen_paths.add(path_str)
    
    return unique_results

def explain_topic_with_ai(topic_path: List[str], node: Dict[str, Any]) -> str:
    """Gera explicação automática do tópico usando Professor Carlos"""
    try:
        from professor_carlos_local import professor_carlos_local
        
        topic_name = topic_path[-1]
        description = node.get("description", "")
        keywords = node.get("keywords", [])
        formulas = node.get("formulas", [])
        
        # Monta pergunta contextualizada
        question = f"""
Olá Professor Carlos! Gostaria de uma explicação didática sobre: {topic_name}

Contexto: {description}

Por favor, explique:
1. O que é e para que serve
2. Como aplicar no ENEM
3. Dicas importantes para Sther
4. Exemplos práticos

{f"Palavras-chave relacionadas: {', '.join(keywords)}" if keywords else ""}
{f"Fórmulas envolvidas: {', '.join(formulas)}" if formulas else ""}

Seja didático e encorajador!
"""
        
        # Verifica se tem API key configurada
        api_key = st.session_state.get('api_key', '')
        if not api_key:
            return """
🔑 **Configure sua API Key primeiro!**

Para receber explicações personalizadas do Professor Carlos:
1. Acesse a barra lateral
2. Configure sua API Key do OpenRouter
3. Clique novamente em "Explicar" neste tópico

💡 **Enquanto isso, aqui está o que sabemos:**
- Tópico: {topic_name}
- Descrição: {description}
""".format(topic_name=topic_name, description=description)
        
        # Gera resposta
        response = professor_carlos_local.get_response(question, api_key)
        return response
        
    except Exception as e:
        return f"""
❌ **Erro ao gerar explicação**

Detalhes: {str(e)}

💡 **Informações básicas do tópico:**
- **Tópico:** {topic_path[-1]}
- **Descrição:** {node.get('description', 'Não disponível')}
- **Nível:** {' > '.join(topic_path[1:])}

Tente recarregar a página ou verificar sua conexão.
"""

def render_mapa_mental_ui():
    """Interface principal do mapa mental"""
    
    # Inicializa estado se necessário
    if 'mapa_mental' not in st.session_state:
        st.session_state.mapa_mental = MapaMentalMatematica()
    
    mapa = st.session_state.mapa_mental
    
    st.markdown("# 🧠 Mapa Mental - Matemática ENEM")
    st.markdown("Explore os tópicos de matemática de forma visual e interativa!")
    
    # Barra de busca
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Buscar tópico:", placeholder="Ex: função quadrática, trigonometria, geometria...")
    
    with col2:
        if st.button("🏠 Início"):
            mapa.navigate_to(["Matemática ENEM"])
            st.rerun()
    
    # Resultados da busca
    if search_query:
        st.markdown("### 🔍 Resultados da Busca")
        results = search_topics(search_query)
        
        if results:
            for result in results[:5]:  # Máximo 5 resultados
                path = result["path"]
                node = result["node"]
                match_type = result["match_type"]
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    **{path[-1]}** ({' > '.join(path[1:-1])})  
                    *{node.get('description', '')}*  
                    🎯 Encontrado em: {match_type}
                    """)
                
                with col2:
                    if st.button("📍 Ir para", key=f"goto_{' > '.join(path)}"):
                        mapa.navigate_to(path)
                        st.rerun()
        else:
            st.info("Nenhum tópico encontrado. Tente outras palavras-chave.")
        
        st.markdown("---")
    
    # Breadcrumb
    render_breadcrumb(mapa.current_path, mapa)
    
    # Nó atual
    current_node = mapa.get_current_node()
    
    # Renderiza o nó atual
    explain_request = render_node_card(current_node, mapa.current_path, mapa)
    
    # Se foi solicitada explicação
    if explain_request:
        st.markdown("### 🤖 Explicação do Professor Carlos")
        with st.spinner("Professor Carlos preparando explicação..."):
            explanation = explain_topic_with_ai(explain_request, mapa.get_node_by_path(explain_request))
            st.markdown(f'<div class="arithmatex">{explanation}</div>', unsafe_allow_html=True)
        st.markdown("---")
    
    # Filhos do nó atual (se expandido)
    if "children" in current_node and mapa.is_expanded(mapa.current_path):
        st.markdown("### 📂 Subtópicos")
        
        children = current_node["children"]
        for child_name, child_node in children.items():
            child_path = mapa.current_path + [child_name]
            
            explain_request_child = render_node_card(child_node, child_path, mapa)
            
            # Se foi solicitada explicação do filho
            if explain_request_child:
                st.markdown(f"### 🤖 Explicação: {child_name}")
                with st.spinner("Professor Carlos preparando explicação..."):
                    explanation = explain_topic_with_ai(explain_request_child, child_node)
                    st.markdown(f'<div class="arithmatex">{explanation}</div>', unsafe_allow_html=True)
                st.markdown("---")
            
            # Renderiza filhos do filho se expandido
            if "children" in child_node and mapa.is_expanded(child_path):
                st.markdown(f"#### 📁 Subtópicos de {child_name}")
                for grandchild_name, grandchild_node in child_node["children"].items():
                    grandchild_path = child_path + [grandchild_name]
                    
                    explain_request_grandchild = render_node_card(grandchild_node, grandchild_path, mapa)
                    
                    if explain_request_grandchild:
                        st.markdown(f"### 🤖 Explicação: {grandchild_name}")
                        with st.spinner("Professor Carlos preparando explicação..."):
                            explanation = explain_topic_with_ai(explain_request_grandchild, grandchild_node)
                            st.markdown(f'<div class="arithmatex">{explanation}</div>', unsafe_allow_html=True)
                        st.markdown("---")
    
    # Estatísticas no final
    st.markdown("---")
    st.markdown("### 📊 Estatísticas do Mapa")
    
    col1, col2, col3 = st.columns(3)
    
    leaf_nodes = mapa.get_all_leaf_nodes()
    
    with col1:
        st.metric("📝 Total de Tópicos", len(leaf_nodes))
    
    with col2:
        st.metric("🔍 Nível Atual", len(mapa.current_path) - 1)
    
    with col3:
        st.metric("📂 Nós Expandidos", len(mapa.expanded_nodes))

# Função principal para integração com o app
def display_mapa_mental():
    """Função principal para exibir o mapa mental"""
    render_mapa_mental_ui() 