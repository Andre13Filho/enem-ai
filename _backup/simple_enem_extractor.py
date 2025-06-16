import PyPDF2
import re
import json
import sqlite3
from typing import List, Tuple, Dict

class SimpleEnemExtractor:
    """Extrator simples e funcional para questões do ENEM"""
    
    def __init__(self):
        self.db_path = "corrected_enem_exercises.db"
        self.init_database()
    
    def init_database(self):
        """Inicializa base de dados limpa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS corrected_exercises (
                id TEXT PRIMARY KEY,
                year INTEGER,
                question_number INTEGER,
                clean_statement TEXT,
                alternative_a TEXT,
                alternative_b TEXT,
                alternative_c TEXT,
                alternative_d TEXT,
                alternative_e TEXT,
                topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def extract_from_one_pdf(self, pdf_path: str, year: int):
        """Extrai de um PDF específico para demonstrar"""
        print(f"📖 Extraindo de {pdf_path}...")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extrai texto completo
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
                
                # Limpa ruído
                clean_text = self.clean_enem_noise(full_text)
                
                # Extrai questões
                exercises = self.extract_questions_with_alternatives(clean_text, year)
                
                # Salva na base
                for exercise in exercises:
                    self.save_exercise(exercise)
                
                print(f"✅ {len(exercises)} questões extraídas e formatadas")
                return exercises
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return []
    
    def clean_enem_noise(self, text: str) -> str:
        """Remove ruído dos PDFs do ENEM"""
        # Padrões específicos para limpar
        patterns = [
            # Remove repetições de ENEM2024
            (r'(?:ENEM\d{4}){15,}.*?(?=\n|$)', ''),
            # Remove códigos
            (r'\*[A-Z0-9]+\*', ''),
            (r'\d{6}AZ\.indb.*?\d{2}:\d{2}:\d{2}', ''),
            # Remove cabeçalhos
            (r'CIÊNCIAS DA NATUREZA.*?AZUL.*?\d+', ''),
            (r'• 2 º DIA • CADERNO.*?(?=\n|$)', ''),
            # Remove linhas de código longas
            (r'(?:^|\n)[A-Z0-9]{40,}(?=\n|$)', ''),
        ]
        
        cleaned = text
        for pattern, replacement in patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Normaliza espaços
        cleaned = re.sub(r'\n{4,}', '\n\n', cleaned)
        cleaned = re.sub(r' {3,}', ' ', cleaned)
        
        return cleaned
    
    def extract_questions_with_alternatives(self, text: str, year: int) -> List[Dict]:
        """Extrai questões com alternativas bem separadas"""
        questions = []
        
        # Estratégia 1: Busca por sequências de 5 alternativas completas
        # Padrão: (A) texto (B) texto (C) texto (D) texto (E) texto
        alternative_sequence_pattern = r'\(A\).*?\(B\).*?\(C\).*?\(D\).*?\(E\)'
        
        # Encontra todas as sequências completas de alternativas
        sequences = re.finditer(alternative_sequence_pattern, text, re.DOTALL)
        
        question_number = 136  # Começa na primeira questão de matemática
        
        for match in sequences:
            # Pega o texto da sequência
            alternatives_text = match.group(0)
            
            # Pega texto antes das alternativas (enunciado)
            start_pos = max(0, match.start() - 1000)  # 1000 chars antes
            before_text = text[start_pos:match.start()]
            
            # Encontra onde começa o enunciado (fim da questão anterior)
            statement = self.extract_statement_before_alternatives(before_text)
            
            if statement and len(statement.strip()) > 30:  # Enunciado substancial
                # Extrai as 5 alternativas
                alternatives = self.parse_five_alternatives(alternatives_text)
                
                if len(alternatives) == 5:  # Deve ter exatamente 5
                    # Verifica se é conteúdo matemático
                    if self.is_math_content(statement + " " + " ".join(alternatives)):
                        question = {
                            'year': year,
                            'number': question_number,
                            'statement': statement.strip(),
                            'alternatives': alternatives,
                            'topic': self.classify_simple_topic(statement + " " + " ".join(alternatives))
                        }
                        
                        questions.append(question)
                        question_number += 1
                        
                        print(f"  📝 Q{question['number']}: {question['topic']}")
        
        return questions
    
    def extract_statement_before_alternatives(self, before_text: str) -> str:
        """Extrai o enunciado que vem antes das alternativas"""
        # Pega as últimas linhas que provavelmente são o enunciado
        lines = before_text.split('\n')
        
        # Procura por onde termina a questão anterior (final das alternativas anteriores)
        statement_lines = []
        found_start = False
        
        # Lê de trás para frente
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            
            # Se encontrou uma alternativa anterior, para
            if re.search(r'\([A-E]\)', line) and found_start:
                break
            
            statement_lines.insert(0, line)
            found_start = True
            
            # Não pega mais que 10 linhas
            if len(statement_lines) > 10:
                break
        
        # Junta as linhas do enunciado
        statement = " ".join(statement_lines)
        
        # Remove fragmentos comuns
        statement = re.sub(r'Disponível em:.*?(?=\n|$)', '', statement, flags=re.IGNORECASE)
        statement = re.sub(r'Acesso em:.*?(?=\n|$)', '', statement, flags=re.IGNORECASE)
        statement = re.sub(r'\(adaptado\)', '', statement, flags=re.IGNORECASE)
        
        # Normaliza espaços
        statement = re.sub(r'\s+', ' ', statement)
        
        return statement.strip()
    
    def parse_five_alternatives(self, alternatives_text: str) -> List[str]:
        """Extrai exatamente as 5 alternativas A, B, C, D, E"""
        alternatives = []
        
        # Encontra cada alternativa
        letters = ['A', 'B', 'C', 'D', 'E']
        
        for i, letter in enumerate(letters):
            # Padrão para esta alternativa
            if i < 4:  # A, B, C, D
                next_letter = letters[i + 1]
                pattern = f'\\({letter}\\)(.*?)\\({next_letter}\\)'
            else:  # E (última)
                pattern = f'\\({letter}\\)(.*?)$'
            
            match = re.search(pattern, alternatives_text, re.DOTALL)
            if match:
                alt_text = match.group(1).strip()
                # Limpa quebras e espaços
                alt_text = re.sub(r'\s+', ' ', alt_text)
                alternatives.append(alt_text)
            else:
                alternatives.append("")  # Alternativa vazia se não encontrar
        
        return alternatives
    
    def is_math_content(self, text: str) -> bool:
        """Verifica se é conteúdo matemático"""
        math_keywords = [
            'função', 'gráfico', 'equação', 'geometria', 'área', 'volume',
            'probabilidade', 'porcentagem', 'número', 'cálculo', 'valor',
            'medida', 'triângulo', 'círculo', 'estatística', 'média'
        ]
        
        text_lower = text.lower()
        matches = sum(1 for keyword in math_keywords if keyword in text_lower)
        return matches >= 1  # Pelo menos 1 palavra-chave
    
    def classify_simple_topic(self, text: str) -> str:
        """Classificação simples de tópicos"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['geometria', 'triângulo', 'círculo', 'área', 'volume']):
            return 'Geometria'
        elif any(word in text_lower for word in ['função', 'gráfico', 'domínio', 'imagem']):
            return 'Funções'
        elif any(word in text_lower for word in ['probabilidade', 'estatística', 'média', 'mediana']):
            return 'Estatística e Probabilidade'
        elif any(word in text_lower for word in ['porcentagem', 'juros', 'desconto']):
            return 'Matemática Financeira'
        elif any(word in text_lower for word in ['equação', 'sistema', 'polinômio']):
            return 'Álgebra'
        else:
            return 'Outros'
    
    def save_exercise(self, exercise: Dict):
        """Salva exercício na base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Garante que temos 5 alternativas
        alts = exercise['alternatives'] + [''] * 5
        
        cursor.execute('''
            INSERT OR REPLACE INTO corrected_exercises 
            (id, year, question_number, clean_statement, 
             alternative_a, alternative_b, alternative_c, alternative_d, alternative_e, topic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"CORRECTED_{exercise['year']}_Q{exercise['number']}",
            exercise['year'],
            exercise['number'],
            exercise['statement'],
            alts[0], alts[1], alts[2], alts[3], alts[4],
            exercise['topic']
        ))
        
        conn.commit()
        conn.close()
    
    def show_corrected_examples(self, limit: int = 2):
        """Mostra exemplos corrigidos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM corrected_exercises 
            ORDER BY year DESC, question_number 
            LIMIT ?
        ''', (limit,))
        
        exercises = cursor.fetchall()
        conn.close()
        
        print(f"\n📚 EXEMPLOS CORRIGIDOS:")
        
        for exercise in exercises:
            _, year, q_num, statement, alt_a, alt_b, alt_c, alt_d, alt_e, topic, _ = exercise
            
            print(f"\n{'='*60}")
            print(f"QUESTÃO {q_num} - ENEM {year}")
            print(f"TÓPICO: {topic}")
            print(f"{'='*60}")
            
            print(f"\nENUNCIADO:")
            print(f"{statement}")
            
            print(f"\nALTERNATIVAS:")
            alternatives = [alt_a, alt_b, alt_c, alt_d, alt_e]
            for i, alt in enumerate(alternatives):
                if alt.strip():  # Só mostra se não estiver vazio
                    letter = chr(65 + i)  # A, B, C, D, E
                    print(f"{letter}) {alt}")
            
            print(f"\n{'-'*60}")
    
    def get_stats(self):
        """Estatísticas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM corrected_exercises')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT topic, COUNT(*) FROM corrected_exercises GROUP BY topic ORDER BY COUNT(*) DESC')
        by_topic = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"Total de questões extraídas: {total}")
        print(f"\nPor tópico:")
        for topic, count in by_topic:
            print(f"  {topic}: {count} questões")

def main():
    """Teste com um PDF específico"""
    extractor = SimpleEnemExtractor()
    
    # Testa com PDF mais recente
    test_file = "Segundo dia/2024/dia02_2024.pdf"
    
    if os.path.exists(test_file):
        print("🚀 TESTE DE EXTRAÇÃO CORRIGIDA")
        print("="*50)
        
        exercises = extractor.extract_from_one_pdf(test_file, 2024)
        
        if exercises:
            extractor.get_stats()
            extractor.show_corrected_examples(2)
        
        print(f"\n✅ Teste concluído! Base: corrected_enem_exercises.db")
    else:
        print(f"❌ Arquivo não encontrado: {test_file}")

if __name__ == "__main__":
    import os
    main() 