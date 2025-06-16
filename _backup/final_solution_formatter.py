import sqlite3
import json
import re
from typing import List, Tuple

class ExerciseFormatter:
    """Formata exercícios já extraídos para ter enunciados e alternativas bem separadas"""
    
    def __init__(self, source_db: str = "enem_math_exercises.db"):
        self.source_db = source_db
        self.target_db = "formatted_math_exercises.db"
        self.init_target_database()
    
    def init_target_database(self):
        """Inicializa base de dados formatada"""
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formatted_exercises (
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
                source_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def process_all_exercises(self):
        """Processa todos os exercícios da base original"""
        print("🔧 Formatando exercícios existentes...")
        
        # Lê da base original
        conn = sqlite3.connect(self.source_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM math_exercises ORDER BY year, question_number')
        exercises = cursor.fetchall()
        conn.close()
        
        formatted_count = 0
        
        for exercise in exercises:
            # Desempacota baseado no número real de colunas
            if len(exercise) >= 10:
                exercise_id, year, question_number, question_text, alternatives_json, correct_answer, topic, difficulty, solution_explanation, image_references = exercise[:10]
            else:
                # Fallback para estrutura diferente
                exercise_id = exercise[0]
                year = exercise[1] 
                question_number = exercise[2]
                question_text = exercise[3]
                alternatives_json = exercise[4] if len(exercise) > 4 else ""
                topic = exercise[6] if len(exercise) > 6 else "Outros"
            
            # Tenta formatar este exercício
            formatted = self.format_single_exercise(
                question_text, alternatives_json, exercise_id, year, question_number, topic
            )
            
            if formatted:
                self.save_formatted_exercise(formatted)
                formatted_count += 1
                print(f"  ✅ {exercise_id} - {topic}")
        
        print(f"\n🎉 {formatted_count} exercícios formatados com sucesso!")
        return formatted_count
    
    def format_single_exercise(self, question_text: str, alternatives_json: str, 
                             exercise_id: str, year: int, question_number: int, topic: str) -> dict:
        """Formata um único exercício"""
        try:
            # Combina o texto da questão com alternativas se disponível
            full_text = question_text
            
            # Se há alternativas em JSON, adiciona ao texto
            try:
                existing_alts = json.loads(alternatives_json) if alternatives_json else []
                if existing_alts:
                    full_text += " " + " ".join(existing_alts)
            except:
                pass
            
            # Tenta extrair enunciado e alternativas do texto completo
            statement, alternatives = self.smart_extract_from_text(full_text)
            
            # Verifica se conseguiu extrair adequadamente
            if statement and len(statement.strip()) > 20 and len(alternatives) >= 3:
                return {
                    'id': f"FORMATTED_{year}_Q{question_number}",
                    'year': year,
                    'question_number': question_number,
                    'statement': statement.strip(),
                    'alternatives': alternatives,
                    'topic': topic,
                    'source_id': exercise_id
                }
            
            return None
            
        except Exception as e:
            print(f"  ❌ Erro ao formatar {exercise_id}: {str(e)}")
            return None
    
    def smart_extract_from_text(self, text: str) -> Tuple[str, List[str]]:
        """Extração inteligente de enunciado e alternativas"""
        
        # Limpa o texto primeiro
        cleaned_text = self.clean_text(text)
        
        # Método 1: Procura por padrão (A) (B) (C) (D) (E)
        alt_pattern = r'\([A-E]\)'
        matches = list(re.finditer(alt_pattern, cleaned_text))
        
        if len(matches) >= 3:
            # Enunciado é tudo antes da primeira alternativa
            first_alt_pos = matches[0].start()
            statement = cleaned_text[:first_alt_pos].strip()
            
            # Extrai alternativas
            alternatives = []
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned_text)
                
                alt_text = cleaned_text[start:end].strip()
                # Remove a letra da alternativa
                clean_alt = re.sub(r'^\([A-E]\)\s*', '', alt_text).strip()
                
                if clean_alt:
                    alternatives.append(clean_alt)
            
            return statement, alternatives
        
        # Método 2: Se não encontrou alternativas claras, tenta outros padrões
        # Procura por linhas que começam com A), B), etc.
        line_pattern = r'^([A-E])\s*\)\s*(.+)$'
        lines = cleaned_text.split('\n')
        
        statement_lines = []
        alternatives = []
        found_alternatives = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = re.match(line_pattern, line)
            if match:
                letter, alt_text = match.groups()
                alternatives.append(alt_text.strip())
                found_alternatives = True
            elif not found_alternatives:
                statement_lines.append(line)
        
        if len(alternatives) >= 3:
            statement = " ".join(statement_lines)
            return statement, alternatives
        
        # Método 3: Fallback - usa texto completo como enunciado
        return cleaned_text, []
    
    def clean_text(self, text: str) -> str:
        """Limpa o texto"""
        # Remove códigos ENEM repetitivos
        cleaned = re.sub(r'(?:ENEM\d{4}){10,}.*?(?=\n|$)', '', text, flags=re.MULTILINE)
        
        # Remove códigos entre asteriscos
        cleaned = re.sub(r'\*[A-Z0-9]+\*', '', cleaned)
        
        # Remove referências
        cleaned = re.sub(r'Disponível em:.*?Acesso em:.*?\d{4}.*?(?:\(adaptado\))?', '', cleaned, flags=re.IGNORECASE)
        
        # Normaliza espaços
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def save_formatted_exercise(self, exercise: dict):
        """Salva exercício formatado"""
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # Garante 5 alternativas
        alts = exercise['alternatives'] + [''] * 5
        
        cursor.execute('''
            INSERT OR REPLACE INTO formatted_exercises 
            (id, year, question_number, clean_statement, 
             alternative_a, alternative_b, alternative_c, alternative_d, alternative_e, 
             topic, source_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exercise['id'],
            exercise['year'],
            exercise['question_number'],
            exercise['statement'],
            alts[0], alts[1], alts[2], alts[3], alts[4],
            exercise['topic'],
            exercise['source_id']
        ))
        
        conn.commit()
        conn.close()
    
    def create_display_examples(self) -> str:
        """Cria exemplos para demonstrar o resultado"""
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM formatted_exercises 
            WHERE alternative_a != '' AND alternative_b != '' AND alternative_c != ''
            ORDER BY year DESC, question_number 
            LIMIT 3
        ''')
        
        exercises = cursor.fetchall()
        conn.close()
        
        if not exercises:
            return "❌ Nenhum exercício bem formatado encontrado."
        
        result = "📚 EXERCÍCIOS FORMATADOS CORRETAMENTE:\n\n"
        
        for exercise in exercises:
            _, year, q_num, statement, alt_a, alt_b, alt_c, alt_d, alt_e, topic, source_id, _ = exercise
            
            result += f"{'='*60}\n"
            result += f"QUESTÃO {q_num} - ENEM {year} | {topic}\n"
            result += f"{'='*60}\n\n"
            
            result += f"ENUNCIADO:\n{statement}\n\n"
            
            result += f"ALTERNATIVAS:\n"
            alternatives = [alt_a, alt_b, alt_c, alt_d, alt_e]
            for i, alt in enumerate(alternatives):
                if alt.strip():
                    letter = chr(65 + i)  # A, B, C, D, E
                    result += f"{letter}) {alt}\n"
            
            result += f"\n{'-'*60}\n\n"
        
        return result
    
    def get_statistics(self) -> str:
        """Gera estatísticas da formatação"""
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        # Total formatado
        cursor.execute('SELECT COUNT(*) FROM formatted_exercises')
        total = cursor.fetchone()[0]
        
        # Com alternativas válidas
        cursor.execute('''
            SELECT COUNT(*) FROM formatted_exercises 
            WHERE alternative_a != '' AND alternative_b != '' AND alternative_c != ''
        ''')
        with_alternatives = cursor.fetchone()[0]
        
        # Por tópico
        cursor.execute('''
            SELECT topic, COUNT(*) FROM formatted_exercises 
            GROUP BY topic ORDER BY COUNT(*) DESC
        ''')
        by_topic = cursor.fetchall()
        
        conn.close()
        
        result = f"📊 ESTATÍSTICAS DE FORMATAÇÃO:\n"
        result += f"Total de exercícios processados: {total}\n"
        result += f"Com alternativas bem formatadas: {with_alternatives}\n"
        result += f"Taxa de sucesso: {(with_alternatives/total)*100:.1f}%\n\n"
        
        result += f"Por tópico:\n"
        for topic, count in by_topic:
            result += f"  {topic}: {count} exercícios\n"
        
        return result

def main():
    """Função principal"""
    print("🚀 FORMATAÇÃO FINAL DOS EXERCÍCIOS")
    print("="*50)
    
    formatter = ExerciseFormatter()
    
    # Processa todos os exercícios
    count = formatter.process_all_exercises()
    
    if count > 0:
        # Mostra estatísticas
        print("\n" + formatter.get_statistics())
        
        # Mostra exemplos
        print(formatter.create_display_examples())
        
        print(f"✅ Base formatada criada: formatted_math_exercises.db")
    else:
        print("❌ Nenhum exercício foi formatado com sucesso.")

if __name__ == "__main__":
    main() 