import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import PyPDF2
import re
from pathlib import Path
import streamlit as st
from dataclasses import dataclass
from enum import Enum

@dataclass
class MathExercise:
    """Estrutura para representar um exercício de matemática"""
    id: str
    year: int
    question_number: int
    question_text: str
    alternatives: List[str]
    correct_answer: str
    topic: str
    difficulty: str
    solution_explanation: str = ""
    image_references: List[str] = None
    
    def __post_init__(self):
        if self.image_references is None:
            self.image_references = []

class MathTopic(Enum):
    """Tópicos de matemática do ENEM"""
    ALGEBRA = "Álgebra"
    GEOMETRY = "Geometria"
    STATISTICS = "Estatística e Probabilidade"
    ARITHMETIC = "Aritmética"
    FUNCTIONS = "Funções"
    TRIGONOMETRY = "Trigonometria"
    COMBINATORICS = "Análise Combinatória"
    SEQUENCES = "Progressões"
    FINANCIAL_MATH = "Matemática Financeira"
    ANALYTICAL_GEOMETRY = "Geometria Analítica"
    OTHER = "Outros"

class EnemMathDatabase:
    """Sistema de base de dados para exercícios de matemática do ENEM"""
    
    def __init__(self, db_path: str = "enem_math_exercises.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Inicializa a base de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS math_exercises (
                id TEXT PRIMARY KEY,
                year INTEGER,
                question_number INTEGER,
                question_text TEXT,
                alternatives TEXT,
                correct_answer TEXT,
                topic TEXT,
                difficulty TEXT,
                solution_explanation TEXT,
                image_references TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                file_path TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                exercises_found INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def extract_math_exercises_from_pdf(self, pdf_path: str, year: int) -> List[MathExercise]:
        """Extrai exercícios de matemática de um PDF do ENEM"""
        exercises = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                # Extrai texto de todas as páginas
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # Processa o texto para encontrar exercícios de matemática
                exercises = self._parse_math_exercises(text, year)
                
        except Exception as e:
            print(f"Erro ao processar {pdf_path}: {str(e)}")
            
        return exercises
    
    def _parse_math_exercises(self, text: str, year: int) -> List[MathExercise]:
        """Parse do texto para extrair exercícios de matemática"""
        exercises = []
        
        # Regex para identificar questões (adaptável conforme formato)
        question_pattern = r"QUESTÃO\s+(\d+)"
        
        # Divide o texto em questões
        questions = re.split(question_pattern, text, flags=re.IGNORECASE)
        
        for i in range(1, len(questions), 2):
            if i + 1 < len(questions):
                question_num = int(questions[i])
                question_content = questions[i + 1]
                
                # Verifica se é uma questão de matemática (segundo dia questões 136-180)
                if self._is_math_question(question_num, question_content):
                    exercise = self._create_math_exercise(
                        year, question_num, question_content
                    )
                    if exercise:
                        exercises.append(exercise)
        
        return exercises
    
    def _is_math_question(self, question_num: int, content: str) -> bool:
        """Verifica se uma questão é de matemática"""
        # No ENEM, matemática geralmente está nas questões 136-180 do segundo dia
        if 136 <= question_num <= 180:
            return True
            
        # Palavras-chave que indicam matemática
        math_keywords = [
            'função', 'equação', 'gráfico', 'geometria', 'triângulo',
            'círculo', 'área', 'volume', 'probabilidade', 'estatística',
            'porcentagem', 'juros', 'progressão', 'logaritmo', 'seno',
            'cosseno', 'tangente', 'derivada', 'integral', 'matriz'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in math_keywords)
    
    def _create_math_exercise(self, year: int, question_num: int, content: str) -> MathExercise:
        """Cria um objeto MathExercise a partir do conteúdo extraído com parsing melhorado"""
        try:
            # Limpa o conteúdo primeiro
            cleaned_content = self._clean_enem_noise(content)
            
            # Separa enunciado e alternativas
            question_text, alternatives = self._smart_parse_alternatives(cleaned_content)
            
            # Se não conseguiu separar alternativas, usa método básico
            if len(alternatives) < 3:
                question_text, alternatives = self._fallback_parse(cleaned_content)
            
            # Identifica tópico baseado no conteúdo
            topic = self._identify_topic(question_text + " " + " ".join(alternatives))
            
            # Cria o exercício
            exercise = MathExercise(
                id=f"ENEM_{year}_Q{question_num}",
                year=year,
                question_number=question_num,
                question_text=question_text.strip(),
                alternatives=alternatives,
                correct_answer="",  # Será preenchido com o gabarito
                topic=topic.value,
                difficulty="Médio",  # Padrão ENEM
                solution_explanation=""
            )
            
            return exercise
            
        except Exception as e:
            print(f"Erro ao criar exercício da questão {question_num}: {str(e)}")
            return None
    
    def _clean_enem_noise(self, text: str) -> str:
        """Remove ruído típico dos PDFs do ENEM"""
        noise_patterns = [
            # Repetições massivas de ENEM
            r'(?:ENEM\d{4}){10,}.*?(?=\n|$)',
            # Códigos de arquivo
            r'\*[A-Z0-9]+\*',
            r'\d{6}AZ\.indb.*?\d{2}:\d{2}:\d{2}',
            # Cabeçalhos
            r'CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS.*?(?=\n|$)',
            r'• 2 º DIA • CADERNO \d+ • AZUL.*?(?=\n|$)',
            # Linhas de código muito longas
            r'(?:^|\n)[A-Z0-9]{50,}(?=\n|$)',
            # Referências
            r'Disponível em:.*?Acesso em:.*?\d{4}.*?(?:\(adaptado\))?',
        ]
        
        cleaned = text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Normaliza espaços
        cleaned = re.sub(r'\n{4,}', '\n\n', cleaned)
        cleaned = re.sub(r' {3,}', ' ', cleaned)
        
        return cleaned.strip()
    
    def _smart_parse_alternatives(self, text: str) -> tuple:
        """Parsing inteligente para separar enunciado e alternativas"""
        # Encontra todas as alternativas
        alt_pattern = r'\([A-E]\)'
        matches = list(re.finditer(alt_pattern, text))
        
        if len(matches) < 3:
            return text, []
        
        # Enunciado vai até a primeira alternativa
        statement_end = matches[0].start()
        statement = text[:statement_end].strip()
        
        # Extrai cada alternativa
        alternatives = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            alt_text = text[start:end].strip()
            # Remove a letra e limpa
            clean_alt = re.sub(r'^\([A-E]\)\s*', '', alt_text).strip()
            clean_alt = re.sub(r'\s+', ' ', clean_alt)  # Normaliza espaços
            
            if clean_alt and len(clean_alt) > 2:
                alternatives.append(clean_alt)
        
        # Limpa o enunciado
        statement = self._clean_statement(statement)
        
        return statement, alternatives
    
    def _clean_statement(self, statement: str) -> str:
        """Limpa o enunciado"""
        # Remove fragmentos comuns
        fragments = [
            r'Disponível em:.*?(?=\n|$)',
            r'Acesso em:.*?(?=\n|$)',
            r'\(adaptado\)',
            r'Fonte:.*?(?=\n|$)'
        ]
        
        cleaned = statement
        for pattern in fragments:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Normaliza espaços e quebras
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _fallback_parse(self, content: str) -> tuple:
        """Método de fallback para parsing quando o método principal falha"""
        parts = content.split('\n')
        question_text = ""
        alternatives = []
        current_alternative = ""
        
        for line in parts:
            line = line.strip()
            if not line:
                continue
                
            # Identifica alternativas (A), (B), (C), (D), (E)
            alt_match = re.match(r'\(([A-E])\)', line)
            if alt_match:
                if current_alternative:
                    clean_alt = re.sub(r'^\([A-E]\)\s*', '', current_alternative).strip()
                    alternatives.append(clean_alt)
                current_alternative = line
            elif current_alternative:
                current_alternative += " " + line
            else:
                question_text += " " + line
        
        # Adiciona a última alternativa
        if current_alternative:
            clean_alt = re.sub(r'^\([A-E]\)\s*', '', current_alternative).strip()
            alternatives.append(clean_alt)
        
        return question_text.strip(), alternatives

    def _identify_topic(self, content: str) -> MathTopic:
        """Identifica o tópico de matemática baseado no conteúdo"""
        content_lower = content.lower()
        
        # Mapeamento de palavras-chave para tópicos
        topic_keywords = {
            MathTopic.GEOMETRY: ['triângulo', 'círculo', 'área', 'volume', 'geometria', 'polígono'],
            MathTopic.ALGEBRA: ['equação', 'sistema', 'inequação', 'polinômio'],
            MathTopic.FUNCTIONS: ['função', 'gráfico', 'domínio', 'imagem', 'crescente'],
            MathTopic.STATISTICS: ['média', 'mediana', 'probabilidade', 'estatística', 'variância'],
            MathTopic.TRIGONOMETRY: ['seno', 'cosseno', 'tangente', 'trigonometria'],
            MathTopic.FINANCIAL_MATH: ['juros', 'desconto', 'financiamento', 'porcentagem'],
            MathTopic.COMBINATORICS: ['combinação', 'permutação', 'arranjo'],
            MathTopic.SEQUENCES: ['progressão', 'sequência', 'termo'],
            MathTopic.ANALYTICAL_GEOMETRY: ['reta', 'parábola', 'circunferência', 'coordenadas']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return topic
                
        return MathTopic.OTHER
    
    def save_exercise(self, exercise: MathExercise):
        """Salva um exercício na base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO math_exercises 
            (id, year, question_number, question_text, alternatives, correct_answer, 
             topic, difficulty, solution_explanation, image_references)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exercise.id,
            exercise.year,
            exercise.question_number,
            exercise.question_text,
            json.dumps(exercise.alternatives),
            exercise.correct_answer,
            exercise.topic,
            exercise.difficulty,
            exercise.solution_explanation,
            json.dumps(exercise.image_references)
        ))
        
        conn.commit()
        conn.close()
    
    def process_all_pdfs(self, base_path: str = "Segundo dia"):
        """Processa todos os PDFs da pasta Segundo dia"""
        years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        total_exercises = 0
        
        for year in years:
            year_path = Path(base_path) / str(year)
            if not year_path.exists():
                continue
                
            # Procura por PDFs de questões (não gabarito)
            pdf_files = list(year_path.glob("*.pdf"))
            question_pdfs = [f for f in pdf_files if 'gabarito' not in f.name.lower() and 'gb' not in f.name.lower()]
            
            for pdf_file in question_pdfs:
                print(f"Processando {pdf_file}...")
                exercises = self.extract_math_exercises_from_pdf(str(pdf_file), year)
                
                for exercise in exercises:
                    self.save_exercise(exercise)
                    total_exercises += 1
                
                # Log do processamento
                self._log_processing(year, str(pdf_file), "SUCCESS", len(exercises))
                print(f"  -> {len(exercises)} exercícios de matemática encontrados")
        
        print(f"\nProcessamento concluído! Total de exercícios: {total_exercises}")
    
    def _log_processing(self, year: int, file_path: str, status: str, exercises_found: int):
        """Registra o log de processamento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO processing_log (year, file_path, status, exercises_found)
            VALUES (?, ?, ?, ?)
        ''', (year, file_path, status, exercises_found))
        
        conn.commit()
        conn.close()
    
    def get_exercises_by_topic(self, topic: str) -> List[Dict]:
        """Busca exercícios por tópico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM math_exercises WHERE topic = ? ORDER BY year DESC, question_number
        ''', (topic,))
        
        results = cursor.fetchall()
        conn.close()
        
        exercises = []
        for row in results:
            exercises.append({
                'id': row[0],
                'year': row[1],
                'question_number': row[2],
                'question_text': row[3],
                'alternatives': json.loads(row[4]),
                'correct_answer': row[5],
                'topic': row[6],
                'difficulty': row[7],
                'solution_explanation': row[8],
                'image_references': json.loads(row[9]) if row[9] else []
            })
        
        return exercises
    
    def get_exercises_by_year(self, year: int) -> List[Dict]:
        """Busca exercícios por ano"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM math_exercises WHERE year = ? ORDER BY question_number
        ''', (year,))
        
        results = cursor.fetchall()
        conn.close()
        
        exercises = []
        for row in results:
            exercises.append({
                'id': row[0],
                'year': row[1],
                'question_number': row[2],
                'question_text': row[3],
                'alternatives': json.loads(row[4]),
                'correct_answer': row[5],
                'topic': row[6],
                'difficulty': row[7],
                'solution_explanation': row[8],
                'image_references': json.loads(row[9]) if row[9] else []
            })
        
        return exercises
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas da base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de exercícios
        cursor.execute('SELECT COUNT(*) FROM math_exercises')
        total_exercises = cursor.fetchone()[0]
        
        # Exercícios por ano
        cursor.execute('SELECT year, COUNT(*) FROM math_exercises GROUP BY year ORDER BY year')
        by_year = dict(cursor.fetchall())
        
        # Exercícios por tópico
        cursor.execute('SELECT topic, COUNT(*) FROM math_exercises GROUP BY topic ORDER BY COUNT(*) DESC')
        by_topic = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_exercises': total_exercises,
            'by_year': by_year,
            'by_topic': by_topic
        }

def main():
    """Função principal para processar os PDFs"""
    print("🔧 Iniciando processamento dos exercícios de matemática do ENEM...")
    
    # Cria a instância da base de dados
    db = EnemMathDatabase()
    
    # Processa todos os PDFs
    db.process_all_pdfs()
    
    # Mostra estatísticas
    stats = db.get_statistics()
    print(f"\n📊 Estatísticas da base de dados:")
    print(f"Total de exercícios: {stats['total_exercises']}")
    print(f"Exercícios por ano: {stats['by_year']}")
    print(f"Exercícios por tópico: {stats['by_topic']}")
    
    # Salva um resumo em JSON
    with open("math_database_summary.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Base de dados de exercícios de matemática criada com sucesso!")
    print("📁 Arquivo: enem_math_exercises.db")
    print("📄 Resumo: math_database_summary.json")

if __name__ == "__main__":
    main()
