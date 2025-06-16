import re
import json
import sqlite3
from typing import List, Tuple, Dict

class AlternativesFixer:
    """Classe para corrigir e melhorar a extração de alternativas dos exercícios"""
    
    def __init__(self, db_path: str = "enem_math_exercises.db"):
        self.db_path = db_path
    
    def fix_all_exercises(self):
        """Corrige todos os exercícios na base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Busca todos os exercícios
        cursor.execute('SELECT * FROM math_exercises')
        exercises = cursor.fetchall()
        
        fixed_count = 0
        
        for exercise in exercises:
            exercise_id = exercise[0]
            raw_alternatives = exercise[4]  # Campo alternatives
            question_text = exercise[3]     # Campo question_text
            
            # Tenta extrair alternativas do texto bruto
            if raw_alternatives:
                try:
                    current_alts = json.loads(raw_alternatives)
                    
                    # Se as alternativas estão vazias ou mal formatadas
                    if not current_alts or len(current_alts) == 0 or all(len(alt) < 5 for alt in current_alts):
                        # Tenta extrair do question_text
                        new_statement, new_alternatives = self.extract_alternatives_from_text(question_text)
                        
                        if new_alternatives and len(new_alternatives) >= 3:
                            # Atualiza na base de dados
                            cursor.execute('''
                                UPDATE math_exercises 
                                SET question_text = ?, alternatives = ?
                                WHERE id = ?
                            ''', (new_statement, json.dumps(new_alternatives, ensure_ascii=False), exercise_id))
                            
                            fixed_count += 1
                            print(f"✅ Corrigido: {exercise_id}")
                        
                except Exception as e:
                    print(f"❌ Erro ao processar {exercise_id}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 {fixed_count} exercícios foram corrigidos!")
        return fixed_count
    
    def extract_alternatives_from_text(self, full_text: str) -> Tuple[str, List[str]]:
        """Extrai enunciado e alternativas de um texto completo"""
        
        # Remove códigos repetitivos do ENEM primeiro
        cleaned_text = self.clean_enem_codes(full_text)
        
        # Procura por padrões de alternativas
        alternatives_pattern = r'\([A-E]\)'
        matches = list(re.finditer(alternatives_pattern, cleaned_text))
        
        if len(matches) < 3:
            return cleaned_text, []
        
        # Encontra onde começam as alternativas
        first_alternative_pos = matches[0].start()
        
        # Enunciado é tudo antes da primeira alternativa
        statement = cleaned_text[:first_alternative_pos].strip()
        
        # Extrai cada alternativa
        alternatives = []
        for i, match in enumerate(matches):
            start_pos = match.start()
            
            # Fim da alternativa atual
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(cleaned_text)
            
            # Texto da alternativa
            alt_text = cleaned_text[start_pos:end_pos].strip()
            
            # Remove a letra da alternativa e limpa
            clean_alt = re.sub(r'^\([A-E]\)\s*', '', alt_text).strip()
            
            # Remove quebras desnecessárias
            clean_alt = re.sub(r'\s+', ' ', clean_alt)
            
            if clean_alt and len(clean_alt) > 3:
                alternatives.append(clean_alt)
        
        # Limpa o enunciado
        statement = self.clean_statement(statement)
        
        return statement, alternatives
    
    def clean_enem_codes(self, text: str) -> str:
        """Remove códigos repetitivos do ENEM"""
        
        # Padrões de limpeza específicos
        patterns = [
            # Remove repetições massivas de ENEM2024
            (r'ENEM\d{4}(?:ENEM\d{4}){10,}.*?(?=\n|$)', ''),
            
            # Remove códigos entre asteriscos
            (r'\*[A-Z0-9]+\*', ''),
            
            # Remove informações de arquivo
            (r'\d{6}AZ\.indb.*?\d{2}:\d{2}:\d{2}', ''),
            
            # Remove cabeçalhos do caderno
            (r'CIÊNCIAS DA NATUREZA E SUAS TECNOLOGIAS.*?AZUL.*?\d+', ''),
            
            # Remove linhas muito longas de códigos
            (r'(?:^|\n)[A-Z0-9]{50,}(?=\n|$)', ''),
            
            # Remove referências de fonte
            (r'Disponível em:.*?Acesso em:.*?\d{4}.*?(?:\(adaptado\))?', ''),
        ]
        
        cleaned = text
        for pattern, replacement in patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Normaliza espaços e quebras
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r' {3,}', ' ', cleaned)
        
        return cleaned.strip()
    
    def clean_statement(self, statement: str) -> str:
        """Limpa e melhora o enunciado"""
        
        # Remove fragmentos comuns
        fragments_to_remove = [
            r'Disponível em:.*?(?=\n|$)',
            r'Acesso em:.*?(?=\n|$)',
            r'\(adaptado\)',
            r'Fonte:.*?(?=\n|$)',
        ]
        
        cleaned = statement
        for pattern in fragments_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Normaliza espaços
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n+', '\n', cleaned)
        
        return cleaned.strip()
    
    def show_examples(self, limit: int = 3):
        """Mostra exemplos dos exercícios corrigidos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question_text, alternatives, topic 
            FROM math_exercises 
            ORDER BY RANDOM() 
            LIMIT ?
        ''', (limit,))
        
        exercises = cursor.fetchall()
        conn.close()
        
        for i, exercise in enumerate(exercises):
            exercise_id, question_text, alternatives_json, topic = exercise
            
            print(f"\n{'='*60}")
            print(f"EXEMPLO {i+1}: {exercise_id}")
            print(f"TÓPICO: {topic}")
            print(f"{'='*60}")
            
            print(f"\nENUNCIADO:")
            print(f"{question_text[:300]}{'...' if len(question_text) > 300 else ''}")
            
            print(f"\nALTERNATIVAS:")
            try:
                alternatives = json.loads(alternatives_json)
                for j, alt in enumerate(alternatives):
                    letter = chr(65 + j)  # A, B, C, D, E
                    print(f"{letter}) {alt}")
            except:
                print("Erro ao carregar alternativas")
            
            print(f"\n{'-'*60}")
    
    def get_statistics(self):
        """Mostra estatísticas da base de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de exercícios
        cursor.execute('SELECT COUNT(*) FROM math_exercises')
        total = cursor.fetchone()[0]
        
        # Exercícios com alternativas válidas
        cursor.execute('''
            SELECT COUNT(*) FROM math_exercises 
            WHERE alternatives != '[]' AND alternatives IS NOT NULL
        ''')
        with_alternatives = cursor.fetchone()[0]
        
        # Por tópico
        cursor.execute('''
            SELECT topic, COUNT(*) FROM math_exercises 
            GROUP BY topic ORDER BY COUNT(*) DESC
        ''')
        by_topic = cursor.fetchall()
        
        conn.close()
        
        print(f"\n📊 ESTATÍSTICAS DA BASE DE DADOS:")
        print(f"Total de exercícios: {total}")
        print(f"Com alternativas: {with_alternatives}")
        print(f"Taxa de sucesso: {(with_alternatives/total)*100:.1f}%")
        
        print(f"\nPor tópico:")
        for topic, count in by_topic:
            print(f"  {topic}: {count} exercícios")

def main():
    """Função principal para corrigir as alternativas"""
    print("🔧 Iniciando correção das alternativas...")
    
    fixer = AlternativesFixer()
    
    # Mostra estatísticas antes
    print("\n--- ANTES DA CORREÇÃO ---")
    fixer.get_statistics()
    
    # Corrige os exercícios
    print("\n🚀 Corrigindo exercícios...")
    fixed_count = fixer.fix_all_exercises()
    
    # Mostra estatísticas depois
    print("\n--- DEPOIS DA CORREÇÃO ---")
    fixer.get_statistics()
    
    # Mostra exemplos
    if fixed_count > 0:
        print("\n📚 EXEMPLOS DE EXERCÍCIOS CORRIGIDOS:")
        fixer.show_examples(3)
    
    print("\n✅ Processo de correção concluído!")

if __name__ == "__main__":
    main() 