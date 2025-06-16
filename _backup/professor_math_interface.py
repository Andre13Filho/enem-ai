import streamlit as st
import sqlite3
import json
import pandas as pd
from typing import List, Dict
from datetime import datetime
from math_exercises_database_creator import EnemMathDatabase, MathTopic

# Configuração da página
st.set_page_config(
    page_title="Professor Carlos - Chat com Sther AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ProfessorStherChat:
    def __init__(self):
        self.db = EnemMathDatabase()
        
        # Inicializa histórico do chat se não existir
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            st.session_state.chat_history.append({
                'sender': 'Sther',
                'message': 'Olá, Professor Carlos! Sou a Sther AI. Posso ajudá-lo com exercícios de matemática do ENEM. Como posso ajudar hoje?',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        
    def main(self):
        st.title("🤖 Professor Carlos - Sistema Sther AI")
        
        # Criando as abas
        tab1, tab2 = st.tabs(["💬 Chat", "🧠 Mapa Mental"])
        
        with tab1:
            self.show_chat_tab()
            
        with tab2:
            self.show_mind_map_tab()
    
    def show_chat_tab(self):
        st.markdown("## 💬 Chat com Sther AI")
        
        # Sidebar com estatísticas para o chat
        with st.sidebar:
            st.markdown("## 📊 Base de Dados")
            
            stats = self.db.get_statistics()
            
            st.metric("Total de Exercícios", stats['total_exercises'])
            st.metric("Anos Disponíveis", len(stats['by_year']))
            st.metric("Tópicos Diferentes", len(stats['by_topic']))
            
            st.markdown("### 📚 Tópicos Disponíveis")
            if stats['by_topic']:
                for topic, count in stats['by_topic'].items():
                    st.write(f"**{topic}:** {count}")
            
            st.markdown("---")
            st.markdown("### ℹ️ Como usar")
            st.info("""
            **Exemplos de solicitações:**
            - "Sther, preciso de exercícios de Geometria"
            - "Me envie questões do ENEM 2024"
            - "Quero exercícios de Probabilidade"
            - "Mostre exercícios de Funções"
            """)
            
            if st.button("🗑️ Limpar Chat"):
                st.session_state.chat_history = []
                st.session_state.chat_history.append({
                    'sender': 'Sther',
                    'message': 'Chat limpo! Como posso ajudar agora?',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                st.rerun()
        
        # Container para o histórico do chat
        chat_container = st.container()
        
        with chat_container:
            # Mostra histórico do chat
            for chat in st.session_state.chat_history:
                if chat['sender'] == 'Professor':
                    with st.chat_message("user"):
                        st.write(f"**{chat['timestamp']}** - {chat['message']}")
                else:  # Sther
                    with st.chat_message("assistant"):
                        st.write(f"**{chat['timestamp']}** - {chat['message']}")
                        
                        # Se a mensagem contém exercícios, mostra eles
                        if 'exercises' in chat:
                            self.display_exercises_in_chat(chat['exercises'])
        
        # Input do usuário
        st.markdown("---")
        user_message = st.chat_input("Digite sua mensagem para a Sther...")
        
        if user_message:
            self.process_user_message(user_message)
    
    def show_mind_map_tab(self):
        st.markdown("## 🧠 Mapa Mental dos Tópicos ENEM")
        
        stats = self.db.get_statistics()
        
        if not stats['by_topic']:
            st.warning("Nenhum dado disponível para gerar o mapa mental.")
            return
        
        # Estatísticas gerais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 Total de Exercícios", stats['total_exercises'])
        
        with col2:
            st.metric("📅 Anos Cobertos", len(stats['by_year']))
        
        with col3:
            st.metric("🎯 Tópicos Únicos", len(stats['by_topic']))
        
        st.markdown("---")
        
        # Visualização dos tópicos
        st.markdown("### 📊 Distribuição por Tópicos")
        
        # Gráfico de barras
        if stats['by_topic']:
            df_topics = pd.DataFrame(list(stats['by_topic'].items()), columns=['Tópico', 'Quantidade'])
            df_topics = df_topics.sort_values('Quantidade', ascending=True)
            
            st.bar_chart(df_topics.set_index('Tópico'))
            
            # Tabela detalhada
            st.markdown("### 📋 Detalhamento por Tópico")
            df_topics_sorted = df_topics.sort_values('Quantidade', ascending=False)
            
            for _, row in df_topics_sorted.iterrows():
                percentage = (row['Quantidade'] / stats['total_exercises']) * 100
                st.write(f"**{row['Tópico']}:** {row['Quantidade']} exercícios ({percentage:.1f}%)")
        
        st.markdown("---")
        
        # Visualização por anos
        st.markdown("### 📅 Distribuição por Anos")
        
        if stats['by_year']:
            df_years = pd.DataFrame(list(stats['by_year'].items()), columns=['Ano', 'Quantidade'])
            df_years = df_years.sort_values('Ano')
            
            st.line_chart(df_years.set_index('Ano'))
            
            # Tabela de anos
            st.markdown("### 📊 Exercícios por Ano")
            df_years_sorted = df_years.sort_values('Ano', ascending=False)
            
            for _, row in df_years_sorted.iterrows():
                percentage = (row['Quantidade'] / stats['total_exercises']) * 100
                st.write(f"**ENEM {row['Ano']}:** {row['Quantidade']} exercícios ({percentage:.1f}%)")
        
        st.markdown("---")
        
        # Mapa mental textual
        st.markdown("### 🗺️ Mapa Mental Estruturado")
        
        st.markdown("""
        ```
        📚 ENEM MATEMÁTICA (557 exercícios)
        ├── 🔢 ÁLGEBRA
        │   ├── Equações e Inequações
        │   ├── Sistemas Lineares
        │   └── Polinômios
        │
        ├── 📐 GEOMETRIA
        │   ├── Geometria Plana
        │   ├── Geometria Espacial
        │   └── Trigonometria
        │
        ├── 📊 ESTATÍSTICA E PROBABILIDADE
        │   ├── Análise de Dados
        │   ├── Probabilidade
        │   └── Estatística Descritiva
        │
        ├── 📈 FUNÇÕES
        │   ├── Função Afim
        │   ├── Função Quadrática
        │   ├── Função Exponencial
        │   └── Função Logarítmica
        │
        ├── 💰 MATEMÁTICA FINANCEIRA
        │   ├── Porcentagem
        │   ├── Juros Simples e Compostos
        │   └── Descontos
        │
        └── 🔗 OUTROS TÓPICOS
            ├── Progressões
            ├── Análise Combinatória
            └── Geometria Analítica
        ```
        """)
    
    def process_user_message(self, message: str):
        # Adiciona mensagem do professor ao chat
        st.session_state.chat_history.append({
            'sender': 'Professor',
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # Processa a mensagem e gera resposta da Sther
        sther_response = self.generate_sther_response(message)
        
        # Adiciona resposta da Sther
        st.session_state.chat_history.append(sther_response)
        
        st.rerun()
    
    def generate_sther_response(self, user_message: str) -> Dict:
        message_lower = user_message.lower()
        
        # Verifica se é uma solicitação de exercícios
        if any(word in message_lower for word in ['exercício', 'exercicios', 'questão', 'questões', 'questao', 'questoes']):
            
            # Identifica o tipo de solicitação
            if 'geometria' in message_lower:
                exercises = self.db.get_exercises_by_topic('Geometria')
                topic = 'Geometria'
            elif 'função' in message_lower or 'funções' in message_lower:
                exercises = self.db.get_exercises_by_topic('Funções')
                topic = 'Funções'
            elif 'probabilidade' in message_lower or 'estatística' in message_lower:
                exercises = self.db.get_exercises_by_topic('Estatística e Probabilidade')
                topic = 'Estatística e Probabilidade'
            elif 'álgebra' in message_lower or 'algebra' in message_lower:
                exercises = self.db.get_exercises_by_topic('Álgebra')
                topic = 'Álgebra'
            elif any(year in message_lower for year in ['2024', '2023', '2022', '2021', '2020']):
                # Extrai o ano da mensagem
                year = None
                for y in ['2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015']:
                    if y in message_lower:
                        year = int(y)
                        break
                
                if year:
                    exercises = self.db.get_exercises_by_year(year)
                    topic = f'ENEM {year}'
                else:
                    exercises = []
                    topic = 'Geral'
            else:
                # Busca geral - pega alguns exercícios aleatórios
                all_stats = self.db.get_statistics()
                if all_stats['by_topic']:
                    first_topic = list(all_stats['by_topic'].keys())[0]
                    exercises = self.db.get_exercises_by_topic(first_topic)[:5]
                    topic = 'Exercícios Gerais'
                else:
                    exercises = []
                    topic = 'Geral'
            
            # Prepara resposta com exercícios
            if exercises:
                # Limita a 5 exercícios para não sobrecarregar o chat
                limited_exercises = exercises[:5]
                
                response_message = f"📚 Encontrei {len(exercises)} exercícios de {topic}. Aqui estão os primeiros {len(limited_exercises)}:"
                
                return {
                    'sender': 'Sther',
                    'message': response_message,
                    'exercises': limited_exercises,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            else:
                return {
                    'sender': 'Sther',
                    'message': f"❌ Desculpe, não encontrei exercícios para essa solicitação. Tente especificar um tópico como Geometria, Funções, ou um ano específico.",
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
        
        # Resposta padrão para outras mensagens
        elif 'olá' in message_lower or 'oi' in message_lower:
            return {
                'sender': 'Sther',
                'message': "Olá, Professor Carlos! Como posso ajudá-lo com exercícios de matemática hoje?",
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        elif 'ajuda' in message_lower or 'help' in message_lower:
            return {
                'sender': 'Sther',
                'message': """🤖 **Como posso ajudar:**

📚 **Para exercícios por tópico:**
- "Preciso de exercícios de Geometria"
- "Mostre questões de Funções"
- "Quero exercícios de Probabilidade"

📅 **Para exercícios por ano:**
- "Exercícios do ENEM 2024"
- "Questões de 2023"

💡 **Tópicos disponíveis:**
Geometria, Funções, Estatística e Probabilidade, Álgebra, Matemática Financeira, e outros.""",
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        else:
            return {
                'sender': 'Sther',
                'message': f"Entendi sua mensagem: '{user_message}'. Para solicitar exercícios, use termos como 'exercícios de Geometria' ou 'questões do ENEM 2024'. Digite 'ajuda' para ver mais opções.",
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
    
    def display_exercises_in_chat(self, exercises: List[Dict]):
        """Exibe exercícios formatados no chat"""
        for i, exercise in enumerate(exercises, 1):
            with st.expander(f"📝 Exercício {i} - ENEM {exercise['year']} Q{exercise['question_number']} ({exercise['topic']})"):
                st.write("**ENUNCIADO:**")
                st.write(exercise['question_text'])
                
                st.write("**ALTERNATIVAS:**")
                try:
                    alternatives = json.loads(exercise['alternatives']) if isinstance(exercise['alternatives'], str) else exercise['alternatives']
                    if alternatives:
                        for j, alt in enumerate(alternatives):
                            letter = chr(65 + j)  # A, B, C, D, E
                            st.write(f"{letter}) {alt}")
                    else:
                        st.write("_(Alternativas não disponíveis)_")
                except:
                    st.write("_(Erro ao carregar alternativas)_")
                
                # Botão para exportar este exercício específico
                if st.button(f"📤 Exportar Exercício {i}", key=f"export_{exercise['id']}"):
                    self.export_single_exercise(exercise)

    def export_single_exercise(self, exercise: Dict):
        """Exporta um único exercício"""
        formatted_exercise = {
            'id': exercise['id'],
            'year': exercise['year'],
            'question_number': exercise['question_number'],
            'topic': exercise['topic'],
            'statement': exercise['question_text'],
            'alternatives': json.loads(exercise['alternatives']) if isinstance(exercise['alternatives'], str) else exercise['alternatives'],
            'exported_at': datetime.now().isoformat(),
            'exported_by': 'Professor Carlos via Sther AI'
        }
        
        filename = f"sther_exercise_{exercise['id'].lower()}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(formatted_exercise, f, indent=2, ensure_ascii=False)
        
        # Adiciona mensagem de confirmação ao chat
        st.session_state.chat_history.append({
            'sender': 'Sther',
            'message': f"✅ Exercício exportado com sucesso!\n📁 Arquivo: {filename}",
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        st.success(f"✅ Exercício exportado: {filename}")

def main():
    interface = ProfessorStherChat()
    interface.main()

if __name__ == "__main__":
    main()
