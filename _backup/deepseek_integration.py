"""
Integração com DeepSeek R1 0528 via OpenRouter para o ENEM AI Helper
Este arquivo contém a configuração para usar a LLM DeepSeek nos professores particulares.
"""

import streamlit as st
from openai import OpenAI
from typing import Dict, Optional
import time

class DeepSeekTeacher:
    """Classe para integração com DeepSeek R1 0528 via OpenRouter"""
    
    def __init__(self, api_key: str, site_url: str = "", site_name: str = "ENEM AI Helper"):
        """
        Inicializa o cliente DeepSeek
        
        Args:
            api_key (str): Chave da API do OpenRouter
            site_url (str): URL do seu site (opcional)
            site_name (str): Nome do seu site (opcional)
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.site_url = site_url
        self.site_name = site_name
        self.model = "deepseek/deepseek-r1-0528:free"
    
    def get_teacher_response(self, subject: str, message: str, teacher_name: str) -> str:
        """
        Obtém resposta do professor usando DeepSeek R1
        
        Args:
            subject (str): Matéria do ENEM
            message (str): Pergunta da Sther
            teacher_name (str): Nome do professor
            
        Returns:
            str: Resposta do professor
        """
        
        # Prompts especializados para cada matéria
        system_prompts = {
            "Matemática": f"""Você é o {teacher_name}, um professor particular brasileiro especializado em Matemática para o ENEM. 
            Você ensina álgebra, geometria, estatística, análise combinatória e matemática aplicada de forma didática e motivadora.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Use analogias do cotidiano brasileiro
            - Explique passo a passo com clareza
            - Seja motivador e paciente
            - Relate conceitos com situações práticas
            - Use exemplos que uma adolescente brasileira entenderia
            - Sempre responda em português brasileiro
            - Foque nos tópicos que caem no ENEM""",
            
            "Língua Portuguesa": f"""Você é a {teacher_name}, uma professora particular brasileira especializada em Língua Portuguesa para o ENEM.
            Você ensina gramática, literatura brasileira, interpretação de textos e análise linguística de forma envolvente.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Use exemplos da literatura brasileira
            - Relacione gramática com textos atuais
            - Seja carismática e inspire amor pela língua
            - Use referências culturais brasileiras
            - Explique de forma clara e didática
            - Sempre responda em português brasileiro
            - Foque nos aspectos que o ENEM cobra""",
            
            "Biologia": f"""Você é o {teacher_name}, um professor particular brasileiro especializado em Biologia para o ENEM.
            Você ensina biologia celular, genética, ecologia, evolução e fisiologia de forma curiosa e interessante.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Relacione com a biodiversidade brasileira
            - Use exemplos da natureza do Brasil
            - Seja curioso e desperte interesse científico
            - Conecte conceitos com o cotidiano
            - Explique processos de forma visual
            - Sempre responda em português brasileiro
            - Foque nos temas do ENEM""",
            
            "Geografia": f"""Você é a {teacher_name}, uma professora particular brasileira especializada em Geografia para o ENEM.
            Você ensina geografia física, humana, geopolítica e questões ambientais com foco na realidade brasileira.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Use exemplos do território brasileiro
            - Relacione com questões socioambientais atuais
            - Conecte geografia com política e sociedade
            - Seja dinâmica e atual
            - Use mapas mentais e comparações
            - Sempre responda em português brasileiro
            - Foque nos temas geográficos do ENEM""",
            
            "História": f"""Você é o {teacher_name}, um professor particular brasileiro especializado em História para o ENEM.
            Você ensina história do Brasil, história geral e atualidades de forma interessante e contextualizada.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Priorize a história do Brasil
            - Relacione passado com presente
            - Use cronologias e marcos temporais
            - Conte histórias envolventes
            - Conecte com questões sociais atuais
            - Sempre responda em português brasileiro
            - Foque nos períodos históricos do ENEM""",
            
            "Química": f"""Você é a {teacher_name}, uma professora particular brasileira especializada em Química para o ENEM.
            Você ensina química orgânica, inorgânica, físico-química e bioquímica de forma prática e interessante.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Use experimentos mentais e analogias
            - Relacione química com o cotidiano
            - Explique reações e processos step-by-step
            - Seja entusiasta e mostre como a química é fascinante
            - Use exemplos de produtos e materiais conhecidos
            - Sempre responda em português brasileiro
            - Foque nos conceitos químicos do ENEM""",
            
            "Física": f"""Você é o {teacher_name}, um professor particular brasileiro especializado em Física para o ENEM.
            Você ensina mecânica, eletromagnetismo, ondulatória, termodinâmica e física moderna de forma clara e aplicada.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Use fenômenos físicos do dia a dia
            - Explique leis e fórmulas com exemplos práticos
            - Seja paciente com cálculos e conceitos
            - Relacione física com tecnologia atual
            - Use analogias e comparações úteis
            - Sempre responda em português brasileiro
            - Foque nos tópicos de física do ENEM""",
            
            "Redação": f"""Você é a {teacher_name}, uma professora particular brasileira especializada em Redação para o ENEM.
            Você ensina redação dissertativa-argumentativa, estrutura textual, argumentação e repertório sociocultural.
            Sua aluna é Sther, uma jovem de 17 anos que está se preparando para o ENEM.
            
            Características do seu ensino:
            - Ensine a estrutura padrão do ENEM
            - Trabalhe argumentação sólida e coesa
            - Desenvolva repertório sociocultural brasileiro
            - Incentive análise crítica de temas sociais
            - Prepare para os 5 critérios de avaliação
            - Sempre responda em português brasileiro
            - Foque na redação específica do ENEM"""
        }
        
        # Seleciona o prompt apropriado para a matéria
        system_prompt = system_prompts.get(subject, f"Você é {teacher_name}, professor de {subject} especializado no ENEM.")
        
        try:
            # Headers opcionais para ranking no OpenRouter
            extra_headers = {}
            if self.site_url:
                extra_headers["HTTP-Referer"] = self.site_url
            if self.site_name:
                extra_headers["X-Title"] = self.site_name
            
            completion = self.client.chat.completions.create(
                extra_headers=extra_headers,
                extra_body={},
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": f"Oi professor(a)! Tenho uma dúvida sobre {subject}: {message}"
                    }
                ],
                max_tokens=800,
                temperature=0.7,
                top_p=0.9
            )
            
            response = completion.choices[0].message.content
            return response if response else "Desculpe Sther, não consegui processar sua pergunta. Pode tentar reformular?"
            
        except Exception as e:
            return f"Opa Sther! Estou com um probleminha técnico aqui. Pode tentar novamente em alguns segundos? 🤖💙"

def setup_deepseek_config():
    """Configura a interface para inserir credenciais do DeepSeek"""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Configuração DeepSeek R1")
    
    # Campo para API Key
    api_key = st.sidebar.text_input(
        "OpenRouter API Key:",
        type="password",
        help="Insira sua chave da API do OpenRouter"
    )
    
    # Campos opcionais
    with st.sidebar.expander("Configurações Avançadas (Opcional)"):
        site_url = st.text_input(
            "URL do seu site:",
            value="",
            help="Para ranking no OpenRouter (opcional)"
        )
        site_name = st.text_input(
            "Nome do seu site:",
            value="ENEM AI Helper",
            help="Para ranking no OpenRouter"
        )
    
    # Status da conexão
    if api_key:
        st.sidebar.success("✅ API Key configurada!")
        
        # Teste de conexão
        if st.sidebar.button("🧪 Testar Conexão"):
            with st.sidebar.spinner("Testando..."):
                try:
                    teacher = DeepSeekTeacher(api_key, site_url, site_name)
                    test_response = teacher.get_teacher_response(
                        "Matemática", 
                        "teste de conexão", 
                        "Prof. Carlos"
                    )
                    if "probleminha técnico" not in test_response:
                        st.sidebar.success("🎉 Conexão OK!")
                    else:
                        st.sidebar.error("❌ Erro na conexão")
                except Exception as e:
                    st.sidebar.error(f"❌ Erro: {str(e)}")
    else:
        st.sidebar.warning("⚠️ Configure sua API Key")
    
    return api_key, site_url, site_name

def get_deepseek_response(subject: str, message: str, teacher_name: str, 
                         api_key: str, site_url: str = "", site_name: str = "ENEM AI Helper") -> str:
    """
    Função principal para obter resposta do DeepSeek
    
    Args:
        subject (str): Matéria
        message (str): Pergunta da Sther
        teacher_name (str): Nome do professor
        api_key (str): Chave da API
        site_url (str): URL do site (opcional)
        site_name (str): Nome do site (opcional)
        
    Returns:
        str: Resposta do professor
    """
    if not api_key:
        return "🔑 Por favor, configure sua API Key do OpenRouter no painel lateral para usar o DeepSeek R1!"
    
    teacher = DeepSeekTeacher(api_key, site_url, site_name)
    return teacher.get_teacher_response(subject, message, teacher_name)

# Exemplo de como usar no app principal
def integration_instructions():
    """
    INSTRUÇÕES PARA INTEGRAR NO APP.PY PRINCIPAL:
    
    1. Importe este módulo no início do app.py:
       from deepseek_integration import setup_deepseek_config, get_deepseek_response
    
    2. Na função main(), adicione a configuração no sidebar:
       api_key, site_url, site_name = setup_deepseek_config()
    
    3. Substitua a função get_teacher_response() por:
       
       def get_teacher_response(subject: str, message: str) -> str:
           teacher_name = SUBJECTS[subject]["teacher"]
           
           # Verifica se há API key configurada
           api_key = st.session_state.get('deepseek_api_key', '')
           site_url = st.session_state.get('deepseek_site_url', '')
           site_name = st.session_state.get('deepseek_site_name', 'ENEM AI Helper')
           
           if api_key:
               return get_deepseek_response(subject, message, teacher_name, api_key, site_url, site_name)
           else:
               # Fallback para resposta simulada
               return "🔑 Configure sua API Key do OpenRouter para ativar os professores inteligentes!"
    
    4. No setup da configuração, salve as variáveis no session_state:
       st.session_state['deepseek_api_key'] = api_key
       st.session_state['deepseek_site_url'] = site_url  
       st.session_state['deepseek_site_name'] = site_name
    """
    pass 