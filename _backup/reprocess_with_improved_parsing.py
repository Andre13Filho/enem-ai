import os
from math_exercises_database_creator import EnemMathDatabase
import sqlite3
import json

def backup_original_database():
    """Faz backup da base de dados original"""
    try:
        # Renomeia a base original
        os.rename("enem_math_exercises.db", "enem_math_exercises_backup.db")
        print("✅ Backup da base original criado: enem_math_exercises_backup.db")
    except:
        print("⚠️ Não foi possível fazer backup (arquivo pode não existir)")

def reprocess_all_exercises():
    """Reprocessa todos os exercícios com parsing melhorado"""
    print("🚀 Iniciando reprocessamento com parsing melhorado...")
    
    # Cria nova instância da base de dados
    db = EnemMathDatabase()
    
    # Processa todos os PDFs novamente
    total = db.process_all_pdfs()
    
    return total

def show_comparison():
    """Mostra comparação entre base original e nova"""
    print("\n📊 COMPARAÇÃO DAS BASES DE DADOS:")
    
    # Base original (backup)
    try:
        conn_old = sqlite3.connect("enem_math_exercises_backup.db")
        cursor_old = conn_old.cursor()
        
        cursor_old.execute('SELECT COUNT(*) FROM math_exercises')
        total_old = cursor_old.fetchone()[0]
        
        cursor_old.execute('''
            SELECT COUNT(*) FROM math_exercises 
            WHERE alternatives != '[]' AND alternatives IS NOT NULL
        ''')
        with_alternatives_old = cursor_old.fetchone()[0]
        
        conn_old.close()
        
        print(f"BASE ORIGINAL:")
        print(f"  Total: {total_old} exercícios")
        print(f"  Com alternativas: {with_alternatives_old} ({(with_alternatives_old/total_old)*100:.1f}%)")
        
    except:
        print("❌ Não foi possível acessar base original")
    
    # Base nova
    try:
        conn_new = sqlite3.connect("enem_math_exercises.db")
        cursor_new = conn_new.cursor()
        
        cursor_new.execute('SELECT COUNT(*) FROM math_exercises')
        total_new = cursor_new.fetchone()[0]
        
        cursor_new.execute('''
            SELECT COUNT(*) FROM math_exercises 
            WHERE alternatives != '[]' AND alternatives IS NOT NULL
        ''')
        with_alternatives_new = cursor_new.fetchone()[0]
        
        conn_new.close()
        
        print(f"\nBASE MELHORADA:")
        print(f"  Total: {total_new} exercícios")
        print(f"  Com alternativas: {with_alternatives_new} ({(with_alternatives_new/total_new)*100:.1f}%)")
        
    except:
        print("❌ Não foi possível acessar base nova")

def show_improved_examples():
    """Mostra exemplos de exercícios com parsing melhorado"""
    try:
        conn = sqlite3.connect("enem_math_exercises.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question_text, alternatives, topic 
            FROM math_exercises 
            WHERE alternatives != '[]' AND alternatives IS NOT NULL
            ORDER BY RANDOM() 
            LIMIT 2
        ''')
        
        exercises = cursor.fetchall()
        conn.close()
        
        print(f"\n📚 EXEMPLOS COM PARSING MELHORADO:")
        
        for i, exercise in enumerate(exercises):
            exercise_id, question_text, alternatives_json, topic = exercise
            
            print(f"\n{'='*60}")
            print(f"EXEMPLO {i+1}: {exercise_id}")
            print(f"TÓPICO: {topic}")
            print(f"{'='*60}")
            
            print(f"\nENUNCIADO:")
            print(f"{question_text[:200]}{'...' if len(question_text) > 200 else ''}")
            
            print(f"\nALTERNATIVAS:")
            try:
                alternatives = json.loads(alternatives_json)
                for j, alt in enumerate(alternatives):
                    letter = chr(65 + j)  # A, B, C, D, E
                    print(f"{letter}) {alt[:80]}{'...' if len(alt) > 80 else ''}")
            except:
                print("Erro ao carregar alternativas")
            
            print(f"\n{'-'*60}")
            
    except Exception as e:
        print(f"❌ Erro ao mostrar exemplos: {str(e)}")

def main():
    """Função principal"""
    print("🔧 REPROCESSAMENTO COM PARSING MELHORADO")
    print("="*50)
    
    # Faz backup
    backup_original_database()
    
    # Reprocessa com parsing melhorado
    total = reprocess_all_exercises()
    
    # Mostra comparação
    show_comparison()
    
    # Mostra exemplos melhorados
    if total > 0:
        show_improved_examples()
    
    print(f"\n✅ Reprocessamento concluído!")
    print(f"Nova base de dados: enem_math_exercises.db")
    print(f"Base original salva em: enem_math_exercises_backup.db")

if __name__ == "__main__":
    main() 