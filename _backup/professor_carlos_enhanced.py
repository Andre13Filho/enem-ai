"""
Professor Carlos - Versão Aprimorada
Integra o sistema RAG aprimorado com interface melhorada
"""

import streamlit as st
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Importa sistema RAG aprimorado
from enhanced_local_math_rag import EnhancedLocalMathRAG

# Encoding utils
from encoding_utils import safe_decode, safe_encode, safe_api_error

class ProfessorCarlosEnhanced:
    """Professor Carlos com sistema RAG aprimorado"""
    
    def __init__(self):
        # Inicializa sistema RAG aprimorado
        self.enhanced_rag = None
        self.initialize_enhanced_system()
        
        # Configurações da interface
        self.show_debug_info = False
        self.conversation_history = []
    
    def initialize_enhanced_system(self):
        """Inicializa sistema RAG aprimorado"""
        try:
            self.enhanced_rag = EnhancedLocalMathRAG()
            
            # Verifica se precisa processar documentos
            if not os.path.exists("./chroma_math_enhanced"):
                st.info("🔄 Sistema aprimorado detectado. Processamento inicial pode ser necessário.")
            
        except Exception as e:
            st.error(f"Erro ao inicializar sistema aprimorado: {str(e)}")
            self.enhanced_rag = None
    
    def process_documents_if_needed(self) -> bool:
        """Processa documentos se necessário"""
        if not self.enhanced_rag:
            return False
        
        try:
            if os.path.exists("./matemática"):
                with st.spinner("🔄 Processando documentos com melhorias..."):
                    return self.enhanced_rag.process_math_documents_enhanced()
            else:
                st.warning("📁 Pasta 'matemática' não encontrada. Usando vectorstore existente.")
                return True
        except Exception as e:
            st.error(f"Erro no processamento: {str(e)}")
            return False
    
    def get_enhanced_response(self, user_message: str, api_key: str) -> Dict[str, Any]:
        """Gera resposta usando sistema aprimorado"""
        if not self.enhanced_rag:
            return {
                "answer": "❌ Sistema aprimorado não está disponível. Verifique a configuração.",
                "sources": [],
                "enhancement_info": {"error": "Sistema não inicializado"}
            }
        
        try:
            # Gera resposta com sistema aprimorado
            result = self.enhanced_rag.get_enhanced_response(
                user_message, 
                api_key, 
                self.conversation_history
            )
            
            # Adiciona ao histórico
            self.conversation_history.append({
                "user": user_message,
                "assistant": result.get("answer", ""),
                "timestamp": str(Path(__file__).stat().st_mtime)
            })
            
            # Mantém apenas últimas 10 interações
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return result
            
        except Exception as e:
            return {
                "answer": safe_api_error(e),
                "sources": [],
                "enhancement_info": {"error": str(e)}
            }
    
    def render_enhanced_interface(self, api_key: str):
        """Renderiza interface aprimorada do Professor Carlos"""
        
        # Header melhorado
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0;">🎬 Professor Carlos - Versão Aprimorada + Séries da Sther!</h1>
            <p style="color: #e0e7ff; margin: 5px 0 0 0;">
                Sistema RAG com analogias das séries favoritas da Sther (FRIENDS, TBBT, Stranger Things, Grey's Anatomy, WandaVision)
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações das séries integradas
        st.markdown("""
        ### 🎭 Séries Integradas nas Explicações:
        
        - 👥 **FRIENDS**: Álgebra, probabilidade e trabalho em equipe matemático
        - 🧪 **The Big Bang Theory**: Física, cálculo e conceitos científicos
        - 🌌 **Stranger Things**: Geometria, trigonometria e mistérios matemáticos  
        - 🏥 **Grey's Anatomy**: Funções, estatística e análise de dados
        - ✨ **WandaVision**: Geometria avançada, física e transformações
        
        **🎬 O Professor Carlos agora começa TODAS as explicações com analogias das suas séries favoritas!**
        """)
        
        st.divider()
        
        # Painel de controle
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🔄 Reprocessar Documentos", help="Reprocessa com melhorias"):
                if self.process_documents_if_needed():
                    st.success("✅ Documentos reprocessados com sucesso!")
                    st.experimental_rerun()
        
        with col2:
            self.show_debug_info = st.checkbox("🔍 Debug Info", 
                                              value=self.show_debug_info,
                                              help="Mostra informações de reranking")
        
        with col3:
            if st.button("📊 Estatísticas"):
                self.show_enhanced_stats()
        
        # Área principal de chat
        st.markdown("### 💬 Chat com Professor Carlos")
        
        # Input do usuário
        user_message = st.text_area(
            "Sua pergunta:",
            height=100,
            placeholder="Ex: Como resolver uma equação do segundo grau?",
            key="enhanced_user_input"
        )
        
        if st.button("🚀 Enviar (Versão Aprimorada)", type="primary"):
            if user_message.strip():
                self.handle_enhanced_query(user_message, api_key)
        
        # Exibe histórico se disponível
        if self.conversation_history:
            self.render_conversation_history()
    
    def handle_enhanced_query(self, user_message: str, api_key: str):
        """Processa consulta com sistema aprimorado"""
        
        with st.spinner("🤖 Professor Carlos está analisando com sistema aprimorado..."):
            # Gera resposta
            result = self.get_enhanced_response(user_message, api_key)
            
            # Exibe resposta principal
            st.markdown("### 👨‍🏫 Resposta do Professor Carlos")
            
            # Aplica formatação matemática
            formatted_answer = self.format_math_content(result.get("answer", ""))
            st.markdown(formatted_answer, unsafe_allow_html=True)
            
            # Informações de debug se habilitadas
            if self.show_debug_info and "reranking_info" in result:
                self.render_debug_info(result)
            
            # Fontes utilizadas
            if result.get("sources"):
                self.render_sources_info(result["sources"])
    
    def format_math_content(self, content: str) -> str:
        """Aplica formatação matemática melhorada"""
        # Formatação básica para LaTeX
        import re
        
        # Substitui padrões matemáticos simples
        content = re.sub(r'\$\$(.*?)\$\$', r'$$\1$$', content)
        content = re.sub(r'\$(.*?)\$', r'$\1$', content)
        
        # Destaca fórmulas
        content = re.sub(
            r'(f\(x\)\s*=|y\s*=|x\s*=)',
            r'**\1**',
            content
        )
        
        # Melhora formatação de listas
        content = re.sub(r'^(\d+\.|\*|\-)', r'**\1**', content, flags=re.MULTILINE)
        
        return content
    
    def render_debug_info(self, result: Dict[str, Any]):
        """Renderiza informações de debug do reranking"""
        st.markdown("### 🔍 Informações de Debug (Sistema Aprimorado)")
        
        # Métricas do reranking
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Documentos Encontrados", 
                result.get("total_docs_found", 0)
            )
        
        with col2:
            st.metric(
                "Após Reranking", 
                result.get("docs_after_reranking", 0)
            )
        
        with col3:
            if result.get("reranking_info"):
                avg_score = sum(info["final_score"] for info in result["reranking_info"]) / len(result["reranking_info"])
                st.metric("Score Médio", f"{avg_score:.3f}")
        
        # Detalhes do reranking
        if result.get("reranking_info"):
            st.markdown("#### 📈 Detalhes do Reranking")
            
            for i, info in enumerate(result["reranking_info"], 1):
                with st.expander(f"Resultado {i} - {info['explanation']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Score Semântico:** {info['semantic_score']:.3f}")
                        st.write(f"**Score Final:** {info['final_score']:.3f}")
                    
                    with col2:
                        st.write(f"**Explicação:** {info['explanation']}")
    
    def render_sources_info(self, sources: List[Dict[str, Any]]):
        """Renderiza informações das fontes"""
        st.markdown("### 📚 Fontes Utilizadas")
        
        for i, source in enumerate(sources, 1):
            with st.expander(f"📄 Fonte {i}: {source['source']} (Score: {source['score']:.3f})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Tópico:** {source['topic']}")
                    st.write(f"**Tipo:** {source['section_type']}")
                
                with col2:
                    st.write(f"**Score:** {source['score']:.3f}")
                
                st.write("**Preview:**")
                st.text(source['content_preview'])
    
    def show_enhanced_stats(self):
        """Exibe estatísticas do sistema aprimorado"""
        if not self.enhanced_rag:
            st.error("Sistema não inicializado")
            return
        
        stats = self.enhanced_rag.get_enhanced_stats()
        
        if "error" in stats:
            st.error(f"Erro ao obter estatísticas: {stats['error']}")
            return
        
        st.markdown("### 📊 Estatísticas do Sistema Aprimorado")
        
        # Métricas gerais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Chunks", stats.get("total_chunks", 0))
        
        with col2:
            st.metric("Reranking", "✅ Ativado" if stats.get("reranking_enabled") else "❌ Inativo")
        
        with col3:
            st.metric("Chunking", stats.get("chunking_strategy", "Básico"))
        
        # Distribuição por tópicos
        if stats.get("topics_distribution"):
            st.markdown("#### 📋 Distribuição por Tópicos")
            topics_data = stats["topics_distribution"]
            
            # Gráfico simples com barras
            for topic, count in topics_data.items():
                percentage = (count / stats["total_chunks"]) * 100
                st.write(f"**{topic.title()}:** {count} chunks ({percentage:.1f}%)")
                st.progress(percentage / 100)
        
        # Distribuição por tipos de seção
        if stats.get("section_types_distribution"):
            st.markdown("#### 🏗️ Distribuição por Tipos de Seção")
            sections_data = stats["section_types_distribution"]
            
            for section_type, count in sections_data.items():
                percentage = (count / stats["total_chunks"]) * 100
                st.write(f"**{section_type.title()}:** {count} chunks ({percentage:.1f}%)")
                st.progress(percentage / 100)
        
        # Configurações técnicas
        with st.expander("⚙️ Configurações Técnicas"):
            st.write(f"**Modelo de Embeddings:** {stats.get('embeddings_model', 'Padrão')}")
            st.write(f"**Estratégia de Chunking:** {stats.get('chunking_strategy', 'Padrão')}")
            st.write(f"**Sofisticação de Prompts:** {stats.get('prompt_sophistication', 'Padrão')}")
    
    def render_conversation_history(self):
        """Renderiza histórico de conversas"""
        st.markdown("### 💭 Histórico da Conversa")
        
        for i, interaction in enumerate(reversed(self.conversation_history[-5:]), 1):
            with st.expander(f"Interação {len(self.conversation_history) - i + 1}"):
                st.write(f"**👤 Você:** {interaction['user']}")
                st.write(f"**🤖 Professor Carlos:** {interaction['assistant'][:200]}...")

def main():
    """Função principal para executar Professor Carlos Aprimorado"""
    st.set_page_config(
        page_title="Professor Carlos - Aprimorado",
        page_icon="🧮",
        layout="wide"
    )
    
    # Verifica chave da API
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("🔑 Configure GROQ_API_KEY nas secrets ou variáveis de ambiente")
        return
    
    # Inicializa Professor Carlos aprimorado
    professor = ProfessorCarlosEnhanced()
    
    # Renderiza interface
    professor.render_enhanced_interface(api_key)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🚀 Professor Carlos - Versão Aprimorada</p>
        <p>✅ Chunking Inteligente | ✅ Reranking Avançado | ✅ Prompts Sofisticadas | ✅ Embeddings Aprimorados</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 