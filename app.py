import streamlit as st
import time
import re
import os
from typing import Dict, List, Any
from datetime import datetime
from groq import Groq
from local_redacao_rag import setup_redacao_ui, analyze_redacao_pdf
from local_portuguese_rag import local_portuguese_rag, LocalPortugueseRAG
from professor_leticia_local import setup_professor_leticia_local_ui, get_professor_leticia_local_response

# Sistema de configuração adaptativo para cloud e local
try:
    from cloud_config import get_config
    cloud_config = get_config()
    print(f"✅ Configuração carregada - Ambiente: {'Cloud' if cloud_config.is_cloud else 'Local'}")
except ImportError:
    print("⚠️ cloud_config não encontrado")
    cloud_config = None

# Carrega variáveis de ambiente do arquivo .env (apenas local)
if not (cloud_config and cloud_config.is_cloud):
    try:
        from dotenv import load_dotenv
        load_dotenv(encoding='utf-8')
        print("✅ Variáveis de ambiente carregadas do arquivo .env")
    except ImportError:
        print("⚠️ python-dotenv não encontrado. Instale com: pip install python-dotenv")
    except Exception as e:
        print(f"⚠️ Erro ao carregar .env: {e}")

# Configura encoding seguro
try:
    from encoding_utils import setup_encoding
    setup_encoding()
except ImportError:
    pass

# Carrega a chave da API Groq a partir das variáveis de ambiente
# No Streamlit Cloud, defina em "Settings" > "Secrets"
# Localmente, pode estar em um arquivo .env
api_key = os.environ.get("GROQ_API_KEY")

# Configuração da página - DEVE SER A PRIMEIRA CHAMADA STREAMLIT
st.set_page_config(
    page_title="ENEM AI Helper - Professores Particulares para Sther",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importação lazy dos sistemas RAG - carrega apenas quando necessário
PROFESSOR_CARLOS_LOCAL_AVAILABLE = False
PROFESSOR_LUCIANA_LOCAL_AVAILABLE = False  
PROFESSOR_ROBERTO_LOCAL_AVAILABLE = False
PROFESSOR_EDUARDO_LOCAL_AVAILABLE = False
PROFESSOR_MARINA_LOCAL_AVAILABLE = False
PROFESSOR_FERNANDO_LOCAL_AVAILABLE = False
PORTUGUESE_RAG_AVAILABLE = False
ENEM_EXERCISES_AVAILABLE = False
EXERCICIOS_PERSONALIZADOS_AVAILABLE = False
REDACAO_AVAILABLE = False

# Cache para módulos importados
_imported_modules = {}

def lazy_import_professor(subject: str):
    """Importa professor sob demanda para economizar memória"""
    global PROFESSOR_CARLOS_LOCAL_AVAILABLE, PROFESSOR_LUCIANA_LOCAL_AVAILABLE
    global PROFESSOR_ROBERTO_LOCAL_AVAILABLE, PROFESSOR_EDUARDO_LOCAL_AVAILABLE
    global PROFESSOR_MARINA_LOCAL_AVAILABLE, PROFESSOR_FERNANDO_LOCAL_AVAILABLE
    global PORTUGUESE_RAG_AVAILABLE, REDACAO_AVAILABLE
    
    if subject == "Matemática" and "carlos" not in _imported_modules:
        try:
            from professor_carlos_local import setup_professor_carlos_local_ui, get_professor_carlos_local_response
            _imported_modules["carlos"] = {
                "setup": setup_professor_carlos_local_ui,
                "response": get_professor_carlos_local_response
            }
            PROFESSOR_CARLOS_LOCAL_AVAILABLE = True
        except ImportError:
            pass

    elif subject == "Química" and "luciana" not in _imported_modules:
        try:
            from professor_luciana_local import setup_professor_luciana_local_ui, get_professor_luciana_local_response
            _imported_modules["luciana"] = {
                "setup": setup_professor_luciana_local_ui,
                "response": get_professor_luciana_local_response
            }
            PROFESSOR_LUCIANA_LOCAL_AVAILABLE = True
        except ImportError:
            pass

    elif subject == "Biologia" and "roberto" not in _imported_modules:
        try:
            from professor_roberto_local import setup_professor_roberto_local_ui, get_professor_roberto_local_response
            _imported_modules["roberto"] = {
                "setup": setup_professor_roberto_local_ui,
                "response": get_professor_roberto_local_response
            }
            PROFESSOR_ROBERTO_LOCAL_AVAILABLE = True
        except ImportError:
            pass

    elif subject == "História" and "eduardo" not in _imported_modules:
        try:
            from professor_eduardo_local import setup_professor_eduardo_local_ui, get_professor_eduardo_local_response
            _imported_modules["eduardo"] = {
                "setup": setup_professor_eduardo_local_ui,
                "response": get_professor_eduardo_local_response
            }
            PROFESSOR_EDUARDO_LOCAL_AVAILABLE = True
        except ImportError:
            pass

    elif subject == "Geografia" and "marina" not in _imported_modules:
        try:
            from professor_marina_local import setup_professor_marina_local_ui, get_professor_marina_local_response
            _imported_modules["marina"] = {
                "setup": setup_professor_marina_local_ui,
                "response": get_professor_marina_local_response
            }
            PROFESSOR_MARINA_LOCAL_AVAILABLE = True
        except ImportError:
            pass

    elif subject == "Física" and "fernando" not in _imported_modules:
        try:
            from professor_fernando_local import setup_professor_fernando_local_ui, get_professor_fernando_local_response
            _imported_modules["fernando"] = {
                "setup": setup_professor_fernando_local_ui,
                "response": get_professor_fernando_local_response
            }
            PROFESSOR_FERNANDO_LOCAL_AVAILABLE = True
        except ImportError:
            pass
    
    elif subject == "Língua Portuguesa" and "leticia" not in _imported_modules:
        try:
            from professor_leticia_local import setup_professor_leticia_local_ui, get_professor_leticia_local_response, PORTUGUESE_RAG_AVAILABLE as PORTUGUESE_AVAILABLE
            _imported_modules["leticia"] = {
                "setup": setup_professor_leticia_local_ui,
                "response": get_professor_leticia_local_response
            }
            PORTUGUESE_RAG_AVAILABLE = PORTUGUESE_AVAILABLE
        except ImportError:
            pass
    
    elif subject == "Redação" and "redacao" not in _imported_modules:
        try:
            from local_redacao_rag import setup_redacao_ui, analyze_redacao_pdf
            _imported_modules["redacao"] = {
                "setup": setup_redacao_ui,
                "analyze": analyze_redacao_pdf
            }
            REDACAO_AVAILABLE = True
        except ImportError:
            pass

def lazy_import_exercises():
    """Importa sistema de exercícios sob demanda"""
    global EXERCICIOS_PERSONALIZADOS_AVAILABLE
    
    if "exercicios" not in _imported_modules:
        try:
            from exercicios_personalizados import exercicios_personalizados
            _imported_modules["exercicios"] = exercicios_personalizados
            EXERCICIOS_PERSONALIZADOS_AVAILABLE = True
        except ImportError:
            pass

def lazy_import_mindmap():
    """Importa mapa mental sob demanda"""
    if "mindmap" not in _imported_modules:
        try:
            from mapa_mental_markmap import display_mapa_mental_wrapper
            _imported_modules["mindmap"] = display_mapa_mental_wrapper
        except ImportError:
            pass

# Configuração MathJax para renderização de fórmulas matemáticas
st.markdown("""
<script>
  window.MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']]
    },
    options: {
      ignoreHtmlClass: 'nostem|nolatexmath',
      processHtmlClass: 'stemblock|latexmath',
      processEscapes: true,
      processEnvironments: true,
      processRefs: true
    }
  };
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
""", unsafe_allow_html=True)

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
        "description": "Especialista em matemática do ENEM com sistema RAG local e formatação matemática aprimorada",
        "intro": "Olá, Futura Senhora Sther Souza! Sou o Professor Carlos, seu professor particular de Matemática! Agora tenho formatação matemática melhorada com LaTeX, respostas mais claras e sem duplicações. Vamos dominar a matemática do ENEM juntos! 🚀"
    },
    "Português": {
        "teacher": "Profa. Ana",
        "icon": "📚",
        "description": "Literatura, gramática e interpretação de texto",
        "intro": "Olá, Futura Dra. Sther! Sou a Professora Ana, especialista em Português para o ENEM. Vou te ajudar com gramática, literatura e redação!"
    },
    "Biologia": {
        "teacher": "Prof. Roberto",
        "icon": "🧬",
        "description": "Especialista em biologia do ENEM com sistema RAG local e analogias das suas séries favoritas",
        "intro": "E aí, Futura Psicóloga Sther! Sou o Professor Roberto de Biologia! Tenho acesso direto aos seus materiais de biologia e vou usar analogias das suas séries favoritas para te ensinar. Vamos desvendar os mistérios da vida juntos! 🧬🔬"
    },
    "Geografia": {
        "teacher": "Profa. Marina",
        "icon": "🌍",
        "description": "Geografia física, humana e geopolítica",
        "intro": "Fala, Futura Psicóloga Sther Souza! Sou a Professora Marina de Geografia. Vamos explorar o mundo e suas transformações!"
    },
    "História": {
        "teacher": "Prof. Eduardo",
        "icon": "🏛️",
        "description": "Especialista em história do ENEM com sistema RAG local e analogias das suas séries favoritas",
        "intro": "Eai, Sther! Sou o Professor Eduardo de História! Tenho acesso direto aos seus materiais de história e vou usar analogias das suas séries favoritas para te ensinar. Vamos viajar no tempo e entender nosso passado juntos! 🏛️📚"
    },
    "Química": {
        "teacher": "Profa. Luciana",
        "icon": "⚗️",
        "description": "Química orgânica, inorgânica e físico-química",
        "intro": "Oi, Lindíssima Sther! Sou a Professora Luciana de Química. Vamos misturar conhecimento e descobrir reações incríveis!"
    },
    "Física": {
        "teacher": "Prof. Fernando",
        "icon": "🧪",
        "description": "Especialista em física do ENEM com sistema RAG local e analogias das suas séries favoritas",
        "intro": "E aí, Minha futura psicóloga Sther! Sou o Professor Fernando de Física! Tenho acesso direto aos seus materiais de física e vou usar analogias das suas séries favoritas para te ensinar. Vamos desvendar os mistérios do universo juntos! 🧪⚡"
    },
    "Redação": {
        "teacher": "Profa. Carla",
        "icon": "✍️",
        "description": "Técnicas de redação e dissertação argumentativa",
        "intro": "Olá, Sther (futura) Souza! Sou a Professora Carla de Redação. Vamos transformar suas ideias em textos nota 1000!"
    },
    "Língua Portuguesa": {
        "teacher": "Professora Letícia",
        "icon": "👩‍🏫",
        "description": "Gramática, literatura e interpretação de texto",
        "intro": "Oi, Princesa Sther! Sou a Professora Letícia. Vamos desvendar os segredos da língua portuguesa e da literatura!"
    },
}

# Carrega chave da API automaticamente do arquivo .env
# Obtém chave de API de forma adaptativa
if cloud_config:
    AUTO_API_KEY = cloud_config.get_api_key('GROQ_API_KEY') or ''
else:
    AUTO_API_KEY = os.getenv('GROQ_API_KEY', '')

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

# Se há API key no .env, sempre usa ela (prioridade máxima)
if AUTO_API_KEY:
    st.session_state.api_key = AUTO_API_KEY

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
                model="llama-3.3-70b-versatile",
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
    if subject == "Matemática" and "carlos" in _imported_modules:
        return _imported_modules["carlos"]["response"](user_message, api_key)
    
    # Professora Luciana especializada (RAG Local de Química)
    elif subject == "Química" and "luciana" in _imported_modules:
        return _imported_modules["luciana"]["response"](user_message, api_key)
    
    # Professor Roberto especializado (RAG Local de Biologia)
    elif subject == "Biologia" and "roberto" in _imported_modules:
        return _imported_modules["roberto"]["response"](user_message, api_key)
    
    # Professor Eduardo especializado (RAG Local de História)
    elif subject == "História" and "eduardo" in _imported_modules:
        return _imported_modules["eduardo"]["response"](user_message, api_key)
    
    # Professora Marina especializada (RAG Local de Geografia)
    elif subject == "Geografia" and "marina" in _imported_modules:
        return _imported_modules["marina"]["response"](user_message, api_key)
    
    # Professora Letícia (RAG Local de Português)
    elif subject == "Língua Portuguesa" and "leticia" in _imported_modules:
        return _imported_modules["leticia"]["response"](user_message, api_key)
    
    # Professor Fernando especializado (RAG Local de Física)
    elif subject == "Física" and "fernando" in _imported_modules:
        return _imported_modules["fernando"]["response"](user_message, api_key)
    
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

def cleanup_unused_modules(current_subject: str):
    """Remove módulos não utilizados da memória para economizar recursos"""
    subject_module_map = {
        "Matemática": "carlos",
        "Química": "luciana", 
        "Biologia": "roberto",
        "História": "eduardo",
        "Geografia": "marina",
        "Física": "fernando",
        "Língua Portuguesa": "leticia",
        "Redação": "redacao"
    }
    
    current_module = subject_module_map.get(current_subject)
    modules_to_remove = []
    
    for module_key in _imported_modules.keys():
        if module_key != current_module and module_key not in ["mindmap", "exercicios"]:
            modules_to_remove.append(module_key)
    
    for module_key in modules_to_remove:
        del _imported_modules[module_key]
        
    # Reset das variáveis globais para módulos removidos
    global PROFESSOR_CARLOS_LOCAL_AVAILABLE, PROFESSOR_LUCIANA_LOCAL_AVAILABLE
    global PROFESSOR_ROBERTO_LOCAL_AVAILABLE, PROFESSOR_EDUARDO_LOCAL_AVAILABLE  
    global PROFESSOR_MARINA_LOCAL_AVAILABLE, PROFESSOR_FERNANDO_LOCAL_AVAILABLE
    global PORTUGUESE_RAG_AVAILABLE, REDACAO_AVAILABLE
    
    if "carlos" not in _imported_modules:
        PROFESSOR_CARLOS_LOCAL_AVAILABLE = False
    if "luciana" not in _imported_modules:
        PROFESSOR_LUCIANA_LOCAL_AVAILABLE = False
    if "roberto" not in _imported_modules:
        PROFESSOR_ROBERTO_LOCAL_AVAILABLE = False
    if "eduardo" not in _imported_modules:
        PROFESSOR_EDUARDO_LOCAL_AVAILABLE = False
    if "marina" not in _imported_modules:
        PROFESSOR_MARINA_LOCAL_AVAILABLE = False
    if "fernando" not in _imported_modules:
        PROFESSOR_FERNANDO_LOCAL_AVAILABLE = False
    if "leticia" not in _imported_modules:
        PORTUGUESE_RAG_AVAILABLE = False
    if "redacao" not in _imported_modules:
        REDACAO_AVAILABLE = False

def main():
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
        
        # Atualiza matéria atual e carrega professor sob demanda
        if current_subject != st.session_state.current_subject:
            st.session_state.current_subject = current_subject
            # Reset das flags ao mudar de matéria
            st.session_state.processing_message = False
            # Limpa módulos não utilizados para economizar memória
            cleanup_unused_modules(current_subject)
            # Carrega professor da matéria selecionada
            lazy_import_professor(current_subject)
            st.rerun()
        else:
            # Carrega professor da matéria atual se ainda não foi carregado
            lazy_import_professor(current_subject)
        
        # Informações do professor atual
        subject_info = SUBJECTS[current_subject]
        st.markdown(f"""
        <div class="teacher-intro">
            <h3>{subject_info['icon']} {subject_info['teacher']}</h3>
            <p>{subject_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuração da API Key
        if not api_key:
            st.error("A chave GROQ_API_KEY não foi encontrada.")
            st.warning("Por favor, configure a chave API nas secrets do Streamlit Cloud ou em um arquivo .env local.")
            if cloud_config and cloud_config.is_cloud:
                st.info("💡 **Dica:** Configure `GROQ_API_KEY` nas secrets do Streamlit Cloud.")
            else:
                st.info("💡 **Dica:** Crie um arquivo `.env` com `GROQ_API_KEY=sua_chave` para configuração automática.")
            st.stop()
        else:
            st.success("🔐 API Key carregada com sucesso!")
        
        # Configuração específica para cada matéria (apenas se carregada)
        if current_subject == "Matemática" and "carlos" in _imported_modules:
            _imported_modules["carlos"]["setup"]()
        elif current_subject == "Química" and "luciana" in _imported_modules:
            _imported_modules["luciana"]["setup"]()
        elif current_subject == "Biologia" and "roberto" in _imported_modules:
            _imported_modules["roberto"]["setup"]()
        elif current_subject == "História" and "eduardo" in _imported_modules:
            _imported_modules["eduardo"]["setup"]()
        elif current_subject == "Geografia" and "marina" in _imported_modules:
            _imported_modules["marina"]["setup"]()
        elif current_subject == "Língua Portuguesa" and "leticia" in _imported_modules:
            _imported_modules["leticia"]["setup"]()
        elif current_subject == "Física" and "fernando" in _imported_modules:
            _imported_modules["fernando"]["setup"]()
        
        # Estatísticas
        st.markdown("### 📊 Seu Progresso")
        progress_value = min(len(st.session_state.chat_history[current_subject]) * 10, 100)
        st.progress(progress_value / 100)
        st.caption(f"Mensagens trocadas: {len(st.session_state.chat_history[current_subject])}")
        
        # Limpar chat
        if st.button("🗑️ Limpar Chat", key="clear_chat"):
            st.session_state.chat_history[current_subject] = []
            st.rerun()

    # --- Área Principal com Abas Condicionais ---
    
    # Lógica para Redação
    if current_subject == "Redação":
        tab_chat, tab_mindmap, tab_revisao = st.tabs([
            "💬 Chat", 
            "🧠 Mapa Mental", 
            "📝 Revisão de Redação"
        ])
        
        with tab_chat:
            add_teacher_intro(current_subject)
            display_chat_history(current_subject)
        
        with tab_mindmap:
            # Lógica do mapa mental
            lazy_import_mindmap()
            if "mindmap" in _imported_modules:
                _imported_modules["mindmap"]()
            else:
                st.error("O sistema de mapa mental não está disponível.")

        with tab_revisao:
            # Lógica da revisão de redação
            if "redacao" in _imported_modules:
                _imported_modules["redacao"]["setup"]()
            else:
                st.warning("⚠️ O módulo de revisão de redação não está disponível.")

    # Lógica para todas as outras matérias
    else:
        tab_chat, tab_mindmap, tab_exercicios = st.tabs([
            "💬 Chat", 
            "🧠 Mapa Mental", 
            "📚 Exercícios Personalizados"
        ])
        
        with tab_chat:
            add_teacher_intro(current_subject)
            display_chat_history(current_subject)
        
        with tab_mindmap:
            # Lógica do mapa mental
            lazy_import_mindmap()
            if "mindmap" in _imported_modules:
                _imported_modules["mindmap"]()
            else:
                st.error("O sistema de mapa mental não está disponível.")
        
        with tab_exercicios:
            # Lógica dos exercícios personalizados
            lazy_import_exercises()
            if "exercicios" in _imported_modules:
                _imported_modules["exercicios"].setup_ui()
            else:
                st.warning("⚠️ O módulo de exercícios personalizados não está disponível.")
    
    # Input do usuário
    with st.container():
        # Usa form para permitir envio via Enter
        with st.form(key=f"message_form_{current_subject}", clear_on_submit=True):
            user_input = st.text_input(
                "Digite sua pergunta:",
                placeholder=f"Pergunte algo sobre {current_subject} para {SUBJECTS[current_subject]['teacher']}...",
                key=f"user_input_{current_subject}"
            )
            
            col1, col2 = st.columns([8, 2])
            with col1:
                st.empty()  # Espaço
            with col2:
                send_button = st.form_submit_button("📤 Enviar", use_container_width=True)
    
    # Processa mensagem do usuário quando botão é clicado OU Enter é pressionado
    if send_button and user_input and user_input.strip():
        message_to_process = user_input.strip()
        
        # Verifica se não está processando e se não é a mesma mensagem
        if not st.session_state.processing_message:
            # Evita processar a mesma mensagem duas vezes
            last_msg_key = f"last_message_{current_subject}"
            if last_msg_key not in st.session_state:
                st.session_state[last_msg_key] = ""
            
            if message_to_process != st.session_state[last_msg_key]:
                # Marca como processando
                st.session_state.processing_message = True
                st.session_state[last_msg_key] = message_to_process
                
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
                
                # Marca como não processando mais
                st.session_state.processing_message = False
                
                # Atualiza página para mostrar nova mensagem
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 1rem;">
        <p>🎓 <strong>ENEM AI Helper</strong> - Sistema personalizado para a Sther</p>
        <p>Powered by DeepSeek R1 Distill via Groq • Carregamento otimizado para economia de memória</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 