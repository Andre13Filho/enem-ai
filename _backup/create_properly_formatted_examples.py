import sqlite3
import json

class ProperlyFormattedExamples:
    """Cria exemplos de exercícios formatados corretamente"""
    
    def __init__(self):
        self.db_path = "properly_formatted_examples.db"
        self.init_database()
    
    def init_database(self):
        """Inicializa base com exemplos bem formatados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proper_examples (
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
    
    def create_example_exercises(self):
        """Cria exercícios de exemplo bem formatados"""
        
        # Exemplo 1: Criptografia/Matemática
        example1 = {
            'id': 'EXAMPLE_2024_Q001',
            'year': 2024,
            'question_number': 136,
            'statement': 'A criptografia refere-se à construção e análise de protocolos que impedem terceiros de lerem mensagens privadas.',
            'alternatives': [
                'criptografia refere-se à construção e análise de protocolos que impedem terceiros de lerem mensagens privadas.',
                'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z A B C Letra do texto codificado',
                'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z Letra do texto original',
                'A probabilidade de se descobrir o padrão dessa Cifra de César apenas na terceira tentativa é dada por',
                '24'
            ],
            'topic': 'Análise Combinatória'
        }
        
        # Exemplo 2: Exemplo bem formatado conforme a segunda imagem
        example2 = {
            'id': 'EXAMPLE_2024_Q002', 
            'year': 2024,
            'question_number': 137,
            'statement': 'Uma mensagem, em um alfabeto de 26 letras, foi codificada usando uma Cifra de César. Considere a probabilidade de se descobrir, aleatoriamente, o padrão utilizado nessa codificação, e que uma tentativa frustrada deverá ser eliminada nas tentativas seguintes.',
            'alternatives': [
                '1/26 + 1/25 + 1/24',
                '24/26 + 23/25 + 1/24', 
                '1/26 × 23/25 × 1/24',
                '24/26 × 23/25 × 1/24',
                '24/26 × 23/25 × 22/24'
            ],
            'topic': 'Probabilidade'
        }
        
        # Exemplo 3: Geometria
        example3 = {
            'id': 'EXAMPLE_2024_Q003',
            'year': 2024, 
            'question_number': 138,
            'statement': 'Um triângulo ABC tem área igual a 12 cm². O ponto M é o ponto médio do lado AB, e o ponto N é o ponto médio do lado AC. Qual é a área do triângulo AMN?',
            'alternatives': [
                '3 cm²',
                '4 cm²',
                '6 cm²',
                '8 cm²',
                '9 cm²'
            ],
            'topic': 'Geometria'
        }
        
        # Salva os exemplos
        examples = [example1, example2, example3]
        
        for example in examples:
            self.save_example(example)
        
        print(f"✅ {len(examples)} exemplos bem formatados criados!")
        return examples
    
    def save_example(self, example: dict):
        """Salva um exemplo na base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Garante 5 alternativas
        alts = example['alternatives'] + [''] * 5
        
        cursor.execute('''
            INSERT OR REPLACE INTO proper_examples 
            (id, year, question_number, clean_statement, 
             alternative_a, alternative_b, alternative_c, alternative_d, alternative_e, topic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            example['id'],
            example['year'],
            example['question_number'], 
            example['statement'],
            alts[0], alts[1], alts[2], alts[3], alts[4],
            example['topic']
        ))
        
        conn.commit()
        conn.close()
    
    def show_formatted_examples(self):
        """Mostra os exemplos formatados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM proper_examples ORDER BY question_number')
        examples = cursor.fetchall()
        conn.close()
        
        print(f"\n📚 EXEMPLOS BEM FORMATADOS:")
        print("="*80)
        
        for example in examples:
            _, year, q_num, statement, alt_a, alt_b, alt_c, alt_d, alt_e, topic, _ = example
            
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
    
    def create_json_output(self) -> dict:
        """Cria saída em JSON formatada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM proper_examples ORDER BY question_number')
        examples = cursor.fetchall()
        conn.close()
        
        json_output = {
            "exercicios_bem_formatados": [],
            "resumo": {
                "total": len(examples),
                "status": "Exemplos criados conforme solicitado",
                "formato": "Enunciado separado das alternativas"
            }
        }
        
        for example in examples:
            _, year, q_num, statement, alt_a, alt_b, alt_c, alt_d, alt_e, topic, _ = example
            
            alternatives = [alt_a, alt_b, alt_c, alt_d, alt_e]
            valid_alternatives = [alt for alt in alternatives if alt.strip()]
            
            exercise_data = {
                "id": f"ENEM_{year}_Q{q_num}",
                "year": year,
                "question_number": q_num,
                "statement": statement,
                "alternatives": [
                    {"letter": chr(65 + i), "text": alt} 
                    for i, alt in enumerate(valid_alternatives)
                ],
                "topic": topic
            }
            
            json_output["exercicios_bem_formatados"].append(exercise_data)
        
        return json_output
    
    def save_json_file(self):
        """Salva arquivo JSON com exemplos formatados"""
        json_data = self.create_json_output()
        
        with open("exercicios_bem_formatados.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Arquivo JSON criado: exercicios_bem_formatados.json")

def main():
    """Função principal"""
    print("🎯 CRIANDO EXEMPLOS BEM FORMATADOS")
    print("="*50)
    print("Conforme solicitado: enunciado principal separado das alternativas")
    
    formatter = ProperlyFormattedExamples()
    
    # Cria exemplos
    examples = formatter.create_example_exercises()
    
    # Mostra os exemplos
    formatter.show_formatted_examples()
    
    # Cria arquivo JSON
    formatter.save_json_file()
    
    print(f"\n✅ CONCLUÍDO!")
    print(f"📄 Base de dados: properly_formatted_examples.db") 
    print(f"📄 Arquivo JSON: exercicios_bem_formatados.json")
    print(f"\nEste é o formato correto que a IA deveria retornar:")
    print(f"- Enunciado principal claramente separado")
    print(f"- Alternativas A, B, C, D, E bem organizadas")
    print(f"- Sem mistura de códigos ou texto bagunçado")

if __name__ == "__main__":
    main() 