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

# Import for chat message types
try:
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError:
    # Fallback if langchain is not available
    class HumanMessage:
        def __init__(self, content):
            self.content = content
    
    class AIMessage:
        def __init__(self, content):
            self.content = content

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
        except ImportError as e:
            pass

    elif subject == "Química" and "luciana" not in _imported_modules:
        try:
            from professor_luciana_local import setup_professor_luciana_local_ui, get_professor_luciana_local_response
            _imported_modules["luciana"] = {
                "setup": setup_professor_luciana_local_ui,
                "response": get_professor_luciana_local_response
            }
            PROFESSOR_LUCIANA_LOCAL_AVAILABLE = True
        except ImportError as e:
            pass

    elif subject == "Biologia" and "roberto" not in _imported_modules:
        try:
            from professor_roberto_local import setup_professor_roberto_local_ui, get_professor_roberto_local_response
            _imported_modules["roberto"] = {
                "setup": setup_professor_roberto_local_ui,
                "response": get_professor_roberto_local_response
            }
            PROFESSOR_ROBERTO_LOCAL_AVAILABLE = True
        except ImportError as e:
            pass

    elif subject == "História" and "eduardo" not in _imported_modules:
        try:
            from professor_eduardo_local import setup_professor_eduardo_local_ui, get_professor_eduardo_local_response
            _imported_modules["eduardo"] = {
                "setup": setup_professor_eduardo_local_ui,
                "response": get_professor_eduardo_local_response
            }
            PROFESSOR_EDUARDO_LOCAL_AVAILABLE = True
        except ImportError as e:
            pass

    elif subject == "Geografia" and "marina" not in _imported_modules:
        try:
            from professor_marina_local import setup_professor_marina_local_ui, get_professor_marina_local_response
            _imported_modules["marina"] = {
                "setup": setup_professor_marina_local_ui,
                "response": get_professor_marina_local_response
            }
            PROFESSOR_MARINA_LOCAL_AVAILABLE = True
        except ImportError as e:
            pass

    elif subject == "Física" and "fernando" not in _imported_modules:
        try:
            from professor_fernando_local import setup_professor_fernando_local_ui, get_professor_fernando_local_response
            _imported_modules["fernando"] = {
                "setup": setup_professor_fernando_local_ui,
                "response": get_professor_fernando_local_response
            }
            PROFESSOR_FERNANDO_LOCAL_AVAILABLE = True
        except ImportError as e:
            pass
    
    elif subject == "Língua Portuguesa" and "leticia" not in _imported_modules:
        try:
            from professor_leticia_local import setup_professor_leticia_local_ui, get_professor_leticia_local_response, PORTUGUESE_RAG_AVAILABLE as PORTUGUESE_AVAILABLE
            _imported_modules["leticia"] = {
                "setup": setup_professor_leticia_local_ui,
                "response": get_professor_leticia_local_response
            }
            PORTUGUESE_RAG_AVAILABLE = PORTUGUESE_AVAILABLE
        except ImportError as e:
            pass
    
    elif subject == "Redação" and "redacao" not in _imported_modules:
        try:
            from local_redacao_rag import setup_redacao_ui, analyze_redacao_pdf
            _imported_modules["redacao"] = {
                "setup": setup_redacao_ui,
                "analyze": analyze_redacao_pdf
            }
            REDACAO_AVAILABLE = True
        except ImportError as e:
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
            # Importa a nova função contextual
            from mapa_mental_markmap import gerar_mapa_mental_contextual
            _imported_modules["mindmap"] = gerar_mapa_mental_contextual
        except ImportError:
            pass

# Configuração MathJax aprimorada para renderização de fórmulas matemáticas
st.markdown("""
<script type="text/javascript">
  window.MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true,
    processRefs: true,
    packages: {'[+]': ['base', 'ams', 'newcommand', 'configmacros', 'action']},
    macros: {
      det: '\\operatorname{det}',
      text: ['\\text{#1}', 1],
      frac: ['\\frac{#1}{#2}', 2],
      sqrt: ['\\sqrt{#1}', 1],
      sum: '\\sum',
      int: '\\int',
      lim: '\\lim',
      sin: '\\sin',
      cos: '\\cos',
      tan: '\\tan',
      log: '\\log',
      ln: '\\ln'
    }
  },
  svg: {
    fontCache: 'global'
    },
    options: {
      ignoreHtmlClass: 'nostem|nolatexmath',
    processHtmlClass: 'stemblock|latexmath|math',
    renderActions: {
      addMenu: [0, '', '']
    }
  },
  startup: {
    ready: function() {
      MathJax.startup.defaultReady();
      console.log('MathJax está pronto!');
    }
    }
  };
</script>
<script type="text/javascript" id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
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
        "avatar": "🧑‍🏫",
        "description": "Especialista em matemática do ENEM com sistema RAG local e formatação matemática aprimorada",
        "intro": "Olá, Futura Senhora Sther Souza! Sou o Professor Carlos, seu professor particular de Matemática! Agora tenho formatação matemática melhorada com LaTeX, respostas mais claras e sem duplicações. Vamos dominar a matemática do ENEM juntos! 🚀"
    },
    "Português": {
        "teacher": "Profa. Ana",
        "icon": "📚",
        "avatar": "👩‍🏫",
        "description": "Literatura, gramática e interpretação de texto",
        "intro": "Olá, Futura Dra. Sther! Sou a Professora Ana, especialista em Português para o ENEM. Vou te ajudar com gramática, literatura e redação!"
    },
    "Biologia": {
        "teacher": "Prof. Roberto",
        "icon": "🧬",
        "avatar": "🧑‍🔬",
        "description": "Especialista em biologia do ENEM com sistema RAG local e analogias das suas séries favoritas",
        "intro": "E aí, Futura Psicóloga Sther! Sou o Professor Roberto de Biologia! Tenho acesso direto aos seus materiais de biologia e vou usar analogias das suas séries favoritas para te ensinar. Vamos desvendar os mistérios da vida juntos! 🧬🔬"
    },
    "Geografia": {
        "teacher": "Profa. Marina",
        "icon": "🌍",
        "avatar": "👩‍🏫",
        "description": "Geografia física, humana e geopolítica",
        "intro": "Fala, Futura Psicóloga Sther Souza! Sou a Professora Marina de Geografia. Vamos explorar o mundo e suas transformações!"
    },
    "História": {
        "teacher": "Prof. Eduardo",
        "icon": "🏛️",
        "avatar": "🧑‍🏫",
        "description": "Especialista em história do ENEM com sistema RAG local e analogias das suas séries favoritas",
        "intro": "Eai, Sther! Sou o Professor Eduardo de História! Tenho acesso direto aos seus materiais de história e vou usar analogias das suas séries favoritas para te ensinar. Vamos viajar no tempo e entender nosso passado juntos! 🏛️📚"
    },
    "Química": {
        "teacher": "Profa. Luciana",
        "icon": "⚗️",
        "avatar": "👩‍🔬",
        "description": "Química orgânica, inorgânica e físico-química",
        "intro": "Oi, Lindíssima Sther! Sou a Professora Luciana de Química. Vamos misturar conhecimento e descobrir reações incríveis!"
    },
    "Física": {
        "teacher": "Prof. Fernando",
        "icon": "🧪",
        "avatar": "🧑‍🔬",
        "description": "Especialista em física do ENEM com sistema RAG local e analogias das suas séries favoritas",
        "intro": "E aí, Minha futura psicóloga Sther! Sou o Professor Fernando de Física! Tenho acesso direto aos seus materiais de física e vou usar analogias das suas séries favoritas para te ensinar. Vamos desvendar os mistérios do universo juntos! 🧪⚡"
    },
    "Redação": {
        "teacher": "Profa. Carla",
        "icon": "✍️",
        "avatar": "👩‍🏫",
        "description": "Técnicas de redação e dissertação argumentativa",
        "intro": "Olá, Sther (futura) Souza! Sou a Professora Carla de Redação. Vamos transformar suas ideias em textos nota 1000!"
    },
    "Língua Portuguesa": {
        "teacher": "Professora Letícia",
        "icon": "👩‍🏫",
        "avatar": "👩‍🏫",
        "description": "Gramática, literatura e interpretação de texto",
        "intro": "Oi, Princesa Sther! Sou a Professora Letícia. Vamos desvendar os segredos da língua portuguesa e da literatura!"
    },
    "Boas-vindas": {
        "teacher": "Assistente IA",
        "icon": "👋",
        "avatar": "🤖",
        "description": "Sua assistente para o ENEM",
        "intro": "Olá, Sther! Bem-vinda ao ENEM AI Helper. Escolha uma matéria na barra lateral para começar a estudar!"
    }
}

def handle_api_error(error_message: str):
    """Detecta erros de API key sem usar cache"""
    error_str = str(error_message).lower()
    
    # Detecta se é um erro de API key inválida
    if any(term in error_str for term in ['invalid api key', 'error code: 401', 'unauthorized', 'invalid_api_key']):
        st.warning("🔧 **API Key invalidada detectada**")
        st.info("🔄 **Por favor, gere uma nova API key no Groq Console e atualize as configurações.**")
        return True
    
    return False

def get_api_key():
    """Carrega a chave da API do Streamlit secrets ou variáveis de ambiente - VERSÃO LIMPA SEM CACHE"""
    
    # Primeiro tenta Streamlit Secrets (para Cloud)
    try:
        if hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
            if api_key and isinstance(api_key, str) and api_key.strip() and len(api_key.strip()) > 10:
                return api_key.strip()
    except:
        pass
    
    # Fallback para variáveis de ambiente (para local)
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key and isinstance(api_key, str) and api_key.strip() and len(api_key.strip()) > 10:
            return api_key.strip()
    except:
        pass
    
    return None

# Inicialização do session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {subject: [] for subject in SUBJECTS.keys()}
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = "Boas-vindas"
if 'processing_message' not in st.session_state:
    st.session_state.processing_message = False
if 'generated_exercises' not in st.session_state:
    st.session_state.generated_exercises = {subject: [] for subject in SUBJECTS.keys()}
if 'last_user_question' not in st.session_state:
    st.session_state.last_user_question = {subject: "" for subject in SUBJECTS.keys()}

# Adiciona diagnóstico de API key se necessário
if 'show_api_diagnostic' not in st.session_state:
    st.session_state.show_api_diagnostic = False

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
        
        # Validação robusta da API key
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            return f"""
🔑 **Configure sua API Key da Groq**

Para ativar {self.name}, você precisa:
1. Obter uma API Key da Groq (https://console.groq.com)
2. Inserir a chave na barra lateral
3. Começar a conversar!

💡 {self.name} está pronto para te ajudar com {self.subject}!
"""
        
        # Limpa a API key para garantir que não há espaços ou caracteres extras
        clean_api_key = api_key.strip()
        
        try:
            # Cria uma nova instância do cliente a cada chamada para evitar cache corrompido
            client = Groq(api_key=clean_api_key)
            
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

## 📐 FORMATAÇÃO DE FÓRMULAS (SE APLICÁVEL):
- Se precisar escrever uma fórmula matemática, use os delimitadores do LaTeX.
- **Fórmula inline**: $ f(x) = ax^2 + bx + c $
- **Fórmula em destaque**: $$ x = \\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}} $$
- NUNCA use colchetes `[ ]` para fórmulas.

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

1. 👋 "Olá Sther! Como vai sua caminhada até a psicologia? Espero te ajudar nessa jornada tão especial e importante hoje!" 
2. 🎬 Inicie SEMPRE com uma analogia das séries favoritas da Sther
3. 📚 Responda a pergunta conectando com a analogia. Explique tópico por tópico, deixando uma explicação clara e o mais completa que pude. (lembre-se SEMPRE das suas diretrizes de comportamento)
4. 📝 Quando aplicável, use exemplos que reforcem a analogia
5. 🎯 Conecte de volta com as séries
6. ❓ Pergunta obrigatória sobre exercícios

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
                temperature=0.1,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Log do erro sem expor a API key
            error_msg = str(e)
            
            return f"""
❌ **Erro na comunicação**

Detalhes: {error_msg}

💡 Verifique sua API Key e conexão com a internet.
"""

def get_teacher_response(subject: str, user_message: str, api_key: str) -> str:
    """Retorna resposta do professor específico com melhor tratamento de erro"""
    
    # Validação inicial da API key
    if not api_key or not isinstance(api_key, str) or not api_key.strip():
        return """
❌ **API Key inválida ou não fornecida**

Por favor, configure sua API Key corretamente nas configurações do Streamlit Cloud.
"""
    
    try:
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
            
    except Exception as e:
        # Resposta de fallback em caso de erro
        error_response = f"""
❌ **Erro no Sistema do Professor**

Ocorreu um erro ao processar sua mensagem:
```
{str(e)}
```

💡 **Tente:**
1. Reformular sua pergunta
2. Verificar se a matéria está funcionando
3. Tentar uma pergunta mais simples

🔄 **Modo de emergência**: Vou tentar responder de forma básica...

---

Olá, Sther! Desculpe, tive um problema técnico, mas estou aqui para te ajudar com {subject}. 

Pode reformular sua pergunta? Vou fazer o meu melhor para responder sobre o tópico que você perguntou: "{user_message}"

💪 Não desista! Estamos aqui para te ajudar a conquistar o ENEM!
"""
        return error_response

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
    
    # Não remover o módulo do mapa mental ou dos exercícios
    modules_to_keep = ["mindmap", "exercicios"]
    if current_subject in subject_module_map:
        modules_to_keep.append(subject_module_map[current_subject])
        
    for module_key in list(_imported_modules.keys()):
        if module_key not in modules_to_keep:
            del _imported_modules[module_key]
            # gc.collect() # Opcional: forçar coleta de lixo

def render_math_content(content: str) -> None:
    """
    Renderiza conteúdo com fórmulas matemáticas usando MathJax.
    O processamento agora é feito diretamente pelo LLM, que foi instruído
    a gerar LaTeX corretamente.
    """
    # A função de processamento `process_mathematical_formulas_new` foi removida 
    # pois estava causando erros de formatação.
    
    # Usa st.markdown com unsafe_allow_html=True para permitir MathJax
    st.markdown(content, unsafe_allow_html=True)
    
    # Força re-renderização do MathJax
    st.markdown("""
    <script>
    if (window.MathJax) {
        MathJax.typesetPromise();
    }
    </script>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #09278d; font-size: 3rem; margin-bottom: 0;">🎓 ENEM AI Helper</h1>
        <h2 style="color: #1e3a8a; margin-top: 0;">Professores Particulares para Sther</h2>
        <p style="color: #64748b; font-size: 1.2rem;">Sistema inteligente com especialistas em cada matéria do ENEM</p>
    </div>
    """, unsafe_allow_html=True)

    # Validação da API Key
    api_key = get_api_key()

    if not api_key:
        st.warning("🔑 **API Key não configurada!**")
        st.info("""
            Para usar o ENEM AI Helper, você precisa configurar sua API Key da Groq.
            
            **Se você estiver executando no Streamlit Cloud:**
            1. Crie um arquivo `secrets.toml` na pasta `.streamlit`.
            2. Adicione sua chave da seguinte forma:
               ```toml
               GROQ_API_KEY = "sua_chave_aqui"
               ```
            
            **Se você estiver executando localmente:**
            1. Crie um arquivo chamado `.env` na pasta principal do projeto.
            2. Adicione sua chave da seguinte forma:
               ```
               GROQ_API_KEY="sua_chave_aqui"
               ```

            Após configurar a chave, reinicie a aplicação.
        """)
        st.stop()

    # Inicializa estado da sessão
    if "current_subject" not in st.session_state:
        st.session_state.current_subject = "Boas-vindas"
    
    # Adiciona a chave de Boas-vindas se não existir
    if "Boas-vindas" not in SUBJECTS:
        SUBJECTS["Boas-vindas"] = {
            "teacher": "Assistente IA", "icon": "👋", "avatar": "🤖", 
            "description": "Sua assistente para o ENEM", 
            "intro": "Olá, Sther! Bem-vinda ao ENEM AI Helper. Escolha uma matéria para começar."
        }
        
    # Inicializa o histórico de chat para todas as matérias, incluindo Boas-vindas
    for subject in SUBJECTS.keys():
        if f"chat_history_{subject}" not in st.session_state:
            st.session_state[f"chat_history_{subject}"] = []

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
        
        if current_subject != st.session_state.current_subject:
            st.session_state.current_subject = current_subject
            cleanup_unused_modules(current_subject)
            lazy_import_professor(current_subject)
            st.rerun()
        else:
            lazy_import_professor(current_subject)
        
        # Garante que subject_info sempre tenha um valor padrão
        subject_info = SUBJECTS.get(current_subject, SUBJECTS["Boas-vindas"])
        
        st.markdown(f"""
        <div class="teacher-intro">
            <h3>{subject_info['icon']} {subject_info['teacher']}</h3>
            <p>{subject_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Painel de Status da Base de Conhecimento (apenas para Matemática)
        if current_subject == "Matemática" and "carlos" in _imported_modules:
            with st.expander("🔎 Status da Base de Conhecimento", expanded=True):
                try:
                    # Importa o singleton diretamente para pegar os stats
                    from local_math_rag import local_math_rag
                    stats = local_math_rag.get_stats()
                    
                    status_icon = "✅" if stats.get("status") == "Carregado" else "❌"
                    st.markdown(f"**Status:** {status_icon} {stats.get('status', 'N/A')}")
                    st.markdown(f"**Documentos Indexados:** {stats.get('total_documents', 'N/A')}")

                    sample_docs = stats.get("sample_documents", [])
                    if sample_docs:
                        st.markdown("**Amostra de Documentos na Base:**")
                        for doc_name in sample_docs:
                            st.markdown(f"- `{doc_name}`")
                except Exception as e:
                    st.error(f"Erro ao obter status: {e}")

        if st.button("🗑️ Limpar Histórico da Matéria"):
            st.session_state[f"chat_history_{current_subject}"] = []
            st.rerun()

        # Status da API Key
        st.markdown("---")
        st.markdown("### 🔧 Status da API Key")
        
        # Mostra status da API key
        current_api_key = get_api_key()
        if current_api_key:
            api_preview = f"{current_api_key[:8]}...{current_api_key[-4:]}" if len(current_api_key) > 12 else "***"
            st.success(f"✅ API Key carregada: `{api_preview}`")
        else:
            st.error("❌ API Key não encontrada")
            st.info("Configure sua API Key no Streamlit Cloud ou arquivo .env")

    # Área Principal com Abas
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🧠 Mapa Mental", "📚 Exercícios Personalizados"])
    
    with tab1:
        # Área de Chat Principal
        st.header(f"Conversando com {subject_info.get('teacher', 'Assistente')}")

        # Adiciona introdução do professor se o chat estiver vazio
        if not st.session_state[f"chat_history_{current_subject}"]:
            st.session_state[f"chat_history_{current_subject}"].append(
                AIMessage(content=subject_info["intro"])
            )

        # Exibe o histórico de chat
        for message in st.session_state[f"chat_history_{current_subject}"]:
            avatar = subject_info.get('avatar', '🤖') if isinstance(message, AIMessage) else "🧑‍🎓"
            with st.chat_message(name="assistant" if isinstance(message, AIMessage) else "user", avatar=avatar):
                # Para matérias que podem conter fórmulas matemáticas, usa renderização especial
                if current_subject in ["Matemática", "Física", "Química"] and isinstance(message, AIMessage):
                    render_math_content(message.content)
                else:
                    st.markdown(message.content)
        
        # Input do usuário
        if prompt := st.chat_input(f"Envie uma mensagem para {subject_info.get('teacher', 'Assistente')}..."):
            st.session_state[f"chat_history_{current_subject}"].append(HumanMessage(content=prompt))
            
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(prompt)
                
            with st.chat_message("assistant", avatar=subject_info.get("avatar", "🤖")):
                message_placeholder = st.empty()
                
                # Obtém a resposta do professor
                full_response = get_teacher_response(current_subject, prompt, api_key)
                
                # Salva a ÚLTIMA interação (pergunta E resposta) para o mapa mental
                st.session_state.last_interaction = {
                    'question': prompt,
                    'answer': full_response,
                    'subject': current_subject
                }
                
                # Simula efeito de digitação e renderiza com fórmulas matemáticas
                if current_subject in ["Matemática", "Física", "Química"]:
                    # Para matérias com fórmulas, usa renderização especial
                    with message_placeholder.container():
                        render_math_content(full_response + "▌")
                    time.sleep(0.01)
                    message_placeholder.empty()
                    with message_placeholder.container():
                        render_math_content(full_response)
                else:
                    # Para outras matérias, usa markdown padrão
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
                    message_placeholder.markdown(full_response)

                st.session_state[f"chat_history_{current_subject}"].append(AIMessage(content=full_response))
                st.rerun()
    
    with tab2:
        # Mapa Mental Contextual
        lazy_import_mindmap()
        if "mindmap" in _imported_modules:
            # Pega a última interação salva
            last_interaction = st.session_state.get('last_interaction', {})
            question = last_interaction.get('question', '')
            answer = last_interaction.get('answer', '')
            
            # Chama a nova função com o contexto
            _imported_modules["mindmap"](
                pergunta_usuario=question,
                resposta_assistente=answer,
                api_key=api_key
            )
        else:
            st.error("❌ Sistema de Mapa Mental não está funcionando.")
    
    with tab3:
        # Exercícios Personalizados
        try:
            lazy_import_exercises()
            if "exercicios" in _imported_modules:
                _imported_modules["exercicios"].setup_ui()
            else:
                st.error("❌ Sistema de Exercícios Personalizados não disponível")
                st.info("Verifique se o arquivo `exercicios_personalizados.py` está presente e os arquivos JSON de questões estão disponíveis.")
        except Exception as e:
            st.error(f"❌ Erro ao carregar Exercícios Personalizados: {e}")
            st.info("""
            **Para ativar os Exercícios Personalizados:**
            1. Verifique se o arquivo `exercicios_personalizados.py` está presente
            2. Certifique-se de que os arquivos `questions_primeiro_dia.json` e `questions_segundo_enem.json` existem
            """)

if __name__ == "__main__":
    main() 