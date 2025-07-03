import streamlit as st
import json
from pathlib import Path
import re
from typing import Dict, List, Tuple

# --- CONFIGURAÇÃO HUGGING FACE ---
# Substitua com seu usuário e nome do repositório onde os PDFs estão.
HF_USER = "Andre13Filho"
HF_REPO = "enem_tests_editions"
HF_PDF_BASE_URL = f"https://huggingface.co/datasets/{HF_USER}/{HF_REPO}/resolve/main"
# ---------------------------------

@st.cache_data
def load_data():
    """Carrega dados das questões do ENEM."""
    try:
        # Carrega questões do primeiro dia
        with open("questions_primeiro_dia.json", "r", encoding="utf-8") as f:
            primeiro_dia = json.load(f)
        
        # Carrega questões do segundo dia
        with open("questions_segundo_enem.json", "r", encoding="utf-8") as f:
            segundo_dia = json.load(f)
        
        # Combina os dados
        all_questions = {**primeiro_dia, **segundo_dia}
        
        return {
            "questions": all_questions,
            "total": len(all_questions)
        }
    except FileNotFoundError as e:
        st.error(f"Arquivo não encontrado: {e}")
        return {"questions": {}, "total": 0}
    except json.JSONDecodeError as e:
        st.error(f"Erro ao decodificar JSON: {e}")
        return {"questions": {}, "total": 0}

@st.cache_data
def load_gabaritos():
    """Carrega dados dos gabaritos do ENEM."""
    try:
        # Carrega gabaritos do primeiro dia
        with open("gabaritos_primeiro_dia.json", "r", encoding="utf-8") as f:
            primeiro_dia_gab = json.load(f)
        
        # Carrega gabaritos do segundo dia
        with open("gabaritos_segundo_dia.json", "r", encoding="utf-8") as f:
            segundo_dia_gab = json.load(f)
        
        # Combina os dados
        all_gabaritos = {**primeiro_dia_gab, **segundo_dia_gab}
        
        return all_gabaritos
    except FileNotFoundError as e:
        st.error(f"Arquivo de gabarito não encontrado: {e}")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"Erro ao decodificar gabarito JSON: {e}")
        return {}

def get_gabarito(question_id: str, gabaritos_data: Dict) -> str:
    """Obtém o gabarito para uma questão específica."""
    return gabaritos_data.get(question_id, "N/A")

def extract_keywords(text):
    """Extrai palavras-chave relevantes do texto."""
    # Remove pontuação e converte para minúsculas
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Lista de stop words em português
    stop_words = {
        'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'não', 'que', 'se', 'por', 'mais',
        'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há',
        'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois',
        'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas', 'numa', 'pelos', 'pelas', 'esse', 'esses', 'essa', 'essas',
        'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes', 'meu', 'minha', 'teu', 'tua', 'nosso', 'nossa', 'vosso', 'vossa'
    }
    
    words = text.split()
    keywords = [word for word in words if word not in stop_words]
    
    return keywords

def calculate_relevance(question_data, keywords, subject):
    """Calcula a relevância de uma questão baseada nas palavras-chave e matéria."""
    score = 0
    
    disciplina = question_data.get("disciplina", "").lower()
    tema = question_data.get("tema", "").lower()
    conteudo = question_data.get("conteudo", "").lower()
    
    # Mapeamento de matérias para disciplinas
    subject_mapping = {
        "Matemática": ["matemática"],
        "Física": ["física"],
        "Química": ["química"],
        "Biologia": ["biologia"],
        "História": ["história"],
        "Geografia": ["geografia"],
        "Língua Portuguesa": ["português", "literatura", "artes"],
        "Linguagens": ["português", "literatura", "artes", "espanhol"],
        "Redação": ["redação", "português", "literatura"]
    }
    
        # Bonus por matéria correspondente
    if subject in subject_mapping:
        for mapped_subject in subject_mapping[subject]:
            if mapped_subject in disciplina:
                score += 10
            
    # Pontuação por palavras-chave encontradas
    for keyword in keywords:
        if keyword in tema:
            score += 5
        if keyword in disciplina:
            score += 3
        if keyword in conteudo:
            score += 1
    
    return score

def find_relevant_exercises(user_question, questions_data, current_subject):
    """Encontra exercícios relevantes baseados na dúvida do usuário."""
    if not user_question:
        return []
    
    keywords = extract_keywords(user_question)
    if not keywords:
        return []
    
    # Calcula relevância para cada questão
    scored_questions = []
    for question_id, question_data in questions_data.items():
        score = calculate_relevance(question_data, keywords, current_subject)
        if score > 0:
            scored_questions.append((question_id, score, question_data))
    
    # Ordena por relevância e depois por ano
    scored_questions.sort(key=lambda x: (x[1], int(x[0].split('_')[0])), reverse=True)
    
    return scored_questions[:5]

def get_pdf_info(question_key):
    """Retorna informações sobre o PDF da questão."""
    year, number_str = question_key.split('_')
    number = int(number_str)
    
    # Determina o dia baseado no número da questão
    if 1 <= number <= 90:
        day = 1
        pdf_name = f"dia01_{year}.pdf"
        # Primeiro dia está na pasta raiz
        possible_paths = [
            Path("Primeiro dia") / year / pdf_name
        ]
    else:
        day = 2
        pdf_name = f"dia02_{year}.pdf"
        # Segundo dia está na pasta raiz
        possible_paths = [
            Path("Segundo dia") / year / pdf_name
        ]
    
    # Procura o PDF nas pastas disponíveis
    for path in possible_paths:
        if path.exists():
            return {
                "path": str(path),
                "name": pdf_name,
                "year": year,
                "day": day,
                "question_number": number
            }
    
    # Se não encontrou com o nome padrão, tenta buscar qualquer PDF do ano na pasta
    if day == 1:
        year_folders = [
            Path("Primeiro dia") / year
        ]
    else:
        year_folders = [
            Path("Segundo dia") / year
        ]
    
    for folder in year_folders:
        if folder.exists():
            # Procura qualquer PDF na pasta do ano
            pdf_files = list(folder.glob("*.pdf"))
            if pdf_files:
                pdf_path = pdf_files[0]  # Pega o primeiro PDF encontrado
                return {
                    "path": str(pdf_path),
                    "name": pdf_path.name,
                    "year": year,
                    "day": day,
                    "question_number": number
                }
    
    return None

class ExerciciosPersonalizados:
    def __init__(self):
        self.data = load_data()
        self.gabaritos = load_gabaritos()

    def setup_ui(self):
        st.markdown("### 📚 Exercícios Personalizados")
        st.markdown("*Recomendações baseadas na sua última dúvida*")

        # Obtém a última pergunta e matéria atual
        last_question = st.session_state.get("last_user_question", "")
        current_subject = st.session_state.get("current_subject", "Geral")

        if not last_question:
            st.info("💡 Faça uma pergunta para qualquer professor no chat e eu recomendarei exercícios do ENEM relacionados!")
            return

        # Extrai o texto da pergunta
        question_text = last_question.get('content', str(last_question)) if isinstance(last_question, dict) else str(last_question)
        
        # Mostra a dúvida analisada
        with st.expander("🔍 Sua última dúvida", expanded=False):
            st.write(f"**Matéria:** {current_subject}")
            st.write(f"**Pergunta:** {question_text}")
        
        st.markdown("---")
        
        # Busca exercícios relevantes
        recommendations = find_relevant_exercises(question_text, self.data["questions"], current_subject)

        if not recommendations:
            st.warning("Não encontrei exercícios específicos para sua dúvida. Tente ser mais específico no chat!")
            return

        # Exibe as recomendações
        st.success(f"🎯 Encontrei **{len(recommendations)}** exercícios recomendados:")

        for i, (question_id, score, question_data) in enumerate(recommendations):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    year, number_str = question_id.split('_')
                    number = int(number_str)
                    st.markdown(f"**📝 Resolva a Questão {number} do ENEM {year}**")
                    
                    tema_completo = f"**📚 {question_data.get('disciplina', 'N/A')}**"
                    if question_data.get('tema'):
                        tema_completo += f" • {question_data.get('tema')}"
                    if question_data.get('conteudo'):
                        tema_completo += f" ({question_data.get('conteudo')})"
                    st.caption(tema_completo)
                    
                    # Adiciona o gabarito
                    gabarito = get_gabarito(question_id, self.gabaritos)
                    if gabarito != "N/A":
                        st.info(f"✅ **Gabarito:** {gabarito}")
                    else:
                        st.warning("⚠️ Gabarito não disponível")
                
                with col2:
                    # Determina o dia e o nome do arquivo com base no número da questão
                    if 1 <= number <= 90:
                        pdf_filename = f"dia01_{year}.pdf"
                    else:
                        pdf_filename = f"dia02_{year}.pdf"
                    
                    pdf_url = f"{HF_PDF_BASE_URL}/{pdf_filename}"
                    
                    st.link_button(
                        "🔗 Abrir Prova (PDF)",
                        url=pdf_url,
                        use_container_width=True
                    )

# Instância global
exercicios_personalizados = ExerciciosPersonalizados() 