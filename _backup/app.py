import streamlit as st
import time
import re
from typing import Dict, List, Any
from datetime import datetime
from groq import Groq

# Configura encoding seguro
try:
    from encoding_utils import setup_encoding
    setup_encoding()
except ImportError:
    pass

# Importa Professor Carlos com sistema RAG Local
try:
    from professor_carlos_local import setup_professor_carlos_local_ui, get_professor_carlos_local_response
    PROFESSOR_CARLOS_LOCAL_AVAILABLE = True
except ImportError:
    PROFESSOR_CARLOS_LOCAL_AVAILABLE = False
    st.error("❌ Professor Carlos Local não disponível. Verifique as dependências")

# Importa sistema de exercícios do ENEM
try:
    from enem_exercises_rag import enem_exercises_rag
    from exercise_formatter import display_exercise_card, format_exercise_content, format_multiple_choice_alternatives
    ENEM_EXERCISES_AVAILABLE = True
except ImportError:
    ENEM_EXERCISES_AVAILABLE = False
    st.warning("⚠️ Sistema de exercícios do ENEM não disponível. Verifique as dependências")

# Configuração da página
st.set_page_config(
    page_title="ENEM AI Helper - Professores Particulares para Sther",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .stSelectbox > div > div {
        background-color: #09278d;
        color: white;
        border-radius: 10px;
        border: none;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #09278d 0%, #1e3a8a 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(9, 39, 141, 0.4);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #09278d;
        background-color: #f8fafc;
    }
    
    .teacher-intro {
        background: linear-gradient(90deg, #09278d 0%, #1e3a8a 100%);
        color: white !important;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .teacher-intro h3 {
        color: white !important;
    }
    
    .teacher-intro p {
        color: white !important;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #09278d 0%, #1e3a8a 100%);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuração das matérias e professores
SUBJECTS = {
    "Matemática": {
        "teacher": "Prof. Carlos",
        "icon": "🧮",
        "description": "Especialista em matemática do ENEM com sistema RAG local baseado em seus documentos",
        "intro": "Olá, Futura Senhora Sther Souza! Sou o Professor Carlos, seu professor particular de Matemática! Agora trabalho com seus materiais locais e tenho acesso direto aos seus documentos de matemática. Vamos dominar a matemática do ENEM juntos! 🚀"
    },
    "Português": {
        "teacher": "Profa. Ana",
        "icon": "📚",
        "description": "Literatura, gramática e interpretação de texto",
        "intro": "Olá, Sther! Sou a Professora Ana, especialista em Português para o ENEM. Vou te ajudar com gramática, literatura e redação!"
    },
    "Biologia": {
        "teacher": "Prof. Roberto",
        "icon": "🧬",
        "description": "Biologia celular, genética e ecologia",
        "intro": "E aí, Sther! Sou o Professor Roberto de Biologia. Vamos desvendar os mistérios da vida juntos!"
    },
    "Geografia": {
        "teacher": "Profa. Marina",
        "icon": "🌍",
        "description": "Geografia física, humana e geopolítica",
        "intro": "Oi, Sther! Sou a Professora Marina de Geografia. Vamos explorar o mundo e suas transformações!"
    },
    "História": {
        "teacher": "Prof. Eduardo",
        "icon": "🏛️",
        "description": "História do Brasil e História Geral",
        "intro": "Olá, Sther! Sou o Professor Eduardo de História. Vamos viajar no tempo e entender nosso passado!"
    },
    "Química": {
        "teacher": "Profa. Luciana",
        "icon": "⚗️",
        "description": "Química orgânica, inorgânica e físico-química",
        "intro": "Oi, Sther! Sou a Professora Luciana de Química. Vamos misturar conhecimento e descobrir reações incríveis!"
    },
    "Física": {
        "teacher": "Prof. Fernando",
        "icon": "⚡",
        "description": "Mecânica, termodinâmica e eletromagnetismo",
        "intro": "E aí, Sther! Sou o Professor Fernando de Física. Vamos entender como o universo funciona!"
    },
    "Redação": {
        "teacher": "Profa. Carla",
        "icon": "✍️",
        "description": "Técnicas de redação e dissertação argumentativa",
        "intro": "Olá, Sther! Sou a Professora Carla de Redação. Vamos transformar suas ideias em textos nota 1000!"
    }
}

# Inicialização do session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {subject: [] for subject in SUBJECTS.keys()}
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = "Matemática"
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'processing_message' not in st.session_state:
    st.session_state.processing_message = False
if 'generated_exercises' not in st.session_state:
    st.session_state.generated_exercises = {subject: [] for subject in SUBJECTS.keys()}
if 'last_user_question' not in st.session_state:
    st.session_state.last_user_question = {subject: "" for subject in SUBJECTS.keys()}

# Inicializa variáveis de controle para Enter
for subject in SUBJECTS.keys():
    if f'send_message_{subject}' not in st.session_state:
        st.session_state[f'send_message_{subject}'] = False
    if f'last_message_{subject}' not in st.session_state:
        st.session_state[f'last_message_{subject}'] = ""

class GroqTeacher:
    """Professor genérico usando DeepSeek R1 Distill via Groq"""
    
    def __init__(self, subject_info: Dict):
        self.subject_info = subject_info
        self.name = subject_info["teacher"]
        self.subject = None  # Will be set when used
    
    def get_response(self, user_message: str, api_key: str) -> str:
        """Gera resposta usando DeepSeek R1 Distill via Groq"""
        
        if not api_key:
            return f"""
🔑 **Configure sua API Key da Groq**

Para ativar {self.name}, você precisa:
1. Obter uma API Key da Groq (https://console.groq.com)
2. Inserir a chave na barra lateral
3. Começar a conversar!

💡 {self.name} está pronto para te ajudar com {self.subject}!
"""
        
        try:
            client = Groq(api_key=api_key)
            
            # Prompt estruturado e profissional para cada professor
            system_prompt = f"""# IDENTIDADE DO PROFESSOR
Você é {self.name}, professor(a) especialista em {self.subject} para o ENEM.
Você é professor particular exclusivo da Sther Souza, uma estudante de 17 anos.

# DIRETRIZES DE COMPORTAMENTO
## Personalidade:
- Didático, paciente e bem-humorado
- Linguagem adequada para jovens de 17 anos
- Seja um professor que gosta de ensinar
- Seja carinhoso, mas profissional
- Seja engraçado, mas profissional
- Dê uma aula para uma jovem de 17 anos que tem dificuldades em sua matéria

## Metodologia de Ensino:
- Use analogias e exemplos práticos
- Relacione com situações do cotidiano brasileiro
- Foque nos tópicos que caem no ENEM
- Responda sempre em português brasileiro

## Estrutura da Resposta:
1. 🎬 **SEMPRE inicie com uma analogia das séries favoritas da Sther** (FRIENDS, The Big Bang Theory, Stranger Things, Grey's Anatomy, WandaVision)
2. Responda a pergunta de forma clara e completa
3. Use formatação em markdown para organizar o conteúdo
4. Inclua exemplos práticos quando relevante
5. SEMPRE termine perguntando sobre exercícios

## 🎭 ANALOGIAS DAS SÉRIES POR TÓPICO (USE SEMPRE):

### 🍕 FRIENDS:
- **Álgebra**: "Como Monica organizava suas receitas por categorias - na álgebra, organizamos variáveis e constantes!"
- **Funções**: "Pense nas funções como o relacionamento de Ross e Rachel - para cada 'entrada' há uma 'saída' específica!"
- **Geometria**: "Como quando Phoebe tentava ensinar Joey sobre as 'coordenadas' do apartamento!"
- **Probabilidade**: "Lembra quando Chandler calculava as chances? 'Could this BE more matemático?'"

### 🧪 THE BIG BANG THEORY:
- **Física**: "Como Sheldon explicava: 'Bazinga! A física é simples quando você entende as leis fundamentais!'"
- **Álgebra**: "Como Leonard tentava explicar conceitos para Penny - cada peça tem seu lugar!"
- **Cálculo**: "Como Howard calculava trajetórias para a NASA - derivadas emocionais!"
- **Estatística**: "Raj usaria estatística para calcular suas chances no amor!"

### 🌌 STRANGER THINGS:
- **Geometria**: "Como Dustin explicava sobre as dimensões no Mundo Invertido!"
- **Trigonometria**: "Como eles usavam coordenadas para navegar em Hawkins!"
- **Álgebra**: "Como quando Will precisava resolver os códigos do Mundo Invertido!"

### 🏥 GREY'S ANATOMY:
- **Funções**: "Como Meredith dizia: 'Você é minha pessoa!' - cada entrada tem sua 'pessoa' específica!"
- **Estatística**: "Como analisavam estatísticas de sucesso das cirurgias no Seattle Grace!"
- **Probabilidade**: "Derek sempre calculava os riscos antes de cada cirurgia!"

### ✨ WANDAVISION:
- **Geometria**: "Como Wanda criava realidades com geometrias perfeitas em Westview!"
- **Trigonometria**: "Visão calculava ângulos e trajetórias com precisão para voar!"
- **Física**: "Como Wanda manipulava a realidade com sua Magia do Caos!"

# FORMATO DA RESPOSTA OBRIGATÓRIO:
Sua resposta deve seguir EXATAMENTE esta estrutura:

1. 🎬 **Analogia das Séries**: Inicie SEMPRE com uma analogia das séries favoritas da Sther
2. 👋 **Cumprimento personalizado**: "Olá Sther!" 
3. 📚 **Explicação clara**: Responda a pergunta conectando com a analogia
4. 📝 **Exemplo prático**: Quando aplicável, use exemplos que reforcem a analogia
5. 🎯 **Fechamento motivacional**: Conecte de volta com as séries
6. ❓ **Pergunta obrigatória sobre exercícios**

# INSTRUÇÃO OBRIGATÓRIA
SEMPRE termine sua resposta com uma dessas frases específicas:
- "Que tal praticar com alguns exercícios do ENEM sobre este tópico, Sther?"
- "Quer que eu traga alguns exercícios do ENEM para você praticar, Sther?"
- "Vamos consolidar o aprendizado com exercícios do ENEM, Sther?"
- "Que tal testar seus conhecimentos com questões do ENEM, Sther?"

# RESTRIÇÕES
- Mantenha foco no currículo do ENEM
- Evite informações excessivamente avançadas
- Use linguagem simples mas precisa"""
            
            response = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # ✅ Temperatura baixa para respostas consistentes
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            from encoding_utils import safe_str
            error_msg = safe_str(e)
            
            return f"""
❌ **Erro na comunicação**

Detalhes: {error_msg}

💡 Verifique sua API Key e conexão com a internet.
"""

def get_teacher_response(subject: str, user_message: str, api_key: str) -> str:
    """Retorna resposta do professor específico"""
    
    # Professor Carlos especializado (RAG Local)
    if subject == "Matemática" and PROFESSOR_CARLOS_LOCAL_AVAILABLE:
        return get_professor_carlos_local_response(user_message, api_key)
    
    # Outros professores (Groq genérico)
    else:
        teacher = GroqTeacher(SUBJECTS[subject])
        teacher.subject = subject
        return teacher.get_response(user_message, api_key)

def add_teacher_intro(subject: str):
    """Adiciona mensagem de introdução do professor"""
    
    if not st.session_state.chat_history[subject]:
        intro_message = {
            "role": "assistant",
            "content": SUBJECTS[subject]["intro"],
            "timestamp": datetime.now().strftime("%H:%M")
        }
        st.session_state.chat_history[subject].append(intro_message)

def display_chat_history(subject: str):
    """Exibe histórico do chat"""
    
    for message in st.session_state.chat_history[subject]:
        with st.container():
            if message["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right; margin: 1rem 0;">
                    <div style="background-color: #09278d; color: white; padding: 1rem; border-radius: 15px; display: inline-block; max-width: 70%;">
                        <strong>Sther:</strong> {message['content']}
                        <br><small>{message['timestamp']}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: left; margin: 1rem 0;">
                    <div class="arithmatex" style="background-color: #f1f5f9; color: #1e293b; padding: 1rem; border-radius: 15px; border-left: 4px solid #09278d; max-width: 80%;">
                        <strong style="color: #1e293b;">{SUBJECTS[subject]['teacher']}:</strong><br><span style="color: #1e293b;">{message['content']}</span>
                        <br><small style="color: #64748b;">{message['timestamp']}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)


def main():
    # Configuração MathJax para renderização de fórmulas matemáticas
    st.markdown("""
    <script>
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true
      },
      options: {
        ignoreHtmlClass: ".*|",
        processHtmlClass: "arithmatex"
      }
    };
    </script>
    <script async src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #09278d; font-size: 3rem; margin-bottom: 0;">🎓 ENEM AI Helper</h1>
        <h2 style="color: #1e3a8a; margin-top: 0;">Professores Particulares para Sther</h2>
        <p style="color: #64748b; font-size: 1.2rem;">Sistema inteligente com especialistas em cada matéria do ENEM</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Selecione a Matéria")
        
        # Seletor de matéria
        current_subject = st.selectbox(
            "Escolha sua matéria:",
            options=list(SUBJECTS.keys()),
            index=list(SUBJECTS.keys()).index(st.session_state.current_subject),
            format_func=lambda x: f"{SUBJECTS[x]['icon']} {x}"
        )
        
        # Atualiza matéria atual
        if current_subject != st.session_state.current_subject:
            st.session_state.current_subject = current_subject
            # Reset das flags ao mudar de matéria
            st.session_state.processing_message = False
            st.rerun()
        
        # Informações do professor atual
        subject_info = SUBJECTS[current_subject]
        st.markdown(f"""
        <div class="teacher-intro">
            <h3>{subject_info['icon']} {subject_info['teacher']}</h3>
            <p>{subject_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuração da API Key
        st.markdown("### 🔑 Configuração")
        api_key = st.text_input(
            "API Key Groq:",
            type="password",
            value=st.session_state.api_key,
            placeholder="Cole sua API Key aqui",
            help="Obtenha em: https://console.groq.com"
        )
        st.session_state.api_key = api_key
        
        if api_key:
            st.success("✅ API Key configurada!")
        else:
            st.warning("⚠️ Configure sua API Key para usar os professores")
        
        # Configuração específica para Matemática
        if current_subject == "Matemática" and PROFESSOR_CARLOS_LOCAL_AVAILABLE:
            setup_professor_carlos_local_ui()
        
        # Estatísticas
        st.markdown("### 📊 Seu Progresso")
        progress_value = min(len(st.session_state.chat_history[current_subject]) * 10, 100)
        st.progress(progress_value / 100)
        st.caption(f"Mensagens trocadas: {len(st.session_state.chat_history[current_subject])}")
        
        # Limpar chat
        if st.button("🗑️ Limpar Chat", key="clear_chat"):
            st.session_state.chat_history[current_subject] = []
            st.rerun()

    # Área principal
    # Para Matemática (Professor Carlos), criar abas Chat e Mapa Mental apenas
    if current_subject == "Matemática" and PROFESSOR_CARLOS_LOCAL_AVAILABLE:
        tab_chat, tab_mindmap = st.tabs(["💬 Chat", "🧠 Mapa Mental"])
        
        with tab_chat:
            # Adiciona introdução do professor se necessário
            add_teacher_intro(current_subject)
            
            # Exibe histórico do chat
            display_chat_history(current_subject)
        
        with tab_mindmap:
            # Aba do mapa mental com streamlit-markmap
            try:
                from mapa_mental_markmap import display_mapa_mental_wrapper
                display_mapa_mental_wrapper()
            except ImportError:
                st.error("Sistema de mapa mental não disponível. Execute: pip install streamlit-markmap==1.0.1")
    
    # else:
    #     # Para outras matérias, criar abas Chat e Exercícios
    #     tab_chat, tab_exercises = st.tabs(["💬 Chat", "📝 Exercícios"])
        
    #     with tab_chat:
    #         # Adiciona introdução do professor se necessário
    #         add_teacher_intro(current_subject)
            
    #         # Exibe histórico do chat
    #         display_chat_history(current_subject)
        
    #     with tab_exercises:
    #         # Aba de exercícios do ENEM
    #         display_exercises_tab(current_subject)
    
    # Input do usuário
    with st.container():
        # Função para processar mensagem quando Enter for pressionado
        def process_message():
            if st.session_state.get(f"user_input_{current_subject}", "").strip():
                if f"last_message_{current_subject}" not in st.session_state:
                    st.session_state[f"last_message_{current_subject}"] = ""
                
                current_message = st.session_state[f"user_input_{current_subject}"].strip()
                
                # Evita processar a mesma mensagem duas vezes
                if current_message != st.session_state[f"last_message_{current_subject}"]:
                    # Salva a mensagem para processamento
                    st.session_state[f"pending_message_{current_subject}"] = current_message
                    st.session_state[f"send_message_{current_subject}"] = True
                    st.session_state[f"last_message_{current_subject}"] = current_message
                    # Limpa a caixa de texto imediatamente
                    st.session_state[f"user_input_{current_subject}"] = ""
        
        user_input = st.text_input(
            "Digite sua pergunta:",
            placeholder=f"Pergunte algo sobre {current_subject} para {SUBJECTS[current_subject]['teacher']}...",
            key=f"user_input_{current_subject}",
            on_change=process_message
        )
        
        col1, col2 = st.columns([8, 2])
        with col1:
            st.empty()  # Espaço
        with col2:
            send_button = st.button("📤 Enviar", key="send_button", use_container_width=True)
    
    # Processa mensagem do usuário quando botão é clicado OU Enter é pressionado
    send_via_button = send_button and user_input.strip()
    send_via_enter = st.session_state.get(f"send_message_{current_subject}", False)
    should_send = send_via_button or send_via_enter
    
    # Determina qual mensagem processar
    message_to_process = ""
    if send_via_button:
        message_to_process = user_input.strip()
    elif send_via_enter:
        message_to_process = st.session_state.get(f"pending_message_{current_subject}", "")
    
    if should_send and message_to_process:
        # Verifica se não está processando e se não é a mesma mensagem
        if not st.session_state.processing_message:
            # Marca como processando
            st.session_state.processing_message = True
            
            # Se foi enviado via botão, limpa a caixa de texto
            if send_via_button:
                st.session_state[f"user_input_{current_subject}"] = ""
            
            # Adiciona mensagem do usuário
            user_message = {
                "role": "user",
                "content": message_to_process,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            st.session_state.chat_history[current_subject].append(user_message)
            
            # Gera resposta do professor
            with st.spinner(f"{SUBJECTS[current_subject]['teacher']} está pensando..."):
                assistant_response = get_teacher_response(current_subject, message_to_process, api_key)
            
            # Adiciona resposta do assistente
            assistant_message = {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            st.session_state.chat_history[current_subject].append(assistant_message)
            
            # Exercícios agora são gerados automaticamente pelo Professor Carlos
            # quando detecta que a Sther está pedindo exercícios
            pass
            
            # Marca como não processando mais
            st.session_state.processing_message = False
            
            # Reset da flag de envio
            if f"send_message_{current_subject}" in st.session_state:
                st.session_state[f"send_message_{current_subject}"] = False
            
            # Limpa mensagem pendente
            if f"pending_message_{current_subject}" in st.session_state:
                del st.session_state[f"pending_message_{current_subject}"]
            
            # Atualiza página
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 1rem;">
        <p>🎓 <strong>ENEM AI Helper</strong> - Sistema personalizado para a Sther</p>
        <p>Powered by DeepSeek R1 Distill via Groq • Matemática com sistema RAG local</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 